SetFactory("OpenCASCADE"); // OpenCASCADE kernel

channel_length = 2e-6;
extension_length = 2e-6;	
bulk_height = 2e-5;
oxide_thickness = 2e-7;	
source_contact = 4e-6;
drain_contact = 4e-6;

// Mesh Densities
finer_mesh = 5e-8;
fine_mesh   = 2e-7; // Fine mesh size
coarse_mesh = 3e-6; // Coarse mesh size

// Dynamic Widths
oxide_width  = extension_length * 2 + channel_length; // Total oxide width
device_width = source_contact + oxide_width + drain_contact; // Total device width

// 2. POINTS
Point(1) = {0, 0, 0, coarse_mesh}; // Bottom-left bulk
Point(2) = {device_width, 0, 0, coarse_mesh}; // Bottom-right bulk
Point(3) = {device_width, bulk_height, 0, fine_mesh}; // Top-right bulk
Point(4) = {source_contact + oxide_width, bulk_height, 0, fine_mesh}; // Right oxide edge
Point(5) = {source_contact, bulk_height, 0, fine_mesh}; // Left oxide edge
Point(6) = {0, bulk_height, 0, fine_mesh}; // Top-left bulk
Point(7) = {source_contact, bulk_height + oxide_thickness, 0, finer_mesh}; // Top-left oxide
Point(8) = {source_contact + oxide_width, bulk_height + oxide_thickness, 0, finer_mesh}; // Top-right oxide

// 3. LINES
Line(1) = {1, 2}; // Bottom boundary
Line(2) = {2, 3}; // Right boundary
Line(3) = {3, 4}; // Drain contact
Line(4) = {4, 5}; // Si/SiO2 interface
Line(5) = {5, 6}; // Source contact
Line(6) = {6, 1}; // Left boundary
Line(7) = {5, 7}; // Left oxide wall
Line(8) = {7, 8}; // Gate contact
Line(9) = {8, 4}; // Right oxide wall

// 4. SURFACES
Curve Loop(1) = {1, 2, 3, 4, 5, 6}; // Bulk boundary loop
Plane Surface(1) = {1}; // Silicon bulk
Curve Loop(2) = {-4, -9, -8, -7}; // Oxide boundary loop 
Plane Surface(2) = {2}; // Gate oxide

// 5. PHYSICAL GROUPS
Physical Surface("bulk")  = {1}; // Bulk material
Physical Surface("oxide") = {2}; // Oxide material
Physical Curve("body")   = {1}; // Body terminal
Physical Curve("drain")  = {3}; // Drain terminal
Physical Curve("oxide_bulk_interface") = {4}; // Interface boundary
Physical Curve("source") = {5}; // Source terminal
Physical Curve("gate")   = {8}; // Gate terminal