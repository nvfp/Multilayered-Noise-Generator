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
if not (
    (len(os.listdir(TMP_DIR)) == 1)
    and
    (os.listdir(TMP_DIR)[0] == '.gitkeep')
):
    raise AssertionError(f'Directory {repr(TMP_DIR)} is not clean.')


## <parser>
parser = argparse.ArgumentParser(prog=SOFTWARE_NAME, description='Multilayered Noise Generation with FFmpeg')
parser.add_argument('--version', action='version', version=f'%(prog)s v{SOFTWARE_VER}')

## Audio-related
parser.add_argument('-d', '--duration', default=60, type=float, help='Track length in seconds (default: 60)')
parser.add_argument('-c', '--color', default='brown', help='Noise color options: white, pink, brown, blue, violet, and velvet (default: brown)')
parser.add_argument('-n', '--nlayer', default=7, type=int, help='Number of layers (default: 7)')
parser.add_argument('-hp', '--highpass', default=20, type=int, help='Highpass frequency value (default: 20 Hz)')
parser.add_argument('-lp', '--lowpass', default=432, type=int, help='Lowpass frequency value (default: 432 Hz)')
parser.add_argument(
    '-v', '--volume', type=int,
    help='Volume amplification: to set the output loudness and address clipping issues (default: half of the number of layers)'
)
parser.add_argument(
    '-s', '--stereo', action=argparse.BooleanOptionalAction, default=True,
    help='Enable stereo mode (True) for stereo output, or disable it (False) for mono output.'
)
parser.add_argument(
    '-dv', '--dyn_vol', action=argparse.BooleanOptionalAction, default=False,
    help='Enable dynamic noise volume by launching a GUI that allows you to adjust the dynamicness parameters'
)
parser.add_argument(
    '-dvd', '--dyn_vol_dual', action=argparse.BooleanOptionalAction, default=True,
    help='Use this option with `-dv` and `-s` to select two volume patterns. If set to `False`, both channels will share the same pattern.'
)
parser.add_argument(
    '-norm', '--normalize', action=argparse.BooleanOptionalAction, default=False,
    help='Apply the `dynaudnorm` filter to normalize the output audio, ensuring optimal amplitude and preventing clipping.'
)
parser.add_argument(
    '-b', '--bitrate', default=256, type=int,
    help=f'Audio bitrate in kilobits per second (default: 256)'
)

## Output
parser.add_argument('-od', '--output_dir', help=f'Output folder path, (default: {repr(OUTPUT_DIR)})')
parser.add_argument(
    '-on', '--output_name',
    help='Specify a custom output filename. If not specified, the default format will be used.'
)
parser.add_argument(
    '-oe', '--output_ext', default='.m4a',
    help='Specify the output extension (default: .m4a)'
)

## Misc
parser.add_argument(
    '-p', '--print', action=argparse.BooleanOptionalAction, default=True,
    help='Print audio metadata'
)
parser.add_argument('-ff', '--ffmpeg', default='ffmpeg', help='FFmpeg binary file path or command (default: ffmpeg)')

args = parser.parse_args()
## </parser>


## <utils>
def printer(__msg: str, /) -> None:
    print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] {__msg}')

def error(__msg: str, /) -> NoReturn:
    parser.exit(1, f'{parser.prog}: ERROR: {__msg}\n')
## </utils>


## <validations and preprocessing>

n_warnings = 0

DUR = args.duration
if DUR <= 0:
    error('Duration should be greater than 0.')
elif DUR > 3600:
    printer('WARNING: Duration longer than 1 hour may increase processing time and require significant storage space.')
    n_warnings += 1

COLOR = args.color.lower()
if COLOR not in {'white', 'pink', 'brown', 'blue', 'violet', 'velvet'}:
    error(f'Invalid color "{COLOR}". Available options are: white, pink, brown, blue, violet, velvet.')

NLAYER = args.nlayer
if NLAYER < 2:
    error('Number of layers must be at least 2.')
elif NLAYER > 20:
    printer('WARNING: The specified number of layers is quite large and may result in longer processing time.')
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
    VOLUME = max(1, round(NLAYER/2))
else:
    if VOLUME < 1:
        error('Volume must be at least 1.')
    elif VOLUME > 2*NLAYER:
        printer('WARNING: The specified volume may cause clipping.')
        n_warnings += 1

BITRATE = args.bitrate
if BITRATE < 32:
    error('Bitrate is too low.')
