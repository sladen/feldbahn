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

chainages = {
 'Waldstrecke': +407, # Farther extend of loop before returning
# 'forest_construction': +300,
 'Eimerkettenbagger': +340,
# 'sidings': +281,
# 'loop': +181,
# 'Rundweichen': 181,
 'Weichen Rundf.': 181,
 'Lokschuppen\n': +90,
# 'Bahnhof': +50,
 'Feldbahnhof': +45,
# 'points': 0,
 'Eingang X': -10,
# 'reversal': -30,
# u'Adelsförsterpfad': -168,
# u'crossing': -168,
 u'Adelsförsterpfad X': -168,
 u'Fußgänger X': -311,
 'Landratsamt': -386,
 }

"""
[Forest +300 (+276)]
Bagger track +376 (+357)
Bagger +376-36
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
# Landratsamt, Waldstrecke, Großefahrt (Landratsamt+Waldstrecke), Fahrt-Opposite (Waldstrecke+Landratsamt)
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
    (L,1433,1437), # arrival refined from photograph
    (W,1446,1456), # interpolated, + from photographs
    (L,1501,1506), # interpolated, + from photographs
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
        y.append(181), x.append(t - datetime.timedelta(minutes=6.5))
        y.append(336), x.append(t - datetime.timedelta(minutes=5.5))
        y.append(336), x.append(t - datetime.timedelta(minutes=4.5))
        y.append(181), x.append(t - datetime.timedelta(minutes=3.5))
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
            bagger(arr - datetime.timedelta(minutes=3))
            road_crossing(arr - datetime.timedelta(minutes=5))
            landratsamt(arr - datetime.timedelta(minutes=5))

        labels.append((dep, departure,))

        # Incline Descent
        incline(arr,incoming=True)
        # Bahnhof
        bahnhof(arr)

    # Last train of day, returning to second platform
    distance(parse_timestamp('1729'), 62) # Bahnhof P.2

    # End-of-day shunting
    distance(parse_timestamp('1739'), 62) # Bahnhof P.2
    distance(parse_timestamp('1741'), 59-40) # Mid-way-siding points
    distance(parse_timestamp('1743'), 59-40) # Mid-way-siding points
    distance(parse_timestamp('1744'), 59-129+2) # Carriage shed
    distance(parse_timestamp('1745'), 59-129+2) # Carriage shed LE
    distance(parse_timestamp('1745'), 59-129+2+18) # Carriage shed LE
    distance(parse_timestamp('1749'), 79) # Front of Lokshuppen

    saved_xy = x,y
    x, y = [], []
    
    # End-of-day shunting - Light-engine to fetch flat wagon
    # and shunting again to allow empty carriages to pass
    distance(parse_timestamp('1727'), -360) # Light engine from Landratsamt
    distance(parse_timestamp('1728'), -360) # 
    distance(parse_timestamp('1730'), 59) # Bahnhof P.2 "02 points"
    distance(parse_timestamp('1731'), 59) # Bahnhof P.2 "02 points"
    distance(parse_timestamp('1732'), 59-80) # Waiting for Child with Bicycle
    distance(parse_timestamp('1733'), 59-80)
    distance(parse_timestamp('1734'), 59-90) # Hand-shunting of display sign wagons + etc
    distance(parse_timestamp('1737'), 59-90) 
    distance(parse_timestamp('1738'), 59-105) # Fetch flat wagon from outside carriage shed
    distance(parse_timestamp('1739'), 59-105) # Fetch flat wagon from outside carriage shed
    distance(parse_timestamp('1740'), 59-51) # Mid-way-siding points
    distance(parse_timestamp('1741'), 59-51) # Mid-way-siding points
    distance(parse_timestamp('1742'), 59-65) # Wait in Mid-way-siding for passenger wagons to pass
    distance(parse_timestamp('1744'), 59-65) # Wait in Mid-way-siding for passenger wagons to pass
    distance(parse_timestamp('1747'), 85) # Lok+wagon to mid-point of Lokshuppen
    distance(parse_timestamp('1750'), 85) # Lok+wagon to mid-point of Lokshuppen
    end_of_day_movement = x,y
    x,y = saved_xy

    # Bring up a Figure/Plot
    def inch(mm): return mm / 25.4
    fig = plt.figure(222,figsize=(inch(298),inch(150)))

    plt.rcParams['font.family'] = 'Ubuntu Mono'

    ax = fig.add_subplot(1,1,1)
    q = plt.plot(*end_of_day_movement, color='lightgray')
    p = plt.plot(x,y)
    plt.setp(p, color='gray')
    ax2 = ax.twinx()
    ax.set_title(u"Wiesloch Feldbahnmuseum: Zeit/Weg und Warten (Fahrt in den Mai 2016)", position=(0.5,-0.11), color='darkgray')

    # Opening/closing hours
    ax.set_xlim(parse_timestamp('1000'), parse_timestamp('1800'))
    ax.set_ylim(-400,400)
    ax.get_xaxis().set_visible(True)

    ax.xaxis.grid(True, which='major')
    ax.xaxis.grid(False, which='minor')

    k,v = zip(*chainages.items())
    ax.yaxis.set_ticks_position('left')
    ax.set_yticks(v)
    ax.set_yticklabels(k, rotation=30, va='baseline')

    ax.yaxis.grid(True, which='major')
    ax.yaxis.grid(False, which='minor')

    # Highlight eyeballed *Waldstrecke* localised peak waiting times - "Spitzenwartezeit"
    annotation = 'Waldstrecke\nSpitzenwartezeit'
    annotation = 'Spitzenwartezeit'
    #ax.axvspan(parse_timestamp(1210), parse_timestamp(1300), 0.4, 0.7, color='lightyellow')
    #ax.axvspan(parse_timestamp(1510), parse_timestamp(1600), 0.4, 0.7, color='lightyellow')

    colour = 'darkgray'
    text_pos = 140
    bbox_props = dict(boxstyle="rarrow,pad=0.1", fc="lightyellow", ec="lightgray", lw=0.5)
    t = parse_timestamp(1210)
    ax.annotate(annotation, xy=(t, -100), xytext=(t, text_pos), ha='left', color=colour, rotation=-2, fontsize='x-small', va='bottom',
                bbox=bbox_props)
    text_pos -= 10
    t = parse_timestamp(1510)
    ax.annotate(annotation, xy=(t, -100), xytext=(t, text_pos), ha='left', color=colour, rotation=-2, fontsize='x-small', va='bottom',
                bbox=bbox_props)

    # Freifahrt
    text_pos -= 10
    annotation = 'Freifahrt'
    bbox_props['fc'] = 'aliceblue'
    #ax.axvspan(parse_timestamp(1700), parse_timestamp(1730), 0.4, 0.7, color='aliceblue')
    ax.axvspan(parse_timestamp(1700), parse_timestamp(1730), 0.0, 1.0, color='aliceblue')
    t = parse_timestamp(1700)
    ax.annotate(annotation, xy=(t, -100), xytext=(t, text_pos), ha='left', color=colour, rotation=-2, fontsize='x-small', va='bottom',
                bbox=bbox_props)

    # Waiting time trend lines
    colour = 'lightgray'
    t = parse_timestamp(1056)
    tt = parse_timestamp(1054)
    annotation = 'Waldstr.\nWarte\nund\nTrends'
    text_pos = 195
    ax.annotate(annotation, xy=(t, 115), xytext=(tt, text_pos), ha='center', color=colour, rotation=0, fontsize='x-small', va='bottom',
                backgroundcolor='white', 
                arrowprops=dict(arrowstyle="->", color=colour, connectionstyle="arc,angleA=248,rad=10,armA=45"))

    # Lunch break definite "pausen"
    colour = 'lightgray'
    t = parse_timestamp(1316)
    tt = parse_timestamp(1318)
    annotation = '"Mittagspause"'
    annotation = '"Mittags-\npausen"'
    text_pos = 220
    ax.annotate(annotation, xy=(t, 100), xytext=(tt, text_pos), ha='center', color=colour, rotation=0, fontsize='small', va='bottom',
                arrowprops=dict(arrowstyle="->", color=colour, connectionstyle="arc,angleA=272,rad=10,armA=35,armB=0,angleB=0"))
    

    # Waiting time possible preference for Waldstrecke.
    t = parse_timestamp(1430)
    t = parse_timestamp(1352)
    tt = parse_timestamp(1433)
    tt = parse_timestamp(1359)
    tt = parse_timestamp(1412)
    annotation = u'Eventuell\nPräferenz\nWaldstr.?'
    annotation = u'Präferenz\nWaldstrecke?'
    text_pos = 270
    colour='darkgray'
    bbox_props=dict(boxstyle="round4,pad=0.3", fc="lightyellow", ec="lightgray", lw=0.3)
    ax.annotate(annotation, xy=(t, 84), xytext=(tt, text_pos), ha='center', color=colour, rotation=0, fontsize='x-small', va='top',
                bbox=bbox_props,
#                backgroundcolor='lightyellow',
                arrowprops=dict(arrowstyle="->", color='gray', connectionstyle="arc,angleA=238,rad=10,armA=67"))

    

    #ax.set_xlabel('01.05.2016 (CET)', labelpad=-29, ha='right', position=(0.99,0), color='gray')
    ax2.set_xlim(parse_timestamp('1000'), parse_timestamp('1800'))
    ax2.set_ylim(-400,400)
    #print `datetime.datetime.strftime('%d.%m.%Y', ax.get_xticks()[0])`
    german_date = matplotlib.dates.DateFormatter("%d.%m.%Y (CET)")
    ax.set_xlabel(german_date(ax.get_xlim()[0]), labelpad=-27, ha='left', position=(0.01,0), color='lightgray', fontsize='x-small')
    #ax2.set_ylabel(u'Landratsamt          —           Waldstrecke')

    # Right
    #ax2.set_ylabel(u'Metierung Süd ↔ Nord', size='small', color='darkgray', labelpad=-32, ha='center')
    ax2.set_ylabel(u'Metierung', size='small', color='darkgray', labelpad=-28, ha='center')
    ax2.set_ylabel(u'Kilometierung', size='small', color='darkgray', labelpad=-28, ha='center')
    ax2.get_xaxis().set_visible(False)
    metres = matplotlib.ticker.FormatStrFormatter('%3dm')
    def abs_metres(value, position):
        s = 'km0+%03d' % abs(value)
        s = 'km%d+%03d' % divmod(abs(value), 1000)
        #if value < 0:
        #    s = s.replace('+','-')
        if abs(value) <1:
            s = 'null'
            s = 'km0'
        return s
    metres = matplotlib.ticker.FuncFormatter(abs_metres)
    ax2.yaxis.set_major_formatter(metres)
    ax2.yaxis.set_label_position('right')
    ax2.yaxis.set_ticks_position('right')
    #ax2.tick_params(axis='y', colors='darkgray')

    # Bottom
    hours = matplotlib.dates.DateFormatter("%Hh")
    ax2.xaxis.set_major_formatter(hours)


    # Top (Abfahrtszeit+Länge (Minuten))
    plt.text(-0.13, 1.1, u'Abfahrtszeit+Länge in Minuten\nWaldstrecke ~10min (870m)\nLandratsamt ~05min (820m)', ha='left', va='top', transform = ax.transAxes, color='darkgray', fontsize='x-small',
             rotation=0)

    (_,first,_) = times[0]
    (_,last,_) = times[-1]
    last = parse_timestamp(last)
    first = parse_timestamp(first)
    spacing = (last-first)/len(times)
    spacing = (last-(first-spacing-spacing))/len(times)

    # 
    advance = first
    offset = 15
    for (t,s),(destination,departure,arrival) in zip(labels,times):
        dep = parse_timestamp(departure)
        arr = parse_timestamp(arrival)
        minutes = int((arr-dep).total_seconds() / 60)
        pretty_time = '%02d:%02d' % (departure/100, departure % 100)
        annotation = '%s+%02d' % (pretty_time, minutes)
        #if departure == 1252:
        #    annotation = '*' + annotation
        colour = 'gray'
        vertical = 350
        if destination in 'Wald':
            vertical += 10
            colour='darkgreen'
        elif destination in 'Land':
            vertical -= 20
            colour='saddlebrown'
        elif destination in ('Gros', 'Oppo'):
            colour='darkblue'
        ax.annotate(annotation, xy=(t, vertical), xytext=(advance, 470), ha='left', color=colour, rotation=30, fontsize='small',
                    arrowprops=dict(arrowstyle="->", color=colour, connectionstyle="arc,angleA=220,rad=10,armA=35,armB=0,angleB=0"))
        offset *= -1
        advance += spacing

    waits = []
    land_waits = []
    wald_waits = []
    last_arr = parse_timestamp('1000')
    for (dest,departure,arrival) in times:
        dep = parse_timestamp(departure)
        waiting_minutes = int((dep-last_arr).total_seconds() / 60)
        mid_time = last_arr + (dep-last_arr)/2
        coord = (mid_time, waiting_minutes * 10,)
        waits.append(coord)
        # Exclude excessively long Mittagessen pausen
        if True or waiting_minutes not in (23,):
            if dest in 'Land':
                land_waits.append(coord)
            elif dest in 'Wald':
                wald_waits.append(coord)
        #ax.annotate('%d' % waiting_minutes, xy=(mid_time, 45), xytext=(dep, 50), ha='right', color='gray', fontsize='small')
        colours = {'Land': 'saddlebrown',
                   'Wald': 'darkgreen',
                   'Oppo': 'darkblue',
                   'Gros': 'darkblue'}
        colour = colours[dest]
        colour = 'darkgray'
        ax.annotate('%d' % waiting_minutes, xy=(mid_time, 45), xytext=(mid_time, 50), ha='center', color=colour, fontsize='small')
        last_arr = parse_timestamp(arrival)
    #ax.plot(*zip(*land_waits), linestyle=':', color='saddlebrown')
    wx,wy = zip(*wald_waits)
    ax.plot(wx,wy, linestyle=':', color='darkgreen')

    wx,wy = zip(*wald_waits[:4])
    wx2 = matplotlib.dates.date2num(wx)
    p = numpy.poly1d(numpy.polyfit(wx2, wy, 1))
    ax2.plot(wx,p(wx2),"r--", color='darkgreen')
    wx,wy = zip(*wald_waits[4:])
    wx2 = matplotlib.dates.date2num(wx)
    p = numpy.poly1d(numpy.polyfit(wx2, wy, 1))
    ax2.plot(wx,p(wx2),"r--", color='darkgreen')

    # Landratsamt waiting times are essentially random, doesn't really help with visualisation
    wx,wy = zip(*land_waits)
    #ax.plot(wx,wy, linestyle=':', color='lightgray')
    wx,wy = zip(*land_waits[:4])
    #ax.plot(wx,wy, linestyle=':', color='saddlebrown')
    wx2 = matplotlib.dates.date2num(wx)
    p = numpy.poly1d(numpy.polyfit(wx2, wy, 1))
    ax2.plot(wx,p(wx2),"r--", color='saddlebrown')
    # Break over lunch ignoring extended pause outlier
    wx,wy = zip(*land_waits[5:])
    wx2 = matplotlib.dates.date2num(wx)
    p = numpy.poly1d(numpy.polyfit(wx2, wy, 1))
    ax2.plot(wx,p(wx2),"r--", color='saddlebrown')

    # Major destination labels
    for l in ax.get_yticklabels():
        if l.get_text() in ('Waldstrecke', 'Feldbahnhof', 'Landratsamt'):
            l.set_weight('bold')
        else:
            l.set_size('small')
            

        if l.get_text() in (u'Adelsförsterpfad X', u'Fußgänger X', u'Landratsamt'):
            l.set_color('saddlebrown')
        elif l.get_text() in (u'Weichen Rundf.', u'Eimerkettenbagger', u'Waldstrecke'):
            l.set_color('darkgreen')
        elif l.get_text() in ('Feldbahnhof', 'Eingang X'):
            l.set_color('darkblue')
        else:
            l.set_color('darkgray')

    # Per-metre distances
    for l in ax2.get_yticklabels():
        l.set_size('x-small')
        l.set_ha('right')
        l.set_color('darkgray')
    ax2.tick_params(direction='in', pad=35)

    # Mileometer
    movements = map(abs,map(operator.sub, y[1:], y[:-1]))
    meterometer = sum(movements)
    timings = map(abs,map(operator.sub, x[1:], x[:-1]))
    total_time = sum(timings, datetime.timedelta())
    total_moving = sum([dt for ddist,dt in zip(movements,timings) if ddist is not 0], datetime.timedelta())
    total_stopped = sum([dt for ddist,dt in zip(movements,timings) if ddist is 0], datetime.timedelta())
    print total_time, total_moving, total_stopped
    kilometres = 0.001 * meterometer
    moving_kph = 3.6*meterometer/total_moving.total_seconds()
    ax.annotate(u'%.1fkm @ %.1fkm/h' % (kilometres, moving_kph),
                xy=(x[-1],y[-1]),
                xytext=(x[-1],y[-1]+20),
                rotation=82, fontsize='small', color='gray', ha='center', backgroundcolor='white',
                va='bottom')

    # Empty trains - Auslastung
    # 4 pax on 10:28 - 4 Gä.
    rotation = 0
    arrow_rotation = 100
    t = parse_timestamp(times[0][1]) - datetime.timedelta(minutes=1)
    tt = t - datetime.timedelta(minutes=1)
    ax.annotate(u'1.\nAuslas\n<10%\n', xy=(t, -10), xytext=(tt, -220), ha='right', color='lightgray', fontsize='small', rotation=rotation, va='top',
#                backgroundcolor='white',
                arrowprops=dict(arrowstyle="->", color='lightgray', 
                                connectionstyle="arc,angleA=%d,rad=10,armA=80,armB=0,angleB=0" % (arrow_rotation -7)))

    # 17 pax on 12:52 "17 Gäste"
    arrow_rotation = 110 -4
    t = parse_timestamp(1252)
    tt = t + datetime.timedelta(minutes=11)
    tt = parse_timestamp(1300)
    ax.annotate(u'12:52\nAuslastung\n<40%', xy=(t, -40), xytext=(tt, -220), ha='center', color='lightgray', fontsize='small',
                rotation=rotation, va='top',
#                backgroundcolor='lightyellow',
                backgroundcolor='white',
                arrowprops=dict(arrowstyle="->", color='lightgray',
                                connectionstyle="arc,angleA=%d,rad=10,armA=50,armB=0,angleB=40" % arrow_rotation))
    # 2x full trains - voll
    t = parse_timestamp(1715)
    #ax.annotate('100%', xy=(t, -40), xytext=(t, -320), ha='center', color='gray', fontsize='small', rotation=rotation, va='top')
    
    #            arrowprops=dict(arrowstyle="->", color='gray', connectionstyle="arc,angleA=120,rad=10,armA=35,armB=0,angleB=40"))

    # Now finally do something useful with it.
    fig.savefig('temp.pdf', transparent=True, papertype='a4', orientation='landscape')

    # Quick and dirty way of stamping the track diagram over the top, sadly not auto-aligned...
    import subprocess
    subprocess.call(["pdftk", "temp.pdf", "background", "track-diagram-overlay.pdf", "output", "2016-fahrt-in-mai.pdf"])

    # Failed attempt to get the GUI updating of the date to work
    def onresize(event):
        print 'onresize()', ax.get_xticks()[0], ax2.get_xlim()[0]
        ax2.set_xlabel(german_date(ax.get_xticks()[0]), labelpad=-29, ha='right', position=(0.99,0), color='gray')
        fig.canvas.draw()
    ax2.callbacks.connect('xlim_changed', onresize)

    # Show interactively; skipped if there's no live terminal
    import sys
    if sys.stdout.isatty():
        plt.show()

if __name__=='__main__':
    main()

"""
"""
