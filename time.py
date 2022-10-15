# -*- coding: utf-8 -*-
"""
Created on Sat Oct 15 00:21:42 2022

@author: hbarr
"""
import csv

def read_csv(csv_name, i=None):
    with open(csv_name) as people_csv:
        reader = csv.reader(people_csv)
        top = 1
        if i == None:
            data = []
        else:
            data = {}
        for row in reader:
            if top:
                top = 0
            elif i != None:
                if row[i] in data:
                    data[row[i]].append(row[:i]+row[i+1:])
                else:
                    data.update({row[i]:[row[:i]+row[i+1:]]})
            else:
                data.append(row)
    return data

def prep_security_data(security_data):
    for student in security_data.keys():
        for i in range(len(security_data[student])):
            track = security_data[student][i]
            track[2]=track[2].split("-")
            track[2][0] = int(track[2][0])
            track[2][1] = int(track[2][1])
            if track[2][0] > track[2][1]:
                track[2][1] += 2400
            security_data[student][i] = track
    return security_data

def locations(time, location_data, security_data):
    location_lists = {place: [] for place in location_data.keys()}
    location_lists.update({"In transit": []})
    
    for student in security_data.keys():
        tracked = False
        for track in security_data[student]:
            if time <= track[2][1] and time >= track[2][0]:
                location_lists[track[1]].append(student)
                tracked = True
        
        if not tracked:
            earl = None
            late = None
            for track in security_data[student]:
                if track[2][1] < time and ((not earl)
                                           or track[2][1] > earl[2][1]):
                    earl = track
                elif track[2][0] > time and ((not late)
                                             or track[2][0] < late[2][0]):
                    late = track
            '''
            if earl:
                earl_lim =time-30
                if earl_lim%100 > 59:
                    earl_lim -= 40
                if earl[2][1] < earl_lim:
                    earl = None
            if late:
                late_lim =time+30
                if late_lim%100 > 59:
                    late_lim += 40
                if late[2][0] > late_lim:
                    late = None'''
            
            if earl and late:
                location_lists["In transit"].append([earl[1],earl[2][1],student,
                                                     late[1],late[2][0]])
            elif not earl:
                location_lists["In transit"].append([None,None,student,
                                                     late[1],late[2][0]])
            else:
                location_lists["In transit"].append([earl[1],earl[2][1],
                                                     student,None,None])
            
                
                
                    
                
    return location_lists

location_data = read_csv("Data/location_data.csv", 0)
security_data = read_csv("Data/security_logs.csv", 0)
security_data = prep_security_data(security_data)

print(locations(1200, location_data, security_data))