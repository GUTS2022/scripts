# -*- coding: utf-8 -*-
"""
Created on Sat Oct 15 12:38:26 2022

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

class network_builder:
    def __init__(self, master):
        self.master = master
        self.master.geometry('1000x720')
        self.big_frame = tk.Label(self.master, image=[])
        self.big_frame.grid()
        self.big_frame.bind('<Button-1>', self.click_event)
        self.big_frame.bind('<B1-Motion>', self.motion_event)
        self.big_frame.bind('<Button-1>', self.click_event)
        self.big_frame.bind('<ButtonRelease-1>', self.release_event)
        
        self.people_data = time_.read_csv("Data/people_data.csv",0)
        self.people_data = time_.prep_people_data(self.people_data)
        self.societies = time_.get_soc_connection_ids(self.people_data)
        self.subjects = time_.get_connection_ids(self.people_data, 4)
        
        self.radius = 10
        self.size = 1000
        self.colour = (0,255,0)
        self.coords = {"base": [(0,0),(255,255,255)]}
        self.generate_coords()
        self.selected_id = "base"
        
        self.update_image()
        update_display_label(self.big_frame, self.base_image)
    
    def generate_coords(self):
        keys = [key for key in self.people_data.keys()]
        angle = 0
        radius = 300
        rows = 13
        rad = 2*np.pi/len(keys)
        for i in range(len(keys)):
            colour = self.people_data[keys[i]][6]
            
            x = int(500 + radius*np.sin(angle))
            y = int(360 + radius*np.cos(angle))
            self.coords.update({keys[i]: [(x,y), colour]})
            angle += rad
        
        keys = [key for key in self.societies.keys()]
        for i in range(len(keys)):
            soc = keys[i]
            x = ((i//4)+1) * 100
            y = ((i%4)+1) * 100
            
            self.coords.update({soc: [(x,y), (255,0,0)]})
        
        keys = [key for key in self.subjects.keys()]
        for i in range(len(keys)):
            soc = keys[i]
            x = ((i//4)+1) * 120
            y = ((i%4)+1) * 120
            
            self.coords.update({soc: [(x,y), (0,0,255)]})
    
    def add_base_connections(self):
        num = 0
        keys = [key for key in self.societies.keys()]
        for i in range(len(keys)):
            soc = keys[i]
            if soc != self.selected_id:
                for j in range(len(self.societies[soc])):
                    if self.societies[soc][j] != self.selected_id:
                            self.base_image = cv2.line(self.base_image,
                                                       self.coords[self.societies[soc][j]][0],
                                                       self.coords[soc][0],
                                                       (255, 128, 0), 1)
                            num += 1
        keys = [key for key in self.subjects.keys()]
        for i in range(len(keys)):
            soc = keys[i]
            if soc != self.selected_id:
                for j in range(len(self.subjects[soc])):
                    if self.subjects[soc][j] != self.selected_id:
                            self.base_image = cv2.line(self.base_image,
                                                       self.coords[self.subjects[soc][j]][0],
                                                       self.coords[soc][0],
                                                       (0, 200, 255), 1)
                            num += 1
        print(num)
                    
    
    def update_image(self):
        image = np.ones((720,1000,3), dtype="uint8")
        self.base_image = image*255
        
        self.add_base_connections()
        
        for key in self.coords.keys():
            if not (key == self.selected_id or key == "base"):
                coord = self.coords[key]
                self.base_image = cv2.circle(self.base_image, coord[0], self.radius,
                                             coord[1], -1)
        
    def click_event(self, event):
        success = False
        for key in self.coords.keys():
            if key != "base":
                if np.sqrt(pow((event.x - self.coords[key][0][0]),2)
                + pow((event.y - self.coords[key][0][1]),2)) <= self.radius:
                    self.selected_id = key
                    success = True
                    break
        if not success:
            self.selected_id = "base"
        self.update_image()
    
    def motion_event(self, event):
        if self.selected_id != "base":
            self.coords[self.selected_id][0] = (event.x, event.y)
            image = self.base_image.copy()
            image = cv2.circle(image, self.coords[self.selected_id][0],
                               self.radius, self.coords[self.selected_id][1], -1)
            update_display_label(self.big_frame, image)
    
    def release_event(self, event):
        self.selected_id = "base"
        self.update_image()
        update_display_label(self.big_frame, self.base_image)
        

if __name__ == "__main__":
    check_for_root(None, network_builder)