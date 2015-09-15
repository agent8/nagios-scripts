#!/usr/bin/env python
#coding=utf8
from utils import *

results_list = [
        summarize('stats_counts.do_engine.production.new_connections.platform.ios.*', 'iOS New Connection'),
        summarize('stats_counts.do_engine.production.new_connections.platform.android.*', 'Android New Connection'),
        summarize('stats_counts.do_engine.production.locale.en_US.*', 'en_US'),
        summarize('stats_counts.do_engine.production.expired_connections.platform.ios.*', 'iOS Expired Connection'),
        summarize('stats_counts.do_engine.production.expired_connections.platform.android.*', 'Android Expired Connection'),
        summarize('stats_counts.do_engine.production.reconnected_connections.platform.ios.*', 'iOS  ReConnection'),
        summarize('stats_counts.do_engine.production.reconnected_connections.platform.android.*', 'Android  ReConnection'),
        summarize('stats_counts.do_engine.production.locale.other.*', 'Other Locale'),

        summarize('stats.gauges.redis.production.processed_connections.en_US.*.*', 'en_US Processed Connections', sum_type='latest'),
        summarize('stats.gauges.redis.production.processed_connections.*.*.*', 'All Processed Connections', sum_type='latest'),
        ]

send_email(results_list)