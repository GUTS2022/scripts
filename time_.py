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

def prep_location_data(location_data):
    for place in location_data.keys():
        location_data[place] = location_data[place][0]
        location_data[place][1] = location_data[place][1].split("-")
        location_data[place][1][0] = int(location_data[place][1][0])
        location_data[place][1][1] = int(location_data[place][1][1])
    return location_data

def prep_people_data(people_data):
    for student in people_data.keys():
        people_data[student] = people_data[student][0]
        if people_data[student][7] == "N/A":
            people_data[student][7] = []
        else:
            people_data[student][7] = people_data[student][7].strip("[]{}")
            people_data[student][7] = people_data[student][7].split(", ")
            for i in range(len(people_data[student][7])):
                people_data[student][7][i] = people_data[student][7][i].strip("'")
                people_data[student][7][i] = people_data[student][7][i].strip('"')
    return people_data

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
            
            if earl and late:
                location_lists["In transit"].append([earl[1],earl[2][1],student,
                                                     late[1],late[2][0]])
            elif not earl:
                location_lists["In transit"].append([None,None,student,
                                                     late[1],late[2][0]])
            else:
                location_lists["In transit"].append([earl[1],earl[2][1],
                                                     student,None,None])
    
    for place in location_data.keys():
        if location_data[place][1][0] >= location_data[place][1][1]:
            location_lists[place].append(location_data[place][1][0] <= time%2400
                                        or location_data[place][1][1] >= time%2400)
        else:
            location_lists[place].append(location_data[place][1][0] <= time%2400
                                        and location_data[place][1][1] >= time%2400)
                    
                
    return location_lists

def get_connection_ids(people_data, i):
    subjects = {}
    for student in people_data.keys():
        subject = people_data[student][i]
        if subject in subjects:
            subjects[subject].add(student)
        else:
            subjects.update({subject: {student}})
    return subjects

def get_soc_connection_ids(people_data):
    societies = {}
    for student in people_data.keys():
        for soc in people_data[student][7]:
            if soc in societies:
                societies[soc].add(student)
            else:
                societies.update({soc: {student}})
    return societies

if __name__ == "__main__":
    location_data = read_csv("Data/location_data.csv", 0)
    security_data = read_csv("Data/security_logs.csv", 0)
    people_data = read_csv("Data/people_data.csv", 0)
    location_data = prep_location_data(location_data)
    security_data = prep_security_data(security_data)
    people_data = prep_people_data(people_data)
    
    print(get_connection_ids(people_data, 4))
    societies = get_soc_connection_ids(people_data)
    for key in societies.keys():
        print(key, len(societies[key])-1)
    
    '''
    locations_list = locations(1300, location_data, security_data)
    for key in locations_list.keys():
        print(key, len(locations_list[key])-1)'''