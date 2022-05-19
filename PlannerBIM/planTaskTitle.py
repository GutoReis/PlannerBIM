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
import pivy.coin as coin
from planProcess import Process
from utils import path


def makeTaskTitle(name = 'Title/Sub-title'):
    """Creates title or sub-title for itemization and hierarchy of 
    project tasks.

    Parameters
    ----------
    name: str, optional
        The label for the schedule.

    Returns
    -------
    <App::FeaturePython>
        The created title or sub-title for itemization.

    Notes
    -----
    Creates a new <App::FeaturePython> object and transforms it into a parametric
    itemization / hierarchy object
    """
    
    if not FreeCAD.ActiveDocument:
        return FreeCAD.Console.PrintError("No active document. Aborting\n")

    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", name)
    PlanTaskTitle(obj)
    
    if FreeCAD.GuiUp:
        ViewProviderTaskTitle(obj.ViewObject)

    FreeCAD.ActiveDocument.recompute()    
    return obj
    

class PlanTaskTitle(Process):
    """The title/sub-title object.

    Parameters
    ----------
    obj: <App::FeaturePython>
        The object to turn into an title/sub-title
    """  
    
    def __init__(self, obj):
        Process.__init__(self, obj)
        self.Object = obj
        obj.Proxy = self
        self.setProperties(obj)

    def setProperties(self, obj):
        """Assign specific properties.
        
        Parameters
        ----------
        obj: <App::FeaturePython>
            The title/sub-title object.
        """
        
        Process.setProperties(self, obj)

        if not hasattr(obj,"Group"):
            obj.addExtension("App::GroupExtensionPython", self)
        
        #hide properties
        obj.setEditorMode("ScheduleStart", 2)
        obj.setEditorMode("ScheduleFinish", 2)
        obj.setEditorMode("ScheduleDuration", 2)
        obj.setEditorMode("ActualStart", 2)
        obj.setEditorMode("ActualFinish", 2)
        obj.setEditorMode("ActualDuration", 2)
        obj.setEditorMode("Dim2nd", 2)
        obj.setEditorMode("Dim3rd", 2)
        obj.setEditorMode("VisibilitySchedule", 2)
        obj.setEditorMode("VisibilityActual", 2)
        obj.setEditorMode("UnlockedBaseline", 2)
        obj.setEditorMode("IsSuccessorFrom", 2)
        obj.setEditorMode("IsPredecessorTo", 2)
        obj.setEditorMode("OperatesOn", 2)

    def onDocumentRestored(self, obj):
        """Method run when the document is restored.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The title/sub-title object.
        """
        Process.onDocumentRestored(self, obj)
        self.setProperties(obj)

    def onChanged(self, obj, prop):
        """Method called when the object has a property changed.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The title/sub-title object.
        prop: string
            The name of the property that has changed.
        """
        
        Process.onChanged(self, obj, prop)

    def __getstate__(self):
       return None
       
    def __setstate__(self, state):
       return None


