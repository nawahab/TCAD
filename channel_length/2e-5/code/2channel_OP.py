####################################################################################
# MOSFET 2D Device Simulation using DEVSIM
# - Bottom-substrate Body Contact
# - Current scaled for 1 um Device Width
# - Caughey-Thomas Velocity Saturation Model (Field-Dependent Mobility)
####################################################################################

import numpy as np # Import NumPy
import csv # Import CSV module
import sys # Import sys module

from devsim import ( # Core DEVSIM imports
    add_gmsh_contact, # Import contact setup
    add_gmsh_interface, # Import interface setup
    add_gmsh_region, # Import region setup
    create_device, # Import device creation
    create_gmsh_mesh, # Import mesh loader
    finalize_mesh, # Import mesh finalizer
    node_model, # Import node model definition
    edge_model, # Import edge model definition
    write_devices, # Import device writer
    set_parameter, # Import parameter setter
    element_from_edge_model, # Import element edge converter
    get_contact_list, # Import contact list getter
    get_region_list, # Import region list getter
    get_contact_current, # Import current getter
    get_parameter, # Import parameter getter
    set_node_values, # Import node value setter
    solve, # Import solver
    element_model, # Import element model definition
)

from devsim.python_packages.simple_physics import ( # Physics module imports
    GetContactBiasName, # Get bias name function
    SetOxideParameters, # Set oxide parameters function
    SetSiliconParameters, # Set silicon parameters function
    CreateSiliconPotentialOnly, # Create potential solver (Si)
    CreateSiliconPotentialOnlyContact, # Create potential contact (Si)
    CreateSiliconDriftDiffusion, # Create DD solver (Si)
    CreateSiliconDriftDiffusionAtContact, # Create DD contact (Si)
    CreateOxidePotentialOnly, # Create potential solver (Ox)
    CreateSiliconOxideInterface, # Create Si/Ox interface
    CreateOxideContact, # Create oxide contact
)

from devsim.python_packages.ramp import rampbias, printAllCurrents # Ramp module imports

from devsim.python_packages.model_create import ( # Model creation imports
    CreateSolution, # Create solution variable
    CreateNodeModel, # Create node model
    CreateNodeModelDerivative, # Create derivative model
)

device = "mos2d" # Define device name

#==================================================================================
# DEVICE STRUCTURE PARAMETERS (Geometric Dimensions)
#==================================================================================

channel_length = 2e-5       # Channel length
extension_length = 4e-6     # S/D extension length
bulk_height = 5e-5          # Bulk depth
oxide_thickness = 1e-6      # Oxide thickness
source_contact = 1e-5       # Source contact width
drain_contact = 1e-5        # Drain contact width

#The default current is given in units of A/cm. so to get the current
#for W=1um, we do I(um)= (I(A/cm)/1e-4)*W(um) since 1um = 1e-4cm

device_width_z = 10e-4       # Z-depth for scaling (cm)

#==================================================================================
# MESH IMPORT AND REGION/CONTACT DEFINITION
#==================================================================================

create_gmsh_mesh(file="2channel.msh", mesh="mos2d") # Load mesh file

add_gmsh_region(mesh="mos2d", gmsh_name="bulk", region="bulk", material="Silicon") # Define Si region
add_gmsh_region(mesh="mos2d", gmsh_name="oxide", region="oxide", material="Oxide") # Define Ox region

add_gmsh_contact(mesh="mos2d", gmsh_name="source", region="bulk", name="source", material="metal") # Source contact
add_gmsh_contact(mesh="mos2d", gmsh_name="gate", region="oxide", name="gate", material="metal") # Gate contact
add_gmsh_contact(mesh="mos2d", gmsh_name="drain", region="bulk", name="drain", material="metal") # Drain contact
add_gmsh_contact(mesh="mos2d", gmsh_name="body", region="bulk", name="body", material="metal") # Body contact

add_gmsh_interface(mesh="mos2d", gmsh_name="oxide_bulk_interface", region0="bulk", region1="oxide", name="oxide_bulk") # Si/Ox interface

finalize_mesh(mesh="mos2d") # Finalize mesh build
create_device(mesh="mos2d", device="mos2d") # Instantiate device

#==================================================================================
# DOPING PROFILE PARAMETERS
#==================================================================================

