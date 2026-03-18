####################################################################################
# CMOS INVERTER 2D Device Simulation using DEVSIM
# This script simulates a 2D CMOS inverter with LDD (Lightly Doped Drain) structure
# Contains both NMOS and PMOS transistors connected in inverter configuration
# Generates Voltage Transfer Characteristic (VTC) curve
####################################################################################

#==================================================================================
# IMPORT SECTION
#==================================================================================

import numpy as np  # NumPy library for numerical operations (e.g., sqrt, exp)
import csv  # CSV library for writing simulation results to CSV files

# Core DEVSIM functions for mesh creation, device setup, and solving
from devsim import (
    add_gmsh_contact,       # Defines electrical contacts on the mesh from GMSH
    add_gmsh_interface,     # Defines interfaces between different regions (e.g., Si/SiO2)
    add_gmsh_region,        # Assigns material regions from GMSH mesh
    create_device,          # Creates the device data structure from the mesh
    create_gmsh_mesh,       # Loads a GMSH mesh file into DEVSIM
    finalize_mesh,          # Finalizes mesh after all regions/contacts are defined
    node_model,             # Creates node-based mathematical models (equations at nodes)
    write_devices,          # Exports device data to files (VTK, Tecplot, etc.)
    set_parameter,          # Sets global or region-specific parameters
    element_from_edge_model,# Converts edge models to element models for visualization
    get_contact_list,       # Retrieves list of all contacts on a device
    get_region_list,        # Retrieves list of regions associated with a contact
    get_contact_current,    # Gets current flowing through a contact
    get_parameter,          # Retrieves parameter values
    set_node_values,        # Sets initial values for node solutions
    solve,                  # Solves the device equations (DC, AC, or transient)
    element_model,          # Creates element-based mathematical models
    add_circuit_node,       # Adds a circuit node for mixed device-circuit simulation
    get_circuit_node_value, # Gets voltage at a circuit node
)

# Pre-built physics models from DEVSIM's simple_physics package
from devsim.python_packages.simple_physics import (
    GetContactBiasName,             # Returns the parameter name for contact bias voltage
    SetOxideParameters,             # Sets standard oxide material parameters
    CreateSiliconPotentialOnly,     # Creates Poisson equation for silicon (no carriers)
    CreateSiliconPotentialOnlyContact,  # Creates contact boundary conditions for potential
    CreateSiliconDriftDiffusion,    # Creates full drift-diffusion equations (Poisson + continuity)
    CreateSiliconDriftDiffusionAtContact,  # Creates contact BCs for drift-diffusion
    CreateOxidePotentialOnly,       # Creates Poisson equation for oxide region
    CreateSiliconOxideInterface,    # Creates Si/SiO2 interface boundary conditions
    CreateOxideContact,             # Creates contact boundary conditions on oxide (gate)
)

# Utility functions for voltage ramping and current output
from devsim.python_packages.ramp import rampbias, printAllCurrents
# rampbias: Gradually ramps voltage on a contact to help convergence
# printAllCurrents: Prints currents at all contacts

# Model creation utilities
from devsim.python_packages.model_create import (
    CreateSolution,             # Creates a solution variable (Potential, Electrons, Holes)
    CreateNodeModel,            # Creates a node model with a given equation
    CreateNodeModelDerivative,  # Creates derivatives of node models for Newton solver
)

#==================================================================================
# DEVICE NAME DEFINITION
#==================================================================================

device = "inv2d"  # Unique identifier for this CMOS inverter device in DEVSIM

#==================================================================================
# MESH IMPORT AND REGION/CONTACT DEFINITION
# The mesh was created externally using GMSH for 2D CMOS inverter geometry
# Contains both NMOS and PMOS transistors with shared output node
#==================================================================================

# Load the GMSH mesh file (.msh format) into DEVSIM
# Mesh contains the complete CMOS inverter structure
create_gmsh_mesh(file="LDD2D_inverter.msh", mesh="inv2d")

# Define semiconductor and oxide regions by mapping GMSH physical groups
# Silicon region: contains both NMOS and PMOS active areas
add_gmsh_region(mesh="inv2d", gmsh_name="bulk", region="bulk", material="Silicon")

# Oxide region: gate dielectric for both transistors
add_gmsh_region(mesh="inv2d", gmsh_name="oxide", region="oxide", material="Oxide")

#==================================================================================
# INVERTER CONTACT DEFINITIONS
# Standard CMOS inverter has: V_dd (power), Ground, V_in (input), V_out (output)
#==================================================================================

