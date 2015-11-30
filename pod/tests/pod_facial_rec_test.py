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

def test_one_face_image():
    try:
        # If system not set up, don't necessarily fail
        if "PRAXYK_IMAGES_DIR" not in os.environ:
            return True

        images_dir = os.environ["PRAXYK_IMAGES_DIR"]
        image_path = os.path.join(images_dir, "one_face.png")
        faces = praxyk.praxyk_python.__detect_faces_in_image(image_path)
        if len(faces) < 1:
            raise RuntimeError("Praxyk did not detect required face.")

        return True
    except:
        print
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=5, file=sys.stdout)
        return False

def test_two_faces_image():
    try:
        # If system not set up, don't necessarily fail
        if "PRAXYK_IMAGES_DIR" not in os.environ:
            return True

        images_dir = os.environ["PRAXYK_IMAGES_DIR"]
        image_path = os.path.join(images_dir, "two_faces.png")
        faces = praxyk.praxyk_python.__detect_faces_in_image(image_path)
        if len(faces) < 2:
            raise RuntimeError("Praxyk did not detect required faces.")

        return True
    except:
        print
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=5, file=sys.stdout)
        return False

if __name__ == "__main__":
    successful = test_one_face_image() and test_two_faces_image()
    sys.exit(0 if successful else 1)