Source_Doping = 5e19    # Source doping density
Drain_Doping = 5e19     # Drain doping density
Body_Doping = 5e19      # Body doping density
well_Doping = 5e16      # Well doping density
Bulk_Doping = 1e15      # Bulk background doping
LDD_Doping = 5e17       # LDD region doping
Interface_charge = 0    # Interface trap charge

Lext = 1e-6             # S/D decay length
Lext_well = 1e-5        # Well decay length

#==================================================================================
# DOPING REGION COORDINATE DEFINITIONS
#==================================================================================

x_min = 0               # Left boundary
x_max = source_contact  # Source outer edge

x_min_1 = source_contact                    # S/D extension start
x_max_1 = source_contact + extension_length # S/D extension end

x_min_2 = source_contact + extension_length * 2 + channel_length  # Drain extension end
x_max_2 = source_contact + extension_length * 2 + channel_length + drain_contact  # Right boundary

x_min_3 = source_contact + extension_length + channel_length      # Drain extension start
x_max_3 = source_contact + extension_length * 2 + channel_length  # Drain extension end

y_max = bulk_height  # Top silicon surface

#==================================================================================
# REGISTER PARAMETERS FOR USE IN EQUATIONS
#==================================================================================

set_parameter(name="y_max", value=y_max)            # Register y_max

set_parameter(name="x_max", value=x_max)    # Register x_max
set_parameter(name="x_min", value=x_min)    # Register x_min
set_parameter(name="x_max_1", value=x_max_1) # Register x_max_1
set_parameter(name="x_min_1", value=x_min_1) # Register x_min_1

set_parameter(name="x_max_2", value=x_max_2) # Register x_max_2
set_parameter(name="x_min_2", value=x_min_2) # Register x_min_2
set_parameter(name="x_max_3", value=x_max_3) # Register x_max_3
set_parameter(name="x_min_3", value=x_min_3) # Register x_min_3

set_parameter(name="Source_Doping", value=Source_Doping)  # Register Source_Doping
set_parameter(name="Drain_Doping", value=Drain_Doping)    # Register Drain_Doping
set_parameter(name="Body_Doping", value=Body_Doping)      # Register Body_Doping
set_parameter(name="well_Doping", value=well_Doping)      # Register well_Doping
set_parameter(name="Bulk_Doping", value=Bulk_Doping)      # Register Bulk_Doping
set_parameter(name="LDD_Doping", value=LDD_Doping)        # Register LDD_Doping

set_parameter(name="Lext", value=Lext)          # Register Lext
set_parameter(name="Lext_well", value=Lext_well) # Register Lext_well

set_parameter(name="Interface_charge", value=0) # Register Interface_charge

#==================================================================================
# DOPING PROFILE FUNCTIONS
#==================================================================================

def create_doping_box(name_prefix, doping_value, x_min, x_max, y_max, decay_len, region="bulk", device="mos2d"): # Function signature
    equation = ( # Start equation definition
        f"ifelse((x >= {x_min}), "           # Check x_min bound
        f"ifelse((x <= {x_max}), "           # Check x_max bound
        f"ifelse((y <= {y_max}), "           # Check y_max bound
        f"{doping_value} * erfc(({y_max} - y)/{decay_len}), 0), "  # Apply erfc profile
        f"0), 0)"                            # Close ifelse blocks
    ) # End equation definition
    node_model(name=name_prefix, device=device, region=region, equation=equation) # Create node model

def create_bottom_doping_box(name_prefix, doping_value, x_min, x_max, decay_len, region="bulk", device="mos2d"): # Function signature
    equation = ( # Start equation definition
        f"ifelse((x >= {x_min}), " # Check x_min bound
        f"ifelse((x <= {x_max}), " # Check x_max bound
        f"{doping_value} * erfc(y/{decay_len}), 0), " # Apply bottom erfc profile
        f"0)" # Close ifelse block
    ) # End equation definition
    node_model(name=name_prefix, device=device, region=region, equation=equation) # Create node model

def create_interface_doping_line(name_prefix, doping_value, x_min, x_max, y_max, tol=1e-9, region="bulk", device="mos2d"): # Function signature
    equation = ( # Start equation definition
        f"ifelse((x >= {x_min}), "           # Check x_min bound
        f"ifelse((x <= {x_max}), "           # Check x_max bound
        f"ifelse(abs(y - {y_max}) < {tol}, " # Check y interface tolerance
        f"{doping_value}, 0), 0), 0)"        # Apply value at interface
    ) # End equation definition
    node_model(name=name_prefix, device=device, region=region, equation=equation) # Create node model

