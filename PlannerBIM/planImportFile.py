# -*- coding: utf-8 -*-

# ***************************************************************************
# *   Copyright (c) 2020 Walmir Paiva eng.walmir@gmail.com                  *   
# *                                                                         *
# *   This file is part of the FreeCAD development system.                  *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   FreeCAD is distributed in the hope that it will be useful,            *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Lesser General Public License for more details.                   *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with FreeCAD; if not, write to the Free Software        *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************/
from xml.etree import ElementTree as ET

import FreeCAD
import PySide
from PySide import QtGui, QtCore
from PySide.QtGui import *
from PySide.QtCore import *

from planEdge import makeEdge
from planSchedule import PlanSchedule, ViewProviderSchedule
from planTask import planTask, ViewProviderTask
from planTaskTitle import PlanTaskTitle, ViewProviderTaskTitle
from xmlItem import XmlItem


def import_xml_file() -> None:
    """To import a XML File from ProjectLibre to autogenerate the objects."""
    FreeCAD.newDocument("schedule")

    path = FreeCAD.ConfigGet("UserAppData")
    filename = ""
    filename, _ = PySide.QtGui.QFileDialog. \
        getOpenFileName(None,"Import XML File",path,"XML Files (*.xml)")
    print(filename)

    print("Reading file...")
    items_list = read_xml_file(filename)
    print("File read, proceeding to objects creation...")
    try:
        create_3d_objects(items_list)
        print("Successfully created all objects")
    except Exception as err:
        print("Error:", err)
    

def read_xml_file(filename: str) -> list:
    xml_file = ET.parse(filename)
    root_element = xml_file.getroot()
    prefix = "{http://schemas.microsoft.com/project}"
    items_list = [] #list of items in "Tasks" tag parsed to XmlItem

    # Getting Tasks tag
    tasks_list = root_element.find(prefix+"Tasks")

    # Generating list of XmlItem's
    for task in tasks_list:
        task_uid = task.find(prefix+"UID").text
        task_name = task.find(prefix+"Name").text
        task_summary = task.find(prefix+"Summary").text
        task_start = task.find(prefix+"Start").text
        task_finish = task.find(prefix+"Finish").text
        task_outline = task.find(prefix+"OutlineNumber").text
        task_predecessor_link = task.find(prefix+"PredecessorLink") # Used to check if there is a predecessor

        if task_predecessor_link:
            task_predecessor_id = task_predecessor_link \
                .find(prefix+"PredecessorUID").text
        else:
            task_predecessor_id = None
        
        xml_item = XmlItem(item_id=task_uid,
                           name=task_name,
                           start_time=task_start,
                           finish_time=task_finish,
                           summary=task_summary,
                           outline_number=task_outline,
                           predecessor_id=task_predecessor_id)
        items_list.append(xml_item)
    
    return items_list


def create_3d_objects(items_list: list) -> None:
    """create_3d_objects Create all 3D objects from items extracted from XML.

    As the items came in order from file 
    Schedule -> Title 1 -> Task 1 -> Task 2 -> Title 2 -> Task 3 -> Task 4...

    We can be based on this order to create the tree in Freecad.

    Args:
        items_list (list): _description_
    """
    # NOTE:This dict will hold 3d task objects created to make the relations between tasks
    task_obj_dict = dict()
    # NOTE: This will hold 3d Schedule objects, will be erased whenever there is a new schedule
    schedule_obj = None
    # NOTE: This will hold 3d Title objects, will be erased whenever there is a new title
    title_obj = None 

    for item in items_list:
        if item.item_type == "SCHEDULE":
            schedule_obj = create_schedule(item.name)
            FreeCAD.ActiveDocument.recompute() # Always recompute after object is added
        elif item.item_type == "TITLE":
            title_obj = create_task_title(item.name)
            title_obj.adjustRelativeLinks(schedule_obj)
            schedule_obj.addObject(title_obj)
            FreeCAD.ActiveDocument.recompute()
        else: # It is a type TASK
            task_obj = create_task(item.name)
            task_obj.adjustRelativeLinks(title_obj)
            title_obj.addObject(task_obj)
            FreeCAD.ActiveDocument.recompute()
            task_obj_dict[item.item_id] = task_obj
            # Must set relation before dates
            if item.predecessor_id:
                create_relation(
                    predecessor_obj=task_obj_dict[item.predecessor_id],
                    successor_obj=task_obj)
                FreeCAD.ActiveDocument.recompute()
            # Setting dates
            task_obj.ScheduleStart = item.start_time
            task_obj.ScheduleFinish = item.finish_time
            FreeCAD.ActiveDocument.recompute()            


def create_schedule(name):
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", name)
    PlanSchedule(obj)

    if FreeCAD.GuiUp:
        ViewProviderSchedule(obj.ViewObject)
    
    FreeCAD.ActiveDocument.recompute()
    return obj


def create_task_title(name):
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", name)
    PlanTaskTitle(obj)

    if FreeCAD.GuiUp:
        ViewProviderTaskTitle(obj.ViewObject)
    
    FreeCAD.ActiveDocument.recompute()
    return obj


def create_task(name):
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", name)
    planTask(obj)

    if FreeCAD.GuiUp:
        ViewProviderTask(obj.ViewObject)
    
    FreeCAD.ActiveDocument.recompute()
    return obj


def create_relation(predecessor_obj, successor_obj):
    item = predecessor_obj.Identification
    descr = predecessor_obj.LongDescription
    param_edge = []
    lag = "Task Relation"
    seq = "FINISH_START"
    dur = "WORKTIME"

    edge = makeEdge(predecObj=predecessor_obj,
                    sucessObj=successor_obj,
                    txtLagValue=lag,
                    txtDurationType=dur,
                    txtSequenceType=seq)
    param_edge.extend([edge.Name, item, descr, lag, seq, dur])

    # append edge in properties in predecessor and successor
    list_suc = successor_obj.IsSuccessorFrom
    list_pred = predecessor_obj.IsPredecessorTo
    list_suc.append(edge.Name)
    list_pred.append(edge.Name)
    successor_obj.IsSuccessorFrom = list_suc
    predecessor_obj.IsPredecessorTo = list_pred
