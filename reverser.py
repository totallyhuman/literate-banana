#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from literate_banana import Bot

def reverse(match, trigger):
    return match[0][::-1]

def reverse_words(match, trigger):
    return ' '.join(match[0].split()[::-1])

reverser = Bot(
    nick = 'Reverser',
    room = 'test',
    short_help = 'I reverse things.',
    long_help = ('I reverse things on command.\n' +
                 '\n' +
                 '    !reverse <string> - reverses the <string>\n' +
                 '    !reversewords <string> - reverses the order of words ' +
                 'in the <string>\n' +
                 '\n' +
                 'by totally𝚑𝚞𝚖𝚊𝚗'),
    generic_ping = 'Pong!',
    specific_ping = 'Pong!',
    regexes = {
        r'(?i)^\s*!reverse\s+(.*)': reverse,
        r'(?i)^\s*!reversewords\s+(.*)': reverse_words
    }
)

while True:
    reverser.receive()
