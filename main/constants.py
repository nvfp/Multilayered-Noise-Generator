import os


SOFTWARE_VER = '1.1.0'
SOFTWARE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOFTWARE_NAME = os.path.basename(SOFTWARE_DIR)

TMP_DIR = os.path.join(SOFTWARE_DIR, 'tmp')  # to store the base-noise files
OUTPUT_DIR = os.path.join(SOFTWARE_DIR, 'output')