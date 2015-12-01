#!/usr/bin/env python                                                                                                                                

## @auth John Allard, Nick Corgan, Nick Church, others
## @date Oct 2015
## @github https://github.com/jhallard/praxyk
## @license MIT

import os, sys, json, redis
from rq import Queue, Connection
import datetime
import rom
from models.nosql.result_base import *


class Result_POD_Face_Detect(ResultBase) :
	num_faces = rom.Integer()
        faces_json = rom.Text()
	faces_detected = rom.OneToMany('DetectedFace', column='result_face_detect')


# @info - This class represents a single detected face in an image that can have
#         multiple faces inside of it. This models forms a many-to-one relationship
#         with the Result_POD_FaceDetect class. All of the fields in this class 
#         correspond to different features of a given face
class DetectedFace(rom.Model) :

	result_face_detect = rom.ManyToOne('Result_POD_FaceDetect', on_delete='set null')
	brow_ll = rom.Float()
	brow_lc = rom.Float()
	brow_lr = rom.Float()
	brow_rl = rom.Float()
	brow_rc = rom.Float()
	brow_rr = rom.Float()
	canthi_ll = rom.Float()
	canthi_lr = rom.Float()
	nose_root = rom.Float()
	canthi_rl = rom.Float()
	canthi_rr = rom.Float()
	ear_l = rom.Float()
	nose_l = rom.Float()
	nose_tip = rom.Float()
	nose_r = rom.Float()
	ear_r = rom.Float()
	mouth_corner_l = rom.Float()
	mouth_upper = rom.Float()
	mouth_lower = rom.Float()
	mouth_corner_r = rom.Float()
	chin = rom.Float()

