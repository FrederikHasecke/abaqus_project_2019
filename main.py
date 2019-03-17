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

# Import sub modules for the different lattices
from utilities import *

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
    # Beam Section. The user can pick between the provided standard beam sections
    # A second getInputs window will open after the selection for the provided variables of the cross sections
    # There is an additional condition which prevents the beam section to be too large and to overlap at areas which
    # are not supposed to overlap. This is not visible in the visualization but unphysical conditions are not desired.
    # You can find additional information in the documentation attached to this code
    #section, width, width_2, height, radius, c, d, thickness, thickness_2, thickness_3, I = select_cross_section()

    # Forth User Input:
    # Material. The user can decide between elastic or hyperelastic Mooney-Rivlin models and enter
    # any desired material values. Values for the most common materials are provided in the accompanying documentation
    #mode, young_modulus, poisson_rate, c10, c01, d1 = select_material()

    # Fifth User Input:
    # Loading Conditions. The User can choose between uniaxial and shear loading as well as decide the provided force
    #loadcase, force = select_loading()


# This function querys the user to choose between the 11 possible Structures and returns the chosen value.
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

    # TODO Create structure if statesments for all 11 Structures
    if structure == 'a':
        Square.create(structure, edge)


    if structure == 'b':
        pass
    if structure == 'c':
        pass
    if structure == 'd':
        pass
    if structure == 'e':
        pass
    if structure == 'f':
        pass
    if structure == 'g':
        pass
    if structure == 'h':
        pass
    if structure == 'i':
        pass
    if structure == 'j':
        pass
    if structure == 'k':
        pass


def select_cross_section():
    possible_sections = ['box', 'pipe', 'circular', 'rectangular', 'hexagonal', 'trapezoidal', 'i', 'l', 't']
    try:
        section = str(getInput("You can choose from the following cross sections\n"
                               "'box', 'pipe', 'circular', 'rectangular', 'hexagonal', 'trapezoidal', 'I', 'L', 'T'\n"
                               "Please enter the desired cross section profile: ")).lower()
    except:
        getWarningReply('The chosen value is not available.\n'
                        'Please choose one of the following sections: \n'
                        "'box', 'pipe', 'circular', 'rectangular', 'hexagonal', 'trapezoidal', 'I', 'L', 'T'\n"
                        , buttons=(YES,))
        section = select_cross_section()

if __name__ == "__main__":
    main()
else:
    print("Please run main.py in the Abaqus CAE scripting interface")

