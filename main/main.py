import argparse
import datetime
import os
import subprocess as sp
import sys
from typing import NoReturn

from main.constants import SOFTWARE_VER, SOFTWARE_NAME, TMP_DIR, OUTPUT_DIR


if (len(os.listdir(TMP_DIR)) != 1) and (os.listdir(TMP_DIR)[0] == '.gitkeep'):
    raise AssertionError('Directory "tmp" is not clean.')


parser = argparse.ArgumentParser(prog=SOFTWARE_NAME, description='Multilayered Noise Generation with FFmpeg')
parser.add_argument('--version', action='version', version=f'%(prog)s {SOFTWARE_VER}')

parser.add_argument('-d', '--duration', default=60, type=float, help='Track length in seconds (default: 60)')
parser.add_argument('-c', '--color', default='brown', help='Noise color options: white, pink, brown, blue, violet, and velvet (default: brown).')
parser.add_argument('-n', '--nlayer', default=7, type=int, help='Number of layers (default: 7)')
parser.add_argument('-hp', '--highpass', default=20, type=int, help='Default highpass value is 20.')
parser.add_argument('-lp', '--lowpass', default=432, type=int, help='Default lowpass value is 432.')
parser.add_argument('-vol', '--volume', type=int, help='Number of volume folds, defaults to the number of layers.')
parser.add_argument('-ff', '--ffmpeg', default='ffmpeg', help='FFmpeg binary file path. Default is \'ffmpeg\'.')
parser.add_argument('-o', '--output', help=f'Output folder path. Default is {OUTPUT_DIR}')

args = parser.parse_args()


def printer(__msg: str, /) -> None:
    print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] {__msg}')

def error(__msg: str, /) -> NoReturn:
    parser.exit(1, f'{parser.prog}: error: {__msg}\n')


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
        error('Error: FFMPEG path is invalid or does not point to an ffmpeg executable.')
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

## constructing output filename
output_filename = f'{COLOR} noise ({NLAYER}-layer {HIGHPASS}-{LOWPASS}hz {VOLUME}x) {datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.m4a'
output_file_pth = os.path.join(output_dir, output_filename)


def main() -> None:

    if n_warnings > 0:
        usr = input(f'\nThere were {n_warnings} warnings. Type y to continue: ')
        if usr != 'y':
            printer('Exiting...')
            sys.exit(1)

    ## generating the base noise
    base_noise_paths = []
    printer('Creating base noises..')
    for i in range(NLAYER):
        pth = os.path.join(TMP_DIR, f'base_noise_{str(i).zfill(3)}.m4a')
        sp.call([FFMPEG, '-v', 'error', '-f', 'lavfi', '-i', f'anoisesrc=d={DUR}:c={COLOR}', pth])
        base_noise_paths.append(pth)
        printer(f'Created base noise [{i+1}/{NLAYER}]: {pth}')

    input_cmd = []
    for pth in base_noise_paths:
        input_cmd += ['-i', pth]

    printer('Generating the output...')
    sp.call([
        FFMPEG,
        '-v', 'error',
        *input_cmd,
        '-filter_complex', f'amix=inputs={NLAYER},highpass=f={HIGHPASS},lowpass=f={LOWPASS},volume={VOLUME}',
        output_file_pth
    ])

    ## deleting the base noises
    for pth in base_noise_paths:
        printer(f'Base noise file deleted: {pth}')
        os.remove(pth)

    printer(f'File successfully created at: {output_file_pth}')