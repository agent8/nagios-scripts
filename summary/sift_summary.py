#!/usr/bin/env python
#coding=utf8
from utils import *


#stats_counts.returnpath_worker-python_worker_manager.production.i-92e03e32.returnpath.returnpath-gmail-classify.messages
results_list = [
    summarize3('Sift Worker'),
    summarize3('Sift Extract'),
    summarize3('Sift Summary', order_by_name=True),
    summarize3('Open API'),
    summarize3('Open Nginx'),
    summarize3('Flight Worker'),
    summarize3('Shipment Worker'),
    summarize3('Api Service'),
     ]

send_email(results_list)