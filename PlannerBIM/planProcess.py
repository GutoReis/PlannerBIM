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
from planner_utils import SetTaskDates, parseDate, parseIsoFormat

class Process:
    """The Schedule Component object.

    Acts as a base for all other Planner objects. Implementation of ifcProcess made up in IFC4.
   
    More information here: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_1/FINAL/HTML/link/ifcprocess.htm

    Parameters
    ----------
    obj: <App::FeaturePython>
        The object to turn into an Planner Component
    """ 

    def __init__(self, obj):
        self.tskSch = SetTaskDates()
        self.tskAct = SetTaskDates()
        self.Object = obj
        obj.Proxy = self
        self.Type = "Process"
        self.setProperties(obj)
        self.setPropertiesValues(obj)

    def setProperties(self, obj):
        """Assign specific properties.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The process object.
        """  

        pl = obj.PropertiesList
        
        ######################## IFC properties ################################
        if not "Identification" in pl:
            obj.addProperty("App::PropertyString","Identification","1-Identification", "Identifier at the occurrence level to a process or activit")
        if not "LongDescription" in pl:
            obj.addProperty("App::PropertyString","LongDescription","1-Identification", "An extended description or narrative that may be provided")
        #schedule data
        if not "ScheduleStart" in pl:
            obj.addProperty("App::PropertyString","ScheduleStart", "2-Schedule", "Date on which a task is scheduled to be started")
        if not "ScheduleFinish" in pl:
            obj.addProperty("App::PropertyString","ScheduleFinish", "2-Schedule", "Date on which a task is scheduled to be finished")
        if not "ScheduleDuration" in pl:
            obj.addProperty("App::PropertyInteger","ScheduleDuration", "2-Schedule", "Amount of time which is scheduled for completion of a task")
        #control data
        if not "ActualStart" in pl:
            obj.addProperty("App::PropertyString","ActualStart", "3-Control", "Date on which a task is actually started")
        if not "ActualFinish" in pl:
            obj.addProperty("App::PropertyString","ActualFinish", "3-Control", "Date on which a task is actually finished")
        if not "ActualDuration" in pl:
            obj.addProperty("App::PropertyInteger","ActualDuration", "3-Control", "Actual duration of the task")
        
        #relations data
        if not "IsSuccessorFrom" in pl:
            obj.addProperty("App::PropertyStringList", "IsSuccessorFrom", "5-Relations", "Dependency between two activities, it refers to the previous activity for which this activity is the successor", 1)
        if not "IsPredecessorTo" in pl:
            obj.addProperty("App::PropertyStringList", "IsPredecessorTo", "5-Relations", "Dependency between two activities, it refers to the subsequent activity for which this activity is the predecessor", 1)
        if not "OperatesOn" in pl:
            obj.addProperty("App::PropertyLinkListGlobal", "OperatesOn", "5-Relations", "Set of relationships to other objects, e.g. products, processes, controls, resources or actors, that are operated on by the process")
        
        ######################## Internal properties ################################
        if not "Placement" in pl:
            obj.addProperty("App::PropertyPlacement","Placement", "Base", "Scheduled task position", 4)
        if not "PlacementActual" in pl:
            obj.addProperty("App::PropertyPlacement","PlacementActual", "Base", "Actual task position", 4)
        if not "Dim2nd" in pl:
            obj.addProperty("App::PropertyInteger","Dim2nd", "4-ExtraDimension", "Extra second dimension to apply to the task")
        if not "Dim3rd" in pl:
            obj.addProperty("App::PropertyInteger","Dim3rd", "4-ExtraDimension", "Extra third dimension to apply to the task")
        if not "RefStartDate" in pl:
            obj.addProperty("App::PropertyString", "RefStartDate", "", "Reference date to calculate task positions", 4)
        if not "RefFinishDate" in pl:
            obj.addProperty("App::PropertyString", "RefFinishDate", "", "Reference date to calculate Latest Finish in PERT/CPM network")#, 4)
        if not "StartPoint" in pl:
            obj.addProperty("App::PropertyVector", "StartPoint", "", "Edge/relationship start point", 4)
        if not "EndPoint" in pl:
            obj.addProperty("App::PropertyVector", "EndPoint", "", "Edge/relationship end point", 4)      
        if not "VisibilitySchedule" in pl:
            obj.addProperty("App::PropertyBool","VisibilitySchedule", "7-Visibility", "Property to control the visibility of the scheduled portion")
        if not "VisibilityActual" in pl:
            obj.addProperty("App::PropertyBool","VisibilityActual", "7-Visibility", "Property to control the visibility of the actual portion")
        if not "UnlockedBaseline" in pl:
            obj.addProperty("App::PropertyBool","UnlockedBaseline", "7-Visibility", "Property to enable/disable editing of the scheduled portion")
        if not "ShowCriticalPath" in pl:
            obj.addProperty("App::PropertyBool","ShowCriticalPath", "", "Use to clean critical path", 4)
   
    def setPropertiesValues(self, obj):
        """Called to set parameters in object initialize.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The process object.
        """
        obj.RefFinishDate = obj.RefStartDate = self.tskAct.referenceStartDate = self.tskSch.referenceStartDate
        obj.ScheduleStart = self.tskSch.start
        obj.ScheduleFinish = self.tskSch.finish     
        obj.ScheduleDuration = self.tskSch.duration
        obj.ActualStart = self.tskAct.start
        obj.ActualFinish = self.tskAct.finish
        obj.ActualDuration = self.tskAct.duration
        obj.VisibilitySchedule = True
        obj.VisibilityActual = False
        obj.UnlockedBaseline = True
        obj.ShowCriticalPath = False
        obj.Dim3rd = 1
        obj.Dim2nd = 1

    def onDocumentRestored(self, obj):
        """Method run when the document is restored.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The process object.
        """
        try:
            self.tskSch = SetTaskDates()
            self.tskAct = SetTaskDates()
            self.tskAct.referenceStartDate = self.tskSch.referenceStartDate = obj.RefStartDate            
            self.tskSch.start = obj.ScheduleStart
            self.tskSch.finish = obj.ScheduleFinish
            self.tskAct.start = obj.ActualStart
            self.tskAct.finish = obj.ActualFinish
            self.setProperties(obj)
        except:
            pass

    def onChanged(self, obj, prop):
        """Method called when the object has a property changed.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The process object.
        prop: string
            The name of the property that has changed.
        """
        if prop == "Label":
            if hasattr(obj,"Label"):
                obj.Identification = obj.Label
        if prop == "Identification":
            if hasattr(obj,"Identification"):
                obj.Label = obj.Identification
        if prop == "ScheduleStart":
            if hasattr(obj,"ScheduleStart") and hasattr(obj,"ScheduleFinish")and hasattr(obj,"ScheduleDuration"):
                self._updateStart(obj, 'Sch')
                self._updateParentStart(obj, 'Sch')
        if prop == "ScheduleFinish":
            if hasattr(obj,"ScheduleStart") and hasattr(obj,"ScheduleFinish")and hasattr(obj,"ScheduleDuration"):
                self._updateFinish(obj, 'Sch')
                self._updateParentFinish(obj, 'Sch')
        if prop == "ScheduleDuration":
            if hasattr(obj,"ScheduleStart") and hasattr(obj,"ScheduleFinish")and hasattr(obj,"ScheduleDuration"):
                self._updateDuration(obj, 'Sch')
        if prop == "ActualStart":
            if hasattr(obj,"ActualStart") and hasattr(obj,"ActualFinish")and hasattr(obj,"ActualDuration"):
                self._updateStart(obj, 'Act')
                self._updateParentStart(obj, 'Act')
        if prop == "ActualFinish":
            if hasattr(obj,"ActualStart") and hasattr(obj,"ActualFinish")and hasattr(obj,"ActualDuration"):
                self._updateFinish(obj, 'Act')
                self._updateParentFinish(obj, 'Act')
        if prop == "ActualDuration":
            if hasattr(obj,"ActualStart") and hasattr(obj,"ActualFinish")and hasattr(obj,"ActualDuration"):
                self._updateDuration(obj, 'Act')
        if prop == "Dim2nd":
            if hasattr(obj,"Dim2nd"):
                self._updateChildPositionY(obj)
        if prop == "RefStartDate":
            if hasattr(obj,"RefStartDate"):
                self._updateReferencialStartDate(obj)
        if prop == "RefFinishDate":
            if hasattr(obj,"RefFinishDate"):
                self._updateReferencialFinishDate(obj)
        if prop=='Group':
            if hasattr(obj,"Group"):
                self._updateGroup(obj)
        if prop=="UnlockedBaseline":
            if hasattr(obj,"UnlockedBaseline"):
                self._updateUnlockedBaseline(obj)

    def _updateStart(self, obj, txt):
        """Called to recalculate the start date and its reference position.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The process object.
        """
        #steps:
        #transforms typed string value into standardized datetime
        #if the baseline has not been created, the schedule and actual dates remain the same
        #update finish date
        try:
            if txt == 'Sch':
                self.tskSch.start = obj.ScheduleStart
                obj.ScheduleStart = self.tskSch.start
                obj.Placement.Base.x = self.tskSch.posX
            
                if hasattr(obj,"UnlockedBaseline"):
                    if obj.UnlockedBaseline:
                        if obj.ActualStart != obj.ScheduleStart:
                            obj.ActualStart = obj.ScheduleStart
    
                obj.ScheduleFinish = self.tskSch.finish
            elif txt== 'Act':
                self.tskAct.start = obj.ActualStart
                obj.ActualStart = self.tskAct.start
                obj.PlacementActual.Base.x = self.tskAct.posX
                
                if hasattr(obj,"UnlockedBaseline"):
                    if obj.UnlockedBaseline:
                        if obj.ScheduleStart != obj.ActualStart:
                            obj.ScheduleStart = obj.ActualStart
                
                obj.ActualFinish = self.tskAct.finish 
        except:
            pass
    
    def _updateParentStart(self, obj, txt):
        """Called to recalculate the parent start date.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The process object.
        """
        try:        
            parent = obj.InList[0]
            if txt == 'Sch':
                l = [parseDate(child.ScheduleStart) for child in parent.OutList]
                parent.ScheduleStart = parseIsoFormat(min(l))
                #FIXME:
                #updates the parent's finish date, because typing PropertyString causes a bug in the 
                #'drawing' at the end of the Gantt bar. Test whether you can remove this piece of 
                #code when there is a PropertyDateTime in the future
                self._updateParentFinish(obj, 'Sch')
            elif txt== 'Act':
                l = [parseDate(child.ActualStart) for child in parent.OutList]
                parent.ActualStart = parseIsoFormat(min(l))
                #FIXME:
                #updates the parent's finish date, because typing PropertyString causes a bug in the 
                #'drawing' at the end of the Gantt bar. Test whether you can remove this piece of 
                #code when there is a PropertyDateTime in the futur
                self._updateParentFinish(obj, 'Act')
        except:
            pass

    def _updateFinish(self, obj, txt):
        """Called to recalculate finish date and duration.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The process object.
        """
        #steps:
        #transforms typed string value into standardized datetime
        #if the baseline has not been created, the schedule and actual dates remain the same
        #update duration  
        try:
            if txt == 'Sch':              
                self.tskSch.finish = obj.ScheduleFinish
                obj.ScheduleFinish = self.tskSch.finish

                if hasattr(obj,"UnlockedBaseline"):
                    if obj.UnlockedBaseline:
                        if obj.ActualFinish != obj.ScheduleFinish:
                            obj.ActualFinish = obj.ScheduleFinish

                obj.ScheduleDuration = self.tskSch.duration

            elif txt== 'Act':
                self.tskAct.finish = obj.ActualFinish
                obj.ActualFinish = self.tskAct.finish

                if hasattr(obj,"UnlockedBaseline"):
                    if obj.UnlockedBaseline:
                        if obj.ScheduleFinish != obj.ActualFinish:
                            obj.ScheduleFinish = obj.ActualFinish

                obj.ActualDuration = self.tskAct.duration
        except:
            pass
   
    def _updateParentFinish(self, obj, txt):
        """Called to recalculate the parent finish date.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The process object.
        """
        try:
            parent = obj.InList[0]
            if txt == 'Sch':
                l = [parseDate(child.ScheduleFinish) for child in parent.OutList]
                parent.ScheduleFinish = parseIsoFormat(max(l))
            elif txt== 'Act':
                l = [parseDate(child.ActualFinish) for child in parent.OutList]
                parent.ActualFinish = parseIsoFormat(max(l))
        except:
            pass

    def _updateDuration(self, obj, txt):
        """Called to recalculate the time duration.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The process object.
        """
        try:
            if txt == 'Sch':
                if obj.ScheduleDuration <= 0:
                    obj.ScheduleDuration = 1
                self.tskSch.duration = obj.ScheduleDuration
                obj.ScheduleFinish = self.tskSch.finish
            elif txt== 'Act':
                if obj.ActualDuration <= 0:
                    obj.ActualDuration = 1
                self.tskAct.duration = obj.ActualDuration
                obj.ActualFinish = self.tskAct.finish
        except:
            pass
    
    def _updateReferencialStartDate(self, obj):
        """Called to recalculate the referencial start date. To use in positioning the gantt bar.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The process object.
        """
        try:
            self.tskAct.referenceStartDate = self.tskSch.referenceStartDate = obj.RefStartDate
            obj.Placement.Base.x = self.tskSch.posX
            obj.PlacementActual.Base.x = self.tskAct.posX
  
            if hasattr(obj,"Group"):
                for child in obj.OutList:
                    child.RefStartDate = obj.RefStartDate
        except:
            pass

    def _updateReferencialFinishDate(self, obj):
        """Called to update the referencial finish date. To use in PERT/CPM network calculations.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The process object.
        """
        try:
            if hasattr(obj,"Group"):
                for child in obj.OutList:
                    child.RefFinishDate = obj.RefFinishDate
        except:
            pass

    def _updateGroup(self, obj):
        """Called to update reference dates and position of children.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The process object.
        """
        try:
            #update reference dates in children
            for child in obj.OutList:
                child.RefStartDate = obj.RefStartDate
                child.RefFinishDate = obj.RefFinishDate
            
            #update property for change position in children           
            if hasattr(obj,"UpdatePosChildren"):
                obj.UpdatePosChildren=True
            else:
                #update super parent property
                self._updateChildPositionY(obj)
        except:
            pass  

    def _updateUnlockedBaseline(self, obj):
        """Called to update actual shape visibility, if baseline exist.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The process object.
        """
        try:
            if hasattr(obj,"VisibilityActual"):
                if obj.UnlockedBaseline:
                    obj.VisibilityActual = False
                else:
                    obj.VisibilityActual = True
        except:
            pass

    def _updateChildPositionY(self, obj):
        """Called to update child positions in y direction.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The process object.
        """
        try:            
            for parent in obj.InListRecursive:
                if hasattr(parent,"Level") and hasattr(parent,"UpdatePosChildren"):
                    if parent.Level == 0:
                        parent.UpdatePosChildren=True
        except:
            pass 

    def setEdgePoints(self, obj):
        """Called to recalculate the start and end points.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The process object.
        """      
        try:
            z = 0.0
            x1 = obj.PlacementActual.Base.x
            x2 = x1+obj.ActualDuration
            y = obj.PlacementActual.Base.y+(obj.Dim2nd/2)

            obj.StartPoint = FreeCAD.Vector(x1, y, z)
            obj.EndPoint = FreeCAD.Vector(x2, y, z)
            
            self.updateEdges(obj)
        except:
            pass

    def updateEdges(self, obj):
        """Called to fire the edge update trigger.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The process object.
        """
        try:
            if obj.IsPredecessorTo:
                for sucName in obj.IsPredecessorTo:
                    suc = FreeCAD.ActiveDocument.getObject(sucName)
                    suc.UpdateEdg = True
    
            if obj.IsSuccessorFrom:
                for predName in obj.IsSuccessorFrom:
                    pred = FreeCAD.ActiveDocument.getObject(predName)
                    pred.UpdateEdg = True
        except:
            pass

    def __getstate__(self):
       return None
       
    def __setstate__(self, state):
       return None
