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
from utils import parseDate
import time
import Draft

class SimulationTransparency():
    def __init__(self):
        self.schedule = None
        self.frameRate = 0.2
        self.initSimulation()

    def initSimulation(self):
        """Called to select the schedule and start simulation.
        """
        try:
            obj = FreeCADGui.Selection.getSelection()[0]
            if hasattr(obj,"Level") and hasattr(obj,"UpdatePosChildren"):
                if obj.Level == 0:
                    self.schedule = obj
            
            self.setListDays()
            self.hideObjects()
            self.simulation()
        except:
            FreeCAD.Console.PrintError('Select Schedule first!\n')
 
    def setListDays(self):
        """Called to set the list of project days.
        """
        tmpListDays = self.schedule.Proxy.setListOfDays(self.schedule)
        self.listDays = [parseDate(t[4]) for t in tmpListDays]
    
    def createRectangleDisplay(self):
        """Called to create the temporary rectangle that indicates the active day.
        """       
        y = self.schedule.Proxy.getChildrendHeight(self.schedule)
        self.rectangle = Draft.makeRectangle(1, y, placement=self.schedule.Placement)
        self.rectangle.ViewObject.Transparency = 80
        self.rectangle.ViewObject.LineColor = (1.00,1.00,1.00)
        FreeCAD.ActiveDocument.recompute()

    def moveRectangleDisplay(self, x):
        """Called to move the rectangle that indicates the active day.
        Parameters
        ----------
        x: int
            Distance to the origin to position the reference rectangle.
        """
        self.rectangle.Placement.Base.x = x
    
    def removeRectangleDisplay(self):
        """Called to delete the rectangle that indicates the active day.
        """
        FreeCAD.ActiveDocument.removeObject(self.rectangle.Name)
        FreeCAD.ActiveDocument.recompute()
  
    def simulation(self):
        """Called to create simulation.
        """
        self.createRectangleDisplay()
        time.sleep(1)
        for num, dt in enumerate(self.listDays):
            time.sleep(self.frameRate)
            self.moveRectangleDisplay(num)
            self.changeVisibilit(dt)
            FreeCAD.Console.PrintMessage("Date = %s \n" %dt)
        self.removeRectangleDisplay()
        FreeCADGui.Selection.clearSelection()
    
    def hideObjects(self):
        """Called to hide all objects at the beginning of the simulation.
        """
        for task in self.schedule.OutListRecursive:
            if hasattr(task,"Completion"):
                for obj in task.OperatesOn:
                    obj.ViewObject.Visibility = False
   
    def changeVisibilit(self, dt):
        """Called to change in the transparency of the object simulating the evolution 
        of the project according to the date.
        
        Parameters
        ----------
        dt: datetime
            Day chosen for the simulation.
        """        
        for task in self.schedule.OutListRecursive:
            if hasattr(task,"Completion"):
                st = parseDate(task.ScheduleStart)
                fn = parseDate(task.ScheduleFinish)
                dur = task.ScheduleDuration
                if st<=dt and dt<=fn:
                    for obj in task.OperatesOn:
                        transp = self.calcPercentConclTask(dt, st, fn, dur)
                        obj.ViewObject.Transparency = transp
                        obj.ViewObject.Visibility = True

        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.updateGui() 

    def calcPercentConclTask(self, dat, start,  finish,  duration):
        """Called to calculation of the percentage of completion of the task for use in 
        the visualization of the Simulation.
        
        Parameters
        ----------
        dat: datetime
            Day chosen for the simulation.
        start: datetime
            Start date of the task.
        finish: datetime
            Finish date of the task.
        duration: int
            Duration of the task.
        
        Returns
        -------
        percentConclTask: int
            Percentage of task completion.
        """  
        try:
            if dat < start:
                percentConclTask = 100
            elif dat >= finish:
                percentConclTask = 0
            else:
                concl = dat-start
                concl= concl.days
                percentConclTask = int((1-(float(concl) / duration))*100)
            return percentConclTask
        except:
            percentConclTask = 100
            return percentConclTask
