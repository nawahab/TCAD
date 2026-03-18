//==============================================================================
// GMSH GEOMETRY FILE FOR 2D CMOS INVERTER WITH LDD STRUCTURE
// This file defines the geometry for a CMOS inverter device simulation
// Contains both NMOS and PMOS transistors with shared output node
// Created for use with DEVSIM semiconductor device simulator
//==============================================================================

//==============================================================================
// GEOMETRY KERNEL SELECTION
//==============================================================================
SetFactory("OpenCASCADE");
// Use OpenCASCADE geometry kernel for better CAD operations
// Provides robust boolean operations and complex shape handling

//==============================================================================
// NMOS TRANSISTOR GEOMETRY PARAMETERS
// NMOS: N-channel MOSFET (electrons as majority carriers in channel)
// Located on the LEFT side of the inverter structure
// Source connects to Ground, Drain connects to V_out
// All dimensions in centimeters (cm) for DEVSIM compatibility
//==============================================================================

// NMOS //

channel_length = 5e-5;          // NMOS gate/channel length: 0.5 μm (500 nm)
                                // Region under gate where inversion layer forms

extension_length = 4e-6;        // NMOS LDD (Lightly Doped Drain) extension: 40 nm
                                // Reduces hot carrier effects and electric field peaks
                                // Present on both source and drain sides

oxide_thickness = 1e-6;         // NMOS gate oxide thickness: 10 nm
                                // Thin oxide for good gate control (high Cox)

source_contact = 1e-5;          // NMOS source contact region width: 100 nm
                                // N+ heavily doped region for ohmic contact to Ground

drain_contact = 1e-5;           // NMOS drain contact region width: 100 nm
                                // N+ heavily doped region, connects to V_out (shared with PMOS)

//==============================================================================
// PMOS TRANSISTOR GEOMETRY PARAMETERS
// PMOS: P-channel MOSFET (holes as majority carriers in channel)
// Located on the RIGHT side of the inverter structure
// Source connects to V_dd, Drain connects to V_out
//==============================================================================

// PMOS //

channel_length_2 = 5e-5;        // PMOS gate/channel length: 0.5 μm (500 nm)
                                // Same as NMOS for symmetric design

extension_length_2 = 4e-6;      // PMOS LDD extension: 40 nm
                                // P- lightly doped regions at source/drain edges

oxide_thickness_2 = 1e-6;       // PMOS gate oxide thickness: 10 nm
                                // Same as NMOS for matched threshold voltages

source_contact_2 = 1e-5;        // PMOS source contact region width: 100 nm
                                // P+ heavily doped region for ohmic contact to V_dd

drain_contact_2 = 1e-5;         // PMOS drain contact region width: 100 nm
                                // P+ heavily doped region, connects to V_out

//==============================================================================
// COMMON STRUCTURE PARAMETERS
// Shared dimensions for both transistors and isolation
//==============================================================================

bulk_height = 5e-5;             // Silicon substrate thickness: 0.5 μm
                                // Depth of silicon below gate oxide

STL_depth = 4.5e-5;             // STI (Shallow Trench Isolation) depth: 0.45 μm
                                // Isolates NMOS (P-well) from PMOS (N-well)
                                // Prevents latch-up by blocking parasitic thyristor

STL_length = 1e-5;              // STI width: 100 nm
                                // Horizontal extent of isolation trench

//==============================================================================
// MESH DENSITY PARAMETERS
// Control element size for numerical accuracy vs. computation time
//==============================================================================

fine_mesh = 1e-6;               // Fine mesh size: 1 μm
                                // Used at silicon surface, channel regions, junctions
                                // Critical areas need fine mesh for accuracy

coarse_mesh = 3e-6;             // Coarse mesh size: 3 μm
                                // Used in bulk regions away from active areas
                                // Reduces computation time without losing accuracy

body_source_space = 5e-6;       // Spacing between body contact and source: 50 nm
                                // Separation for layout design rules

body_contact = 1e-5;            // Body/well contact width: 100 nm
                                // NMOS: P+ contact to P-well (ties to Ground)
                                // PMOS: N+ contact to N-well (ties to V_dd)

