#!/usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib.dates
import matplotlib.ticker
import datetime
import time
import operator
import math
import numpy
import sys
import zipfile
import csv
import StringIO
import copy

def parse_timestamp(i, base_date=None):
    s = str(i)
    assert len(s) == 4
    hours = int(s[:2])
    minutes = int(s[-2:])
    return base_date + datetime.timedelta(hours=hours, minutes=minutes)

def main():
    def german_float(s):
        return float(s.replace(',','.'))

    def parse_kasse_timestamp(t):
        # nb. note rounding errors, eg. '-3,499' (e3.50)
        return datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S')

    # Transform ISO-8859-15 contents with CP437 filenames, all to UTF-8
    with zipfile.ZipFile('speedy-kasse/Fahrtags-Umsatz.zip', 'r') as z:
        namelist = [name.decode('cp437') for name in z.namelist()]
        # Sort by YYYY-mm-dd date
        namelist.sort()
        # Encodings fun
        for most_recent in namelist:
            print 'processing', most_recent
            file_datestamp = most_recent[:len('YYYY-mm-dd')]
            target_date = datetime.datetime.strptime(file_datestamp, '%Y-%m-%d')
            raw = z.open(most_recent.encode('cp437'), 'r').read()
            contents = raw.decode('iso-8859-15').encode('utf-8')
            csvfile = csv.reader(contents.splitlines(True), delimiter=';', quotechar='"')
            headers = csvfile.next()

            # Opening balance line
            cd = csv.DictReader(contents.splitlines(True), delimiter=';', quotechar='"')
            opening_row = cd.next()

            # Assert.
            if opening_row['Belegpositionstext'] != 'Einlage Wechselgeld':
                print 'skipping processing', most_recent, target_date
                print opening_row
                continue
            
            starting_balance = german_float(opening_row['Gewinn'])

            #for row in csvfile:
            cat_x = dict(total=[], rides=[], drinks=[], cakes=[], food=[], members=[], whistles=[], unknown=[],
                         pommes_c=[], breadroll_c=[], whistles_c=[], rides_c=[], child_c=[], adult_c=[])
            cat_y = copy.deepcopy(cat_x)

            def append_cat(category, x, y):
                if not cat_x.has_key(category):
                    cat_x[category] = list()
                    cat_y[category] = list()
                cat_x[category].append(x)
                cat_y[category].append(y)

            for d in cd:
                timestamp = parse_kasse_timestamp(d['Belegzeitstempel'])
                profit = german_float(d['Gewinn'])
                # Skip testing in evening before
                if timestamp < target_date:
                    print 'skipping test dated', timestamp
                    continue
                agt = d['ArtikelGruppenText']
                atk = d['ArtikelTextKurz']
                bpt = d['Belegpositionstext']
                zls = d['Zahlungsart']
                count = int(d['Menge'])
                if bpt == 'Abschöpfung, Kasse an Bank':
                    continue
                if 'Kostenlos' in zls:
                    append_cat('members', timestamp, profit)
                elif agt == 'Sonstiges' and 'Fahrkarte' in atk:
                    append_cat('rides', timestamp, profit)
                    multi_ticket = count
                    if bpt[0].isdigit():
                        multi_ticket *= int(bpt[0])
                    if 'Erwachsener' in bpt:
                        append_cat('adult_c', timestamp, multi_ticket)
                    elif 'Kind' in bpt:
                        append_cat('child_c', timestamp, multi_ticket)
                    append_cat('rides_c', timestamp, multi_ticket)
                elif agt == 'Sonstiges' and atk == 'Lokpfeife':
                    append_cat('whistles', timestamp, profit)
                    append_cat('whistles_c', timestamp, count)
                elif agt == 'Getränke':
                    append_cat('drinks', timestamp, profit)
                elif agt == 'Kaffee&Kuchen':
                    append_cat('cakes', timestamp, profit)
                elif agt == 'Speisen':
                    append_cat('food', timestamp, profit)
                    if 'Pommes' in bpt:
                        append_cat('pommes_c', timestamp, count)
                    if 'Brötchen' in bpt:
                        append_cat('breadroll_c', timestamp, count)
                    if 'Steak' in bpt:
                        append_cat('steak_c', timestamp, count)
                    if 'wurst' in bpt.lower():
                        append_cat('sausage_c', timestamp, count)
                    if 'Kartoffelsalat' in bpt:
                        append_cat('potato_c', timestamp, count)
                else:
                    append_cat('unknown', timestamp, profit)
                    print 'unknown:', bpt, agt, atk, profit
                append_cat('total', timestamp, profit)
        render(target_date,cat_x,cat_y)

def render(target_date,cat_x,cat_y):
    x = []
    y = []

    # Bring up a Figure/Plot
    def inch(mm): return mm / 25.4
    fig = plt.figure(222,figsize=(inch(298),inch(150)))

    plt.rcParams['font.family'] = 'Ubuntu Mono'

    ax = fig.add_subplot(1,1,1)
    p = plt.plot(x,y)
    plt.setp(p, color='gray')
    ax2 = ax.twinx()
    ax.set_title(u"Wiesloch Feldbahnmuseum: Geld (Fahrt in den Mai 2016)", position=(0.5,-0.11), color='darkgray')

    # Opening/closing hours
    ax.set_xlim(parse_timestamp('1000', target_date), parse_timestamp('1800', target_date))
    ax.set_ylim(-400,400)
    ax.get_xaxis().set_visible(True)

    ax.xaxis.grid(True, which='major')
    ax.xaxis.grid(False, which='minor')

    ax.yaxis.set_ticks_position('left')

    ax.yaxis.grid(True, which='major')
    ax.yaxis.grid(False, which='minor')

    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Hh"))

    for k in cat_x.keys():
        foo = cat_y[k]
        running_total = numpy.cumsum(foo)

        if k == 'total':
            ax.set_ylim(0, running_total.max())

        # if the unknown category is empty we can skip it
        if k == 'unknown' and running_total.size == 0:
            continue
        s = '%s (%d)' % (k, running_total[-1])
        ax.plot(cat_x[k], running_total, label=s)
        ax.legend(loc = 'upper left')

    fig.savefig('cash.pdf', transparent=True, papertype='a4', orientation='landscape')

    # Show interactively; skipped if there's no live terminal
    if sys.stdout.isatty():
        plt.show()

if __name__=='__main__':
    main()
