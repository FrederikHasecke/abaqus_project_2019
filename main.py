from abaqus import *
from abaqusConstants import *
import __main__
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

import time
import os
import sys
workdir = os.getcwd()


'''
The main() function is a wrapper for all subfunctions needed for the parametrization of the archmedean lattices.
It gets called at the very end of this file, so that every funtion can be read into the memory and no variable 
gets declared before the execution.
'''
def main():
    # Call a function to open a new file
    # This is especially useful to execute a new run after a previous run did not yield the correct boundary conditions
    new_start()

    # First user input:
    # Define the chosen structure. The response should be a, b, c, d, e, f, g, h, i or k.
    # They are corresponding to the listings in Shimada et al., SR 2015
    structure = select_structure()

    # Second User Input:
    # Choosing the edge length. All structures are built with a edge length of 1[mm]
    # a simple scaling of the vertices locations will ensure a proper edge length
    edge = select_edge_length(structure)

    # Create the choosen structure
    # This function depends on the previous user inputs to create the choosen structure with the correct edge length
    create_structure(structure, edge)

    # Third User Input:
    # Material. The user can decide between elastic or hyperelastic Mooney-Rivlin models and enter
    # any desired material values. Values for the most common materials are provided in the accompanying documentation.
    # We have limited this script to use
    model, young_modulus, poisson_rate, c10, c01, d1 = select_material()

    # Create the choosen Material
    create_material(model, young_modulus, poisson_rate, c10, c01, d1)

    # Fourth User Input:
    # Beam Section. The user can pick between the provided standard beam sections
    # A second getInputs window will open after the selection for the provided variables of the cross sections
    # There is an additional condition which prevents the beam section to be too large and to overlap at areas which
    # are not supposed to overlap. This is not visible in the visualization but unphysical conditions are not desired.
    # You can find additional information in the documentation attached to this code
    section, width, width_2, height, radius, d, thickness, thickness_2, thickness_3, i = select_cross_section(edge, structure)

    # Create the choosen Cross section and assign it to the structure
    create_cross_section(section, width, width_2, height, radius, d, thickness, thickness_2, thickness_3, i)

    # Create the mesh for the FEA
    create_mesh(edge)

    # Create the assembly
    create_assembly()

    # Create the step module
    create_step()

    # Fifth User Input:
    # Loading Conditions.
    # The User can choose between uniaxial and shear forces as well as decide the provided force and axis
    force, loadcase, axis = select_boundary_conditions()

    # Create the Boundary conditions for the user
    # This includes:
    #   - Loads
    #   - Boundary Conditions (fixed and movable bearings)
    #   - Periodic Boundary Conditions (Equations)
    create_boundary_conditions(structure, force, loadcase, axis)

    # Run the prepared analysis and display the result
    run_analysis(workdir)

# Makro to delete everything and open a new file
def new_start():
    Mdb()
    session.viewports['Viewport: 1'].setValues(displayedObject=None)

# This function queries the user to choose between the 11 possible Structures and returns the chosen value.
# Takes in the chosen structure from the user input and checks if it is one of the 11 possible structures.
# If it is not, the user gets queried again
# We have left the option for the "Mapple Leaf" in the selectable strucutures, but we did not include it.
# We therefore added a repeat if the user chooses this structure
def select_structure():
    possible_structures = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'k']
    structure = str(getInput("Please choose one of the 11 Structures presented in the attached documentation."
                             " [Choose from a to k] excluding 'j'", "a"))

    if structure in possible_structures:
        pass

    else:
        getWarningReply('The chosen letter is not part of the possible options.\n'
                    ' Please choose an available option.', buttons=(YES,))
        structure = select_structure()

    return structure


def select_edge_length(structure):
    # This dictionary has no further use than to read back the choosen strucutre to the user.
    # It can be seen as a check without an option to correct the mistake.
    structure_dict = {'a': 'Square', 'b': 'Honeycomb', 'c': 'Triangular', 'd': 'CaVO', 'e': 'Star', 'f': 'SrCuBo',
                      'g': 'Kagome', 'h': 'Bounce', 'i': 'Trellis', 'j': 'Mapple_leaf', 'k': 'SHD'}

    # We added a try/catch for user inputs which are not integer or float values to keep the script from crashing
    # later on in the execution
    try:
        edge_length = float(getInput("Please enter the desired edge length for "+
                                     structure_dict[structure]+" in [mm]", "20"))

    except:
        getWarningReply('The provided value is not a valid number.\n'
                        'Please choose an Integer or float.\n'
                        'Please note: Python uses a dot for decimal values', buttons=(YES,))
        edge_length = select_edge_length(structure)

    # This second check makes sure, that the user did not select an edge size of zero or a negativ value, as this would
    # crash the execution later on.
    if edge_length > 0.0:
        pass
    else:
        getWarningReply('The edge length must be larger than Zero.\n'
                        ' Please choose a value larger than Zero.', buttons=(YES,))
        edge_length = select_edge_length()
    return edge_length

