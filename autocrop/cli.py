import argparse
import os
import shutil
import sys

from PIL import Image

from .__version__ import __version__
from .autocrop import Cropper, ImageReadError
from .constants import (
    QUESTION_OVERWRITE,
    CV2_FILETYPES,
    PILLOW_FILETYPES,
)

COMBINED_FILETYPES = CV2_FILETYPES + PILLOW_FILETYPES
INPUT_FILETYPES = COMBINED_FILETYPES + [s.upper() for s in COMBINED_FILETYPES]


def output(filename, image):
    """
    Move the input file to the output location and write over it with the
    cropped image data.
    """
    # Encode the image as an in-memory PNG
    img_new = Image.fromarray(image)
    # Write the new image (converting the format to match the output
    # filename if necessary)
    img_new.save(filename)


def main(
    input_f, fheight=500, fwidth=500, facePercent=50
):
    """
    Crops folder of images to the desired height and width if a
    face is found.

    If `input_f == output_d` or `output_d is None`, overwrites all files
    where the biggest face was found.

    Parameters:
    -----------

    - `input_f`: `str`
        * Image path.
    - `fheight`: `int`, default=`500`
        * Height (px) to which to crop the image.
    - `fwidth`: `int`, default=`500`
        * Width (px) to which to crop the image.
    - `facePercent`: `int`, default=`50`
        * Percentage of face from height.

    """
    input_filename = input_f


    # Main loop
    cropper = Cropper(width=fwidth, height=fheight, face_percent=facePercent)

    # Attempt the crop
    try:
        image = cropper.crop(input_filename)
    except ImageReadError:
        print("Read error:       {}".format(input_filename))
        return ''

    # Did the crop produce an invalid image?
    if isinstance(image, type(None)):
        print("Face crop failed")
    else:
        output(input_filename, image)
        print("Face crop complete")


def input_path(p):
    """Returns path, only if input is a valid directory."""
    no_file = "Input file does not exist"
    no_image = "Input file is not an image"
    p = os.path.abspath(p)
    if not os.path.isfile(p):
        raise argparse.ArgumentTypeError(no_file)
    filetype = os.path.splitext(p)[-1]
    if not filetype in INPUT_FILETYPES:
        raise argparse.ArgumentTypeError(no_image)
    else:
        return p


def output_path(p):
    """
    Returns path, if input is a valid directory name.
    If directory doesn't exist, creates it.
    """
    p = os.path.abspath(p)
    if not os.path.isdir(p):
        os.makedirs(p)
    return p


def size(i):
    """Returns valid only if input is a positive integer under 1e5"""
    error = "Invalid pixel size"
    try:
        i = int(i)
    except ValueError:
        raise argparse.ArgumentTypeError(error)
    if i > 0 and i < 1e5:
        return i
    else:
        raise argparse.ArgumentTypeError(error)


def chk_extension(extension):
    """Check if the extension passed is valid or not."""
    error = "Invalid image extension"
    extension = str(extension).lower()
    if not extension.startswith("."):
        extension = f".{extension}"
    if extension in COMBINED_FILETYPES:
        return extension.lower().replace(".", "")
    else:
        raise argparse.ArgumentTypeError(error)


def parse_args(args):
    """Helper function. Parses the arguments given to the CLI."""
    help_d = {
        "desc": "Automatically crops faces from batches of pictures",
        "input": """Image file location""",
        "width": "Width of cropped files in px. Default=500",
        "height": "Height of cropped files in px. Default=500",
        "facePercent": "Percentage of face to image height",
    }

    parser = argparse.ArgumentParser(description=help_d["desc"])
    parser.add_argument(
        "-i", "--input", default=".", type=input_path, help=help_d["input"]
    )
    parser.add_argument("-w", "--width", type=size, default=500, help=help_d["width"])
    parser.add_argument("-H", "--height", type=size, default=500, help=help_d["height"])
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s version {}".format(__version__),
    )
    parser.add_argument(
        "--facePercent", type=size, default=50, help=help_d["facePercent"]
    )

    return parser.parse_args()


def command_line_interface():
    """
    AUTOCROP
    --------
    Crops faces from batches of images.
    """
    args = parse_args(sys.argv[1:])

    print("Processing image:", args.input)

    main(
        args.input,
        args.height,
        args.width,
        args.facePercent,
    )