//==============================================================================
// NMOS REGION POINT DEFINITIONS
// Points define the NMOS transistor cross-section (left side of inverter)
// Layout: [Body Contact] - [Source] - [LDD] - [Channel] - [LDD] - [Drain]
// Point format: Point(ID) = {x, y, z, mesh_size};
//==============================================================================

// Bottom corners of NMOS bulk region
Point(1)  = {0, 0, 0, coarse_mesh};
// Bottom-left corner of NMOS active region (origin reference)

Point(4)  = {source_contact + extension_length * 2 + channel_length + drain_contact, 0, 0, coarse_mesh};
// Bottom-right corner of NMOS bulk (at STI boundary)
// x = total NMOS width: source + 2*LDD + channel + drain

// Top surface of silicon (gate oxide interface)
Point(5)  = {0, bulk_height, 0, fine_mesh};
// Top-left corner of NMOS (source region start)

Point(8)  = {source_contact + extension_length * 2 + channel_length + drain_contact, bulk_height, 0, fine_mesh};
// Top-right corner of NMOS (drain region end, at STI)

//==============================================================================
// NMOS SILICON SURFACE POINTS (y = bulk_height)
// Define boundaries between source, LDD, channel, LDD, drain regions
//==============================================================================

Point(14) = {source_contact, bulk_height, 0, fine_mesh};
// End of source region / Start of source-side LDD
// x = source_contact (10 nm from origin)

Point(15) = {source_contact + extension_length, bulk_height, 0, fine_mesh};
// End of source-side LDD / Start of channel
// x = source + LDD extension

Point(16) = {source_contact + extension_length + channel_length, bulk_height, 0, fine_mesh};
// End of channel / Start of drain-side LDD
// x = source + LDD + channel

Point(17) = {source_contact + extension_length + channel_length + extension_length, bulk_height, 0, fine_mesh};
// End of drain-side LDD / Start of drain region
// x = source + 2*LDD + channel

Point(18) = {source_contact + extension_length + channel_length + extension_length + drain_contact, bulk_height, 0, fine_mesh};
// End of drain region (same as Point 8)
// x = total NMOS width

//==============================================================================
// NMOS GATE OXIDE POINTS (y = bulk_height + oxide_thickness)
// Define the top surface of the gate oxide
//==============================================================================

Point(24) = {source_contact, bulk_height + oxide_thickness, 0, fine_mesh};
// Gate oxide corner above source/LDD boundary

Point(25) = {source_contact + extension_length, bulk_height + oxide_thickness, 0, fine_mesh};
// Gate oxide corner above LDD/channel boundary (gate edge)

Point(26) = {source_contact + extension_length + channel_length, bulk_height + oxide_thickness, 0, fine_mesh};
// Gate oxide corner above channel/LDD boundary (gate edge)

Point(27) = {source_contact + extension_length + channel_length + extension_length, bulk_height + oxide_thickness, 0, fine_mesh};
// Gate oxide corner above LDD/drain boundary

//==============================================================================
// STI (SHALLOW TRENCH ISOLATION) REGION POINTS
// STI separates NMOS from PMOS to prevent latch-up
// Filled with oxide (SiO2) in real devices
//==============================================================================

Point(29) = {source_contact + extension_length * 2 + channel_length + drain_contact + STL_length, 0, 0, coarse_mesh};
// Bottom-right corner of STI trench (start of PMOS region)

Point(31) = {source_contact + extension_length * 2 + channel_length + drain_contact, bulk_height - STL_depth, 0, fine_mesh};
// Bottom-left corner of STI trench (NMOS side)
// y = bulk_height - STL_depth: trench goes down into silicon

Point(32) = {source_contact + extension_length * 2 + channel_length + drain_contact + STL_length, 0, 0, coarse_mesh};
// Same as Point(29) - bottom-right of STI

Point(58) = {source_contact + extension_length * 2 + channel_length + drain_contact + STL_length, bulk_height - STL_depth, 0, fine_mesh};
// Bottom-right corner of STI trench (PMOS side)

//==============================================================================
// PMOS REGION POINT DEFINITIONS
// Points define the PMOS transistor cross-section (right side of inverter)
// Layout: [Source/V_dd] - [LDD] - [Channel] - [LDD] - [Drain/V_out] - [Body Contact]
// PMOS starts after STI region
//==============================================================================

