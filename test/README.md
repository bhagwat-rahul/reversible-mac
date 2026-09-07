# Reversible MAC top-level testbench

The cocotb test drives the fixed TinyTapeout interface of `tt_um_bhagwat_rahul_reversible_mac`.
It covers all 4-bit operand pairs, add/subtract cancellation, wraparound,
valid/ena hold, synchronous reset priority and input-only bidirectional pins.

## Setting up

Install `requirements.txt` and Icarus, or use the existing IIC-OSIC-TOOLS
container. Run `iic-pdk sky130A` in each new container shell. The Makefile
includes the two project RTL files and the simulation-only custom cell models.

## How to run

To run the RTL simulation:

```sh
make -B
```

To run gate-level simulation, first complete hardening and copy the final
powered `tt_um_bhagwat_rahul_reversible_mac` netlist to `gate_level_netlist.v`. The ordinary
SKY130 library and the powered Boolean custom-cell models are loaded by the
Makefile. This checks connectivity/function, not custom-cell timing signoff.

Then run:

```sh
make -B GATES=yes
```

If you wish to save the waveform in VCD format instead of FST format, edit tb.v to use `$dumpfile("tb.vcd");` and then run:

```sh
make -B FST=
```

This will generate `tb.vcd` instead of `tb.fst`.

## How to view the waveform file

Using GTKWave

```sh
gtkwave tb.fst tb.gtkw
```

Using Surfer

```sh
surfer tb.fst
```
