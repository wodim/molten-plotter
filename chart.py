# -*- coding: utf-8 -*-

from jinja2 import Template, Environment, FileSystemLoader
import sqlite3
import time
import sys
import re
from collections import OrderedDict
from datetime import datetime

realms = {
    'WotLK': {'capacity': 4000, 'realms': ('Lordaeron', 'Deathwing', 'Ragnaros')},
    'Cataclysm': {'capacity': 3500, 'realms': ('Frostwolf', 'Neltharion', 'Sargeras', 'Warsong')},
}

translations = {
    'Lordaeron': 'Lordaeron x1',
    'Deathwing': 'Deathwing x12',
    'Ragnaros': 'Ragnaros x20',
    'Frostwolf': 'Frostwolf x3',
    'Neltharion': 'Neltharion x12',
    'Sargeras': 'Sargeras x20',
    'Warsong': u'Warsong x∞',
}

timediff = -(60 * 60)
timestamp = int(time.time()) + timediff
now = datetime.fromtimestamp(timestamp).strftime('%d-%b %H:%M')
twodays = timestamp - (60 * 60 * 24 * 2) # last 48 hours

connection = sqlite3.connect('plot.sqlite')
cursor = connection.cursor()

html_charts = OrderedDict({})
for version in realms.iteritems():
    # cata or wotlk
    users = {}
    for realm_name in version[1]['realms']:
        # each one of the realms
        users[realm_name] = []
        cursor.execute('SELECT timestamp, users_online, users_queued FROM plot WHERE timestamp > ? AND realm = ?', (twodays, realm_name))
        for sample in cursor.fetchall():
            users[realm_name].append(sample)

    # resort the list of dicts of tuples of lists of tuples of lists of lists
    store = OrderedDict({})
    for realm_name in version[1]['realms']:
        for item in users[realm_name]:
            alt_key = datetime.fromtimestamp(item[0] + timediff).strftime('%d-%b %H:%M:%S')
            keylist = store.get(alt_key, [])

            users_online = item[1]
            users_queued = item[2]
            # if a realm is full or empty, don't draw a line for online users
            if users_online >= version[1]['capacity'] or users_online == 0:
                users_online = 'null'
            # then, if there's a queue, sum the capacity of the realm to the queue and draw it
            if users_online == 'null' and users_queued != 0:
                users_queued += version[1]['capacity']
            # but if there are no players and no queue, the realm is down, don't draw any lines
            elif users_queued == 0:
                users_queued = 'null'

            keylist.append((realm_name, users_online, users_queued))
            store[alt_key] = keylist

    html_charts[version[0]] = store

jinja_env = Environment(trim_blocks=True, lstrip_blocks=True)
jinja_env.loader = FileSystemLoader('.')
template = jinja_env.get_template('chart.html')
output = template.render(charts=html_charts, realms=realms, translations=translations, now=now)
# minify
output = re.sub(r'\r|\n|\s{2,}', '', output)

print output