elif BITRATE > 320:
    printer('WARNING: Bitrate is too high.')
    n_warnings += 1

## <constructing output filename>
if args.output_dir is None:
    output_dir = OUTPUT_DIR
else:
    if not os.path.isdir(args.output_dir):
        error(f'The specified directory path is not valid: {args.output_dir}')
    output_dir = args.output_dir

output_ext = args.output_ext.lower()
if output_ext not in ALLOWED_EXTENSIONS:
    error(f'Invalid output extension: {repr(output_ext)}')

if args.output_name is None:
    output_filename = (
        f'noise-{COLOR} ({NLAYER}-layer {HIGHPASS}-{LOWPASS}hz {VOLUME}x) '
        + datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        + output_ext
    )
else:
    output_filename = validate_filename(args.output_name) + output_ext

OUTPUT_FILE_PTH = os.path.join(output_dir, output_filename)
if os.path.exists(OUTPUT_FILE_PTH):
    error(f'Output file conflict. Please try a different filename or file extension: {repr(OUTPUT_FILE_PTH)}')
## </constructing output filename>

FFMPEG = args.ffmpeg
if FFMPEG != 'ffmpeg':
    if not (os.path.isfile(FFMPEG) and os.path.splitext(FFMPEG.lower())[1] == '.exe'):
        error('FFMPEG path is invalid or does not point to an ffmpeg executable.')