// PMOS x-offset = NMOS_width + STL_length
// x_pmos_start = source_contact + extension_length*2 + channel_length + drain_contact + STL_length

Point(35) = {source_contact + extension_length * 2 + channel_length + drain_contact + source_contact_2 + extension_length_2 * 2 + channel_length_2 + drain_contact_2 + STL_length, 0, 0, coarse_mesh};
// Bottom-right corner of PMOS bulk (far right of inverter)

Point(36) = {source_contact + extension_length * 2 + channel_length + drain_contact + STL_length, bulk_height, 0, fine_mesh};
// Top-left corner of PMOS (at STI, start of PMOS source)

Point(39) = {source_contact + extension_length * 2 + channel_length + drain_contact + source_contact_2 + extension_length_2 * 2 + channel_length_2 + drain_contact_2 + STL_length, bulk_height, 0, fine_mesh};
// Top-right corner of PMOS (drain region end)

//==============================================================================
// PMOS SILICON SURFACE POINTS (y = bulk_height)
// Define boundaries between PMOS regions
//==============================================================================

Point(45) = {source_contact + extension_length * 2 + channel_length + drain_contact + source_contact_2 + STL_length, bulk_height, 0, fine_mesh};
// End of PMOS source region / Start of source-side LDD

Point(46) = {source_contact + extension_length * 2 + channel_length + drain_contact + source_contact_2 + extension_length_2 + STL_length, bulk_height, 0, fine_mesh};
// End of source-side LDD / Start of PMOS channel

Point(47) = {source_contact + extension_length * 2 + channel_length + drain_contact + source_contact_2 + extension_length_2 + channel_length_2 + STL_length, bulk_height, 0, fine_mesh};
// End of PMOS channel / Start of drain-side LDD

Point(48) = {source_contact + extension_length * 2 + channel_length + drain_contact + source_contact_2 + extension_length_2 + channel_length_2 + extension_length_2 + STL_length, bulk_height, 0, fine_mesh};
// End of drain-side LDD / Start of PMOS drain region

Point(49) = {source_contact + extension_length * 2 + channel_length + drain_contact + source_contact_2 + extension_length_2 + channel_length_2 + extension_length_2 + drain_contact_2 + STL_length, bulk_height, 0, fine_mesh};
// End of PMOS drain region

//==============================================================================
// PMOS GATE OXIDE POINTS (y = bulk_height + oxide_thickness_2)
// Define the top surface of PMOS gate oxide
//==============================================================================

Point(54) = {source_contact + extension_length * 2 + channel_length + drain_contact + source_contact_2 + STL_length, bulk_height + oxide_thickness_2, 0, fine_mesh};
// Gate oxide corner above PMOS source/LDD boundary

Point(55) = {source_contact + extension_length * 2 + channel_length + drain_contact + source_contact_2 + extension_length_2 + STL_length, bulk_height + oxide_thickness_2, 0, fine_mesh};
// Gate oxide corner above PMOS LDD/channel boundary (gate edge)

Point(56) = {source_contact + extension_length * 2 + channel_length + drain_contact + source_contact_2 + extension_length_2 + channel_length_2 + STL_length, bulk_height + oxide_thickness_2, 0, fine_mesh};
// Gate oxide corner above PMOS channel/LDD boundary (gate edge)

Point(57) = {source_contact + extension_length * 2 + channel_length + drain_contact + source_contact_2 + extension_length_2 + channel_length_2 + extension_length_2 + STL_length, bulk_height + oxide_thickness_2, 0, fine_mesh};
// Gate oxide corner above PMOS LDD/drain boundary

//==============================================================================
// BODY CONTACT REGION POINTS
// Body contacts tie the wells to fixed potentials to prevent floating body effects
//==============================================================================

// NMOS Body Contact (P-well contact, connects to Ground)
// Located to the LEFT of NMOS source

Point(87)  = {-body_source_space, bulk_height, 0, fine_mesh};
// Top-right corner of NMOS body contact region

Point(88)  = {-body_source_space - body_contact, bulk_height, 0, fine_mesh};
// Top-left corner of NMOS body contact region (leftmost point)

Point(89)  = {-body_source_space, 0, 0, coarse_mesh};
// Bottom-right corner of NMOS body contact region

