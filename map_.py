# -*- coding: utf-8 -*-
"""
Created on Sat Oct 15 22:40:35 2022

@author: hbarr
"""

import time_
import extract_testimony as et

import tkinter as tk

import cv2
import numpy as np
from PIL import Image, ImageTk

def check_for_root(active_gui_master, gui_name, *args, **kwargs):
    """
    Creates a tkinter window built out of a root instance. If no root instance
    exists, a root instance is created.
    Parameters
    ----------
    active_gui_master : TKinter object
        The initial root master instance.
    gui_name : Custom GUI class
        The GUI class which is being opened.
    *args :
        The arguments needed by the custom GUI class.
    **kwargs :
        The keyword arguments needed by the custom GUI class.
    Returns
    -------
    gui_instance : Custom GUI instance
        The object created, through which the tkinter window is modified.
    """
    # The tk.Toplevel and tk.Tk objects are very similar, in that they both
    # create TKinter windows which can be modified in the same way.
    # However there can only be one instance of the base tk.Tk object.
    # Therefore, new windows must be created using tk.Toplevel
    if active_gui_master != None:
        new_window = tk.Toplevel(active_gui_master)
        gui_instance = gui_name(new_window, *args, **kwargs)
        new_window.wait_window()
        
    else:
        root = tk.Tk()
        gui_instance = gui_name(root, *args, **kwargs)
        root.mainloop()
    return gui_instance

def update_display_label(label, img):
    """
    Displays an image through a TKinter label.
    Parameters
    ----------
    label : tk.Label object
        This label has properties such as a defined position within the
        TKinter window.
    img : Array-like
        The image to be displayed. It simply needs to be numpy compatible.
    """
    # Convert the Image object into a TkPhoto object, compatible with TKinter
    # labels.
    imgtk = Image.fromarray(img.astype(np.uint8))
    imgtk = ImageTk.PhotoImage(image=imgtk)
    
    # Display the image in the assigned label.
    label.configure(image = imgtk)
    label.image = imgtk

