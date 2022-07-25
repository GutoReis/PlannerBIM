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
from pivy import coin
from PySide import QtCore
from PySide.QtGui import QTableWidgetItem
from planProcess import Process
from planner_utils import path, parseDate, parseIsoFormat, add2Date


def makeTask(name='Task'):
    """Create a task based on a given object, and returns the generated task.

    Parameters
    ----------
    name: str, optional
        The name to give to the created task.

    Returns
    -------
    <App::FeaturePython>
        Returns the generated schedule task.

    Notes
    -----
    Creates a new <App::FeaturePython> object, and turns it into a parametric task
    object.
    """
    
    if not FreeCAD.ActiveDocument:
        FreeCAD.Console.PrintError("No active document. Aborting\n")
        return
    
    obj = FreeCAD.ActiveDocument.addObject('App::FeaturePython', name)
    planTask(obj)
    
    if FreeCAD.GuiUp:
        ViewProviderTask(obj.ViewObject)

    FreeCAD.ActiveDocument.recompute()
    return obj

class planTask(Process):
    """The Task object. Is an identifiable unit of work to be carried out in a construction project

    More information here: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_1/FINAL/HTML/link/ifctask.htm

    Parameters
    ----------
    obj: <App::FeaturePython>
        The object to turn into an Schedulle Task
    """  
   
    def __init__(self, obj):
        Process.__init__(self, obj)  
        self.Object = obj
        obj.Proxy = self
        self.setProperties(obj)
        self.setPropertiesValues(obj)

    def setProperties(self, obj):
        """Assign specific properties.
        
        Parameters
        ----------
        obj: <App::FeaturePython>
            The task object.
        """
        
        IfcTaskTypeEnum = ['NOTDEFINED', 'ATTENDANCE', 'CONSTRUCTION', 'DEMOLITION', 'DISMANTLE', 'DISPOSAL', 'INSTALLATION', 'LOGISTIC', 
                          'MAINTENANCE', 'MOVE', 'OPERATION', 'REMOVAL', 'RENOVATION', 'USERDEFINED']
        IfcTaskDurationEnum = ['NOTDEFINED', 'ELAPSEDTIME','WORKTIME']
        
        Process.setProperties(self, obj)
        
        pl = obj.PropertiesList
        
        ######################## IFC properties ################################       
        #schedule data
        if not "Status" in pl:
            obj.addProperty("App::PropertyString","Status", "6-Config", "Current status of the task. Examples: Not Yet Started, Started, Completed")
        if not "IsMilestone" in pl:
            obj.addProperty("App::PropertyBool", "IsMilestone","6-Config", "Identifies whether a task is a milestone task (=TRUE) or not (= FALSE").IsMilestone=False
        if not "Priority" in pl:
            obj.addProperty("App::PropertyInteger", "Priority", "6-Config", "Value indicates the relative priority of the task (in comparison to the priorities of other tasks)")
        if not "PredefinedType" in pl:
            obj.addProperty("App::PropertyEnumeration","PredefinedType", "6-Config", "Predefined types of a task").PredefinedType = IfcTaskTypeEnum
        if not "WorkMethod" in pl:
            obj.addProperty("App::PropertyString", "WorkMethod","6-Config", "Method of work used in carrying out a task")        
        if not "DurationType" in pl:
            obj.addProperty("App::PropertyEnumeration","DurationType", "2-Schedule", "Enables to specify the type of duration values for ScheduleDuration").DurationType = IfcTaskDurationEnum    

        #control data
        if not "StatusTime" in pl:
            obj.addProperty("App::PropertyString","StatusTime", "3-Control", "Date or time at which the status of the tasks within the schedule is analyzed")
        if not "Completion" in pl:
            obj.addProperty("App::PropertyPercent","Completion", "3-Control", "Percentage of task completion")
        if not "RemainingTime" in pl:
            obj.addProperty("App::PropertyInteger","RemainingTime", "3-Control", "Amount of time remaining to complete a task", 1)
        if not "EarlyStart" in pl:
            obj.addProperty("App::PropertyString","EarlyStart", "", "The earliest date on which a task can be started")#, 4)
        if not "EarlyFinish" in pl:
            obj.addProperty("App::PropertyString","EarlyFinish", "", "The earliest date on which a task can be finished")#, 4)
        if not "LateStart" in pl:
            obj.addProperty("App::PropertyString","LateStart", "", "The latest date on which a task can be started")#, 4)
        if not "LateFinish" in pl:
            obj.addProperty("App::PropertyString","LateFinish", "", "The latest date on which a task can be finished")#, 4)
        if not "FreeFloat" in pl:
            obj.addProperty("App::PropertyInteger","FreeFloat", "", "Amount of time during which the start or finish of a task may be varied without any effect on the overall programme of work", 4)
        if not "TotalFloat" in pl:
            obj.addProperty("App::PropertyInteger","TotalFloat", "", "Difference between the duration available to carry out a task and the scheduled duration of the task", 4)
        if not "IsCritical" in pl:
            obj.addProperty("App::PropertyBool","IsCritical", "", "A flag which identifies whether a scheduled task is a critical item within the programme", 4)

        obj.setEditorMode("VisibilitySchedule", 2)
        obj.setEditorMode("VisibilityActual", 2)
        obj.setEditorMode("UnlockedBaseline", 2)

    def setPropertiesValues(self, obj):
        """Called to set parameters in object initialize.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The process object.
        """
        Process.setPropertiesValues(self, obj)

    def onDocumentRestored(self, obj):
        """Method run when the document is restored.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The task object.
        """        
        Process.onDocumentRestored(self,obj)
        self.setProperties(obj)
    
    def onChanged(self, obj, prop):
        """Method called when the object has a property changed.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The task object.
        prop: string
            The name of the property that has changed.
        """       
        if prop == "ActualStart":
            if hasattr(obj,"ActualStart") and hasattr(obj,"EarlyStart"):
                #update EarlyStart property
                obj.EarlyStart = obj.ActualStart

        Process.onChanged(self, obj, prop)

        if prop == "IsMilestone":
            if hasattr(obj,"IsMilestone"):
                #set properties to change task into milestone
                if obj.IsMilestone:
                    obj.ScheduleFinish = obj.ScheduleStart
                    obj.ActualFinish = obj.ActualStart
                    obj.setEditorMode("ScheduleFinish", 1)
                    obj.setEditorMode("ScheduleDuration", 1)
                    obj.setEditorMode("ActualFinish", 1)
                    obj.setEditorMode("ActualDuration", 1)
                else:
                    obj.setEditorMode("ScheduleFinish", 0)
                    obj.setEditorMode("ScheduleDuration", 0)
                    obj.setEditorMode("ActualFinish", 0)
                    obj.setEditorMode("ActualDuration", 0)
        if prop == "Completion":
            if hasattr(obj,"Completion"):
                #remaining time calculation
                obj.RemainingTime = obj.ActualDuration - int(obj.Completion*obj.ActualDuration/100)
        if prop == "StatusTime":
            if hasattr(obj,"StatusTime"):
                dt = parseDate(obj.StatusTime)
                obj.StatusTime = parseIsoFormat(dt)
        if prop == "PlacementActual":
            if hasattr(obj,"PlacementActual"):
                Process.setEdgePoints(self, obj)
        if prop == "Dim2nd":
            if hasattr(obj,"Dim2nd"):
                Process.setEdgePoints(self, obj) 
        if prop == "IsSuccessorFrom":
            if hasattr(obj,"IsSuccessorFrom"):
                #updates the start date from relationships with predecessors
                self._updateStartFromPredecessors(obj)
                Process.setEdgePoints(self, obj)
        if prop == "ActualFinish":   
            if hasattr(obj,"ActualFinish") and hasattr(obj,"EarlyFinish"):
                #update EarlyFinish property
                obj.EarlyFinish = obj.ActualFinish
                
                #clean critical path if task has changed
                if obj.ShowCriticalPath == True:
                    self._triggerToSuperParentCleanCriticalPath(obj)

                #update sucessors, forward propagation
                self._triggerToSucessorsProcess(obj)
                Process.setEdgePoints(self, obj)
        if prop == "ShowCriticalPath":
            if hasattr(obj,"ShowCriticalPath"):
                if obj.ShowCriticalPath == False:
                    self._cleanCriticalPath(obj)
                    #update edge
                    Process.setEdgePoints(self, obj)

    def _updateStartFromPredecessors(self, obj):
        """Called to update to the biggest start date due to the relationship with the predecessors.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The object that has changed.
        """
        if obj.IsSuccessorFrom:
            predecDatesList = []
            for edgName in obj.IsSuccessorFrom:
                edg = FreeCAD.ActiveDocument.getObject(edgName)
                predec = edg.RelatingProcess
                if edg.SequenceType == 'FINISH_START':
                    predFinish = parseDate(predec.ActualFinish)
                    objStart = add2Date(predFinish, edg.intLagValue+1)
                    predecDatesList.append(objStart)
                elif edg.SequenceType == 'FINISH_FINISH':
                    predFinish = parseDate(predec.ActualFinish)
                    objFinish = add2Date(predFinish, edg.intLagValue)
                    objStart = add2Date(objFinish, -obj.ActualDuration+1)
                    predecDatesList.append(objStart)
                elif edg.SequenceType == 'START_START':
                    predStart = parseDate(predec.ActualStart)
                    objStart = add2Date(predStart, edg.intLagValue)
                    predecDatesList.append(objStart)                        
                elif edg.SequenceType == 'START_FINISH':
                    predStart = parseDate(predec.ActualStart)
                    objFinish = add2Date(predStart, edg.intLagValue-1)
                    objStart = add2Date(objFinish, -obj.ActualDuration+1)
                    predecDatesList.append(objStart)  

            obj.ActualStart = parseIsoFormat(max(predecDatesList))

    def updateLateFinishFromSucessors(self, obj):
        """Called to update to the lowest most latest finish date of successors.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The object that has changed.
        """
        try:           
            if obj.IsPredecessorTo:
                sucesDatesList = []
                for edgName in obj.IsPredecessorTo:
                    edg = FreeCAD.ActiveDocument.getObject(edgName)
                    suces = edg.RelatedProcess
                    objActualFinish = parseDate(obj.ActualFinish)
                    objRefFinish = parseDate(obj.RefFinishDate)
                    if objActualFinish == objRefFinish:
                        objLateFinish = objActualFinish
                        sucesDatesList.append(objLateFinish)
                    else:
                        if edg.SequenceType == 'FINISH_START':
                            sucLateStart = parseDate(suces.LateStart)
                            objLateFinish = add2Date(sucLateStart, -edg.intLagValue-1)
                            sucesDatesList.append(objLateFinish)
                        elif edg.SequenceType == 'FINISH_FINISH':
                            sucLateFinish = parseDate(suces.LateFinish)
                            objLateFinish = add2Date(sucLateFinish, -edg.intLagValue)
                            sucesDatesList.append(objLateFinish)
                        elif edg.SequenceType == 'START_START':
                            sucLateStart = parseDate(suces.LateStart)
                            objLateStart = add2Date(sucLateStart, -edg.intLagValue)
                            objLateFinish = add2Date(objLateStart, obj.ActualDuration-1)
                            sucesDatesList.append(objLateFinish)                       
                        elif edg.SequenceType == 'START_FINISH':
                            sucLateFinish = parseDate(suces.LateFinish)
                            objLateStart = add2Date(sucLateFinish, -edg.intLagValue+1)
                            objLateFinish = add2Date(objLateStart, obj.ActualDuration-1)
                            sucesDatesList.append(objLateFinish)
                
                lateFinish = min(sucesDatesList)
            elif obj.IsSuccessorFrom:
                predecDatesList = []
                for edgName in obj.IsSuccessorFrom:
                    edg = FreeCAD.ActiveDocument.getObject(edgName)
                    predecActualFinish = parseDate(edg.RelatingProcess.ActualFinish)
                    objActualFinish = parseDate(obj.ActualFinish)
                    objRefFinish = parseDate(obj.RefFinishDate)
                    if objActualFinish < predecActualFinish and predecActualFinish == objRefFinish:
                        objLateFinish = objActualFinish
                        predecDatesList.append(objLateFinish)
                    else:
                        objLateFinish = objRefFinish
                        predecDatesList.append(objLateFinish)

                lateFinish = min(predecDatesList)
            else:
                lateFinish = parseDate(obj.RefFinishDate)
            
            #clean properties and mark that the activity was considered in the calculation of the critical path
            obj.Proxy._cleanCriticalPath(obj)
            obj.ShowCriticalPath = True
            
            #set date properties later
            lateStart = add2Date(lateFinish, -obj.ActualDuration+1)
            obj.LateStart = parseIsoFormat(lateStart)
            obj.LateFinish = parseIsoFormat(lateFinish)            

            #set free and total float calculations 
            earlyStart = parseDate(obj.EarlyStart)
            obj.FreeFloat, obj.TotalFloat = self._calcFreeAndTotalFloat(lateStart, earlyStart, lateFinish, obj.ActualDuration)
            
            #set critical property
            if obj.FreeFloat <= 0 or obj.TotalFloat <= 0:
                obj.IsCritical = True
            else:
                obj.IsCritical = False

            #update edge
            Process.setEdgePoints(self, obj)
            FreeCAD.ActiveDocument.recompute()
            
            #back propagation
            obj.Proxy._triggerToPredecessorsProcess(obj)
        except:
            pass

    def _cleanCriticalPath(self, obj):
        """Called to clear properties when changing task dates.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The object that has changed.
        """
        try:
            obj.IsCritical = False
            obj.LateStart = obj.LateFinish = ''
            obj.FreeFloat = obj.TotalFloat = 1
        except:
            pass

    def _calcFreeAndTotalFloat(self, lateStart, earlyStart, lateFinish, duration):
        """Called to Free and total float calculations.
        Description in #http://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/link/ifctasktime.htm

        Parameters
        ----------
        lateStart: datetime
        earlyStart: datetime
        lateFinish: datetime
        duration: int
        
        Returns
        -------
        freeFloat: int
        totalFloat: int
        """
        #Free float property calculation
        tf = lateStart - earlyStart
        freeFloat = tf.days
        
        #Total float property calculation 
        durFloat = lateFinish - earlyStart
        durFloat = durFloat.days +1
        totalFloat = durFloat - duration
        
        return freeFloat, totalFloat

    def _triggerToSucessorsProcess(self, obj):
        """Called to trigger the update on the successors. Forward propagation according to PERT/CPM.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The object that has changed.
        """
        if hasattr(obj, 'IsPredecessorTo'):
            if obj.IsPredecessorTo:
                for edgName in obj.IsPredecessorTo:
                    edg = FreeCAD.ActiveDocument.getObject(edgName)
                    suc = edg.RelatedProcess
                    suc.Proxy.onChanged(suc, "IsSuccessorFrom")

    def _triggerToPredecessorsProcess(self, obj):
        """Called to trigger the update on the predecessors. Back propagation according to PERT/CPM.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The object that has changed.
        """        
        if hasattr(obj, 'IsSuccessorFrom'):
            for edgName in obj.IsSuccessorFrom:
                edg = FreeCAD.ActiveDocument.getObject(edgName)
                pred = edg.RelatingProcess
                pred.Proxy.updateLateFinishFromSucessors(pred)

    def _triggerToSuperParentCleanCriticalPath(self, obj):
        """Called to trigger clean critical path in super parent.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The process object.
        """
        try:            
            for parent in obj.InListRecursive:
                if hasattr(parent,"Level") and hasattr(parent,"UpdatePosChildren"):
                    if parent.Level == 0:                        
                        if parent.ShowCriticalPath==True:
                            parent.ShowCriticalPath=False
        except:
            pass 

    def __getstate__(self):
       return None
       
    def __setstate__(self, state):
       return None


