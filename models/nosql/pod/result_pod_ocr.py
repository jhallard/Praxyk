#!/usr/bin/env python                                                                                                                                

## @auth John Allard, Nick Church, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

import os, sys, json, redis
from rq import Queue, Connection
import datetime
import rom
from models.nosql.result_base import *


# @info - This class defines a result object specific to the Optical 
#	  character recognition service. We dervice from the ResultBase
#	  class which contains all of the meta data common to all results,
#	  and the only member that this class adds is the result_string which
#	  is the prediction returned by the Praxyk OCR libraries.
class Result_POD_OCR(ResultBase) :
    result_string = rom.Text()
