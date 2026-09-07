`default_nettype none
// A separately named integration fixture: project.v is deliberately unchanged.
module reversible_cells_smoke (
    input wire [2:0] abc,
    output wire [5:0] result
);
`ifdef USE_POWER_PINS
    supply1 VDD;
    supply0 VGND;
`endif
    rev_not u_not (
`ifdef USE_POWER_PINS
        .VDD(VDD), .VGND(VGND),
`endif
        .A(abc[2]), .Y(result[5])
    );
    rev_cnot u_cnot (
`ifdef USE_POWER_PINS
        .VDD(VDD), .VGND(VGND),
`endif
        .A(abc[2]), .B(abc[1]), .A_OUT(result[4]), .B_OUT(result[3])
    );
    rev_toffoli u_toffoli (
`ifdef USE_POWER_PINS
        .VDD(VDD), .VGND(VGND),
`endif
        .A(abc[2]), .B(abc[1]), .C(abc[0]),
        .A_OUT(result[2]), .B_OUT(result[1]), .C_OUT(result[0])
    );
endmodule

`ifdef TESTBENCH
module testbench;
    reg [2:0] abc;
    wire [5:0] result;
    reversible_cells_smoke dut (.abc(abc), .result(result));
    integer i;
    initial begin
        for (i=0; i<8; i=i+1) begin
            abc=i;
            #1;
            if (result !== {~abc[2], abc[2], abc[2]^abc[1],
                            abc[2], abc[1], abc[0]^(abc[2]&abc[1])})
                $fatal(1, "Incorrect reversible primitive outputs: %b -> %b",abc,result);
        end
        $display("PASS: all primitive truth tables");
        $finish;
    end
endmodule
`endif
`default_nettype wire
