# -*- coding: mbcs -*-
# Do not delete the following import lines
from abaqus import *
from abaqusConstants import *
import __main__

def traingle():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
        sheetSize=200.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.setPrimaryObject(option=STANDALONE)
    s.Spot(point=(10.0, 0.0))
    s.Spot(point=(0.0, 15.0))
    s.Spot(point=(20.0, 15.0))
    s.Spot(point=(10.0, 30.0))
    s.Spot(point=(0.0, 30.0))
    s.Spot(point=(20.0, 30.0))
    s.Line(point1=(0.0, 30.0), point2=(10.0, 30.0))
    s.HorizontalConstraint(entity=g[2], addUndoState=False)
    s.Line(point1=(10.0, 30.0), point2=(20.0, 15.0))
    s.Line(point1=(20.0, 15.0), point2=(10.0, 0.0))
    s.Line(point1=(10.0, 0.0), point2=(0.0, 15.0))
    s.Line(point1=(0.0, 15.0), point2=(10.0, 30.0))
    s.Line(point1=(10.0, 30.0), point2=(20.0, 30.0))
    s.HorizontalConstraint(entity=g[7], addUndoState=False)
    s.Line(point1=(0.0, 15.0), point2=(20.0, 15.0))
    s.HorizontalConstraint(entity=g[8], addUndoState=False)
    s.ParallelConstraint(entity1=g[7], entity2=g[8])
    s.ParallelConstraint(entity1=g[8], entity2=g[2], addUndoState=False)
    s.ParallelConstraint(entity1=g[5], entity2=g[3])
    s.ParallelConstraint(entity1=g[6], entity2=g[4])
    session.viewports['Viewport: 1'].view.setValues(nearPlane=181.281, 
        farPlane=195.843, width=80.3786, height=33.8403, cameraPosition=(
        5.95156, 5.88341, 188.562), cameraTarget=(5.95156, 5.88341, 0))
    s.AngularDimension(line1=g[5], line2=g[4], textPoint=(10.8604125976563, 
        10.0025482177734), value=60.0)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=181.281, 
        farPlane=195.843, width=90.9672, height=38.2982, cameraPosition=(
        5.23814, 5.22391, 188.562), cameraTarget=(5.23814, 5.22391, 0))
    s.AngularDimension(line1=g[5], line2=g[8], textPoint=(6.06251096725464, 
        11.0331859588623), value=60.0)
    s.ObliqueDimension(vertex1=v[18], vertex2=v[19], textPoint=(12.1556587219238, 
        9.52707672119141), value=1.0)
    session.viewports['Viewport: 1'].view.setValues(nearPlane=187.424, 
        farPlane=189.7, width=12.5596, height=5.28773, cameraPosition=(
        0.238087, 15.0835, 188.562), cameraTarget=(0.238087, 15.0835, 0))
    s.ObliqueDimension(vertex1=v[6], vertex2=v[7], textPoint=(-0.598231256008148, 
        16.3410797119141), value=0.5)
    s.ObliqueDimension(vertex1=v[16], vertex2=v[17], textPoint=(0.361802160739899, 
        16.420295715332), value=0.5)
    p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR, 
        type=DEFORMABLE_BODY)
    p = mdb.models['Model-1'].parts['Part-1']
    p.BaseWire(sketch=s)
    s.unsetPrimaryObject()
    p = mdb.models['Model-1'].parts['Part-1']
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    del mdb.models['Model-1'].sketches['__profile__']


def crosssection():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON, 
        engineeringFeatures=ON)
    session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
        referenceRepresentation=OFF)
    mdb.models['Model-1'].BoxProfile(name='Profile-1', b=4.0, a=6.0, 
        uniformThickness=ON, t1=1.0)
    mdb.models['Model-1'].Material(name='Material-1')
    mdb.models['Model-1'].materials['Material-1'].Elastic(table=((20000.0, 0.3), ))
    mdb.models['Model-1'].BeamSection(name='Section-1', 
        integration=DURING_ANALYSIS, poissonRatio=0.0, profile='Profile-1', 
        material='Material-1', temperatureVar=LINEAR, 
        consistentMassMatrix=False)
    p = mdb.models['Model-1'].parts['Part-1']
    e = p.edges
    edges = e.getSequenceFromMask(mask=('[#7f ]', ), )
    region = p.Set(edges=edges, name='Set-1')
    p = mdb.models['Model-1'].parts['Part-1']
    p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)


def materialMooney():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    mdb.models['Model-1'].Material(name='Material-2')
    mdb.models['Model-1'].materials['Material-2'].Hyperelastic(
        materialType=ISOTROPIC, testData=OFF, type=MOONEY_RIVLIN, 
        moduliTimeScale=INSTANTANEOUS, volumetricResponse=VOLUMETRIC_DATA, 
        table=((3.0, 4.0, 5.0), ))


