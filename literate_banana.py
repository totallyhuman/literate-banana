#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
literate_banana

A Euphoria (euphoria.io) bot library (?)
"""

import json
import websocket as ws


class Bot(object):

    def __init__(self, room, nick):
        self.session = ws.create_connection('wss://euphoria.io/room/{}/ws'.format(room))

        self.session.send(
            json.dumps({
                'type': 'nick',
                'data': {
                    'name': nick
                }
            }))


    def post(self, message, parent = ''):
        self.session.send(
            json.dumps({
                'type': 'send',
                'data': {
                    'content': message,
                    'parent': parent
                }
            }))