# V_out: Output node - connects NMOS drain to PMOS drain
# This is a floating node whose voltage is determined by circuit operation
add_gmsh_contact(mesh="inv2d", gmsh_name="V_out", region="bulk", 
                 name="V_out", material="metal")

# V_in: Input gate - controls both NMOS and PMOS gates (tied together)
# Located on oxide region
add_gmsh_contact(mesh="inv2d", gmsh_name="V_in", region="oxide", 
                 name="V_in", material="metal")

# V_dd: Power supply - connects to PMOS source
# Typically set to positive voltage (e.g., 3V, 5V)
add_gmsh_contact(mesh="inv2d", gmsh_name="V_dd", region="bulk", 
                 name="V_dd", material="metal")

# Ground: Ground reference - connects to NMOS source
# Fixed at 0V
add_gmsh_contact(mesh="inv2d", gmsh_name="Ground", region="bulk", 
                 name="Ground", material="metal")

# Define the Si/SiO2 interface - critical for MOS operation
# Interface where inversion layer forms for both NMOS and PMOS
add_gmsh_interface(mesh="inv2d", gmsh_name="oxide_bulk_interface",
                   region0="bulk", region1="oxide", name="oxide_bulk")

# Finalize mesh: completes mesh setup, creates internal data structures
finalize_mesh(mesh="inv2d")

# Create the device object from the finalized mesh
create_device(mesh="inv2d", device="inv2d")

#==================================================================================
# CMOS INVERTER GEOMETRY PARAMETERS
# All dimensions are in centimeters (cm) - DEVSIM default unit system
#==================================================================================

#----------------------------------------------------------------------------------
# NMOS TRANSISTOR PARAMETERS
#----------------------------------------------------------------------------------
channel_length = 5e-5       # NMOS channel length: 0.5 μm
extension_length = 4e-6     # NMOS LDD extension: 40 nm each side
oxide_thickness = 1e-6      # NMOS gate oxide thickness: 10 nm
source_contact = 1e-5       # NMOS source contact width: 100 nm
drain_contact = 1e-5        # NMOS drain contact width: 100 nm

#----------------------------------------------------------------------------------
# PMOS TRANSISTOR PARAMETERS
#----------------------------------------------------------------------------------
channel_length_2 = 5e-5     # PMOS channel length: 0.5 μm
extension_length_2 = 4e-6   # PMOS LDD extension: 40 nm each side
oxide_thickness_2 = 1e-6    # PMOS gate oxide thickness: 10 nm
source_contact_2 = 1e-5     # PMOS source contact width: 100 nm
drain_contact_2 = 1e-5      # PMOS drain contact width: 100 nm

#----------------------------------------------------------------------------------
# COMMON STRUCTURE PARAMETERS
#----------------------------------------------------------------------------------
bulk_height = 5e-5          # Silicon substrate depth: 0.5 μm
body_source_space = 5e-6    # Spacing between body contact and source: 50 nm
body_contact = 1e-5         # Body contact width: 100 nm
STL_length = 1e-5           # STI (Shallow Trench Isolation) length between NMOS and PMOS: 100 nm
                            # Separates N-well from P-well

#==================================================================================
# NMOS DOPING PROFILE PARAMETERS
# NMOS: N-type source/drain in P-well
#==================================================================================

Source_Doping = 5e19        # NMOS N+ source doping: heavily doped for ohmic contact
Drain_Doping = 5e19         # NMOS N+ drain doping: heavily doped for ohmic contact
Body_Doping = 5e19          # NMOS P+ body contact doping: ensures good substrate contact
Pwell_Doping = 5e16         # P-well doping: moderate doping under NMOS
Bulk_Doping = 1e15          # P-type substrate background doping: lightly doped
LDD_Doping = 5e17           # NMOS LDD (N-): reduces hot carrier effects

Lext = 1e-6                 # NMOS S/D junction decay length: 10 nm
Lext_well = 1e-5            # P-well junction decay length: 100 nm

Interface_charge_Nmos = 0   # NMOS interface charge (for Vth adjustment)

#==================================================================================
# PMOS DOPING PROFILE PARAMETERS  
# PMOS: P-type source/drain in N-well
#==================================================================================

Source_Doping_p = 5e19      # PMOS P+ source doping: heavily doped for ohmic contact
Drain_Doping_p = 5e19       # PMOS P+ drain doping: heavily doped for ohmic contact
Body_Doping_p = 5e19        # PMOS N+ body contact doping: ensures good N-well contact
Nwell_Doping = 5e16         # N-well doping: moderate doping under PMOS
LDD_Doping_p = 5e17         # PMOS LDD (P-): reduces hot carrier effects

Lext_p = 1e-6               # PMOS S/D junction decay length: 10 nm
Lext_well_p = 1e-5          # N-well junction decay length: 100 nm

