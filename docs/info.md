## How it works

An unsigned 4 × 4-bit multiply-accumulate unit built from custom SKY130 CNOT
and Toffoli gate macros. Each enabled rising edge updates an 8-bit accumulator:
add A × B when reverse is low, or subtract A × B when reverse is high. Results
wrap modulo 256. The accumulator uses conventional flip-flops and synchronous
reset. Logical reversibility does not imply adiabatic operation or energy recovery.

The TinyTapeout signal interface is unchanged. `ui_in[3:0]` is A and
`ui_in[7:4]` is B. `uio_in[0]` is valid, `uio_in[1]` is reverse, and
`uo_out[7:0]` is the accumulator. All bidirectional pins remain inputs; bits
2 through 7 are unused. `ena=0` prevents accumulation, but does not disable reset.

**Prototype status:** RTL and synthesis have been tested; this is not yet a
timing-qualified or physically signed-off submission. 100 kHz is a bring-up
target, not a verified maximum clock frequency. Custom-macro timing models,
placement/power routing, full-design DRC/LVS and TinyTapeout precheck remain
required. The 1×1 tile request is not a proven fit.

## How to test

1. Select the project, drive valid low, and hold `rst_n=0` over a rising clock
   edge. The accumulator becomes zero. Then release reset.
2. Drive `ui_in=0x53` (B=5, A=3), `uio_in=0x01` (valid=1, reverse=0).
   Each rising edge adds 15: outputs become 15, 30, 45, etc.
3. Set `uio_in=0x03` to subtract 15 per rising edge.
4. Set valid low to hold the result. Keeping valid high repeats the operation
   on every clock; there is no request/ready handshake.
5. To exercise wraparound, reset then subtract 1 × 1: output is 255. Adding
   1 × 1 returns it to zero.

Drive operands and controls away from rising edges and meet setup/hold timing.
Undoing an update requires the same operands; reverse does not store history.
Only one maximum-valued product (15 × 15 = 225) fits without possible overflow.

The repository's cocotb regression runs with `make -C test`. It checks all
256 operand pairs, add/subtract cancellation, modular arithmetic, enable/valid
hold, synchronous reset and bidirectional-pin directions.

## External hardware

No special peripheral is required. Use a TinyTapeout-compatible controller or
pattern generator to drive the operands/control bits and read the 8-bit result.
