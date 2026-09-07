`default_nettype none

// Unsigned accumulator update: S <- S +/- A*B, modulo 2**ACC_WIDTH.
// Defaults preserve the original interface. For a small experiment use
// INPUT_WIDTH=4, ACC_WIDTH=12 (up to 18 maximum-valued products without wrap).
// Arithmetic uses only our CNOT/Toffoli cells; storage/reset are conventional.
// Compile with reversible_cells.sim.v OR reversible_cells.blackbox.v, not both.
module reversible_mac #(
    parameter integer INPUT_WIDTH = 8,
    parameter integer ACC_WIDTH = 32
) (
`ifdef USE_POWER_PINS
    inout wire VDD, VGND,
`endif
    input  logic        clk,
    input  logic        rst_n,
    input  logic        valid,
    input  logic        reverse,

    input  logic [INPUT_WIDTH-1:0] a_in,
    input  logic [INPUT_WIDTH-1:0] b_in,

    output wire [INPUT_WIDTH-1:0] a_out,
    output wire [INPUT_WIDTH-1:0] b_out,
    output wire [ACC_WIDTH-1:0] running_sum_out
);

    logic [ACC_WIDTH-1:0] accumulator;
    wire [ACC_WIDTH-1:0] stage [0:INPUT_WIDTH];
    wire [ACC_WIDTH-1:0] next_sum;

`ifndef SYNTHESIS
    initial begin
        if (INPUT_WIDTH < 1 || ACC_WIDTH < 2*INPUT_WIDTH)
            $fatal(1, "Require INPUT_WIDTH >= 1 and ACC_WIDTH >= 2*INPUT_WIDTH");
    end
`endif

    // ~S + P, complemented again, is S-P modulo the accumulator width.
    // Conditional complement avoids an irreversible add/sub mux or a second
    // multiplier. rev_not is unnecessary: these inversions are controlled.
    for (genvar bit_index = 0; bit_index < ACC_WIDTH; bit_index = bit_index+1) begin : sign_control
        rev_cnot before_add (
`ifdef USE_POWER_PINS
            .VDD(VDD), .VGND(VGND),
`endif
            .A(reverse), .B(accumulator[bit_index]),
            .A_OUT(), .B_OUT(stage[0][bit_index])
        );
        rev_cnot after_add (
`ifdef USE_POWER_PINS
            .VDD(VDD), .VGND(VGND),
`endif
            .A(reverse), .B(stage[INPUT_WIDTH][bit_index]),
            .A_OUT(), .B_OUT(next_sum[bit_index])
        );
    end

    // Accumulate one shifted partial-product row per combinational stage.
    // The adder restores its addend and carry ancilla, so each partial product
    // can then be uncomputed using the unchanged multiplier inputs.
    for (genvar row = 0; row < INPUT_WIDTH; row = row+1) begin : partial_row
        localparam integer ROW_WIDTH = ACC_WIDTH-row;
        wire [ROW_WIDTH-1:0] addend;
        wire [ROW_WIDTH-1:0] restored_addend;
        wire [INPUT_WIDTH-1:0] cleaned_product;
        wire cleaned_carry;

        for (genvar col = 0; col < INPUT_WIDTH; col = col+1) begin : partial_bit
            rev_toffoli compute (
`ifdef USE_POWER_PINS
                .VDD(VDD), .VGND(VGND),
`endif
                .A(a_in[col]), .B(b_in[row]), .C(1'b0),
                .A_OUT(), .B_OUT(), .C_OUT(addend[col])
            );
            // Retain cleanup even though its known-zero result is not an
            // external output; ordinary synthesis would otherwise prune it.
            (* keep *) rev_toffoli uncompute (
`ifdef USE_POWER_PINS
                .VDD(VDD), .VGND(VGND),
`endif
                .A(a_in[col]), .B(b_in[row]), .C(restored_addend[col]),
                .A_OUT(), .B_OUT(), .C_OUT(cleaned_product[col])
            );
        end
        assign addend[ROW_WIDTH-1:INPUT_WIDTH] = '0;
        if (row > 0) begin : unshifted_bits
            assign stage[row+1][row-1:0] = stage[row][row-1:0];
        end
        reversible_mac_add #(.WIDTH(ROW_WIDTH)) add_row (
`ifdef USE_POWER_PINS
            .VDD(VDD), .VGND(VGND),
