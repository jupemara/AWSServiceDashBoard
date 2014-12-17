#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2

import chats.base


class HealthDashboardMessage(chats.base.HealthDashboardMessage):

    def convert_message(self, message):
        message['pubDate'] = message['pubDate'].__str__()
        return message

    def notify(self, token=None, channel_id=None):
        endpoint = (
            'https://api.chatwork.com/v1/rooms/{0}/messages'
            ''.format(channel_id)
        )
        headers = {
            'X-ChatWorkToken': token
        }

        for message in self.messages:
            content_body = (
                'AWS Service Name: {service_name}\n'
                'Published Date: {pubDate}\n'
                'Message URL: {guid}\n'
                'Message Detail: {description}\n'
                ''.format(
                    service_name=message['service_name'],
                    pubDate=message['pubDate'],
                    guid=message['guid'],
                    description=message['description']
                )
            )
            content = (
                '[info][title]{title}[/title]'
                '{body}[/info]'
                ''.format(
                    title=message['title'],
                    body=content_body
                )
            )

            data = {
                'body':content
            }
            data = urllib.urlencode(data)
            request = urllib2.Request(
                endpoint,
                data=data,
                headers=headers
            )
            response = urllib2.urlopen(request)

