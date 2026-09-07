![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg) ![](../../workflows/fpga/badge.svg)

# TinyTapeout 4/8 reversible-gate MAC

- [Read the documentation for project](docs/info.md)

**Prepared for development and submission review, not cleared for fabrication.**
The top signal interface is unchanged; the module is `tt_um_reversible_mac`.
Operands are `ui_in[3:0]` / `ui_in[7:4]`, valid/reverse are `uio_in[0]` /
`uio_in[1]`, and `uo_out` is the 8-bit accumulator. All bidirectional pins are
inputs. Reset is synchronous, and arithmetic wraps modulo 256.

## Included files

- `src/project.v`, `src/reversible_mac.v`: wired 4-bit/8-bit implementation.
- `src/reversible_stdcells/`: all three Xschem schematics, symbols and benches,
  characterization scripts/CSVs, KLayout layout generator/router, GDS/OAS/LEF,
  extraction and verification reports, Verilog models and layout screenshots.
- `src/tests/`: standalone MAC arithmetic/cleanup/synthesis regression.
- `test/`: cocotb tests through the TinyTapeout pins.
- `src/config.json`: LibreLane custom macro views, synthesis blackboxes and
  VPWR/VGND-to-VDD/VGND macro power-net hooks. No signal pins were added.

Copied cell collateral comes from the local `reversible-circuit` workspace,
including its uncommitted MAC implementation—not a remote branch. Archived
reports may contain original absolute paths. Use the Python entry points to
regenerate them here; do not run archived generated Tcl scripts directly.
The copied cell READMEs contain the original workspace's examples; use the
paths below for this repository. No sibling repository is needed to build RTL.

## Local checks in IIC-OSIC-TOOLS

```sh
docker exec -it -w /foss/designs/current-designs/reversible-mac \
  iic-osic-tools_xserver_uid_501 bash -i
iic-pdk sky130A
make -C test
python3 src/tests/check_reversible_mac.py
# To recheck the copied physical cells (not the assembled MAC):
python3 src/reversible_stdcells/layout/validate.py
```

Always run `iic-pdk sky130A` in each new container shell. For Xschem, use
`xschem --rcfile "$PWD/src/reversible_stdcells/xschemrc"` followed by a cell or
testbench schematic path. `info.yaml` lists only project RTL; LibreLane obtains
the cell declarations from `EXTRA_VERILOG_MODELS`. The cocotb Makefile instead
loads the zero-delay Boolean models, including for eventual gate-level tests.
Never substitute those simulation models into physical synthesis. The optional
FPGA workflow is not configured to replace these ASIC blackboxes.

## Remaining submission blockers

- **Fit is unproven:** 112 CNOT + 76 Toffoli macros alone occupy 9,799.40 µm².
  Local SKY130 synthesis adds about 521.75 µm² of ordinary cells, before physical
  buffering, macro spacing, PDN and routing. Synthesis's reported area alone
  excludes the blackboxes and must not be mistaken for total area.
- **Timing is unqualified:** custom cells lack characterized Liberty timing
  arcs. Their functional-only Liberty is copied for reference, but deliberately
  not loaded by the production config. 100 kHz/10,000 ns is only a bring-up
  target, not timing closure. A green flow with blackboxed STA is insufficient.
- **Physical integration is unfinished:** place all 188 macros, validate power
  access to their small M3 pins, route the design, and run full chip-level
  DRC/LVS/antenna/density checks plus TinyTapeout precheck. PDN hooks name the
  nets; they do not themselves build a working physical supply network.
- **LVS must handle wire aliases:** A_OUT/B_OUT are physical shorts to their
  inputs, not independent buffers. Cell-level validation normalizes those
  aliases; the final assembled design needs equivalent correct treatment.

The template workflows remain enabled; no failing checks have been disabled
to imply tapeout readiness. Nothing has been pushed or submitted.

## What is Tiny Tapeout?

Tiny Tapeout is an educational project that aims to make it easier and cheaper than ever to get your digital and analog designs manufactured on a real chip.

To learn more and get started, visit https://tinytapeout.com.

The GitHub action will automatically build the ASIC files using [LibreLane](https://www.zerotoasiccourse.com/terminology/librelane/).

## Enable GitHub actions to build the results page

- [Enabling GitHub Pages](https://tinytapeout.com/faq/#my-github-action-is-failing-on-the-pages-part)

## Resources

- [FAQ](https://tinytapeout.com/faq/)
- [Digital design lessons](https://tinytapeout.com/digital_design/)
- [Learn how semiconductors work](https://tinytapeout.com/siliwiz/)
- [Join the community](https://tinytapeout.com/discord)
- [Build your design locally](https://www.tinytapeout.com/guides/local-hardening/)

## What next?

- [Submit your design to the next shuttle](https://app.tinytapeout.com/).
- Edit [this README](README.md) and explain your design, how it works, and how to test it.
- Share your project on your social network of choice:
  - LinkedIn [#tinytapeout](https://www.linkedin.com/search/results/content/?keywords=%23tinytapeout) [@TinyTapeout](https://www.linkedin.com/company/100708654/)
  - Mastodon [#tinytapeout](https://chaos.social/tags/tinytapeout) [@matthewvenn](https://chaos.social/@matthewvenn)
  - X (formerly Twitter) [#tinytapeout](https://twitter.com/hashtag/tinytapeout) [@tinytapeout](https://twitter.com/tinytapeout)
  - Bluesky [@tinytapeout.com](https://bsky.app/profile/tinytapeout.com)