'''
Creation of the 10 available lattices using periodic smalles unit cells.
Mapple leaf has once again been excluded as the RVE is too large.
'''
def create_structure(structure, edge):
    # Create a bunch of if statements to create the corresponing structure.
    # If the time permits, change this to a more sophisticated method of selection

    # The created points get multiplied by the user-selected edge length to scale the lattice accordingly
    # In a second run the Oblique Dimension Restrain gets scaled to the proper value as well.

    if structure == 'a':
        s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                                     sheetSize=edge * 2)
        g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
        s1.setPrimaryObject(option=STANDALONE)
        s1.Spot(point=(0.0, edge * 0.5))
        s1.Spot(point=(edge * 0.5, edge * 0.5))
        s1.Spot(point=(edge * 0.5, edge * 0.0))
        s1.Spot(point=(edge * 1.0, edge * 0.5))
        s1.Spot(point=(edge * 0.5, edge * 1.0))
        s1.Line(point1=(0.0, edge * 0.5), point2=(edge * 0.5, edge * 0.5))
        s1.HorizontalConstraint(entity=g[2], addUndoState=False)
        s1.Line(point1=(edge * 0.5, edge * 0.5), point2=(edge * 1.0, edge * 0.5))
        s1.HorizontalConstraint(entity=g[3], addUndoState=False)
        s1.ParallelConstraint(entity1=g[2], entity2=g[3], addUndoState=False)
        s1.Line(point1=(edge * 0.5, edge * 1.0), point2=(edge * 0.5, edge * 0.5))
        s1.VerticalConstraint(entity=g[4], addUndoState=False)
        s1.Line(point1=(edge * 0.5, edge * 0.5), point2=(edge * 0.5, 0.0))
        s1.VerticalConstraint(entity=g[5], addUndoState=False)
        s1.ParallelConstraint(entity1=g[4], entity2=g[5], addUndoState=False)
        p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR,
                                       type=DEFORMABLE_BODY)
        p = mdb.models['Model-1'].parts['Part-1']
        p.BaseWire(sketch=s1)
        s1.unsetPrimaryObject()
        p = mdb.models['Model-1'].parts['Part-1']
        del mdb.models['Model-1'].sketches['__profile__']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)

    if structure == 'b':
        session.viewports['Viewport: 1'].setValues(displayedObject=None)
        s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                                    sheetSize=200.0)
        g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
        s.setPrimaryObject(option=STANDALONE)
        s.Spot(point=(edge * 20.0, edge * 10.0))
        s.Spot(point=(edge * 20.0, edge * 12.5))
        s.Line(point1=(edge * 20.0, edge * 10.0), point2=(edge * 20.0, edge * 12.5))
        s.VerticalConstraint(entity=g[2], addUndoState=False)
        s.ObliqueDimension(vertex1=v[2], vertex2=v[3], textPoint=(edge * 19.0659027099609,
                                                                  edge * 11.248706817627), value=edge * 0.5)
        s.Spot(point=(edge * 19.6390190124512, edge * 12.7782030105591))
        s.Line(point1=(edge * 20.0, edge * 12.5), point2=(edge * 19.6390190124512, edge * 12.7782030105591))
        s.AngularDimension(line1=g[3], line2=g[2], textPoint=(edge * 19.9206638336182,
                                                              edge * 12.3458127975464), value=120.0)
        s.ObliqueDimension(vertex1=v[5], vertex2=v[6], textPoint=(edge * 19.6173553466797,
                                                                  edge * 12.3458127975464), value=edge)
        s.Spot(point=(edge * 19.3032131195068, edge * 13.7943201065063))
        s.Line(point1=(edge * 19.1339745962156, edge * 13.0), point2=(edge * 19.3032131195068,
                                                                      edge * 13.7943201065063))
        s.AngularDimension(line1=g[4], line2=g[3], textPoint=(edge * 19.3790397644043,
                                                              edge * 13.0592565536499), value=120.0)
        s.ObliqueDimension(vertex1=v[8], vertex2=v[9], textPoint=(edge * 18.7940864562988,
                                                                  edge * 13.3727397918701), value=edge)
        s.Spot(point=(edge * 20.0, edge * 15.0))
        s.Line(point1=(edge * 19.1339745962156, edge * 14.0), point2=(edge * 20.0, edge * 15.0))
        s.AngularDimension(line1=g[4], line2=g[5], textPoint=(edge * 19.3248767852783,
                                                              edge * 13.9888954162598), value=120.0)
        s.ObliqueDimension(vertex1=v[11], vertex2=v[12], textPoint=(edge * 19.5631923675537,
                                                                    edge * 14.5942420959473), value=edge)
        s.Spot(point=(edge * 20.0, edge * 15.0))
        s.Line(point1=(edge * 20.0, edge * 14.5), point2=(edge * 20.0, edge * 15.0))
        s.VerticalConstraint(entity=g[6], addUndoState=False)
        s.ObliqueDimension(vertex1=v[14], vertex2=v[15], textPoint=(edge * 19.6173553466797,
                                                                    edge * 14.7131490707397), value=edge * 0.5)
        s.Spot(point=(edge * 20.7222671508789, edge * 13.9888954162598))
        s.Line(point1=(edge * 20.0, edge * 14.5), point2=(edge * 20.7222671508789, edge * 13.9888954162598))
        s.AngularDimension(line1=g[5], line2=g[7], textPoint=(edge * 19.9748268127441,
                                                              edge * 14.3239974975586), value=120.0)
        s.ObliqueDimension(vertex1=v[17], vertex2=v[18], textPoint=(edge * 20.5381145477295,
                                                                    edge * 14.5834321975708), value=edge)
        s.Spot(point=(edge * 20.689769744873, edge * 12.8863000869751))
        s.Line(point1=(edge * 20.0, edge * 12.5), point2=(edge * 20.689769744873, edge * 12.8863000869751))
        s.AngularDimension(line1=g[3], line2=g[8], textPoint=(edge * 20.0506534576416,
                                                              edge * 12.6809148788452), value=120.0)
        s.ObliqueDimension(vertex1=v[20], vertex2=v[21], textPoint=(edge * 20.5814437866211,
                                                                    edge * 12.4430999755859), value=edge)
        p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR,
                                       type=DEFORMABLE_BODY)
        p = mdb.models['Model-1'].parts['Part-1']
        p.BaseWire(sketch=s)
        s.unsetPrimaryObject()
        p = mdb.models['Model-1'].parts['Part-1']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        del mdb.models['Model-1'].sketches['__profile__']

    if structure == 'c':
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
                                                        farPlane=195.843, width=80.3786, height=33.8403,
                                                        cameraPosition=(
                                                            5.95156, 5.88341, 188.562),
                                                        cameraTarget=(5.95156, 5.88341, 0))
        s.AngularDimension(line1=g[5], line2=g[4], textPoint=(10.8604125976563,
                                                              10.0025482177734), value=60.0)
        session.viewports['Viewport: 1'].view.setValues(nearPlane=181.281,
                                                        farPlane=195.843, width=90.9672, height=38.2982,
                                                        cameraPosition=(
                                                            5.23814, 5.22391, 188.562),
                                                        cameraTarget=(5.23814, 5.22391, 0))
        s.AngularDimension(line1=g[5], line2=g[8], textPoint=(6.06251096725464,
                                                              11.0331859588623), value=60.0)
        s.ObliqueDimension(vertex1=v[18], vertex2=v[19], textPoint=(12.1556587219238,
                                                                    9.52707672119141), value=edge)
        session.viewports['Viewport: 1'].view.setValues(nearPlane=187.424,
                                                        farPlane=189.7, width=12.5596, height=5.28773, cameraPosition=(
                0.238087, 15.0835, 188.562), cameraTarget=(0.238087, 15.0835, 0))
        s.ObliqueDimension(vertex1=v[6], vertex2=v[7], textPoint=(-0.598231256008148,
                                                                  16.3410797119141), value=0.5*edge)
        s.ObliqueDimension(vertex1=v[16], vertex2=v[17], textPoint=(0.361802160739899,
                                                                    16.420295715332), value=0.5*edge)
        p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR,
                                       type=DEFORMABLE_BODY)
        p = mdb.models['Model-1'].parts['Part-1']
        p.BaseWire(sketch=s)
        s.unsetPrimaryObject()
        p = mdb.models['Model-1'].parts['Part-1']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        del mdb.models['Model-1'].sketches['__profile__']

    if structure == 'd':
        s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                                    sheetSize=200.0)
        g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
        s.setPrimaryObject(option=STANDALONE)
        s.Spot(point=(30.0, 25.0))
        s.Spot(point=(30.0, 20.0))
        s.Spot(point=(35.0, 15.0))
        s.Spot(point=(25.0, 15.0))
        s.Spot(point=(30.0, 10.0))
        s.Spot(point=(40.0, 15.0))
        s.Spot(point=(30.0, 5.0))
        s.Spot(point=(20.0, 15.0))
        s.Line(point1=(30.0, 25.0), point2=(30.0, 20.0))
        s.VerticalConstraint(entity=g[2], addUndoState=False)
        s.Line(point1=(30.0, 20.0), point2=(35.0, 15.0))
        s.Line(point1=(35.0, 15.0), point2=(30.0, 10.0))
        s.PerpendicularConstraint(entity1=g[3], entity2=g[4], addUndoState=False)
        s.Line(point1=(30.0, 10.0), point2=(25.0, 15.0))
        s.PerpendicularConstraint(entity1=g[4], entity2=g[5], addUndoState=False)
        s.Line(point1=(25.0, 15.0), point2=(30.0, 20.0))
        s.PerpendicularConstraint(entity1=g[5], entity2=g[6], addUndoState=False)
        s.Line(point1=(20.0, 15.0), point2=(25.0, 15.0))
        s.HorizontalConstraint(entity=g[7], addUndoState=False)
        s.Line(point1=(40.0, 15.0), point2=(35.0, 15.0))
        s.HorizontalConstraint(entity=g[8], addUndoState=False)
        s.Line(point1=(30.0, 10.0), point2=(30.0, 5.0))
        s.VerticalConstraint(entity=g[9], addUndoState=False)
        session.viewports['Viewport: 1'].view.setValues(nearPlane=179.294,
                                                        farPlane=197.829, width=60.805, height=31.3156,
                                                        cameraPosition=(23.733,
                                                                        12.253, 188.562),
                                                        cameraTarget=(23.733, 12.253, 0))
        s.ObliqueDimension(vertex1=v[14], vertex2=v[15], textPoint=(25.1149806976318,
                                                                    10.4430112838745), value=edge)
        s.ObliqueDimension(vertex1=v[12], vertex2=v[13], textPoint=(35.5946273803711,
                                                                    10.5579309463501), value=edge)
        s.ObliqueDimension(vertex1=v[20], vertex2=v[21], textPoint=(33.9247970581055,
                                                                    12.9137811660767), value=0.5*edge)
        s.ObliqueDimension(vertex1=v[8], vertex2=v[9], textPoint=(27.8212642669678,
                                                                  14.2928152084351), value=0.5*edge)
        s.ObliqueDimension(vertex1=v[18], vertex2=v[19], textPoint=(25.1725616455078,
                                                                    8.20208168029785), value=0.5*edge)
        s.ObliqueDimension(vertex1=v[22], vertex2=v[23], textPoint=(31.7367343902588,
                                                                    7.22526550292969), value=0.5*edge)
        p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR,
                                       type=DEFORMABLE_BODY)
        p = mdb.models['Model-1'].parts['Part-1']
        p.BaseWire(sketch=s)
        s.unsetPrimaryObject()
        p = mdb.models['Model-1'].parts['Part-1']
        del mdb.models['Model-1'].sketches['__profile__']
        p = mdb.models['Model-1'].parts['Part-1']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)

    if structure == 'e':
        s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                                    sheetSize=200.0)
        g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
        s.setPrimaryObject(option=STANDALONE)
        s.Spot(point=(edge * 40.0, edge * 20.0))
        s.Spot(point=(edge * 42.5, edge * 20.0))
        session.viewports['Viewport: 1'].view.setValues(nearPlane=184.898,
                                                        farPlane=192.225, width=24.0357, height=12.3788,
                                                        cameraPosition=(
                                                            40.8794, 21.5074, 188.562),
                                                        cameraTarget=(40.8794, 21.5074, 0))
        s.Line(point1=(edge * 40.0, edge * 20.0), point2=(edge * 42.5, edge * 20.0))
        s.HorizontalConstraint(entity=g[2], addUndoState=False)
        s.ObliqueDimension(vertex1=v[2], vertex2=v[3], textPoint=(edge * 41.2890586853027,
                                                                  edge * 20.7465476989746), value=edge)
        session.viewports['Viewport: 1'].view.setValues(nearPlane=186.818,
                                                        farPlane=190.305, width=11.4391, height=5.89132,
                                                        cameraPosition=(
                                                            41.8348, 20.251, 188.562),
                                                        cameraTarget=(41.8348, 20.251, 0))
        s.Spot(point=(edge * 41.997257232666, edge * 19.2619190216064))
        s.Line(point1=(edge * 41.5, edge * 20.0), point2=(edge * 41.997257232666, edge * 19.2619190216064))
        s.Line(point1=(edge * 42.5, edge * 20.0), point2=(edge * 41.997257232666, edge * 19.2619190216064))
        s.AngularDimension(line1=g[2], line2=g[3], textPoint=(edge * 41.661449432373,
                                                              edge * 19.8564548492432), value=60.0)
        s.AngularDimension(line1=g[2], line2=g[4], textPoint=(edge * 42.3113975524902,
                                                              edge * 19.8564548492432), value=60.0)
        s.Spot(point=(edge * 42.0839157104492, edge * 18.3538990020752))
        s.Line(point1=(edge * 42.0, edge * 19.1339745962156), point2=(edge * 42.0839157104492,
                                                                      edge * 18.3538990020752))
        s.AngularDimension(line1=g[4], line2=g[5], textPoint=(edge * 42.1489105224609,
                                                              edge * 19.0457229614258), value=150.0)
        s.ObliqueDimension(vertex1=v[10], vertex2=v[11], textPoint=(edge * 41.7806091308594,
                                                                    edge * 18.7862892150879), value=edge * 0.5)
        s.Spot(point=(edge * 43.0913352966309, edge * 20.2780361175537))
        s.Line(point1=(edge * 42.5, edge * 20.0), point2=(edge * 43.0913352966309, edge * 20.2780361175537))
        s.AngularDimension(line1=g[4], line2=g[6], textPoint=(edge * 42.603874206543,
                                                              edge * 19.921314239502), value=150.0)
        s.ObliqueDimension(vertex1=v[13], vertex2=v[14], textPoint=(edge * 42.9396820068359,
                                                                    edge * 19.8888835906982), value=edge)
        s.Spot(point=(edge * 43.9362678527832, edge * 21.0671463012695))
        s.Line(point1=(edge * 43.3660254037844, edge * 20.5), point2=(edge * 43.9362678527832,
                                                                      edge * 21.0671463012695))
        s.AngularDimension(line1=g[6], line2=g[7], textPoint=(edge * 43.2754898071289,
                                                              edge * 20.6347579956055), value=150.0)
        s.ObliqueDimension(vertex1=v[16], vertex2=v[17], textPoint=(edge * 43.849609375,
                                                                    edge * 20.6563758850098), value=edge)
        s.Spot(point=(edge * 40.8490142822266, edge * 20.3428936004639))
        s.Line(point1=(edge * 41.5, edge * 20.0), point2=(edge * 40.8490142822266, edge * 20.3428936004639))
        s.AngularDimension(line1=g[2], line2=g[8], textPoint=(edge * 41.1848220825195,
                                                              edge * 20.083459854126), value=30.0)
        s.ObliqueDimension(vertex1=v[19], vertex2=v[20], textPoint=(edge * 41.0548324584961,
                                                                    edge * 19.9105033874512), value=edge)
        s.Spot(point=(edge * 40.1990661621094, edge * 21.1536254882813))
        s.Line(point1=(edge * 40.6339745962156, edge * 20.5), point2=(edge * 40.1990661621094,
                                                                      edge * 21.1536254882813))
        s.AngularDimension(line1=g[8], line2=g[9], textPoint=(edge * 40.3182258605957,
                                                              edge * 20.7860946655273), value=30.0)
        s.ObliqueDimension(vertex1=v[22], vertex2=v[23], textPoint=(edge * 40.144905090332,
                                                                    edge * 20.7104244232178), value=edge)
        s.Spot(point=(edge * 40.0582466125488, edge * 20.429370880127))
        s.Line(point1=(edge * 40.6339745962156, edge * 20.5), point2=(edge * 40.0582466125488,
                                                                      edge * 20.429370880127))
        s.AngularDimension(line1=g[10], line2=g[9], textPoint=(edge * 40.2098999023438,
                                                               edge * 20.6888065338135), value=60.0)
        s.ObliqueDimension(vertex1=v[25], vertex2=v[26], textPoint=(edge * 40.3182258605957,
                                                                    edge * 20.2347965240479), value=edge * 0.5)
        s.Spot(point=(edge * 40.144905090332, edge * 22.0832633972168))
        s.Line(point1=(edge * 40.1339745962156, edge * 21.3660254037844), point2=(edge * 40.144905090332,
                                                                                  edge * 22.0832633972168))
        s.AngularDimension(line1=g[9], line2=g[11], textPoint=(edge * 40.0474128723145,
                                                               edge * 21.640064239502), value=30.0)
        s.ObliqueDimension(vertex1=v[28], vertex2=v[29], textPoint=(edge * 39.8524284362793,
                                                                    edge * 21.726541519165), value=edge)
        s.Spot(point=(edge * 40.5565376281738, edge * 23.0453319549561))
        s.Line(point1=(edge * 40.1339745962156, edge * 22.3660254037844), point2=(edge * 40.5565376281738,
                                                                                  edge * 23.0453319549561))
        s.AngularDimension(line1=g[11], line2=g[12], textPoint=(edge * 40.3073921203613,
                                                                edge * 22.3426990509033), value=150.0)
        s.ObliqueDimension(vertex1=v[31], vertex2=v[32], textPoint=(edge * 40.5998687744141,
                                                                    edge * 22.5805130004883), value=edge)
        session.viewports['Viewport: 1'].view.setValues(nearPlane=187.282,
                                                        farPlane=189.841, width=8.39519, height=4.32366,
                                                        cameraPosition=(
                                                            42.3066, 22.8246, 188.562),
                                                        cameraTarget=(42.3066, 22.8246, 0))
        s.Spot(point=(edge * 41.1935691833496, edge * 23.9472007751465))
        s.Line(point1=(edge * 40.6339745962156, edge * 23.2320508075688), point2=(edge * 41.1935691833496,
                                                                                  edge * 23.9472007751465))
        s.AngularDimension(line1=g[12], line2=g[13], textPoint=(edge * 40.9391708374023,
                                                                edge * 23.756799697876), value=30.0)
        s.ObliqueDimension(vertex1=v[34], vertex2=v[35], textPoint=(edge * 41.1220207214355,
                                                                    edge * 23.2332000732422), value=edge)
        s.Spot(point=(edge * 42.401969909668, edge * 23.756799697876))
        s.Line(point1=(edge * 41.5, edge * 23.7320508075688), point2=(edge * 42.401969909668,
                                                                      edge * 23.756799697876))
        s.AngularDimension(line1=g[13], line2=g[14], textPoint=(edge * 41.8136672973633,
                                                                edge * 23.8202667236328), value=30.0)
        s.ObliqueDimension(vertex1=v[37], vertex2=v[38], textPoint=(edge * 41.9249687194824,
                                                                    edge * 23.5664005279541), value=edge)
        s.Spot(point=(edge * 43.2764663696289, edge * 23.3601341247559))
        s.Line(point1=(edge * 42.5, edge * 23.7320508075688), point2=(edge * 43.2764663696289,
                                                                      edge * 23.3601341247559))
        s.AngularDimension(line1=g[14], line2=g[15], textPoint=(edge * 42.8551177978516,
                                                                edge * 23.661600112915), value=30.0)
        s.ObliqueDimension(vertex1=v[40], vertex2=v[41], textPoint=(edge * 42.7517700195313,
                                                                    edge * 23.3283996582031), value=edge)
        s.Spot(point=(edge * 43.9045181274414, edge * 22.3922691345215))
        s.Line(point1=(edge * 43.3660254037844, edge * 23.2320508075688), point2=(edge * 43.9045181274414,
                                                                                  edge * 22.3922691345215))
        s.AngularDimension(line1=g[15], line2=g[16], textPoint=(edge * 43.5865173339844,
                                                                edge * 23.0190010070801), value=30.0)
        s.ObliqueDimension(vertex1=v[43], vertex2=v[44], textPoint=(edge * 43.3639183044434,
                                                                    edge * 22.6699352264404), value=edge)
        s.Spot(point=(edge * 40.1839218139648, edge * 23.1935348510742))
        s.Line(point1=(edge * 40.6339745962156, edge * 23.2320508075688), point2=(edge * 40.1839218139648,
                                                                                  edge * 23.1935348510742))
        s.AngularDimension(line1=g[17], line2=g[12], textPoint=(edge * 40.4621696472168,
                                                                edge * 23.1380004882813), value=60.0)
        s.ObliqueDimension(vertex1=v[46], vertex2=v[47], textPoint=(edge * 40.3667678833008,
                                                                    edge * 23.4394664764404), value=edge * 0.5)
        s.Spot(point=(edge * 43.8329658508301, edge * 23.2332000732422))
        s.Line(point1=(edge * 43.3660254037844, edge * 23.2320508075688), point2=(edge * 43.8329658508301,
                                                                                  edge * 23.2332000732422))
        s.AngularDimension(line1=g[18], line2=g[16], textPoint=(edge * 43.6501159667969,
                                                                edge * 23.0745334625244), value=60.0)
        s.ObliqueDimension(vertex1=v[49], vertex2=v[50], textPoint=(edge * 43.6342163085938,
                                                                    edge * 23.4394664764404), value=edge * 0.5)
        s.Spot(point=(edge * 42.0203666687012, edge * 24.3597316741943))
        s.Line(point1=(edge * 41.5, edge * 23.7320508075688), point2=(edge * 42.0203666687012,
                                                                      edge * 24.3597316741943))
        s.AngularDimension(line1=g[19], line2=g[14], textPoint=(edge * 41.7262191772461,
                                                                edge * 23.8519992828369), value=60.0)
        s.Line(point1=(edge * 41.9076655308654, edge * 24.4381482195221), point2=(edge * 42.5,
                                                                                  edge * 23.7320508075688))
        s.AngularDimension(line1=g[20], line2=g[14], textPoint=(edge * 42.2986183166504,
                                                                edge * 23.8281993865967), value=60.0)
        s.Spot(point=(edge * 42.0203666687012, edge * 24.9309310913086))
        s.Line(point1=(edge * 42.0203666687012, edge * 24.9309310913086), point2=(edge * 42.0,
                                                                                  edge * 24.5980762113532))
        s.AngularDimension(line1=g[21], line2=g[19], textPoint=(edge * 41.8454666137695,
                                                                edge * 24.5501327514648), value=150.0)
        s.ObliqueDimension(vertex1=v[57], vertex2=v[58], textPoint=(edge * 42.2588691711426,
                                                                    edge * 24.7167320251465), value=edge * 0.5)
        s.Spot(point=(edge * 44.0031471252441, edge * 20.6134433746338))
        s.Line(point1=(edge * 43.3660254037844, edge * 20.5), point2=(edge * 44.0031471252441,
                                                                      edge * 20.6134433746338))
        s.AngularDimension(line1=g[22], line2=g[7], textPoint=(edge * 43.560359954834,
                                                               edge * 20.6632308959961), value=60.0)
        s.ObliqueDimension(vertex1=v[60], vertex2=v[61], textPoint=(edge * 43.6788520812988,
                                                                    edge * 20.246265411377), value=edge * 0.5)
        p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR,
                                       type=DEFORMABLE_BODY)
        p = mdb.models['Model-1'].parts['Part-1']
        p.BaseWire(sketch=s)
        s.unsetPrimaryObject()
        p = mdb.models['Model-1'].parts['Part-1']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        del mdb.models['Model-1'].sketches['__profile__']

    if structure == 'f':
        s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                                    sheetSize=200.0)
        g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
        s.setPrimaryObject(option=STANDALONE)
        s.Spot(point=(edge * 45.0, edge * 25.0))
        s.Spot(point=(edge * 45.0, edge * 22.5))
        s.Line(point1=(edge * 45.0, edge * 25.0), point2=(edge * 45.0, edge * 22.5))
        s.VerticalConstraint(entity=g[2], addUndoState=False)
        session.viewports['Viewport: 1'].view.setValues(nearPlane=182.168,
                                                        farPlane=194.955, width=41.9475, height=21.6037,
                                                        cameraPosition=(
                                                            45.2945, 22.9523, 188.562),
                                                        cameraTarget=(45.2945, 22.9523, 0))
        s.ObliqueDimension(vertex1=v[2], vertex2=v[3], textPoint=(edge * 44.0630722045898,
                                                                  edge * 23.6856727600098), value=edge)
        session.viewports['Viewport: 1'].view.setValues(nearPlane=185.873,
                                                        farPlane=191.25, width=17.6399, height=9.08484, cameraPosition=(
                45.7044, 23.0366, 188.562), cameraTarget=(45.7044, 23.0366, 0))
        s.Spot(point=(edge * 46.0886306762695, edge * 23.1282997131348))
        s.Line(point1=(edge * 45.0, edge * 23.5), point2=(edge * 46.0886306762695, edge * 23.1282997131348))
        s.AngularDimension(line1=g[2], line2=g[3], textPoint=(edge * 45.1865882873535,
                                                              edge * 23.2283172607422), value=60.0)
        s.ObliqueDimension(vertex1=v[5], vertex2=v[6], textPoint=(edge * 45.9215850830078,
                                                                  edge * 23.5450344085693), value=edge)
        s.Line(point1=(edge * 45.0, edge * 22.5), point2=(edge * 45.8660254037844, edge * 23.0))
        s.Spot(point=(edge * 43.9504585266113, edge * 23.0449523925781))
        s.Line(point1=(edge * 45.0, edge * 23.5), point2=(edge * 43.9504585266113, edge * 23.0449523925781))
        s.AngularDimension(line1=g[5], line2=g[2], textPoint=(edge * 44.9193153381348,
                                                              edge * 23.3616714477539), value=60.0)
        s.ObliqueDimension(vertex1=v[10], vertex2=v[11], textPoint=(edge * 44.234432220459,
                                                                    edge * 23.595043182373), value=edge)
        s.Line(point1=(edge * 45.0, edge * 22.5), point2=(edge * 44.1339745962156, edge * 23.0))
        session.viewports['Viewport: 1'].view.setValues(nearPlane=186.818,
                                                        farPlane=190.305, width=11.4391, height=5.89132,
                                                        cameraPosition=(
                                                            45.5038, 23.2199, 188.562),
                                                        cameraTarget=(45.5038, 23.2199, 0))
        s.Spot(point=(edge * 43.6297378540039, edge * 23.8955001831055))
        s.Line(point1=(edge * 44.1339745962156, edge * 23.0), point2=(edge * 43.6297378540039,
                                                                      edge * 23.8955001831055))
        s.AngularDimension(line1=g[7], line2=g[5], textPoint=(edge * 44.1605262756348,
                                                              edge * 23.23610496521), value=90.0)
        s.ObliqueDimension(vertex1=v[15], vertex2=v[16], textPoint=(edge * 43.6189041137695,
                                                                    edge * 23.3009643554688), value=edge)
        s.Spot(point=(edge * 44.431339263916, edge * 24.0252170562744))
        s.Line(point1=(edge * 43.6339745962156, edge * 23.8660254037844), point2=(edge * 44.431339263916,
                                                                                  edge * 24.0252170562744))
        s.AngularDimension(line1=g[8], line2=g[7], textPoint=(edge * 43.8355522155762,
                                                              edge * 23.7657833099365), value=90.0)
        s.Line(point1=(edge * 44.3381402703574, edge * 24.2725756453043), point2=(edge * 45.0, edge * 23.5))
        s.AngularDimension(line1=g[8], line2=g[9], textPoint=(edge * 44.3338470458984,
                                                              edge * 24.1116943359375), value=90.0)
        s.Spot(point=(edge * 45.4712562561035, edge * 24.1225051879883))
        s.Line(point1=(edge * 45.0, edge * 23.5), point2=(edge * 45.4712562561035, edge * 24.1225051879883))
        s.AngularDimension(line1=g[10], line2=g[3], textPoint=(edge * 45.1896133422852,
                                                               edge * 23.4955387115479), value=90.0)
        s.ObliqueDimension(vertex1=v[23], vertex2=v[24], textPoint=(edge * 45.5037536621094,
                                                                    edge * 23.7117347717285), value=edge)
        s.Spot(point=(edge * 46.6303291320801, edge * 24.1981735229492))
        s.Line(point1=(edge * 45.5, edge * 24.3660254037844), point2=(edge * 46.6303291320801,
                                                                      edge * 24.1981735229492))
        s.Line(point1=(edge * 46.6303291320801, edge * 24.1981735229492), point2=(edge * 45.8660254037844,
                                                                                  edge * 23.0))
        s.AngularDimension(line1=g[11], line2=g[12], textPoint=(edge * 46.3270225524902,
                                                                edge * 24.0684566497803), value=90.0)
        s.Spot(point=(edge * 46.4895095825195, edge * 22.4902324676514))
        s.Line(point1=(edge * 45.8660254037844, edge * 23.0), point2=(edge * 46.4895095825195,
                                                                      edge * 22.4902324676514))
        s.AngularDimension(line1=g[4], line2=g[13], textPoint=(edge * 45.9153861999512,
                                                               edge * 22.8469543457031), value=90.0)
        s.ObliqueDimension(vertex1=v[31], vertex2=v[32], textPoint=(edge * 45.8178939819336,
                                                                    edge * 22.4253730773926), value=edge)
        s.Spot(point=(edge * 45.3087692260742, edge * 21.387638092041))
        s.Line(point1=(edge * 46.3660254037844, edge * 22.1339745962156), point2=(edge * 45.3087692260742,
                                                                                  edge * 21.387638092041))
        s.Line(point1=(edge * 45.3087692260742, edge * 21.387638092041), point2=(edge * 45.0, edge * 22.5))
        s.AngularDimension(line1=g[15], line2=g[14], textPoint=(edge * 45.4387588500977,
                                                                edge * 21.6903095245361), value=90.0)
        s.AngularDimension(line1=g[13], line2=g[14], textPoint=(edge * 46.1537017822266,
                                                                edge * 22.1983680725098), value=90.0)
        s.Spot(point=(edge * 44.431339263916, edge * 21.9173145294189))
        s.Line(point1=(edge * 45.0, edge * 22.5), point2=(edge * 44.431339263916, edge * 21.9173145294189))
        s.AngularDimension(line1=g[6], line2=g[16], textPoint=(edge * 44.7454795837402,
                                                               edge * 22.3821353912354), value=90.0)
        s.ObliqueDimension(vertex1=v[39], vertex2=v[40], textPoint=(edge * 44.5071678161621,
                                                                    edge * 22.3497047424316), value=edge)
        s.Spot(point=(edge * 43.2289352416992, edge * 22.1659393310547))
        s.Line(point1=(edge * 44.5, edge * 21.6339745962156), point2=(edge * 43.2289352416992,
                                                                      edge * 22.1659393310547))
        s.Line(point1=(edge * 43.2289352416992, edge * 22.1659393310547), point2=(edge * 44.1339745962156,
                                                                                  edge * 23.0))
        s.AngularDimension(line1=g[18], line2=g[17], textPoint=(edge * 43.4455833435059,
                                                                edge * 22.2091789245605), value=90.0)
        s.AngularDimension(line1=g[17], line2=g[16], textPoint=(edge * 44.4205055236816,
                                                                edge * 21.8740768432617), value=90.0)
        s.Line(point1=(edge * 44.5, edge * 21.6339745962156), point2=(edge * 45.5, edge * 21.6339745962156))
        s.HorizontalConstraint(entity=g[19], addUndoState=False)
        s.delete(objectList=(d[14],))
        s.Spot(point=(edge * 43.5105781555176, edge * 21.6362609863281))
        s.Line(point1=(edge * 43.6339745962156, edge * 22.1339745962156), point2=(edge * 43.5105781555176,
                                                                                  edge * 21.6362609863281))
        s.AngularDimension(line1=g[20], line2=g[17], textPoint=(edge * 43.7705574035645,
                                                                edge * 21.8632659912109), value=60.0)
        s.ObliqueDimension(vertex1=v[49], vertex2=v[50], textPoint=(edge * 43.3805885314941,
                                                                    edge * 21.8200283050537), value=edge * 0.5)
        s.Spot(point=(edge * 43.6838989257813, edge * 24.317081451416))
        s.Line(point1=(edge * 43.6339745962156, edge * 23.8660254037844), point2=(edge * 43.6838989257813,
                                                                                  edge * 24.317081451416))
        s.AngularDimension(line1=g[21], line2=g[8], textPoint=(edge * 43.8030548095703,
                                                               edge * 24.1116943359375), value=60.0)
        s.ObliqueDimension(vertex1=v[52], vertex2=v[53], textPoint=(edge * 43.3589248657227,
                                                                    edge * 24.0576457977295), value=edge * 0.5)
        s.Spot(point=(edge * 43.4997482299805, edge * 23.0199108123779))
        s.Line(point1=(edge * 44.1339745962156, edge * 23.0), point2=(edge * 43.4997482299805,
                                                                      edge * 23.0199108123779))
        s.AngularDimension(line1=g[22], line2=g[18], textPoint=(edge * 43.8788833618164,
                                                                edge * 22.814525604248), value=60.0)
        s.ObliqueDimension(vertex1=v[55], vertex2=v[56], textPoint=(edge * 43.5539093017578,
                                                                    edge * 23.3658218383789), value=edge * 0.5)
        s.Spot(point=(edge * 46.4786758422852, edge * 22.998291015625))
        s.Line(point1=(edge * 45.8660254037844, edge * 23.0), point2=(edge * 46.4786758422852,
                                                                      edge * 22.998291015625))
        s.AngularDimension(line1=g[23], line2=g[13], textPoint=(edge * 46.0887069702148,
                                                                edge * 22.8793830871582), value=60.0)
        s.ObliqueDimension(vertex1=v[58], vertex2=v[59], textPoint=(edge * 46.4245147705078,
                                                                    edge * 23.268533706665), value=edge * 0.5)
        p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR,
                                       type=DEFORMABLE_BODY)
        p = mdb.models['Model-1'].parts['Part-1']
        p.BaseWire(sketch=s)
        s.unsetPrimaryObject()
        p = mdb.models['Model-1'].parts['Part-1']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        del mdb.models['Model-1'].sketches['__profile__']

    if structure == 'g':
        s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                                    sheetSize=200.0)
        g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
        s.setPrimaryObject(option=STANDALONE)
        s.Spot(point=(edge*25.0, edge*10.0))
        s.Spot(point=(edge*30.0, edge*10.0))
        s.Line(point1=(edge*25.0, edge*10.0), point2=(edge*30.0, edge*10.0))
        s.HorizontalConstraint(entity=g[2], addUndoState=False)
        s.ObliqueDimension(vertex1=v[2], vertex2=v[3], textPoint=(edge*27.3458099365234,
                                                                  edge*12.7896881103516), value=edge)
        s.Spot(point=(edge*29.4940586090088, edge*9.61226367950439))
        s.Line(point1=(edge*30.0, edge*10.0), point2=(edge*29.4940586090088, edge*9.61226367950439))
        s.Line(point1=(edge*29.4940586090088, edge*9.61226367950439), point2=(edge*29.0, edge*10.0))
        s.AngularDimension(line1=g[2], line2=g[4], textPoint=(edge*29.2078590393066,
                                                              edge*9.89786338806152), value=60.0)
        s.AngularDimension(line1=g[2], line2=g[3], textPoint=(edge*29.7405071258545,
                                                              edge*9.92166328430176), value=60.0)
        s.Spot(point=(edge*30.6468067169189, edge*9.90579605102539))
        s.Line(point1=(edge*30.0, edge*10.0), point2=(edge*30.6468067169189, edge*9.90579605102539))
        s.HorizontalConstraint(entity=g[5])
        s.ObliqueDimension(vertex1=v[10], vertex2=v[11], textPoint=(edge*30.320858001709,
                                                                    edge*9.78679656982422), value=0.5*edge)
        s.Spot(point=(edge*28.3174591064453, edge*10.0961961746216))
        s.Line(point1=(edge*28.3174591064453, edge*10.0961961746216), point2=(edge*29.0, edge*10.0))
        s.HorizontalConstraint(entity=g[6])
        s.ObliqueDimension(vertex1=v[13], vertex2=v[14], textPoint=(edge*28.6990585327148,
                                                                    edge*9.79472923278809), value=0.5*edge)
        s.Spot(point=(edge*30.3466510772705, edge*10.7745780944824))
        s.Line(point1=(edge*30.0, edge*10.0), point2=(edge*30.3466510772705, edge*10.7745780944824))
        s.AngularDimension(line1=g[7], line2=g[5], textPoint=(edge*30.1891174316406,
                                                              edge*10.1050138473511), value=60.0)
        s.ObliqueDimension(vertex1=v[16], vertex2=v[17], textPoint=(edge*30.066593170166,
                                                                    edge*10.4892854690552), value=edge)
        s.Spot(point=(edge*28.61962890625, edge*10.8793792724609))
        s.Line(point1=(edge*29.0, edge*10.0), point2=(edge*28.61962890625, edge*10.8793792724609))
        s.AngularDimension(line1=g[8], line2=g[6], textPoint=(edge*28.7946643829346,
                                                              edge*10.128303527832), value=60.0)
        s.ObliqueDimension(vertex1=v[19], vertex2=v[20], textPoint=(edge*28.5729522705078,
                                                                    edge*10.3437280654907), value=edge)
        s.Spot(point=(edge*28.9228687286377, edge*11.6237344741821))
        s.Line(point1=(edge*28.5, edge*10.8660254037844), point2=(edge*28.9228687286377,
                                                        edge*11.6237344741821))
        s.AngularDimension(line1=g[9], line2=g[8], textPoint=(edge*28.6901092529297,
                                                              edge*10.8283767700195), value=120.0)
        s.ObliqueDimension(vertex1=v[22], vertex2=v[23], textPoint=(edge*28.5490417480469,
                                                                    edge*11.3421926498413), value=edge)
        s.Spot(point=(edge*30.2841663360596, edge*11.7222747802734))
        s.Line(point1=(edge*30.5, edge*10.8660254037844), point2=(edge*30.2841663360596,
                                                        edge*11.7222747802734))
        s.AngularDimension(line1=g[7], line2=g[10], textPoint=(edge*30.3264865875244,
                                                               edge*10.8776473999023), value=120.0)
        s.ObliqueDimension(vertex1=v[25], vertex2=v[26], textPoint=(edge*30.0937252044678,
                                                                    edge*11.1521511077881), value=edge)
        s.Line(point1=(edge*29.0, edge*11.7320508075688), point2=(edge*30.0, edge*11.7320508075688))
        s.HorizontalConstraint(entity=g[11], addUndoState=False)
        s.delete(objectList=(d[12],))
        s.Spot(point=(edge*28.5631484985352, edge*11.6026191711426))
        s.Line(point1=(edge*29.0, edge*11.7320508075688), point2=(edge*28.5631484985352,
                                                        edge*11.6026191711426))
        s.HorizontalConstraint(entity=g[12])
        s.ObliqueDimension(vertex1=v[30], vertex2=v[31], textPoint=(edge*28.7637672424316, edge*11.6482591629028), value=0.5*edge)
        s.Spot(point=(edge*30.6245670318604, edge*11.6456441879272))
        s.Line(point1=(edge*30.0, edge*11.7320508075688), point2=(edge*30.6245670318604,
                                                        edge*11.6456441879272))
        s.HorizontalConstraint(entity=g[13])
        s.ObliqueDimension(vertex1=v[33], vertex2=v[34], textPoint=(edge*30.3310317993164,
                                                                    edge*11.6508750915527), value=0.5*edge)
        s.Spot(point=(edge*29.4585571289063, edge*12.0890169143677))
        s.Line(point1=(edge*29.4585571289063, edge*12.0890169143677), point2=(edge*30.0,
                                                                    edge*11.7320508075688))
        s.AngularDimension(line1=g[14], line2=g[11], textPoint=(edge*29.7822399139404,
                                                                edge*11.7817687988281), value=60.0)
        s.ObliqueDimension(vertex1=v[36], vertex2=v[37], textPoint=(edge*29.7480278015137,
                                                                    edge*11.9708442687988), value=edge)
        s.Line(point1=(edge*29.5, edge*12.5980762113532), point2=(edge*29.0, edge*11.7320508075688))

        p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR,
                                       type=DEFORMABLE_BODY)
        p = mdb.models['Model-1'].parts['Part-1']
        p.BaseWire(sketch=s)
        s.unsetPrimaryObject()
        p = mdb.models['Model-1'].parts['Part-1']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        del mdb.models['Model-1'].sketches['__profile__']

    # Bounce
    if structure == 'h':
        mdb.models.changeKey(fromName='Model-1', toName='Model-1')
        session.viewports['Viewport: 1'].setValues(displayedObject=None)
        s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                                    sheetSize=200.0)
        g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
        s.setPrimaryObject(option=STANDALONE)
        s.Spot(point=(edge * 47.5, edge * 35.0))
        s.Spot(point=(edge * 45.0, edge * 30.0))
        s.Spot(point=(edge * 50.0, edge * 30.0))
        s.Spot(point=(edge * 45.0, edge * 25.0))
        s.Spot(point=(edge * 50.0, edge * 25.0))
        s.Spot(point=(edge * 47.5, edge * 20.0))
        s.Line(point1=(edge * 45.0, edge * 25.0), point2=(edge * 45.0, edge * 30.0))
        s.VerticalConstraint(entity=g[2], addUndoState=False)
        s.Line(point1=(edge * 45.0, edge * 30.0), point2=(edge * 47.5, edge * 35.0))
        s.Line(point1=(edge * 47.5, edge * 35.0), point2=(edge * 50.0, edge * 30.0))
        s.Line(point1=(edge * 50.0, edge * 30.0), point2=(edge * 50.0, edge * 25.0))
        s.VerticalConstraint(entity=g[5], addUndoState=False)
        s.Line(point1=(edge * 50.0, edge * 25.0), point2=(edge * 47.5, edge * 20.0))
        s.Line(point1=(edge * 47.5, edge * 20.0), point2=(edge * 45.0, edge * 25.0))
        s.Line(point1=(edge * 45.0, edge * 30.0), point2=(edge * 50.0, edge * 30.0))
        s.HorizontalConstraint(entity=g[8], addUndoState=False)
        s.Line(point1=(edge * 45.0, edge * 25.0), point2=(edge * 50.0, edge * 25.0))
        s.HorizontalConstraint(entity=g[9], addUndoState=False)
        s.ObliqueDimension(vertex1=v[6], vertex2=v[7], textPoint=(edge * 43.3270835876465,
                                                                  edge * 27.537712097168), value=edge)
        s.ObliqueDimension(vertex1=v[8], vertex2=v[9], textPoint=(edge * 44.6553268432617,
                                                                  edge * 30.3415641784668), value=edge)
        s.ObliqueDimension(vertex1=v[10], vertex2=v[11], textPoint=(edge * 48.2824516296387,
                                                                    edge * 28.7102317810059), value=edge)
        s.ObliqueDimension(vertex1=v[14], vertex2=v[15], textPoint=(edge * 47.8226776123047,
                                                                    edge * 22.8986129760742), value=edge)
        s.ObliqueDimension(vertex1=v[16], vertex2=v[17], textPoint=(edge * 44.7161979675293,
                                                                    edge * 24.3010540008545), value=edge)
        s.ObliqueDimension(vertex1=v[20], vertex2=v[21], textPoint=(edge * 45.2375106811523,
                                                                    edge * 25.2971286773682), value=edge)
        s.Spot(point=(edge * 46.5862312316895, edge * 24.7652835845947))
        s.Spot(point=(edge * 46.1076545715332, edge * 23.8426952362061))
        s.Spot(point=(edge * 44.8241958618164, edge * 23.7450103759766))
        s.Spot(point=(edge * 44.2803535461426, edge * 24.6350364685059))
        s.Spot(point=(edge * 44.323860168457, edge * 26.3282566070557))
        s.Spot(point=(edge * 44.9003295898438, edge * 27.1857204437256))
        s.Spot(point=(edge * 46.1729164123535, edge * 27.1965751647949))
        s.Spot(point=(edge * 46.6623687744141, edge * 26.3282566070557))
        s.Line(point1=(edge * 45.0, edge * 25.0), point2=(edge * 44.2803535461426, edge * 24.6350364685059))
        s.Line(point1=(edge * 44.2803535461426, edge * 24.6350364685059), point2=(edge * 44.8241958618164,
                                                                                  edge * 23.7450103759766))
        s.Line(point1=(edge * 44.8241958618164, edge * 23.7450103759766), point2=(edge * 45.5,
                                                                                  edge * 24.1339745962156))
        s.Line(point1=(edge * 45.5, edge * 24.1339745962156), point2=(edge * 46.1076545715332,
                                                                      edge * 23.8426952362061))
        s.Line(point1=(edge * 46.1076545715332, edge * 23.8426952362061), point2=(edge * 46.5862312316895,
                                                                                  edge * 24.7652835845947))
        s.Line(point1=(edge * 46.5862312316895, edge * 24.7652835845947), point2=(edge * 46.0, edge * 25.0))
        s.Line(point1=(edge * 45.0, edge * 26.0), point2=(edge * 44.323860168457, edge * 26.3282566070557))
        s.Line(point1=(edge * 44.323860168457, edge * 26.3282566070557), point2=(edge * 44.9003295898438,
                                                                                 edge * 27.1857204437256))
        s.Line(point1=(edge * 44.9003295898438, edge * 27.1857204437256), point2=(edge * 45.5,
                                                                                  edge * 26.8660254037844))
        s.Line(point1=(edge * 45.5, edge * 26.8660254037844), point2=(edge * 46.1729164123535,
                                                                      edge * 27.1965751647949))
        s.Line(point1=(edge * 46.1729164123535, edge * 27.1965751647949), point2=(edge * 46.6623687744141,
                                                                                  edge * 26.3282566070557))
        s.Line(point1=(edge * 46.6623687744141, edge * 26.3282566070557), point2=(edge * 46.0, edge * 26.0))
        s.AngularDimension(line1=g[10], line2=g[11], textPoint=(edge * 44.3927917480469,
                                                                edge * 24.5817852020264), value=90.0)
        s.AngularDimension(line1=g[11], line2=g[12], textPoint=(edge * 44.8614616394043,
                                                                edge * 23.8919429779053), value=90.0)
        s.AngularDimension(line1=g[10], line2=g[7], textPoint=(edge * 45.0137825012207,
                                                               edge * 24.8974761962891), value=90.0)
        s.ObliqueDimension(vertex1=v[30], vertex2=v[31], textPoint=(edge * 44.4923820495605,
                                                                    edge * 24.9676284790039), value=edge)
        s.AngularDimension(line1=g[15], line2=g[14], textPoint=(edge * 46.4900970458984,
                                                                edge * 24.7162456512451), value=90.0)
        s.AngularDimension(line1=g[13], line2=g[14], textPoint=(edge * 46.0741539001465,
                                                                edge * 24.0030193328857), value=90.0)
        s.AngularDimension(line1=g[13], line2=g[6], textPoint=(edge * 45.6347732543945,
                                                               edge * 24.2368640899658), value=90.0)
        s.ObliqueDimension(vertex1=v[36], vertex2=v[37], textPoint=(edge * 45.6582069396973,
                                                                    edge * 23.7691745758057), value=edge)
        s.AngularDimension(line1=g[19], line2=g[20], textPoint=(edge * 46.1500434875488,
                                                                edge * 27.127779006958), value=90.0)
        s.AngularDimension(line1=g[20], line2=g[21], textPoint=(edge * 46.5798606872559,
                                                                edge * 26.3327121734619), value=90.0)
        s.AngularDimension(line1=g[4], line2=g[21], textPoint=(edge * 46.0504493713379,
                                                               edge * 26.0685615539551), value=90.0)
        s.ObliqueDimension(vertex1=v[52], vertex2=v[53], textPoint=(edge * 46.3964042663574,
                                                                    edge * 26.0502548217773), value=edge)
        s.AngularDimension(line1=g[16], line2=g[17], textPoint=(edge * 44.408447265625,
                                                                edge * 26.3664321899414), value=90.0)
        s.AngularDimension(line1=g[17], line2=g[18], textPoint=(edge * 44.9307289123535,
                                                                edge * 27.1211700439453), value=90.0)
        s.AngularDimension(line1=g[3], line2=g[18], textPoint=(edge * 45.4062042236328,
                                                               edge * 26.8605766296387), value=90.0)
        s.ObliqueDimension(vertex1=v[46], vertex2=v[47], textPoint=(edge * 45.14013671875,
                                                                    edge * 26.8679523468018), value=edge)
        s.Spot(point=(edge * 44.1605949401855, edge * 27.2073268890381))
        s.Spot(point=(edge * 44.6507415771484, edge * 27.5763092041016))
        s.Spot(point=(edge * 46.3490447998047, edge * 27.60205078125))
        s.Spot(point=(edge * 46.8176918029785, edge * 27.3617839813232))
        s.Line(point1=(edge * 44.1605949401855, edge * 27.2073268890381), point2=(edge * 44.6339745962156,
                                                                                  edge * 27.3660254037844))
        s.Line(point1=(edge * 44.6339745962156, edge * 27.3660254037844), point2=(edge * 44.6507415771484,
                                                                                  edge * 27.5763092041016))
        s.AngularDimension(line1=g[22], line2=g[17], textPoint=(edge * 44.4572639465332,
                                                                edge * 27.2244873046875), value=60.0)
        s.ObliqueDimension(vertex1=v[58], vertex2=v[59], textPoint=(edge * 44.2207908630371,
                                                                    edge * 27.2116165161133), value=edge * 0.5)
        s.AngularDimension(line1=g[23], line2=g[22], textPoint=(edge * 44.5475540161133,
                                                                edge * 27.4132690429688), value=90.0)
        s.ObliqueDimension(vertex1=v[60], vertex2=v[61], textPoint=(edge * 44.7625274658203,
                                                                    edge * 27.4690456390381), value=edge * 0.5)
        s.Line(point1=(edge * 46.3490447998047, edge * 27.60205078125), point2=(edge * 46.3660254037844,
                                                                                edge * 27.3660254037844))
        s.Line(point1=(edge * 46.3660254037844, edge * 27.3660254037844), point2=(edge * 46.8176918029785,
                                                                                  edge * 27.3617839813232))
        s.AngularDimension(line1=g[25], line2=g[20], textPoint=(edge * 46.486629486084,
                                                                edge * 27.2545223236084), value=60.0)
        s.AngularDimension(line1=g[24], line2=g[25], textPoint=(edge * 46.4436340332031,
                                                                edge * 27.4132690429688), value=90.0)
        s.ObliqueDimension(vertex1=v[64], vertex2=v[65], textPoint=(edge * 46.6973075866699,
                                                                    edge * 27.1086444854736), value=edge * 0.5)
        s.ObliqueDimension(vertex1=v[62], vertex2=v[63], textPoint=(edge * 46.2544593811035,
                                                                    edge * 27.4947891235352), value=edge * 0.5)
        s.Spot(point=(edge * 44.1319313049316, edge * 23.6154727935791))
        s.Spot(point=(edge * 44.620231628418, edge * 23.068775177002))
        s.Spot(point=(edge * 46.8354415893555, edge * 23.6273574829102))
        s.Spot(point=(edge * 46.3650054931641, edge * 23.1103706359863))
        s.Line(point1=(edge * 44.1319313049316, edge * 23.6154727935791), point2=(edge * 44.6339745962156,
                                                                                  edge * 23.6339745962156))
        s.Line(point1=(edge * 44.6339745962156, edge * 23.6339745962156), point2=(edge * 44.620231628418,
                                                                                  edge * 23.068775177002))
        s.Line(point1=(edge * 46.8354415893555, edge * 23.6273574829102), point2=(edge * 46.3660254037844,
                                                                                  edge * 23.6339745962156))
        s.Line(point1=(edge * 46.3660254037844, edge * 23.6339745962156), point2=(edge * 46.3650054931641,
                                                                                  edge * 23.1103706359863))
        s.AngularDimension(line1=g[26], line2=g[11], textPoint=(edge * 44.4813232421875,
                                                                edge * 23.7532444000244), value=60.0)
        s.ObliqueDimension(vertex1=v[70], vertex2=v[71], textPoint=(edge * 44.306510925293,
                                                                    edge * 23.4872150421143), value=edge * 0.5)
        s.AngularDimension(line1=g[27], line2=g[26], textPoint=(edge * 44.5337677001953,
                                                                edge * 23.5482711791992), value=90.0)
        s.ObliqueDimension(vertex1=v[72], vertex2=v[73], textPoint=(edge * 44.7653923034668,
                                                                    edge * 23.3258533477783), value=edge * 0.5)
        s.AngularDimension(line1=g[28], line2=g[14], textPoint=(edge * 46.5135154724121,
                                                                edge * 23.7532444000244), value=60.0)
        s.ObliqueDimension(vertex1=v[74], vertex2=v[75], textPoint=(edge * 46.6271438598633,
                                                                    edge * 23.4654102325439), value=edge * 0.5)
        s.AngularDimension(line1=g[29], line2=g[28], textPoint=(edge * 46.4654426574707,
                                                                edge * 23.5657157897949), value=90.0)
        s.ObliqueDimension(vertex1=v[76], vertex2=v[77], textPoint=(edge * 46.2294464111328,
                                                                    edge * 23.3127708435059), value=edge * 0.5)
        p = mdb.models['Model-1'].Part(name='Part_1',
                                       dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
        p = mdb.models['Model-1'].parts['Part_1']
        p.BaseWire(sketch=s)
        s.unsetPrimaryObject()
        p = mdb.models['Model-1'].parts['Part_1']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        del mdb.models['Model-1'].sketches['__profile__']

    if structure == 'i':
        s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                                              sheetSize=200.0)
        g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
        s1.setPrimaryObject(option=STANDALONE)
        s1.Spot(point=(30.0, 30.0))
        s1.Spot(point=(35.0, 30.0))
        s1.Spot(point=(32.5, 35.0))
        s1.Spot(point=(30.0, 25.0))
        s1.Spot(point=(35.0, 25.0))
        s1.Spot(point=(32.5, 20.0))
        s1.Spot(point=(30.0, 20.0))
        s1.Spot(point=(35.0, 20.0))
        s1.Spot(point=(32.5, 17.5))
        s1.Spot(point=(35.0, 35.0))
        s1.Spot(point=(30.0, 35.0))
        s1.Spot(point=(32.5, 37.5))
        s1.Line(point1=(35.0, 30.0), point2=(32.5, 35.0))
        s1.Line(point1=(32.5, 35.0), point2=(30.0, 30.0))
        s1.Line(point1=(30.0, 30.0), point2=(30.0, 25.0))
        s1.VerticalConstraint(entity=g[4], addUndoState=False)
        s1.Line(point1=(30.0, 25.0), point2=(32.5, 20.0))
        s1.Line(point1=(32.5, 20.0), point2=(35.0, 25.0))
        s1.Line(point1=(35.0, 25.0), point2=(30.0, 25.0))
        s1.HorizontalConstraint(entity=g[7], addUndoState=False)
        s1.Line(point1=(30.0, 30.0), point2=(35.0, 30.0))
        s1.HorizontalConstraint(entity=g[8], addUndoState=False)
        s1.Line(point1=(32.5, 35.0), point2=(30.0, 35.0))
        s1.HorizontalConstraint(entity=g[9], addUndoState=False)
        s1.Line(point1=(32.5, 37.5), point2=(32.5, 35.0))
        s1.VerticalConstraint(entity=g[10], addUndoState=False)
        s1.Line(point1=(32.5, 35.0), point2=(35.0, 35.0))
        s1.HorizontalConstraint(entity=g[11], addUndoState=False)
        s1.PerpendicularConstraint(entity1=g[10], entity2=g[11], addUndoState=False)
        s1.Line(point1=(30.0, 20.0), point2=(32.5, 20.0))
        s1.HorizontalConstraint(entity=g[12], addUndoState=False)
        s1.Line(point1=(32.5, 20.0), point2=(32.5, 17.5))
        s1.VerticalConstraint(entity=g[13], addUndoState=False)
        s1.PerpendicularConstraint(entity1=g[12], entity2=g[13], addUndoState=False)
        s1.Line(point1=(32.5, 20.0), point2=(35.0, 20.0))
        s1.HorizontalConstraint(entity=g[14], addUndoState=False)
        s1.ObliqueDimension(vertex1=v[16], vertex2=v[17], textPoint=(28.5407028198242,
                                                                     27.4260063171387), value=edge)
        s1.ObliqueDimension(vertex1=v[28], vertex2=v[29], textPoint=(31.6618881225586,
                                                                     32.0797729492188), value=0.5*edge)
        s1.ObliqueDimension(vertex1=v[30], vertex2=v[31], textPoint=(34.0949020385742,
                                                                     32.1991767883301), value=0.5*edge)
        s1.ObliqueDimension(vertex1=v[26], vertex2=v[27], textPoint=(30.9838333129883,
                                                                     32.1195755004883), value=0.5*edge)
        s1.ObliqueDimension(vertex1=v[36], vertex2=v[37], textPoint=(33.7758178710938,
                                                                     19.263557434082), value=0.5*edge)
        s1.ObliqueDimension(vertex1=v[34], vertex2=v[35], textPoint=(31.4225730895996,
                                                                     18.5869235992432), value=0.5*edge)
        s1.ObliqueDimension(vertex1=v[32], vertex2=v[33], textPoint=(30.9838333129883,
                                                                     18.2287063598633), value=0.5*edge)
        s1.ObliqueDimension(vertex1=v[22], vertex2=v[23], textPoint=(32.3294982910156,
                                                                     24.3677749633789), value=edge)
        s1.ObliqueDimension(vertex1=v[20], vertex2=v[21], textPoint=(32.4945907592773,
                                                                     23.2694492340088), value=edge)
        s1.ObliqueDimension(vertex1=v[18], vertex2=v[19], textPoint=(29.3853015899658,
                                                                     23.077241897583), value=edge)
        s1.ObliqueDimension(vertex1=v[24], vertex2=v[25], textPoint=(44.1129112243652,
                                                                     2.4116268157959), value=edge)
        s1.ObliqueDimension(vertex1=v[12], vertex2=v[13], textPoint=(43.9024353027344,
                                                                     4.40695905685425), value=edge)
        s1.ObliqueDimension(vertex1=v[14], vertex2=v[15], textPoint=(41.67138671875,
                                                                     3.9028754234314), value=edge)
        p = mdb.models['Model-1'].Part(name='Part-1',
                                                dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
        p = mdb.models['Model-1'].parts['Part-1']
        p.BaseWire(sketch=s1)
        s1.unsetPrimaryObject()
        p = mdb.models['Model-1'].parts['Part-1']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        del mdb.models['Model-1'].sketches['__profile__']

    # TODO create j: Mapple Leaf Structure
    # If the user somehow does manage to select the mapple leaf letter "j"
    # the script will recall the main() file to query the user for new inputs.
    # This should never happen but adds an additional layer of savety
    if structure == 'j':
        getWarningReply('The chosen strucutre is not yet available.\n'
                        'Please choose one of the following structures: \n'
                        "'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'\n"
                        , buttons=(YES,))
        main()

    if structure == 'k':
        s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                                    sheetSize=200.0)
        g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
        s.setPrimaryObject(option=STANDALONE)
        s.Spot(point=(edge * 45.0, edge * 30.0))
        s.Spot(point=(edge * 47.5, edge * 30.0))
        s.Line(point1=(edge * 45.0, edge * 30.0), point2=(edge * 47.5, edge * 30.0))
        s.HorizontalConstraint(entity=g[2], addUndoState=False)
        session.viewports['Viewport: 1'].view.setValues(nearPlane=182.913,
                                                        farPlane=194.211, width=37.0648, height=19.089, cameraPosition=(
                45.4831, 28.1021, 188.562), cameraTarget=(45.4831, 28.1021, 0))
        s.ObliqueDimension(vertex1=v[2], vertex2=v[3], textPoint=(edge * 45.9745216369629,
                                                                  edge * 31.0617179870605), value=edge)
        s.Spot(point=(edge * 47.5, edge * 28.75))
        s.Line(point1=(edge * 47.5, edge * 30.0), point2=(edge * 47.5, edge * 28.75))
        s.VerticalConstraint(entity=g[3], addUndoState=False)
        s.ObliqueDimension(vertex1=v[5], vertex2=v[6], textPoint=(edge * 48.5016708374023,
                                                                  edge * 29.4155120849609), value=edge)
        s.Spot(point=(edge * 46.25, edge * 28.75))
        s.Line(point1=(edge * 46.5, edge * 30.0), point2=(edge * 46.25, edge * 28.75))
        s.Line(point1=(edge * 46.25, edge * 28.75), point2=(edge * 47.5, edge * 29.0))
        session.viewports['Viewport: 1'].view.setValues(nearPlane=186.035,
                                                        farPlane=191.089, width=16.5815, height=8.53975,
                                                        cameraPosition=(
                                                            46.2356, 28.76, 188.562), cameraTarget=(46.2356, 28.76, 0))
        s.AngularDimension(line1=g[4], line2=g[5], textPoint=(edge * 46.5967636108398,
                                                              edge * 29.0028839111328), value=90.0)
        s.AngularDimension(line1=g[2], line2=g[4], textPoint=(edge * 46.6752777099609,
                                                              edge * 29.8020153045654), value=90.0)
        s.Spot(point=(edge * 45.9372711181641, edge * 28.3604431152344))
        s.Line(point1=(edge * 46.5, edge * 29.0), point2=(edge * 45.9372711181641, edge * 28.3604431152344))
        s.AngularDimension(line1=g[6], line2=g[5], textPoint=(edge * 46.643871307373,
                                                              edge * 28.7991828918457), value=130.0)
        s.ObliqueDimension(vertex1=v[13], vertex2=v[14], textPoint=(edge * 45.8430595397949,
                                                                    edge * 29.0498905181885), value=edge)
        s.Spot(point=(edge * 48.1983871459961, edge * 28.2194194793701))
        s.Line(point1=(edge * 47.5, edge * 29.0), point2=(edge * 48.1983871459961, edge * 28.2194194793701))
        s.AngularDimension(line1=g[5], line2=g[7], textPoint=(edge * 47.397575378418,
                                                              edge * 28.8148517608643), value=130.0)
        s.ObliqueDimension(vertex1=v[16], vertex2=v[17], textPoint=(edge * 48.2769012451172,
                                                                    edge * 28.8618602752686), value=edge)
        s.Spot(point=(edge * 46.4868507385254, edge * 27.3576107025146))
        s.Line(point1=(edge * 45.8572123903135, edge * 28.233955556881), point2=(edge * 46.4868507385254,
                                                                                 edge * 27.3576107025146))
        s.AngularDimension(line1=g[6], line2=g[8], textPoint=(edge * 46.1256980895996,
                                                              edge * 28.188081741333), value=120.0)
        session.viewports['Viewport: 1'].view.setValues(nearPlane=187.359,
                                                        farPlane=189.765, width=7.89148, height=4.06424,
                                                        cameraPosition=(
                                                            46.7667, 28.4079, 188.562),
                                                        cameraTarget=(46.7667, 28.4079, 0))
        s.delete(objectList=(d[4],))
        s.delete(objectList=(d[6],))
        s.AngularDimension(line1=g[5], line2=g[6], textPoint=(edge * 46.4901695251465,
                                                              edge * 28.8665142059326), value=120.0)
        s.AngularDimension(line1=g[5], line2=g[7], textPoint=(edge * 47.4616584777832,
                                                              edge * 28.8366851806641), value=120.0)
        s.ObliqueDimension(vertex1=v[19], vertex2=v[20], textPoint=(edge * 46.4004936218262,
                                                                    edge * 27.9045181274414), value=edge)
        s.Spot(point=(edge * 47.603645324707, edge * 27.2855606079102))
        s.Line(point1=(edge * 48.0, edge * 28.1339745962156), point2=(edge * 47.603645324707,
                                                                      edge * 27.2855606079102))
        s.AngularDimension(line1=g[7], line2=g[9], textPoint=(edge * 47.8427810668945,
                                                              edge * 28.09840965271), value=120.0)
        s.ObliqueDimension(vertex1=v[22], vertex2=v[23], textPoint=(edge * 47.5737533569336,
                                                                    edge * 27.8970623016357), value=edge)
        s.Line(point1=(edge * 46.5, edge * 27.2679491924311), point2=(edge * 47.5, edge * 27.2679491924312))
        s.HorizontalConstraint(entity=g[10], addUndoState=False)
        s.delete(objectList=(d[13],))
        s.Spot(point=(edge * 45.294490814209, edge * 27.8523178100586))
        s.Line(point1=(edge * 46.0, edge * 28.1339745962156), point2=(edge * 45.294490814209,
                                                                      edge * 27.8523178100586))
        s.AngularDimension(line1=g[11], line2=g[8], textPoint=(edge * 45.9969520568848,
                                                               edge * 27.9418048858643), value=90.0)
        s.ObliqueDimension(vertex1=v[27], vertex2=v[28], textPoint=(edge * 45.8624382019043,
                                                                    edge * 27.7329998016357), value=edge)
        s.Spot(point=(edge * 45.7503433227539, edge * 27.2557315826416))
        s.Line(point1=(edge * 45.1339745962156, edge * 27.6339745962156), point2=(edge * 45.7503433227539,
                                                                                  edge * 27.2557315826416))
        s.Line(point1=(edge * 45.7503433227539, edge * 27.2557315826416), point2=(edge * 46.5,
                                                                                  edge * 27.2679491924311))
        s.AngularDimension(line1=g[12], line2=g[13], textPoint=(edge * 45.8474922180176,
                                                                edge * 27.3601341247559), value=90.0)
        s.AngularDimension(line1=g[8], line2=g[13], textPoint=(edge * 46.2883987426758,
                                                               edge * 27.4123363494873), value=90.0)
        s.Spot(point=(edge * 48.851634979248, edge * 28.01637840271))
        s.Line(point1=(edge * 48.0, edge * 28.1339745962156), point2=(edge * 48.851634979248,
                                                                      edge * 28.01637840271))
        s.AngularDimension(line1=g[14], line2=g[9], textPoint=(edge * 47.9922409057617,
                                                               edge * 28.01637840271), value=9.0)
        s.undo()
        s.AngularDimension(line1=g[9], line2=g[14], textPoint=(edge * 48.0893898010254,
                                                               edge * 28.0611228942871), value=90.0)
        s.ObliqueDimension(vertex1=v[35], vertex2=v[36], textPoint=(edge * 48.2164306640625,
                                                                    edge * 27.7479152679443), value=edge)
        s.Spot(point=(edge * 48.1192817687988, edge * 27.4123363494873))
        s.Line(point1=(edge * 48.8660254037844, edge * 27.6339745962156), point2=(edge * 48.1192817687988,
                                                                                  edge * 27.4123363494873))
        s.Line(point1=(edge * 48.1192817687988, edge * 27.4123363494873), point2=(edge * 47.5,
                                                                                  edge * 27.2679491924312))
        s.AngularDimension(line1=g[15], line2=g[14], textPoint=(edge * 48.5004043579102,
                                                                edge * 27.6957130432129), value=90.0)
        s.AngularDimension(line1=g[9], line2=g[16], textPoint=(edge * 47.6559562683105,
                                                               edge * 27.3974208831787), value=90.0)
        session.viewports['Viewport: 1'].view.setValues(nearPlane=187.277,
                                                        farPlane=189.847, width=8.42954, height=4.34135,
                                                        cameraPosition=(
                                                            46.966, 31.6681, 188.562),
                                                        cameraTarget=(46.966, 31.6681, 0))
        s.Spot(point=(edge * 45.8564338684082, edge * 30.7320728302002))
        s.Line(point1=(edge * 46.5, edge * 30.0), point2=(edge * 45.8564338684082, edge * 30.7320728302002))
        s.AngularDimension(line1=g[17], line2=g[2], textPoint=(edge * 46.5988082885742,
                                                               edge * 30.1585369110107), value=120.0)
        s.ObliqueDimension(vertex1=v[43], vertex2=v[44], textPoint=(edge * 46.4631042480469,
                                                                    edge * 30.5329284667969), value=edge)
        s.Spot(point=(edge * 47.9239044189453, edge * 30.9630813598633))
        s.Line(point1=(edge * 47.5, edge * 30.0), point2=(edge * 47.9239044189453, edge * 30.9630813598633))
        s.AngularDimension(line1=g[2], line2=g[18], textPoint=(edge * 47.4609184265137,
                                                               edge * 30.1665019989014), value=120.0)
        s.ObliqueDimension(vertex1=v[46], vertex2=v[47], textPoint=(edge * 47.5088157653809,
                                                                    edge * 30.5568256378174), value=edge)
        s.Spot(point=(edge * 46.4471397399902, edge * 31.6003437042236))
        s.Line(point1=(edge * 46.0, edge * 30.8660254037844), point2=(edge * 46.4471397399902,
                                                                      edge * 31.6003437042236))
        s.AngularDimension(line1=g[17], line2=g[19], textPoint=(edge * 46.1597671508789,
                                                                edge * 30.8754577636719), value=120.0)
        s.ObliqueDimension(vertex1=v[49], vertex2=v[50], textPoint=(edge * 46.415210723877,
                                                                    edge * 31.0507049560547), value=edge)
        s.Spot(point=(edge * 47.5407447814941, edge * 31.5206851959229))
        s.Line(point1=(edge * 48.0, edge * 30.8660254037844), point2=(edge * 47.5407447814941,
                                                                      edge * 31.5206851959229))
        s.Line(point1=(edge * 47.5407447814941, edge * 31.5206851959229), point2=(edge * 46.5,
                                                                                  edge * 31.7320508075688))
        s.AngularDimension(line1=g[20], line2=g[18], textPoint=(edge * 47.8520660400391,
                                                                edge * 30.8356285095215), value=120.0)
        s.AngularDimension(line1=g[21], line2=g[20], textPoint=(edge * 47.5646934509277,
                                                                edge * 31.3613700866699), value=120.0)
        s.Spot(point=(edge * 45.3535346984863, edge * 31.0347728729248))
        s.Line(point1=(edge * 46.0, edge * 30.8660254037844), point2=(edge * 45.3535346984863,
                                                                      edge * 31.0347728729248))
        s.AngularDimension(line1=g[22], line2=g[19], textPoint=(edge * 45.9202919006348,
                                                                edge * 31.0188407897949), value=90.0)
        s.ObliqueDimension(vertex1=v[57], vertex2=v[58], textPoint=(edge * 45.8644142150879,
                                                                    edge * 31.2737464904785), value=edge)
        s.Spot(point=(edge * 45.4493255615234, edge * 32.4606475830078))
        s.Line(point1=(edge * 45.1339745962156, edge * 31.3660254037844), point2=(edge * 45.4493255615234,
                                                                                  edge * 32.4606475830078))
        s.Line(point1=(edge * 45.4493255615234, edge * 32.4606475830078), point2=(edge * 46.5,
                                                                                  edge * 31.7320508075688))
        s.AngularDimension(line1=g[23], line2=g[24], textPoint=(edge * 45.5530967712402,
                                                                edge * 32.2296409606934), value=90.0)
        s.AngularDimension(line1=g[24], line2=g[19], textPoint=(edge * 46.3752975463867,
                                                                edge * 31.6720352172852), value=90.0)
        s.Spot(point=(edge * 48.1234703063965, edge * 31.9986324310303))
        s.Line(point1=(edge * 47.5, edge * 31.7320508075689), point2=(edge * 48.1234703063965,
                                                                      edge * 31.9986324310303))
        s.AngularDimension(line1=g[25], line2=g[20], textPoint=(edge * 47.6285514831543,
                                                                edge * 31.6800003051758), value=90.0)
        s.ObliqueDimension(vertex1=v[65], vertex2=v[66], textPoint=(edge * 47.9079399108887,
                                                                    edge * 31.6322059631348), value=edge)
        s.Spot(point=(edge * 49.1053199768066, edge * 31.456958770752))
        s.Line(point1=(edge * 48.3660254037844, edge * 32.2320508075689), point2=(edge * 49.1053199768066,
                                                                                  edge * 31.456958770752))
        s.Line(point1=(edge * 49.1053199768066, edge * 31.456958770752), point2=(edge * 48.0,
                                                                                 edge * 30.8660254037844))
        s.AngularDimension(line1=g[25], line2=g[26], textPoint=(edge * 48.4028587341309,
                                                                edge * 32.0782890319824), value=90.0)
        s.AngularDimension(line1=g[26], line2=g[27], textPoint=(edge * 48.7540893554688,
                                                                edge * 31.3773021697998), value=90.0)
        s.Spot(point=(edge * 45.2497596740723, edge * 32.9943542480469))
        s.Line(point1=(edge * 45.6339745962156, edge * 32.2320508075688), point2=(edge * 45.2497596740723,
                                                                                  edge * 32.9943542480469))
        s.AngularDimension(line1=g[28], line2=g[23], textPoint=(edge * 45.3934478759766,
                                                                edge * 32.237606048584), value=120.0)
        s.ObliqueDimension(vertex1=v[73], vertex2=v[74], textPoint=(edge * 45.2417793273926,
                                                                    edge * 32.4367523193359), value=edge)
        s.Spot(point=(edge * 45.1459884643555, edge * 33.5917892456055))
        s.Line(point1=(edge * 45.1339745962156, edge * 33.0980762113532), point2=(edge * 45.1459884643555,
                                                                                  edge * 33.5917892456055))
        s.AngularDimension(line1=g[29], line2=g[28], textPoint=(edge * 45.2816925048828,
                                                                edge * 33.0899467468262), value=150.0)
        s.ObliqueDimension(vertex1=v[76], vertex2=v[77], textPoint=(edge * 45.3934478759766,
                                                                    edge * 33.2731590270996), value=edge * 0.5)
        s.Spot(point=(edge * 44.6830024719238, edge * 32.9784240722656))
        s.Line(point1=(edge * 45.1339745962156, edge * 33.0980762113532), point2=(edge * 44.6830024719238,
                                                                                  edge * 32.9784240722656))
        s.AngularDimension(line1=g[29], line2=g[30], textPoint=(edge * 45.0501976013184,
                                                                edge * 33.2014656066895), value=90.0)
        s.ObliqueDimension(vertex1=v[79], vertex2=v[80], textPoint=(edge * 44.8985290527344,
                                                                    edge * 32.874870300293), value=edge * 0.5)
        s.Spot(point=(edge * 44.7069511413574, edge * 31.2179851531982))
        s.Line(point1=(edge * 45.1339745962156, edge * 31.3660254037844), point2=(edge * 44.7069511413574,
                                                                                  edge * 31.2179851531982))
        s.AngularDimension(line1=g[23], line2=g[31], textPoint=(edge * 45.0182685852051,
                                                                edge * 31.4410285949707), value=120.0)
        s.ObliqueDimension(vertex1=v[82], vertex2=v[83], textPoint=(edge * 44.8825645446777,
                                                                    edge * 31.1781578063965), value=edge * 0.5)
        s.Spot(point=(edge * 48.8179473876953, edge * 32.9943542480469))
        s.Line(point1=(edge * 48.3660254037844, edge * 32.2320508075689), point2=(edge * 48.8179473876953,
                                                                                  edge * 32.9943542480469))
        s.AngularDimension(line1=g[32], line2=g[26], textPoint=(edge * 48.5625076293945,
                                                                edge * 32.1659126281738), value=120.0)
        s.ObliqueDimension(vertex1=v[85], vertex2=v[86], textPoint=(edge * 48.7620697021484,
                                                                    edge * 32.4765815734863), value=edge)
        s.Spot(point=(edge * 48.75, edge * 33.75))
        s.Line(point1=(edge * 48.8660254037844, edge * 33.0980762113533), point2=(edge * 48.75, edge * 33.75))
        s.AngularDimension(line1=g[33], line2=g[32], textPoint=(edge * 48.7461051940918,
                                                                edge * 33.0819778442383), value=150.0)
        s.ObliqueDimension(vertex1=v[88], vertex2=v[89], textPoint=(edge * 48.6263694763184,
                                                                    edge * 33.4484062194824), value=edge * 0.5)
        s.Spot(point=(edge * 49.3447952270508, edge * 33.0341835021973))
        s.Line(point1=(edge * 48.8660254037844, edge * 33.0980762113533), point2=(edge * 49.3447952270508,
                                                                                  edge * 33.0341835021973))
        s.AngularDimension(line1=g[33], line2=g[34], textPoint=(edge * 49.0494422912598,
                                                                edge * 33.1775703430176), value=90.0)
        s.ObliqueDimension(vertex1=v[91], vertex2=v[92], textPoint=(edge * 49.08935546875,
                                                                    edge * 32.8509712219238), value=edge * 0.5)
        s.Spot(point=(edge * 49.4086570739746, edge * 31.2259521484375))
        s.Line(point1=(edge * 48.8660254037844, edge * 31.3660254037844), point2=(edge * 49.4086570739746,
                                                                                  edge * 31.2259521484375))
        s.AngularDimension(line1=g[26], line2=g[35], textPoint=(edge * 48.9696159362793,
                                                                edge * 31.4410285949707), value=120.0)
        s.ObliqueDimension(vertex1=v[94], vertex2=v[95], textPoint=(edge * 49.1053199768066,
                                                                    edge * 31.1861228942871), value=edge * 0.5)
        session.viewports['Viewport: 1'].view.setValues(nearPlane=186.91,
                                                        farPlane=190.214, width=12.269, height=6.31875, cameraPosition=(
                46.9014, 26.7204, 188.562), cameraTarget=(46.9014, 26.7204, 0))
        s.Spot(point=(edge * 45.205135345459, edge * 25.9146366119385))
        s.Line(point1=(edge * 45.6339745962156, edge * 26.7679491924311), point2=(edge * 45.205135345459,
                                                                                  edge * 25.9146366119385))
        s.AngularDimension(line1=g[12], line2=g[36], textPoint=(edge * 45.4026489257813,
                                                                edge * 26.6798439025879), value=120.0)
        s.ObliqueDimension(vertex1=v[97], vertex2=v[98], textPoint=(edge * 45.7279624938965,
                                                                    edge * 26.2856464385986), value=edge)
        s.Spot(point=(edge * 45.0773315429688, edge * 25.3697185516357))
        s.Line(point1=(edge * 45.1339745962156, edge * 25.9019237886467), point2=(edge * 45.0773315429688,
                                                                                  edge * 25.3697185516357))
        s.AngularDimension(line1=g[36], line2=g[37], textPoint=(edge * 45.2516098022461,
                                                                edge * 25.8102912902832), value=150.0)
        s.ObliqueDimension(vertex1=v[100], vertex2=v[101], textPoint=(edge * 45.4491195678711,
                                                                      edge * 25.636381149292), value=edge * 0.5)
        s.Spot(point=(edge * 44.5545043945313, edge * 25.7175388336182))
        s.Line(point1=(edge * 45.1339745962156, edge * 25.9019237886467), point2=(edge * 44.5545043945313,
                                                                                  edge * 25.7175388336182))
        s.AngularDimension(line1=g[38], line2=g[37], textPoint=(edge * 45.0192413330078,
                                                                edge * 25.7407264709473), value=90.0)
        s.ObliqueDimension(vertex1=v[103], vertex2=v[104], textPoint=(edge * 44.7984924316406,
                                                                      edge * 25.5668163299561), value=edge * 0.5)
        s.Spot(point=(edge * 44.7055435180664, edge * 27.4682388305664))
        s.Line(point1=(edge * 45.1339745962156, edge * 27.6339745962156), point2=(edge * 44.7055435180664,
                                                                                  edge * 27.4682388305664))
        s.AngularDimension(line1=g[39], line2=g[12], textPoint=(edge * 45.0540962219238,
                                                                edge * 27.4334564208984), value=120.0)
        s.ObliqueDimension(vertex1=v[106], vertex2=v[107], textPoint=(edge * 44.8565826416016,
                                                                      edge * 27.931999206543), value=edge * 0.5)
        s.Spot(point=(edge * 48.8649291992188, edge * 25.8450736999512))
        s.Line(point1=(edge * 48.3660254037844, edge * 26.7679491924312), point2=(edge * 48.8649291992188,
                                                                                  edge * 25.8450736999512))
        s.AngularDimension(line1=g[15], line2=g[40], textPoint=(edge * 48.5744705200195,
                                                                edge * 26.7494087219238), value=120.0)
        s.ObliqueDimension(vertex1=v[109], vertex2=v[110], textPoint=(edge * 48.2956275939941,
                                                                      edge * 26.2044887542725), value=edge)
        s.Spot(point=(edge * 48.8997840881348, edge * 25.3233413696289))
        s.Line(point1=(edge * 48.8660254037844, edge * 25.9019237886468), point2=(edge * 48.8997840881348,
                                                                                  edge * 25.3233413696289))
        s.AngularDimension(line1=g[40], line2=g[41], textPoint=(edge * 48.7022705078125,
                                                                edge * 25.8218860626221), value=150.0)
        s.ObliqueDimension(vertex1=v[112], vertex2=v[113], textPoint=(edge * 48.5396156311035,
                                                                      edge * 25.5552215576172), value=edge * 0.5)
        s.Spot(point=(edge * 49.4109954833984, edge * 25.7755088806152))
        s.Line(point1=(edge * 48.8660254037844, edge * 25.9019237886468), point2=(edge * 49.4109954833984,
                                                                                  edge * 25.7755088806152))
        s.AngularDimension(line1=g[42], line2=g[41], textPoint=(edge * 49.0043487548828,
                                                                edge * 25.7871036529541), value=90.0)
        s.ObliqueDimension(vertex1=v[115], vertex2=v[116], textPoint=(edge * 49.2018623352051,
                                                                      edge * 25.5900039672852), value=edge * 0.5)
        s.Spot(point=(edge * 49.3296661376953, edge * 27.7812767028809))
        s.Line(point1=(edge * 48.8660254037844, edge * 27.6339745962156), point2=(edge * 49.3296661376953,
                                                                                  edge * 27.7812767028809))
        s.AngularDimension(line1=g[43], line2=g[15], textPoint=(edge * 48.8765487670898,
                                                                edge * 27.4914264678955), value=120.0)
        s.ObliqueDimension(vertex1=v[118], vertex2=v[119], textPoint=(edge * 49.132152557373,
                                                                      edge * 28.0015640258789), value=edge * 0.5)
        p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR,
                                       type=DEFORMABLE_BODY)
        p = mdb.models['Model-1'].parts['Part-1']
        p.BaseWire(sketch=s)
        s.unsetPrimaryObject()
        p = mdb.models['Model-1'].parts['Part-1']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        del mdb.models['Model-1'].sketches['__profile__']