Point(90)  = {-body_source_space - body_contact, 0, 0, coarse_mesh};
// Bottom-left corner of NMOS body contact region (leftmost point)

// PMOS Body Contact (N-well contact, connects to V_dd)
// Located to the RIGHT of PMOS drain

Point(91) = {source_contact + extension_length * 2 + channel_length + drain_contact + source_contact_2 + extension_length_2 * 2 + channel_length_2 + drain_contact_2 + STL_length + body_source_space, 0, 0, coarse_mesh};
// Bottom-left corner of PMOS body contact spacing

Point(92) = {source_contact + extension_length * 2 + channel_length + drain_contact + source_contact_2 + extension_length_2 * 2 + channel_length_2 + drain_contact_2 + STL_length + body_source_space, bulk_height, 0, fine_mesh};
// Top-left corner of PMOS body contact region

Point(93) = {source_contact + extension_length * 2 + channel_length + drain_contact + source_contact_2 + extension_length_2 * 2 + channel_length_2 + drain_contact_2 + STL_length + body_source_space + body_contact, 0, 0, coarse_mesh};
// Bottom-right corner of PMOS body contact (rightmost point)

Point(94) = {source_contact + extension_length * 2 + channel_length + drain_contact + source_contact_2 + extension_length_2 * 2 + channel_length_2 + drain_contact_2 + STL_length + body_source_space + body_contact, bulk_height, 0, fine_mesh};
// Top-right corner of PMOS body contact (rightmost point)

//==============================================================================
// LINE DEFINITIONS (EDGES)
// Lines connect points to form the edges of the geometry
// Line format: Line(ID) = {start_point, end_point};
// "//+" is GMSH auto-formatting marker
//==============================================================================

////////

//+
// Line 2: NMOS source region top surface (Ground contact area)
Line(2) = {5, 14};
//+
// Line 3: NMOS source-side LDD region top surface
Line(3) = {14, 15};
//+
// Line 4: NMOS channel region top surface (under gate)
Line(4) = {15, 16};
//+
// Line 5: NMOS drain-side LDD region top surface
Line(5) = {16, 17};
//+
// Line 6: NMOS drain region top surface (V_out contact area)
Line(6) = {17, 8};
//+
// Line 7: Bottom of NMOS bulk region
Line(7) = {1, 4};
//+
// Line 8: NMOS drain edge going down to STI
Line(8) = {8, 31};
//+
// Line 9: STI trench bottom (horizontal)
Line(9) = {31, 58};
//+
// Line 10: STI trench right edge going up to PMOS
Line(10) = {58, 36};
//+
// Line 11: Bottom of STI region (NMOS side to STI)
Line(11) = {4, 29};
//+
// Line 12: Bottom of inverter (STI to PMOS)
Line(12) = {29, 35};
//+
//+
// Line 14: PMOS drain region top surface (V_dd contact area)
Line(14) = {39, 48};
//+
// Line 15: PMOS drain-side LDD region top surface
Line(15) = {48, 47};
//+
// Line 16: PMOS channel region top surface (under gate)
Line(16) = {47, 46};
//+
// Line 17: PMOS source-side LDD region top surface
Line(17) = {46, 45};
//+
// Line 18: PMOS source region top surface (V_out contact area)
Line(18) = {45, 36};
//+
//+

//==============================================================================
// NMOS GATE OXIDE LINES
// Define the boundaries of NMOS gate oxide region
//==============================================================================

//+
// Line 19: Left edge of NMOS gate oxide (source side)
Line(19) = {14, 24};
//+
// Line 20: Top of NMOS gate oxide (left extension)
Line(20) = {24, 25};
//+
// Line 21: NMOS gate oxide to silicon interface (LDD/channel boundary)
Line(21) = {25, 15};
//+
// Line 22: Top of NMOS gate oxide (over channel) - THIS IS V_in CONTACT
Line(22) = {25, 26};
//+
// Line 23: NMOS gate oxide to silicon interface (channel/LDD boundary)
Line(23) = {26, 16};
//+
// Line 24: Top of NMOS gate oxide (right extension)
Line(24) = {26, 27};
//+
// Line 25: Right edge of NMOS gate oxide (drain side)
Line(25) = {27, 17};

//==============================================================================
// PMOS GATE OXIDE LINES
// Define the boundaries of PMOS gate oxide region
//==============================================================================

