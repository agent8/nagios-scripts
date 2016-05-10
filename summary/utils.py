#!/usr/bin/env python
# coding=utf8
import requests
import smtplib
import os
import os.path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from optparse import OptionParser
try:
    from requests.packages import urllib3
    urllib3.disable_warnings()
except:
    pass
from tornado import template

discovery_tools_url = 'https://discovery-tools-staging.easilydo.com/metrics'

graphite_url = "https://edo_graphite_reader:very_secret@graphite.easilydo.com"


duration = 60
subject = ''
email_list = ['waiting@easilydo.com', 'ping@easilydo.com']

parser = OptionParser()

parser.add_option("--duration", dest="duration",
                  help="duration", type="int", default=1440)
parser.add_option("--subject",
                  dest="subject", default='',
                  help="Email Subject")
parser.add_option('--emails', default='waiting@easilydo.com', dest="emails")
parser.add_option('--compare_hour', action='store_true', dest="compare_hour", default=False)
parser.add_option('--date', dest="date", default='')


(options, args) = parser.parse_args()

if options.duration > 60:
    subject = 'Daily Summary'
else:
    subject = 'Hourly Summary'

if options.subject:
    subject = '%s - %s' % (subject, options.subject)


def get_total(cache):
    total = 0
    cache = cache[0]
    for point in cache['datapoints']:
        try:
            point = point[0]
            if not point:
                continue
        except:
            continue
        total += float(point)
    return total


def get_avg(cache):
    total = 0
    cache = cache[0]

    for point in cache['datapoints']:
        try:
            point = point[0]
            if not point:
                continue
        except:
            continue
        total += float(point)
    total /= len(cache['datapoints'])
    return total


def get_latest(cache):
    total = 0
    cache = cache[0]

    for point in cache['datapoints']:
        try:
            point = point[0]
            if not point:
                continue
        except:
            continue
        return float(point)
    return total


def get_query_path(base_path):
    local_graphite_url = graphite_url
    url = '%(local_graphite_url)s/metrics/find?query=%(base_path)s' % locals()
    print 'query path>>>', url
    try:
        res = requests.get(url, verify=False)
        return res.json()
    except:
        import traceback; traceback.print_exc();
        print "Could not get Job from graphite server. Will not setup checks", url

    return []

def get_query_data(metric, sum_type='sum'):
    local_graphite_url = graphite_url

    if sum_type == 'latest':
        sum_metrics = "sumSeries(sum(%(metric)s))" % locals()
    else:
        sum_metrics = "sumSeries(%(sum_type)s(%(metric)s))" % locals()
    local_duration = options.duration

    if sum_type == 'latest':
        local_duration = 60

    if options.compare_hour:
        metrics = {"yesterday": sum_metrics,
           "day_before": "timeShift(%(sum_metrics)s,'-1h')" % locals(),
           "week_before": "timeShift(%(sum_metrics)s,'-2h')" % locals()
           }
        local_duration = 60
    else:
        metrics = {"yesterday": sum_metrics,
               "day_before": "timeShift(%(sum_metrics)s,'-1d')" % locals(),
               "week_before": "timeShift(%(sum_metrics)s,'-1w')" % locals()
               }
    total = {}
    for id, metric in metrics.items():
        if sum_type == 'latest':
            url = "%(local_graphite_url)s/render?target=%(metric)s&format=json" % locals()
        else:
            url = "%(local_graphite_url)s/render?target=%(metric)s&from=-%(local_duration)smin&format=json" % locals()
        print 'sum_metrics>>>', url
        resp = {}
        try:
            resp = requests.get(url, verify=False).json()
        except:
            print "Could not get info from graphite server -%s %s" % (url, metric)

        if not resp:
            continue
        if sum_type == 'latest':
            total[id] = int(get_latest(resp))
        else:
            if sum_type == 'avg':
                total[id] = int(get_avg(resp))
            else:
                total[id] = int(get_total(resp))

        if not total[id]:
            total[id] = 0
    return {'yesterday': total.get('yesterday', 0) or 0, 'day_before': total.get(
        'day_before', 0) or 0, 'week_before': total.get('week_before', 0) or 0}