#==================================================================================
# CREATE ALL DOPING PROFILES
#==================================================================================

create_doping_box("well_Doping", "well_Doping", "x_min", "x_max_2", "y_max", "Lext_well") # Create well

create_doping_box("SourceDoping1", "Source_Doping", "x_min", "x_max", "y_max", "Lext") # Create main source
create_doping_box("SourceDoping2", "LDD_Doping", "x_min_1", "x_max_1", "y_max", "Lext") # Create source LDD
create_doping_box("DrainDoping1", "Drain_Doping", "x_min_2", "x_max_2", "y_max", "Lext") # Create main drain
create_doping_box("DrainDoping2", "LDD_Doping", "x_min_3", "x_max_3", "y_max", "Lext") # Create drain LDD

create_bottom_doping_box("BodyDoping", "Body_Doping", "x_min", "x_max_2", "Lext") # Create body contact doping

create_interface_doping_line("Interface_charge", "Interface_charge", "x_min_1", "x_max_3", "y_max") # Create interface charge

#==================================================================================
# COMBINE DOPING PROFILES
#==================================================================================

node_model(name="SourceDoping", device=device, region="bulk", equation="SourceDoping1 + SourceDoping2") # Total source doping
node_model(name="DrainDoping", device=device, region="bulk", equation="DrainDoping1 + DrainDoping2") # Total drain doping

node_model(name="Donors", device=device, region="bulk", equation="DrainDoping + SourceDoping + Interface_charge") # Total N-type
node_model(name="Acceptors", device=device, region="bulk", equation="Bulk_Doping + well_Doping + BodyDoping") # Total P-type
node_model(name="NetDoping", device=device, region="bulk", equation="Donors - Acceptors") # Net doping calculation

#==================================================================================
# PHYSICS SETUP AND SOLVER CONFIGURATION
#==================================================================================

silicon_regions = ("bulk",)       # Tuple of Si regions
oxide_regions = ("oxide",)        # Tuple of Ox regions
regions = ("bulk", "oxide")       # Tuple of all regions
interfaces = ("oxide_bulk",)      # Tuple of interfaces

for i in regions: # Iterate regions
    CreateSolution(device, i, "Potential")  # Create potential variable

#==================================================================================
# FUNDAMENTAL PHYSICAL CONSTANTS AND MATERIAL PARAMETERS
#==================================================================================

q = 1.6e-19         # Elementary charge
k = 1.3806503e-23   # Boltzmann constant
eps_0 = 8.85e-14    # Vacuum permittivity
T = 300             # Temperature (K)
eps_si = 11.1       # Si relative permittivity
eps_ox = 3.9        # Ox relative permittivity
mu_n = 1000         # Electron low-field mobility
mu_p = 500          # Hole low-field mobility
NC = 2.8e19         # Conduction band DOS
NV = 1.04e19        # Valence band DOS
Eg = 1.08           # Bandgap energy (eV)

n_i = np.sqrt(NC * NV) * np.exp(-Eg / (2 * k * T / q))  # Intrinsic carrier density

taun = 1e-7         # Electron lifetime
taup = 1e-7         # Hole lifetime

#==================================================================================
# SILICON REGION PHYSICS SETUP (With Velocity Saturation)
#==================================================================================

