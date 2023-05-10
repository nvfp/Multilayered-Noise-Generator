import argparse
import datetime
import os
import subprocess as sp
import sys
import time
from typing import NoReturn

from main.constants import SOFTWARE_VER, SOFTWARE_NAME, TMP_DIR, OUTPUT_DIR, ALLOWED_EXTENSIONS
from main.dyn_vol import dyn_vol
from main.utils import validate_filename


## To ensure the cleanliness of the "tmp" folder,
## which is used to store intermediate files during the generation of the final output,
## and prevent unintended deletions.
if (len(os.listdir(TMP_DIR)) != 1) and (os.listdir(TMP_DIR)[0] == '.gitkeep'):
    raise AssertionError('Directory "tmp" is not clean.')


## <parser>
parser = argparse.ArgumentParser(prog=SOFTWARE_NAME, description='Multilayered Noise Generation with FFmpeg')
parser.add_argument('--version', action='version', version=f'%(prog)s {SOFTWARE_VER}')

parser.add_argument('-d', '--duration', default=60, type=float, help='Track length in seconds (default: 60)')
parser.add_argument('-c', '--color', default='brown', help='Noise color options: white, pink, brown, blue, violet, and velvet (default: brown).')
parser.add_argument('-n', '--nlayer', default=7, type=int, help='Number of layers (default: 7)')
parser.add_argument('-hp', '--highpass', default=20, type=int, help='Highpass frequency value (default: 20 Hz)')
parser.add_argument('-lp', '--lowpass', default=432, type=int, help='Lowpass frequency value (default: 432 Hz)')
parser.add_argument('-vol', '--volume', type=int, help='Number of volume folds, defaults to the number of layers.')
parser.add_argument(
    '-dv', '--dyn_vol', action=argparse.BooleanOptionalAction, default=False,
    help='Use dynamic volume (using Perlin noise) and open the GUI to set the dynamic volume parameters.'
)
parser.add_argument(
    '-dvs', '--dyn_vol_stereo', action=argparse.BooleanOptionalAction, default=True,
    help='For stereo output, use this option to select two noise patterns. If set to False, both channels will share the same pattern.'
)
parser.add_argument(
    '-s', '--stereo', action=argparse.BooleanOptionalAction, default=True,
    help='Enable stereo mode (True) for stereo output, or disable it (False) for mono output'
)
parser.add_argument('-ff', '--ffmpeg', default='ffmpeg', help='FFmpeg binary file path or command (default: \'ffmpeg\')')
parser.add_argument('-o', '--output', help=f'Output folder path, default is {OUTPUT_DIR}')
parser.add_argument(
    '-of', '--output_filename',
    help='Specify a custom output filename. If not specified, the default format will be used.'
)
parser.add_argument(
    '-ext', '--output_extension', default='.m4a',
    help='Specify the output extension. The default extension is .m4a.'
)
parser.add_argument(
    '-b', '--audio_bitrate', default=256, type=int,
    help=f'Audio bitrate in kilobits per second (default: 256)'
)
parser.add_argument(
    '-pm', '--print_metadata', action=argparse.BooleanOptionalAction, default=True,
    help='Print audio metadata.'
)

args = parser.parse_args()
## </parser>


## <utils>
def printer(__msg: str, /) -> None:
    print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] {__msg}')

def error(__msg: str, /) -> NoReturn:
    parser.exit(1, f'{parser.prog}: error: {__msg}\n')
## </utils>


## <validations and preprocessing>

n_warnings = 0

DUR = args.duration
if DUR <= 0:
    error('Duration should be greater than 0.')
elif DUR > 3600:
    printer('Warning: The specified duration is longer than 1 hour. This may result in longer processing time.')
    n_warnings += 1

COLOR = args.color.lower()
if COLOR not in {'white', 'pink', 'brown', 'blue', 'violet', 'velvet'}:
    error(f'Invalid color "{COLOR}". Available options are: white, pink, brown, blue, violet, velvet.')

NLAYER = args.nlayer
if NLAYER < 2:
    error('Number of layers must be at least 2.')
elif NLAYER > 20:
    printer('Warning: The specified number of layers is quite large and may result in longer processing time.')
    n_warnings += 1

HIGHPASS = args.highpass
LOWPASS = args.lowpass
if HIGHPASS < 20:
    error('Highpass frequency must be greater than or equal to 20 Hz.')
if LOWPASS > 20000:
    error('Lowpass frequency must be less than or equal to 20,000 Hz.')
if HIGHPASS >= LOWPASS:
    error('Highpass frequency must be less than lowpass frequency.')

VOLUME = args.volume
if VOLUME is None:
    VOLUME = NLAYER
else:
    if VOLUME < 1:
        error('Volume must be at least 1.')
    elif VOLUME > 2*NLAYER:
        printer('Warning: The specified volume may cause clipping.')
        n_warnings += 1

