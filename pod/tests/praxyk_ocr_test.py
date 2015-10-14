#!/usr/bin/env python

import praxyk

import os
import sys
import traceback

#
# For now, until we come up with a more permanent solution,
# store the relevant test images in a set location, and use
# an environment variable (PRAXYK_IMAGES_DIR) to give the path
# to where they are stored.
#

def test_empty_image():
    try:
        images_dir = os.environ["PRAXYK_IMAGES_DIR"]
        empty_image = os.path.join(images_dir, "empty.png")
        image_str = praxyk.get_string_from_image(empty_image)
        if image_str != "":
            raise RuntimeError("Praxyk detected a string in an empty image.")

        return True
    except:
        print
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=5, file=sys.stdout)
        return False

def test_typed_text():
    try:
        images_dir = os.environ["PRAXYK_IMAGES_DIR"]
        typed_image = os.path.join(images_dir, "typed_text.png")
        image_str = praxyk.get_string_from_image(typed_image)
        if image_str == "":
            raise RuntimeError("Praxyk detected no string in image with typed text.")
        # TODO: check actual string

        return True
    except:
        print
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=5, file=sys.stdout)
        return False

if __name__ == "__main__":
    successful = test_empty_image() and test_typed_text()
    sys.exit(0 if successful else 1)
