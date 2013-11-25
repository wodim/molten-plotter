# -*- coding: utf-8 -*-

from jinja2 import Template, Environment, FileSystemLoader
import sqlite3
import time
import sys
import re
from collections import OrderedDict
from datetime import datetime

realms = {
    'WotLK': ('Lordaeron', 'Deathwing', 'Ragnaros'),
    'Cataclysm': ('Frostwolf', 'Neltharion', 'Sargeras', 'Warsong'),
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
    for realm in version[1]:
        # each one of the realms
        users[realm] = []
        cursor.execute('SELECT timestamp, users_online, users_queued FROM plot WHERE timestamp > ? AND realm = ?', (twodays, realm))
        for sample in cursor.fetchall():
            users[realm].append(sample)

    # resort the list of dicts of tuples of lists of tuples of lists of lists
    store = OrderedDict({})
    for name in users:
        for item in users[name]:
            alt_key = datetime.fromtimestamp(item[0] + timediff).strftime('%d-%b %H:%M:%S')
            keylist = store.get(alt_key, [])
            keylist.append((name, item[1], item[2]))
            store[alt_key] = keylist

    html_charts[version[0]] = store

jinja_env = Environment(trim_blocks=True, lstrip_blocks=True)
jinja_env.loader = FileSystemLoader('.')
template = jinja_env.get_template('chart.html')
output = template.render(charts=html_charts, realms=realms, translations=translations, now=now)
# minify
output = re.sub(r'\r|\n|\s{2,}', '', output)

print output