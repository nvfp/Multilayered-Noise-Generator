## Multilayered-Noise-Generator
This program generates multilayered deep noise using the FFmpeg noise generator. It can create brown noise, white noise, and other types of noise that are known to help some people relax and promote a focused ambiance.

## Installation
1. Download this repository and save it to your machine (e.g. ~/myproject/multilayered_noise_generator).
2. Install [FFmpeg](https://ffmpeg.org/download.html) on your machine, if it is not already installed.
3. You're all set and ready to use!

## Usage
### Try running the following:
```sh
python multilayered_noise_generator
```
This will generate seven layers of 60 seconds brown noise that cutoff within the range of 20 to 432 Hz.

### You can also run:
```sh
python multilayered_noise_generator -d 3600 -c white -n 15 -lp 300
```
This command will generate one hour of deep white noise that may help promote relaxation, improve concentration, and aid in sleep.

### Here are the available command line options for customizing the generated noise:
* `-d`: Track length in seconds (default: 60)
* `-c`: Noise color options: white, pink, brown, blue, violet, and velvet (default: brown)
* `-n`: Number of layers (default: 7)
* `-hp`: Highpass frequency value (default: 20 Hz)
* `-lp`: Lowpass frequency value (default: 432 Hz)
* `-vol`: Number of volume folds (default: number of layers)
* `-ff`: FFmpeg binary file path or command (default: 'ffmpeg')
* `-o`: Output folder path (default: multilayered_noise_generator/output)

## Learn more
To learn about the FFmpeg aspect, visit this [webpage](https://nvfp.github.io/learning/ffmpeg/index.html#multilayered_noise_generator) for more information.

## Troubleshooting
### If you encounter the error message "multilayered_noise_generator: error: ffmpeg not found or not a recognized command (ffmpeg)", try the following steps:
- Ensure that FFmpeg is installed on your machine and is accessible as a command in the shell.
- If FFmpeg is installed but not accessible, add its location to your system's PATH variable.
- Alternatively, you can reference the FFmpeg binary using the `-ff` flag when running the `multilayered_noise_generator` command. For example:
```sh
python multilayered_noise_generator -ff ~/ffmpeg/bin/ffmpeg.exe
```
By following these steps, you should be able to resolve the FFmpeg-related error and use `multilayered_noise_generator` as intended.

## License
This project is licensed under the MIT license.
