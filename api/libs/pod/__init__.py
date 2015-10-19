#!/usr/bin/python
import os                                                                                                                                        
import sys

sys.path.append('../../') 

import api
from models.sql import *

__all__ = ['bayes_spam_route', 'ocr_route']
