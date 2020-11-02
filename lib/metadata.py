import os
import json

from PIL import Image
from PIL.ExifTags import TAGS

def extract_metadata(image_file_path: str) -> dict:
    try:
        image = Image.open(image_file_path)
    except IOError:
        # make sure to log this error later to a logger file
        raise Exception(IOError)

    exif = {}
    try:
        for tag, value in image._getexif().items():
            try:
                value = value.decode('utf-8')
            except (UnicodeDecodeError, AttributeError):
                pass

            value = str(value)

            if tag in TAGS:
                exif[TAGS[tag]] = value


    except AttributeError:
        # no exif data
        exif = {}

    return exif

# extract_metadata('../data/reel.jpg')
