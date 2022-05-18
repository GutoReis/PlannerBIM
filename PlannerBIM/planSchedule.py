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
from utils import path, parseDate, parseIsoFormat, listBtw2Dates


def makeSchedule(name = 'Schedule'):
    """Create an project schedule.

    Parameters
    ----------
    name: str, optional
        The label for the schedule.

    Returns
    -------
    <App::FeaturePython>
        The created project.

    Notes
    -----
    Creates a new <App::FeaturePython> object, and turns it into a parametric schedule
    object.
    """
    
    if not FreeCAD.ActiveDocument:
        return FreeCAD.Console.PrintError("No active document. Aborting\n")
    obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython", name)
    PlanSchedule(obj)
    
    if FreeCAD.GuiUp:
        ViewProviderSchedule(obj.ViewObject)

    FreeCAD.ActiveDocument.recompute()    
    return obj
    

class PlanSchedule(Process):
    """The schedulle object. It is the project schedule or part of that project

    Parameters
    ----------
    obj: <App::FeaturePython>
        The object to turn into an Project Schedulle.
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
            The schedulle object.
        """
        
        Process.setProperties(self, obj)

        ######################## Internal properties ################################        
        if not hasattr(obj,"Group"):
            obj.addExtension("App::GroupExtensionPython", self)
        if not hasattr(obj,"Level"):
            obj.addProperty("App::PropertyInteger", "Level", "", "", 4).Level = 0    
        if not hasattr(obj,"UpdatePosChildren"):
            obj.addProperty("App::PropertyBool","UpdatePosChildren", "", "", 4).UpdatePosChildren=False
        if not hasattr(obj,"GridOn"):
            obj.addProperty("App::PropertyBool","GridOn", "", "", 4).GridOn=True
        
        #hide properties
        obj.setEditorMode("ScheduleStart", 2)
        obj.setEditorMode("ScheduleFinish", 2)
        obj.setEditorMode("ScheduleDuration", 2)
        obj.setEditorMode("ActualStart", 2)
        obj.setEditorMode("ActualFinish", 2)
        obj.setEditorMode("ActualDuration", 2)
        obj.setEditorMode("Dim2nd", 2)
        obj.setEditorMode("Dim3rd", 2)
        obj.setEditorMode("IsSuccessorFrom", 2)
        obj.setEditorMode("IsPredecessorTo", 2)
        obj.setEditorMode("OperatesOn", 2) 

    def onDocumentRestored(self, obj):
        """Method run when the document is restored.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The schedulle object.
        """
        Process.onDocumentRestored(self, obj)
        self.setProperties(obj)

    def onChanged(self, obj, prop):
        """Method called when the object has a property changed.

        Parameters
        ----------
        
        obj: <App::FeaturePython>
            The schedulle object.
        prop: string
            The name of the property that has changed.
        """

        if prop == "ScheduleStart" or prop=="ActualStart":
            if hasattr(obj,"ScheduleStart") and hasattr(obj,"ActualStart") and hasattr(obj,"RefStartDate"):
                self._setReferenceStartDate(obj)
        if prop == "ActualFinish":
            if hasattr(obj,"ActualFinish")and hasattr(obj,"RefFinishDate"):
                obj.RefFinishDate = obj.ActualFinish
 
        Process.onChanged(self, obj, prop)
        
        if prop=="UpdatePosChildren":
            if hasattr(obj,"UpdatePosChildren"):
                if obj.UpdatePosChildren:
                    self._updateChildrenPosY(obj, obj.Placement.Base.y)
                    obj.UpdatePosChildren=False
        if prop=="VisibilitySchedule":
            if hasattr(obj,"VisibilitySchedule"):
                self._updateScheduleVisibility(obj)
        if prop=="VisibilityActual":
            if hasattr(obj,"VisibilityActual"):
                self._updateActualVisibility(obj)
        if prop=="UnlockedBaseline":
            if hasattr(obj,"UnlockedBaseline"):
                self._updateChildUnlockedBaseline(obj)
        if prop == "ShowCriticalPath":
            if hasattr(obj,"ShowCriticalPath"):
                if obj.ShowCriticalPath==False:
                    self._updateChildCleanCriticalPath(obj)

    def _setReferenceStartDate(self, obj):
        """Called to updates to the lowest reference start date for the entire schedule.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The schedulle object.
        """
        try:
            l =[parseDate(obj.ActualStart), parseDate(obj.ScheduleStart)]
            obj.RefStartDate = parseIsoFormat(min(l))
        except:
            pass

    def _updateChildrenPosY(self, obj, y):
        """Changes the position on the y-axis, mirroring the position
          in TreeView. Called when a child is placed in the 'Group'
          property of the object or one of its children.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The schedulle object.
        y: int
            The y value of the object's current position.
        
        Returns
        -------
        y: int
            The y value of current position.
        """

        for children in obj.Group:
            y-=children.Dim2nd+0.2
            if hasattr(children,"Placement"):
                children.Placement.Base.y = y
            if hasattr(children,"PlacementActual"):
                children.PlacementActual.Base.y = y
            if hasattr(children,"Group"):
                y = self._updateChildrenPosY(children, y)
        return y

    def _updateScheduleVisibility(self, obj):
        """Called to define if the part of the schedule form will be visible.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The schedulle object.
        """      
        for child in obj.OutListRecursive:
            if hasattr(child,"VisibilitySchedule"):
                child.VisibilitySchedule = obj.VisibilitySchedule
    
    def _updateActualVisibility(self, obj):
        """Called to define if the part of the actual form will be visible.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The schedulle object.
        """
        for child in obj.OutListRecursive:
            if hasattr(child,"VisibilityActual"):
                child.VisibilityActual = obj.VisibilityActual
    
    def _updateChildUnlockedBaseline(self, obj):
        """Called to define existing and locked baseline.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The schedulle object.
        """
        for child in obj.OutListRecursive:
            if hasattr(child,"UnlockedBaseline"):
                child.UnlockedBaseline = obj.UnlockedBaseline

    def _updateChildCleanCriticalPath(self, obj):
        """Called to update critical path demonstration in children.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The schedulle object.
        """
        for child in obj.OutListRecursive:
            if hasattr(child,"ShowCriticalPath"):
                child.ShowCriticalPath = obj.ShowCriticalPath

    def setListOfDays(self, obj):
        """Called to define the list of days for the scheduling period. 
        To draw the date grid and simulate progress.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The schedulle object.
        
        Returns
        -------
        li: list
            List of dates of the total period of the schedule
        """
        tmp = [parseDate(t) for t in [obj.ScheduleStart, obj.ScheduleFinish, obj.ActualStart, obj.ActualFinish]]
        st = parseIsoFormat(min(tmp))
        fn = parseIsoFormat(max(tmp))
        li = listBtw2Dates(st, fn)
        return li

    def getChildrendHeight(self, obj):
        """Calculates the sum of second dimension of each child.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The schedulle object.
        
        Returns
        -------
        h: int
            The sum of second dimension of each child.
        """
        h=obj.Dim2nd-0.2
        for child in obj.OutListRecursive:
            if hasattr(child,"Dim2nd"):
                h-=child.Dim2nd+0.2
        h-=1
        return h

    def __getstate__(self):
       return None
       
    def __setstate__(self, state):
       return None


