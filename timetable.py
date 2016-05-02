#!/usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib.dates
import matplotlib.ticker
import datetime
import random

chainages = {
# 'forest_construction': +300,
 'Bagger': +376,
# 'sidings': +281,
# 'loop': +181,
 'Lokschupp.': +90,
 'Bahnhof': +50,
# 'points': 0,
 'Eingang X': -10,
# 'reversal': -30,
# u'Adelsförsterpfad': -168,
# u'crossing': -168,
 u'Adelsförst. X': -168,
 u'Fuß. X': -311,
 'Landratsamt': -386,
 }

"""
[Forest +300 (+276)]
Bagger +376 (+356)
Sidings +281
Points +181
Bahnhof +124 (+50)
Points 0
Eingang -10
Reversal -30
Road -168
Foot -311
Landratsamt -386 (-360)
"""
L,W,G,F='Land','Wald','Gros','Oppo'

# Times from on the station clock.  Camera timestamps are 50 minutes behind
times = [
    #(G,1028,1034,1038,), # 1034 pass
    (G,1028,1041,), # 1034 pass
    (L,1048,1053),
    (W,1105,1115), # 1110 bagger
    (L,1124,1129),
    (W,1137,1146),
    # Bagger start-up 1200
    (L,1202,1207),
    (W,1219,1229),
    (L,1236,1241),
    (W,1252,1302), # 17 passengers, "pause"
    (L,1325,1330),
    (W,1337,1347),
    # Engines in yard
    (L,1357,1404), # Landratsamt, slow
    (W,1411,1421),
    (L,1433,1438),
    (W,1445,1455), # interpolated, missing times
    (L,1505,1510), # interpolated, missing times
    (W,1517,1527),
    (L,1534,1539),
    (W,1547,1557),
    (L,1611,1616),
    (W,1621,1631),
    (L,1635,1640), # interpolated, missing times
    (W,1646,1656),
    (G,1701,1713), # interpolated, from photographs
    (F,1717,1729), # interpolated, from photographs
    ]

def parse_timestamp(i):
    s = str(i)
    assert len(s) == 4
    hours = int(s[:2])
    minutes = int(s[-2:])
    return datetime.datetime(2016,5,1,hours,minutes)


