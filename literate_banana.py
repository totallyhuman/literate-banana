#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
literate_banana

A Euphoria (euphoria.io) bot library.
"""

import json
import re
import websocket as ws


class Bot(object):

    def __init__(self, room, nick, **kwargs):
        self.nick = nick
        self.room = room
        self.last_message = None

        if 'short_help' in kwargs:
            self.short_help = kwargs['short_help']
        else:
            self.short_help = None

        if 'long_help' in kwargs:
            self.long_help = kwargs['long_help']
        else:
            self.short_help = None

        if 'generic_ping' in kwargs:
            self.generic_ping = kwargs['generic_ping']
        else:
            self.generic_ping = 'Pong!'

        if 'specific_ping' in kwargs:
            self.specific_ping = kwargs['specific_ping']
        else:
            self.specific_ping = 'Pong!'

        if 'regexes' in kwargs:
            self.regexes = kwargs['regexes']

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


    def kill(self):
        self.session.close()


    def log(self, mode, message):
        if mode == 'send':
            print('[{0}] Sent message: {1!r}'.format(
                self.nick, message).encode('utf-8'))
        elif mode == 'receive':
            print('[{0}] Received trigger message: {1!r}'.format(
                self.nick, message).encode('utf-8'))


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
            elif re.match(r'\s*!kill\s+@?{}\s*$'.format(self.nick),
                          incoming['data']['content']):
                self.log('receive', incoming['data']['content'])
                self.post('/me is now exiting.', incoming['data']['id'])
                self.kill()

            for regex, response in self.regexes.items():
                if re.match(regex, incoming['data']['content']):
                    self.log('receive', incoming['data']['content'])
                    result = response(
                        re.match(regex, incoming['data']['content']).groups())

                    if result:
                        self.post(result, incoming['data']['id'])
