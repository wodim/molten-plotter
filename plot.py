# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import re
import requests
import sqlite3
import time

realms = {
    'rb6': 'Lordaeron',
    'rb2': 'Deathwing',
    'rb7': 'Ragnaros',
    'rb4': 'Frostwolf',
    'rb1': 'Neltharion',
    'rb3': 'Sargeras',
    'rb5': 'Warsong',
}

connection = sqlite3.connect('plot.sqlite')
cursor = connection.cursor()

session = requests.session()
headers = { 'User-Agent': 'feelme best maeg' }
# don't catch the exception if site is being down due to ddos as always, just crash
response = session.get('https://www.molten-wow.com/', headers=headers).text
timestamp = int(time.time()) # consistency between requests

soup = BeautifulSoup(response)

for realm in realms.iteritems():
    users_online = 0
    users_queued = 0

    try:
        players = soup.find(id=realm[0]).find(class_='players').get_text(strip=True)

        re_no_queue = re.compile(r'^(\d+) players online$')
        re_with_queue = re.compile(r'^(\d+) players(\d+) queue$')

        no_queue = re.findall(re_no_queue, players)
        with_queue = re.findall(re_with_queue, players)
        
        if no_queue != []:
            users_online = no_queue[0]
        elif with_queue != []:
            users_online = with_queue[0][0]
            users_queued = with_queue[0][1]
        else:
            pass # 0/0
    except:
        pass # 0/0 players (server unavailable)

    realm = realm[1]

    cursor.execute('INSERT INTO plot (timestamp, realm, users_online, users_queued) VALUES (?, ?, ?, ?)',
        (timestamp, realm, users_online, users_queued))

connection.commit()
connection.close()