for i in silicon_regions: # Loop over Si regions
    CreateSiliconPotentialOnly(device, i) # Setup Poisson equation
    set_parameter(device=device, region=i, name="Permittivity", value=eps_si * eps_0) # Set Si permittivity
    set_parameter(device=device, region=i, name="ElectronCharge", value=q) # Set charge
    set_parameter(device=device, region=i, name="n_i", value=n_i) # Set intrinsic density
    set_parameter(device=device, region=i, name="NC", value=NC) # Set NC
    set_parameter(device=device, region=i, name="NV", value=NV) # Set NV
    set_parameter(device=device, region=i, name="Eg", value=Eg) # Set Eg
    set_parameter(device=device, region=i, name="T", value=T) # Set Temperature
    set_parameter(device=device, region=i, name="KT", value=k * T) # Set thermal energy
    set_parameter(device=device, region=i, name="V_t", value=k * T / q) # Set thermal voltage
    set_parameter(device=device, region=i, name="n1", value=n_i) # Set SRH n1
    set_parameter(device=device, region=i, name="p1", value=n_i) # Set SRH p1
    set_parameter(device=device, region=i, name="taun", value=taun) # Set SRH tau_n
    set_parameter(device=device, region=i, name="taup", value=taup) # Set SRH tau_p

    # --- Caughey-Thomas Velocity Saturation Model Implementation ---
    set_parameter(device=device, region=i, name="mu_n0", value=mu_n) # Low-field e- mobility
    set_parameter(device=device, region=i, name="mu_p0", value=mu_p) # Low-field h+ mobility
    set_parameter(device=device, region=i, name="vsat_n", value=1e7) # Electron sat. velocity
    set_parameter(device=device, region=i, name="vsat_p", value=1e7) # Hole sat. velocity
    set_parameter(device=device, region=i, name="beta_n", value=2.0) # Electron fitting param
    set_parameter(device=device, region=i, name="beta_p", value=1.0) # Hole fitting param

    # Calculate parallel electric field along the mesh edges
    edge_model( # Create E-field edge model
        device=device, region=i, name="EParallel",  # Model parameters
        equation="(Potential@n0 - Potential@n1)/EdgeLength" # E-field equation
    ) # End edge model

    # Define dynamic edge mobility for electrons
    mu_n_eq = "mu_n0 / pow(1.0 + pow(mu_n0 * abs(EParallel) / vsat_n, beta_n), 1.0/beta_n)" # Caughey-Thomas e- eq
    edge_model(device=device, region=i, name="mu_n", equation=mu_n_eq) # Set e- mobility model
    edge_model(device=device, region=i, name="mu_n:Potential@n0", equation=f"diff({mu_n_eq}, Potential@n0)") # Derivative w.r.t n0
    edge_model(device=device, region=i, name="mu_n:Potential@n1", equation=f"diff({mu_n_eq}, Potential@n1)") # Derivative w.r.t n1

    # Define dynamic edge mobility for holes
    mu_p_eq = "mu_p0 / pow(1.0 + pow(mu_p0 * abs(EParallel) / vsat_p, beta_p), 1.0/beta_p)" # Caughey-Thomas h+ eq
    edge_model(device=device, region=i, name="mu_p", equation=mu_p_eq) # Set h+ mobility model
    edge_model(device=device, region=i, name="mu_p:Potential@n0", equation=f"diff({mu_p_eq}, Potential@n0)") # Derivative w.r.t n0
    edge_model(device=device, region=i, name="mu_p:Potential@n1", equation=f"diff({mu_p_eq}, Potential@n1)") # Derivative w.r.t n1

#==================================================================================
# OXIDE REGION PHYSICS SETUP
#==================================================================================

for reg in oxide_regions: # Loop over Ox regions
    SetOxideParameters(device, reg, 300)  # Setup oxide properties
    CreateOxidePotentialOnly(device, reg, "log_damp") # Setup Poisson for oxide
    set_parameter(device=device, name=GetContactBiasName("gate"), value=0.0) # Initialize gate bias
    CreateOxideContact(device, reg, "gate") # Setup gate contact boundary

#==================================================================================
# CONTACT BOUNDARY CONDITIONS FOR SILICON REGIONS
#==================================================================================

contacts = get_contact_list(device=device) # Retrieve all contacts

for c in contacts: # Loop over contacts
    reg = get_region_list(device=device, contact=c)[0] # Get contact's region
    if reg not in silicon_regions: # Skip non-silicon regions
        continue # Continue loop
    
    CreateSiliconPotentialOnlyContact(device, reg, c) # Setup Poisson contact BC
    set_parameter(device=device, name=GetContactBiasName(c), value=0.0) # Initialize bias to 0V

#==================================================================================
# INTERFACE BOUNDARY CONDITIONS
#==================================================================================

for i in interfaces: # Loop over interfaces
    CreateSiliconOxideInterface(device, i) # Link Si/Ox boundary conditions

#==================================================================================
# INITIAL EQUILIBRIUM SOLVE (POTENTIAL ONLY)
#==================================================================================

solve(type="dc", absolute_error=1.0e-5, relative_error=1e-5, maximum_iterations=30) # 1st Poisson solve
solve(type="dc", absolute_error=1.0e-5, relative_error=1e-5, maximum_iterations=30) # 2nd Poisson solve

