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
import FreeCADGui
from utils import path
import planTask, planSchedule, planTaskTitle, planCriticalPath, planSimulation #, planImportSchedule


class CmdCreateSchedule:
    def GetResources(self):
        return {'Pixmap'  : path()+"/icons/schdl_icon.svg", 
                'MenuText': "Create project schedule",
                'ToolTip': "Create project schedule"}

    def IsActive(self):
        return True

    def Activated(self):
        planSchedule.makeSchedule()


class CmdCreateTaskTitle:
    def GetResources(self):
        return {'Pixmap'  : path()+"/icons/title_icon.svg", 
                'MenuText': "Create task title",
                'ToolTip': "Create task title"}

    def IsActive(self):
        return True

    def Activated(self):
        planTaskTitle.makeTaskTitle()


class CmdCreateTask:
    def GetResources(self):
        return {'Pixmap'  : path()+"/icons/task_icon.svg", 
                'MenuText': "Create task",
                'ToolTip': "Create task"}

    def IsActive(self):
        return True

    def Activated(self):
        planTask.makeTask()

class CmdCreateCriticalPath:
    def GetResources(self):
        return {'Pixmap'  : path()+"/icons/crit_path_icon.svg", 
                'MenuText': "Show critical path",
                'ToolTip': "Show critical path"}

    def IsActive(self):
        return True

    def Activated(self):
        planCriticalPath.CriticalPath()

class CmdCreateAnimation:
    def GetResources(self):
        return {'Pixmap'  : path()+"/icons/animation_icon.svg", 
                'MenuText': "Create animation",
                'ToolTip': "Create animation"}

    def IsActive(self):
        return True

    def Activated(self):
        planSimulation.SimulationTransparency()


class CmdImportSchedule:
    def GetResources(self):
        return {'Pixmap'  : path()+"/icons/import_xlm.svg", 
                'MenuText': "Import schedule from xlm",
                'ToolTip': "Import schedule from xlm"}

    def IsActive(self):
        return True

    def Activated(self):
        pass


if FreeCAD.GuiUp:
    FreeCADGui.addCommand("CreateSchedule",CmdCreateSchedule())
    FreeCADGui.addCommand("CreateTaskTitle",CmdCreateTaskTitle())
    FreeCADGui.addCommand("CreateTask",CmdCreateTask())
    FreeCADGui.addCommand("CreateCriticalPath",CmdCreateCriticalPath())
    FreeCADGui.addCommand("CreateAnimation",CmdCreateAnimation())
    FreeCADGui.addCommand("ImportSchedule",CmdImportSchedule())
    
    
    
