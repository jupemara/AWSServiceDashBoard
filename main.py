#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import HTMLParser
# For python 3.X
except ImportError:
    from html import parser as HTMLParser
import datetime
import logging
import optparse
import os
import re
import urllib2
import xml.etree.ElementTree


DEFAULT_VALUES = {
    'service_health_dashboard_url': 'http://status.aws.amazon.com/',
    'log_level': 'DEBUG',
    'region': 'us-east-1',
    'duration': '0',
    'chat_integration': 'stdout',
    'chat_api_token': None,
    'chat_api_channel_id': None
}

RSS_PREFIX = 'rss'

def get_args():

    usage = (
        'This script gets AWS Health Dashboard status. '
        'See "https://github.com/JumpeiArashi/AWSServiceDashBoard"'
        'if your want detail.'
    )
    parser = optparse.OptionParser(usage=usage)

    parser.add_option(
        '--health-dashboard-url', '-u',
        type='string', default=DEFAULT_VALUES['service_health_dashboard_url'],
        dest='service_health_dashboard_url',
        help='AWS Service Health Dashboard URL.'
    )

    parser.add_option(
        '--log-level', '-l',
        type='choice', default=DEFAULT_VALUES['log_level'],
        dest='log_level',
        choices=[
            'DEBUG',
            'INFO',
            'WARNING',
            'ERROR',
            'CRITICAL'
        ],
        help=(
            'Script log level. You can choose one in '
            '"DEBUG", "INFO", "WARNING", "ERROR" or "CRITICAL".'
        )
    )

    parser.add_option(
        '--duration', '-D',
        type='string', default=DEFAULT_VALUES['duration'],
        help='Time duration.'
    )

    parser.add_option(
        '--region', '-R',
        type='string', default=DEFAULT_VALUES['region'],
        help=(
            'AWS region name. '
            'You can multiple regions by using comma as delimiter.'
        ),
    )

    parser.add_option(
        '--chat-integration', '-C',
        type='choice', default=DEFAULT_VALUES['chat_integration'],
        choices=[
            'stdout',
            'chatwork',
            'slack'
        ],
        dest='chat_integration',
        help=(
            'You can specify any channel. We support "chatwork" and "slack".'
        )
    )

    parser.add_option(
        '--chat-api-token', '-k',
        type='string', default=DEFAULT_VALUES['chat_api_token'],
        dest='chat_api_token',
        help=(
            'Chat API Token.'
        )
    )

    parser.add_option(
        '--chat-api-channel-id', '-c',
        type='string', default=DEFAULT_VALUES['chat_api_channel_id'],
        dest='chat_api_channel_id',
        help=(
            'Chat channel ID(in other words, room ID ).'
        )
    )

    arguments = parser.parse_args()[0]
    return arguments


def set_log_level(log_level=DEFAULT_VALUES['log_level']):
    logging.basicConfig(
        format='[%(levelname)s] %(message)s',
        level=getattr(logging, log_level)
    )


def get_all_regions_rss(
    service_health_dashboard_url=DEFAULT_VALUES['service_health_dashboard_url']
):
    """
    Get all regions RSS feeds.
    :param str service_health_dashboard_url: AWS Service Health Dashboard URL
    :rtype: list
    :return: List RSS feeds of each regions
    """
    health_dashboard_html = urllib2.urlopen(
        service_health_dashboard_url
    ).read()
    logging.debug(health_dashboard_html)
    health_dashboard_et = xml.etree.ElementTree.fromstring(
        health_dashboard_html
    )
    logging.debug(health_dashboard_et)


def separate_strings(raw_strings, delimiter=','):
    """
    Split strings by using specified delimiter.
    e.g:
      ' hogehoge, chomechome fugafuga, mogemoge' ->
      ['hogehoge', 'chomechome fugafuga', 'mogemoge']
    :param str delimiter:Delimiter string
    :rtype: list
    :return: List of split strings
    """
    result = raw_strings.split(delimiter)
    result = [
        entry.rstrip().strip() for entry in result
    ]
    return result


