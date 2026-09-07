`default_nettype none
// Zero-delay Boolean simulation view, NOT a synthesis or transistor model.
module rev_not (
`ifdef USE_POWER_PINS
    inout wire VDD, VGND,
`endif
    input wire A,
    output wire Y
);
    assign Y = ~A;
endmodule

module rev_cnot (
`ifdef USE_POWER_PINS
    inout wire VDD, VGND,
`endif
    input wire A, B,
    output wire A_OUT, B_OUT
);
    assign A_OUT = A;
    assign B_OUT = A ^ B;
endmodule

module rev_toffoli (
`ifdef USE_POWER_PINS
    inout wire VDD, VGND,
`endif
    input wire A, B, C,
    output wire A_OUT, B_OUT, C_OUT
);
    assign A_OUT = A;
    assign B_OUT = B;
    assign C_OUT = C ^ (A & B);
endmodule
`default_nettype wire
