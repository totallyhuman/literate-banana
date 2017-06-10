#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
nick

Example bot using the Literate Banana library.
"""

from literate_banana import Bot

bot = Bot(
    'test',
    'nick',
    short_help = 'This is a short help message.',
    long_help = 'This is a not very long help message.',
    generic_ping = 'This is a generic ping reply.',
    specific_ping = 'This is a specific ping reply.')

bot.receive()
bot.post('message')

while True:
    bot.receive()
