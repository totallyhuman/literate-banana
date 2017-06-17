#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Literate Banana

A Euphoria (euphoria.io) bot library.

Sumant Bhaskaruni
v1.0.0
"""

import json
import re
import time
import websocket as ws


class Bot(object):
    """A connection to Euphoria.

    Bots can send and receive messages as well as other types of packets as
    well.

    Positional arguments:
        nick (str): the nickname the bot will take
        room (str): the room the bot will connect to

    Keyword arguments:
        short_help (str): the message returned on '!help' (default: None)
        long_help (str): the message returned on '!help @BotName'
                         (default: None)
        generic_ping (str): the message returned on '!ping' (default: 'Pong!')
        specific_ping (str): the message returned on '!ping @BotName'
                             (default: 'Pong!')
        regexes (dict): regexes and responses to execute based on them
                        (default: {})

    Attributes:
        nick (str): the nickname of the bot
        room (str): the room the bot is connected to
        start_time (float): the time the bot started in seconds since the epoch
        pause (bool): whether the bot has been paused or not
        last_message (dict): JSON packet of the bot's last message sent
        short_help (str): the message returned on '!help'
        long_help (str): the message returned on '!help @BotName'
        generic_ping (str): the message returned on '!ping'
        specific_ping (str): the message returned on '!ping @BotName'
        regexes (dict): regexes and responses to execute based on them
        session (websocket.Websocket): the connection to Euphoria
    """

    def __init__(self, nick, room, **kwargs):
        """See class docstring for details."""

        self.nick = nick
        self.room = room
        self.start_time = time.time()
        self.pause = False
        self.last_message = None

        self.short_help = kwargs.get('short_help', None)
        self.long_help = kwargs.get('long_help', None)
        self.generic_ping = kwargs.get('generic_ping', 'Ping!')
        self.specific_ping = kwargs.get('specific_ping', 'Ping!')
        self.regexes = kwargs.get('regexes', {})

        self.session = ws.WebSocket()
        self.session.connect('wss://euphoria.io/room/{}/ws'.format(self.room))
        self.log('connect')

        self.session.send(
            json.dumps({
                'type': 'nick',
                'data': {
                    'name': self.nick
                }
            }))

    def post(self, message, parent = ''):
        """Posts a message in the room.

        Arguments:
            message (str): the content of the message
            parent (str): the id of the message to reply to (default: '')
        """

        if message:
            self.session.send(
                json.dumps({
                    'type': 'send',
                    'data': {
                        'content': message,
                        'parent': parent
                    }
                }))

            self.log('send', message)

    def uptime(self):
        """Returns the uptime (the amount of time since the start of the
        bot)."""

        delta = self.format_delta(time.time() - self.start_time)

        return '/me has been up since {0} ({1})'.format(
            self.format_time(self.start_time), delta)

    @staticmethod
    def mention(nick):
        return '@' + re.sub(r' ', '', nick)

    @staticmethod
    def format_time(seconds):
        """Formats an amount of seconds into a timestamp.

        Arguments:
            seconds (float): seconds to be converted to the returned timestamp
        """

        struct = time.gmtime(seconds)

        return '{0:04d}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d} UTC'.format(
            struct.tm_year, struct.tm_mon, struct.tm_mday, struct.tm_hour,
            struct.tm_min, struct.tm_sec)

    @staticmethod
    def format_delta(seconds):
        """Formats a time difference into '[XXd ][XXh ][XXm ][XX.XXs]'.

        Arguments:
            seconds (float): seconds to be converted to the returned delta
        """

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

    def log(self, mode, message = None):
        """Log events to the terminal.

        Arguments:
            mode (str): the type of event to be logged
            message (<type>): the message, only if sent or received
                              (default: None)
        """

        current_time = self.format_time(time.time())

        if mode == 'connect':
            print(
                repr('[{0}][{1}] Connected to &{2}.'.format(
                    current_time, self.nick, self.room).encode('utf-8'))[2:-1])
        elif mode == 'send':
            print(
                repr('[{0}][{1}] Sent message: {2!r}'.format(
                    current_time, self.nick, message).encode('utf-8'))[2:-1])
        elif mode == 'receive':
            print(
                repr('[{0}][{1}] Received trigger message: {2!r}'.format(
                    current_time, self.nick, message).encode('utf-8'))[2:-1])
        elif mode == 'disconnect':
            print(
                repr('[{0}][{1}] Disconnected from &{2}.'.format(
                    current_time, self.nick, self.room).encode('utf-8'))[2:-1])

    def receive(self):
        """Function that recieves packets from Euphoria and employs the
        botrulez and the regexes specified."""

        if self.session.connected:
            incoming = json.loads(self.session.recv())
        else:
            self.log('disconnect')
            exit()

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

        elif incoming['type'] == 'send-event':
            if self.pause and not re.search(
                    r'(?i)^\s*!(unpause|restore|kill)\s+@?{}\s*$'.format(
                        self.nick), incoming['data']['content']):
                self.log('receive', incoming['data']['content'])
                self.post('/me is paused.', incoming['data']['id'])
                self.post(
                    ('Type "!restore @{0}" to restore me or "!kill @{0}" to '
                    + 'kill me.').format(self.nick),
                    incoming['data']['id'])
                return

            if re.search(r'(?i)^\s*!ping\s*$', incoming['data']['content']):
                self.log('receive', incoming['data']['content'])
                self.post(self.generic_ping, incoming['data']['id'])

            elif re.search(r'(?i)^\s*!ping\s+@?{}\s*$'.format(self.nick),
                           incoming['data']['content']):
                self.log('receive', incoming['data']['content'])
                self.post(self.specific_ping, incoming['data']['id'])

            elif re.search(r'(?i)^\s*!help\s*$', incoming['data']['content']):
                self.log('receive', incoming['data']['content'])
                self.post(self.short_help, incoming['data']['id'])

            elif re.search(r'(?i)^\s*!help\s+@?{}\s*$'.format(self.nick),
                           incoming['data']['content']):
                self.log('receive', incoming['data']['content'])
                self.post(self.long_help, incoming['data']['id'])

            elif re.search(r'(?i)^\s*!uptime\s+@?{}\s*$'.format(self.nick),
                           incoming['data']['content']):
                self.log('receive', incoming['data']['content'])
                self.post(self.uptime(), incoming['data']['id'])

            elif re.search(r'(?i)^\s*!pause\s+@?{}\s*$'.format(self.nick),
                           incoming['data']['content']):
                self.log('receive', incoming['data']['content'])
                self.post('/me has been paused.', incoming['data']['id'])
                self.pause = True

            elif re.search(
                    r'(?i)^\s*!(unpause|restore)\s+@?{}\s*$'.format(self.nick),
                    incoming['data']['content']):
                self.log('receive', incoming['data']['content'])
                self.post('/me has been restored.', incoming['data']['id'])
                self.pause = False

            elif re.search(r'(?i)^\s*!kill\s+@?{}\s*$'.format(self.nick),
                           incoming['data']['content']):
                self.log('receive', incoming['data']['content'])
                self.post('/me is now exiting.', incoming['data']['id'])
                self.session.close()

            for regex, response in self.regexes.items():
                if re.search(regex, incoming['data']['content']):
                    self.log('receive', incoming['data']['content'])

                    result = response(re.search(
                        regex, incoming['data']['content']).groups(),
                        incoming['data'])

                    if isinstance(result, list):
                        for message in result:
                            self.post(message, incoming['data']['id'])
                    else:
                        self.post(result, incoming['data']['id'])
