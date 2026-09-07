# OpenROAD physical-import test only: deliberately does NOT claim STA closure.
set root [file dirname [file normalize [info script]]]
read_lef $::env(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/techlef/sky130_fd_sc_hd__nom.tlef
read_lef $::env(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef
foreach cell {rev_not rev_cnot rev_toffoli} {
    read_lef $root/views/$cell/$cell.lef
}
read_liberty $root/views/reversible_cells.functional_only.lib
read_verilog $root/integration/smoke_netlist.v
link_design reversible_cells_smoke
initialize_floorplan -die_area {0 0 160 100} -core_area {4.6 5.44 155.4 94.56} -site unithd
make_tracks
place_macro -macro_name u_not -location {9.2 10.88} -orientation R0
place_macro -macro_name u_cnot -location {23 32.64} -orientation R0
place_macro -macro_name u_toffoli -location {59.8 54.4} -orientation R0
add_global_connection -net VDD -inst_pattern .* -pin_pattern VDD -power
add_global_connection -net VGND -inst_pattern .* -pin_pattern VGND -ground
global_connect
set block [ord::get_db_block]
if {[llength [$block getInsts]] != 3} { error "Expected exactly three blackbox instances" }
foreach inst [$block getInsts] {
    if {![[$inst getMaster] isBlock]} { error "Not a hard macro: [$inst getName]" }
    foreach iterm [$inst getITerms] {
        if {[$iterm getNet] == "NULL"} { error "Unconnected macro terminal" }
    }
}
file mkdir $root/integration
place_pins -hor_layers met3 -ver_layers met2
set_wire_rc -signal -layer met2
set_routing_layers -signal met1-met4
global_route
detailed_route -output_drc $root/integration/routing.drc
if {[detailed_route_num_drvs] != 0} { error "Signal-routing DRC violations" }
write_def $root/integration/smoke.def
write_db $root/integration/smoke.odb
puts "PASS: all three LEFs link and signal-route with zero router DRCs. No timing, PDN, or chip-level signoff performed."