def convert_seconds(duration):
    """
    Convert to seconds from minutes, hours or days
    :param str duration: Human-readable duration
    :rtype: int
    :return: Converted seconds
    """
    duration_suffix = duration[-1]
    logging.debug(
        'duration_suffix is {0}'.format(duration_suffix)
    )
    if duration_suffix in ['s', 'S']:
        try:
            result = int(duration[:-1])
        except Exception:
            logging.error(
                'Invalid duration format. e.g: 60m , 60s , or 24h'
            )
    elif duration_suffix in ['m', 'M']:
        try:
            result = int(duration[:-1]) * 60
        except Exception:
            logging.error(
                'Invalid duration format. e.g: 60m , 60s , or 24h'
            )
    elif duration_suffix in ['h', 'H']:
        try:
            result = int(duration[:-1]) * 60 * 60
        except Exception:
            logging.error(
                'Invalid duration format. e.g: 60m , 60s , or 24h'
            )
    elif duration_suffix in ['d', 'D']:
        try:
            result = int(duration[:-1]) * 60 * 60 * 24
        except Exception:
            logging.error(
                'Invalid duration format. e.g: 60m , 60s , or 24h'
            )
    elif duration_suffix in ['w', 'W']:
        try:
            result = int(duration[:-1]) * 60 * 60 * 24 * 7
        except Exception:
            logging.error(
                'Invalid duration format. e.g: 60m , 60s , or 24h'
            )
    elif duration_suffix in [str(entry) for entry in range(0,10)]:
        result = int(duration)
    else:
        raise ValueError(
            'Sorry, your specified suffix {0} cannot use.'
            ''.format(duration_suffix)
        )

    logging.debug(
        'Current item durations is {0} seconds.'.format(result)
    )
    return result


def pst_to_utc(datetime_str):
    """
    Convert PST time to UTC time.
    This function may be going to add some changing in the future.
    :param str datetime_str:
    Datetime string. e.g: 'Wed, 26 Nov 2014 23:52:53 PST'
    :rtype:
    :return:
    """
    # Assume UTC -8 to delta between UTC and PST
    utc_pst_delta_hours = 8
    # 'Wed, 26 Nov 2014 23:52:53 PST' -> 'Wed, 26 Nov 2014 23:52:53'
    datetime_str = datetime_str[:-4]
    logging.debug(
        'pst_to_utc: Current datetime string is "{0}"'
        ''.format(datetime_str)
    )

    datetime_dt = datetime.datetime.strptime(
        datetime_str, '%a, %d %b %Y %H:%M:%S'
    )
    return datetime_dt + datetime.timedelta(hours=utc_pst_delta_hours)


def is_over_duration(duration, datetime_str):
    """
    Comparing with current time,
    return whether "datetime_str" is over specified duration.
    Because AWS Health Dashboard's timezone is PST,
    we'll compare with PST current time.
    :param int duration: Duration seconds.
    :param datetime_str:
    Datetime string. e.g: 'Wed, 26 Nov 2014 23:52:53 PST'
    :rtype: bool
    :return: T or F.
    """
    # Assume UTC -8 to delta between UTC and PST
    utc_pst_delta_hours = 8

    datetime_dt = pst_to_utc(datetime_str)
    dt_delta = datetime.datetime.utcnow() - datetime_dt
    dt_delta_seconds = dt_delta.days * 86400 + dt_delta.seconds
    logging.debug(
        'is_over_duration: Given duration is {0}'.format(duration)
    )
    logging.debug(
        'is_over_duration: Delta seconds is {0}'.format(dt_delta_seconds)
    )
    if dt_delta_seconds > duration:
        return True
    else:
        logging.info(
            'is_over_duration: {0} is not over {1} seconds is {0}.'
            ''.format(dt_delta.seconds, duration)
        )
        return False


