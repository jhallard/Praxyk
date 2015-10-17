#!/usr/bin/python
import os                                                                                                                                        
import sys

sys.path.append('../') 

import api
from models.sql import *

__all__ = ['users_route', 'results_route']