Interface_charge_Pmos = 0   # PMOS interface charge (for Vth adjustment)

#==================================================================================
# NMOS COORDINATE DEFINITIONS
# Define x-y boundaries for NMOS doping regions
# NMOS is on the left side of the inverter
#==================================================================================

# P-well/Body contact region (left of NMOS source)
x_min_well = -body_source_space - body_contact  # Left edge of body contact
x_max_well = -body_source_space                  # Right edge of body contact

# NMOS N+ source region
x_min = 0               # Source left edge (at origin)
x_max = source_contact  # Source right edge

# NMOS source-side LDD region
x_min_1 = source_contact                    # LDD starts where source ends
x_max_1 = source_contact + extension_length # LDD extends by extension_length

# NMOS N+ drain region (connects to V_out)
x_min_2 = source_contact + extension_length * 2 + channel_length  # Drain start
x_max_2 = source_contact + extension_length * 2 + channel_length + drain_contact  # Drain end

# NMOS drain-side LDD region
x_min_3 = source_contact + extension_length + channel_length      # Drain LDD start
x_max_3 = source_contact + extension_length * 2 + channel_length  # Drain LDD end

# Silicon surface (where gate oxide sits)
y_max = bulk_height

#==================================================================================
# REGISTER NMOS PARAMETERS FOR DEVSIM EQUATIONS
#==================================================================================

# Well boundaries
set_parameter(name="x_min_well", value=x_min_well)  # P-well left boundary
set_parameter(name="x_max_well", value=x_max_well)  # P-well right boundary
set_parameter(name="y_max", value=y_max)            # Silicon surface

# NMOS source region boundaries
set_parameter(name="x_max", value=x_max)
set_parameter(name="x_min", value=x_min)

# NMOS source LDD boundaries
set_parameter(name="x_max_1", value=x_max_1)
set_parameter(name="x_min_1", value=x_min_1)

# NMOS drain region boundaries
set_parameter(name="x_max_2", value=x_max_2)
set_parameter(name="x_min_2", value=x_min_2)

# NMOS drain LDD boundaries
set_parameter(name="x_max_3", value=x_max_3)
set_parameter(name="x_min_3", value=x_min_3)

# NMOS doping concentrations
set_parameter(name="Source_Doping", value=Source_Doping)
set_parameter(name="Drain_Doping", value=Drain_Doping)
set_parameter(name="Body_Doping", value=Body_Doping)
set_parameter(name="Pwell_Doping", value=Pwell_Doping)
set_parameter(name="Bulk_Doping", value=Bulk_Doping)
set_parameter(name="LDD_Doping", value=LDD_Doping)

# NMOS decay lengths
set_parameter(name="Lext", value=Lext)
set_parameter(name="Lext_well", value=Lext_well)

# Interface charges
set_parameter(name="Interface_charge_Nmos", value=Interface_charge_Nmos)
set_parameter(name="Interface_charge_Pmos", value=Interface_charge_Pmos)

#==================================================================================
# DOPING PROFILE FUNCTION
# Creates box-shaped doping with erfc decay from surface
#==================================================================================

def create_doping_box(
    name_prefix,    # Name for this doping model
    doping_value,   # Doping concentration (parameter name or value)
    x_min,          # Left boundary (parameter name)
    x_max,          # Right boundary (parameter name)
    y_max,          # Top boundary - surface (parameter name)
    decay_len,      # Characteristic decay length (parameter name or value)
    region="bulk",  # Region to apply doping
    device="inv2d"  # Device name
):
    """
    Creates a box-shaped doping profile with erfc decay from surface.
    Models realistic diffused junction profiles from ion implantation.
    
    The erfc (complementary error function) profile:
    - Maximum at surface (y = y_max)
    - Decays into bulk following Gaussian diffusion physics
    - decay_len controls junction depth/abruptness
    """
    # DEVSIM equation with nested conditionals for box boundaries
    equation = (
        f"ifelse((x >= {x_min}), "           # Check left boundary
        f"ifelse((x <= {x_max}), "           # Check right boundary
        f"ifelse((y <= {y_max}), "           # Check below surface
        f"{doping_value} * erfc(({y_max} - y)/{decay_len}), 0), "  # erfc decay
        f"0), 0)"                            # Outside: zero doping
    )

    # Create node model
    node_model(
        name=name_prefix,
        device=device,
        region=region,
        equation=equation
    )

#==================================================================================
# CREATE NMOS DOPING PROFILES
#==================================================================================

