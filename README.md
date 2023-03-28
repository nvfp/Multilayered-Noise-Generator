## Multilayered-Noise-Generator
This program generates multilayered deep noise using the FFmpeg noise generator. It can create brown noise, white noise, and other types of noise that are known to help some people relax and promote a focused ambiance.

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
To learn about the FFmpeg aspect, visit this [webpage](https://nvfp.github.io/learning/ffmpeg#multilayered_noise_generator) for more information.

## License
This project is licensed under the MIT license.