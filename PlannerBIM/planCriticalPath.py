# -*- coding: utf-8 -*-

# ***************************************************************************
# *   Copyright (c) 2022 Henrique Reis https://www.linkedin.com/in/pedrohrl/*
# *   and Gustavo Reis https://github.com/GutoReis                          *
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


class CriticalPath():
    def __init__(self):
        self.schedule = None
        self.showCriticalPath()

    def showCriticalPath(self):
        """Called to select the schedule and start CPM.
        """
        try:
            #select schedule
            obj = FreeCADGui.Selection.getSelection()[0]
            if hasattr(obj,"Level") and hasattr(obj,"UpdatePosChildren"):
                if obj.Level == 0:
                    self.schedule = obj
                    #mark that the schedule was considered in the calculation of the critical path
                    self.schedule.ShowCriticalPath = True
            
            self._selectTasksWithoutSucessors()
            self._initBackPropagation()
        except:
            FreeCAD.Console.PrintError('Select Schedule first!\n')

    def _selectTasksWithoutSucessors(self):
        """Called to select tasks that have no successors.
        """
        self.listTasksToInitBackPropagation = []
        for obj in self.schedule.OutListRecursive:
            if hasattr(obj,"EarlyFinish"):
                if not obj.IsPredecessorTo:
                    self.listTasksToInitBackPropagation.append(obj)

    def _initBackPropagation(self):
        """Called to start backward propagation from tasks that have no successors.
        """
        for obj in self.listTasksToInitBackPropagation:       
            #get lowest most latest finish date of successors, calculate free and total float and set critical property
            obj.Proxy.updateLateFinishFromSucessors(obj)


    
    
    