# P-well: extends under entire NMOS device
create_doping_box("Pwell_Doping", "Pwell_Doping", "x_min_well", "x_max_2", "y_max", "Lext_well")

# NMOS N+ source
create_doping_box("SourceDoping1", "Source_Doping", "x_min", "x_max", "y_max", "Lext")

# NMOS source-side LDD (N-)
create_doping_box("SourceDoping2", "LDD_Doping", "x_min_1", "x_max_1", "y_max", "Lext")

# NMOS N+ drain
create_doping_box("DrainDoping1", "Drain_Doping", "x_min_2", "x_max_2", "y_max", "Lext")

# NMOS drain-side LDD (N-)
create_doping_box("DrainDoping2", "LDD_Doping", "x_min_3", "x_max_3", "y_max", "Lext")

# NMOS P+ body contact
create_doping_box("Body_Contact_Doping", "Body_Doping", "x_min_well", "x_max_well", "y_max", "Lext")

# NMOS interface charge (under gate)
create_doping_box("Interface_charge_Nmos", "Interface_charge_Nmos", "x_max_1", "x_min_3", "y_max", "1e-9")

# Combine NMOS source doping components
node_model(
    name="SourceDoping",
    device=device,
    region="bulk",
    equation="SourceDoping1 + SourceDoping2"  # N+ source + source LDD
)

# Combine NMOS drain doping components
node_model(
    name="DrainDoping",
    device=device,
    region="bulk",
    equation="DrainDoping1 + DrainDoping2"    # N+ drain + drain LDD
)

#==================================================================================
# PMOS COORDINATE DEFINITIONS
# Define x-y boundaries for PMOS doping regions
# PMOS is on the right side of the inverter, separated by STI
#==================================================================================

# PMOS starts after NMOS drain + STI isolation
# x_base = source_contact + extension_length*2 + channel_length + drain_contact + STL_length

# PMOS P+ source region (connects to V_dd)
x_min_p = source_contact + extension_length * 2 + channel_length + drain_contact + STL_length
x_max_p = x_min_p + source_contact_2

# PMOS source-side LDD region
x_min_1_p = x_max_p
x_max_1_p = x_max_p + extension_length_2

# PMOS drain-side LDD region (note: PMOS source/drain naming follows current flow)
x_min_3_p = x_max_1_p + channel_length_2
x_max_3_p = x_min_3_p + extension_length_2

# PMOS P+ drain region (connects to V_out)
x_min_2_p = x_max_3_p
x_max_2_p = x_min_2_p + drain_contact_2

# PMOS N+ body contact (N-well contact)
x_min_body_p = x_max_2_p + body_source_space
x_max_well_p = x_min_body_p + body_contact

#==================================================================================
# REGISTER PMOS PARAMETERS FOR DEVSIM EQUATIONS
#==================================================================================

# N-well/body contact boundaries
set_parameter(name="x_min_body_p", value=x_min_body_p)
set_parameter(name="x_max_well_p", value=x_max_well_p)

# PMOS source region boundaries
set_parameter(name="x_max_p", value=x_max_p)
set_parameter(name="x_min_p", value=x_min_p)

# PMOS source LDD boundaries
set_parameter(name="x_max_1_p", value=x_max_1_p)
set_parameter(name="x_min_1_p", value=x_min_1_p)

# PMOS drain region boundaries
set_parameter(name="x_max_2_p", value=x_max_2_p)
set_parameter(name="x_min_2_p", value=x_min_2_p)

# PMOS drain LDD boundaries
set_parameter(name="x_max_3_p", value=x_max_3_p)
set_parameter(name="x_min_3_p", value=x_min_3_p)

# PMOS doping concentrations
set_parameter(name="Source_Doping_p", value=Source_Doping_p)
set_parameter(name="Drain_Doping_p", value=Drain_Doping_p)
set_parameter(name="Body_Doping_p", value=Body_Doping_p)
set_parameter(name="Bulk_Doping", value=Bulk_Doping)
set_parameter(name="Nwell_Doping", value=Nwell_Doping)
set_parameter(name="LDD_Doping_p", value=LDD_Doping_p)

# PMOS decay lengths
set_parameter(name="Lext_p", value=Lext_p)
set_parameter(name="Lext_well_p", value=Lext_well_p)

#==================================================================================
# CREATE PMOS DOPING PROFILES
#==================================================================================

# N-well: extends under entire PMOS device
create_doping_box("Nwell_Doping", "Nwell_Doping", "x_min_p", "x_max_well_p", "y_max", "Lext_well_p")

# PMOS P+ source (connects to V_dd)
create_doping_box("SourceDoping1_p", "Source_Doping_p", "x_min_p", "x_max_p", "y_max", "Lext_p")

