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
from pivy import coin

def makeEdge(predecObj, sucessObj, txtLagValue, txtDurationType, txtSequenceType, name='Edge'):
    """Create a logical sequence relationship that exists between two processes based on a given 
    object, and returns the generated edge.

    Parameters
    ----------
    predecObj: <App::FeaturePython>
        The process object reference , that is the predecessor. 

    sucessObj: <App::FeaturePython>
        The process object reference , that is the sucessor.

    txtLagValue: str
        Describes the duration of the sequence, it is the time lag between the predecessor and the successor 
        as specified by the SequenceType. The value of the selected time interval can be a proportion or a 
        measure of time.
    
    txtDurationType: str
        The allowed types of task duration that specify the lag time measurement (work time or elapsed time).
    
    txtSequenceType: str
        The way in which the time lag applies to the sequence. 
        
    name: str, optional
        The label for the edge. 

    Returns
    -------
    <App::FeaturePython>
        The created edge.

    Notes
    -----
    Creates a new <App::FeaturePython> object, and turns it into a parametric edge
    object.
    """

    e=FreeCAD.ActiveDocument.addObject("App::FeaturePython",name)
    Edge(e)
    _ViewProviderEdge(e.ViewObject)
    e.RelatingProcess = predecObj
    e.RelatedProcess = sucessObj
    e.LagValue = txtLagValue
    e.DurationType = txtDurationType
    e.SequenceType = txtSequenceType
    return e

class Edge():
    """The egde object. It represents a sequential relationship between processes where one process must occur 
    before the other in time and where the moment of the relationship can be described as a type of sequence.
    
    More information here: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_1/FINAL/HTML/link/ifcrelsequence.htm
    
    Parameters
    ----------
    obj: <App::FeaturePython>
        The object to turn into an Edge.
    """  

    def __init__(self, obj):
        self.Object = obj
        obj.Proxy = self   
        self.setProperties(obj)

    def setProperties(self, obj):
        """Assign specific properties.
        
        Parameters
        ----------
        obj: <App::FeaturePython>
            The edge object.
        """

        pl = obj.PropertiesList
        ######################## IFC properties ################################
        if not "RelatingProcess" in pl:
            obj.addProperty("App::PropertyLink", "RelatingProcess", "Relations", "Reference to the process, that is the predecessor")
        if not "RelatedProcess" in pl:
            obj.addProperty("App::PropertyLink", "RelatedProcess", "Relations", "Reference to the process, that is the successor")
        if not "LagValue" in pl:            
            obj.addProperty("App::PropertyString","LagValue","Relations","Value of the time lag selected as being either a ratio or a time measure") # string because is possible representation in number or percentage
        if not "DurationType" in pl:
            obj.addProperty("App::PropertyString","DurationType", "Relations", "The allowed types of task duration that specify the lag time measurement (work time or elapsed time)")            
        if not "SequenceType" in pl:
            obj.addProperty("App::PropertyString","SequenceType", "Relations", "The way in which the time lag applies to the sequence")            

        ######################## Internal properties ################################
        #internal lag value numerical
        if not "intLagValue" in pl:            
            obj.addProperty("App::PropertyInteger","intLagValue","","", 4).intLagValue = 0
        #trigger for update edge draw   
        if not "UpdateEdg" in pl:
            obj.addProperty("App::PropertyBool","UpdateEdg", "", "", 4).UpdateEdg=False

    def execute(self, obj):
        """
        Called on document recompute.
        
        Parameters
        ----------
        obj: <App::FeaturePython>
            The edge object.
        """
        obj.ViewObject.ShowInTree=False

    def onChanged(self, obj, prop):
        """Method called when the object has a property changed.

        Parameters
        ----------
        
        obj: <App::FeaturePython>
            The schedulle object.
        prop: string
            The name of the property that has changed.
        """

        if prop == "LagValue":
            if hasattr(obj,"LagValue"):
                obj.intLagValue = self._parseLagValue(obj)


    def onDocumentRestored(self, obj):
        """Method run when the document is restored.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The edge object.
        """        
        self.setProperties(obj)
        obj.UpdateEdg = True
    

    def _parseLagValue(self, obj):
        """Called to parse the lag value(string) and transform it into an integer value.
        
        Parameters
        ----------
        obj: <App::FeaturePython>
            The edge object.
        
        Returns
        -------
        lag: int
            The integer value to update sucessor process.
        """
        import re
        try:
            txt = obj.LagValue
            if re.findall("[d,D]", txt):
                days = int(re.split('[d, D]',txt)[0])
            elif re.findall("[%]", txt):
                rate = re.split('[%]',txt)[0]/100
                days = int(obj.RelatingProcess.ScheduleDuration * rate)
            else:
                days = int(txt)
            
            return days
        except:
            return 0
            print("Invalid lag text")

    def __getstate__(self):
       return None
       
    def __setstate__(self, state):
       return None


