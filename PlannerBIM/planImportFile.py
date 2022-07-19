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

import FreeCAD
import PySide
from PySide import QtGui, QtCore
from PySide.QtGui import *
from PySide.QtCore import *

from planSchedule import PlanSchedule, ViewProviderSchedule
from planTask import planTask, ViewProviderTask
from planTaskTitle import PlanTaskTitle, ViewProviderTaskTitle


def import_xml_file() -> None:
    """To import a XML File from ProjectLibre to autogenerate the objects."""
    if not FreeCAD.ActiveDocument:
        return FreeCAD.Console.PrintError("No active document.")

    path = FreeCAD.ConfigGet("UserAppData")
    file_name = ""
    file_name, _ = PySide.QtGui.QFileDialog. \
        getOpenFileName(None,"Import XML File",path,"XML Files (*.xml)")
    print(file_name)
    print("Creating Objects")
    
    schedule_obj = create_schedule()
    title_obj = create_task_title()
    task_1 = create_task()
    task_2 = create_task()
    print("Schedule Created")
    
    print("Relating Objects")
    title_obj.adjustRelativeLinks(schedule_obj)
    schedule_obj.addObject(title_obj)
    task_1.adjustRelativeLinks(title_obj)
    title_obj.addObject(task_1)
    task_2.adjustRelativeLinks(title_obj)
    title_obj.addObject(task_2)
    FreeCAD.ActiveDocument.recompute()
    print("Objects related")

    print("Customizing Data for objects")
    task_1.ScheduleFinish = "2022-07-22T00:00:00"
    task_2.ScheduleStart = "2022-07-23T00:00:00"
    task_2.ScheduleFinish = "2022-07-25T00:00:00"
    FreeCAD.ActiveDocument.recompute()
    print("Objects Ready")
    


def create_schedule():
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "Schedule")
    PlanSchedule(obj)

    if FreeCAD.GuiUp:
        ViewProviderSchedule(obj.ViewObject)
    
    FreeCAD.ActiveDocument.recompute()
    return obj


def create_task_title():
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "task-title")
    PlanTaskTitle(obj)

    if FreeCAD.GuiUp:
        ViewProviderTaskTitle(obj.ViewObject)
    
    FreeCAD.ActiveDocument.recompute()
    return obj


def create_task():
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", "Task")
    planTask(obj)

    if FreeCAD.GuiUp:
        ViewProviderTask(obj.ViewObject)
    
    FreeCAD.ActiveDocument.recompute()
    return obj