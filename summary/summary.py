#!/usr/bin/env python
# coding=utf8
from utils import *

discovery_order_dotypes = [
    'facebook_birthday_discovery',
    'facebook_important_post_discovery',
    'facebook_popular_post_discovery',
    'facebook_daily_photo_discovery',
    'contact_discovery',
    'calendar_invite_discovery',
    'itunes_free_song_discovery',
    'itunes_free_app_discovery',
    'facebook_event_discovery',
    'shipment_discovery',
    'receipt_discovery',
    'deal_discovery',
    'job_changes_discovery'
]

push_order_dotypes = [
    '100__birthdays',
    '2045__important_email_alerts',
    '2052__important_posts',
    '2073__tagged_photos_of_me',
    '10__contact_information',
    '500__bad_weather_alerts',
    '2068__meeting_setup',
    '2070__job_changes',
    '106__free_itunes_single_of_the_week',
    '2006__free_app_of_the_week',
    '500__bad_weather_alerts',
    '2071__daily_top_photos'
]

activeuser_order = [
    'prod-ActiveUsers', 'prod-ActiveUsers-EmailEnabled', 'prod-ActiveUsers-FacebookEnabled'
]


def summarize_message():
    base_path = 'stats_counts.worker.production.*.mailhandler'
    do_types = get_query_path("%(base_path)s.*" % locals())

    results = {}
    for x in do_types:
        txt = x['text']
        results.update(summarize_result(
            "%(base_path)s.%(txt)s.*" % locals(), '', 'sum', txt))

    return summarize_total('Classify Process Message', results)


results_list = [
    summarize('stats_counts.worker.production.*.*.discovery_count.*',
              'Discovery', discovery_order_dotypes),
    summarize('stats_counts.scheduler.production.*.job_success.*',
              'Scheduler Jobs'),
    summarize('stats_counts.scheduler.production.*.tasks.number.*',
              'Scheduler Tasks'),
    summarize('stats_counts.push_notifications.production.*.notifications.pushs.android.*',
              'Notifications Android', push_order_dotypes),
    summarize('stats_counts.push_notifications.production.*.notifications.pushs.ios.*',
              'Notifications iOS', push_order_dotypes),
    summarize('stats.gauges.dynamodb.prod-ActiveUsers*',
              'Active User Count', activeuser_order, '.item_count', 'avg'),
    summarize('stats_counts.log_center.production.error_log.*', 'Error Log Num'),

    summarize('stats_counts.worker.production.*.tms.*',
              'TMS Success', None, '.SUCCESS'),
    summarize('stats_counts.worker.production.*.tms.*',
              'TMS Fail', None, '.FAIL'),
    summarize('stats_counts.nginx.production.response_error.*', 'Nginx Status'),
    summarize('stats_counts.job_server.production.*.total_submitted_jobs.*',
              'Total Submitted Jobs'),
    summarize('stats_counts.worker.production.*.*',
              'Begin Process', None, '.begin_process'),
    summarize('stats_counts.worker.production.*.*',
              'Finish Process', None, '.finish_process'),

    summarize('stats_counts.worker.production.*.mailhandler.*.*',
              'Total Process Message'),
    summarize_message()
]

send_email(results_list)
