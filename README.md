Molten-WoW Plotter
==================

This project uses two scripts for plotting charts on how many users
are connected to all realms in Molten during the last 48 hours, inspired by
the chart shown by Steam in its main page.

There are three charts, one for WotLK servers, one for Cataclysm servers and
one for the MoP server.

It requires:
* jinja2 (templating support)
* sqlite3 (for storing the data)
* bs4 (for parsing the html)
* requests (for fetching molten's web page)

You must create a sqlite3 database called `plot.sqlite` with one table with
the following schema:

    CREATE TABLE plot (id INTEGER primary key, timestamp INTEGER, realm TEXT, users_online INTEGER, users_queued INTEGER);

Then, you should set up two cron jobs, one for fetching the data and the
other one for generating the html report file. For example, I fetch the
data every minute and then generate a new report every 15 minutes.

    */1 * * * * (cd /home/wodim/molten-plotter/ && python2 plot.py &>> log.txt)
    */15 * * * * (cd /home/wodim/molten-plotter/ && python2 chart.py &> /home/http/vortigaunt.net/molten-plotter/index.html)

You can see the results here: http://joneame.net/molten-plotter/