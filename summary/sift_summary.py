#!/usr/bin/env python
#coding=utf8
from utils import *


#stats_counts.returnpath_worker-python_worker_manager.production.i-92e03e32.returnpath.returnpath-gmail-classify.messages
results_list = [
    summarize3('Sift Worker', 'Sift Worker'),
    summarize3('Sift Extract', 'Sift Extract'),
    summarize3('Open DB', 'Open DB'),
    summarize3('Open API', 'Open API'),
    summarize3('Open Nginx', 'Open Nginx'),
    summarize3('Flight Worker', 'Flight Worker'),
    summarize3('Shipment Worker', 'Shipment Worker'),
    summarize3('Api Service', 'Api Service'),
     ]

send_email(results_list)