def remove_html_comment(text):
    """
    This method is nightmare and not so cool...
    But AWS status page has following strange comment line.
    "<!-- --End YUI Div ---->"
    The python HTMLParser cannot parse above line.
    :param str text: Raw input
    :rtype: str
    :return: String after removing "<!-- --.*"
    """
    return re.sub(
        r'\<\!\ --.*', '', text
    )


def is_with_region(service_name):
    """
    Return if given string is being with region name.
    e.g:
      1. When given string is "cloudfront", return False
      2. When given string is "dynamodb-us-east-1", return True
    :param str service_name: AWS service name
    :rtype: bool
    :return: True or False
    """
    pattern = re.compile(r'[a-zA-Z0-9]+-[a-zA-Z]+-[a-zA-Z]+-[0-9]')
    if re.match(pattern, service_name):
        logging.debug(
            'is_with_region: {0} matched {1}.'
            ''.format(
                service_name, pattern.pattern
            )
        )
        return True
    else:
        logging.debug(
            'is_with_region: {0} didn\'t match {1}.'
            ''.format(
                service_name, pattern.pattern
            )
        )
        return False


def define_chat_integration(name):
    """
    Return chat class in each chat modules.
    :param str name: chat module name
    :rtype: class
    :return: Chat Integration Class
    """

    chats_dir = 'chats'
    mapping = {
        'stdout': '{0}.base'.format(chats_dir),
        'chatwork': '{0}.chatwork'.format(chats_dir),
        'slack': '{0}.slack'.format(chats_dir)
    }
    try:
        if name == 'stdout':
            chat_module = getattr(__import__(mapping[name]), 'base')
        else:
            chat_module = getattr(__import__(mapping[name]), name)

        logging.debug(chat_module)
        chat_cls = getattr(chat_module, 'HealthDashboardMessage')
        logging.debug(chat_cls)
        return chat_cls

    except KeyError:
        logging.error(
            'Not supported your specified chat integration "{0}"'
            ''.format(name)
        )


