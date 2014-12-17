#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json


class HealthDashboardMessage(object):
    """
    One message is following dictionary.
    {
        'title': 'Title. e.g: Informational message: [RESOLVED] MESSAGE',
        'pubDate': 'Published Date. e.g: 1970-01-01 00:00:00',
        'guid': 'Specific message URL',
        'description': 'Message detail',
        'service_name': 'Service name. e.g: ec2-ap-northeast-1'
    }
    """

    def __init__(self):
        self.raw_messages = list()
        self.messages = None

    def get_messages(self):
        return self.messages

    def convert_message(self, message):
        message['pubDate'] = message['pubDate'].__str__()
        return message

    def append_messages(self, messages):
        self.raw_messages.extend(messages)
        result = list()
        for entry in messages:
            result.append(
                self.convert_message(entry)
            )
        self.messages = result

    def notify(self, token=None, channel_id=None):
        """
        Notify messages.
        :param str token: Chat API Token
        :param str channel_id: Chat Channel ID (in other words, Room ID)
        :rtype: None
        :return: None
        """
        print(
            json.dumps(self.messages)
        )
