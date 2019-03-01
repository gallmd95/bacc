import csv
from heapq import *
import sys
import datetime
import time

#precision coefficient ε*h(x)
epsilon = 75


parse_time = lambda time: datetime.datetime.strptime(time, "%Y-%m-%d-%H:%M:%S")
priorities = {'low':['low','medium','high'], 'medium':['medium','high'], 'high':['high']}
get_options = lambda priority: priorities[priority]
choices = {"low":0,"medium":1,"high":2}
get_choice = lambda choice: choices[choice]

class Node (object):
    def __init__(self, id, d, i, qs, children, start_time, end_time):
        self.id=id
        self.decision=d
        self.index=i
        self.qs=qs
        self.children=children
        self.start_time = start_time
        self.end_time = end_time
    def __str__(self):
        return  self.id+","+self.decision+","+datetime.datetime.isoformat(self.start_time)+","+datetime.datetime.isoformat(self.end_time)
    def __lt__(self, other):
        return self.index < other.index
    def __gt__(self, other):
        return self.index > other.index

def get_path(cameFrom, current):
    path = []
    while current in cameFrom:
        if current.id == '_start':
            continue
        current = cameFrom[current]
        path = [current] + path
    return path[1:]

def dist(current, child):
    return (max(child.qs) - max(current.qs)).total_seconds() / 60

def update_qs(option, qs, visitor):
    choice = get_choice(option)
    return [qs[i] if choice!=i else (max(qs[i], visitor['Time_Arrival'])+ datetime.timedelta(minutes=int(visitor['Processing_Time'])))
        for i in range(3)]    

def get_children(node, dmvVisitors):  
    nextVisitors = []
    if len(node.children) > 0:
        nextVisitors = node.children
    else:
        start = node.index + 1
        while start < len(dmvVisitors)-1 and dmvVisitors[node.index]['Time_Arrival'] == dmvVisitors[start]['Time_Arrival']:
            start += 1
        if start >= len(dmvVisitors):
            return [Node("_end", "end", len(dmvVisitors), [max(node.qs) for x in range(3)],[],max(node.qs),max(node.qs))]
        finish = start
        while finish < len(dmvVisitors)-1 and dmvVisitors[finish]['Time_Arrival'] == dmvVisitors[finish+1]['Time_Arrival']:
            finish += 1
        finish += 1
        nextVisitors = dmvVisitors[start:finish]
        tempIndex = start
        for each in nextVisitors:
            each['Index'] = tempIndex
            tempIndex+=1
    newNodes = []
    for visitor in nextVisitors:
        children = [child for child in nextVisitors if child['Customer_ID']!=visitor['Customer_ID']]
        options = get_options(visitor['Priority'])
        for option in options:
            start_time = max(node.qs[get_choice(option)], visitor['Time_Arrival'])
            end_time = max(node.qs[get_choice(option)], visitor['Time_Arrival'])+ datetime.timedelta(minutes=int(visitor['Processing_Time']))
            newNodes.append(
                Node(visitor['Customer_ID'], 
                    option, 
                    visitor['Index'],
                    update_qs(option, node.qs, visitor),  
                    children,
                    start_time,
                    end_time
                    )
            )
    return newNodes

def dmv(dmvVisitors):
    l = len(dmvVisitors)
    count=0
    opened=[]
    closed = set()
    cameFrom = {}
    gScore = {}
    start=Node('_start', "low",-1, [ dmvVisitors[0]['Time_Arrival'] for x in range(3)],[],dmvVisitors[0]['Time_Arrival'],dmvVisitors[0]['Time_Arrival'])
    gScore[start.id]=0
    heappush(opened, (len(dmvVisitors), start))

    while len(opened)>0:
        current = heappop(opened)
        if current[1].id == '_end':
            return get_path(cameFrom, current[1])
        closed.add(current[1])
        children = get_children(current[1], dmvVisitors)
        for child in children:
            if child in closed:
                continue
            temp = gScore[current[1].id]+dist(current[1],child)
            if child not in opened:
                heappush(opened, (temp + epsilon*(l-child.index), child))
            elif temp >= gScore[child.id]:
                continue
            cameFrom[child] = current[1]
            gScore[child.id] = temp
            count += 1
            
visitors = []
with open(sys.argv[1]) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        visitors.append(dict(row))

for each in visitors:
    each['Time_Arrival'] = parse_time(each['Time_Arrival'])

visitors.sort(key=lambda x : x['Time_Arrival'])

best = dmv(visitors)

with open('result.csv', 'w') as file:
    file.write("Customer_ID,Counter_ID,Start_Time,End_Time\n")
    for row in best:
        file.write(str(row)+"\n")

print((best[-1].end_time - best[0].start_time).total_seconds() / 60)