'''
The material selection is pretty straight forward. The user can choose between linear and nonlinear
materials using either:
- Young Modulus
- Poisson Rate
for the linear model or
- c10
- c01
- d1
for the non-linear Mooney-Rivlin material model.
We have limited the material choices to Mooney-Rivlin material depending on Coefficients and for a 
Instantaneous time scale for the viscoelasticity. 
Future studies might yield different results using the "Test data" input sources or "Long-term" time scales.
'''
def select_material():

    # Define all possible return statements as None
    young_modulus = None
    poisson_rate = None
    c10 = None
    c01 = None
    d1 = None

    # Query the user
    model = str(getInput("You can choose from the following material models\n"
                               "'linear', 'nonlinear'\n"
                               "Please enter the desired material model: ", "linear")).lower()

    # Query the user for additional information regarding the material
    # Offers values for quick tries
    if model == 'linear':
        fields = (('Young Modulus [MPa]:', '210000'), ('Poisson Rate:', '0.3'))
        young_modulus, poisson_rate = getInputs(fields=fields, label='Specify Material dimensions:',
                                                dialogTitle='Create Material', )
    elif model == 'nonlinear':
        fields = (('c10 [MPa]:', '0.3339'), ('c01 [MPa]:', '-0.000337'), ('d1:', '0.0015828'))
        c10, c01, d1 = getInputs(fields=fields, label='Specify Material dimensions:',
                                                dialogTitle='Create Material', )
    else:
        getWarningReply('The chosen value is not available.\n'
                        'Please choose one of the following material models: \n'
                        "'linear', 'nonlinear'\n"
                        , buttons=(YES,))
        section = select_material()

    return model, young_modulus, poisson_rate, c10, c01, d1