# PMOS source-side LDD (P-)
create_doping_box("SourceDoping2_p", "LDD_Doping_p", "x_min_1_p", "x_max_1_p", "y_max", "Lext_p")

# PMOS P+ drain (connects to V_out)
create_doping_box("DrainDoping1_p", "Drain_Doping_p", "x_min_2_p", "x_max_2_p", "y_max", "Lext_p")

# PMOS drain-side LDD (P-)
create_doping_box("DrainDoping2_p", "LDD_Doping_p", "x_min_3_p", "x_max_3_p", "y_max", "Lext_p")

# PMOS N+ body contact (N-well tie)
create_doping_box("Body_Contact_Doping_p", "Body_Doping_p", "x_min_body_p", "x_max_well_p", "y_max", "Lext")

# PMOS interface charge (under gate)
create_doping_box("Interface_charge_Pmos", "Interface_charge_Pmos", "x_max_1_p", "x_min_3_p", "y_max", "1e-9")

# Combine PMOS source doping components
node_model(
    name="SourceDoping_pp",
    device=device,
    region="bulk",
    equation="SourceDoping1_p + SourceDoping2_p"  # P+ source + source LDD
)

# Combine PMOS drain doping components
node_model(
    name="DrainDoping_pp",
    device=device,
    region="bulk",
    equation="DrainDoping1_p + DrainDoping2_p"    # P+ drain + drain LDD
)

#==================================================================================
# NET DOPING CALCULATION
# Combine all doping contributions for CMOS structure
# NMOS: N-type S/D in P-well | PMOS: P-type S/D in N-well
#==================================================================================

# Total interface charge (both transistors)
node_model(
    name="Interface_charge",
    device=device,
    region="bulk",
    equation="Interface_charge_Nmos + Interface_charge_Pmos",
)

# Bulk background doping model
node_model(
    name="Bulk_Doping",
    device=device,
    region="bulk",
    equation="Bulk_Doping",  # P-type substrate
)

# Total DONOR concentration (N-type dopants)
# Includes: NMOS S/D, N-well, PMOS N+ body contact
node_model(
    name="Donors",
    device=device,
    region="bulk",
    equation="DrainDoping + SourceDoping + Nwell_Doping + Interface_charge + Body_Contact_Doping_p + 1",
    # +1 prevents numerical issues in fully P-type regions
)

# Total ACCEPTOR concentration (P-type dopants)
# Includes: PMOS S/D, P-well, NMOS P+ body contact, bulk
node_model(
    name="Acceptors",
    device=device,
    region="bulk",
    equation="DrainDoping_pp + SourceDoping_pp + Bulk_Doping + Pwell_Doping + Body_Contact_Doping",
)

# Net doping = Donors - Acceptors
# Positive = N-type | Negative = P-type
node_model(
    name="NetDoping", 
    device=device, 
    region="bulk", 
    equation="Donors - Acceptors"
)

#==================================================================================
# REGION DEFINITIONS FOR PHYSICS
#==================================================================================

silicon_regions = ("bulk",)       # Regions with drift-diffusion
oxide_regions = ("oxide",)        # Regions with only Poisson equation
regions = ("bulk", "oxide")       # All regions
interfaces = ("oxide_bulk",)      # Si/SiO2 interfaces

#==================================================================================
# CIRCUIT NODE DEFINITION
# V_out is a floating circuit node - its voltage is determined by
# the balance of currents from NMOS and PMOS
#==================================================================================

circuit_contacts = ("V_out",)     # Contacts that are circuit nodes (not fixed voltage)

# Create circuit node for V_out
# This allows the solver to determine V_out based on current continuity
add_circuit_node(name="V_out_bias")

#==================================================================================
# CREATE SOLUTION VARIABLES
#==================================================================================

# Initialize potential variable for all regions
for i in regions:
    CreateSolution(device, i, "Potential")

#==================================================================================
# FUNDAMENTAL PHYSICAL CONSTANTS AND MATERIAL PARAMETERS
#==================================================================================

q = 1.6e-19         # Elementary charge in Coulombs
k = 1.3806503e-23   # Boltzmann constant in J/K
eps_0 = 8.85e-14    # Vacuum permittivity in F/cm
T = 300             # Temperature in Kelvin (room temperature)
eps_si = 11.1       # Relative permittivity of silicon
eps_ox = 3.9        # Relative permittivity of SiO2
mu_n = 1000         # Electron mobility in cm²/V·s
mu_p = 500          # Hole mobility in cm²/V·s
NC = 2.8e19         # Conduction band effective DOS in /cm³
NV = 1.04e19        # Valence band effective DOS in /cm³
Eg = 1.08           # Silicon bandgap energy in eV