class ViewProviderTask:
    """A View Provider for the task object.

    Parameters
    ----------
    vobj: <Gui.ViewProviderDocumentObject>
        The view provider to turn into a task view provider.
    """

    def __init__(self, vobj):
        self.setProperties(vobj)
        vobj.Proxy = self

    def setProperties(self, vobj):
        """Assign specific properties.
        
        Parameters
        ----------
        vobj: <Gui.ViewProviderDocumentObject>
            The component's view provider object.
        """
        #Scheduled part
        vobj.addProperty("App::PropertyColor","LineColorSchedule","1-Schedule","Scheduled part line color").LineColorSchedule=(0.0,0.0,0.0) 
        vobj.addProperty("App::PropertyColor","ShapeColorSchedule","1-Schedule","Scheduled part shape color").ShapeColorSchedule=(0.8,0.8,0.8)
        vobj.addProperty("App::PropertyInteger","TransparencySchedule","1-Schedule","Scheduled part transparency").TransparencySchedule = 60

        #Actual part
        vobj.addProperty("App::PropertyColor","LineColorActual","2-Actual","Actual part line color").LineColorActual=(0.0,0.0,0.0) 
        vobj.addProperty("App::PropertyColor","ShapeColorActual","2-Actual","Actual part shape color").ShapeColorActual=(0.0,0.0,1.0)
        vobj.addProperty("App::PropertyColor","ShapeColorCompletion","2-Actual","Completion part shape color").ShapeColorCompletion=(0.0,0.0,0.0)
        vobj.addProperty("App::PropertyInteger","TransparencyActual","2-Actual","Actual part transparency").TransparencyActual = 60
        vobj.addProperty("App::PropertyInteger","TransparencyCompletion","2-Actual","Completion part transparency")
    
    #tanks to https://forum.freecadweb.org/viewtopic.php?t=11818
    def onDelete(self, vobj, subelements):
        """Custom delete to remove the edges before removing the task object.
        
        Parameters
        ----------
        vobj: <Gui.ViewProviderDocumentObject>
            The component's view provider object. 
        subelements: tuple of strings
         
        Returns
        -------
        bool
            True if the object will be deleted.
        """
        self.removeEdge()
        return True

    #thanks to https://forum.freecadweb.org/viewtopic.php?style=3&f=22&t=12139&start=10
    def doubleClicked(self, vobj):
        """Custom double click for task set edit mode.
        
        Parameters
        ----------
        vobj: <Gui.ViewProviderDocumentObject>
            The component's view provider object.
        """
        doc = FreeCADGui.getDocument(vobj.Object.Document)
        if not doc.getInEdit():
            doc.setEdit(vobj.Object.Name)
        else:
            FreeCAD.Console.PrintError('Active Task Dialog found! Please close this one first!\n')
        return True

    def setEdit(self,vobj, mode=0):
        """Called when the document requests the object to enter edit mode.
        Edit mode is entered when a user double clicks on an object in the tree
        view, or when they use the menu option [Edit -> Toggle Edit Mode].
        Parameters
        ----------
        vobj: <Gui.ViewProviderDocumentObject>
            The component's view provider object.
        mode: int or str
            The edit mode the document has requested. Set to 0 when requested via
            a double click or [Edit -> Toggle Edit Mode].
        Returns
        -------
        bool
            If edit mode was entered.
        """
        if mode == 0:
            relTask = RelationsTaskPanel()
            relTask.obj = self.Object
            relTask.update()
            FreeCADGui.Control.showDialog(relTask)
            return True
        return False
    
    
    def attach(self, vobj):
        self.Object = vobj.Object  #from https://forum.freecadweb.org/viewtopic.php?f=22&t=12139&p=160045&hilit=setedit#p161062       
        
        #draw shapes for scheduled and actual task representation
        self.scale = coin.SoScale()
        style=coin.SoDrawStyle()
        style.lineWidth=2
        style.style = coin.SoDrawStyle.LINES
        
        #schedule node
        self.shapeSchedule = coin.SoCube()
        self.coordsSchedule = coin.SoCoordinate3()
        self.originSchedule = coin.SoTranslation()
        self.translSchedule = coin.SoTranslation()
        self.shapeColorSchedule = coin.SoMaterial()
        self.lineColorSchedule = coin.SoBaseColor()
        
        self.wireSchedule = coin.SoSeparator()
        self.wireSchedule.addChild(style)
        self.wireSchedule.addChild(self.lineColorSchedule)
        self.wireSchedule.addChild(self.shapeSchedule)

        self.shadeSchedule = coin.SoSeparator()
        self.shadeSchedule.addChild(self.shapeColorSchedule)
        self.shadeSchedule.addChild(self.shapeSchedule)
        
        self.scheduleNode = coin.SoSeparator()
        self.scheduleNode.addChild(self.originSchedule)
        self.scheduleNode.addChild(self.coordsSchedule)
        self.scheduleNode.addChild(self.translSchedule)
        self.scheduleNode.addChild(self.wireSchedule)
        self.scheduleNode.addChild(self.shadeSchedule)
        
        self.scheduleSwitch = coin.SoSwitch()
        self.scheduleSwitch.setName('scheduleSwitch')
        self.scheduleSwitch.whichChild = 0
        self.scheduleSwitch.addChild(self.scheduleNode)
        
        #actual node
        self.shapeActual = coin.SoCube()
        self.coordsActual = coin.SoCoordinate3()
        self.originActual = coin.SoTranslation()
        self.translActual = coin.SoTranslation()
        self.shapeColorActual = coin.SoMaterial()
        self.lineColorActual = coin.SoBaseColor()
        
        self.wireActual = coin.SoSeparator()
        self.wireActual.addChild(style)
        self.wireActual.addChild(self.lineColorActual)
        self.wireActual.addChild(self.shapeActual)

        self.shadeActual = coin.SoSeparator()
        self.shadeActual.addChild(self.shapeColorActual)
        self.shadeActual.addChild(self.shapeActual)
   
        self.actualNode = coin.SoSeparator()
        self.actualNode.addChild(self.originActual)
        self.actualNode.addChild(self.coordsActual)
        self.actualNode.addChild(self.translActual)
        self.actualNode.addChild(self.wireActual)
        self.actualNode.addChild(self.shadeActual)
        
        self.actualSwitch = coin.SoSwitch()
        self.actualSwitch.setName('actualSwitch')
        self.actualSwitch.whichChild = 0
        self.actualSwitch.addChild(self.actualNode)
        
        #completion node
        self.shapeCompletion = coin.SoCube()
        self.shapeColorCompletion = coin.SoMaterial()       
        self.originCompletion = coin.SoTranslation()
        self.translCompletion = coin.SoTranslation()
        self.coordsCompletion = coin.SoCoordinate3()

        self.shadeCompletion = coin.SoSeparator()
        self.shadeCompletion.addChild(self.shapeColorCompletion)
        self.shadeCompletion.addChild(self.shapeCompletion)

        self.completionNode = coin.SoSeparator()
        self.completionNode.addChild(self.originCompletion)
        self.completionNode.addChild(self.coordsCompletion)
        self.completionNode.addChild(self.translCompletion)
        self.completionNode.addChild(self.shadeCompletion)
        
        self.completionSwitch = coin.SoSwitch()
        self.completionSwitch.setName('completionSwitch')
        self.completionSwitch.whichChild = 0
        self.completionSwitch.addChild(self.completionNode)

        #root node
        self.rootNode = coin.SoGroup()
        self.rootNode.addChild(self.scale)
        self.rootNode.addChild(self.scheduleSwitch)
        self.rootNode.addChild(self.actualSwitch)
        self.rootNode.addChild(self.completionSwitch)
        vobj.addDisplayMode(self.rootNode,"Flatlines")
        
        #to update properties
        self.onChanged(vobj,"ShapeColorSchedule")
        self.onChanged(vobj,"LineColorSchedule")
        self.onChanged(vobj,"TransparencySchedule")
        self.onChanged(vobj,"ShapeColorActual")
        self.onChanged(vobj,"LineColorActual")
        self.onChanged(vobj,"TransparencyActual")
        self.onChanged(vobj,"ShapeColorCompletion")
        self.onChanged(vobj,"TransparencyCompletion")

    def updateData(self, obj, prop):
        """Method called when the task object has a property changed.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The object that has changed.
        prop: string
            The name of the property that has changed.
        """  
        
        #schedule part properties
        if prop == "Placement":
            if hasattr(obj,"Placement"):
                p = obj.Placement.Base
                self.translSchedule.translation=(p.x,p.y,p.z)
        if prop == "ScheduleDuration":
            if hasattr(obj,"ScheduleDuration"):
                self.shapeSchedule.width = float(obj.ScheduleDuration)
                self._updateOriginSchedule()
        if prop == "VisibilitySchedule":
            if hasattr(obj,"VisibilitySchedule"):
                if obj.VisibilitySchedule:
                    self.scheduleSwitch.whichChild = 0
                else:
                    self.scheduleSwitch.whichChild = -1

        #actual part properties    
        if prop == "PlacementActual":
            if hasattr(obj,"PlacementActual"):
                p = obj.PlacementActual.Base
                self.translActual.translation=(p.x,p.y,p.z)
                self.translCompletion.translation=(p.x,p.y,p.z)
        if prop == "ActualDuration":
            if hasattr(obj,"ActualDuration"):
                self.shapeActual.width = float(obj.ActualDuration)
                self.updateData(obj, "Completion")
                self._updateOriginActual()
        if prop == "Completion":
            if hasattr(obj,"Completion"):               
                self.shapeCompletion.width = int(obj.Completion*obj.ActualDuration/100)
                self._updateOriginActual()
        if prop == "VisibilityActual":
            if hasattr(obj,"VisibilityActual"):
                if obj.VisibilityActual:
                    self.actualSwitch.whichChild = 0
                    self.completionSwitch.whichChild = 0
                else:
                    self.actualSwitch.whichChild = -1
                    self.completionSwitch.whichChild = -1
        
        #general properties
        if prop == "Dim2nd":
            if hasattr(obj,"Dim2nd"):
                self.shapeSchedule.height = obj.Dim2nd
                self.shapeActual.height = obj.Dim2nd
                self.shapeCompletion.height = obj.Dim2nd/2.0
                self._updateOriginSchedule()
                self._updateOriginActual()
        if prop == "Dim3rd":
            if hasattr(obj,"Dim3rd"):
                self.shapeSchedule.depth = obj.Dim3rd
                self.shapeActual.depth = obj.Dim3rd
                self.shapeCompletion.depth = obj.Dim3rd
                self._updateOriginSchedule()
                self._updateOriginActual()
        if prop == "IsMilestone":
            vobj = obj.ViewObject
            if hasattr(obj,"IsMilestone") and hasattr(vobj,"ShapeColorSchedule") and hasattr(vobj,"ShapeColorActual"):
                if obj.IsMilestone:
                    vobj.ShapeColorSchedule = (1.0,0.0,0.0)
                    vobj.ShapeColorActual = (1.0,0.0,0.0)
                else:
                    vobj.ShapeColorSchedule = (0.8,0.8,0.8)
                    vobj.ShapeColorActual = (0.0,0.0,1.0)
        if prop == "IsCritical":
            vobj = obj.ViewObject
            if hasattr(obj,"IsCritical")and hasattr(vobj,"LineColorSchedule") and hasattr(vobj,"LineColorActual"):
                if obj.IsCritical:
                    vobj.LineColorSchedule=(1.0,0.0,0.0)
                    vobj.LineColorActual=(1.0,0.0,0.0)
                else:
                    vobj.LineColorSchedule=(0.0,0.0,0.0)
                    vobj.LineColorActual=(0.0,0.0,0.0)   

    def _updateOriginSchedule(self):
        """Called to translate the shape representation of the schedule task to the original position.
        """
        self.originSchedule.translation = (self.shapeSchedule.width.getValue()/2.0, 
                      self.shapeSchedule.height.getValue()/2.0,
                      self.shapeSchedule.depth.getValue()/2.0)

    def _updateOriginActual(self):
        """Called to translate the shape representation of the actual task to the original position.
        """
        self.originActual.translation = (self.shapeActual.width.getValue()/2.0, 
                      self.shapeActual.height.getValue()/2.0,
                      self.shapeActual.depth.getValue()/2.0)
        self.originCompletion.translation = (self.shapeCompletion.width.getValue()/2.0, 
                      self.shapeCompletion.height.getValue()/2.0,
                      self.shapeCompletion.depth.getValue()/2.0)

    def onChanged(self,vp, prop):
        #schedule part properties
        if prop == "ShapeColorSchedule":
            if hasattr(vp,"ShapeColorSchedule"):
                c = vp.ShapeColorSchedule
                self.shapeColorSchedule.diffuseColor = (c[0], c[1], c[2])
        if prop == "LineColorSchedule":
            if hasattr(vp,"LineColorSchedule"):
                c = vp.LineColorSchedule
                self.lineColorSchedule.rgb.setValue(c[0],c[1],c[2])
        if prop == "TransparencySchedule":
            if hasattr(vp,"TransparencySchedule"):
                t = float(vp.TransparencySchedule/100)
                self.shapeColorSchedule.transparency.setValue(t)
        #actual part properties     
        if prop == "ShapeColorActual":
            if hasattr(vp,"ShapeColorActual"):
                c = vp.ShapeColorActual
                self.shapeColorActual.diffuseColor = (c[0], c[1], c[2])
        if prop == "LineColorActual":
            if hasattr(vp,"LineColorActual"):
                c = vp.LineColorActual
                self.lineColorActual.rgb.setValue(c[0],c[1],c[2]) 
        if prop == "TransparencyActual":
            if hasattr(vp,"TransparencyActual"):
                t = float(vp.TransparencyActual/100)
                self.shapeColorActual.transparency.setValue(t)
        #completion part properties    
        if prop == "ShapeColorCompletion":
            if hasattr(vp,"ShapeColorCompletion"):
                c = vp.ShapeColorCompletion
                self.shapeColorCompletion.diffuseColor = (c[0], c[1], c[2])
        if prop == "TransparencyCompletion":
            if hasattr(vp,"TransparencyCompletion"): 
                t = float(vp.TransparencyCompletion/100)
                self.shapeColorCompletion.transparency.setValue(t)

    def removeEdge(self):
        """Called to delete the relationship edges between the task and the successors/predecessors.
        """
        listPredecessors = self.Object.IsSuccessorFrom
        listSucessors = self.Object.IsPredecessorTo
        #update list of edges in predecesors and delete it
        for edgeName in listPredecessors:
            edge = FreeCAD.ActiveDocument.getObject(edgeName)
            list_pred = edge.RelatingProcess.IsPredecessorTo
            list_pred.remove(edge.Name)
            edge.RelatingProcess.IsPredecessorTo = list_pred
            FreeCAD.ActiveDocument.removeObject(edgeName)
        #update list of edges in sucessors and delete it
        for edgeName in listSucessors:
            edge = FreeCAD.ActiveDocument.getObject(edgeName)
            list_suc = edge.RelatedProcess.IsSuccessorFrom
            list_suc.remove(edge.Name)
            edge.RelatedProcess.IsSuccessorFrom = list_suc
            FreeCAD.ActiveDocument.removeObject(edgeName)

    def getDisplayModes(self,obj):
        modes=[]
        modes.append("Flatlines")
        return modes

    def getDefaultDisplayMode(self):
        return "Flatlines"

    def setDisplayMode(self,mode):
        return mode

    def getIcon(self):
        return path()+"/icons/task_icon.svg"  

    def __getstate__(self):
       return None
       
    def __setstate__(self, state):
       return None


