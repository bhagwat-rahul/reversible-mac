`default_nettype none
// Synthesis view only. Never compile together with reversible_cells.sim.v.
// Read with Yosys read_verilog -lib; do not map the cells back to RTL gates.
(* blackbox *) module rev_not (
`ifdef USE_POWER_PINS
    inout wire VDD, VGND,
`endif
    input wire A,
    output wire Y
);
endmodule

(* blackbox *) module rev_cnot (
`ifdef USE_POWER_PINS
    inout wire VDD, VGND,
`endif
    input wire A, B,
    output wire A_OUT, B_OUT
);
endmodule

(* blackbox *) module rev_toffoli (
`ifdef USE_POWER_PINS
    inout wire VDD, VGND,
`endif
    input wire A, B, C,
    output wire A_OUT, B_OUT, C_OUT
);
endmodule
`default_nettype wire