def main():
    x = []
    y = []

    def bahnhof(t):
        # Bahnhof
        y.append(45), x.append(t)
    def incline(t,coupling=False,incoming=False,chainage=-40):
        # Incline accent
        d = datetime.timedelta(seconds=50)
        if incoming:
            d = -d
            chainage = chainage + 10

        y.append(chainage), x.append(t + d)
        if not coupling: return
        # Coupling at top of incline
        y.append(chainage), x.append(t + datetime.timedelta(seconds=80))
    def road_crossing(t):
        # Road crossing outbound for flag carrier + slow
        y.append(-168+10), x.append(t + datetime.timedelta(seconds=70))
        y.append(-168+10), x.append(t + datetime.timedelta(seconds=90))
        y.append(-168-10), x.append(t + datetime.timedelta(seconds=100))
    def landratsamt(t):
        # Landratsamt
        y.append(-360), x.append(t + datetime.timedelta(seconds=120))
        y.append(-360), x.append(t + datetime.timedelta(seconds=180))
    def bagger(t):
        # Bagger
        y.append(356), x.append(t - datetime.timedelta(minutes=5.5))
        y.append(356), x.append(t - datetime.timedelta(minutes=4.5))
    def distance(t,d):
        y.append(d), x.append(t)

    # Opening time, static train waiting
    bahnhof(parse_timestamp('1000'))

    labels = []
    # Public trips
    for destination,departure,arrival in times:
        dep = parse_timestamp(departure)
        arr = parse_timestamp(arrival)
        if arr < dep: print 'departed before arrived:', dep, arr

        bahnhof(dep)
        
        mid = dep + (arr - dep)/2
        if destination in ('Land', 'Gros'):
            incline(dep)
            road_crossing(dep)
            landratsamt(dep)
        if destination in ('Wald', 'Oppo', 'Gros'):
            if destination in ('Wald', 'Oppo'):
                incline(dep,coupling=True)
            if destination not in ('Oppo',):
                bagger(arr)
        if destination in ('Oppo',):
            bagger(arr - datetime.timedelta(minutes=4))
            landratsamt(dep + datetime.timedelta(minutes=6))

        labels.append((dep, departure,))

        # Incline Descent
        incline(arr,incoming=True)
        # Bahnhof
        bahnhof(arr)

    # Last train of day, returning to second platform
    distance(parse_timestamp('1729'), 62) # Bahnhof P.2

    # End-of-day shunting
    distance(parse_timestamp('1739'), 62) # Bahnhof P.2
    distance(parse_timestamp('1743'), -112+62) # Carriage shed
    distance(parse_timestamp('1744'), -112+62) # Carriage shed
    distance(parse_timestamp('1748'), 87) # Inside Shed

    def inch(mm): return mm / 25.4

    # Bring up a Figure/Plot
    fig = plt.figure(figsize=(inch(298),inch(150)))
    
    p = plt.plot(x,y)
    plt.setp(p, color='gray')
    ax = plt.gca()
    ax2 = ax.twinx()
    ax.set_title("Wiesloch Feldbahn: Fahrt in den Mai 2016: Time/Distance", position=(0.5,0))

    # Opening/closing hours
    ax.set_xlim(parse_timestamp('1000'), parse_timestamp('1800'))
    ax.set_ylim(-400,400)
    ax.get_xaxis().set_visible(True)

    ax.xaxis.grid(True, which='major')
    ax.xaxis.grid(False, which='minor')

    k,v = zip(*chainages.items())
    ax.yaxis.set_ticks_position('left')
    ax.set_yticks(v)
    ax.set_yticklabels(k, rotation=40, va='baseline')

    ax.yaxis.grid(True, which='major')
    ax.yaxis.grid(False, which='minor')

    ax.set_xlabel('01.05.2016 (CET)')
    ax2.set_xlim(parse_timestamp('1000'), parse_timestamp('1800'))
    ax2.set_ylim(-400,400)
    ax2.set_ylabel(u'Landratsamt          —           Waldstrecke ')
    ax2.get_xaxis().set_visible(False)
    metres = matplotlib.ticker.FormatStrFormatter('%3dm')
    ax2.yaxis.set_major_formatter(metres)
    ax2.yaxis.set_label_position('right')
    ax2.yaxis.set_ticks_position('right')
    hours = matplotlib.dates.DateFormatter("%Hh")
    ax2.xaxis.set_major_formatter(hours)


    (_,first,_) = times[0]
    (_,last,_) = times[-1]
    last = parse_timestamp(last)
    first = parse_timestamp(first)
    spacing = (last-first)/len(times)
    spacing = (last-(first-spacing-spacing))/len(times)

    advance = first
    offset = 15
    for (t,s),(destination,departure,arrival) in zip(labels,times):
        dep = parse_timestamp(departure)
        arr = parse_timestamp(arrival)
        minutes = int((arr-dep).total_seconds() / 60)

        annotation = '%s+%02d' % (s, minutes)
        colour = 'gray'
        vertical = 350
        if destination in 'Wald':
            vertical += 10
            colour='darkgreen'
        elif destination in 'Land':
            vertical -= 20
            colour='darkred'
        elif destination in ('Gros', 'Oppo'):
            colour='darkblue'
        ax.annotate(annotation, xy=(t, vertical), xytext=(advance, 470), ha='left', color=colour, rotation=40, fontsize='small',
                    arrowprops=dict(arrowstyle="->", color=colour, connectionstyle="arc,angleA=220,rad=10,armA=35,armB=0,angleB=0"))
        offset *= -1
        advance += spacing

    plt.savefig('temp.pdf', transparent=True)
    plt.show()

if __name__=='__main__':
    main()

"""
"""
