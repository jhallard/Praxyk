from __future__ import print_function
import os
import sys
import json
import binhex
import praxyk
# import Image

STORE_BASENAME = "/drive1/img_store/"
class ImgPack(object):
    def __init__(self, img_path, img_user, user_token):
        self.is_img = True
        '''
        Image descriptor class
        '''
        self.img_name = os.path.basename(img_path)
        self.img_path = img_path
        self.img_text = str()
        self.img_user = img_user
        self.user_token = user_token
        self.data = read_img(img_path)

    def dump_data(self):
        print('Image: %s' % self.img_name)
        print('  text: %s' % self.img_text)
        print('User: %s' % self.img_user)
        print('  User authentication token: %s' % self.user_token)

class DataPack(object):
    '''
    Class for JSON data for use at a later date.
    '''
    def __init__(self, user, user_token, data):
        self.is_img = False
        self.user = user
        self.data = json.loads(data)
        self.user_token = user_token

    def dump_data(self):
        print('Data: %s' % json.dumps(self.data))
        print('User: %s' % self.user)
        print('  User authentication token: %s' % self.user_token)

# http://pythontips.com/2014/01/15/the-open-function-explained/#more-416
def read_img(img_path):
    '''
    Reads an image file to memory
    '''
    with open(img_path, 'r+') as f:
        jpgdata = f.read()
    return jpgdata

def get_data_img(img_path, user, user_token):
    '''
    Function that creates image object.  Can be expanded on later
    '''
    data = DataPack(img_path, user, user_token)
    return data

def get_data_other(user, user_token, data_path):
    data_to_obj = json.load(data_path)
    data = DataPack(user, user_token, data_to_obj)
    return data

def run_img_rec(img_path):
    '''
    Runs OCR.  Takes in a local path to an image file, and returns an image
    descriptor object with the text object filled out.
    '''
    data = ImgPack(img_path, 'foo', 'bar')
    print('Transferring image data to %s...' % (STORE_BASENAME + data.img_name))
    img_out = open(STORE_BASENAME + data.img_name, 'w+')
    img_out.write(data.data)
    img_out.close()
    print('{Running OCR...}')
    try:
        data.img_text = praxyk.get_string_from_image(STORE_BASENAME + data.img_name)
    except Exception as e:
        print('Error running OCR: %s' % str(e))
        return ''
    data.dump_data()
    print('This is where data can be returned to the user')
    return data.img_text

def hello():
    print('Hello, world!')
