/*
 * Copyright (c) 2026 Rahul Bhagwat
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_bhagwat_rahul_reversible_mac (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  reversible_mac #(.INPUT_WIDTH(4), .ACC_WIDTH(8)) u_mac (
      .clk(clk), .rst_n(rst_n),
      .valid(ena & uio_in[0]), .reverse(uio_in[1]),
      .a_in(ui_in[3:0]), .b_in(ui_in[7:4]),
      .a_out(), .b_out(), .running_sum_out(uo_out)
  );

  // Bidirectional pins are inputs: bit 0 valid, bit 1 reverse.
  assign uio_out = 8'b0;
  assign uio_oe  = 8'b0;

  wire _unused = &{uio_in[7:2], 1'b0};

endmodule