class AWSHealthDashboardParser(HTMLParser.HTMLParser):

    def __init__(self,
                 region=DEFAULT_VALUES['region'],
                 duration=DEFAULT_VALUES['duration'],
                 service_health_dashboard_url=DEFAULT_VALUES[
                     'service_health_dashboard_url'
                 ]):
        HTMLParser.HTMLParser.__init__(self)
        self.aws_service_health_dashboard_url = service_health_dashboard_url
        self.region_regex = self.generate_regex(
            region_list=separate_strings(region)
        )
        self.items = list()
        self.item_duration = convert_seconds(duration=duration)

    def generate_regex(self, region_list):
        """
        Generate regex such as r'AAA|BBB|CCC|' from given list type object.
        :param list region_list: Region List
        :rtype: re.compile()
        :return: Regex object such as r'us-east-1|ap-northeast-1|'
        """
        result_string = str()
        if len(region_list) > 0:
            for entry in region_list:
                result_string += entry + '|'
            result_string = result_string[:-1]
        else:
            result_string = '.*'

        logging.debug(
            'generate_regex: The generated regex is {0}'.format(result_string)
        )

        return re.compile(result_string)

    def rss_url_to_service_name(self, rss_url):
        """
        Convert to AWS service name from rss url.
        e.g:
          http://status.aws.amazon.com/ec2-ap-northeast-1.rss
          -> ec2-ap-northeast-1
        :param str rss_url: AWS Service rss URL
        :rtype: str
        :return: AWS Service name
        """
        return os.path.basename(rss_url).split('.')[0]

    def parse_aws_rss(self, rss_url, duration):
        """
        Parse AWS rss feed.
        At Dec 1 2014 aws feed has following XML documentation.
        <?xml version="1.0" encoding="UTF-8"?>
          <rss version="2.0">
            <channel>
              <title>Amazon Elastic Compute Cloud (N. Virginia) Service Status</title>
              <link>http://status.aws.amazon.com/</link>
              <link rel="alternate" href="http://status.aws.amazon.com/rss/all.rss" type="application/rss+xml" title="Amazon Web Services Status Feed"/>
              <title type="text">Current service status feed for Amazon Elastic Compute Cloud (N. Virginia).</title>
              <language>en-us</language>
              <pubDate>Sun, 30 Nov 2014 18:22:08 PST</pubDate>
              <updated>Sun, 30 Nov 2014 18:22:08 PST</updated>
              <generator>AWS Service Health Dashboard RSS Generator</generator>
              <ttl>5</ttl>

               <item>
                <title type="text">Informational message: Increased API Error Rates</title>
                <link>http://status.aws.amazon.com</link>
                <pubDate>Wed, 26 Nov 2014 23:52:53 PST</pubDate>
                <guid>http://status.aws.amazon.com/#GUID</guid>
                <description>SAMPLE_DESCRIPTION</description>
               </item>

          </channel>
        </rss>
        :param str rss_url: AWS rss url
        :rtype: list
        :return: List of <item> tag contents
        """
        response = urllib2.urlopen(rss_url)
        rss_contents = response.read()
        rss_elementtree = xml.etree.ElementTree.fromstring(rss_contents)
        result = list()

        for entry in rss_elementtree.findall('.//item'):
            pubDate = entry.find('pubDate').text
            logging.debug(
                '{0}.parse_aws_rss: Current item\'s "pubData" is {1}'
                ''.format(
                    self.__class__, pubDate
                )
            )
            if not is_over_duration(
                duration=duration,
                datetime_str=pubDate
            ):
                item = dict()
                item['title'] = entry.find('title').text
                item['pubDate'] = pst_to_utc(pubDate)
                item['guid'] = entry.find('guid').text
                item['description'] = entry.find('description').text
                item['service_name'] = self.rss_url_to_service_name(rss_url)
                logging.info(item)
                result.append(item)

        return result

    def handle_starttag(self, tag, attrs):
        """
        Parse "<a href="rss/AWS_SERVICE.xml">"
        :param tag:
        :param attrs:
        :return:
        """
        if len(attrs) <= 0:
            return None

        if tag == 'a' and attrs[0][1].startswith(RSS_PREFIX):
            service_rss_uri = attrs[0][1]
            logging.debug(
                'current "href" value of "a" tag is {0}'.format(
                    service_rss_uri
                )
            )
            service_rss_url = os.path.join(
                self.aws_service_health_dashboard_url, service_rss_uri
            )
            service_name = self.rss_url_to_service_name(service_rss_url)
            logging.debug(
                '{0}.handle_starttag: Current conducting rss url is {1}'
                ''.format(
                    self.__class__, service_rss_url
                )
            )
            if self.region_regex.search(service_name):
                logging.debug(
                    '{0}.handle_starttag: {1} was matched regex({2})'
                    ''.format(
                        self.__class__,
                        service_name,
                        self.region_regex.pattern
                    )
                )
                self.items.extend(
                    self.parse_aws_rss(
                        rss_url=service_rss_url,
                        duration=self.item_duration
                    )
                )
            elif is_with_region(service_name) is False:
                self.items.extend(
                    self.parse_aws_rss(
                        rss_url=service_rss_url,
                        duration=self.item_duration
                    )
                )


def main():
    arguments = get_args()
    set_log_level(arguments.log_level)

    raw_text = urllib2.urlopen(arguments.service_health_dashboard_url).read()
    raw_text = remove_html_comment(raw_text)
    aws_health_dashboard_parser = AWSHealthDashboardParser(
        region=arguments.region,
        duration=arguments.duration,
        service_health_dashboard_url=arguments.service_health_dashboard_url
    )
    aws_health_dashboard_parser.feed(raw_text)

    chat_cls = define_chat_integration(name=arguments.chat_integration)
    chat_kls = chat_cls()
    chat_kls.append_messages(
        messages=aws_health_dashboard_parser.items
    )
    chat_kls.notify(
        token=arguments.chat_api_token,
        channel_id=arguments.chat_api_channel_id
    )


if __name__ == '__main__':
    main()
