import praxyk
import json

def get_facial_data(img_path):
    """
    Detects facial features in the given image and returns a JSON-parseable
    string indicating the position of each feature.

    Args:
        filename (str): path to image to be evaluated

    Returns:
        str: JSON-parseable string describing facial features

    Raises:
        RuntimeError: If the given file does not exist or cannot be opened.
                      If CLandmark fails to initialize.
                      Any other C++ exception.
    """
    out = list()
    face = praxyk.praxyk_python.__detect_faces_in_image(img_path)
    for i in face:
        temp = dict()
        for key in i:
            temp[key] = [i[key].x, i[key].y]
        out.append(temp)
    return json.dumps(out, indent=2)