# Intrinsic carrier concentration
n_i = np.sqrt(NC * NV) * np.exp(-Eg / (2 * k * T / q))  # ≈ 1.5×10¹⁰ /cm³

# SRH recombination lifetimes
taun = 1e-7         # Electron lifetime in seconds
taup = 1e-7         # Hole lifetime in seconds

#==================================================================================
# SILICON REGION PHYSICS SETUP
#==================================================================================

for i in silicon_regions:
    # Create Poisson equation for potential
    CreateSiliconPotentialOnly(device, i)
    
    # Set material parameters
    set_parameter(device=device, region=i, name="Permittivity", value=eps_si * eps_0)
    set_parameter(device=device, region=i, name="ElectronCharge", value=q)
    set_parameter(device=device, region=i, name="n_i", value=n_i)
    set_parameter(device=device, region=i, name="NC", value=NC)
    set_parameter(device=device, region=i, name="NV", value=NV)
    set_parameter(device=device, region=i, name="Eg", value=Eg)
    set_parameter(device=device, region=i, name="T", value=T)
    set_parameter(device=device, region=i, name="KT", value=k * T)
    set_parameter(device=device, region=i, name="V_t", value=k * T / q)  # Thermal voltage
    set_parameter(device=device, region=i, name="mu_n", value=mu_n)
    set_parameter(device=device, region=i, name="mu_p", value=mu_p)
    
    # SRH recombination parameters
    set_parameter(device=device, region=i, name="n1", value=n_i)
    set_parameter(device=device, region=i, name="p1", value=n_i)
    set_parameter(device=device, region=i, name="taun", value=taun)
    set_parameter(device=device, region=i, name="taup", value=taup)

#==================================================================================
# OXIDE REGION PHYSICS SETUP
#==================================================================================

for reg in oxide_regions:
    # Set oxide material parameters
    SetOxideParameters(device, reg, 300)
    
    # Create Poisson equation for oxide
    CreateOxidePotentialOnly(device, reg, "log_damp")
    
    # Initialize V_in (gate) contact bias to 0V
    set_parameter(device=device, name=GetContactBiasName("V_in"), value=0.0)
    
    # Create gate contact boundary condition
    CreateOxideContact(device, reg, "V_in")

#==================================================================================
# CONTACT BOUNDARY CONDITIONS
# Different handling for circuit nodes vs. fixed-voltage contacts
#==================================================================================

contacts = get_contact_list(device=device)

for c in contacts:
    reg = get_region_list(device=device, contact=c)[0]
    
    # Skip contacts on oxide (gate handled separately)
    if reg not in silicon_regions:
        continue
    
    if c in circuit_contacts:  # V_out is a circuit node
        # Circuit contact: voltage determined by current balance
        # is_circuit=True enables mixed device-circuit simulation
        CreateSiliconPotentialOnlyContact(device, reg, c, is_circuit=True)
    else:
        # Fixed voltage contact: V_dd, Ground
        CreateSiliconPotentialOnlyContact(device, reg, c, is_circuit=False)
        set_parameter(device=device, name=GetContactBiasName(c), value=0.0)

#==================================================================================
# INTERFACE BOUNDARY CONDITIONS
#==================================================================================

for i in interfaces:
    CreateSiliconOxideInterface(device, i)

#==================================================================================
# INITIAL EQUILIBRIUM SOLVE (POTENTIAL ONLY)
#==================================================================================

# Solve Poisson equation with relaxed tolerances
solve(type="dc", absolute_error=1e5, relative_error=1e2, maximum_iterations=1000)

# Export initial potential for visualization
write_devices(file="LDD2D_inverter_potential.dat", type="tecplot")

#==================================================================================
# ADD CARRIER TRANSPORT EQUATIONS (DRIFT-DIFFUSION)
#==================================================================================

for i in silicon_regions:
    # Create carrier concentration variables
    CreateSolution(device, i, "Electrons")
    CreateSolution(device, i, "Holes")
    
    # Initialize from equilibrium values
    set_node_values(device=device, region=i, name="Electrons", 
                    init_from="IntrinsicElectrons")
    set_node_values(device=device, region=i, name="Holes", 
                    init_from="IntrinsicHoles")
    
    # Create drift-diffusion equations
    CreateSiliconDriftDiffusion(device, i, "mu_n", "mu_p")

#==================================================================================
# CONTACT BOUNDARY CONDITIONS FOR DRIFT-DIFFUSION
#==================================================================================

