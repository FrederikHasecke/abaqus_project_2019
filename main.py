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

import os
workdir = "H:/Abaqus Files/abaqus_project_2019"
os.chdir(workdir)

# Import sub modules for the different lattices
#H:\Abaqus Files\abaqus_project_2019\utilities
from utilities import shapeSquare

def main():
    # First user input:
    # Define the chosen structure. The response should be a, b, c, d, e, f, g, h, i or k.
    # They are corresponding to the listings in Shimada et al., SR 2015
    structure = select_structure()

    # Second User Input:
    # Choosing the edge length. All structures are built with a edge length of 1[mm]
    # a simple scaling of the vertices locations will ensure a proper edge length
    edge = select_edge_length(structure)

    # Create the choosen structure
    create_structure(structure, edge)

    # Third User Input:
    # Material. The user can decide between elastic or hyperelastic Mooney-Rivlin models and enter
    # any desired material values. Values for the most common materials are provided in the accompanying documentation
    model, young_modulus, poisson_rate, c10, c01, d1 = select_material()

    # Create the choosen Material
    create_material(model, young_modulus, poisson_rate, c10, c01, d1)

    # Fourth User Input:
    # Beam Section. The user can pick between the provided standard beam sections
    # A second getInputs window will open after the selection for the provided variables of the cross sections
    # There is an additional condition which prevents the beam section to be too large and to overlap at areas which
    # are not supposed to overlap. This is not visible in the visualization but unphysical conditions are not desired.
    # You can find additional information in the documentation attached to this code
    section, width, width_2, height, radius, c, d, thickness, thickness_2, thickness_3, I = select_cross_section(edge)

    # Fifth User Input:
    # Loading Conditions. The User can choose between uniaxial and shear loading as well as decide the provided force
    #loadcase, force = select_loading()


# This function queries the user to choose between the 11 possible Structures and returns the chosen value.
# Takes in the chosen structure from the user input and checks if it is one of the 11 possible structures.
# If it is not, the user gets queried again
def select_structure():
    possible_structures = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']
    structure = str(getInput("Please choose one of the 11 Structures presented in the attached documentation."
                             " [Choose from a to k]"))
    if structure in possible_structures:
        pass
    else:
        getWarningReply('The chosen letter is not part of the possible options.\n'
                        ' Please choose an available option.', buttons=(YES,))
        structure = select_structure()
    return structure

def select_edge_length(structure):
    structure_dict = {'a': 'Square', 'b': 'Honeycomb', 'c': 'Triangular', 'd': 'CaVO', 'e': 'Star', 'f': 'SrCuBo',
                      'g': 'Kagome', 'h': 'Bounce', 'i': 'Trellis', 'j': 'Mapple_leaf', 'k': 'SHD'}
    try:
        edge_length = float(getInput("Please enter the desired edge length for "+
                                     structure_dict[structure]+" in [mm]"))
    except:
        getWarningReply('The provided value is not a valid number.\n'
                        'Please choose an Integer or float.\n'
                        'Please note: Python uses a dot for decimal values', buttons=(YES,))
        edge_length = select_edge_length(structure)
    if edge_length > 0.0:
        pass
    else:
        getWarningReply('The edge length must be larger than Zero.\n'
                        ' Please choose a value larger than Zero.', buttons=(YES,))
        edge_length = select_edge_length()
    return edge_length