FFMPEG = args.ffmpeg
if FFMPEG != 'ffmpeg':
    if not (os.path.isfile(FFMPEG) and os.path.splitext(FFMPEG.lower())[1] == '.exe'):
        error('FFMPEG path is invalid or does not point to an ffmpeg executable.')
try:
    sp.run([FFMPEG, '-version'], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    printer(f'INFO: ffmpeg valid and usable.')
except FileNotFoundError:
    error(f'ffmpeg not found or not a recognized command ({FFMPEG})')


if args.output is None:
    output_dir = OUTPUT_DIR
else:
    if not os.path.isdir(args.output):
        error(f'The specified directory path is not valid: {args.output}')
    output_dir = args.output


OUTPUT_EXTENSION = args.output_extension.lower()
if OUTPUT_EXTENSION not in ALLOWED_EXTENSIONS:
    error(f'Invalid output extension: {repr(OUTPUT_EXTENSION)}')


## <constructing output filename>
if args.output_filename is None:
    output_filename = (
        f'noise-{COLOR} ({NLAYER}-layer {HIGHPASS}-{LOWPASS}hz {VOLUME}x) {datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}{OUTPUT_EXTENSION}'
    )
else:
    output_filename = validate_filename(args.output_filename) + OUTPUT_EXTENSION

output_file_pth = os.path.join(output_dir, output_filename)
if os.path.exists(output_file_pth):
    error(f'Output file conflict. Please try a different filename or file extension: {repr(output_file_pth)}')
## </constructing output filename>


BITRATE = args.audio_bitrate
if BITRATE < 32:
    error('Bitrate is too low')
elif BITRATE > 320:
    printer('Warning: Bitrate is too high')
    n_warnings += 1

## </validations and preprocessing>


def main() -> None:

    if n_warnings > 0:
        usr = input(f'\nThere were {n_warnings} warnings. Type y to continue: ')
        if usr != 'y':
            printer('Exiting...')
            sys.exit(1)


    ## dynamic volume
    dyn_vol_filter = ''
    dyn_vol_filter2 = ''
    if args.dyn_vol:
        printer('INFO: opening dyn_vol GUI..')
        dyn_vol_filter, dyn_vol_filter_metadata = dyn_vol(DUR)
        printer('INFO: dyn_vol_filter generated.')

        if args.stereo:
            if args.dyn_vol_stereo:
                printer('INFO: opening dyn_vol GUI again..')
                dyn_vol_filter2, dyn_vol_filter_metadata2 = dyn_vol(DUR)
                printer('INFO: dyn_vol_filter2 generated.')
            else:
                dyn_vol_filter2, dyn_vol_filter_metadata2 = dyn_vol_filter, dyn_vol_filter_metadata


    ## <core>
    base_noise_paths = []

    if args.stereo:

        printer(f'Creating {2*NLAYER} base noises..')
        left_noise_pths = []
        for i in range(NLAYER):
            time.sleep(0.1)
            pth = os.path.join(TMP_DIR, f'base_noise_stereo_left_{str(i).zfill(3)}.wav')
            sp.call([
                FFMPEG,
                '-v', 'error', '-stats',
                '-f', 'lavfi', '-i', f'anoisesrc=d={DUR}:c={COLOR}:s={time.time()}',
                '-b:a', f'{BITRATE}k',
                pth
            ])
            base_noise_paths.append(pth)
            left_noise_pths.append(pth)
            printer(f'Created base noise [{i+1}/{NLAYER}]: {pth}')

        right_noise_pths = []
        for i in range(NLAYER):
            time.sleep(0.1)
            pth = os.path.join(TMP_DIR, f'base_noise_stereo_right_{str(i).zfill(3)}.wav')
            sp.call([
                FFMPEG,
                '-v', 'error', '-stats',
                '-f', 'lavfi', '-i', f'anoisesrc=d={DUR}:c={COLOR}:s={time.time()}',
                '-b:a', f'{BITRATE}k',
                pth
            ])
            base_noise_paths.append(pth)
            right_noise_pths.append(pth)
            printer(f'Created base noise [{i+1}/{NLAYER}]: {pth}')

        printer('Generating the left channel...')
        left_channel_pth = os.path.join(TMP_DIR, 'left_channel.wav')
        input_cmd = []
        for pth in left_noise_pths:
            input_cmd += ['-i', pth]
        sp.call([
            FFMPEG,
            '-v', 'error', '-stats',
            *input_cmd,
            '-filter_complex', f'amix=inputs={NLAYER},highpass=f={HIGHPASS},lowpass=f={LOWPASS},volume={VOLUME}{dyn_vol_filter}',
            '-b:a', f'{BITRATE}k',
            left_channel_pth
        ])
        base_noise_paths.append(left_channel_pth)

        printer('Generating the right channel...')
        right_channel_pth = os.path.join(TMP_DIR, 'right_channel.wav')
        input_cmd = []
        for pth in right_noise_pths:
            input_cmd += ['-i', pth]
        sp.call([
            FFMPEG,
            '-v', 'error', '-stats',
            *input_cmd,
            '-filter_complex', f'amix=inputs={NLAYER},highpass=f={HIGHPASS},lowpass=f={LOWPASS},volume={VOLUME}{dyn_vol_filter2}',
            '-b:a', f'{BITRATE}k',
            right_channel_pth
        ])
        base_noise_paths.append(right_channel_pth)

        printer('Mixing into stereo...')
        sp.call([
            FFMPEG,
            '-v', 'error', '-stats',
            '-i', left_channel_pth,
            '-i', right_channel_pth,
            '-filter_complex', '[0:a][1:a]amerge=inputs=2[a]',
            '-map', '[a]',
            '-b:a', f'{BITRATE}k',
            output_file_pth
        ])
    else:
        printer(f'Creating {NLAYER} base noises..')
        for i in range(NLAYER):
            time.sleep(0.1)
            pth = os.path.join(TMP_DIR, f'base_noise_mono_{str(i).zfill(3)}.wav')
            sp.call([
                FFMPEG,
                '-v', 'error', '-stats',
                '-f', 'lavfi', '-i', f'anoisesrc=d={DUR}:c={COLOR}:s={time.time()}',
                '-b:a', f'{BITRATE}k',
                pth
            ])
            base_noise_paths.append(pth)
            printer(f'Created base noise [{i+1}/{NLAYER}]: {pth}')

        input_cmd = []
        for pth in base_noise_paths:
            input_cmd += ['-i', pth]

        printer('Generating the output...')
        sp.call([
            FFMPEG,
            '-v', 'error', '-stats',
            *input_cmd,
            '-filter_complex', f'amix=inputs={NLAYER},highpass=f={HIGHPASS},lowpass=f={LOWPASS},volume={VOLUME}{dyn_vol_filter}',
            '-b:a', f'{BITRATE}k',
            output_file_pth
        ])
    ## </core>


    ## deleting the intermediate files (base noises)
    for pth in base_noise_paths:
        printer(f'Base noise file deleted: {pth}')
        os.remove(pth)

    printer(f'File successfully created at: {output_file_pth}')

    
    if args.print_metadata:
        md = (
            '\n'
            '===================================================='
            '\n'
            'Audio metadata:\n'
            f'- Software version: {SOFTWARE_VER}\n'
            f'- Created on: {datetime.datetime.now().strftime("%b %#d, %Y, (%#I:%M %p)")}\n'
            f'- Duration: {DUR} secs\n'
            f'- Color: {COLOR}\n'
            f'- Number of layers: {NLAYER}\n'
            f'- Highpass: {HIGHPASS} hz\n'
            f'- Lowpass: {LOWPASS} hz\n'
            f'- Volume: {VOLUME}x\n'
            f'- Bitrate: {BITRATE} kbps\n'
            f'- Type: {"stereo" if args.stereo else "mono"}\n'
            f'- Using dynamic volume: {args.dyn_vol}' + ((' (stereo)' if args.dyn_vol_stereo else ' (mono)') if args.dyn_vol else '')
        )
        if args.dyn_vol:
            md += (
                '\n' + ('  *left channel*\n' if args.dyn_vol_stereo else '') +
                f'  - Number of changes: {dyn_vol_filter_metadata["nchanges"]} transitions\n'
                f'  - Min volume: {dyn_vol_filter_metadata["vol_min"]}x\n'
                f'  - Max volume: {dyn_vol_filter_metadata["vol_max"]}x\n'
                f'  - Perlin noise persistence: {dyn_vol_filter_metadata["persistence"]}\n'
                f'  - Perlin noise octaves: {dyn_vol_filter_metadata["octaves"]}\n'
                f'  - Perlin noise frequency: {dyn_vol_filter_metadata["frequency"]}\n'
                f'  - Perlin noise seed: {dyn_vol_filter_metadata["seed"]}'
            )
            if args.dyn_vol_stereo:
                md += (
                    '\n'
                    '  *right channel*\n'
                    f'  - Number of changes: {dyn_vol_filter_metadata2["nchanges"]} transitions\n'
                    f'  - Min volume: {dyn_vol_filter_metadata2["vol_min"]}x\n'
                    f'  - Max volume: {dyn_vol_filter_metadata2["vol_max"]}x\n'
                    f'  - Perlin noise persistence: {dyn_vol_filter_metadata2["persistence"]}\n'
                    f'  - Perlin noise octaves: {dyn_vol_filter_metadata2["octaves"]}\n'
                    f'  - Perlin noise frequency: {dyn_vol_filter_metadata2["frequency"]}\n'
                    f'  - Perlin noise seed: {dyn_vol_filter_metadata2["seed"]}'
                )
        md += (
            '\n\n'
            'Software source code:\n'
            'https://github.com/nvfp/Multilayered-Noise-Generator'
            '\n'
            '===================================================='
        )
        print(md)