class ViewProviderTaskTitle:
    """A View Provider for the title/sub-title object.

    Parameters
    ----------
    vobj: <Gui.ViewProviderDocumentObject>
        The view provider to turn into a title/sub-title view provider.
    """

    def __init__(self,vobj):
        self.setProperties(vobj)
        vobj.Proxy = self

    def setProperties(self, vobj):
        """Assign specific properties.
        
        Parameters
        ----------
        vobj: <Gui.ViewProviderDocumentObject>
            The component's view provider object.
        """
        vobj.addExtension("Gui::ViewProviderGroupExtensionPython", self)
        
        #Scheduled part
        vobj.addProperty("App::PropertyColor","LineColorSchedule","1-Schedule","Scheduled part line color").LineColorSchedule=(0.0,0.0,0.0) 
        vobj.addProperty("App::PropertyColor","ShapeColorSchedule","1-Schedule","Scheduled part shape color").ShapeColorSchedule=(0.4,0.4,0.4)
        vobj.addProperty("App::PropertyInteger","TransparencySchedule","1-Schedule","Scheduled part transparency").TransparencySchedule = 50

        #Actual part
        vobj.addProperty("App::PropertyColor","LineColorActual","2-Actual","Actual part line color").LineColorActual=(0.0,0.0,0.0) 
        vobj.addProperty("App::PropertyColor","ShapeColorActual","2-Actual","Actual part shape color").ShapeColorActual=(0.05,0.5,0.65)
        vobj.addProperty("App::PropertyInteger","TransparencyActual","2-Actual","Actual part transparency").TransparencyActual = 50

    def attach(self, vobj):
        """ Adds display of the Gantt bar to the currency scenario graph.
        
        Parameters
        ----------
        vobj: <Gui.ViewProviderDocumentObject>
            The view provider object.
        """        
        self.Object = vobj.Object  #from https://forum.freecadweb.org/viewtopic.php?f=22&t=12139&p=160045&hilit=setedit#p161062 
        
        self.bar = self.ganttBarTitleView()
        
        vobj.addDisplayMode(self.bar,"Flatlines")
        
        #to update properties
        self.onChanged(vobj,"ShapeColorSchedule")
        self.onChanged(vobj,"LineColorSchedule")
        self.onChanged(vobj,"TransparencySchedule")
        self.onChanged(vobj,"ShapeColorActual")
        self.onChanged(vobj,"LineColorActual")
        self.onChanged(vobj,"TransparencyActual")

    def ganttBarTitleView(self):
        #draw shapes for scheduled and actual title/subtitle representation
        style=coin.SoDrawStyle()
        style.lineWidth=2
        style.style = coin.SoDrawStyle.LINES
        self.scale = coin.SoScale()
        
        #schedule node
        self.boxSchedule = coin.SoCube()
        self.boxSchedule.height = 0.5
        self.boxSchedule.depth = 0.0
        self.cone1Schedule = coin.SoCone()
        self.cone1Schedule.bottomRadius = 0.5
        self.cone1Schedule.height = 0.5
        self.cone2Schedule = coin.SoCone()
        self.cone2Schedule.bottomRadius = 0.5
        self.cone2Schedule.height = 0.5

        self.coordsSchedule = coin.SoCoordinate3()
        self.originSchedule = coin.SoTranslation()
        self.translSchedule = coin.SoTranslation()
        self.shapeColorSchedule = coin.SoMaterial()
        self.translCone1Schedule = coin.SoTranslation()
        self.translCone1Schedule.translation = (self.cone1Schedule.bottomRadius.getValue(), 
                                        self.cone1Schedule.height.getValue()*1.5, 
                                        self.cone1Schedule.bottomRadius.getValue())
        self.translCone2Schedule = coin.SoTranslation()
        self.lineColorSchedule = coin.SoBaseColor()
        
        self.conesSchedule = coin.SoSeparator()
        self.conesSchedule.addChild(self.translCone1Schedule)
        self.conesSchedule.addChild(self.cone1Schedule)
        self.conesSchedule.addChild(self.translCone2Schedule)
        self.conesSchedule.addChild(self.cone2Schedule)
        
        self.wireSchedule = coin.SoSeparator()
        self.wireSchedule.addChild(style)
        self.wireSchedule.addChild(self.lineColorSchedule)
        self.wireSchedule.addChild(self.conesSchedule)
        self.wireSchedule.addChild(self.originSchedule)
        self.wireSchedule.addChild(self.boxSchedule)
        
        self.shadeSchedule = coin.SoSeparator()
        self.shadeSchedule.addChild(self.shapeColorSchedule)
        self.shadeSchedule.addChild(self.conesSchedule)
        self.shadeSchedule.addChild(self.originSchedule)
        self.shadeSchedule.addChild(self.boxSchedule)

        self.scheduleNode = coin.SoSeparator()
        self.scheduleNode.addChild(self.coordsSchedule)
        self.scheduleNode.addChild(self.translSchedule)
        self.scheduleNode.addChild(self.wireSchedule)
        self.scheduleNode.addChild(self.shadeSchedule)
        
        self.scheduleSwitch = coin.SoSwitch()
        self.scheduleSwitch.setName('scheduleSwitch')
        self.scheduleSwitch.whichChild = 0
        self.scheduleSwitch.addChild(self.scheduleNode)

        #actual node
        self.boxActual = coin.SoCube()
        self.boxActual.height = 0.5
        self.boxActual.depth = 0.0
        self.cone1Actual = coin.SoCone()
        self.cone1Actual.bottomRadius = 0.5
        self.cone1Actual.height = -0.5
        self.cone2Actual = coin.SoCone()
        self.cone2Actual.bottomRadius = 0.5
        self.cone2Actual.height = -0.5

        self.coordsActual = coin.SoCoordinate3()
        self.originActual = coin.SoTranslation()
        self.translActual = coin.SoTranslation()
        self.shapeColorActual = coin.SoMaterial()
        self.translCone1Actual = coin.SoTranslation()
        self.translCone1Actual.translation = (self.cone1Actual.bottomRadius.getValue(), 
                                            -self.cone1Actual.height.getValue()/2, 
                                            self.cone1Actual.bottomRadius.getValue())
        self.translCone2Actual = coin.SoTranslation()
        self.lineColorActual = coin.SoBaseColor()
        
        self.conesActual = coin.SoSeparator()
        self.conesActual.addChild(self.translCone1Actual)
        self.conesActual.addChild(self.cone1Actual)
        self.conesActual.addChild(self.translCone2Actual)
        self.conesActual.addChild(self.cone2Actual)
        
        self.wireActual = coin.SoSeparator()
        self.wireActual.addChild(style)
        self.wireActual.addChild(self.lineColorActual)
        self.wireActual.addChild(self.conesActual)
        self.wireActual.addChild(self.originActual)
        self.wireActual.addChild(self.boxActual)
        
        self.shadeActual = coin.SoSeparator()
        self.shadeActual.addChild(self.shapeColorActual)
        self.shadeActual.addChild(self.conesActual)
        self.shadeActual.addChild(self.originActual)
        self.shadeActual.addChild(self.boxActual)

        self.actualNode = coin.SoSeparator()
        self.actualNode.addChild(self.coordsActual)
        self.actualNode.addChild(self.translActual)
        self.actualNode.addChild(self.wireActual)
        self.actualNode.addChild(self.shadeActual)
        
        self.actualSwitch = coin.SoSwitch()
        self.actualSwitch.setName('actualSwitch')
        self.actualSwitch.whichChild = 0
        self.actualSwitch.addChild(self.actualNode)
        
        #root node
        self.rootNode = coin.SoGroup()
        self.rootNode.addChild(self.scale)
        self.rootNode.addChild(self.scheduleSwitch)
        self.rootNode.addChild(self.actualSwitch)
        
        return self.rootNode

    def updateData(self, obj, prop):
        """Method called when the title object has a property changed.

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
                orig = float(obj.ScheduleDuration)
                self.boxSchedule.width = orig
                self.originSchedule.translation = (orig/2.0, 
                                                self.boxSchedule.height.getValue()/2.0,
                                                self.boxSchedule.depth.getValue()/2.0)
                self.translCone2Schedule.translation = (orig-(2*self.cone1Schedule.bottomRadius.getValue()), 0.0, 0.0)
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
        if prop == "ActualDuration":
            if hasattr(obj,"ActualDuration"):
                orig = float(obj.ActualDuration)
                self.boxActual.width = orig
                self.originActual.translation = (orig/2.0, 
                                                self.boxActual.height.getValue()/2.0+self.boxActual.height.getValue(),
                                                self.boxActual.depth.getValue()/2.0)
                self.translCone2Actual.translation = (orig-(2*self.cone1Actual.bottomRadius.getValue()), 0.0, 0.0)
        if prop == "VisibilityActual":
            if hasattr(obj,"VisibilityActual"):
                if obj.VisibilityActual:
                    self.actualSwitch.whichChild = 0
                else:
                    self.actualSwitch.whichChild = -1

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
    
    def getDisplayModes(self,obj):
        modes=[]
        modes.append("Flatlines")
        return modes

    def getDefaultDisplayMode(self):
        return "Flatlines"

    def setDisplayMode(self,mode):
        return mode

    def getIcon(self):
        return path()+"/icons/title_icon.svg"

    def __getstate__(self):
       return None
       
    def __setstate__(self, state):
       return None