def create_structure(structure, edge):
    # Create a bunch of if statements to create the corresponing structure.
    # If the time permits, change this to a more sophisticated method of selection

    # TODO Create structure if statements for all 11 Structures
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
        p = mdb.models['Model-1'].Part(name='Part', dimensionality=TWO_D_PLANAR,
                                       type=DEFORMABLE_BODY)
        p = mdb.models['Model-1'].parts['Part']
        p.BaseWire(sketch=s1)
        s1.unsetPrimaryObject()
        p = mdb.models['Model-1'].parts['Part']
        del mdb.models['Model-1'].sketches['__profile__']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)

    if structure == 'b':
        s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                                    sheetSize=200.0)
        g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
        s.setPrimaryObject(option=STANDALONE)
        s.Spot(point=(5.0, 15.0))
        s.Spot(point=(10.0, 10.0))
        s.Spot(point=(10.0, 5.0))
        s.Spot(point=(15.0, 15.0))
        s.Spot(point=(15.0, 20.0))
        s.Spot(point=(10.0, 25.0))
        s.Spot(point=(5.0, 20.0))
        s.Line(point1=(5.0, 20.0), point2=(10.0, 25.0))
        s.Line(point1=(10.0, 25.0), point2=(15.0, 20.0))
        s.PerpendicularConstraint(entity1=g[2], entity2=g[3], addUndoState=False)
        s.Line(point1=(15.0, 20.0), point2=(15.0, 15.0))
        s.VerticalConstraint(entity=g[4], addUndoState=False)
        s.Line(point1=(15.0, 15.0), point2=(10.0, 10.0))
        s.Line(point1=(10.0, 10.0), point2=(10.0, 5.0))
        s.VerticalConstraint(entity=g[6], addUndoState=False)
        s.Line(point1=(5.0, 15.0), point2=(10.0, 10.0))
        s.AngularDimension(line1=g[2], line2=g[3], textPoint=(9.71992492675781,
                                                              20.7295341491699), value=120.0)
        s.delete(objectList=(c[10],))
        s.AngularDimension(line1=g[3], line2=g[4], textPoint=(11.8052291870117,
                                                              18.4535140991211), value=120.0)
        s.AngularDimension(line1=g[5], line2=g[4], textPoint=(12.1310577392578,
                                                              16.047435760498), value=120.0)
        s.AngularDimension(line1=g[5], line2=g[7], textPoint=(10.3064155578613,
                                                              12.9910669326782), value=120.0)
        s.ObliqueDimension(vertex1=v[7], vertex2=v[8], textPoint=(3.5291748046875,
                                                                  23.9159622192383), value=edge)
        s.ObliqueDimension(vertex1=v[9], vertex2=v[10], textPoint=(14.9331855773926,
                                                                   24.1110496520996), value=edge)
        s.ObliqueDimension(vertex1=v[11], vertex2=v[12], textPoint=(19.2992935180664,
                                                                    16.5676689147949), value=edge)
        s.ObliqueDimension(vertex1=v[13], vertex2=v[14], textPoint=(14.4770278930664,
                                                                    8.89422988891602), value=edge)
        s.ObliqueDimension(vertex1=v[17], vertex2=v[18], textPoint=(5.67964553833008,
                                                                    9.93469715118408), value=edge)
        s.ObliqueDimension(vertex1=v[15], vertex2=v[16], textPoint=(8.80760192871094,
                                                                    7.26850128173828), value=edge)
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
        session.viewports['Viewport: 1'].setValues(displayedObject=None)
        s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                                          sheetSize=200.0)
        g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
        s.setPrimaryObject(option=STANDALONE)
        s.Spot(point=(45.0, 25.0))
        s.Spot(point=(45.0, 22.5))
        s.Spot(point=(46.25, 27.5))
        s.Spot(point=(43.75, 27.5))
        s.Line(point1=(45.0, 22.5), point2=(45.0, 25.0))
        s.VerticalConstraint(entity=g[2], addUndoState=False)
        s.Line(point1=(45.0, 25.0), point2=(46.25, 27.5))
        s.Line(point1=(46.25, 27.5), point2=(43.75, 27.5))
        s.HorizontalConstraint(entity=g[4], addUndoState=False)
        s.Line(point1=(43.75, 27.5), point2=(45.0, 25.0))
        s.AngularDimension(line1=g[4], line2=g[5], textPoint=(44.3024673461914,
                                                              27.1297302246094), value=60.0)
        s.AngularDimension(line1=g[3], line2=g[4], textPoint=(45.5373764038086,
                                                              27.1297302246094), value=60.0)
        s.ObliqueDimension(vertex1=v[8], vertex2=v[9], textPoint=(44.8835983276367,
                                                                  28.2653980255127), value=edge)
        s.ObliqueDimension(vertex1=v[4], vertex2=v[5], textPoint=(44.5842170715332,
                                                                  25.7109546661377), value=edge)
        s.Spot(point=(42.8706321716309, 27.8417129516602))
        s.Spot(point=(42.4985046386719, 28.6266059875488))
        s.Spot(point=(42.5154190063477, 29.3355407714844))
        s.Line(point1=(43.5566243270259, 27.5), point2=(42.8706321716309,
                                                        27.8417129516602))
        s.Line(point1=(42.8706321716309, 27.8417129516602), point2=(42.4985046386719,
                                                                    28.6266059875488))
        s.Line(point1=(42.4985046386719, 28.6266059875488), point2=(42.5154190063477,
                                                                    29.3355407714844))
        s.AngularDimension(line1=g[6], line2=g[4], textPoint=(43.1666450500488,
                                                              27.5885219573975), value=30.0)
        s.AngularDimension(line1=g[6], line2=g[7], textPoint=(42.6676559448242,
                                                              28.1371021270752), value=30.0)
        s.AngularDimension(line1=g[8], line2=g[7], textPoint=(42.3801002502441,
                                                              28.9388751983643), value=30.0)
        s.ObliqueDimension(vertex1=v[15], vertex2=v[16], textPoint=(42.9805793762207,
                                                                    27.3775291442871), value=edge)
        s.ObliqueDimension(vertex1=v[17], vertex2=v[18], textPoint=(42.7014846801758,
                                                                    28.466251373291), value=edge)
        s.ObliqueDimension(vertex1=v[19], vertex2=v[20], textPoint=(42.3716430664063,
                                                                    29.2511444091797), value=edge)
        s.Spot(point=(42.2363243103027, 27.9936275482178))
        s.Line(point1=(42.2363243103027, 27.9936275482178), point2=(42.6905989232415,
                                                                    28.0))
        s.AngularDimension(line1=g[9], line2=g[7], textPoint=(42.1263771057129,
                                                              28.2552585601807), value=60.0)
        s.ObliqueDimension(vertex1=v[22], vertex2=v[23], textPoint=(42.4562187194824,
                                                                    27.7741947174072), value=0.5*edge)
        s.Spot(point=(45.3824920654297, 27.765754699707))
        s.Spot(point=(45.8983955383301, 28.3734149932861))
        s.Spot(point=(45.8645668029785, 27.5041236877441))
        s.Line(point1=(45.8983955383301, 28.3734149932861), point2=(45.3824920654297,
                                                                    27.765754699707))
        s.Line(point1=(45.3824920654297, 27.765754699707), point2=(44.5566243270259,
                                                                   27.5))
        s.Line(point1=(45.3824920654297, 27.765754699707), point2=(45.8645668029785,
                                                                   27.5041236877441))
        s.AngularDimension(line1=g[4], line2=g[11], textPoint=(45.0949401855469,
                                                               27.5800819396973), value=30.0)
        s.AngularDimension(line1=g[11], line2=g[10], textPoint=(45.6531295776367,
                                                                28.297456741333), value=30.0)
        s.AngularDimension(line1=g[10], line2=g[12], textPoint=(46.0083427429199,
                                                                28.1961803436279), value=60.0)
        s.ObliqueDimension(vertex1=v[29], vertex2=v[30], textPoint=(44.815845489502,
                                                                    27.934549331665), value=edge)
        s.ObliqueDimension(vertex1=v[31], vertex2=v[32], textPoint=(45.6531295776367,
                                                                    27.7826347351074), value=0.5*edge)
        s.ObliqueDimension(vertex1=v[27], vertex2=v[28], textPoint=(45.4247779846191,
                                                                    28.4831314086914), value=edge)
        s.Spot(point=(42.5090026855469, 30.5987682342529))
        s.Spot(point=(43.1529541015625, 31.0589008331299))
        s.Spot(point=(44.2580032348633, 31.0747680664063))
        s.Line(point1=(42.1905989232415, 29.8660254037844), point2=(42.5090026855469,
                                                                    30.5987682342529))
        s.Line(point1=(42.5090026855469, 30.5987682342529), point2=(43.1529541015625,
                                                                    31.0589008331299))
        s.Line(point1=(43.1529541015625, 31.0589008331299), point2=(44.2580032348633,
                                                                    31.0747680664063))
        s.AngularDimension(line1=g[8], line2=g[13], textPoint=(42.2943534851074,
                                                               30.3766345977783), value=30.0)
        s.AngularDimension(line1=g[13], line2=g[14], textPoint=(42.8667526245117,
                                                                30.9081687927246), value=30.0)
        s.AngularDimension(line1=g[14], line2=g[15], textPoint=(43.6538009643555,
                                                                31.0033683776855), value=30.0)
        s.ObliqueDimension(vertex1=v[36], vertex2=v[37], textPoint=(42.6521034240723,
                                                                    30.1069030761719), value=edge)
        s.ObliqueDimension(vertex1=v[38], vertex2=v[39], textPoint=(43.2245025634766,
                                                                    30.6939678192139), value=edge)
        s.ObliqueDimension(vertex1=v[40], vertex2=v[41], textPoint=(44.2000007629395,
                                                                    31.0687103271484), value=edge)
        s.Spot(point=(45.3867988586426, 30.7842121124268))
        s.Spot(point=(46.0166625976563, 29.9571800231934))
        s.Line(point1=(44.5566243270259, 31.2320508075689), point2=(45.3867988586426,
                                                                    30.7842121124268))
        s.Line(point1=(45.3867988586426, 30.7842121124268), point2=(46.0166625976563,
                                                                    29.9571800231934))
        s.Spot(point=(46.0630760192871, 30.7842121124268))
        s.Line(point1=(45.3867988586426, 30.7842121124268), point2=(46.0630760192871,
                                                                    30.7842121124268))
        s.HorizontalConstraint(entity=g[18], addUndoState=False)
        s.AngularDimension(line1=g[15], line2=g[16], textPoint=(44.836498260498,
                                                                31.1547222137451), value=30.0)
        s.AngularDimension(line1=g[16], line2=g[17], textPoint=(45.6321144104004,
                                                                30.5460262298584), value=30.0)
        s.ObliqueDimension(vertex1=v[44], vertex2=v[45], textPoint=(44.8829078674316,
                                                                    30.810676574707), value=edge)
        s.ObliqueDimension(vertex1=v[46], vertex2=v[47], textPoint=(45.479621887207,
                                                                    30.2350635528564), value=edge)
        s.ObliqueDimension(vertex1=v[49], vertex2=v[50], textPoint=(45.784610748291,
                                                                    30.5857238769531), value=0.5*edge)
        s.Spot(point=(44.1270713806152, 31.8361968994141))
        s.Spot(point=(42.1844367980957, 30.7180500030518))
        s.Line(point1=(42.1844367980957, 30.7180500030518), point2=(42.6905989232415,
                                                                    30.7320508075688))
        s.Line(point1=(43.5566243270259, 31.2320508075689), point2=(44.1270713806152,
                                                                    31.8361968994141))
        s.Line(point1=(44.1270713806152, 31.8361968994141), point2=(44.5566243270259,
                                                                    31.2320508075689))
        s.AngularDimension(line1=g[19], line2=g[13], textPoint=(42.4629020690918,
                                                                30.5923404693604), value=60.0)
        s.ObliqueDimension(vertex1=v[53], vertex2=v[54], textPoint=(42.3833389282227,
                                                                    30.8966884613037), value=0.5*edge)
        s.AngularDimension(line1=g[20], line2=g[15], textPoint=(43.9546852111816,
                                                                31.4127559661865), value=60.0)
        s.AngularDimension(line1=g[21], line2=g[15], textPoint=(44.2994537353516,
                                                                31.3532104492188), value=60.0)
        p = mdb.models['Model-1'].Part(name='Part-1',
                                             dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
        p = mdb.models['Model-1'].parts['Part-1']
        p.BaseWire(sketch=s)
        s.unsetPrimaryObject()
        p = mdb.models['Model-1'].parts['Part-1']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        del mdb.models['Model-1'].sketches['__profile__']


    if structure == 'f':
        session.viewports['Viewport: 1'].setValues(displayedObject=None)
        s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                                             sheetSize=200.0)
        g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
        s1.setPrimaryObject(option=STANDALONE)
        s1.Spot(point=(55.0, 40.0))
        s1.Spot(point=(55.0, 35.0))
        s1.Spot(point=(60.0, 37.5))
        s1.Spot(point=(50.0, 37.5))
        s1.Line(point1=(50.0, 37.5), point2=(55.0, 40.0))
        s1.Line(point1=(55.0, 40.0), point2=(60.0, 37.5))
        s1.Line(point1=(60.0, 37.5), point2=(55.0, 35.0))
        s1.Line(point1=(55.0, 35.0), point2=(50.0, 37.5))
        s1.Line(point1=(55.0, 40.0), point2=(55.0, 35.0))
        s1.VerticalConstraint(entity=g[6], addUndoState=False)
        s1.ObliqueDimension(vertex1=v[4], vertex2=v[5], textPoint=(50.331600189209,
                                                                   41.4930267333984), value=edge)
        s1.ObliqueDimension(vertex1=v[10], vertex2=v[11], textPoint=(53.1605529785156,
                                                                     37.0915794372559), value=edge)
        s1.ObliqueDimension(vertex1=v[6], vertex2=v[7], textPoint=(57.8512573242188,
                                                                   40.5073471069336), value=edge)
        s1.ObliqueDimension(vertex1=v[8], vertex2=v[9], textPoint=(54.9354972839355,
                                                                   38.425407409668), value=edge)
        s1.ObliqueDimension(vertex1=v[12], vertex2=v[13], textPoint=(36.1081161499023,
                                                                     59.3965301513672), value=edge)
        s1.Spot(point=(17.3265018463135, 70.5950317382813))
        s1.Spot(point=(18.2375373840332, 70.1096496582031))
        s1.Spot(point=(15.7823734283447, 70.1250610351563))
        s1.Spot(point=(16.6779670715332, 70.5410995483398))
        s1.Spot(point=(18.3070240020752, 68.7998886108398))
        s1.Spot(point=(17.3265018463135, 68.3761444091797))
        s1.Spot(point=(16.5930404663086, 68.2913970947266))
        s1.Spot(point=(15.7592105865479, 68.9462738037109))
        s1.Line(point1=(16.130724222743, 69.5027724506163), point2=(15.7823734283447,
                                                                    70.1250610351563))
        s1.Line(point1=(15.7823734283447, 70.1250610351563), point2=(16.6779670715332,
                                                                     70.5410995483398))
        s1.Line(point1=(16.6779670715332, 70.5410995483398), point2=(16.9967496265275,
                                                                     70.0027724506164))
        s1.Line(point1=(16.9967496265275, 70.0027724506164), point2=(17.3265018463135,
                                                                     70.5950317382813))
        s1.Line(point1=(17.3265018463135, 70.5950317382813), point2=(18.2375373840332,
                                                                     70.1096496582031))
        s1.Line(point1=(18.2375373840332, 70.1096496582031), point2=(17.8627750303123,
                                                                     69.5027724506163))
        s1.Line(point1=(17.8627750303123, 69.5027724506163), point2=(18.3070240020752,
                                                                     68.7998886108398))
        s1.Line(point1=(18.3070240020752, 68.7998886108398), point2=(17.3265018463135,
                                                                     68.3761444091797))
        s1.Line(point1=(17.3265018463135, 68.3761444091797), point2=(16.9967496265275,
                                                                     69.0027724506164))
        s1.Line(point1=(16.9967496265275, 69.0027724506164), point2=(16.5930404663086,
                                                                     68.2913970947266))
        s1.Line(point1=(16.5930404663086, 68.2913970947266), point2=(15.7592105865479,
                                                                     68.9462738037109))
        s1.Line(point1=(15.7592105865479, 68.9462738037109), point2=(16.130724222743,
                                                                     69.5027724506163))
        s1.AngularDimension(line1=g[7], line2=g[2], textPoint=(16.2077598571777,
                                                               69.6178817749023), value=90.0)
        s1.AngularDimension(line1=g[8], line2=g[7], textPoint=(15.8614177703857,
                                                               70.0819931030273), value=90.0)
        s1.AngularDimension(line1=g[8], line2=g[9], textPoint=(16.6415023803711,
                                                               70.4489822387695), value=90.0)
        s1.ObliqueDimension(vertex1=v[26], vertex2=v[27], textPoint=(16.7494525909424,
                                                                     70.2425079345703), value=edge)
        s1.AngularDimension(line1=g[10], line2=g[3], textPoint=(17.1070384979248,
                                                                70.0068664550781), value=90.0)
        s1.AngularDimension(line1=g[11], line2=g[10], textPoint=(17.3634204864502,
                                                                 70.4871368408203), value=90.0)
        s1.ObliqueDimension(vertex1=v[28], vertex2=v[29], textPoint=(17.2982006072998,
                                                                     70.2335357666016), value=edge)
        s1.AngularDimension(line1=g[12], line2=g[11], textPoint=(18.2599143981934,
                                                                 70.3364028930664), value=90.0)
        s1.AngularDimension(line1=g[13], line2=g[14], textPoint=(18.14990234375,
                                                                 68.8344116210938), value=90.0)
        s1.AngularDimension(line1=g[14], line2=g[15], textPoint=(17.3584766387939,
                                                                 68.5027084350586), value=90.0)
        s1.AngularDimension(line1=g[4], line2=g[13], textPoint=(17.8570747375488,
                                                                69.3793487548828), value=90.0)
        s1.ObliqueDimension(vertex1=v[34], vertex2=v[35], textPoint=(17.8333320617676,
                                                                     69.0792388916016), value=edge)
        s1.AngularDimension(line1=g[17], line2=g[16], textPoint=(16.5551815032959,
                                                                 68.4355773925781), value=90.0)
        s1.AngularDimension(line1=g[18], line2=g[17], textPoint=(15.8626852035522,
                                                                 68.9647216796875), value=90.0)
        s1.AngularDimension(line1=g[5], line2=g[16], textPoint=(16.8796653747559,
                                                                68.9489288330078), value=90.0)
        s1.ObliqueDimension(vertex1=v[40], vertex2=v[41], textPoint=(16.559139251709,
                                                                     68.7870254516602), value=edge)
        s1.Line(point1=(16.4967496265275, 68.1367470468319), point2=(17.4967496265273,
                                                                     68.1367470468318))
        s1.HorizontalConstraint(entity=g[19], addUndoState=False)
        s1.delete(objectList=(d[4],))
        s1.Spot(point=(18.3912200927734, 69.4988174438477))
        s1.Spot(point=(15.6209583282471, 69.5066452026367))
        s1.Spot(point=(15.6366539001465, 68.1909866333008))
        s1.Spot(point=(15.6131105422974, 70.8379669189453))
        s1.Line(point1=(15.630724222743, 70.3687978544007), point2=(15.6131105422974,
                                                                    70.8379669189453))
        s1.Line(point1=(15.6307242227431, 68.6367470468319), point2=(15.6366539001465,
                                                                     68.1909866333008))
        s1.Line(point1=(16.130724222743, 69.5027724506163), point2=(15.6209583282471,
                                                                    69.5066452026367))
        s1.Line(point1=(17.8627750303123, 69.5027724506163), point2=(18.3912200927734,
                                                                     69.4988174438477))
        s1.AngularDimension(line1=g[23], line2=g[13], textPoint=(18.0145282745361,
                                                                 69.3970108032227), value=60.0)
        s1.ObliqueDimension(vertex1=v[58], vertex2=v[59], textPoint=(18.2185707092285,
                                                                     69.6789321899414), value=0.5*edge)
        s1.AngularDimension(line1=g[7], line2=g[22], textPoint=(15.9270210266113,
                                                                69.6084518432617), value=60.0)
        s1.ObliqueDimension(vertex1=v[56], vertex2=v[57], textPoint=(15.814754486084,
                                                                     69.3057708740234), value=0.5*edge)
        s1.AngularDimension(line1=g[21], line2=g[17], textPoint=(15.7047185897827,
                                                                 68.5388946533203), value=60.0)
        s1.ObliqueDimension(vertex1=v[54], vertex2=v[55], textPoint=(15.9371995925903,
                                                                     68.2858123779297), value=0.5*edge)
        s1.AngularDimension(line1=g[20], line2=g[8], textPoint=(15.7014322280884,
                                                                70.469856262207), value=60.0)
        s1.ObliqueDimension(vertex1=v[52], vertex2=v[53], textPoint=(15.4659738540649,
                                                                     70.5839157104492), value=0.5*edge)
        p = mdb.models['Model-1'].Part(name='Part-1',
                                               dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
        p = mdb.models['Model-1'].parts['Part-1']
        p.BaseWire(sketch=s1)
        s1.unsetPrimaryObject()
        p = mdb.models['Model-1'].parts['Part-1']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        del mdb.models['Model-1'].sketches['__profile__']


    if structure == 'g':
        session.viewports['Viewport: 1'].setValues(displayedObject=None)
        s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                                             sheetSize=200.0)
        g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
        s1.setPrimaryObject(option=STANDALONE)
        s1.Spot(point=(35.0, 25.0))
        s1.Spot(point=(40.0, 25.0))
        s1.Spot(point=(42.5, 22.5))
        s1.Spot(point=(40.0, 20.0))
        s1.Spot(point=(35.0, 20.0))
        s1.Spot(point=(32.5, 22.5))
        s1.Line(point1=(32.5, 22.5), point2=(35.0, 25.0))
        s1.Line(point1=(35.0, 25.0), point2=(40.0, 25.0))
        s1.HorizontalConstraint(entity=g[3], addUndoState=False)
        s1.Line(point1=(40.0, 25.0), point2=(42.5, 22.5))
        s1.Line(point1=(42.5, 22.5), point2=(40.0, 20.0))
        s1.AngularDimension(line1=g[2], line2=g[3], textPoint=(35.4775161743164,
                                                               23.544548034668), value=120.0)
        s1.AngularDimension(line1=g[3], line2=g[4], textPoint=(40.0675468444824,
                                                               23.637393951416), value=120.0)
        s1.ObliqueDimension(vertex1=v[8], vertex2=v[9], textPoint=(37.3383407592773,
                                                                   26.3299293518066), value=edge)
        s1.ObliqueDimension(vertex1=v[6], vertex2=v[7], textPoint=(37.1212425231934,
                                                                   23.9778289794922), value=edge)
        s1.ObliqueDimension(vertex1=v[10], vertex2=v[11], textPoint=(41.6802597045898,
                                                                     23.8540344238281), value=edge)
        s1.Line(point1=(38.5, 24.1339745962156), point2=(35.0, 20.0))
        s1.Line(point1=(35.0, 20.0), point2=(40.0, 20.0))
        s1.HorizontalConstraint(entity=g[6], addUndoState=False)
        s1.Line(point1=(40.0, 20.0), point2=(40.5, 24.1339745962156))
        s1.AngularDimension(line1=g[5], line2=g[6], textPoint=(36.4079284667969,
                                                               20.7282180786133), value=120.0)
        s1.ObliqueDimension(vertex1=v[12], vertex2=v[13], textPoint=(39.1854591369629,
                                                                     21.5610656738281), value=edge)
        s1.AngularDimension(line1=g[6], line2=g[7], textPoint=(40.2515678405762,
                                                               23.4575862884521), value=120.0)
        s1.Spot(point=(39.5133323669434, 25.6798229217529))
        s1.Spot(point=(39.4938735961914, 22.6701049804688))
        s1.Spot(point=(40.7975807189941, 23.2817573547363))
        s1.Spot(point=(38.2971839904785, 23.2720489501953))
        s1.Spot(point=(38.3750190734863, 25.0196266174316))
        s1.Spot(point=(40.6419143676758, 25.0002098083496))
        s1.Line(point1=(38.2971839904785, 23.2720489501953), point2=(39.0,
                                                                     23.2679491924311))
        s1.Line(point1=(39.0, 23.2679491924311), point2=(39.4938735961914,
                                                         22.6701049804688))
        s1.Line(point1=(39.4938735961914, 22.6701049804688), point2=(40.0,
                                                                     23.2679491924311))
        s1.Line(point1=(40.0, 23.2679491924311), point2=(40.7975807189941,
                                                         23.2817573547363))
        s1.Line(point1=(38.3750190734863, 25.0196266174316), point2=(39.0, 25.0))
        s1.Line(point1=(39.0, 25.0), point2=(39.5133323669434, 25.6798229217529))
        s1.Line(point1=(39.5133323669434, 25.6798229217529), point2=(40.0, 25.0))
        s1.Line(point1=(40.0, 25.0), point2=(40.6419143676758, 25.0002098083496))
        s1.AngularDimension(line1=g[12], line2=g[2], textPoint=(38.8539810180664,
                                                                24.9306106567383), value=60.0)
        s1.AngularDimension(line1=g[15], line2=g[4], textPoint=(40.1180953979492,
                                                                24.9036445617676), value=60.0)
        s1.ObliqueDimension(vertex1=v[32], vertex2=v[33], textPoint=(38.5657234191895,
                                                                     25.0804290771484), value=0.5*edge)
        s1.ObliqueDimension(vertex1=v[38], vertex2=v[39], textPoint=(40.3583068847656,
                                                                     24.9096355438232), value=0.5*edge)
        s1.AngularDimension(line1=g[13], line2=g[3], textPoint=(39.2173004150391,
                                                                25.0864219665527), value=60.0)
        s1.AngularDimension(line1=g[14], line2=g[3], textPoint=(39.8178329467773,
                                                                25.0744361877441), value=60.0)
        s1.AngularDimension(line1=g[8], line2=g[5], textPoint=(38.7706718444824,
                                                               23.4087715148926), value=60.0)
        s1.ObliqueDimension(vertex1=v[24], vertex2=v[25], textPoint=(38.6139450073242,
                                                                     23.1541728973389), value=0.5*edge)
        s1.AngularDimension(line1=g[7], line2=g[11], textPoint=(40.2067031860352,
                                                                23.3578510284424), value=60.0)
        s1.ObliqueDimension(vertex1=v[30], vertex2=v[31], textPoint=(40.4363212585449,
                                                                     23.1941814422607), value=0.5*edge)
        s1.AngularDimension(line1=g[10], line2=g[6], textPoint=(39.7802658081055,
                                                                23.1941814422607), value=60.0)
        s1.AngularDimension(line1=g[6], line2=g[9], textPoint=(39.1387901306152,
                                                               23.1832695007324), value=60.0)
        p = mdb.models['Model-1'].Part(name='Part-1',
                                               dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
        p = mdb.models['Model-1'].parts['Part-1']
        p.BaseWire(sketch=s1)
        s1.unsetPrimaryObject()
        p = mdb.models['Model-1'].parts['Part-1']
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        del mdb.models['Model-1'].sketches['__profile__']


    if structure == 'h':
        s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                                            sheetSize=200.0)
        g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
        s.setPrimaryObject(option=STANDALONE)
        s.Spot(point=(47.5, 35.0))
        s.Spot(point=(45.0, 30.0))
        s.Spot(point=(50.0, 30.0))
        s.Spot(point=(45.0, 25.0))
        s.Spot(point=(50.0, 25.0))
        s.Spot(point=(47.5, 20.0))
        s.Line(point1=(45.0, 25.0), point2=(45.0, 30.0))
        s.VerticalConstraint(entity=g[2], addUndoState=False)
        s.Line(point1=(45.0, 30.0), point2=(47.5, 35.0))
        s.Line(point1=(47.5, 35.0), point2=(50.0, 30.0))
        s.Line(point1=(50.0, 30.0), point2=(50.0, 25.0))
        s.VerticalConstraint(entity=g[5], addUndoState=False)
        s.Line(point1=(50.0, 25.0), point2=(47.5, 20.0))
        s.Line(point1=(47.5, 20.0), point2=(45.0, 25.0))
        s.Line(point1=(45.0, 30.0), point2=(50.0, 30.0))
        s.HorizontalConstraint(entity=g[8], addUndoState=False)
        s.Line(point1=(45.0, 25.0), point2=(50.0, 25.0))
        s.HorizontalConstraint(entity=g[9], addUndoState=False)
        s.ObliqueDimension(vertex1=v[6], vertex2=v[7], textPoint=(43.3270835876465,
                                                                  27.537712097168), value=edge)
        s.ObliqueDimension(vertex1=v[8], vertex2=v[9], textPoint=(44.6553268432617,
                                                                  30.3415641784668), value=edge)
        s.ObliqueDimension(vertex1=v[10], vertex2=v[11], textPoint=(48.2824516296387,
                                                                    28.7102317810059), value=edge)
        s.ObliqueDimension(vertex1=v[14], vertex2=v[15], textPoint=(47.8226776123047,
                                                                    22.8986129760742), value=edge)
        s.ObliqueDimension(vertex1=v[16], vertex2=v[17], textPoint=(44.7161979675293,
                                                                    24.3010540008545), value=edge)
        s.ObliqueDimension(vertex1=v[20], vertex2=v[21], textPoint=(45.2375106811523,
                                                                    25.2971286773682), value=edge)
        s.Spot(point=(46.5862312316895, 24.7652835845947))
        s.Spot(point=(46.1076545715332, 23.8426952362061))
        s.Spot(point=(44.8241958618164, 23.7450103759766))
        s.Spot(point=(44.2803535461426, 24.6350364685059))
        s.Spot(point=(44.323860168457, 26.3282566070557))
        s.Spot(point=(44.9003295898438, 27.1857204437256))
        s.Spot(point=(46.1729164123535, 27.1965751647949))
        s.Spot(point=(46.6623687744141, 26.3282566070557))
        s.Line(point1=(45.0, 25.0), point2=(44.2803535461426, 24.6350364685059))
        s.Line(point1=(44.2803535461426, 24.6350364685059), point2=(44.8241958618164,
                                                                    23.7450103759766))
        s.Line(point1=(44.8241958618164, 23.7450103759766), point2=(45.5,
                                                                    24.1339745962156))
        s.Line(point1=(45.5, 24.1339745962156), point2=(46.1076545715332,
                                                        23.8426952362061))
        s.Line(point1=(46.1076545715332, 23.8426952362061), point2=(46.5862312316895,
                                                                    24.7652835845947))
        s.Line(point1=(46.5862312316895, 24.7652835845947), point2=(46.0, 25.0))
        s.Line(point1=(45.0, 26.0), point2=(44.323860168457, 26.3282566070557))
        s.Line(point1=(44.323860168457, 26.3282566070557), point2=(44.9003295898438,
                                                                   27.1857204437256))
        s.Line(point1=(44.9003295898438, 27.1857204437256), point2=(45.5,
                                                                    26.8660254037844))
        s.Line(point1=(45.5, 26.8660254037844), point2=(46.1729164123535,
                                                        27.1965751647949))
        s.Line(point1=(46.1729164123535, 27.1965751647949), point2=(46.6623687744141,
                                                                    26.3282566070557))
        s.Line(point1=(46.6623687744141, 26.3282566070557), point2=(46.0, 26.0))
        s.AngularDimension(line1=g[10], line2=g[11], textPoint=(44.3927917480469,
                                                                24.5817852020264), value=90.0)
        s.AngularDimension(line1=g[11], line2=g[12], textPoint=(44.8614616394043,
                                                                23.8919429779053), value=90.0)
        s.AngularDimension(line1=g[10], line2=g[7], textPoint=(45.0137825012207,
                                                               24.8974761962891), value=90.0)
        s.ObliqueDimension(vertex1=v[30], vertex2=v[31], textPoint=(44.4923820495605,
                                                                    24.9676284790039), value=edge)
        s.AngularDimension(line1=g[15], line2=g[14], textPoint=(46.4900970458984,
                                                                24.7162456512451), value=90.0)
        s.AngularDimension(line1=g[13], line2=g[14], textPoint=(46.0741539001465,
                                                                24.0030193328857), value=90.0)
        s.AngularDimension(line1=g[13], line2=g[6], textPoint=(45.6347732543945,
                                                               24.2368640899658), value=90.0)
        s.ObliqueDimension(vertex1=v[36], vertex2=v[37], textPoint=(45.6582069396973,
                                                                    23.7691745758057), value=edge)
        s.AngularDimension(line1=g[19], line2=g[20], textPoint=(46.1500434875488,
                                                                27.127779006958), value=90.0)
        s.AngularDimension(line1=g[20], line2=g[21], textPoint=(46.5798606872559,
                                                                26.3327121734619), value=90.0)
        s.AngularDimension(line1=g[4], line2=g[21], textPoint=(46.0504493713379,
                                                               26.0685615539551), value=90.0)
        s.ObliqueDimension(vertex1=v[52], vertex2=v[53], textPoint=(46.3964042663574,
                                                                    26.0502548217773), value=edge)
        s.AngularDimension(line1=g[16], line2=g[17], textPoint=(44.408447265625,
                                                                26.3664321899414), value=90.0)
        s.AngularDimension(line1=g[17], line2=g[18], textPoint=(44.9307289123535,
                                                                27.1211700439453), value=90.0)
        s.AngularDimension(line1=g[3], line2=g[18], textPoint=(45.4062042236328,
                                                               26.8605766296387), value=90.0)
        s.ObliqueDimension(vertex1=v[46], vertex2=v[47], textPoint=(45.14013671875,
                                                                    26.8679523468018), value=edge)
        s.Spot(point=(44.1605949401855, 27.2073268890381))
        s.Spot(point=(44.6507415771484, 27.5763092041016))
        s.Spot(point=(46.3490447998047, 27.60205078125))
        s.Spot(point=(46.8176918029785, 27.3617839813232))
        s.Line(point1=(44.1605949401855, 27.2073268890381), point2=(44.6339745962156,
                                                                    27.3660254037844))
        s.Line(point1=(44.6339745962156, 27.3660254037844), point2=(44.6507415771484,
                                                                    27.5763092041016))
        s.AngularDimension(line1=g[22], line2=g[17], textPoint=(44.4572639465332,
                                                                27.2244873046875), value=60.0)
        s.ObliqueDimension(vertex1=v[58], vertex2=v[59], textPoint=(44.2207908630371,
                                                                    27.2116165161133), value=0.5*edge)
        s.AngularDimension(line1=g[23], line2=g[22], textPoint=(44.5475540161133,
                                                                27.4132690429688), value=90.0)
        s.ObliqueDimension(vertex1=v[60], vertex2=v[61], textPoint=(44.7625274658203,
                                                                    27.4690456390381), value=0.5*edge)
        s.Line(point1=(46.3490447998047, 27.60205078125), point2=(46.3660254037844,
                                                                  27.3660254037844))
        s.Line(point1=(46.3660254037844, 27.3660254037844), point2=(46.8176918029785,
                                                                    27.3617839813232))
        s.AngularDimension(line1=g[25], line2=g[20], textPoint=(46.486629486084,
                                                                27.2545223236084), value=60.0)
        s.AngularDimension(line1=g[24], line2=g[25], textPoint=(46.4436340332031,
                                                                27.4132690429688), value=90.0)
        s.ObliqueDimension(vertex1=v[64], vertex2=v[65], textPoint=(46.6973075866699,
                                                                    27.1086444854736), value=0.5*edge)
        s.ObliqueDimension(vertex1=v[62], vertex2=v[63], textPoint=(46.2544593811035,
                                                                    27.4947891235352), value=0.5*edge)
        s.Spot(point=(44.1319313049316, 23.6154727935791))
        s.Spot(point=(44.620231628418, 23.068775177002))
        s.Spot(point=(46.8354415893555, 23.6273574829102))
        s.Spot(point=(46.3650054931641, 23.1103706359863))
        s.Line(point1=(44.1319313049316, 23.6154727935791), point2=(44.6339745962156,
                                                                    23.6339745962156))
        s.Line(point1=(44.6339745962156, 23.6339745962156), point2=(44.620231628418,
                                                                    23.068775177002))
        s.Line(point1=(46.8354415893555, 23.6273574829102), point2=(46.3660254037844,
                                                                    23.6339745962156))
        s.Line(point1=(46.3660254037844, 23.6339745962156), point2=(46.3650054931641,
                                                                    23.1103706359863))
        s.AngularDimension(line1=g[26], line2=g[11], textPoint=(44.4813232421875,
                                                                23.7532444000244), value=60.0)
        s.ObliqueDimension(vertex1=v[70], vertex2=v[71], textPoint=(44.306510925293,
                                                                    23.4872150421143), value=0.5*edge)
        s.AngularDimension(line1=g[27], line2=g[26], textPoint=(44.5337677001953,
                                                                23.5482711791992), value=90.0)
        s.ObliqueDimension(vertex1=v[72], vertex2=v[73], textPoint=(44.7653923034668,
                                                                    23.3258533477783), value=0.5*edge)
        s.AngularDimension(line1=g[28], line2=g[14], textPoint=(46.5135154724121,
                                                                23.7532444000244), value=60.0)
        s.ObliqueDimension(vertex1=v[74], vertex2=v[75], textPoint=(46.6271438598633,
                                                                    23.4654102325439), value=0.5*edge)
        s.AngularDimension(line1=g[29], line2=g[28], textPoint=(46.4654426574707,
                                                                23.5657157897949), value=90.0)
        s.ObliqueDimension(vertex1=v[76], vertex2=v[77], textPoint=(46.2294464111328,
                                                                    23.3127708435059), value=0.5*edge)
        p = mdb.models['Model-1'].Part(name='Part-1',
                                               dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
        p = mdb.models['Model-1'].parts['Part-1']
        p.BaseWire(sketch=s)
        s.unsetPrimaryObject()
        p = mdb.models['Model-1'].parts['Part-1']
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
    if structure == 'j':
        getWarningReply('The chosen strucutre is not yet available.\n'
                        'Please choose one of the following structures: \n'
                        "'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'\n"
                        , buttons=(YES,))
        main()

    # TODO create k: SHD Structure
    if structure == 'k':
        getWarningReply('The chosen strucutre is not yet available.\n'
                        'Please choose one of the following structures: \n'
                        "'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'\n"
                        , buttons=(YES,))
        main()


#mode, young_modulus, poisson_rate, c10, c01, d1 = select_material()

def select_material():
    # TODO this is fucking ugly, change!
    young_modulus = None
    poisson_rate = None
    c10 = None
    c01 = None
    d1 = None
    try:
        model = str(getInput("You can choose from the following material models\n"
                               "'linear', 'nonlinear'\n"
                               "Please enter the desired material model: ")).lower()
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

    except:
        getWarningReply('The chosen value is not available.\n'
                        'Please choose one of the following material models: \n'
                        "'linear', 'nonlinear'\n"
                        , buttons=(YES,))
        section = select_material()

    return model, young_modulus, poisson_rate, c10, c01, d1

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



# section, width, width_2, height, radius, c, d, thickness, thickness_2, thickness_3, I = select_cross_section()

def select_cross_section(edge):
    # TODO this is fucking ugly, change!
    possible_sections = ['box', 'pipe', 'circular', 'rectangular', 'hexagonal', 'trapezoidal', 'i', 'l', 't']
    section = None
    width = None
    width_2 = None
    height = None
    radius = None
    c = None
    d = None
    thickness = None
    thickness_2 = None
    thickness_3 = None
    I = None

    try:
        section = str(getInput("You can choose from the following cross sections\n"
                               "'box', 'pipe', 'circular', 'rectangular', 'hexagonal', 'trapezoidal', 'I', 'L', 'T'\n"
                               "Please enter the desired cross section profile: ")).lower()

        if section == 'box':
            fields = (('Width [mm]:', '5'), ('Poisson Rate:', '0.3'))
            young_modulus, poisson_rate = getInputs(fields=fields, label='Specify Material dimensions:',
                                                    dialogTitle='Create Material', )
            if float(thickness) <= float(width)/2.0 and float(thickness) <= float(height)/2.0:
                if float(width) <= float(edge)/3.0 and float(height) <= float(edge)/3.0:
                    pass
            else:
                getWarningReply('The thickness MUST NOT be equal or greater than half the width/height of the cross section.\n'
                                'AND\n'
                                'The width and height MUST NOT be greater than the edge length divided by three\n'
                                'Therefore:\n'
                                'Max width/height: ', float(edge)/3.0,'\n',
                                'Max thickness: ', float(width)/2.0,'\n',
                                'Please choose the length, width and thickness according to this.\n'
                                , buttons=(YES,))
                section = select_material()


    except:
        getWarningReply('The chosen value is not available.\n'
                        'Please choose one of the following sections: \n'
                        "'box', 'pipe', 'circular', 'rectangular', 'hexagonal', 'trapezoidal', 'I', 'L', 'T'\n"
                        , buttons=(YES,))
        section = select_cross_section()

if __name__ == "__main__":
    main()
else:
    print("Please run main.py via Abaqus CAE by using 'File > Run Script... > main.py'")