`endif
            .a(addend), .b(stage[row][ACC_WIDTH-1:row]),
            .sum(stage[row+1][ACC_WIDTH-1:row]),
            .a_restored(restored_addend), .carry_restored(cleaned_carry)
        );
    end

    always_ff @(posedge clk) begin
        if (!rst_n) begin
            accumulator <= '0;
        end
        else if (valid) begin
            accumulator <= next_sum;
        end
    end

    // Preserved outputs are wires, not buffers. The gate A_OUT/B_OUT ports
    // above are left open: they physically alias their input nets, and must
    // not be joined as additional drivers in a digital netlist.
    assign a_out = a_in;
    assign b_out = b_in;
    assign running_sum_out = accumulator;
endmodule

// Cuccaro-style MAJ / inverse-UMA ripple adder:
// (a,b,0) -> (a,a+b mod 2**WIDTH,0). No discarded carry or garbage bits.
// Forward MAJ: p=b^a, q=carry^a, carry_next=a^(p&q).
// Backward UMA: restore a, restore carry, then sum=p^restored_carry.
// The most significant bit only needs two XORs; overflow is modular.
module reversible_mac_add #(
    parameter integer WIDTH = 8
) (
`ifdef USE_POWER_PINS
    inout wire VDD, VGND,
`endif
    input wire [WIDTH-1:0] a, b,
    output wire [WIDTH-1:0] sum, a_restored,
    output wire carry_restored
);
    wire [WIDTH-1:0] carry, uncarry;
    wire [WIDTH-2:0] p, q;
    wire top_xor;
    assign carry[0] = 1'b0;
    assign uncarry[WIDTH-1] = carry[WIDTH-1];
    assign carry_restored = uncarry[0];
    assign a_restored[WIDTH-1] = a[WIDTH-1];

    for (genvar i = 0; i < WIDTH-1; i = i+1) begin : ripple
        rev_cnot maj_b (
`ifdef USE_POWER_PINS
            .VDD(VDD), .VGND(VGND),
`endif
            .A(a[i]), .B(b[i]), .A_OUT(), .B_OUT(p[i])
        );
        rev_cnot maj_c (
`ifdef USE_POWER_PINS
            .VDD(VDD), .VGND(VGND),
`endif
            .A(a[i]), .B(carry[i]), .A_OUT(), .B_OUT(q[i])
        );
        rev_toffoli maj_a (
`ifdef USE_POWER_PINS
            .VDD(VDD), .VGND(VGND),
`endif
            .A(p[i]), .B(q[i]), .C(a[i]),
            .A_OUT(), .B_OUT(), .C_OUT(carry[i+1])
        );
        rev_toffoli uma_a (
`ifdef USE_POWER_PINS
            .VDD(VDD), .VGND(VGND),
`endif
            .A(p[i]), .B(q[i]), .C(uncarry[i+1]),
            .A_OUT(), .B_OUT(), .C_OUT(a_restored[i])
        );
        rev_cnot uma_c (
`ifdef USE_POWER_PINS
            .VDD(VDD), .VGND(VGND),
`endif
            .A(a_restored[i]), .B(q[i]), .A_OUT(), .B_OUT(uncarry[i])
        );
        rev_cnot uma_b (
`ifdef USE_POWER_PINS
            .VDD(VDD), .VGND(VGND),
`endif
            .A(uncarry[i]), .B(p[i]), .A_OUT(), .B_OUT(sum[i])
        );
    end
    rev_cnot msb_a (
`ifdef USE_POWER_PINS
        .VDD(VDD), .VGND(VGND),
`endif
        .A(a[WIDTH-1]), .B(b[WIDTH-1]), .A_OUT(), .B_OUT(top_xor)
    );
    rev_cnot msb_c (
`ifdef USE_POWER_PINS
        .VDD(VDD), .VGND(VGND),
`endif
        .A(carry[WIDTH-1]), .B(top_xor), .A_OUT(), .B_OUT(sum[WIDTH-1])
    );
endmodule
`default_nettype wire