write_devices(file="MOSFET_potential.dat", type="tecplot") # Output potential data

#==================================================================================
# ADD CARRIER TRANSPORT EQUATIONS (DRIFT-DIFFUSION)
#==================================================================================

for i in silicon_regions: # Loop over Si regions
    CreateSolution(device, i, "Electrons")  # Add electron variable
    CreateSolution(device, i, "Holes")      # Add hole variable
    
    set_node_values(device=device, region=i, name="Electrons", init_from="IntrinsicElectrons") # Init electrons
    set_node_values(device=device, region=i, name="Holes", init_from="IntrinsicHoles") # Init holes
    
    CreateSiliconDriftDiffusion(device, i, "mu_n", "mu_p") # Setup DD equations with custom mobility

#==================================================================================
# CONTACT BOUNDARY CONDITIONS FOR DRIFT-DIFFUSION
#==================================================================================

for c in contacts: # Loop over contacts
    tmp = get_region_list(device=device, contact=c)  # Get regions for contact
    r = tmp[0]  # Extract primary region
    if r in silicon_regions: # If it's a Si region
        CreateSiliconDriftDiffusionAtContact(device, r, c) # Set Ohmic boundary conditions

#==================================================================================
# SOLVE DRIFT-DIFFUSION EQUATIONS
#==================================================================================

solve(type="dc", absolute_error=1e5, relative_error=1, maximum_iterations=100) # Solve coupled DD system

#==================================================================================
# POST-PROCESSING & ELEMENT MODELS FOR VISUALIZATION
#==================================================================================

for r in silicon_regions: # Loop over Si regions
    node_model(device=device, region=r, name="logElectrons", equation="log(Electrons)/log(10)") # Calc log(n)

for r in silicon_regions: # Loop over Si regions
    element_from_edge_model(edge_model="ElectricField", device=device, region=r) # Convert E-field to elements
    element_from_edge_model(edge_model="ElectronCurrent", device=device, region=r) # Convert J_n to elements
    element_from_edge_model(edge_model="HoleCurrent", device=device, region=r) # Convert J_p to elements
    
    element_model(device=device, region=r, name="ElectricField_mag", equation="pow((ElectricField_x^2 + ElectricField_y^2),0.5)") # Calc |E|
    element_model(device=device, region=r, name="ElectronCurrent_mag", equation="pow((ElectronCurrent_x^2 + ElectronCurrent_y^2),0.5)") # Calc |J_n|
    element_model(device=device, region=r, name="HoleCurrent_mag", equation="pow((HoleCurrent_x^2 + HoleCurrent_y^2),0.5)") # Calc |J_p|
    
    set_parameter(device=device, region=r, name="E_base", value=0) # Set energy reference
    
    Ec_expr = "-Potential + E_base" # Conduction band formula
    CreateNodeModel(device, r, "Ec", Ec_expr) # Create Ec model
    CreateNodeModelDerivative(device, r, "Ec", Ec_expr, "Potential")  # Ec derivative
    
    Ev_expr = "Ec - Eg" # Valence band formula
    CreateNodeModel(device, r, "Ev", Ev_expr) # Create Ev model
    CreateNodeModelDerivative(device, r, "Ev", Ev_expr, "Potential")  # Ev derivative
    
    EFn_expr = "Ec + V_t * log(Electrons / NC)" # Electron quasi-Fermi formula
    CreateNodeModel(device, r, "EFn", EFn_expr) # Create EFn model
    CreateNodeModelDerivative(device, r, "EFn", EFn_expr, "Electrons", "Potential")  # EFn derivative
    
    EFp_expr = "Ev - V_t * log(Holes / NV)" # Hole quasi-Fermi formula
    CreateNodeModel(device, r, "EFp", EFp_expr) # Create EFp model
    CreateNodeModelDerivative(device, r, "EFp", EFp_expr, "Holes", "Potential")  # EFp derivative

#==================================================================================
# FINAL EQUILIBRIUM SOLVE AND OUTPUT
#==================================================================================

solve(type="dc", absolute_error=1e15, relative_error=1e8, maximum_iterations=100) # Final strict solve
write_devices(file="gmsh_mos2d_zero", type="vtk") # Export zero-bias VTK

#==================================================================================
# CSV OUTPUT SETUP FOR I-V CHARACTERISTICS
#==================================================================================

