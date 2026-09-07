# Reversible SKY130 layout prototypes

Three transistor-level, double-height **LEF `CLASS BLOCK` hard macros**, built
with KLayout Python and the installed SKY130 PCells from the existing Xschem
schematics. The compacted layouts preserve every transistor's W/L and the
logical interfaces. They are **not abuttable single-height standard cells or
a timing/tapeout-ready library**.

| Macro | Devices | Width × height (µm) | Area (µm²) |
|---|---:|---:|---:|
| `rev_not` | 2 | 3.68 × 5.44 | 20.0192 |
| `rev_cnot` | 8 | 8.28 × 5.44 | 45.0432 |
| `rev_toffoli` | 12 | 11.50 × 5.44 | 62.5600 |

### Compaction results and limits

Compared with the original 9.20 × 10.88, 30.82 × 13.60 and 45.54 × 16.32 µm
layouts, widths decrease by **60.0%, 73.1%, 74.7%** and areas decrease by
**80.0%, 89.3%, 91.6%**, respectively (5.0×, 9.3×, 11.9× smaller areas).

NMOS and mirrored PMOS now occupy facing rows, with one shared well and one
contacted tap per body domain. This replaces isolated body-tied transistor
tiles and long external buses. A deterministic grid router connects M1 device
escapes using vertical M2 and horizontal M3 over the devices. Horizontal pitch
is 0.51 µm, limited by 0.37 µm M2 via landings plus 0.14 µm clearance in this
routing architecture. The tested 0.48 µm pitch with smaller landings failed
via-enclosure checks and was rejected. The generator first tries without an
extra output-side routing column; Toffoli needs that column with the current
placement and bounded route-order search.

This is a substantial compaction pass, **not a proof of globally minimum
width**. Device diffusion remains separate. Shared diffusion, folded devices,
different pin placement and lower-metal routing could improve area further.
Height is two 2.72 µm HD rows; widths are multiples of the 0.46 µm site.
There are no standard-cell rail/abutment guarantees: retain macro separation
and routing halos, and verify the assembled layout rather than placing these
edge-to-edge like HD cells.

For the 160 × 100 µm budget, 16 partial-product Toffolis now total **1,000.96
µm²** instead of 11,891.40 µm². That excludes adders, accumulator registers,
temporary-bit cleanup, routing, halos and control. No complete MAC or GEMM
has been synthesized or floorplanned by this pass, so this is not a fit claim.

Timing results are in `characterization/summary.csv` and `timing.csv`.
Nominal means TT, 1.8 V, 27 °C, 100 ps input ramps and 10 fF/output.
Summary delays exclude physically shorted preserved outputs. See the parent
README for stimulus, PVT pairings and measurement definitions.

## Files

- `views/<cell>/<cell>.oas` and `.gds`: complete, flattened physical geometry.
- `.lef`: boundary, M3 pins and conservative LI/M1/M2/M3 routing obstructions.
  Pin-access corridors reach the boundary; upper metals remain available.
- `.schematic.spice`, `.lvs.spice`, `.pex.spice`: reference and extracted circuits.
  **PEX contains capacitance, not distributed wire resistance.**
- `geometry.json`: dimensions, ports, devices and physical pin aliases.
- `.png`: KLayout rendering of the delivered OAS.
- `verification/`: DRC, LVS, extraction logs and raw extracted netlists.
- `verification.json`: verification results and checked GDS SHA-256 hashes.
- `characterization/{summary,timing}.csv`: 45 passing extracted simulations
  across five process corners and three paired voltage/temperature points;
  690 transition measurements. This is a single-slew/single-load sweep.
- `views/reversible_cells.functional_only.lib`: functions, area and power
  pins for physical import, with `dont_use`; **no timing arcs, capacitance
  tables or power models**. Do not use its absence of timing for STA closure.
- `reversible_cells.blackbox.v`: synthesis declarations.
- `reversible_cells.sim.v`: Boolean simulation models (not physical timing).
- `smoke.v`, `check_integration.py`, `smoke.tcl`, `integration/`: reproducible
  synthesis, simulation, placement and signal-routing example and results.

## Reproduce in the running container

From the host, enter the existing container rather than starting another:

```sh
docker exec -it -w /foss/designs/current-designs/reversible-circuit/reversible_stdcells/layout \
  iic-osic-tools_xserver_uid_501 bash -i
iic-pdk sky130A
python3 build.py
python3 validate.py
python3 ../characterize.py --extracted-dir views --output-dir characterization
python3 check_integration.py
klayout -e -b -r render.py
```

Run `iic-pdk sky130A` in **every new shell**, before any EDA command. For
headless `docker exec`, use `bash -ic 'iic-pdk sky130A; ...'` since this image
defines it as an interactive Bash alias. Scripts inherit the PDK environment.
Rebuilding geometry requires repeating validation and characterization.

## Verilog and physical integration

Instantiate these modules explicitly; arithmetic RTL is not automatically
mapped into reversible gates. For example:

```verilog
rev_cnot u_cnot (
    .A(control), .B(data),
    .A_OUT(control_out), .B_OUT(data_out)
);
```

For synthesis, read `reversible_cells.blackbox.v` as a library (Yosys
`read_verilog -lib`) before reading your RTL. For simulation, compile
`reversible_cells.sim.v` **instead**, never both definitions. Define
`USE_POWER_PINS` consistently if explicitly connecting `.VDD(...)` and
`.VGND(...)`; otherwise the physical flow must connect those LEF power pins
globally. Both interface variants are covered by the integration test.

Load the SKY130 technology LEF, these three macro LEFs and the functional-only
Liberty into the physical flow. Floorplan them as blocks with routing access,
connect a real PDN to VDD/VGND, and merge the supplied GDS/OAS geometry during
stream-out. `smoke.tcl` demonstrates LEF import, macro placement, global supply
connections and signal routing; it does **not** build a physical PDN or perform
final merged-layout signoff. `project.v` is intentionally unchanged: its current
top is an ordinary 8-bit addition example, not a reversible macro assembly.

### Preserved outputs are wires

CNOT's A_OUT is physically shorted to A. Toffoli's A_OUT/B_OUT are shorted to
A/B. These are not buffers: downstream load is seen by the upstream driver.
Use only one driver per aliased net and do not treat these ports as independent
electrical nets during extraction, timing, or chip-level LVS.

The schematic zero-volt VKEEP sources represent those wires. Magic extraction
uses `ext2spice short voltage` to retain all logical ports. Validation checks
that the independently extracted shorts are **exactly** the expected aliases,
then normalizes their polarity and device-node names before Netgen comparison.
Unnormalized extraction is retained as `verification/{lvs,pex}.raw.spice`.

## Verified scope and remaining work

All three macros pass Magic DRC, the installed KLayout macro deck
(FEOL/BEOL/grid/pin/zero-area), Netgen LVS, GDS/OAS geometry comparison and
pin-metal coverage checks. Icarus checks all Boolean truth rows; Yosys retains
the three blackboxes with and without explicit supply ports. OpenROAD imports
and routes the three-macro smoke design with **zero detailed-router DRCs**.
The smoke floorplan is 160 × 100 µm; it contains only three gates, not a GEMM.

Before production arithmetic integration: realistic cascaded-driver simulations,
drive sizing as needed, distributed RC
extraction, slew/load/PVT timing and power libraries (including proper handling
of wire aliases and transmission-gate paths), physical PDN, and final chip-level
DRC/LVS/antenna/density checks are still required. This macro deck excludes
chip-level density and antenna checks. Logical reversibility alone does not
make these ordinary CMOS circuits adiabatic or electrically bidirectional.