class map_viewer:
    def __init__(self, master):
        self.master = master
        self.master.attributes("-fullscreen", True)
        self.big_frame = tk.Label(self.master, image=[])
        self.big_frame.grid(column = 0, row = 0)
        
        self.time = 900        
        self.timer = tk.Scale(self.master, from_=0, to=3000,
                              length=1000,
                              orient=tk.HORIZONTAL,
                              tickinterval=120,
                              command=self.update_time)
        self.timer.set(self.time)
        self.timer.grid(column = 0, row = 1)
        
        self.text = ""
        self.text_disp = tk.Label(self.master, text=self.text)
        self.text_disp.grid(column = 1, row = 0, rowspan = 2)
        
        self.big_frame.bind('<Button-1>', self.click_event)
        #self.big_frame.bind('<B1-Motion>', self.motion_event)
        #self.big_frame.bind('<Button-1>', self.click_event)
        #self.big_frame.bind('<ButtonRelease-1>', self.release_event)
        
        self.background = cv2.imread("Data/Screenshot (15).png")
        self.background = cv2.resize(self.background, (1280, 720))
        update_display_label(self.big_frame, self.background)
        
        self.people_data = time_.read_csv("Data/people_data.csv",0)
        self.people_data = time_.prep_people_data(self.people_data)
        self.societies = time_.get_soc_connection_ids(self.people_data)
        self.subjects = time_.get_connection_ids(self.people_data, 4)
        
        self.location_data = time_.read_csv("Data/location_data_.csv", 0)
        self.location_data = time_.prep_location_data(self.location_data)
        
        self.security_data = time_.read_csv("Data/security_logs.csv", 0)
        self.security_data = time_.prep_security_data(self.security_data)
        self.locations_list = time_.locations(self.time, self.location_data,
                                              self.security_data)
        
        self.tests = et.extract_tests()
        
        self.transit_loc = [30, 875]
        self.outliers = set()
        self.place_buildings()
        self.place_students()
    
    def place_buildings(self):
        keys = [key for key in self.location_data.keys()]
        self.img = self.background.copy()
        for i in range(len(keys)):
            if (len(self.locations_list[keys[i]]) > 1 
                and not self.locations_list[keys[i]][-1]):
                colour = (255,0,0)
            else:
                colour = (0,0,0)
            coords = self.location_data[keys[i]][0]
            self.img = cv2.circle(self.img, (coords[1], coords[0]),
                                  10, colour, -1)
        self.img = cv2.circle(self.img, (self.transit_loc[1], self.transit_loc[0]),
                              10, (0,0,255), -1)
        update_display_label(self.big_frame, self.img)
    
    def update_time(self, time):
        self.time = int(time)/2
        self.locations_list = time_.locations(self.time, self.location_data,
                                              self.security_data)
        self.place_buildings()
        self.place_students()
    
    def place_students(self):
        keys = [key for key in self.location_data.keys()]
        self.coords = []
        for i in range(len(keys)):
            angle = 0
            radius = 15
            rad = 2*np.pi/15
            if len(self.locations_list[keys[i]]) > 1:
                for j in range(len(self.locations_list[keys[i]])-1):
                    if self.locations_list[keys[i]][j] in self.people_data:
                        colour = self.people_data[self.locations_list[keys[i]][j]][6]
                        coords = self.location_data[keys[i]][0]
                        x = int(coords[1] + radius*np.sin(angle))
                        y = int(coords[0] + radius*np.cos(angle))
                        self.img = cv2.circle(self.img, (x, y),
                                              3, colour, -1)
                        self.coords.append((x,y, self.locations_list[keys[i]][j]))
                        if j == 15:
                            rad = 2*np.pi/25
                            radius = 22
                            angle = 0
                        elif j == 40:
                            rad = 2*np.pi/30
                            radius = 29
                            angle = 0
                        else:
                            angle += rad
                    else:
                        self.outliers.add(self.locations_list[keys[i]][j])
        if self.locations_list["In transit"]:
            transit_list = self.locations_list["In transit"]
            for i in range(len(transit_list)):
                if transit_list[i][2] not in self.people_data:
                    self.outliers.add(transit_list[i][2])
                else:
                    colour = self.people_data[transit_list[i][2]][6]
                    if transit_list[i][0] and transit_list[i][-1]:
                        coords1 = self.location_data[transit_list[i][0]][0]
                        coords2 = self.location_data[transit_list[i][3]][0]
                    elif transit_list[i][0]:
                        coords1 = self.location_data[transit_list[i][0]][0]
                        coords2 = self.transit_loc
                        transit_list[i][4] = transit_list[i][1] + 30
                    else:
                        coords2 = self.location_data[transit_list[i][3]][0]
                        coords1 = self.transit_loc
                        transit_list[i][1] = transit_list[i][4] - 30
                    x = coords2[1] - coords1[1]
                    y = coords2[0] - coords1[0]
                    ratio = ((self.time-transit_list[i][1])
                             /(transit_list[i][4] - transit_list[i][1]))
                    if ratio < 1 and ratio > 0:
                        x = int(x*ratio + coords1[1])
                        y = int(y*ratio + coords1[0])
                        self.img = cv2.circle(self.img, (x, y),
                                              3, colour, -1)
                        self.coords.append((x,y, transit_list[i][2]))
        update_display_label(self.big_frame, self.img)
    
    def click_event(self, event):
        self.text_disp.destroy()
        self.text = ""
        for key in self.location_data.keys():
            coords = self.location_data[key][0]
            if np.sqrt(pow((event.x - coords[1]),2)
            + pow((event.y - coords[0]),2)) <= 10:
                self.text += key + "\n\n" + self.location_data[key][2] + "\n\n"
                if len(self.locations_list[key]) > 1:
                    self.text += "# inside: " + str(len(self.locations_list[key])-1) + "\n\n"
        if np.sqrt(pow((event.x - self.transit_loc[1]),2)
        + pow((event.y - self.transit_loc[0]),2)) <= 10:
            self.text += "Offsite\n\nThis indicates the location the student goes to when leaving the university, typically to go home.\n\n"
        
        for coords in self.coords:
            if np.sqrt(pow((event.x - coords[0]),2)
            + pow((event.y - coords[1]),2)) <= 3:
                self.text += "ID: " + coords[2] + "\nName: " + self.people_data[coords[2]][0] + "\n"
                self.text += "Age: " + self.people_data[coords[2]][1] + "\n"
                self.text += "Subject/Year: " + self.people_data[coords[2]][4] + " "
                self.text += self.people_data[coords[2]][3] + "\n"
                if self.people_data[coords[2]][7]:
                    self.text += "Societies: " + self.people_data[coords[2]][7][0]
                    for soc in self.people_data[coords[2]][7][1:]:
                        self.text += ", " + soc
                    self.text += "\n"
                if coords[2] in self.tests:
                    self.text += '\n"' + self.tests[coords[2]] + '"\n'
                self.text += "\n"
            
        self.text_disp = tk.Label(self.master, text=self.text,
                                  wraplength = 200)
        self.text_disp.grid(column = 1, row = 0, rowspan = 2)
        
if __name__ == "__main__":
    maps = check_for_root(None, map_viewer)
    print(maps.outliers)