for c in contacts:
    tmp = get_region_list(device=device, contact=c)
    r = tmp[0]
    
    if r in silicon_regions:
        if c in circuit_contacts:
            # V_out: Circuit node - voltage found by solver
            CreateSiliconDriftDiffusionAtContact(device, r, c, is_circuit=True)
        else:
            # V_dd, Ground: Fixed voltage contacts
            CreateSiliconDriftDiffusionAtContact(device, r, c, is_circuit=False)

#==================================================================================
# SOLVE DRIFT-DIFFUSION
#==================================================================================

#solve(type="dc", absolute_error=1e5, relative_error=1, maximum_iterations=2000)
solve(type="dc", absolute_error=1e5, relative_error=1, maximum_iterations=5000)
#==================================================================================
# POST-PROCESSING: VISUALIZATION MODELS
#==================================================================================

for r in silicon_regions:
    # Log-scale electron concentration for visualization
    node_model(device=device, region=r, name="logElectrons", 
               equation="log(Electrons)/log(10)")
    
    # Convert edge models to element models for ParaView
    element_from_edge_model(edge_model="ElectricField", device=device, region=r)
    element_from_edge_model(edge_model="ElectronCurrent", device=device, region=r)
    element_from_edge_model(edge_model="HoleCurrent", device=device, region=r)
    
    # Field/current magnitudes
    element_model(device=device, region=r, name="ElectricField_mag",
                  equation="pow((ElectricField_x^2 + ElectricField_y^2),0.5)")
    element_model(device=device, region=r, name="ElectronCurrent_mag",
                  equation="pow((ElectronCurrent_x^2 + ElectronCurrent_y^2),0.5)")
    element_model(device=device, region=r, name="HoleCurrent_mag",
                  equation="pow((HoleCurrent_x^2 + HoleCurrent_y^2),0.5)")
    
    #==============================================================================
    # BAND DIAGRAM QUANTITIES
    #==============================================================================
    
    set_parameter(device=device, region=r, name="E_base", value=0)
    
    # Conduction band edge
    Ec_expr = "-Potential + E_base"
    CreateNodeModel(device, r, "Ec", Ec_expr)
    CreateNodeModelDerivative(device, r, "Ec", Ec_expr, "Potential")
    
    # Valence band edge
    Ev_expr = "Ec - Eg"
    CreateNodeModel(device, r, "Ev", Ev_expr)
    CreateNodeModelDerivative(device, r, "Ev", Ev_expr, "Potential")
    
    # Electron quasi-Fermi level
    EFn_expr = "Ec + V_t * log(Electrons / NC)"
    CreateNodeModel(device, r, "EFn", EFn_expr)
    CreateNodeModelDerivative(device, r, "EFn", EFn_expr, "Electrons", "Potential")
    
    # Hole quasi-Fermi level
    EFp_expr = "Ev - V_t * log(Holes / NV)"
    CreateNodeModel(device, r, "EFp", EFp_expr)
    CreateNodeModelDerivative(device, r, "EFp", EFp_expr, "Holes", "Potential")

#==================================================================================
# FINAL EQUILIBRIUM SOLVE AND OUTPUT
#==================================================================================

solve(type="dc", absolute_error=1e5, relative_error=1, maximum_iterations=100)
write_devices(file="LDD2D_inverter_zero", type="vtk")

#==================================================================================
# CSV OUTPUT SETUP FOR VTC (Voltage Transfer Characteristic)
#==================================================================================

writer = None  # CSV writer object

# Contact name to bias parameter mapping
# V_out uses circuit node value, others use contact bias
contact_bias_map = {
    "V_dd": "V_dd_bias",      # Power supply bias
    "V_in": "V_in_bias",      # Input gate bias
    "Ground": "Ground_bias",  # Ground reference
    "V_out": "V_out_bias",    # Output (circuit node)
}

# Order of contacts in CSV output
ordered_contacts = ["V_dd", "V_in", "Ground", "V_out"]

def CSVCallback(step):
    """
    Callback function for VTC data collection.
    Records voltage and current at each contact during V_in sweep.
    V_out voltage shows the inverter transfer characteristic.
    """
    global writer
    print(f"=== Step {step} ===")
    
    contact_data = {}
    
    # Collect data for each contact
    for name in ordered_contacts:
        bias_name = contact_bias_map[name]
        
        # Get voltage
        try:
            if name == "V_out":
                # V_out is circuit node - get from circuit solution
                voltage = get_circuit_node_value(node=bias_name, solution="dcop")
            else:
                # Fixed contacts - get from parameter
                voltage = get_parameter(device=device, name=bias_name)
        except Exception as e:
            print(f"[WARN] Failed to get voltage for {name}: {e}")
            voltage = 0.0
        
        # Get current
        try:
            elec = get_contact_current(device=device, contact=name,
                                       equation="ElectronContinuityEquation")
            hole = get_contact_current(device=device, contact=name,
                                       equation="HoleContinuityEquation")
            current = elec + hole
        except:
            current = 0.0
        
        contact_data[name] = {"V": voltage, "I": current}
    
    # Get V_in separately for clarity
    try:
        V_in_voltage = get_parameter(device=device, name=GetContactBiasName("V_in"))
    except:
        V_in_voltage = 0.0
    
    # Write CSV row
    row = [step]
    for name in ordered_contacts:
        row.append(contact_data[name]["V"])
        row.append(contact_data[name]["I"])
    row.append(V_in_voltage)
    
    writer.writerow(row)

