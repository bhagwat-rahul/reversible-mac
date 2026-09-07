# SKY130 reversible CMOS cells

Exactly three cell schematics and three testbench schematics:

| Cell | Schematic | Testbench | Mapping | MOS count |
|---|---|---|---|---|
| NOT | `rev_not/rev_not.sch` | `rev_not/tb_rev_not.sch` | A → NOT A | 2 |
| CNOT | `rev_cnot/rev_cnot.sch` | `rev_cnot/tb_rev_cnot.sch` | A,B → A,A XOR B | 8 |
| Toffoli | `rev_toffoli/rev_toffoli.sch` | `rev_toffoli/tb_rev_toffoli.sch` | A,B,C → A,B,C XOR (A AND B) | 12 |

Each directory also contains its hierarchical `.sym`. The existing NOT
schematic was preserved unchanged, including its `VDD`/`VGND` supply names.
All cells use these supply names, ordinary input/output directions, and
`sky130_fd_pr__nfet_01v8` / `sky130_fd_pr__pfet_01v8` models.

These implement the shared conversation's **logically reversible, conventional
CMOS** approach, not adiabatic or electrically bidirectional computation.

Compacted LEF/OAS/GDS hard macros, Verilog blackboxes, extracted characterization
and physical verification are documented in [layout/README.md](layout/README.md).
They are double-height layout prototypes, not a timing-qualified standard-cell library.

## Circuit choices

- NOT: existing Wn = Wp = 1 µm, L = 0.15 µm inverter.
- CNOT: two CMOS inverters generate A_BAR and B_BAR. Two complementary
  transmission gates select B for A=0 and B_BAR for A=1.
- Toffoli: a static NAND2 plus inverter generates T=A AND B; a C inverter
  and two transmission gates select C for T=0 and C_BAR for T=1.
- W=1 µm, L=0.15 µm everywhere except the two series NAND NMOS devices,
  which have W=2 µm. All devices have nf=1 and multiplicity=1.
  These are initial sizes, not balanced or optimized drive strengths.
- NMOS bulks connect to VGND; PMOS bulks connect to VDD.
- Matching net labels connect the separated transistor groups.
- `VKEEPA` and `VKEEPB` are **zero-volt wire models**, not physical supplies:
  they preserve distinct subcircuit input/output pin names while enforcing
  identical voltages. They become metal connections in layout. An eventual
  LVS/CDL flow must handle these as shorts, not fabricated voltage sources.
  They are not output buffers. Preserved-output load is seen by the input driver.

## Gate-level reversible MAC

[`../reversible_mac.v`](../reversible_mac.v) explicitly instantiates CNOT and
Toffoli cells, with no behavioral multiply/add/subtract in the datapath. Its
defaults remain unsigned 8-bit operands and a 32-bit accumulator. A smaller
instance can use:

```verilog
reversible_mac #(.INPUT_WIDTH(4), .ACC_WIDTH(12)) u_mac (
    .clk(clk), .rst_n(rst_n), .valid(valid), .reverse(reverse),
    .a_in(a), .b_in(b), .a_out(a_preserved), .b_out(b_preserved),
    .running_sum_out(sum)
);
```

Here `a`, `b` and preserved outputs are 4 bits; `sum` is 12 bits. Parameters
require INPUT_WIDTH >= 1 and ACC_WIDTH >= 2 × INPUT_WIDTH. On each rising edge:
reset low clears the accumulator synchronously; otherwise valid high adds the
unsigned product, or subtracts it when reverse is high. Valid low holds state.
Arithmetic wraps modulo 2**ACC_WIDTH. Inputs are preserved combinationally,
not registered. Applying a forward update and then its reverse with the **same
operands** restores the accumulator; reverse does not remember past inputs.
Starting at zero, 12 bits accommodate 18 worst-case 4-bit products (18 × 225 =
4,050); 8 bits only accommodate one worst-case product before possible wrap.

The combinational network computes shifted partial products with Toffoli,
adds each row through a MAJ/UMA ripple adder, restores the addend/carry, and
uncomputes the partial products. Cleanup cells have `keep` attributes so Yosys
does not prune their unused zero outputs. Conditional CNOT complements before
and after accumulation implement subtraction; no standalone NOT is needed.
This is logically reversible arithmetic with ordinary flip-flops and reset,
not physically reversible storage, energy recovery, or a quantum circuit.

Compile as SystemVerilog (`iverilog -g2012` / Yosys `read_verilog -sv`). Use
`layout/reversible_cells.sim.v` for simulation, or read
`layout/reversible_cells.blackbox.v` with Yosys `read_verilog -lib` for synthesis;
never compile both. Define `USE_POWER_PINS` consistently to expose and connect
VDD/VGND on the MAC and its cells. Cell alias outputs are left open internally
instead of connecting multiple output ports to the same digital net; their
physical input/output shorts still need correct chip-level LVS treatment.

Run the self-checking regression inside the container from the repository root:

```sh
iic-pdk sky130A
python3 tests/check_reversible_mac.py
```

