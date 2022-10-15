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
        
        self.people_data = time_.read_csv("Data/people_data.csv",0)
        self.people_data = time_.prep_people_data(self.people_data)
        self.societies = time_.get_soc_connection_ids(self.people_data)
        
        self.radius = 10
        self.size = 1000
        self.colour = (0,255,0)
        self.coords = [[(0,0),(255,255,255)]]
        self.generate_coords()
        self.selected = 0
        
        self.update_image()
        update_display_label(self.big_frame, self.base_image)
    
    def generate_coords(self):
        self.keys = [key for key in self.people_data.keys()]
        for i in range(len(self.keys)):
            colour = self.people_data[self.keys[i]][0][6][1:]
            colour = (int(colour[:2], base=16),int(colour[2:4], base=16),
                      int(colour[4:6], base=16))
            
            rows = 13
            x = (900//rows+2)*((i%rows)+1)
            y = (600//rows+2)*((i//rows)+1)
            self.coords.append([(x,y), colour])
    
    def add_base_connections(self):
        for soc in self.societies.keys():
            for i in range(len(self.societies[soc])):
                
    
    def update_image(self):
        image = np.ones((720,1000,3), dtype="uint8")
        self.base_image = image*255
        
        self.add_base_connections()
        
        for coord in self.coords[:self.selected]+self.coords[self.selected+1:]:
            self.base_image = cv2.circle(self.base_image, coord[0], self.radius,
                                         coord[1], -1)
        
    def click_event(self, event):
        success = False
        for i in range(1, len(self.coords)):
            if np.sqrt(pow((event.x - self.coords[i][0][0]),2)
            + pow((event.y - self.coords[i][0][1]),2)) <= self.radius:
                self.selected = i
                success = True
                break
        if not success:
            self.selected = 0
        self.update_image()
    
    def motion_event(self, event):
        if self.selected:
            self.coords[self.selected][0] = (event.x, event.y)
            image = self.base_image.copy()
            image = cv2.circle(image, self.coords[self.selected][0],
                                    self.radius, self.coords[self.selected][1], -1)
            update_display_label(self.big_frame, image)
        

if __name__ == "__main__":
    check_for_root(None, network_builder)