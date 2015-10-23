import os, sys, json, redis
from rq import Queue, Connection
import datetime
import rom
from models.nosql.result_base import *


class Result_POD_OCR(ResultBase) :
    RESULT_ACTIVE   = "active"   # means the result is being computed
    RESULT_FINISHED = "finished" # means computation is finished
    RESULT_FAILED   = "failed"   # means computation failed

    result_string = rom.Text()

    RESULT_ACTIVE   = "active"   # means the result is being computed
    RESULT_FINISHED = "finished" # means computation is finished
    RESULT_FAILED   = "failed"   # means computation failed