'''
This function assigns the selected model to the previously built structure
It does not require the structure model as input as all functions are executed inside the Abaqus program.
'''
def create_material(model, young_modulus, poisson_rate, c10, c01, d1):
    if model == 'linear':
        mdb.models['Model-1'].Material(name='Material-1')
        mdb.models['Model-1'].materials['Material-1'].Elastic(table=((float(young_modulus), float(poisson_rate)),))

    elif model == 'nonlinear':
        mdb.models['Model-1'].Material(name='Material-1')
        mdb.models['Model-1'].materials['Material-1'].Hyperelastic(
            materialType=ISOTROPIC, testData=OFF, type=MOONEY_RIVLIN,
            moduliTimeScale=INSTANTANEOUS, volumetricResponse=VOLUMETRIC_DATA,
            table=((float(c10), float(c01), float(d1)),))

'''
The cross section selection has very different required inputs for varying cross sections.
Once the user chooses a certain cross section from the possible choices he has to decide the parameters for the section.
Sadly we have not been able the reproduce the helpful GUI used in abaqus to view which parameter correponds to 
which dimension. 
We strongly recommend to get aquainted with the Abaqus cross sections so the user can enter the desired dimensions.
'''
def select_cross_section(edge, structure):
    # definition of list for structure geometries which require certain catches
    triangle_structures = ['b', 'c','e', 'f', 'g', 'h', 'i', 'j']
    quad_structures = ['a', 'd', 'k']
    width = None
    width_2 = None
    height = None
    radius = None
    d = None
    thickness = None
    thickness_2 = None
    thickness_3 = None
    i = None

    section = str(getInput("You can choose from the following cross sections\n"
                           "'box', 'pipe', 'circular', 'rectangular', 'hexagonal', 'trapezoidal', 'I', 'L', 'T'\n"
                           "Please enter the desired cross section profile: ", "circular")).lower()

    if section == 'box':
        fields = (('Width [mm]:', '5'), ('Height [mm]:', '5'), ('Thickness [mm]:', '1'))
        width, height, thickness = getInputs(fields=fields, label='Specify cross section dimensions:',
                                                dialogTitle='Create Cross Section', )
        if float(thickness) >= float(width)/2.0 or float(thickness) >= float(height)/2.0:
            getWarningReply(
                'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                , buttons=(YES,))
            section = select_cross_section(edge, structure)
        if structure in quad_structures:
            if float(width) >= float(edge) / 2.0 or float(height) >= float(edge) / 2.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)
        if structure in triangle_structures:
            if float(width) >= float(edge)/3.0 or float(height) >= float(edge)/3.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)

    if section == 'circular':
        radius = str(getInput("Specify cross section dimensions:", "2"))

        if structure in quad_structures:
            if float(radius) >= float(edge)/2.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)
        if structure in triangle_structures:
            if float(radius) >= float(edge)/3.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)

    if section == 'pipe':
        fields = (('Radius [mm]:', '5'), ('Thickness [mm]:', '1'))
        radius, thickness = getInputs(fields=fields, label='Specify cross section dimensions:',
                                                dialogTitle='Create Cross Section', )
        if thickness >= radius:
            getWarningReply(
                'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                , buttons=(YES,))
            section = select_cross_section(edge, structure)
        if structure in quad_structures:
            if float(radius) >= float(edge)/2.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)

        if structure in triangle_structures:
            if float(radius) >= float(edge)/3.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)

    if section == 'rectangular':
        fields = (('Width [mm]:', '5'), ('Height [mm]:', '3'))
        width, height = getInputs(fields=fields, label='Specify cross section dimensions:',
                                                dialogTitle='Create Cross Section', )
        if structure in quad_structures:
            if float(width) >= float(edge)/2.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)
            if float(height) >= float(edge) / 2.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)

        if structure in triangle_structures:
            if float(width) >= float(edge)/3.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)
            if float(height) >= float(edge) / 3.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)

    if section == 'hexagonal':
        fields = (('Radius [mm]:', '5'), ('Thickness [mm]:', '1'))
        radius, thickness = getInputs(fields=fields, label='Specify cross section dimensions:',
                                                dialogTitle='Create Cross Section', )
        if thickness >= radius:
            getWarningReply(
                'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                , buttons=(YES,))
            section = select_cross_section(edge, structure)
        if structure in quad_structures:
            if float(radius) >= float(edge)/2.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)

        if structure in triangle_structures:
            if float(radius) >= float(edge)/3.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)

    if section == 'trapezoidal':
        fields = (('Width [mm]:', '5'), ('Height [mm]:', '3'), ('Width small [mm]:', '2'), ('Offset [mm]:', '1'))
        width, height, width_2, d = getInputs(fields=fields, label='Specify cross section dimensions:',
                                                dialogTitle='Create Cross Section', )
        if structure in quad_structures:
            if float(width) >= float(edge)/2.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)
            if float(height) >= float(edge) / 2.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)

        if structure in triangle_structures:
            if float(width) >= float(edge)/3.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)
            if float(height) >= float(edge) / 3.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)

    if section == 'i':
        fields = (('Offset [mm]:', '2'), ('Height [mm]:', '4'), ('Width [mm]:', '3'),('Width top [mm]:', '3'),
                  ('Thickness bottom [mm]:', '1'), ('Thickness top [mm]:', '1'), ('Thickness mid [mm]:', '1'))
        i, height, width, width_2, thickness, thickness_2, thickness_3 = getInputs(fields=fields,
                                                                         label='Specify cross section dimensions:',
                                                                         dialogTitle='Create Cross Section', )
        if structure in quad_structures:
            if float(width) >= float(edge)/2.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)
            if float(width_2) >= float(edge) / 2.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)
            if float(height) >= float(edge) / 2.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)

        if structure in triangle_structures:
            if float(width) >= float(edge)/3.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)
            if float(width_2) >= float(edge) / 3.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)
            if float(height) >= float(edge) / 3.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)

    if section == 'l':
        fields = (('Width [mm]:', '5'), ('Height [mm]:', '5'), ('Thickness bottom [mm]:', '1'), ('Thickness top [mm]:', '1'))
        width, height, thickness, thickness_2 = getInputs(fields=fields, label='Specify cross section dimensions:',
                                                dialogTitle='Create Cross Section', )
        if structure in quad_structures:
            if float(width) >= float(edge) / 2.0 or float(height) >= float(edge) / 2.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)

        if structure in triangle_structures:
            if float(width) >= float(edge)/3.0 or float(height) >= float(edge)/3.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)

    if section == 't':
        fields = (('Width [mm]:', '5'), ('Height [mm]:', '5'),('Offset [mm]:', '2'), ('Thickness top [mm]:', '1'), ('Thickness bottom [mm]:', '1'))
        width, height, i, thickness, thickness_2 = getInputs(fields=fields, label='Specify cross section dimensions:',
                                                dialogTitle='Create Cross Section', )
        if structure in quad_structures:
            if float(width) >= float(edge) / 2.0 or float(height) >= float(edge) / 2.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)
        if structure in triangle_structures:
            if float(width) >= float(edge) / 3.0 or float(height) >= float(edge) / 3.0:
                getWarningReply(
                    'The radius/width/height/thickness is too large (in relation to the edge size)\n'
                    , buttons=(YES,))
                section = select_cross_section(edge, structure)

    return section, width, width_2, height, radius, d, thickness, thickness_2, thickness_3, i