//+
// Line 26: Left edge of PMOS gate oxide (source side)
Line(26) = {54, 45};
//+
// Line 27: Top of PMOS gate oxide (left extension)
Line(27) = {54, 55};
//+
// Line 28: PMOS gate oxide to silicon interface (LDD/channel boundary)
Line(28) = {55, 46};
//+
// Line 29: Top of PMOS gate oxide (over channel) - THIS IS V_in CONTACT
Line(29) = {55, 56};
//+
// Line 30: PMOS gate oxide to silicon interface (channel/LDD boundary)
Line(30) = {56, 47};
//+
// Line 31: Top of PMOS gate oxide (right extension)
Line(31) = {56, 57};
//+
// Line 32: Right edge of PMOS gate oxide (drain side)
Line(32) = {57, 48};
//+
// Line 33: Connection from NMOS drain to PMOS source (through STI top)
Line(33) = {8, 36};

//==============================================================================
// NMOS BODY CONTACT LINES
// Lines defining the P-well body contact region (left side)
//==============================================================================

//+
// Line 34: NMOS source to body contact spacing (top surface)
Line(34) = {5, 87};
//+
// Line 35: NMOS body contact top surface (Ground contact area)
Line(35) = {87, 88};
//+
// Line 36: Left edge of NMOS body contact (vertical)
Line(36) = {88, 90};
//+
// Line 37: Bottom of NMOS body contact region
Line(37) = {90, 89};
//+
// Line 38: Right edge of NMOS body contact to source
Line(38) = {89, 1};

//==============================================================================
// PMOS BODY CONTACT LINES
// Lines defining the N-well body contact region (right side)
//==============================================================================

//+
// Line 39: Bottom of PMOS to body contact spacing
Line(39) = {35, 91};
//+
// Line 40: Bottom of PMOS body contact region
Line(40) = {91, 93};
//+
// Line 41: Right edge of PMOS body contact (vertical)
Line(41) = {93, 94};
//+
// Line 42: PMOS body contact top surface (V_dd contact area)
Line(42) = {94, 92};
//+
// Line 43: PMOS body contact to drain spacing (top surface)
Line(43) = {92, 39};

//==============================================================================
// CURVE LOOPS AND SURFACES - OXIDE REGIONS
// Define closed boundaries for gate oxide surfaces
// Curve Loop format: Curve Loop(ID) = {line1, line2, ...};
// Positive = forward direction, Negative = reverse direction
//==============================================================================

//+
// Curve loop for PMOS gate oxide (drain side extension)
Curve Loop(3) = {32, 15, -30, 31};
//+
// Duplicate curve loop (GMSH quirk)
Curve Loop(4) = {32, 15, -30, 31};
//+
// Surface 2: PMOS gate oxide - drain side extension
// Above PMOS drain-side LDD region
Plane Surface(2) = {4};
//+
// Curve loop for PMOS gate oxide (channel region)
Curve Loop(5) = {30, 16, -28, 29};
//+
// Surface 3: PMOS gate oxide - over channel
// This is where PMOS gate control occurs
Plane Surface(3) = {5};
//+
// Curve loop for PMOS gate oxide (source side extension)
Curve Loop(6) = {28, 17, -26, 27};
//+
// Surface 4: PMOS gate oxide - source side extension
// Above PMOS source-side LDD region
Plane Surface(4) = {6};
//+
// Curve loop for STI region (between NMOS and PMOS)
Curve Loop(7) = {33, -10, -9, -8};
//+
// Surface 5: STI (Shallow Trench Isolation) region
// Oxide-filled trench separating NMOS from PMOS
Plane Surface(5) = {7};
//+
// Curve loop for NMOS gate oxide (drain side extension)
Curve Loop(8) = {5, -25, -24, 23};
//+
// Surface 6: NMOS gate oxide - drain side extension
// Above NMOS drain-side LDD region
Plane Surface(6) = {8};
//+
// Curve loop for NMOS gate oxide (channel region)
Curve Loop(9) = {22, 23, -4, -21};
//+
// Surface 7: NMOS gate oxide - over channel
// This is where NMOS gate control occurs
Plane Surface(7) = {9};
//+
// Curve loop for NMOS gate oxide (source side extension)
Curve Loop(10) = {20, 21, -3, 19};
//+
// Surface 8: NMOS gate oxide - source side extension
// Above NMOS source-side LDD region
Plane Surface(8) = {10};
//+
//+

