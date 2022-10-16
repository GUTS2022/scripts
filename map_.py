# -*- coding: utf-8 -*-
"""
Created on Sat Oct 15 22:40:35 2022

@author: hbarr
"""

import time_

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
        self.master.geometry('1280x800')
        self.big_frame = tk.Label(self.master, image=[])
        self.big_frame.grid()
        
        self.time = 900        
        self.timer = tk.Scale(self.master, from_=0, to=1500,
                              length=1000,
                              orient=tk.HORIZONTAL,
                              tickinterval=60,
                              command=self.update_time)
        self.timer.set(self.time)
        self.timer.grid()
        
        #self.big_frame.bind('<Button-1>', self.click_event)
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
            update_display_label(self.big_frame, self.img)
    
    def update_time(self, time):
        self.time = int(time)
        self.time = ((self.time//60)*100) + (self.time%60) + 300
        self.locations_list = time_.locations(self.time, self.location_data,
                                              self.security_data)
        self.place_buildings()
        self.place_students()
    
    def place_students(self):
        keys = [key for key in self.location_data.keys()]
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
        update_display_label(self.big_frame, self.img)
                    
        
if __name__ == "__main__":
    maps = check_for_root(None, map_viewer)
    print(maps.outliers)