def EmptyCallback(device):
    """Empty callback for bias ramping without data recording."""
    pass

#==================================================================================
# BIAS SETUP AND VTC SIMULATION
# Generate Voltage Transfer Characteristic: V_out vs V_in
#==================================================================================

# Step 1: Ramp V_dd to operating voltage (power supply)
print("Ramping V_dd to 3V...")
rampbias(device, "V_dd", 3,         # Target: 3V power supply
         0.1,                        # Step size: 100mV
         1e-12,                      # Min step
         100,                        # Max iterations
         1e3,                        # Absolute error
         1e16,                       # Relative error
         EmptyCallback)              # No recording

# Step 2: Initialize V_in to 0V (low input)
print("Setting V_in to 0V...")
rampbias(device, "V_in", 0,         # Target: 0V
         0.01,                       # Step size: 10mV
         1e-12,
         100,
         1e3,
         1e16,
         EmptyCallback)

#==================================================================================
# VTC CURVE GENERATION
# Sweep V_in from 0V to V_dd while recording V_out
# Expected behavior:
#   - V_in = 0V → NMOS OFF, PMOS ON → V_out = V_dd (high)
#   - V_in = V_dd → NMOS ON, PMOS OFF → V_out = 0V (low)
#==================================================================================

# Open CSV file for VTC data
csvfile = open("ramp_currents_full.csv", "w", newline='')
writer = csv.writer(csvfile)

# Write header
header = ["Step"]
for name in ordered_contacts:
    header += [f"{name}_V", f"{name}_I"]
header += ["V_in_V"]
writer.writerow(header)

# Sweep V_in from 0V to 3V (full VTC curve)
print("Sweeping V_in from 0V to 3V (VTC curve)...")
rampbias(device, "V_in", 3,         # Target: 3V (same as V_dd)
         0.01,                       # Step size: 10mV for smooth curve
         1e-12,
         100,
         1e3,
         1e16,
         CSVCallback)                # Record VTC data

# Export final state
write_devices(file="LDD2D_inverter", type="vtk")

# Close CSV file
csvfile.close()

#==================================================================================
# SIMULATION COMPLETE
#==================================================================================

print("=" * 60)
print("CMOS Inverter Simulation Complete!")
print("=" * 60)
print("Output files:")
print("  - LDD2D_inverter_potential.dat: Initial potential (Tecplot)")
print("  - LDD2D_inverter_zero.vtk: Zero-bias equilibrium")
print("  - LDD2D_inverter.vtk: Final biased state")
print("  - ramp_currents_full.csv: VTC data (V_out vs V_in)")
print("")
print("VTC Analysis:")
print("  - Plot V_out_V vs V_in_V for transfer characteristic")
print("  - Switching threshold ≈ V_dd/2 for balanced inverter")
print("  - Gain = -dV_out/dV_in at switching point")
print("=" * 60)

#==================================================================================
# CMOS INVERTER OPERATION SUMMARY:
#
# Structure:
#   - PMOS: Source → V_dd, Drain → V_out, Gate → V_in
#   - NMOS: Source → Ground, Drain → V_out, Gate → V_in
#   - Gates tied together (common input)
#   - Drains tied together (common output)
#
# Operation:
#   V_in LOW (0V):
#     - NMOS: Vgs = 0 < Vth → OFF (no current path to ground)
#     - PMOS: Vsg = V_dd > |Vth| → ON (current path from V_dd)
#     - V_out pulled HIGH by PMOS → V_out ≈ V_dd
#
#   V_in HIGH (V_dd):
#     - NMOS: Vgs = V_dd > Vth → ON (current path to ground)
#     - PMOS: Vsg = 0 < |Vth| → OFF (no current path from V_dd)
#     - V_out pulled LOW by NMOS → V_out ≈ 0V
#
# Result: V_out = NOT(V_in) → INVERTER
#==================================================================================