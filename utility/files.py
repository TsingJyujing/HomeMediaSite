import re


def filter_extension(filename, extensions):
    return re.search("\\.(%s)$" % "|".join(extensions), filename) is not None


regexp_image_file = re.compile("\\.(%s)$" % "|".join([
    "jpg",
    "jpeg",
    "bmp",
    "png",
    "gif"
]))


def filter_images(image_filename):
    return regexp_image_file.search(image_filename) is not None
