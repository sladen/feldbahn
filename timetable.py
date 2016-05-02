#!/usr/bin/env python
import matplotlib.pyplot as plt
import datetime
import random

chainages = {
 'forest_construction': +300,
 'bagger': +376-20,
 'sidings': +281,
 'loop_points': +181,
 'bahnhof': +124-84,
 'points': 0,
 'eingang': -10,
 'reversal': -30,
 'road': -168,
 'foot': -311,
 'landratsamt': -386 + 36,
 }

"""
[Forest +300 (+276)]
Bagger +376 (+356)
Sidings +281
Points +181
Bahnhof +124 (+40)
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
        y.append(40), x.append(t)
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

        # Incline Descent
        incline(arr,incoming=True)
        # Bahnhof
        bahnhof(arr)

    # Last train of day, returning to second platform
    distance(parse_timestamp('1729'), 62) # Bahnhof P.2

    # Shunting
    distance(parse_timestamp('1739'), 62) # Bahnhof P.2
    distance(parse_timestamp('1743'), -112+62) # Carriage shed
    distance(parse_timestamp('1744'), -112+62) # Carriage shed
    distance(parse_timestamp('1748'), 87) # Inside Shed

    p = plt.plot(x,y)
    print `p[0]`, dir(p[0])
    # Opening/closing hours
    plt.xlim(parse_timestamp('1000'), parse_timestamp('1800'))
    plt.setp(p, color='gray')
    plt.xlabel('Departure Time: 01.05.2016 (CET)')
    plt.ylabel('Distance')
    plt.gcf().autofmt_xdate()
    q = plt.plot()
    p[0].axes.yaxis.set_ticks_position('left')
    p[0].axes.yaxis.set_label_position('right')

            

    plt.yticks([200,0,-200], ['a','b','c'])
    plt.savefig('temp.pdf', transparent=True)
    plt.show()

if __name__=='__main__':
    main()

"""
"""
