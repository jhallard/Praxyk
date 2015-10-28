import praxyk
import json

def get_facial_data(img_path):
    out = list()
    face = praxyk.detect_faces_in_image("/home/mike/Downloads/face-01.jpg")
    for i in face:
        temp = dict()
        for key in i:
            temp[key] = [i[key].x, i[key].y]
        out.append(temp)
    return json.dumps(out, indent=2)
