#!/usr/bin/env python
#coding=utf8
from utils import *

results_list = [
        summarize('stats_counts.do_engine.production.new_connections.platform.ios.*', 'iOS New Connections'),
        summarize('stats_counts.do_engine.production.new_connections.platform.android.*', 'Android New Connections'),
        summarize('stats_counts.do_engine.production.new_connections.locale.en_US.*', 'en_US New Connections'),
        summarize('stats_counts.do_engine.production.expired_connections.platform.ios.*', 'iOS Expired Connections'),
        summarize('stats_counts.do_engine.production.expired_connections.platform.android.*', 'Android Expired Connections'),
        summarize('stats_counts.do_engine.production.expired_connections.locale.en_US.*', 'en_US Expired Connections'),
        
        summarize('stats_counts.do_engine.production.reconnected_connections.platform.ios.*', 'iOS  ReConnections'),
        summarize('stats_counts.do_engine.production.reconnected_connections.platform.android.*', 'Android  ReConnections'),
        summarize('stats_counts.do_engine.production.reconnected_connections.locale.en_US.*', 'en_US ReConnections'),
        
        summarize('stats_counts.do_engine.production.new_connections.locale.other.*', 'Other Locale New Connections'),
        summarize('stats_counts.do_engine.production.expired_connections.locale.other.*', 'Other Locale Expired Connections'),
        summarize('stats_counts.do_engine.production.reconnected_connections.locale.other.*', 'Other Locale ReConnections'),

        summarize2('%returnpath.returnpath%', 'Unique User', name_index=-2),
        summarize('stats_counts.job_server.production.*.total_submitted_jobs.returnpath*',
              'Total Submitted Jobs'),
    
        ]

send_email(results_list)