'''
Depending on the users choices this function creates the cross section for the beams in the selected structure.
'''
def create_cross_section(section, width, width_2, height, radius, d, thickness, thickness_2, thickness_3, i):
    if section == 'box':
        mdb.models['Model-1'].BoxProfile(name='Profile-1', b=float(width), a=float(height),
                                                 uniformThickness=ON, t1=float(thickness))
    if section == 'circular':
        mdb.models['Model-1'].CircularProfile(name='Profile-1', r=float(radius))
    if section == 'pipe':
        mdb.models['Model-1'].PipeProfile(name='Profile-1', r=float(radius), t=float(thickness))
    if section == 'rectangular':
        mdb.models['Model-1'].RectangularProfile(name='Profile-1', a=float(width), b=float(height))
    if section == 'hexagonal':
        mdb.models['Model-1'].HexagonalProfile(name='Profile-1', r=float(radius), t=float(thickness))
    if section == 'trapezoidal':
        mdb.models['Model-1'].TrapezoidalProfile(name='Profile-1', a=float(width), b=float(height),
                                                 c=float(width_2), d=float(d))
    if section == 'i':
        mdb.models['Model-1'].IProfile(name='Profile-1', l=float(i), h=float(height), b1=float(width),
                                       b2=float(width_2), t1=float(thickness), t2=float(thickness_2),
                                       t3=float(thickness_3))
    if section == 't':
        mdb.models['Model-1'].TProfile(name='Profile-1', b=float(width), h=float(height), l=float(i),
                                       tf=float(thickness), tw=float(thickness_2))
    if section == 'l':
        mdb.models['Model-1'].LProfile(name='Profile-1', a=float(width), b=float(height), t1=float(thickness),
                                       t2=float(thickness_2))

    mdb.models['Model-1'].BeamSection(name='Section-1', integration=DURING_ANALYSIS, poissonRatio=0.0,
                                      profile='Profile-1', material='Material-1', temperatureVar=LINEAR,
                                      consistentMassMatrix=False)
    p = mdb.models['Model-1'].parts['Part-1']
    e = p.edges
    edges = e.getSequenceFromMask(mask=('[#ffffffff #3ff ]',), )
    region = p.Set(edges=edges, name='Set-1')
    p = mdb.models['Model-1'].parts['Part-1']
    p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0,
                        offsetType=MIDDLE_SURFACE, offsetField='',
                        thicknessAssignment=FROM_SECTION)
    p = mdb.models['Model-1'].parts['Part-1']
    e = p.edges
    edges = e.getSequenceFromMask(mask=('[#ffffffff #3ff ]',), )
    region = p.Set(edges=edges, name='Set-2')
    p = mdb.models['Model-1'].parts['Part-1']
    p.assignBeamSectionOrientation(region=region, method=N1_COSINES, n1=(0.0, 0.0,
                                                                         -1.0))

