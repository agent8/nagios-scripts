#!/usr/bin/env python
# coding=utf8
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from optparse import OptionParser
try:
    from requests.packages import urllib3
    urllib3.disable_warnings()
except:
    pass

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
        sum_metrics = metric
    else:
        sum_metrics = "sumSeries(%(sum_type)s(%(metric)s)" % locals()

    if options.compare_hour:
        metrics = {"yesterday": sum_metrics,
           "day_before": "timeShift(%(sum_metrics)s,'-1h')" % locals(),
           "week_before": "timeShift(%(sum_metrics)s,'-2h')" % locals()
           }
    else:
        metrics = {"yesterday": sum_metrics,
               "day_before": "timeShift(%(sum_metrics)s,'-1d')" % locals(),
               "week_before": "timeShift(%(sum_metrics)s,'-1w')" % locals()
               }
    total = {}
    for id, metric in metrics.items():
        local_duration = options.duration
        url = "%(local_graphite_url)s/render?target=%(metric)s&from=-%(local_duration)smin&format=json" % locals()
        print url
        resp = {}
        try:
            resp = requests.get(url, verify=False).json()
        except:
            print "Could not get info from graphite server -%s %s" % (url, metric)

        if not resp:
            continue
        if sum_type == 'latest':
            total[id] = int(get_latest(resp))
        if sum_type == 'avg':
            total[id] = int(get_avg(resp))
        else:
            total[id] = int(get_total(resp))

        if not total[id]:
            total[id] = 0
    return {'yesterday': total.get('yesterday', 0), 'day_before': total.get(
        'day_before', 0), 'week_before': total.get('week_before', 0)}


def summarize_result(base_path, extra_metric='', sum_type='sum'):
    results = {}
    do_types = {}
    # stats_counts.scheduler.production.i-60ac6a05.job_success.addcalendaritem

    do_types = get_query_path(base_path)
    if not do_types:
        return

    for item in do_types:
        do_type = item['text']
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
        new_results = sorted(results.items(), key=lambda x: x[1])

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


def format_percent(current, past):
    color = 'green'
    flag = False
    if past:
        percent = (current / float(past)) * 100.0
        flag = (percent > 130 or percent < 50)
        percent_change = percent - 100
    else:
        percent_change = 0

    if percent_change < 0:
        color = 'red'

    str_percent = '%.2f' % percent_change
    html = "<font color='%(str_percent)s'>%(str_percent)s %%</font>" % locals()
    if flag:
        html = "<b>%(html)s</b>" % locals()

    return html


def send_email(results_list):
    content = ""
    for results in results_list:
        new_results = results['results']
        if not new_results:
            continue

        if options.compare_hour:
            content += "<br><table border=1><tr><td>%s</td><td>Last Hour</td><td>Hour Before</td><td>Change</td><td>2 Hour Before</td><td>Change</td></tr>" % (
            results['title'], )
        else:
            content += "<br><table border=1><tr><td>%s</td><td>Yesterday</td><td>Day Before</td><td>Change</td><td>Week Before</td><td>Change</td></tr>" % (
            results['title'], )

        for key, count in new_results:
            #count = results['results'][key]
            yesterday = count['yesterday']
            day_before = count['day_before']
            week_before = count['week_before']

            percent_html = format_percent(yesterday, day_before)
            percent_html_week = format_percent(yesterday, week_before)
            content += "<tr><td>%(key)s</td><td>%(yesterday)s</td><td>%(day_before)s</td><td>%(percent_html)s</td><td>%(week_before)s</td><td>%(percent_html_week)s</td></tr>" % locals()

        content += "</table><hr><br>"

    body = """<html>
<body>
%s
</body>
</html>
""" % (content,)


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

    for to in options.emails.split(','):
        msg['To'] = to
        smtpserver.sendmail(from_email, to, msg.as_string())

    smtpserver.close()