class _ViewProviderEdge:
    """A View Provider for the edge object.

    Parameters
    ----------
    vobj: <Gui.ViewProviderDocumentObject>
        The view provider to turn into a edge view provider.
    """
    
    def __init__(self,vobj):
        vobj.Proxy = self

    def attach(self, vobj):
        """ Adds display of the edge to the currency scenario graph.
        
        Parameters
        ----------
        vobj: <Gui.ViewProviderDocumentObject>
            The view provider object.
        """
        
        self.Object = vobj.Object  #from https://forum.freecadweb.org/viewtopic.php?f=22&t=12139&p=160045&hilit=setedit#p161062
        
        #draw shape for edge
        #points
        point = coin.SoSeparator()
        self.ptCoords = coin.SoCoordinate3()
        p1 = coin.SoType.fromName('SoIndexedPointSet').createInstance()
        p1.coordIndex.set1Value(0, 0)     
        point.addChild(self.ptCoords)
        point.addChild(p1)
        
        #arrow
        triang = coin.SoSeparator()
        self.triangCoords = coin.SoCoordinate3()
        self.triangFace = coin.SoFaceSet()
        triang.addChild(self.triangCoords)
        triang.addChild(self.triangFace)
        
        #edge
        edg = coin.SoSeparator()
        self.lineCoords = coin.SoCoordinate3()
        self.line = coin.SoLineSet()
        edg.addChild(self.lineCoords)
        edg.addChild(self.line)
        
        pick = coin.SoPickStyle()
        pick.style.setValue(coin.SoPickStyle.UNPICKABLE)
        
        self.color = coin.SoBaseColor()
        self.color.rgb.setValue(0.0,0.0,0.0)
        
        Style = coin.SoDrawStyle()
        Style.pointSize.setValue(7)
        Style.lineWidth=2
        Style.style = coin.SoDrawStyle.LINES

        #s = coin.SoSeparator()       
        s = coin.SoGroup()
        s.addChild(pick)
        s.addChild(self.color)
        s.addChild(Style)
        s.addChild(triang)
        s.addChild(point)
        s.addChild(edg)
        vobj.addDisplayMode(s,"Flatlines")
        
        #FIXME: Not implemented yet
        '''
        self.edgeSwitch = coin.SoSwitch()
        self.edgeSwitch.setName('edgeSwitch')
        self.edgeSwitch.whichChild = 0
        self.edgeSwitch.addChild(s)

        #root node
        self.scale = coin.SoScale()
        node = coin.SoGroup()
        node.addChild(self.scale)
        node.addChild(self.edgeSwitch)        
        vobj.addDisplayMode(node,"Flatlines")
        '''

    def updateData(self, obj, prop):
        """Method called when the edge object has a property changed.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The object that has changed.
        prop: string
            The name of the property that has changed.
        """       
        if prop == "UpdateEdg":
            if hasattr(obj,"UpdateEdg"):
                if obj.UpdateEdg:
                    self._updateViewEdge(obj)
                    obj.UpdateEdg = False

    def _updateViewEdge(self, obj):
        """Called to update the edge design.

        Parameters
        ----------
        obj: <App::FeaturePython>
            The object that has changed.
        """
        
        #FIXME: Not implemented yet
        '''
        #hide edge if tasks is not visible  
        if obj.RelatingProcess.VisibilityActual is False or obj.RelatedProcess.VisibilityActual is False:
            self.edgeSwitch.whichChild = -1
        else:
            self.edgeSwitch.whichChild = 0
        '''
        
        
        #change color of the edge to indicate critical path  
        if obj.RelatingProcess.IsCritical is True and obj.RelatedProcess.IsCritical is True:
            self.color.rgb.setValue(1.0,0.0,0.0)
        else:
            self.color.rgb.setValue(0.0,0.0,0.0)
        
        #set points for draw line edge
        if obj.SequenceType == 'START_START':
          dir1, dir2 = -0.5, -0.5
          p1 = [obj.RelatingProcess.StartPoint.x, obj.RelatingProcess.StartPoint.y, 0.0]
          p6 = [obj.RelatedProcess.StartPoint.x, obj.RelatedProcess.StartPoint.y, 0.0]
        elif obj.SequenceType == 'FINISH_FINISH':
          dir1, dir2 = 0.5, 0.5
          p1 = [obj.RelatingProcess.EndPoint.x, obj.RelatingProcess.EndPoint.y, 0.0]
          p6 = [obj.RelatedProcess.EndPoint.x, obj.RelatedProcess.EndPoint.y, 0.0]
        elif obj.SequenceType == 'START_FINISH':
          dir1, dir2 = -0.5, 0.5
          p1 = [obj.RelatingProcess.StartPoint.x, obj.RelatingProcess.StartPoint.y, 0.0]
          p6 = [obj.RelatedProcess.EndPoint.x, obj.RelatedProcess.EndPoint.y, 0.0]
        elif obj.SequenceType == 'FINISH_START':
          dir1, dir2 = 0.5, -0.5
          p1 = [obj.RelatingProcess.EndPoint.x, obj.RelatingProcess.EndPoint.y, 0.0]
          p6 = [obj.RelatedProcess.StartPoint.x, obj.RelatedProcess.StartPoint.y, 0.0]
        #line points
        p2 = [p1[0]+dir1, p1[1], 0.0]
        p3 = [p2[0], (p6[1]+p1[1])/2, 0.0]
        p5= [p6[0]+dir2, p6[1], 0.0]
        p4= [p5[0], p3[1], 0.0]
        #arrow points
        pt1 = p6
        pt2 = [p6[0]+dir2/3, p6[1]+dir2/3, 0.0]
        pt3 = [p6[0]+dir2/3, p6[1]-dir2/3, 0.0]
        
        self.line.numVertices.deleteValues(0)
        self.triangFace.numVertices.deleteValues(0)
        self.ptCoords.point.set1Value(0, p1)
        self.triangCoords.point.setValues([pt1, pt2, pt3])
        self.triangFace.numVertices.setValues([3])
        self.lineCoords.point.setValues([p1, p2, p3, p4, p5, p6])
        self.line.numVertices.setValues([6])

    def getDisplayModes(self,obj):
        modes=[]
        modes.append("Flatlines")
        return modes

    def getDefaultDisplayMode(self):
        return "Flatlines"

    def setDisplayMode(self,mode):
        return mode

    def getIcon(self):
        return 

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None
