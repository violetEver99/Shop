# -*- coding: utf-8 -*-
##############################################################################
# FileName: logger\views.py
# Description: web日志模块, 只在标准输出流中打印日志
# Version: V1.0
# Author: Qiurong
# Function List:
#   1. ------ 
#   2. -----
# History:
#	<author>		<time>		<version>		<desc>
#	Qiurong		    2016/8/16	V1.0			创建文件
###############################################################################
from django.conf import settings
import logging, logging.handlers
import os

logger = logging.getLogger("mylog")
logger.setLevel(logging.DEBUG)

filePath = settings.LOG_PATH
if not os.path.exists(filePath):
    os.mkdir(filePath)
formatter = logging.Formatter("[%(asctime)s][%(filename)s][%(funcName)s][Line:%(lineno)d][%(levelname)s]:%(message)s")

fileHandle = logging.handlers.RotatingFileHandler(filePath + os.sep + "log.log", maxBytes=(10*(1<<20)), backupCount=5)
fileHandle.setFormatter(formatter)
logger.addHandler(fileHandle)
