#!/usr/bin/env python
#coding=utf8
from utils import *


#stats_counts.returnpath_worker-python_worker_manager.production.i-92e03e32.returnpath.returnpath-gmail-classify.messages
results_list = [
    summarize3('Sift Summary', 'Sift Summary', sum_total=0),
    ]

send_email(results_list)