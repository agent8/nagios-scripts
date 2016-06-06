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


results_list = [
    summarize3('Discovery', order_do_types=discovery_order_dotypes),

    summarize3('Scheduler Jobs'),
    summarize3('Scheduler Tasks'),
    summarize3('Notifications Android', order_do_types=push_order_dotypes),
    summarize3('Notifications iOS', order_do_types=push_order_dotypes),
    summarize3('Active User Count', order_do_types=activeuser_order),
    summarize3('Error Log Num'),
    summarize3('Nginx Status'),
    summarize3('Total Submitted Jobs'),
    summarize3('Begin Process'),
    summarize3('Finish Process'),

    summarize3('Total Process Message'),
    summarize3('Classify Process Message'),
    summarize3('CatchAll Invite')
]

send_email(results_list)
