#!/usr/bin/python
import sys 
import os

user = os.expanduser("~")
sys.path.insert(0, user+'/praxyk-api-live/')
sys.path.insert(0, user+'/praxyk-api-live/api')
sys.path.insert(0, user+'/praxyk-api-live/api/')

from api import *
from api_server import *
from api import PRAXYK_API_APP as application