Tests cover every 4-bit operand pair, seeded random sequences, reset priority,
valid hold, modular wrap, forward/reverse cancellation and restored temporary
bits, with and without explicit supplies. Yosys checks retain exactly these
arithmetic macros plus accumulator flip-flops:

| Operand / accumulator bits | CNOT | Toffoli | Macro-only area (µm²) |
|---|---:|---:|---:|
| 4 / 8 | 112 | 76 | 9,799.40 |
| 4 / 12 | 184 | 108 | 15,044.43 |
| 8 / 32 | 960 | 568 | 78,775.55 |

These areas exclude flip-flops, tie cells, buffers, PDN and routing halos.
**The 4/12 version leaves insufficient practical margin in 160 × 100 µm; the
8/32 version exceeds it outright.** No MAC place/route or timing closure has
been performed. The 4/8 version is only a candidate for physical exploration,
not a verified fit. A useful wider-accumulator GEMM in that area needs further
arithmetic optimization, smaller cells, or a time-multiplexed architecture.
The entire multiplier/adder chain is combinational between accumulator edges;
the testbench's zero-delay timing does not establish a physical clock period.

## Open and run in the existing IIC-OSIC-TOOLS container

From the host (uses the existing container; does not start another one):

```sh
docker exec -it iic-osic-tools_xserver_uid_501 bash
iic-pdk sky130A
cd /foss/designs/current-designs/reversible-circuit/reversible_stdcells
xschem --rcfile "$PWD/xschemrc" rev_cnot/tb_rev_cnot.sch
```

Use the local `xschemrc` when opening files from outside a cell directory;
it loads SKY130 symbols and all three local cell symbols. Always run
`iic-pdk sky130A` in **each new shell**. In this image it is an interactive
Bash alias; a plain `bash -lc` does not define it.

For reproducible headless characterization, from the host:

```sh
docker exec iic-osic-tools_xserver_uid_501 bash -ic \
  'iic-pdk sky130A; python3 /foss/designs/current-designs/reversible-circuit/reversible_stdcells/characterize.py'
```

The Python runner invokes Xschem and ngspice directly, inheriting that PDK
environment. It uses temporary netlists/waveforms, fails on simulation,
truth-table, or timing errors, and writes `summary.csv` and `timing.csv`
only after the complete sweep passes. NumPy is already installed in the image.
The runner does not modify the schematics.

Individual testbenches run nominal TT / 1.8 V / 27 °C from Xschem's normal
netlist/simulate workflow and export `wave.txt` in the simulator working
directory. Their SIM blocks contain the transient analysis; MODELS selects
the corner. Each input source has a readable `PWL / 100 ps` display value;
its actual SPICE waveform is in the source's **`stimulus` property**, used by
its instance `format` override. Edit `stimulus`, not the display label, to
change a waveform. Automated pass/fail and timing extraction are in the runner.

## Characterization conditions and interpretation

- Process: **tt, ss, ff, sf, fs**.
- Each process is tested at these three paired operating points:
  **1.8 V / 27 °C**, **1.62 V / 125 °C**, **1.98 V / −40 °C**.
  This is 15 conditions per cell, **45 simulations** total, not a full
  independent voltage × temperature grid.
- Ideal input voltage drivers, **100 ps full 0–100% ramps** (60 ps 20–80%).
- **10 fF on every output**, including preserved outputs.
- 5 ps transient step; 20 ns per directed transition, with 10 ns to establish
  its initial state and 10 ns after changing one input.
- All 2/4/8 truth-table rows are checked for NOT/CNOT/Toffoli. All 2/8/24
  directed single-input transitions are exercised respectively. Inputs and
  outputs are checked 5 ns before and after each measured transition against
  the independent Boolean mapping. Low must be within −10% to +10% VDD;
  high within 90% to 110% VDD.
- Every sensitized input→output transition is measured: delay is input 50%
  crossing to output 50% crossing; slew is output 20–80% rise or 80–20% fall.
  Missing or multiple crossings in the measurement window fail the run.
- `timing.csv` identifies the state, input, output and output edge for every
  measurement. `ideal_wire=True` explicitly marks preserved-output paths;
  their zero intrinsic delay is **not** a transistor drive-strength result.
  `summary.csv` reports worst delay and slew over **non-wire paths only**.

This is a **pre-layout, single-slew/single-load characterization**, not a
Liberty library, extracted signoff, power characterization, or hazard-free
switching guarantee. Unsensitized outputs are checked at settled sample
times, not for all transient glitches. Transmission-gate data paths load
their input sources and may conduct in either direction internally; input
driver resistance, cascaded-cell behavior, parasitics, and slew/load grids
need separate evaluation before using these as a production cell library.

## Truth tables

```text
NOT       CNOT          TOFFOLI
A  Y      AB  A_OUT B_OUT   ABC  A_OUT B_OUT C_OUT
0  1      00     0 0       000       0 0 0
1  0      01     0 1       001       0 0 1
          10     1 1       010       0 1 0
          11     1 0       011       0 1 1
                          100       1 0 0
                          101       1 0 1
                          110       1 1 1
                          111       1 1 0
```
