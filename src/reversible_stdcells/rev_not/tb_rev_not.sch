v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
E {}
T {rev_not: exhaustive truth table and isolated timing transitions
100 ps input ramps; 10 fF per output; nominal TT / 1.8 V / 27 C
Run ../characterize.py for 15 process / voltage / temperature combinations.} 0 -260 0 0 0.35 0.35 {}
C {rev_not.sym} 0 0 0 0 {name=XDUT}
C {lab_pin.sym} -40 -120 0 0 {name=l-40_-120 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 40 -120 0 0 {name=l40_-120 sig_type=std_logic lab=VGND}
C {lab_pin.sym} -120 -60 0 0 {name=l-120_-60 sig_type=std_logic lab=A}
C {lab_pin.sym} 120 -60 0 1 {name=l120_-60 lab=Y}
C {vsource.sym} -300 380 0 0 {name=VVDD value="'VDDVAL'"}
C {lab_pin.sym} -300 350 0 0 {name=l-300_350 sig_type=std_logic lab=VDD}
C {lab_pin.sym} -300 410 0 0 {name=l-300_410 sig_type=std_logic lab=0}
C {vsource.sym} -100 380 0 0 {name=VVGND value="0"}
C {lab_pin.sym} -100 350 0 0 {name=l-100_350 sig_type=std_logic lab=VGND}
C {lab_pin.sym} -100 410 0 0 {name=l-100_410 sig_type=std_logic lab=0}
C {vsource.sym} 150 380 0 0 {name=VINA value="PWL / 100 ps" format="@name @pinlist @stimulus" stimulus="PWL(
+ 0n 'VDDVAL*0'
+ 10n 'VDDVAL*0'
+ 10.1n 'VDDVAL*1'
+ 20n 'VDDVAL*1'
+ 20.1n 'VDDVAL*1'
+ 30n 'VDDVAL*1'
+ 30.1n 'VDDVAL*0')"}
C {lab_pin.sym} 150 350 0 0 {name=l150_350 sig_type=std_logic lab=A}
C {lab_pin.sym} 150 410 0 0 {name=l150_410 sig_type=std_logic lab=0}
C {capa.sym} 0 550 0 0 {name=CLOADY value=10f}
C {lab_pin.sym} 0 520 0 0 {name=l0_520 sig_type=std_logic lab=Y}
C {lab_pin.sym} 0 580 0 0 {name=l0_580 sig_type=std_logic lab=0}
C {code_shown.sym} 350 -120 0 0 {name=SIM only_toplevel=false value=".param VDDVAL=1.8
.temp 27
.control
set wr_singlescale
set wr_vecnames
tran 5p 40n
wrdata wave.txt v(A) v(Y)
.endc"}
C {code_shown.sym} -300 700 0 0 {name=MODELS only_toplevel=false value="tcleval(.lib $::env(PDK_ROOT)/sky130A/libs.tech/ngspice/sky130.lib.spice tt)"}
