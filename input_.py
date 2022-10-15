# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import csv
import numpy as np
import cv2
import matplotlib.pyplot as plt

def read_csv(csv_name):
    with open(csv_name) as people_csv:
        reader = csv.reader(people_csv)
        top = 1
        for row in reader:
            if top:
                data = {header: [] for header in row}
                keys = [header for header in row]
                top = 0
            else:
                for i in range(len(row)):
                    data[keys[i]].append(row[i])
    return data

def add_element(image, people_data, header):
    size, throw, away = np.shape(image)
    subjects = {}
    for subject in people_data[header]:
        if subject in subjects:
            subjects[subject] += 1
        else:
            subjects.update({subject: 1})
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_thickness = 3
    text_colour = (0,0,0)
    bg_colour = (0,0,0)
    
    
    cols = int(np.ceil(np.sqrt(len(subjects.keys()))))
    i = 1
    j = 1
    scale = size//(cols+1)
    
    for subject in subjects.keys():
        
        x = i*scale
        y = j*scale
        
        subjects[subject] = [subjects[subject], x, y]
        
        text_size, baseline = cv2.getTextSize(subject, font, font_scale,
                                              font_thickness)
        text_w, text_h = text_size
        pad = 3
        
        #image = cv2.rectangle(image, (x - pad, y - text_h - pad),
        #                      (x + pad, y + pad), bg_colour, -1)
        image = cv2.putText(image, subject, (x-(text_w//2), y), font, font_scale,
                            text_colour, font_thickness)
        
        if i == cols:
            i = 1
            j += 1
        else: i += 1
    
    plt.figure(figsize=(10,10))
    plt.imshow(image, interpolation='nearest')
    plt.show()
    
    radius = 80
    dot_size = 10
    dot_colour = (0,255,0)
    for subject in subjects.keys():
        rad = 2*np.pi/subjects[subject][0]
        angle = 0
        for i in range(subjects[subject][0]):
            x = int(subjects[subject][1] + radius*np.sin(angle))
            y = int(subjects[subject][2] + radius*np.cos(angle))
            
            image = cv2.circle(image, (x,y), dot_size, dot_colour, -1)
            
            angle += rad
    plt.figure(figsize=(10,10))
    plt.imshow(image, interpolation='nearest')
    plt.savefig("Sample.png", dpi=600)
    plt.show()
    
    return image

if __name__ == "__main__":
    people_data = read_csv("Data/people_data.csv")
    location_data = read_csv("Data/location_data.csv")
    security_data = read_csv("Data/security_logs.csv")
    #print(subjects)
    
    size = 1500
    image = np.ones((size,size,3), dtype="uint8")
    image = image*255
    new = add_element(image, people_data, "Subject")