writer = None  # Init CSV writer variable
ordered_contacts = ["body", "source", "drain"] # Define contact output order

def CSVCallback(step): # Define CSV logging callback
    global writer  # Use global writer
    contact_data = {}  # Dict for contact data
    
    for name in ordered_contacts: # Loop contacts
        voltage = get_parameter(device=device, name=GetContactBiasName(name)) # Get voltage
        
        try: # Try to get electron current
            elec = get_contact_current(device=device, contact=name, equation="ElectronContinuityEquation") # Get I_n
        except: # Handle missing eq
            elec = 0.0  # Default to 0
        
        try: # Try to get hole current
            hole = get_contact_current(device=device, contact=name, equation="HoleContinuityEquation") # Get I_p
        except: # Handle missing eq
            hole = 0.0  # Default to 0
        
        # Scale current by realistic 1 μm Z-width
        current = (elec + hole) * device_width_z # Calc total scaled current
        contact_data[name] = {"V": voltage, "I": current} # Store data
    
    gate_voltage = get_parameter(device=device, name=GetContactBiasName("gate")) # Get gate voltage
    
    row = [step] # Start CSV row
    for name in ordered_contacts: # Loop contacts
        row.append(contact_data[name]["V"])  # Append voltage
        row.append(contact_data[name]["I"])  # Append current
    row.append(gate_voltage)  # Append gate voltage
    
    writer.writerow(row) # Write row to file

def EmptyCallback(device): # Define blank callback
    pass  # Do nothing

#==================================================================================
# VOLTAGE RAMPING AND I-V CHARACTERIZATION
#==================================================================================

# Transfer Curve Simulation
#rampbias(device, "drain", 3, 0.01, 1e-12, 100, 1e15, 5e15, EmptyCallback) # Ramp drain to 3V
#rampbias(device, "gate", -3, 0.01, 1e-12, 100, 1e15, 5e15, EmptyCallback) # Ramp gate to -3V
#write_devices(file="gmsh_mos2d_off", type="vtk") # Export OFF-state VTK


#==================================================================================
# OUTPUT CHARACTERISTICS SWEEP (Id vs Vds at constant Vgs)
#==================================================================================


csvfile = open("ramp_output_curves.csv", "w", newline='')
writer = csv.writer(csvfile)  

header = ["Step"]  
for name in ordered_contacts:
    header += [f"{name}_V", f"{name}_I"]  
header += ["gate_V"]  
writer.writerow(header)  

print("Initializing Output Characteristics Sweep...")

# Start from 0V everywhere
rampbias(device, "gate", 0, 0.01, 1e-12, 100, 1e5, 5e13, EmptyCallback)
rampbias(device, "drain", 0, 0.01, 1e-12, 100, 1e5, 5e13, EmptyCallback)

# Sweep Drain at various Gate voltages
#gate_voltages = [0.0, 0.5]
gate_voltages = [0.5, 1.0, 2.0, 3.0]

for Vg in gate_voltages:
    print(f"Sweeping Vds for Vgs = {Vg} V...")
    
    # 1. Ramp Gate up to target Vg (while Drain is 0V)
    rampbias(device, "gate", Vg, 0.05, 1e-12, 100, 1e5, 5e13, EmptyCallback)
    
    # 2. Sweep Drain from 0V to 5V and record to CSV
    rampbias(device, "drain", 5.0, 0.05, 1e-12, 100, 1e5, 5e13, CSVCallback)
    
    # 3. Ramp Drain back to 0V (without recording) before stepping to the next Vg
    rampbias(device, "drain", 0.0, 0.5, 1e-12, 100, 1e5, 5e13, EmptyCallback)

write_devices(file="gmsh_mos2d_output", type="vtk")
csvfile.close()
print("Simulation complete. Data saved to 'ramp_output_curves.csv'")

class Logger(object): # Define custom logger
    def __init__(self): # Initialize logger
        self.terminal = sys.stdout # Store standard output
        self.log = open("OP_simulation_log.log", "a") # Open log file

    def write(self, message): # Write method
        self.terminal.write(message) # Write to console
        self.log.write(message)  # Write to file

    def flush(self): # Flush method
        pass    # Do nothing

# Redirect standard output and errors to the Logger
sys.stdout = Logger() # Replace stdout
sys.stderr = sys.stdout # Replace stderr