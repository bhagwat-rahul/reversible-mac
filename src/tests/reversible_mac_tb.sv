`timescale 1ns/1ps
`default_nettype none

module mac_case #(parameter W=4, S=12) (output reg done=0);
    reg clk=0, rst_n=0, valid=0, reverse=0;
    reg [W-1:0] a=0, b=0;
    wire [W-1:0] ao, bo;
    wire [S-1:0] sum;
    reg [S-1:0] expected=0, saved;
    reg [31:0] random_state=32'h13579bdf;
    integer checks=0;
`ifdef USE_POWER_PINS
    supply1 VDD;
    supply0 VGND;
`endif
    reversible_mac #(.INPUT_WIDTH(W), .ACC_WIDTH(S)) dut (
`ifdef USE_POWER_PINS
        .VDD(VDD), .VGND(VGND),
`endif
        .clk(clk), .rst_n(rst_n), .valid(valid), .reverse(reverse),
        .a_in(a), .b_in(b), .a_out(ao), .b_out(bo), .running_sum_out(sum)
    );

    // Check the claimed reversible cleanup, not only the observable result.
    for (genvar r=0; r<W; r=r+1) begin : cleanup_checks
        always @(posedge clk) if (rst_n) begin
            if (dut.partial_row[r].restored_addend !== dut.partial_row[r].addend ||
                dut.partial_row[r].cleaned_product !== {W{1'b0}} ||
                dut.partial_row[r].cleaned_carry !== 1'b0)
                $fatal(1, "Ancilla not restored W=%0d S=%0d row=%0d", W,S,r);
        end
    end

    task step(input [W-1:0] av,bv, input subtract,enable,reset_n);
        begin
            a=av; b=bv; reverse=subtract; valid=enable; rst_n=reset_n;
            #2;
            if (sum !== expected) $fatal(1,"Accumulator changed without a clock");
            if (ao !== a || bo !== b) $fatal(1,"Inputs not preserved");
            if (!reset_n) expected=0;
            else if (enable) begin
                if (subtract) expected=expected-av*bv;
                else expected=expected+av*bv;
            end
            clk=1;
            #1;
            if (sum !== expected)
                $fatal(1,"MAC mismatch W=%0d S=%0d a=%0d b=%0d reverse=%b got=%h expected=%h",
                       W,S,a,b,reverse,sum,expected);
            clk=0;
            checks=checks+1;
            #1;
        end
    endtask

    initial begin
        // Synchronous reset: initialize at an edge, not by a testbench force.
        #1; clk=1; #1; clk=0;
        step('1,'1,0,1,0); // reset overrides valid
        step(1,1,1,1,1);   // underflow
        step(1,1,0,1,1);   // overflow back to zero
        repeat (20) step('1,'1,0,1,1);
        step('1,'1,1,0,1); // hold despite changing operation
        if (W<=4) begin
            for (integer i=0; i<(1<<W); i=i+1)
                for (integer j=0; j<(1<<W); j=j+1) begin
                    saved=expected;
                    step(i,j,0,1,1);
                    step(i,j,1,1,1);
                    if (sum !== saved) $fatal(1,"Forward/reverse not inverse");
                    step(i,j,(i^j)&1,1,1);
                end
        end
        repeat (2000) begin
            random_state=random_state ^ (random_state<<13);
            random_state=random_state ^ (random_state>>17);
            random_state=random_state ^ (random_state<<5);
            step(random_state[7:0],random_state[15:8],random_state[16],
                 random_state[17],random_state[23:18]!=0);
        end
        step('1,'1,1,1,0);
        $display("PASS MAC W=%0d S=%0d: %0d cycles, cleanup and reference arithmetic",W,S,checks);
        done=1;
    end
endmodule

module reversible_mac_tb;
    wire [3:0] done;
    mac_case #(.W(1),.S(2)) minimum_width(done[0]);
    mac_case #(.W(4),.S(8)) small_wrap(done[1]);
    mac_case #(.W(4),.S(12)) dot_product(done[2]);
    mac_case #(.W(8),.S(32)) original_interface(done[3]);
    initial begin
        wait (&done);
        $display("PASS all reversible MAC cases");
        $finish;
    end
    initial begin
        #100000;
        $fatal(1,"Timed out");
    end
endmodule
`default_nettype wire
