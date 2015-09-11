#!/usr/bin/env python
#coding=utf8
from utils import *

def summary_locale():
    result = get_query_data('stats_counts.do_engine.production.*', extra_metric='.en_US.*.*')
    results[do_type] = result

results_list = [
        summarize('stats_counts.do_engine.production.new_connections.*.ios.*', 'iOS New Connection'),
        summarize('stats_counts.do_engine.production.new_connections.*.android.*', 'Android New Connection'),
        summarize('stats_counts.do_engine.production.*', 'en_US', extra_metric='.en_US.*.*'),
        summarize('stats_counts.do_engine.production.expired_connections.*.ios.*', 'iOS Expired Connection'),
        summarize('stats_counts.do_engine.production.expired_connections.*.android.*', 'Android Expired Connection'),
        summarize('stats_counts.do_engine.production.reconnected_connections.*.ios.*', 'iOS  ReConnection'),
        summarize('stats_counts.do_engine.production.reconnected_connections.*.android.*', 'Android  ReConnection'),
        summarize('stats_counts.do_engine.production.*', 'All Locale', extra_metric='.*.*.*'),

        summarize('stats.gauges.redis.production.processed_connections.en_US', 'en_US Processed Connections', extra_metric='.*.*', sum_type='avg'),
        summarize('stats.gauges.redis.production.processed_connections.*.*.*', 'All Processed Connections', sum_type='avg'),
        ]

send_email(results_list)