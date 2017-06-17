#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import requests
from literate_banana import Bot


def format_xkcd(data):
    details = 'xkcd #{0}; "{1}" ({2}-{3:02d}-{4:02d}, xkcd.com/{5})\n'.format(
        data['num'], data['title'], data['year'],
        int(data['month']), int(data['day']), data['num'])
    image = '{}'.format(data['img'])

    if data['alt']:
        alt_text = 'Alt text: {}'.format(data['alt'])
    else:
        alt_text = '(no alt text)'

    return [details + image, alt_text]


def latest_xkcd(match, trigger):
    return format_xkcd(requests.get('https://xkcd.com/info.0.json').json())


def numbered_xkcd(match, trigger):
    return format_xkcd(
        requests.get('https://xkcd.com/{}/info.0.json'.format(match[0])).json())


def random_xkcd(match, trigger):
    rand = random.randint(
        1, requests.get('https://xkcd.com/info.0.json').json()['num'])
    return format_xkcd(
        requests.get('https://xkcd.com/{}/info.0.json'.format(rand)).json())


totallyxkcd = Bot(
    nick = 'totallyxkcd',
    room = 'xkcd',
    short_help = 'I display xkcd comics.',
    long_help = ('I display xkcd comics on command.\n' +
                 '\n' +
                 '    !totallyxkcd -> the latest xkcd comic\n' +
                 '    !totallyxkcd <number> -> the <number>th xkcd comic\n' +
                 '    !totallyxkcd random -> a random xkcd comic\n' +
                 '\n' +
                 'by totally𝚑𝚞𝚖𝚊𝚗'),
    generic_ping = 'Pong!',
    specific_ping = 'Pong!',
    regexes = {
        r'(?i)^\s*!totallyxkcd$': latest_xkcd,
        r'(?i)^\s*!totallyxkcd\s+(\d+)\s*$': numbered_xkcd,
        r'(?i)^\s*!totallyxkcd\s+random\s*$': random_xkcd
    })

while True:
    totallyxkcd.receive()
