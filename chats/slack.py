#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import sys
import urllib
import urllib2

import chats.base

class HealthDashboardMessage(chats.base.HealthDashboardMessage):

    def convert_message(self, message):
        if '[RESOLVED]' in message['title']:
            color = 'good'
        else:
            color = 'danger'

        pretext = '{0}: <{1}|{2}>'.format(
            message['service_name'],
            message['guid'],
            message['title']
        )
        fallback = (
            '{0}\n'
            'Published date: {1}\n'
            '{2}'.format(
                pretext,
                message['pubDate'],
                message['description']
            )
        )

        message =  {
            'fallback': fallback,
            'pretext': pretext,
            'color': color,
            'fields': [
                {
                    'title': 'Published date: {0}'.format(
                        message['pubDate']
                    ),
                    'value': message['description']
                }
            ]
        }
        return message

    def notify(self, token=None, channel_id=None):

        if channel_id is not None:
            logging.critical(
                (
                    'You can\'t specify "channel_id" argument '
                    'when using "slack" as chat integration.'
                )
            )
            sys.exit(1)

        if not token.startswith('http'):
            logging.critical(
                (
                    'You must specify "Webhook URL" as "token" argument '
                    'when using "slack".'
                )
            )
            sys.exit(1)

        payload = {
            'attachments': self.messages,
            'icon_emoji': ':scream_cat:'
        }

        urllib2.urlopen(
            token,
            data=json.dumps(payload)
        )