def summarize_result(base_path, extra_metric='', sum_type='sum', do_type_prefix=''):
    results = {}
    do_types = {}
    # stats_counts.scheduler.production.i-60ac6a05.job_success.addcalendaritem

    do_types = get_query_path(base_path)
    if not do_types:
        print 'not found metric', base_path
        return

    for item in do_types:
        do_type = do_type_prefix + item['text']
        item_id = item['id']
        metric = '%(item_id)s%(extra_metric)s' % locals()

        if isinstance(sum_type, dict):
            real_sum_type = sum_type.get(do_type, sum_type.get('', 'sum'))
        else:
            real_sum_type = sum_type

        result = get_query_data(metric, real_sum_type)
        if result:
            results[do_type] = result
    return results


def summarize_total(title, results, order_do_types=None, order_by_name=None, sum_total=True):
    if not order_by_name:
        if not order_do_types:
            new_results = sorted(
                results.items(), key=lambda x: x[1]['yesterday'] or 0, reverse=True)
        else:
            new_results = []
            for d in order_do_types:
                if d in results:
                    new_results.append([d, results[d]])
                    del results[d]

            new_results += sorted(results.items(),
                                  key=lambda x: x[1]['yesterday'] or 0, reverse=True)
    else:
        new_results = sorted(results.items(), key=lambda x: x[0])

    if sum_total:
        total_count = {'yesterday': 0, 'day_before': 0, 'week_before': 0}
        for key, count in new_results:
            yesterday = count['yesterday']
            day_before = count['day_before']
            week_before = count['week_before']
            if yesterday is None or day_before is None or week_before is None:
                continue
            total_count['yesterday'] += yesterday
            total_count['day_before'] += day_before
            total_count['week_before'] += week_before

        new_results.append(['Total', total_count])

    return {'title': title, 'results': new_results}


def summarize(base_path, title, order_do_types=None, extra_metric='', sum_type='sum', sum_total=True):
    results = summarize_result(base_path, extra_metric, sum_type)

    return summarize_total(title, results, order_do_types, sum_total=sum_total)


def summarize2(base_path, title, order_do_types=None, sum_total=1, name_index=-1):
    url = '/get_log_summary/?metrics=%s&name_index=%s&sum_total=0&date=%s' % (base_path, name_index, options.date)
    url = discovery_tools_url + url
    print url
    res = requests.get(url)

    return summarize_total(title, res.json(), order_do_types, sum_total=sum_total)


def summarize3(base_path, title, sum_total=1):
    url = '/get_daily_summary/?group=%s&sum_total=0&date=%s' % (base_path, options.date)
    url = discovery_tools_url + url
    print url
    res = requests.get(url)

    return summarize_total(title, res.json(), order_by_name=True, sum_total=sum_total)


def format_percent(current, past):
    if past:
        percent = round((current / float(past)) * 100.0, 2)
    else:
        percent = 100

    return percent


template_file = os.path.dirname(__file__) + '/summary_email.html'

def send_email(results_list):
    content = ""
    template_string = file(template_file).read()
    tpl = template.Template(template_string)
    for results in results_list:
        new_results = results['results']
        if not new_results:
            continue

        for key, count in new_results:
            yesterday = count['yesterday']
            day_before = count['day_before']
            week_before = count['week_before']

            percent_html = format_percent(yesterday, day_before)
            percent_html_week = format_percent(yesterday, week_before)
            
            count['percent'] = percent_html
            count['percent_week'] = percent_html_week

    body = tpl.generate(results_list=results_list, options=options)

    from_email = 'developer@easilydo.com'


    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email

    part2 = MIMEText(body, 'html')
    msg.attach(part2)

    smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(from_email, 'secret008')

    emails = options.emails.split(',')
    msg['To'] = emails[0]
    msg['CC'] = ','.join(emails[1:])
    smtpserver.sendmail(from_email, emails, msg.as_string())

    smtpserver.close()

