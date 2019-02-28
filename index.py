import csv
from heapq import *
import sys
import datetime

class Node (object):
    def __init__(self, id, d, i, qs):
        self.id=id
        self.decision=d
        self.index=i
        self.qs=qs

def get_path(cameFrom, current):
    return current

def dist(current, child):
    return 0

def dmv(visitors):
    opened=[]
    closed = set()
    cameFrom = {}
    gScore = {}
    fScore = {}
    start=Node('_start', None,-1, [visitors[0].arrival for x in range(3)])
    gScore[start.id]=0
    heappush(opened, (len(visitors), start))

    while len(opened)>0:
        current = heappop(opened)
        if current.id == 'end':
            return get_path(cameFrom, current)
        closed.add(current)
        #define children as the possible decisions

        for each in children:
            if each in closed:
                continue
            #define dist as adding time to finish
            temp = gScore[current]+dist(current,each)
            if each not in opened:
                heappush(opened, (temp + each.index, each))
            elif temp >= gScore[each.id]:
                continue
            #they will never be in opened already but the branches are isolated i think. nodes never share children
            cameFrom[each.id] = current
            gScore[each.id] = temp



parse_time = lambda time: datetime.datetime.strptime(time, "%Y-%m-%d-%H:%M:%S").time()

visitors = []
with open(sys.argv[1]) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        visitors.append(dict(row))

visitors.sort(key=lambda x :  parse_time(x['Time_Arrival']))

for each in visitors:
    print(each)
#there are dup times
