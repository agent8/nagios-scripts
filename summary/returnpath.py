#!/usr/bin/env python
#coding=utf8
from utils import *


#stats_counts.returnpath_worker-python_worker_manager.production.i-92e03e32.returnpath.returnpath-gmail-classify.messages
results_list = [
    summarize(graphite_url, 'stats_counts.returnpath_worker*.production.*.returnpath.*classify', 'Message', extra_metric='.messages'),
    summarize(graphite_url, 'stats_counts.returnpath_worker*.production.*.returnpath.*classify', 'Process Day', extra_metric='.process_day'),
    summarize(graphite_url, 'stats_counts.returnpath_worker*.production.*.returnpath.blackbox.*', 'Message', sum_type={'offline_queue': 'avg'}, sum_total=False)
     ]

send_email(results_list, list, options.subject)