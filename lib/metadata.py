import os
import json

from PIL import Image
from PIL.TiffImagePlugin import IFDRational
from PIL.ExifTags import TAGS, GPSTAGS


def extract_metadata(image) -> dict:
    try:
        image = Image.open(image)
    except IOError:
        raise

    exif = {}
    try:
        for tag, value in image._getexif().items():
            if tag in TAGS:
                # tags are stored as numbers
                # convert them to strings
                exif[TAGS[tag]] = value
    except AttributeError:
        # empty exif data
        return exif

    try:
        gpsinfo = {}
        for key in exif['GPSInfo'].keys():
            key_str = GPSTAGS.get(key, key)
            value = exif['GPSInfo'][key]
            gpsinfo[key_str] = value
        exif['GPSInfo'] = gpsinfo
    except KeyError:
        # pass if there is no gpsinfo
        pass

    return exif