class RelationsTaskPanel:
    """The task pane that sets up relations for the schedule task.
    """

    def __init__(self):        
        self.obj = None
        header = ['edg_name', 'Item', 'Long Description', 'Lag Value', 'Sequence Type', 'Duration Type']
        
        self.form = FreeCADGui.PySideUic.loadUi(path()+"/ui/dialogTask.ui")
        self.form.tab_predec.setHorizontalHeaderLabels(header)
        self.form.tab_predec.setColumnHidden(0, True)
        self.form.tab_sucess.setHorizontalHeaderLabels(header)
        self.form.tab_sucess.setColumnHidden(0, True)
        self.form.toolBox.setCurrentIndex(1)
        
        QtCore.QObject.connect(self.form.btn_add, QtCore.SIGNAL("clicked()"), self.addPredecessor)
        QtCore.QObject.connect(self.form.btn_edit, QtCore.SIGNAL("clicked()"), self.editPredecessor)
        QtCore.QObject.connect(self.form.btn_del, QtCore.SIGNAL("clicked()"), self.removePredecessor)


    def update(self):
        """Update form with task data.
        """
        self.form.lin_identification.setText(self.obj.Identification)
        self.form.txt_description.setPlainText(self.obj.LongDescription)
        self.searchPredecessorEdges()
        self.searchSucessorEdges()
        FreeCADGui.Selection.clearSelection()
        #FreeCADGui.ExpressionBinding(self.form.lin_identification.text()).bind(self.obj,"Identification")

    def searchPredecessorEdges(self):
        """Called for search predecessor and fill dialog in task pane.
        """
        for edgeName in self.obj.IsSuccessorFrom:
            paramEdge=[]
            edge = FreeCAD.ActiveDocument.getObject(edgeName)
            paramEdge.extend([edge.Name, edge.RelatingProcess.Identification, edge.RelatingProcess.LongDescription, 
                            edge.LagValue,edge.SequenceType, edge.DurationType])
            self.insertPredecessorInTaskPanel(paramEdge)

    def searchSucessorEdges(self):
        """Called for search sucessor and fill dialog in task pane.
        """
        for edgeName in self.obj.IsPredecessorTo:
            paramEdge=[]
            edge = FreeCAD.ActiveDocument.getObject(edgeName)
            paramEdge.extend([edge.Name, edge.RelatedProcess.Identification, edge.RelatedProcess.LongDescription, 
                            edge.LagValue,edge.SequenceType, edge.DurationType])
            self.insertSucessorInTaskPanel(paramEdge)

    def insertPredecessorInTaskPanel(self, paramEdge):
        """Called for insert predecessor relation in task pane.
        Parameters
        ----------
        paramEdge: List
            The list of edge data.
        """
        if paramEdge:
            rowPosition = self.form.tab_predec.rowCount()
            self.form.tab_predec.insertRow(rowPosition)
            for idx, i in enumerate(paramEdge):
                item = QTableWidgetItem(i)
                self.form.tab_predec.setItem(rowPosition, idx, item)

    def insertSucessorInTaskPanel(self, paramEdge):
        """Called for insert sucessor relation in task pane.
        Parameters
        ----------
        paramEdge: List
            The list of edge data.
        """
        if paramEdge:
            rowPosition = self.form.tab_sucess.rowCount()
            self.form.tab_sucess.insertRow(rowPosition)
            for idx, i in enumerate(paramEdge):
                item = QTableWidgetItem(i)
                self.form.tab_sucess.setItem(rowPosition, idx, item)

    def addPredecessor(self):
        """Called to create relationship of the task and its predecessor, and insert it in the task pane.
        """
        from planEdge import makeEdge
        
        try:
            predecObj = FreeCADGui.Selection.getSelection()[0]
        except:
            FreeCAD.Console.PrintError("Select a predecessor task fisrt \n")
            return

        item = predecObj.Identification
        descr = predecObj.LongDescription
        paramEdge= []
        
        #open dialog to config relation
        dialog = RelationConfigDialog().form
        dialog.lbl_predec_Identif.setText(item)
        dialog.lbl_predec_Descrip.setText(descr)
        
        result = dialog.exec_()
        if result:
            lag = dialog.lin_lag.text()
            if lag == "" or lag == None:
                lag = "0"
            seq  = dialog.cmb_sequence.currentText()
            dur = dialog.cmb_duration.currentText()
           
            #create FC object edge
            edge = makeEdge(predecObj, self.obj, lag, dur, seq)

            paramEdge.extend([edge.Name, item, descr, lag, seq, dur])
            
            #append edge in properties in predecessor and sucessor
            list_suc = self.obj.IsSuccessorFrom
            list_pred = predecObj.IsPredecessorTo
            list_suc.append(edge.Name)
            list_pred.append(edge.Name)
            self.obj.IsSuccessorFrom = list_suc
            predecObj.IsPredecessorTo = list_pred

            
            self.insertPredecessorInTaskPanel(paramEdge)
    
    def editPredecessor(self):
        """Called to edit relationship of the task and its predecessor.
        """
        try:
            rowselected = self.form.tab_predec.currentRow()
        except:
            FreeCAD.Console.PrintError("Select row fisrt \n")
        
        edgeName = self.form.tab_predec.item(rowselected, 0).text()
        #select edge object
        edge = FreeCAD.ActiveDocument.getObject(edgeName)
        
        predecObj = edge.RelatingProcess
        item = predecObj.Identification
        descr = predecObj.LongDescription
        
        #open dialog to reconfig relation and set data
        dialog = RelationConfigDialog().form
        dialog.lbl_predec_Identif.setText(item)
        dialog.lbl_predec_Descrip.setText(descr)
        dialog.lin_lag.setText(edge.LagValue)
        
        #update of the fields with edge data
        #thanks to https://stackoverflow.com/questions/22797794/pyqt-how-to-set-combobox-to-item-knowing-items-text-a-title/22798753
        index = dialog.cmb_sequence.findText(edge.SequenceType, QtCore.Qt.MatchFixedString)
        if index >= 0:
            dialog.cmb_sequence.setCurrentIndex(index)
        
        index = dialog.cmb_duration.findText(edge.DurationType, QtCore.Qt.MatchFixedString)
        if index >= 0:
            dialog.cmb_duration.setCurrentIndex(index)
        
        result = dialog.exec_()
        if result:
            edge.LagValue = dialog.lin_lag.text()
            edge.SequenceType  = dialog.cmb_sequence.currentText()
            edge.DurationType = dialog.cmb_duration.currentText()
            
            self.form.tab_predec.item(rowselected, 3).setText(edge.LagValue)
            self.form.tab_predec.item(rowselected, 4).setText(edge.SequenceType)
            self.form.tab_predec.item(rowselected, 5).setText(edge.DurationType)
        
        #calls onChange to update the edge    #and the critical path
        self.obj.Proxy.onChanged(self.obj, 'IsSuccessorFrom')
        #self.obj.Proxy.onChanged(self.obj, 'IsPredecessorTo')
    
    def removePredecessor(self):
        """Called to remove relationship of the task and its predecessor.
        """
        #select row
        rowselected = self.form.tab_predec.currentRow()
        edgeName = self.form.tab_predec.item(rowselected, 0).text()
        #select edge object
        edge = FreeCAD.ActiveDocument.getObject(edgeName)
        #update relationship lists
        list_suc = self.obj.IsSuccessorFrom
        list_pred = edge.RelatingProcess.IsPredecessorTo
        list_suc.remove(edge.Name)
        list_pred.remove(edge.Name)
        self.obj.IsSuccessorFrom = list_suc
        edge.RelatingProcess.IsPredecessorTo = list_pred
        
        #update critical path
        #self.obj.Proxy.updateLateFinishFromSucessors(self.obj)
        
        #delete table row and FC object
        FreeCAD.ActiveDocument.removeObject(edgeName)
        self.form.tab_predec.removeRow(rowselected)
  
    def accept(self):
        self.obj.Identification = self.form.lin_identification.text()
        self.obj.LongDescription = self.form.txt_description.toPlainText()
        FreeCADGui.Selection.clearSelection()
        FreeCADGui.Control.closeDialog()
        FreeCADGui.ActiveDocument.resetEdit()
        FreeCAD.ActiveDocument.recompute()
        return True

    def reject(self):
        FreeCADGui.Selection.clearSelection()
        FreeCADGui.Control.closeDialog()
        FreeCADGui.ActiveDocument.resetEdit()
        FreeCAD.ActiveDocument.recompute()
        return True

class RelationConfigDialog:
    """Interface for relationship configuration.
    """

    def __init__(self):
        self.predec = None      
        self.form = FreeCADGui.PySideUic.loadUi(path()+"/ui/dialogRelationConfig.ui")
        self.form.cmb_sequence.addItems(['FINISH_START', 'FINISH_FINISH','START_START', 'START_FINISH'])
        self.form.cmb_duration.addItems(['WORKTIME', 'ELAPSEDTIME','NOTDEFINED'])