class ViewProviderSchedule:
    """A View Provider for the schedule object.

    Parameters
    ----------
    vobj: <Gui.ViewProviderDocumentObject>
        The view provider to turn into a schedule view provider.
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
        vobj.addProperty("App::PropertyColor","ShapeColorSchedule","1-Schedule","Scheduled part shape color").ShapeColorSchedule=(0.0,0.0,0.0)
        vobj.addProperty("App::PropertyInteger","TransparencySchedule","1-Schedule","Scheduled part transparency").TransparencySchedule = 40

        #Actual part
        vobj.addProperty("App::PropertyColor","LineColorActual","2-Actual","Actual part line color").LineColorActual=(0.0,0.0,0.0) 
        vobj.addProperty("App::PropertyColor","ShapeColorActual","2-Actual","Actual part shape color").ShapeColorActual=(0.04,0.1,0.4)
        vobj.addProperty("App::PropertyInteger","TransparencyActual","2-Actual","Actual part transparency").TransparencyActual = 40

    def attach(self, vobj):
        """ Adds display of the timeline, grid of days and Gantt bar to 
        the currency scenario graph.
        
        Parameters
        ----------
        vobj: <Gui.ViewProviderDocumentObject>
            The view provider object.
        """        
        self.Object = vobj.Object  #from https://forum.freecadweb.org/viewtopic.php?f=22&t=12139&p=160045&hilit=setedit#p161062 
        
        #draw grid and shapes for schedule representation
        self.grid = self.gridView()
        self.bar = self.ganttBarTitleView()
        
        #root node
        self.node = coin.SoGroup()
        self.node.addChild(self.grid)
        self.node.addChild(self.bar)
        
        vobj.addDisplayMode(self.node,"Flatlines")
        
        self.onChanged(vobj,"ShapeColorSchedule")
        self.onChanged(vobj,"LineColorSchedule")
        self.onChanged(vobj,"TransparencySchedule")
        self.onChanged(vobj,"ShapeColorActual")
        self.onChanged(vobj,"LineColorActual")
        self.onChanged(vobj,"TransparencyActual")

    def ganttBarTitleView(self):
        """Called to draw Gantt bar.
        """
        #draw gantt bar shape
        style=coin.SoDrawStyle()
        style.lineWidth=2
        style.style = coin.SoDrawStyle.LINES
        self.scale = coin.SoScale()
        
        #schedule node
        self.boxSchedule = coin.SoCube()
        self.boxSchedule.height = 0.5
        self.boxSchedule.depth = 1.0
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
        self.boxActual.depth = 1.0
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

    def gridView(self):
        """Called to draw grid with lines and dates.
        """

        #timeline
        tm = coin.SoSeparator()
        timeLineStyle = coin.SoDrawStyle()
        timeLineStyle.style = coin.SoDrawStyle.LINES
        self.tmcoords = coin.SoCoordinate3()
        self.tmlines = coin.SoLineSet()
        tm.addChild(timeLineStyle)
        tm.addChild(self.tmcoords)
        tm.addChild(self.tmlines)
        
        #grid dates
        gr = coin.SoSeparator()
        gridStyle = coin.SoDrawStyle()
        gridStyle.style = coin.SoDrawStyle.LINES
        gridStyle.linePattern = 0x0f0f
        self.grcoords = coin.SoCoordinate3()
        self.grlines = coin.SoLineSet()
        gr.addChild(gridStyle)
        gr.addChild(self.grcoords)
        gr.addChild(self.grlines)
        
        #text dates
        self.text= coin.SoSeparator()
        self.rootText= coin.SoSeparator()
        font = coin.SoFont()
        font.size=0.3
        font.name = "Arial"
        self.rootText.addChild(font)
        self.rootText.addChild(self.text)

        pick = coin.SoPickStyle()
        pick.style.setValue(coin.SoPickStyle.UNPICKABLE)
        
        s = coin.SoSeparator()
        s.addChild(pick)
        s.addChild(tm)
        s.addChild(gr)
        s.addChild(self.rootText)
        
        self.gridSwitch = coin.SoSwitch()
        self.gridSwitch.setName('Grid')
        self.gridSwitch.whichChild = 0
        self.gridSwitch.addChild(s)

        return self.gridSwitch

    def updateData(self, obj, prop):
        """Method called when the schedulle object has a property changed.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The object that has changed.
        prop: string
            The name of the property that has changed.
        """

        if prop == "ScheduleStart" or prop == "ScheduleFinish" \
            or prop == "ActualStart" or prop == "ActualFinish" \
            or prop == 'UpdatePosChildren':
            if hasattr(obj,"ScheduleStart") and hasattr(obj,"ScheduleFinish") \
                and hasattr(obj,"ActualStart") and hasattr(obj,"ActualFinish") \
                and hasattr(obj,"UpdatePosChildren"):
                if obj.GridOn:
                    self._updateGrid(obj)
        if prop == "GridOn":
            #Set the grid visibility
            if hasattr(obj,"GridOn"):
                if obj.GridOn:
                    self.gridSwitch.whichChild = 0
                else:
                    self.gridSwitch.whichChild = -1
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

    #Inspired by Draft/draftguitools/gui_trackers.py 
    #https://github.com/FreeCAD/FreeCAD/blob/master/src/Mod/Draft/draftguitools/gui_trackers.py
    #Tank you Yorik
    def _updateGrid(self, obj):
        """Called to update the timeline and date grid view when 
        the schedule has its dates changed.

        Parameters
        ----------
        listDays: List
            List of days in the schedule.
        ptBase: <FreeCAD.Vector>
            Base point that will be used to calculate the grid properties.
        """
        #height between two lines
        h = 1.5 
        
        #list of days to draw timeline
        listDays = obj.Proxy.setListOfDays(obj)

        #base point to insert grid
        if obj.Placement.Base.x <= obj.PlacementActual.Base.x:
            ptBase = obj.Placement.Base
        else:
            ptBase = obj.PlacementActual.Base

        #time line
        idx_tm = []
        pts_tm = []
        x = x_sup = x_inf = ptBase.x
        y = y_inf = ptBase.y+h
        y_sup_d = y_inf+1
        y_sup_w = y_inf+1.5
        y_sup_m = y_inf+2
        y_sup_y = y_inf+2.5
        z = ptBase.z
        
        days_txt =[]
 
        for d in listDays:
            if d[0]==1 and d[1]==1:
                ptsup = [x_sup, y_sup_y, z]
                days_txt.append([str(d[1])+'/'+str(d[2]), ptsup])
            elif d[0]==1:
                ptsup = [x_sup, y_sup_m, z]
                days_txt.append([str(d[1])+'/'+str(d[2]), ptsup])
            elif d[3]==6:
                ptsup = [x_sup, y_sup_w, z]
                days_txt.append([str(d[0]), ptsup])
            else:
                ptsup = [x_sup, y_sup_d, z]
                days_txt.append([str(d[0]), ptsup])
            
            pts_tm.extend([[x_inf, y_inf, z], ptsup])
            x_sup+=1
            x_inf+=1
        
        pts_tm.extend([[x, y, z], [x_inf, y_inf, z]])
        
        for p in range(0, len(pts_tm), 2):
            idx_tm.append(2)
        
        #delete existing texts to insert new ones
        self.rootText.removeChild(self.text)
        
        self.text = coin.SoSeparator()
        #text
        for d in days_txt:
            t = coin.SoSeparator()
            txtpos = coin.SoTransform()
            txtpos.translation.setValue(d[1])
            txt = coin.SoAsciiText()
            txt.string = d[0]
            t.addChild(txtpos)
            t.addChild(txt)
            self.text.addChild(t)
        self.rootText.addChild(self.text)
        
        #grid
        idx_gr = []
        pts_gr = []
        x_sup = x_inf = ptBase.x
        y_sup = ptBase.y+h
        y_inf = obj.Proxy.getChildrendHeight(obj)
        z = ptBase.z
        
        for d in listDays:
            pts_gr.extend([[x_sup, y_sup, z], [x_inf, y_inf, z]])
            x_sup+=1
            x_inf+=1

        for p in range(0, len(pts_gr), 2):
            idx_gr.append(2)
        
        self.grlines.numVertices.deleteValues(0)
        self.grcoords.point.setValues(pts_gr)
        self.grlines.numVertices.setValues(idx_gr)
        self.tmlines.numVertices.deleteValues(0)
        self.tmcoords.point.setValues(pts_tm)
        self.tmlines.numVertices.setValues(idx_tm)

    def getDisplayModes(self,obj):
        modes=[]
        modes.append("Flatlines")
        return modes

    def getDefaultDisplayMode(self):
        return "Flatlines"

    def setDisplayMode(self,mode):
        return mode

    def getIcon(self):
        return path()+"/icons/schdl_icon.svg"

    def __getstate__(self):
       return None
       
    def __setstate__(self, state):
       return None
