#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Literate Banana

A Euphoria (euphoria.io) bot library.
"""

import json
import re
import time
import websocket as ws


class Bot(object):

    def __init__(self, room, nick, **kwargs):
        self.nick = nick
        self.room = room
        self.start_time = time.time()
        self.pause = False
        self.last_message = None

        self.short_help = kwargs.get('short_help', None)
        self.long_help = kwargs.get('long_help', None)
        self.generic_ping = kwargs.get('generic_ping', None)
        self.specific_ping = kwargs.get('specific_ping', None)
        self.regexes = kwargs.get('regexes', {})

        self.session = ws.create_connection(
            'wss://euphoria.io/room/{}/ws'.format(self.room))

        self.session.send(
            json.dumps({
                'type': 'nick',
                'data': {
                    'name': self.nick
                }
            }))

    def post(self, message, parent = ''):
        if message:
            self.session.send(
                json.dumps({
                    'type': 'send',
                    'data': {
                        'content': message,
                        'parent': parent
                    }
                }))

    def uptime(self):
        start = time.gmtime(self.start_time)
        start_time = (
            '{0:04d}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d} UTC'.format(
                start.tm_year, start.tm_mon, start.tm_mday, start.tm_hour,
                start.tm_min, start.tm_sec))
        delta = self.format_delta(time.time() - self.start_time)

        return '/me has been up since {0} ({1})'.format(start_time, delta)

    @staticmethod
    def format_delta(seconds):
        result = ''

        if seconds >= 86400:
            result += '{:.0f}d '.format(seconds / 86400)
            seconds %= 86400
        if seconds >= 3600:
            result += '{:.0f}h '.format(seconds / 3600)
            seconds %= 3600
        if seconds >= 60:
            result += '{:.0f}m '.format(seconds / 60)
            seconds %= 60
        if seconds != 0:
            result += '{:.2f}s '.format(seconds)
        if seconds == 0:
            result += '0s '

        return result[:-1]

    def log(self, mode, message):
        if mode == 'send':
            print(repr('[{0}] Sent message: {1!r}'.format(
                self.nick, message).encode('utf-8'))[2:-1])
        elif mode == 'receive':
            print(repr('[{0}] Received trigger message: {1!r}'.format(
                self.nick, message).encode('utf-8'))[2:-1])

    def receive(self):
        incoming = json.loads(self.session.recv())

        if incoming['type'] == 'ping-event':
            self.session.send(
                json.dumps({
                    'type': 'ping-reply',
                    'data': {
                        'time': incoming['data']['time']
                    }
                }))

        elif incoming['type'] == 'send-reply':
            self.last_message = incoming
            self.log('send', incoming['data']['content'])

        elif incoming['type'] == 'send-event':
            if self.pause and not re.match(
                    r'\s*!(unpause|restore)\s+@?{}\s*$'.format(self.nick),
                    incoming['data']['content']):
                return

            if re.match(r'\s*!ping\s*$', incoming['data']['content']):
                self.log('receive', incoming['data']['content'])
                self.post(self.generic_ping, incoming['data']['id'])

            elif re.match(r'\s*!ping\s+@?{}\s*$'.format(self.nick),
                          incoming['data']['content']):
                self.log('receive', incoming['data']['content'])
                self.post(self.specific_ping, incoming['data']['id'])

            elif re.match(r'\s*!help\s*$', incoming['data']['content']):
                self.log('receive', incoming['data']['content'])
                self.post(self.short_help, incoming['data']['id'])

            elif re.match(r'\s*!help\s+@?{}\s*$'.format(self.nick),
                          incoming['data']['content']):
                self.log('receive', incoming['data']['content'])
                self.post(self.long_help, incoming['data']['id'])

            elif re.match(r'\s*!uptime\s+@?{}\s*$'.format(self.nick),
                          incoming['data']['content']):
                self.log('receive', incoming['data']['content'])
                self.post(self.uptime(), incoming['data']['id'])

            elif re.match(r'\s*!pause\s+@?{}\s*$'.format(self.nick),
                          incoming['data']['content']):
                self.log('receive', incoming['data']['content'])
                self.post('/me has been paused.', incoming['data']['id'])
                self.pause = True

            elif re.match(r'\s*!(unpause|restore)\s+@?{}\s*$'.format(self.nick),
                          incoming['data']['content']):
                self.log('receive', incoming['data']['content'])
                self.post('/me has been restored.', incoming['data']['id'])
                self.pause = False

            elif re.match(r'\s*!kill\s+@?{}\s*$'.format(self.nick),
                          incoming['data']['content']):
                self.log('receive', incoming['data']['content'])
                self.post('/me is now exiting.', incoming['data']['id'])
                self.session.close()

            for regex, response in self.regexes.items():
                if re.match(regex, incoming['data']['content']):
                    self.log('receive', incoming['data']['content'])
                    result = response(
                        re.match(regex, incoming['data']['content']).groups())

                    if result:
                        self.post(result, incoming['data']['id'])