'''
Simple function to mesh the model with a size of 0.1 times the selected edge size to ensure proper meshes even for very
small or very large lattices.
'''
def create_mesh(edge):
    p = mdb.models['Model-1'].parts['Part-1']
    p.seedPart(size=0.1*edge, deviationFactor=0.1, minSizeFactor=0.1)
    p.generateMesh()

# Self explanatory
def create_assembly():
    a = mdb.models['Model-1'].rootAssembly
    a.DatumCsysByDefault(CARTESIAN)
    p = mdb.models['Model-1'].parts['Part-1']
    a.Instance(name='Part-1-1', part=p, dependent=ON)

# Self explanatory
def create_step():
    mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial', initialInc=0.1)

'''
The user can select the load cases.
He/she can choose the axis of the force and the stress (uniaxial / shear)
Additionally the User can specify the Force
'''
def select_boundary_conditions():
    fields = (('Force [N]:', '1000'), ('Loadcase [uniaxial/shear]:', 'uniaxial'), ('Axis [x/y]:', 'x'))
    force, loadcase, axis = getInputs(fields=fields, label='Specify Loading Conditions:',
                                         dialogTitle='Create Loadcase', )


    return force, loadcase, axis

'''
This function applies the selected conditions to the selected lattice.

We have decided to use a macro which maps all possible forces, boundary conditions and equations onto the lattice
and in a second step we deactivate or suppress all conditions not used in the selected load case.
'''
def create_boundary_conditions(structure, force, loadcase, axis):

    # Square
    if structure == 'a':
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#4 ]',), )
        p.Set(vertices=verts, name='L1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#1 ]',), )
        p.Set(vertices=verts, name='R1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#10 ]',), )
        p.Set(vertices=verts, name='T1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#8 ]',), )
        p.Set(vertices=verts, name='B1')
        a1 = mdb.models['Model-1'].rootAssembly
        a1.regenerate()
        a = mdb.models['Model-1'].rootAssembly
        session.viewports['Viewport: 1'].setValues(displayedObject=a)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF, loads=ON,
                                                                   bcs=ON, predefinedFields=ON, connectors=ON)
        session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
            meshTechnique=OFF)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#10 ]',), )
        region = a.Set(vertices=verts1, name='Set-1')
        mdb.models['Model-1'].ConcentratedForce(name='Load-1', createStepName='Step-1',
                                                region=region, cf1=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#10 ]',), )
        region = a.Set(vertices=verts1, name='Set-2')
        mdb.models['Model-1'].ConcentratedForce(name='Load-2', createStepName='Step-1',
                                                region=region, cf2=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#8 ]',), )
        region = a.Set(vertices=verts1, name='Set-3')
        mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF,
                                                                   predefinedFields=OFF, interactions=ON,
                                                                   constraints=ON,
                                                                   engineeringFeatures=ON)
        mdb.models['Model-1'].Equation(name='Constraint-1', terms=((1.0, 'Part-1.L1',
                                                                    2), (-1.0, 'Part-1.R1', 2), (-1.0, 'Part-1.B1', 2)))


        if loadcase == 'uniaxial':
            mdb.models['Model-1'].constraints['Constraint-1'].suppress()
            session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                       predefinedFields=ON, interactions=OFF,
                                                                       constraints=OFF,
                                                                       engineeringFeatures=OFF)
            mdb.models['Model-1'].loads['Load-1'].suppress()

        if loadcase == 'shear':
            session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                       predefinedFields=ON, interactions=OFF,
                                                                       constraints=OFF,
                                                                       engineeringFeatures=OFF)
            mdb.models['Model-1'].loads['Load-2'].suppress()

    # Honeycomb
    if structure == 'b':
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#1 ]',), )
        region = a.Set(vertices=verts1, name='Set-1')
        mdb.models['Model-1'].ConcentratedForce(name='Load-1', createStepName='Step-1',
                                                region=region, cf1=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#1 ]',), )
        region = a.Set(vertices=verts1, name='Set-2')
        mdb.models['Model-1'].ConcentratedForce(name='Load-2', createStepName='Step-1',
                                                region=region, cf2=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#80 ]',), )
        region = a.Set(vertices=verts1, name='Set-3')
        mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#18 ]',), )
        region = a.Set(vertices=verts1, name='Set-4')
        mdb.models['Model-1'].ConcentratedForce(name='Load-3', createStepName='Step-1',
                                                region=region, cf1=-1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#18 ]',), )
        region = a.Set(vertices=verts1, name='Set-5')
        mdb.models['Model-1'].ConcentratedForce(name='Load-4', createStepName='Step-1',
                                                region=region, cf2=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#4 ]',), )
        region = a.Set(vertices=verts1, name='Set-6')
        mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#40 ]',), )
        region = a.Set(vertices=verts1, name='Set-7')
        mdb.models['Model-1'].DisplacementBC(name='BC-3', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=OFF,
                                                               engineeringFeatures=OFF)
        session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
            referenceRepresentation=ON)
        p1 = mdb.models['Model-1'].parts['Part-1']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#8 ]',), )
        p.Set(vertices=verts, name='L1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#10 ]',), )
        p.Set(vertices=verts, name='L2')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#4 ]',), )
        p.Set(vertices=verts, name='R1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#40 ]',), )
        p.Set(vertices=verts, name='R2')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#1 ]',), )
        p.Set(vertices=verts, name='T1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#80 ]',), )
        p.Set(vertices=verts, name='B1')
        a1 = mdb.models['Model-1'].rootAssembly
        a1.regenerate()
        a = mdb.models['Model-1'].rootAssembly
        session.viewports['Viewport: 1'].setValues(displayedObject=a)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF,
                                                                   predefinedFields=OFF, interactions=ON,
                                                                   constraints=ON,
                                                                   engineeringFeatures=ON)
        mdb.models['Model-1'].Equation(name='Constraint-1', terms=((1.0, 'Part-1-1.L1',
                                                                    2), (-1.0, 'Part-1-1.R1', 2),
                                                                   (-1.0, 'Part-1-1.B1', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-2', terms=((1.0, 'Part-1-1.L2',
                                                                    2), (-1.0, 'Part-1-1.R2', 2),
                                                                   (-1.0, 'Part-1-1.B1', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-3', terms=((1.0, 'Part-1-1.T1',
                                                                    1), (-1.0, 'Part-1-1.B1', 1),
                                                                   (-1.0, 'Part-1-1.R1', 1)))


        if loadcase == 'uniaxial':
            if axis == 'y':
                mdb.models['Model-1'].constraints['Constraint-3'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-2'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-3'].suppress()

            if axis == 'x':
                mdb.models['Model-1'].constraints['Constraint-1'].suppress()
                mdb.models['Model-1'].constraints['Constraint-2'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-1'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-3'].setValues(u2=UNSET, ur3=UNSET)

        if loadcase == 'shear':
            if axis == 'y':
                mdb.models['Model-1'].constraints['Constraint-1'].suppress()
                mdb.models['Model-1'].constraints['Constraint-2'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-1'].suppress()

            if axis == 'x':
                mdb.models['Model-1'].constraints['Constraint-3'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-2'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-3'].suppress()

    # Triangular
    if structure == 'c':
        session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=OFF,
                                                               engineeringFeatures=OFF)
        session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
            referenceRepresentation=ON)
        p1 = mdb.models['Model-1'].parts['Part-1']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#8 ]',), )
        p.Set(vertices=verts, name='L1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#10 ]',), )
        p.Set(vertices=verts, name='R1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#4 ]',), )
        p.Set(vertices=verts, name='T1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#2 ]',), )
        p.Set(vertices=verts, name='T2')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#1 ]',), )
        p.Set(vertices=verts, name='T3')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#20 ]',), )
        p.Set(vertices=verts, name='B1')
        a1 = mdb.models['Model-1'].rootAssembly
        a1.regenerate()
        a = mdb.models['Model-1'].rootAssembly
        session.viewports['Viewport: 1'].setValues(displayedObject=a)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#20 ]',), )
        region = a.Set(vertices=verts1, name='Set-1')
        mdb.models['Model-1'].ConcentratedForce(name='Load-1', createStepName='Step-1',
                                                region=region, cf1=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#20 ]',), )
        region = a.Set(vertices=verts1, name='Set-2')
        mdb.models['Model-1'].ConcentratedForce(name='Load-2', createStepName='Step-1',
                                                region=region, cf2=-1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#11 ]',), )
        region = a.Set(vertices=verts1, name='Set-3')
        mdb.models['Model-1'].ConcentratedForce(name='Load-3', createStepName='Step-1',
                                                region=region, cf1=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#11 ]',), )
        region = a.Set(vertices=verts1, name='Set-4')
        mdb.models['Model-1'].ConcentratedForce(name='Load-4', createStepName='Step-1',
                                                region=region, cf2=-1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#2 ]',), )
        region = a.Set(vertices=verts1, name='Set-5')
        mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#4 ]',), )
        region = a.Set(vertices=verts1, name='Set-6')
        mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#1 ]',), )
        region = a.Set(vertices=verts1, name='Set-7')
        mdb.models['Model-1'].DisplacementBC(name='BC-3', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#8 ]',), )
        region = a.Set(vertices=verts1, name='Set-8')
        mdb.models['Model-1'].DisplacementBC(name='BC-4', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF,
                                                                   predefinedFields=OFF, interactions=ON,
                                                                   constraints=ON,
                                                                   engineeringFeatures=ON)
        mdb.models['Model-1'].Equation(name='Constraint-1', terms=((1.0, 'Part-1-1.L1',
                                                                    2), (-1.0, 'Part-1-1.R1', 2),
                                                                   (-1.0, 'Part-1-1.T2', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-2', terms=((1.0, 'Part-1-1.T2',
                                                                    1), (-1.0, 'Part-1-1.B1', 1),
                                                                   (-1.0, 'Part-1-1.L1', 1)))

        if loadcase == 'uniaxial':
            if axis == 'y':
                mdb.models['Model-1'].constraints['Constraint-1'].suppress()
                mdb.models['Model-1'].constraints['Constraint-2'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-2'].setValues(u1=UNSET, ur3=UNSET)
                mdb.models['Model-1'].boundaryConditions['BC-3'].setValues(u1=UNSET, ur3=UNSET)

            if axis == 'x':
                mdb.models['Model-1'].constraints['Constraint-1'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-1'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-2'].setValues(u2=UNSET, ur3=UNSET)
                mdb.models['Model-1'].boundaryConditions['BC-3'].suppress()

        if loadcase == 'shear':
            if axis == 'y':
                mdb.models['Model-1'].constraints['Constraint-1'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-1'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-3'].suppress()

            if axis == 'x':
                mdb.models['Model-1'].constraints['Constraint-2'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-4'].suppress()





    # CaVo
    if structure == 'd':
        session.viewports['Viewport: 1'].view.setValues(nearPlane=858.195,
                                                        farPlane=878.817, width=69.9693, height=33.0268,
                                                        viewOffsetX=185.367,
                                                        viewOffsetY=61.5612)
        p1 = mdb.models['Model-1'].parts['Part-1']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=OFF,
                                                               engineeringFeatures=OFF, mesh=ON)
        session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
            meshTechnique=ON)
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#80 ]',), )
        p.Set(vertices=verts, name='L1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#40 ]',), )
        p.Set(vertices=verts, name='R1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#20 ]',), )
        p.Set(vertices=verts, name='T1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#1 ]',), )
        p.Set(vertices=verts, name='B1')
        a1 = mdb.models['Model-1'].rootAssembly
        a1.regenerate()
        a = mdb.models['Model-1'].rootAssembly
        session.viewports['Viewport: 1'].setValues(displayedObject=a)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF, loads=ON,
                                                                   bcs=ON, predefinedFields=ON, connectors=ON)
        session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
            meshTechnique=OFF)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#20 ]',), )
        region = a.Set(vertices=verts1, name='Set-1')
        mdb.models['Model-1'].ConcentratedForce(name='Load-1', createStepName='Step-1',
                                                region=region, cf1=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#20 ]',), )
        region = a.Set(vertices=verts1, name='Set-2')
        mdb.models['Model-1'].ConcentratedForce(name='Load-2', createStepName='Step-1',
                                                region=region, cf2=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#1 ]',), )
        region = a.Set(vertices=verts1, name='Set-3')
        mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF,
                                                                   predefinedFields=OFF, interactions=ON,
                                                                   constraints=ON,
                                                                   engineeringFeatures=ON)
        mdb.models['Model-1'].Equation(name='Constraint-1', terms=((1.0, 'Part-1-1.L1',
                                                                    2), (-1.0, 'Part-1-1.R1', 2),
                                                                   (-1.0, 'Part-1-1.B1', 2)))


        if loadcase == 'uniaxial':
            mdb.models['Model-1'].constraints['Constraint-1'].suppress()
            session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                       predefinedFields=ON, interactions=OFF,
                                                                       constraints=OFF,
                                                                       engineeringFeatures=OFF)
            mdb.models['Model-1'].loads['Load-1'].suppress()

        if loadcase == 'shear':
            session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                       predefinedFields=ON, interactions=OFF,
                                                                       constraints=OFF,
                                                                       engineeringFeatures=OFF)
            mdb.models['Model-1'].loads['Load-2'].suppress()

    # Star
    if structure == 'e':
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#100 ]',), )
        p.Set(vertices=verts, name='L1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#200 ]',), )
        p.Set(vertices=verts, name='L2')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#400 ]',), )
        p.Set(vertices=verts, name='L3')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#1000 ]',), )
        p.Set(vertices=verts, name='L4')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#10 ]',), )
        p.Set(vertices=verts, name='R1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#40 ]',), )
        p.Set(vertices=verts, name='R2')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#80000 ]',), )
        p.Set(vertices=verts, name='R3')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#40000 ]',), )
        p.Set(vertices=verts, name='R4')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#1 ]',), )
        p.Set(vertices=verts, name='T1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#20000 ]',), )
        p.Set(vertices=verts, name='B1')
        a1 = mdb.models['Model-1'].rootAssembly
        a1.regenerate()
        a = mdb.models['Model-1'].rootAssembly
        session.viewports['Viewport: 1'].setValues(displayedObject=a)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                   predefinedFields=ON, connectors=ON,
                                                                   adaptiveMeshConstraints=OFF)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#1 ]',), )
        region = a.Set(vertices=verts1, name='Set-1')
        mdb.models['Model-1'].ConcentratedForce(name='Load-1', createStepName='Step-1',
                                                region=region, cf2=float(force), distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#1 ]',), )
        region = a.Set(vertices=verts1, name='Set-2')
        mdb.models['Model-1'].ConcentratedForce(name='Load-2', createStepName='Step-1',
                                                region=region, cf1=float(force), distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#100 ]',), )
        region = a.Set(vertices=verts1, name='Set-3')
        mdb.models['Model-1'].ConcentratedForce(name='Load-3', createStepName='Step-1',
                                                region=region, cf1=-float(force), distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#200 ]',), )
        region = a.Set(vertices=verts1, name='Set-4')
        mdb.models['Model-1'].ConcentratedForce(name='Load-4', createStepName='Step-1',
                                                region=region, cf1=-float(force), distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#400 ]',), )
        region = a.Set(vertices=verts1, name='Set-5')
        mdb.models['Model-1'].ConcentratedForce(name='Load-5', createStepName='Step-1',
                                                region=region, cf1=-float(force), distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#1000 ]',), )
        region = a.Set(vertices=verts1, name='Set-6')
        mdb.models['Model-1'].ConcentratedForce(name='Load-6', createStepName='Step-1',
                                                region=region, cf1=-float(force), distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#20000 ]',), )
        region = a.Set(vertices=verts1, name='Set-7')
        mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#10 ]',), )
        region = a.Set(vertices=verts1, name='Set-8')
        mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#40 ]',), )
        region = a.Set(vertices=verts1, name='Set-9')
        mdb.models['Model-1'].DisplacementBC(name='BC-3', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#80000 ]',), )
        region = a.Set(vertices=verts1, name='Set-10')
        mdb.models['Model-1'].DisplacementBC(name='BC-4', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#40000 ]',), )
        region = a.Set(vertices=verts1, name='Set-11')
        mdb.models['Model-1'].DisplacementBC(name='BC-5', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF,
                                                                   predefinedFields=OFF, interactions=ON,
                                                                   constraints=ON,
                                                                   engineeringFeatures=ON)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#100 ]',), )
        region = a.Set(vertices=verts1, name='Set-12')
        mdb.models['Model-1'].ConcentratedForce(name='Load-7', createStepName='Step-1',
                                                region=region, cf2=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#200 ]',), )
        region = a.Set(vertices=verts1, name='Set-13')
        mdb.models['Model-1'].ConcentratedForce(name='Load-8', createStepName='Step-1',
                                                region=region, cf2=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#400 ]',), )
        region = a.Set(vertices=verts1, name='Set-14')
        mdb.models['Model-1'].ConcentratedForce(name='Load-9', createStepName='Step-1',
                                                region=region, cf2=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#1000 ]',), )
        region = a.Set(vertices=verts1, name='Set-15')
        mdb.models['Model-1'].ConcentratedForce(name='Load-10',
                                                createStepName='Step-1', region=region, cf2=1000.0,
                                                distributionType=UNIFORM, field='', localCsys=None)
        mdb.models['Model-1'].Equation(name='Constraint-1', terms=((1.0, 'Part-1-1.L1',
                                                                    1), (-1.0, 'Part-1-1.R1', 1),
                                                                   (-1.0, 'Part-1-1.B1', 1)))
        mdb.models['Model-1'].Equation(name='Constraint-2', terms=((1.0, 'Part-1-1.L1',
                                                                    2), (-1.0, 'Part-1-1.R1', 2),
                                                                   (-1.0, 'Part-1-1.B1', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-3', terms=((1.0, 'Part-1-1.L2',
                                                                    1), (-1.0, 'Part-1-1.R2', 1),
                                                                   (-1.0, 'Part-1-1.B1', 1)))
        mdb.models['Model-1'].Equation(name='Constraint-4', terms=((1.0, 'Part-1-1.L2',
                                                                    2), (-1.0, 'Part-1-1.R2', 2),
                                                                   (-1.0, 'Part-1-1.B1', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-5', terms=((1.0, 'Part-1-1.L3',
                                                                    1), (-1.0, 'Part-1-1.R3', 1),
                                                                   (-1.0, 'Part-1-1.B1', 1)))
        mdb.models['Model-1'].Equation(name='Constraint-6', terms=((1.0, 'Part-1-1.L3',
                                                                    2), (-1.0, 'Part-1-1.R3', 2),
                                                                   (-1.0, 'Part-1-1.B1', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-7', terms=((1.0, 'Part-1-1.L4',
                                                                    1), (-1.0, 'Part-1-1.R4', 1),
                                                                   (-1.0, 'Part-1-1.B1', 1)))
        mdb.models['Model-1'].Equation(name='Constraint-8', terms=((1.0, 'Part-1-1.L4',
                                                                    2), (-1.0, 'Part-1-1.R4', 2),
                                                                   (-1.0, 'Part-1-1.B1', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-9', terms=((1.0, 'Part-1-1.T1',
                                                                    1), (-1.0, 'Part-1-1.B1', 1),
                                                                   (-1.0, 'Part-1-1.R2', 1)))

        session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                   predefinedFields=ON, interactions=OFF,
                                                                   constraints=OFF,
                                                                   engineeringFeatures=OFF)

        if loadcase == 'uniaxial':
            if axis == 'y':
                mdb.models['Model-1'].constraints['Constraint-1'].suppress()
                mdb.models['Model-1'].constraints['Constraint-3'].suppress()
                mdb.models['Model-1'].constraints['Constraint-5'].suppress()
                mdb.models['Model-1'].constraints['Constraint-7'].suppress()
                mdb.models['Model-1'].constraints['Constraint-9'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-2'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-3'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-5'].suppress()
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].loads['Load-5'].suppress()
                mdb.models['Model-1'].loads['Load-6'].suppress()
                mdb.models['Model-1'].loads['Load-7'].suppress()
                mdb.models['Model-1'].loads['Load-8'].suppress()
                mdb.models['Model-1'].loads['Load-9'].suppress()
                mdb.models['Model-1'].loads['Load-10'].suppress()

            if axis == 'x':
                mdb.models['Model-1'].constraints['Constraint-1'].suppress()
                mdb.models['Model-1'].constraints['Constraint-2'].suppress()
                mdb.models['Model-1'].constraints['Constraint-3'].suppress()
                mdb.models['Model-1'].constraints['Constraint-4'].suppress()
                mdb.models['Model-1'].constraints['Constraint-5'].suppress()
                mdb.models['Model-1'].constraints['Constraint-6'].suppress()
                mdb.models['Model-1'].constraints['Constraint-7'].suppress()
                mdb.models['Model-1'].constraints['Constraint-8'].suppress()
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-7'].suppress()
                mdb.models['Model-1'].loads['Load-8'].suppress()
                mdb.models['Model-1'].loads['Load-9'].suppress()
                mdb.models['Model-1'].loads['Load-10'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-1'].suppress()

        if loadcase == 'shear':
            if axis == 'y':
                mdb.models['Model-1'].constraints['Constraint-9'].suppress()
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].loads['Load-5'].suppress()
                mdb.models['Model-1'].loads['Load-6'].suppress()
                mdb.models['Model-1'].loads['Load-7'].suppress()
                mdb.models['Model-1'].loads['Load-8'].suppress()
                mdb.models['Model-1'].loads['Load-9'].suppress()
                mdb.models['Model-1'].loads['Load-10'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-2'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-3'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-5'].suppress()

            if axis == 'x':
                mdb.models['Model-1'].constraints['Constraint-1'].suppress()
                mdb.models['Model-1'].constraints['Constraint-2'].suppress()
                mdb.models['Model-1'].constraints['Constraint-3'].suppress()
                mdb.models['Model-1'].constraints['Constraint-4'].suppress()
                mdb.models['Model-1'].constraints['Constraint-5'].suppress()
                mdb.models['Model-1'].constraints['Constraint-6'].suppress()
                mdb.models['Model-1'].constraints['Constraint-7'].suppress()
                mdb.models['Model-1'].constraints['Constraint-8'].suppress()
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].loads['Load-5'].suppress()
                mdb.models['Model-1'].loads['Load-6'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-1'].suppress()

    # SrCuBO
    if structure == 'f':
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#4000 ]',), )
        p.Set(vertices=verts, name='L1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#40 ]',), )
        p.Set(vertices=verts, name='L2')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#100 ]',), )
        p.Set(vertices=verts, name='L3')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#2 ]',), )
        p.Set(vertices=verts, name='L4')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#1 ]',), )
        p.Set(vertices=verts, name='L5')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#1000 ]',), )
        p.Set(vertices=verts, name='R1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#8000 ]',), )
        p.Set(vertices=verts, name='R2')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#400 ]',), )
        p.Set(vertices=verts, name='R3')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#80 ]',), )
        p.Set(vertices=verts, name='T1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#2000 ]',), )
        p.Set(vertices=verts, name='T2')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#8 ]',), )
        p.Set(vertices=verts, name='B1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#800 ]',), )
        p.Set(vertices=verts, name='B2')
        a1 = mdb.models['Model-1'].rootAssembly
        a1.regenerate()
        a = mdb.models['Model-1'].rootAssembly
        session.viewports['Viewport: 1'].setValues(displayedObject=a)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#6080 ]',), )
        region = a.Set(vertices=verts1, name='Set-1')
        mdb.models['Model-1'].ConcentratedForce(name='Load-1', createStepName='Step-1',
                                                region=region, cf1=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#6080 ]',), )
        region = a.Set(vertices=verts1, name='Set-2')
        mdb.models['Model-1'].ConcentratedForce(name='Load-2', createStepName='Step-1',
                                                region=region, cf2=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#9400 ]',), )
        region = a.Set(vertices=verts1, name='Set-3')
        mdb.models['Model-1'].ConcentratedForce(name='Load-3', createStepName='Step-1',
                                                region=region, cf1=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#9400 ]',), )
        region = a.Set(vertices=verts1, name='Set-4')
        mdb.models['Model-1'].ConcentratedForce(name='Load-4', createStepName='Step-1',
                                                region=region, cf2=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#4000 ]',), )
        region = a.Set(vertices=verts1, name='Set-5')
        mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#40 ]',), )
        region = a.Set(vertices=verts1, name='Set-6')
        mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#100 ]',), )
        region = a.Set(vertices=verts1, name='Set-7')
        mdb.models['Model-1'].DisplacementBC(name='BC-3', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#2 ]',), )
        region = a.Set(vertices=verts1, name='Set-8')
        mdb.models['Model-1'].DisplacementBC(name='BC-4', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#1 ]',), )
        region = a.Set(vertices=verts1, name='Set-9')
        mdb.models['Model-1'].DisplacementBC(name='BC-5', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#8 ]',), )
        region = a.Set(vertices=verts1, name='Set-10')
        mdb.models['Model-1'].DisplacementBC(name='BC-6', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#800 ]',), )
        region = a.Set(vertices=verts1, name='Set-11')
        mdb.models['Model-1'].DisplacementBC(name='BC-7', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF,
                                                                   predefinedFields=OFF, interactions=ON,
                                                                   constraints=ON,
                                                                   engineeringFeatures=ON)
        mdb.models['Model-1'].Equation(name='Constraint-1', terms=((1.0, 'Part-1-1.L2',
                                                                    2), (-1.0, 'Part-1-1.R1', 2),
                                                                   (-1.0, 'Part-1-1.B2', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-2', terms=((1.0, 'Part-1-1.L3',
                                                                    2), (-1.0, 'Part-1-1.R2', 2),
                                                                   (-1.0, 'Part-1-1.B2', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-3', terms=((1.0, 'Part-1-1.L4',
                                                                    2), (-1.0, 'Part-1-1.R3', 2),
                                                                   (-1.0, 'Part-1-1.B2', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-4', terms=((1.0, 'Part-1-1.B2',
                                                                    1), (-1.0, 'Part-1-1.T2', 1),
                                                                   (-1.0, 'Part-1-1.L3', 1)))
        mdb.models['Model-1'].Equation(name='Constraint-5', terms=((1.0, 'Part-1-1.B1',
                                                                    1), (-1.0, 'Part-1-1.T1', 1),
                                                                   (-1.0, 'Part-1-1.L3', 1)))


        if loadcase == 'uniaxial':
            if axis == 'y':
                mmdb.models['Model-1'].constraints['Constraint-4'].suppress()
                mdb.models['Model-1'].constraints['Constraint-5'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                    predefinedFields=ON, interactions=OFF, constraints=OFF,
                    engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-1'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-2'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-3'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-4'].suppress()

            if axis == 'x':
                mdb.models['Model-1'].constraints['Constraint-1'].suppress()
                mdb.models['Model-1'].constraints['Constraint-2'].suppress()
                mdb.models['Model-1'].constraints['Constraint-3'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-6'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-7'].suppress()

        if loadcase == 'shear':
            if axis == 'y':
                mdb.models['Model-1'].constraints['Constraint-1'].suppress()
                mdb.models['Model-1'].constraints['Constraint-2'].suppress()
                mdb.models['Model-1'].constraints['Constraint-3'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-6'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-7'].suppress()

            if axis == 'x':
                mdb.models['Model-1'].constraints['Constraint-5'].suppress()
                mdb.models['Model-1'].constraints['Constraint-4'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-1'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-2'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-3'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-4'].suppress()



    # Kagome
    if structure == 'g':
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#1 ]',), )
        p.Set(vertices=verts, name='L1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#4 ]',), )
        p.Set(vertices=verts, name='L2')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#10 ]',), )
        p.Set(vertices=verts, name='L3')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#200 ]',), )
        p.Set(vertices=verts, name='R1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#400 ]',), )
        p.Set(vertices=verts, name='R2')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#800 ]',), )
        p.Set(vertices=verts, name='R3')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#40 ]',), )
        p.Set(vertices=verts, name='T1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#100 ]',), )
        p.Set(vertices=verts, name='B1')
        a1 = mdb.models['Model-1'].rootAssembly
        a1.regenerate()
        a = mdb.models['Model-1'].rootAssembly
        session.viewports['Viewport: 1'].setValues(displayedObject=a)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF, loads=ON,
                                                                   bcs=ON, predefinedFields=ON, connectors=ON)
        session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
            meshTechnique=OFF)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#40 ]',), )
        region = a.Set(vertices=verts1, name='Set-1')
        mdb.models['Model-1'].ConcentratedForce(name='Load-1', createStepName='Step-1',
                                                region=region, cf1=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#40 ]',), )
        region = a.Set(vertices=verts1, name='Set-2')
        mdb.models['Model-1'].ConcentratedForce(name='Load-2', createStepName='Step-1',
                                                region=region, cf2=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#e00 ]',), )
        region = a.Set(vertices=verts1, name='Set-3')
        mdb.models['Model-1'].ConcentratedForce(name='Load-3', createStepName='Step-1',
                                                region=region, cf1=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#e00 ]',), )
        region = a.Set(vertices=verts1, name='Set-4')
        mdb.models['Model-1'].ConcentratedForce(name='Load-4', createStepName='Step-1',
                                                region=region, cf2=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#100 ]',), )
        region = a.Set(vertices=verts1, name='Set-5')
        mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#4 ]',), )
        region = a.Set(vertices=verts1, name='Set-6')
        mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#1 ]',), )
        region = a.Set(vertices=verts1, name='Set-7')
        mdb.models['Model-1'].DisplacementBC(name='BC-3', createStepName='Step-1',
                                             region=region, u1=0.0, u2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#10 ]',), )
        region = a.Set(vertices=verts1, name='Set-8')
        mdb.models['Model-1'].DisplacementBC(name='BC-4', createStepName='Step-1',
                                             region=region, u1=0.0, u2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF,
                                                                   predefinedFields=OFF, interactions=ON,
                                                                   constraints=ON,
                                                                   engineeringFeatures=ON)
        mdb.models['Model-1'].Equation(name='Constraint-1', terms=((1.0, 'Part-1-1.L1',
                                                                    2), (-1.0, 'Part-1-1.R1', 2),
                                                                   (-1.0, 'Part-1-1.B1', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-2', terms=((1.0, 'Part-1-1.L2',
                                                                    2), (-1.0, 'Part-1-1.R2', 2),
                                                                   (-1.0, 'Part-1-1.B1', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-3', terms=((1.0, 'Part-1-1.L3',
                                                                    2), (-1.0, 'Part-1-1.R3', 2),
                                                                   (-1.0, 'Part-1-1.B1', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-4', terms=((1.0, 'Part-1-1.B1',
                                                                    1), (-1.0, 'Part-1-1.T1', 1),
                                                                   (-1.0, 'Part-1-1.L2', 1)))

        if loadcase == 'uniaxial':
            if axis == 'y':
                mdb.models['Model-1'].constraints['Constraint-1'].suppress()
                mdb.models['Model-1'].constraints['Constraint-2'].suppress()
                mdb.models['Model-1'].constraints['Constraint-3'].suppress()
                mdb.models['Model-1'].constraints['Constraint-4'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-2'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-3'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-4'].suppress()

            if axis == 'x':
                mdb.models['Model-1'].constraints['Constraint-1'].suppress()
                mdb.models['Model-1'].constraints['Constraint-2'].suppress()
                mdb.models['Model-1'].constraints['Constraint-3'].suppress()
                mdb.models['Model-1'].constraints['Constraint-4'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-1'].suppress()

        if loadcase == 'shear':
            if axis == 'y':
                mdb.models['Model-1'].constraints['Constraint-1'].suppress()
                mdb.models['Model-1'].constraints['Constraint-2'].suppress()
                mdb.models['Model-1'].constraints['Constraint-3'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-1'].suppress()

            if axis == 'x':
                mdb.models['Model-1'].constraints['Constraint-4'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-2'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-3'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-4'].suppress()

    # Bounce
    if structure == 'h':
        a = mdb.models['Model-1'].rootAssembly
        session.viewports['Viewport: 1'].setValues(displayedObject=a)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#104 ]',), )
        region = a.Set(vertices=verts1, name='Set-1')
        mdb.models['Model-1'].ConcentratedForce(name='Load-1', createStepName='Step-1',
                                                region=region, cf1=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#104 ]',), )
        region = a.Set(vertices=verts1, name='Set-2')
        mdb.models['Model-1'].ConcentratedForce(name='Load-2', createStepName='Step-1',
                                                region=region, cf2=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#210009 ]',), )
        region = a.Set(vertices=verts1, name='Set-3')
        mdb.models['Model-1'].ConcentratedForce(name='Load-3', createStepName='Step-1',
                                                region=region, cf1=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#210009 ]',), )
        region = a.Set(vertices=verts1, name='Set-4')
        mdb.models['Model-1'].ConcentratedForce(name='Load-4', createStepName='Step-1',
                                                region=region, cf2=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#40000 ]',), )
        region = a.Set(vertices=verts1, name='Set-5')
        mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#100000 ]',), )
        region = a.Set(vertices=verts1, name='Set-6')
        mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#80000 ]',), )
        region = a.Set(vertices=verts1, name='Set-7')
        mdb.models['Model-1'].DisplacementBC(name='BC-3', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#4000 ]',), )
        region = a.Set(vertices=verts1, name='Set-8')
        mdb.models['Model-1'].DisplacementBC(name='BC-4', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#40 ]',), )
        region = a.Set(vertices=verts1, name='Set-9')
        mdb.models['Model-1'].DisplacementBC(name='BC-5', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#8000 ]',), )
        region = a.Set(vertices=verts1, name='Set-10')
        mdb.models['Model-1'].DisplacementBC(name='BC-6', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF,
                                                                   predefinedFields=OFF, interactions=ON,
                                                                   constraints=ON,
                                                                   engineeringFeatures=ON)
        p1 = mdb.models['Model-1'].parts['Part_1']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        p = mdb.models['Model-1'].parts['Part_1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#8000 ]',), )
        p.Set(vertices=verts, name='L1')
        p = mdb.models['Model-1'].parts['Part_1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#40 ]',), )
        p.Set(vertices=verts, name='L2')
        p = mdb.models['Model-1'].parts['Part_1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#4000 ]',), )
        p.Set(vertices=verts, name='L3')
        p = mdb.models['Model-1'].parts['Part_1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#80000 ]',), )
        p.Set(vertices=verts, name='L4')
        p = mdb.models['Model-1'].parts['Part_1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#1 ]',), )
        p.Set(vertices=verts, name='R1')
        p = mdb.models['Model-1'].parts['Part_1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#8 ]',), )
        p.Set(vertices=verts, name='R2')
        p = mdb.models['Model-1'].parts['Part_1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#10000 ]',), )
        p.Set(vertices=verts, name='R3')
        p = mdb.models['Model-1'].parts['Part_1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#200000 ]',), )
        p.Set(vertices=verts, name='R4')
        p = mdb.models['Model-1'].parts['Part_1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#100 ]',), )
        p.Set(vertices=verts, name='T1')
        p = mdb.models['Model-1'].parts['Part_1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#4 ]',), )
        p.Set(vertices=verts, name='T2')
        p = mdb.models['Model-1'].parts['Part_1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#40000 ]',), )
        p.Set(vertices=verts, name='B1')
        p = mdb.models['Model-1'].parts['Part_1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#100000 ]',), )
        p.Set(vertices=verts, name='B2')
        a1 = mdb.models['Model-1'].rootAssembly
        a1.regenerate()
        a = mdb.models['Model-1'].rootAssembly
        session.viewports['Viewport: 1'].setValues(displayedObject=a)
        mdb.models['Model-1'].Equation(name='Constraint-1', terms=((1.0, 'Part-1.L1',
                                                                    2), (-1.0, 'Part-1.R1', 2),
                                                                   (-1.0, 'Part-1.B1', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-2', terms=((1.0, 'Part-1.L2',
                                                                    2), (-1.0, 'Part-1.R2', 2),
                                                                   (-1.0, 'Part-1.B1', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-3', terms=((1.0, 'Part-1.L3',
                                                                    2), (-1.0, 'Part-1.R3', 2),
                                                                   (-1.0, 'Part-1.B1', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-4', terms=((1.0, 'Part-1.L4',
                                                                    2), (-1.0, 'Part-1.R4', 2),
                                                                   (-1.0, 'Part-1.B1', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-5', terms=((1.0, 'Part-1.B1',
                                                                    1), (-1.0, 'Part-1.T1', 1),
                                                                   (-1.0, 'Part-1.L3', 1)))
        mdb.models['Model-1'].Equation(name='Constraint-6', terms=((1.0, 'Part-1.B2',
                                                                    1), (-1.0, 'Part-1.T2', 1),
                                                                   (-1.0, 'Part-1.L3', 1)))

        if loadcase == 'uniaxial':
            if axis == 'y':
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-3'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-5'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-6'].suppress()
                mdb.models['Model-1'].constraints['Constraint-1'].suppress()
                mdb.models['Model-1'].constraints['Constraint-2'].suppress()
                mdb.models['Model-1'].constraints['Constraint-3'].suppress()
                mdb.models['Model-1'].constraints['Constraint-4'].suppress()
                mdb.models['Model-1'].constraints['Constraint-5'].suppress()
                mdb.models['Model-1'].constraints['Constraint-6'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF,
                                                                           predefinedFields=OFF, interactions=ON,
                                                                           constraints=ON,
                                                                           engineeringFeatures=ON)

            if axis == 'x':
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-1'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-2'].suppress()
                mdb.models['Model-1'].constraints['Constraint-1'].suppress()
                mdb.models['Model-1'].constraints['Constraint-2'].suppress()
                mdb.models['Model-1'].constraints['Constraint-3'].suppress()
                mdb.models['Model-1'].constraints['Constraint-4'].suppress()
                mdb.models['Model-1'].constraints['Constraint-5'].suppress()
                mdb.models['Model-1'].constraints['Constraint-6'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF,
                                                                           predefinedFields=OFF, interactions=ON,
                                                                           constraints=ON,
                                                                           engineeringFeatures=ON)

        if loadcase == 'shear':
            if axis == 'y':
                mdb.models['Model-1'].boundaryConditions['BC-1'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-2'].suppress()
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].constraints['Constraint-1'].suppress()
                mdb.models['Model-1'].constraints['Constraint-2'].suppress()
                mdb.models['Model-1'].constraints['Constraint-3'].suppress()
                mdb.models['Model-1'].constraints['Constraint-4'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF,
                                                                           predefinedFields=OFF, interactions=ON,
                                                                           constraints=ON,
                                                                           engineeringFeatures=ON)

            if axis == 'x':
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-3'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-5'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-6'].suppress()
                mdb.models['Model-1'].constraints['Constraint-5'].suppress()
                mdb.models['Model-1'].constraints['Constraint-6'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF,
                                                                           predefinedFields=OFF, interactions=ON,
                                                                           constraints=ON,
                                                                           engineeringFeatures=ON)


    # Trellis
    if structure == 'i':
        p1 = mdb.models['Model-1'].parts['Part-1']
        session.viewports['Viewport: 1'].setValues(displayedObject=p1)
        session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=OFF,
                                                               engineeringFeatures=OFF, mesh=ON)
        session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
            meshTechnique=ON)
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#100 ]',), )
        p.Set(vertices=verts, name='L1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#40 ]',), )
        p.Set(vertices=verts, name='L2')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#4 ]',), )
        p.Set(vertices=verts, name='L3')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#1 ]',), )
        p.Set(vertices=verts, name='L4')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#400 ]',), )
        p.Set(vertices=verts, name='R1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#200 ]',), )
        p.Set(vertices=verts, name='R2')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#8 ]',), )
        p.Set(vertices=verts, name='R3')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#10 ]',), )
        p.Set(vertices=verts, name='R4')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#800 ]',), )
        p.Set(vertices=verts, name='T1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#20 ]',), )
        p.Set(vertices=verts, name='B1')
        a1 = mdb.models['Model-1'].rootAssembly
        a1.regenerate()
        a = mdb.models['Model-1'].rootAssembly
        session.viewports['Viewport: 1'].setValues(displayedObject=a)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF, loads=ON,
                                                                   bcs=ON, predefinedFields=ON, connectors=ON)
        session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
            meshTechnique=OFF)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#800 ]',), )
        region = a.Set(vertices=verts1, name='Set-1')
        mdb.models['Model-1'].ConcentratedForce(name='Load-1', createStepName='Step-1',
                                                region=region, cf1=float(force), distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#800 ]',), )
        region = a.Set(vertices=verts1, name='Set-2')
        mdb.models['Model-1'].ConcentratedForce(name='Load-2', createStepName='Step-1',
                                                region=region, cf2=float(force), distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#145 ]',), )
        region = a.Set(vertices=verts1, name='Set-3')
        mdb.models['Model-1'].ConcentratedForce(name='Load-3', createStepName='Step-1',
                                                region=region, cf1=-float(force), distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#145 ]',), )
        region = a.Set(vertices=verts1, name='Set-4')
        mdb.models['Model-1'].ConcentratedForce(name='Load-4', createStepName='Step-1',
                                                region=region, cf2=float(force), distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#20 ]',), )
        region = a.Set(vertices=verts1, name='Set-5')
        mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#400 ]',), )
        region = a.Set(vertices=verts1, name='Set-6')
        mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1',
                                             region=region, u1=0.0, u2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        mdb.models['Model-1'].DisplacementBC(name='BC-6', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#200 ]',), )
        region = a.Set(vertices=verts1, name='Set-7')
        mdb.models['Model-1'].DisplacementBC(name='BC-3', createStepName='Step-1',
                                             region=region, u1=0.0, u2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        mdb.models['Model-1'].DisplacementBC(name='BC-7', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#8 ]',), )
        region = a.Set(vertices=verts1, name='Set-8')
        mdb.models['Model-1'].DisplacementBC(name='BC-4', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#10 ]',), )
        region = a.Set(vertices=verts1, name='Set-9')
        mdb.models['Model-1'].DisplacementBC(name='BC-5', createStepName='Step-1',
                                             region=region, u1=0.0, u2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        mdb.models['Model-1'].DisplacementBC(name='BC-8', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF,
                                                                   predefinedFields=OFF, interactions=ON,
                                                                   constraints=ON,
                                                                   engineeringFeatures=ON)
        mdb.models['Model-1'].Equation(name='Constraint-1', terms=((1.0, 'Part-1-1.L1',
                                                                    2), (-1.0, 'Part-1-1.R1', 2),
                                                                   (-1.0, 'Part-1-1.B1', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-2', terms=((1.0, 'Part-1-1.L2',
                                                                    2), (-1.0, 'Part-1-1.R2', 2),
                                                                   (-1.0, 'Part-1-1.B1', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-3', terms=((1.0, 'Part-1-1.L3',
                                                                    2), (-1.0, 'Part-1-1.R3', 2),
                                                                   (-1.0, 'Part-1-1.B1', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-4', terms=((1.0, 'Part-1-1.L4',
                                                                    2), (-1.0, 'Part-1-1.R4', 2),
                                                                   (-1.0, 'Part-1-1.B1', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-5', terms=((1.0, 'Part-1-1.B1',
                                                                    1), (-1.0, 'Part-1-1.T1', 1),
                                                                   (-1.0, 'Part-1-1.R2', 1)))
        mdb.models['Model-1'].Equation(name='Constraint-6', terms=((1.0, 'Part-1-1.L1',
                                                                    1), (-1.0, 'Part-1-1.L2', 1),
                                                                   (-1.0, 'Part-1-1.B1', 1)))
        mdb.models['Model-1'].Equation(name='Constraint-7', terms=((1.0, 'Part-1-1.L3',
                                                                    1), (-1.0, 'Part-1-1.L4', 1),
                                                                   (-1.0, 'Part-1-1.B1', 1)))
        mdb.models['Model-1'].Equation(name='Constraint-8', terms=((1.0, 'Part-1-1.R1',
                                                                    1), (-1.0, 'Part-1-1.R2', 1),
                                                                   (-1.0, 'Part-1-1.B1', 1)))
        mdb.models['Model-1'].Equation(name='Constraint-9', terms=((1.0, 'Part-1-1.R3',
                                                                    1), (-1.0, 'Part-1-1.R4', 1),
                                                                   (-1.0, 'Part-1-1.B1', 1)))

        if loadcase == 'uniaxial':
            if axis == 'y':
                mdb.models['Model-1'].constraints['Constraint-5'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-2'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-3'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-5'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-6'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-7'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-8'].suppress()

            if axis == 'x':
                mdb.models['Model-1'].constraints['Constraint-1'].suppress()
                mdb.models['Model-1'].constraints['Constraint-2'].suppress()
                mdb.models['Model-1'].constraints['Constraint-3'].suppress()
                mdb.models['Model-1'].constraints['Constraint-4'].suppress()
                mdb.models['Model-1'].constraints['Constraint-6'].suppress()
                mdb.models['Model-1'].constraints['Constraint-7'].suppress()
                mdb.models['Model-1'].constraints['Constraint-8'].suppress()
                mdb.models['Model-1'].constraints['Constraint-9'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-1'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-6'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-7'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-8'].suppress()

        if loadcase == 'shear':
            if axis == 'y':
                mdb.models['Model-1'].constraints['Constraint-5'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-2'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-3'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-5'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-6'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-7'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-8'].suppress()
                mdb.models['Model-1'].constraints['Constraint-6'].suppress()
                mdb.models['Model-1'].constraints['Constraint-7'].suppress()
                mdb.models['Model-1'].constraints['Constraint-8'].suppress()
                mdb.models['Model-1'].constraints['Constraint-9'].suppress()

            if axis == 'x':
                mdb.models['Model-1'].constraints['Constraint-1'].suppress()
                mdb.models['Model-1'].constraints['Constraint-2'].suppress()
                mdb.models['Model-1'].constraints['Constraint-3'].suppress()
                mdb.models['Model-1'].constraints['Constraint-4'].suppress()
                mdb.models['Model-1'].constraints['Constraint-6'].suppress()
                mdb.models['Model-1'].constraints['Constraint-7'].suppress()
                mdb.models['Model-1'].constraints['Constraint-8'].suppress()
                mdb.models['Model-1'].constraints['Constraint-9'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-1'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-2'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-3'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-5'].suppress()

    # No!
    if structure == 'j':
        pass

    # SHD
    if structure == 'k':
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#0 #1 ]',), )
        p.Set(vertices=verts, name='L1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#10000000 ]',), )
        p.Set(vertices=verts, name='L2')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#10000 ]',), )
        p.Set(vertices=verts, name='L3')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#0 #4 ]',), )
        p.Set(vertices=verts, name='L4')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#20000000 ]',), )
        p.Set(vertices=verts, name='R1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#2000000 ]',), )
        p.Set(vertices=verts, name='R2')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#20000 ]',), )
        p.Set(vertices=verts, name='R3')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#4 ]',), )
        p.Set(vertices=verts, name='R4')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#0 #2 ]',), )
        p.Set(vertices=verts, name='T1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#40000000 ]',), )
        p.Set(vertices=verts, name='T2')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#0 #8 ]',), )
        p.Set(vertices=verts, name='B1')
        p = mdb.models['Model-1'].parts['Part-1']
        v = p.vertices
        verts = v.getSequenceFromMask(mask=('[#1000 ]',), )
        p.Set(vertices=verts, name='B2')
        a1 = mdb.models['Model-1'].rootAssembly
        a1.regenerate()
        a = mdb.models['Model-1'].rootAssembly
        session.viewports['Viewport: 1'].setValues(displayedObject=a)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(mesh=OFF, loads=ON,
                                                                   bcs=ON, predefinedFields=ON, connectors=ON)
        session.viewports['Viewport: 1'].assemblyDisplay.meshOptions.setValues(
            meshTechnique=OFF)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#40000000 #2 ]',), )
        region = a.Set(vertices=verts1, name='Set-1')
        mdb.models['Model-1'].ConcentratedForce(name='Load-1', createStepName='Step-1',
                                                region=region, cf1=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#40000000 #2 ]',), )
        region = a.Set(vertices=verts1, name='Set-2')
        mdb.models['Model-1'].ConcentratedForce(name='Load-2', createStepName='Step-1',
                                                region=region, cf2=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#22020004 ]',), )
        region = a.Set(vertices=verts1, name='Set-3')
        mdb.models['Model-1'].ConcentratedForce(name='Load-3', createStepName='Step-1',
                                                region=region, cf1=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#22020004 ]',), )
        region = a.Set(vertices=verts1, name='Set-4')
        mdb.models['Model-1'].ConcentratedForce(name='Load-4', createStepName='Step-1',
                                                region=region, cf2=1000.0, distributionType=UNIFORM, field='',
                                                localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#0 #8 ]',), )
        region = a.Set(vertices=verts1, name='Set-5')
        mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#1000 ]',), )
        region = a.Set(vertices=verts1, name='Set-6')
        mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#0 #1 ]',), )
        region = a.Set(vertices=verts1, name='Set-7')
        mdb.models['Model-1'].DisplacementBC(name='BC-3', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#10000000 ]',), )
        region = a.Set(vertices=verts1, name='Set-8')
        mdb.models['Model-1'].DisplacementBC(name='BC-4', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#10000 ]',), )
        region = a.Set(vertices=verts1, name='Set-9')
        mdb.models['Model-1'].DisplacementBC(name='BC-5', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        a = mdb.models['Model-1'].rootAssembly
        v1 = a.instances['Part-1-1'].vertices
        verts1 = v1.getSequenceFromMask(mask=('[#0 #4 ]',), )
        region = a.Set(vertices=verts1, name='Set-10')
        mdb.models['Model-1'].DisplacementBC(name='BC-6', createStepName='Step-1',
                                             region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF,
                                             distributionType=UNIFORM, fieldName='', localCsys=None)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF,
                                                                   predefinedFields=OFF, interactions=ON,
                                                                   constraints=ON,
                                                                   engineeringFeatures=ON)
        mdb.models['Model-1'].Equation(name='Constraint-1', terms=((1.0, 'Part-1-1.L1',
                                                                    2), (-1.0, 'Part-1-1.R1', 2),
                                                                   (-1.0, 'Part-1-1.B1', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-2', terms=((1.0, 'Part-1-1.L2',
                                                                    2), (-1.0, 'Part-1-1.R2', 2),
                                                                   (-1.0, 'Part-1-1.B1', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-3', terms=((1.0, 'Part-1-1.L3',
                                                                    2), (-1.0, 'Part-1-1.R3', 2),
                                                                   (-1.0, 'Part-1-1.B1', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-4', terms=((1.0, 'Part-1-1.L4',
                                                                    2), (-1.0, 'Part-1-1.R4', 2),
                                                                   (-1.0, 'Part-1-1.B1', 2)))
        mdb.models['Model-1'].Equation(name='Constraint-5', terms=((1.0, 'Part-1-1.B1',
                                                                    1), (-1.0, 'Part-1-1.T1', 1),
                                                                   (-1.0, 'Part-1-1.L3', 1)))
        mdb.models['Model-1'].Equation(name='Constraint-6', terms=((1.0, 'Part-1-1.B2',
                                                                    1), (-1.0, 'Part-1-1.T2', 1),
                                                                   (-1.0, 'Part-1-1.L3', 1)))

        if loadcase == 'uniaxial':
            if axis == 'y':
                mdb.models['Model-1'].constraints['Constraint-1'].suppress()
                mdb.models['Model-1'].constraints['Constraint-2'].suppress()
                mdb.models['Model-1'].constraints['Constraint-3'].suppress()
                mdb.models['Model-1'].constraints['Constraint-4'].suppress()
                mdb.models['Model-1'].constraints['Constraint-5'].suppress()
                mdb.models['Model-1'].constraints['Constraint-6'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-3'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-5'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-6'].suppress()

            if axis == 'x':
                mdb.models['Model-1'].constraints['Constraint-1'].suppress()
                mdb.models['Model-1'].constraints['Constraint-2'].suppress()
                mdb.models['Model-1'].constraints['Constraint-3'].suppress()
                mdb.models['Model-1'].constraints['Constraint-4'].suppress()
                mdb.models['Model-1'].constraints['Constraint-5'].suppress()
                mdb.models['Model-1'].constraints['Constraint-6'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-1'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-2'].suppress()

        if loadcase == 'shear':
            if axis == 'y':
                mdb.models['Model-1'].constraints['Constraint-1'].suppress()
                mdb.models['Model-1'].constraints['Constraint-2'].suppress()
                mdb.models['Model-1'].constraints['Constraint-3'].suppress()
                mdb.models['Model-1'].constraints['Constraint-4'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-1'].suppress()
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-1'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-2'].suppress()

            if axis == 'x':
                session.viewports['Viewport: 1'].view.setValues(nearPlane=1518.81,
                                                                farPlane=1586.35, width=229.861, height=108.103,
                                                                viewOffsetX=281.592,
                                                                viewOffsetY=160.727)
                mdb.models['Model-1'].constraints['Constraint-5'].suppress()
                mdb.models['Model-1'].constraints['Constraint-6'].suppress()
                session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                                           predefinedFields=ON, interactions=OFF,
                                                                           constraints=OFF,
                                                                           engineeringFeatures=OFF)
                mdb.models['Model-1'].loads['Load-2'].suppress()
                mdb.models['Model-1'].loads['Load-3'].suppress()
                mdb.models['Model-1'].loads['Load-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-3'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-4'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-5'].suppress()
                mdb.models['Model-1'].boundaryConditions['BC-6'].suppress()



def run_analysis(workdir):
    job_number = 1
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF,
        predefinedFields=OFF, connectors=OFF)

    while os.path.exists(str(workdir)+'/Job-'+str(job_number)+'.odb'):
        job_number += 1
    mdb.Job(name='Job-'+str(job_number), model='Model-1', description='', type=ANALYSIS,
        atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
        scratch='', resultsFormat=ODB)
    mdb.jobs['Job-'+str(job_number)].submit(consistencyChecking=OFF)
    session.mdbData.summary()

    while not os.path.exists(str(workdir)+'/Job-'+str(job_number)+'.odb'):
        time.sleep(1)

    execution = 0
    while execution == 0:
        try:
            o3 = session.openOdb(name=str(workdir)+'/Job-'+str(job_number)+'.odb')
            session.viewports['Viewport: 1'].setValues(displayedObject=o3)
            session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
                UNDEFORMED, DEFORMED, ))
            session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
                UNDEFORMED, DEFORMED, CONTOURS_ON_DEF, ))
            execution = 1
        except:
            time.sleep(1)

if __name__ == "__main__":
    main()
else:
    print("Please run main.py via Abaqus CAE by using 'File > Run Script... > main.py'")

