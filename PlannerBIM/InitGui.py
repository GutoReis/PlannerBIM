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

"""Initialization of the BIM Planner workbench"""


class PlannerBIM(Workbench):
    from utils import path
    
    MenuText = "Planner BIM"
    ToolTip = "Workbench for BIM 4D"
    Icon =  path()+"/icons/schdl_icon.svg"

    def Initialize(self):
        import planner
        self.list = ["CreateSchedule",  "CreateTaskTitle", "CreateTask", "CreateCriticalPath","CreateAnimation", "ImportSchedule"]
        self.appendToolbar("PlannerBIM",self.list)
        self.appendMenu("PlannerBIM",self.list)

    def Activated(self):
        FreeCADGui.activeDocument().activeView().viewTop()
        return

    def Deactivated(self):
        return

    def ContextMenu(self, recipient):
        self.appendContextMenu("PlannerBIM", self.list)

    def GetClassName(self): 
        return "Gui::PythonWorkbench"

Gui.addWorkbench(PlannerBIM())