//==============================================================================
// CURVE LOOP AND SURFACE - SILICON BULK REGION
// Define the complete silicon substrate including both transistors
//==============================================================================

//+
// Curve loop for entire silicon bulk region
// Traces the complete boundary of the silicon substrate
// Includes: NMOS body contact, NMOS active, STI, PMOS active, PMOS body contact
Curve Loop(11) = {35, 36, 37, 38, 7, 11, 12, 39, 40, 41, 42, 43, 14, 15, 16, 17, 18, -10, -9, -8, -6, -5, -4, -3, -2, 34};
//+
// Surface 9: Silicon bulk (entire semiconductor region)
// Contains both NMOS and PMOS transistors with their doping profiles
Plane Surface(9) = {11};
//+

//==============================================================================
// PHYSICAL GROUPS - CONTACTS AND REGIONS
// Physical groups define named entities for DEVSIM boundary conditions
// These names must match what's expected in the simulation script
//==============================================================================

//==============================================================================
// ELECTRICAL CONTACT DEFINITIONS
//==============================================================================

// V_out: Inverter output node
// Connected to NMOS drain (Line 6) and PMOS source (Line 18)
// This is a floating node - voltage determined by circuit operation
Physical Curve("V_out") = {6, 18};

// V_in: Inverter input gate
// Connected to both NMOS gate (Line 22) and PMOS gate (Line 29)
// Gates are tied together for complementary switching
Physical Curve("V_in") = {29, 22};

// Ground: Ground reference (0V)
// Connected to NMOS source (Line 2) and NMOS body contact (Line 35)
// NMOS source and P-well both tied to ground
Physical Curve("Ground") = {35, 2};

// V_dd: Power supply
// Connected to PMOS source (Line 14) and PMOS body contact (Line 42)
// PMOS source and N-well both tied to V_dd
Physical Curve("V_dd") = {14, 42};

//==============================================================================
// MATERIAL REGION DEFINITIONS
//==============================================================================

//+
// Silicon bulk region - semiconductor material
// Contains all doped regions for both NMOS and PMOS
Physical Surface("bulk") = {9};
//+
// Oxide regions - gate dielectric material
// Includes: NMOS gate oxide (surfaces 6,7,8), PMOS gate oxide (2,3,4), STI (5)
Physical Surface("oxide") = {8, 7, 6, 4, 3, 2, 5};

//==============================================================================
// INTERFACE DEFINITION
//==============================================================================

//+
// Silicon-Oxide interface
// Critical boundary where inversion layers form under gate bias
// Includes interfaces for both NMOS and PMOS channels and LDD regions
// Also includes STI sidewalls
Physical Curve("oxide_bulk_interface") = {3, 4, 5, 17, 16, 15, 8, 9, 10};

//==============================================================================
// END OF GEOMETRY FILE
//==============================================================================
// To generate mesh, run: gmsh LDD2D_inverter.geo -2
// Output: LDD2D_inverter.msh (for use with DEVSIM)
//
// INVERTER STRUCTURE LAYOUT (left to right):
//   [NMOS P+ Body] - [NMOS N+ Source/GND] - [NMOS LDD] - [NMOS Channel] - 
//   [NMOS LDD] - [NMOS N+ Drain/V_out] - [STI] - [PMOS P+ Source/V_out] - 
//   [PMOS LDD] - [PMOS Channel] - [PMOS LDD] - [PMOS P+ Drain/V_dd] - [PMOS N+ Body]
//
// CONTACT CONNECTIONS:
//   V_dd   → PMOS source + PMOS body (N-well tie)
//   Ground → NMOS source + NMOS body (P-well tie)
//   V_in   → NMOS gate + PMOS gate (common input)
//   V_out  → NMOS drain + PMOS drain (common output, floating)
//
// INVERTER OPERATION:
//   V_in = LOW  → NMOS OFF, PMOS ON  → V_out = HIGH (V_dd)
//   V_in = HIGH → NMOS ON,  PMOS OFF → V_out = LOW  (Ground)
//==============================================================================
