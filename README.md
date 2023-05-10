## Multilayered-Noise-Generator
This program generates multilayered deep audio noise using the FFmpeg audio source "anoisesrc" to generate the noise. It can create brown noise, white noise, and other types of noise that are known to help some people relax and promote a focused ambiance.

## Installation
1. Download this repository and save it to your machine (e.g. `~/projects/noise_gen`).
2. Install dependencies:
    - [carbon](https://github.com/nvfp/carbon)
    - NumPy:
        ```sh
        pip install -r requirements.txt
        ```
    - [FFmpeg](https://ffmpeg.org/download.html)
3. All set and ready to use!

## Usage
- Try it:
    ```sh
    python noise_gen
    ```
    This generates a 7-layer, 60-second brown noise stereo with a cutoff range of 20-432 Hz.

- More customized:
    ```sh
    python noise_gen -d 3600 -c violet -n 15 -hp 900 -lp 1750 -v 9 --no-stereo -b 320 -oe .mp3
    ```
    Output: 1-hour mp3 file at 320kbps of 15-layered mono violet noise (900-1750 Hz).

- Using dynamic volume:
    ```sh
    python noise_gen -dv
    ```
    This command launches the GUI for setting the volume pattern that dynamically adjusts the volume, creating a captivating ambience.
    ![Dynamic volume demo gif](media/dv-demo.gif)

- Below are the options available to customize the generated noise:
    - `-d`: Track length in seconds (default: `60`)
    - `-c`: Noise color options: white, pink, brown, blue, violet, and velvet (default: `brown`)
    - `-n`: Number of layers (default: `7`)
    - `-hp`: Highpass frequency value (default: `20` Hz)
    - `-lp`: Lowpass frequency value (default: `432` Hz)
    - `-v`: Volume amplification: to set the output loudness and address clipping issues (default: half of the number of layers)
    - `-s`: Enable stereo mode (True) for stereo output, or disable it (False) for mono output. (default: `True`)
    - `-dv`: Enable dynamic noise volume by launching a GUI that allows you to adjust the dynamicness parameters (default: `False`)
    - `-dvd`: Use this option with `-dv` and `-s` to select two volume patterns. If set to `False`, both channels will share the same pattern. (default: `True`)
    - `-norm`: Apply the `dynaudnorm` filter to normalize the output audio, ensuring optimal amplitude and preventing clipping. (default: `False`)
    - `-b`: Audio bitrate in kilobits per second (default: `256`)
    - `-od`: Output folder path (default: `noise_gen/output`)
    - `-on`: Specify a custom output filename. If not specified, the default format will be used.
    - `-oe`: Specify the output extension (default: `.m4a`)
    - `-p`: Print audio metadata (default: `True`)
    - `-ff`: FFmpeg binary file path or command (default: `ffmpeg`)

## Learn more
To learn about the FFmpeg side, visit this [webpage](https://nvfp.github.io/misc/ffmpeg/index.html#multilayered_noise_generator) for more information.

## Troubleshooting
- If you encounter the error `noise_gen: ERROR: ffmpeg not found or not a recognized command (ffmpeg)`, try these:
    - Ensure that FFmpeg is installed and accessible as a command in the shell.
    - If FFmpeg is installed but not accessible, add its location to system's PATH variable.
    - Alternatively, you can reference the FFmpeg binary using the `-ff` flag when running a command. Example:

        ```sh
        python noise_gen -ff ~/ffmpeg/bin/ffmpeg.exe
        ```

## Changelog
- v2.0.0 (May 10, 2023):
    - Added `--normalize` arg: To normalize the output audio and ensure optimal amplitude
    - Updated `--volume` default value to `half the number of layers` to prevent clipping
    - Updated the optional argument from `-vol` to `-v`
    - Updated the optional argument from `-dvs` to `-dvd` and `--dyn_vol_stereo` to `--dyn_vol_dual`
    - Updated the optional argument from `--audio_bitrate` to `--bitrate`
    - Updated the optional argument from `-o` to `-od` and `--output` to `--output_dir`
    - Updated the optional argument from `-of` to `-on` and `--output_filename` to `--output_name`
    - Updated the optional argument from `-ext` to `-oe` and `--output_extension` to `--output_ext`
    - Updated the optional argument from `-pm` to `-p` and `--print_metadata` to `--print`
- 1.4.0 (May 10, 2023):
    - Added `stereo` arg: Enable or disable stereo audio output
    - Added `stereo_dyn_vol` arg: Enable or disable dynamic volume for both left and right audio channels
    - Added `custom_output_filename` arg: Specify a custom output filename for the audio file
    - Added `output_extension` arg: Specify the desired extension for the output audio file
    - Updated the base noise extension from `.m4a` to `.wav` to enhance the quality
- 1.3.0 (May 9, 2023):
    - Added `bitrate` arg
- 1.2.0 (May 9, 2023):
    - Bug fixed: The `seed` option is now used on the `anoisesrc` filter to ensure uniqueness of each noise
    - Added `print_metadata` argument
- 1.1.0 (May 6, 2023):
    - added volume-randomizer using Perlin noise
    - changed the output filename format

## License
This project is licensed under the MIT license.
