#!/usr/bin/env python
#coding=utf8
from utils import *


#stats_counts.returnpath_worker-python_worker_manager.production.i-92e03e32.returnpath.returnpath-gmail-classify.messages
results_list = [
    summarize('stats_counts.returnpath_worker*.production.*.returnpath.*classify', 'Unique User', extra_metric='.finish_all_process'),
    summarize('stats_counts.returnpath_worker*.production.*.returnpath.*classify', 'Message', extra_metric='.messages'),
    summarize('stats_counts.returnpath_worker*.production.*.returnpath.*classify', 'Process Day', extra_metric='.process_day')
     ]

send_email(results_list)