try:
    sp.run([FFMPEG, '-version'], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    printer(f'INFO: ffmpeg valid and usable.')
except FileNotFoundError:
    error(f'ffmpeg not found or not a recognized command ({FFMPEG})')

## </validations and preprocessing>


def main() -> None:

    if n_warnings > 0:
        usr = input(f'\nThere were {n_warnings} warnings. Type y to continue: ')
        if usr != 'y':
            printer('INFO: Exiting...')
            sys.exit(1)

    ## dynamic volume
    dyn_vol_filter = ''
    dyn_vol_filter_right_channel = ''
    if args.dyn_vol:
        printer('INFO: opening the GUI..')
        dyn_vol_filter, dyn_vol_md = dyn_vol(DUR)
        printer('INFO: dyn_vol_filter generated.')

        if args.stereo:
            if args.dyn_vol_dual:
                printer('INFO: opening the GUI again..')
                dyn_vol_filter_right_channel, dyn_vol_md_rc = dyn_vol(DUR)
                printer('INFO: dyn_vol_filter_right_channel generated.')
            else:
                printer('INFO: Both channels have the same volume pattern.')
                dyn_vol_filter_right_channel, dyn_vol_md_rc = dyn_vol_filter, dyn_vol_md
    dyn_vol_filter_pack = {
        'left': dyn_vol_filter,
        'right': dyn_vol_filter_right_channel,
    }
    
    ## normalization
    norm_filter = ''
    if args.normalize:
        norm_filter = ',dynaudnorm'

    ## <core>
    intermediate_file_pths = []

    if args.stereo:

        mono_pths = []
        for side in ['left', 'right']:

            printer(f'INFO: Creating {NLAYER} base noises for the {side} channel.')
            base_pths = []
            for i in range(NLAYER):
                time.sleep(0.1)
                pth = os.path.join(TMP_DIR, f'stereo_base_{side}_{str(i).zfill(3)}.wav')
                sp.call([
                    FFMPEG, '-v', 'error', '-stats',
                    '-f', 'lavfi', '-i', f'anoisesrc=d={DUR}:c={COLOR}:s={time.time()}',
                    '-b:a', f'{BITRATE}k',
                    pth
                ])
                intermediate_file_pths.append(pth)
                base_pths.append(pth)
                printer(f'INFO: Created ({i+1}/{NLAYER}): {pth}')

            printer(f'INFO: Generating the {side} channel.')
            mono_pth = os.path.join(TMP_DIR, f'stereo_{side}_channel.wav')
            input_cmd = []
            for pth in base_pths:
                input_cmd += ['-i', pth]
            sp.call([
                FFMPEG, '-v', 'error', '-stats',
                *input_cmd,
                '-filter_complex', f'amix=inputs={NLAYER},highpass=f={HIGHPASS},lowpass=f={LOWPASS},volume={VOLUME}{dyn_vol_filter_pack[side]}',
                '-b:a', f'{BITRATE}k',
                mono_pth
            ])
            intermediate_file_pths.append(mono_pth)
            mono_pths.append(mono_pth)

        printer('INFO: Mixing into stereo...')
        sp.call([
            FFMPEG, '-v', 'error', '-stats',
            '-i', mono_pths[0],
            '-i', mono_pths[1],
            '-filter_complex', f'[0:a][1:a]amerge=inputs=2{norm_filter}[a]',
            '-map', '[a]',
            '-b:a', f'{BITRATE}k',
            OUTPUT_FILE_PTH
        ])
    
    else:  # mono

        printer(f'INFO: Creating {NLAYER} base noises..')
        for i in range(NLAYER):
            time.sleep(0.1)
            pth = os.path.join(TMP_DIR, f'mono_base_{str(i).zfill(3)}.wav')
            sp.call([
                FFMPEG, '-v', 'error', '-stats',
                '-f', 'lavfi', '-i', f'anoisesrc=d={DUR}:c={COLOR}:s={time.time()}',
                '-b:a', f'{BITRATE}k',
                pth
            ])
            intermediate_file_pths.append(pth)
            printer(f'INFO: Created ({i+1}/{NLAYER}): {pth}')

        input_cmd = []
        for pth in intermediate_file_pths:
            input_cmd += ['-i', pth]

        printer('INFO: Generating the output...')
        sp.call([
            FFMPEG, '-v', 'error', '-stats',
            *input_cmd,
            '-filter_complex', f'amix=inputs={NLAYER},highpass=f={HIGHPASS},lowpass=f={LOWPASS},volume={VOLUME}{dyn_vol_filter}{norm_filter}',
            '-b:a', f'{BITRATE}k',
            OUTPUT_FILE_PTH
        ])
    ## </core>

    ## deleting the intermediate files (base noises)
    for pth in intermediate_file_pths:
        printer(f'INFO: Deleting {repr(pth)}...')
        os.remove(pth)

    printer(f'INFO: The output successfully created at: {OUTPUT_FILE_PTH}')

    ## printing metadata
    if args.print:
        md = (
            '\n'
            '===================================================='
            '\n'
            'Audio metadata:\n'
            f'- Software version: {SOFTWARE_VER}\n'
            f'- Created on: {datetime.datetime.now().strftime("%b %#d, %Y (%#I:%M %p)")}\n'
            f'- Duration: {DUR} secs\n'
            f'- Color: {COLOR}\n'
            f'- Number of layers: {NLAYER}\n'
            f'- Highpass: {HIGHPASS} hz\n'
            f'- Lowpass: {LOWPASS} hz\n'
            f'- Volume: {VOLUME}x\n'
            f'- Channels: {"stereo" if args.stereo else "mono"}\n'
            f'- Normalized: {args.normalize}\n'
            f'- Bitrate: {BITRATE} kbps\n'
            f'- Using dynamic volume: {args.dyn_vol}' + ((' (dual)' if args.dyn_vol_dual else ' (single)') if args.dyn_vol else '')
        )
        if args.dyn_vol:
            md += (
                '\n' + ('  *left channel*\n' if args.dyn_vol_dual else '') +
                f'  - Number of changes: {dyn_vol_md["nchanges"]} transitions\n'
                f'  - Min volume: {dyn_vol_md["vol_min"]}x\n'
                f'  - Max volume: {dyn_vol_md["vol_max"]}x\n'
                f'  - Perlin noise persistence: {dyn_vol_md["persistence"]}\n'
                f'  - Perlin noise octaves: {dyn_vol_md["octaves"]}\n'
                f'  - Perlin noise frequency: {dyn_vol_md["frequency"]}\n'
                f'  - Perlin noise seed: {dyn_vol_md["seed"]}'
            )
            if args.dyn_vol_dual:
                md += (
                    '\n'
                    '  *right channel*\n'
                    f'  - Number of changes: {dyn_vol_md_rc["nchanges"]} transitions\n'
                    f'  - Min volume: {dyn_vol_md_rc["vol_min"]}x\n'
                    f'  - Max volume: {dyn_vol_md_rc["vol_max"]}x\n'
                    f'  - Perlin noise persistence: {dyn_vol_md_rc["persistence"]}\n'
                    f'  - Perlin noise octaves: {dyn_vol_md_rc["octaves"]}\n'
                    f'  - Perlin noise frequency: {dyn_vol_md_rc["frequency"]}\n'
                    f'  - Perlin noise seed: {dyn_vol_md_rc["seed"]}'
                )
        md += (
            '\n\n'
            'Software source code:\n'
            'https://github.com/nvfp/Multilayered-Noise-Generator'
            '\n'
            '===================================================='
        )
        print(md)