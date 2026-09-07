v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
E {}
T {rev_toffoli: conventional CMOS, logically reversible at the boundary} 0 -230 0 0 0.4 0.4 {}
C {iopin.sym} 0 -140 0 0 {name=VDD lab=VDD}
C {iopin.sym} 150 -140 0 0 {name=VGND lab=VGND}
C {ipin.sym} 300 -140 0 0 {name=A lab=A}
C {ipin.sym} 450 -140 0 0 {name=B lab=B}
C {ipin.sym} 600 -140 0 0 {name=C lab=C}
C {opin.sym} 750 -140 0 0 {name=A_OUT lab=A_OUT}
C {opin.sym} 900 -140 0 0 {name=B_OUT lab=B_OUT}
C {opin.sym} 1050 -140 0 0 {name=C_OUT lab=C_OUT}
T {NAND(A,B): T_BAR} 0 0 0 0 0.3 0.3 {}
T {T = A AND B} 600 0 0 0 0.3 0.3 {}
T {C complement} 900 0 0 0 0.3 0.3 {}
T {Pass C when T=0} 1200 0 0 0 0.3 0.3 {}
T {Pass C_BAR when T=1} 1500 0 0 0.3 0.3 {}
C {sky130_fd_pr/pfet_01v8.sym} 0 100 0 0 {name=MPA W=1 L=0.15 nf=1 mult=1 model=pfet_01v8 spiceprefix=X
ad=0.29 as=0.29 pd=2.58 ps=2.58 nrd=0.29 nrs=0.29 sa=0 sb=0 sd=0}
N 20 40 20 70 {lab=VDD}
C {lab_pin.sym} 20 40 0 0 {name=l20_40 sig_type=std_logic lab=VDD}
N -80 100 -20 100 {lab=A}
C {lab_pin.sym} -80 100 0 0 {name=l-80_100 sig_type=std_logic lab=A}
N 20 130 20 160 {lab=T_BAR}
C {lab_pin.sym} 20 160 0 0 {name=l20_160 sig_type=std_logic lab=T_BAR}
N 20 100 60 100 {lab=VDD}
C {lab_pin.sym} 60 100 0 1 {name=l60_100 lab=VDD}
C {sky130_fd_pr/pfet_01v8.sym} 300 100 0 0 {name=MPB W=1 L=0.15 nf=1 mult=1 model=pfet_01v8 spiceprefix=X
ad=0.29 as=0.29 pd=2.58 ps=2.58 nrd=0.29 nrs=0.29 sa=0 sb=0 sd=0}
N 320 40 320 70 {lab=VDD}
C {lab_pin.sym} 320 40 0 0 {name=l320_40 sig_type=std_logic lab=VDD}
N 220 100 280 100 {lab=B}
C {lab_pin.sym} 220 100 0 0 {name=l220_100 sig_type=std_logic lab=B}
N 320 130 320 160 {lab=T_BAR}
C {lab_pin.sym} 320 160 0 0 {name=l320_160 sig_type=std_logic lab=T_BAR}
N 320 100 360 100 {lab=VDD}
C {lab_pin.sym} 360 100 0 1 {name=l360_100 lab=VDD}
C {sky130_fd_pr/nfet_01v8.sym} 0 260 0 0 {name=MNA W=2 L=0.15 nf=1 mult=1 model=nfet_01v8 spiceprefix=X
ad=0.58 as=0.58 pd=4.58 ps=4.58 nrd=0.145 nrs=0.145 sa=0 sb=0 sd=0}
N 20 200 20 230 {lab=T_BAR}
C {lab_pin.sym} 20 200 0 0 {name=l20_200 sig_type=std_logic lab=T_BAR}
N -80 260 -20 260 {lab=A}
C {lab_pin.sym} -80 260 0 0 {name=l-80_260 sig_type=std_logic lab=A}
N 20 290 20 320 {lab=NAND_MID}
C {lab_pin.sym} 20 320 0 0 {name=l20_320 sig_type=std_logic lab=NAND_MID}
N 20 260 60 260 {lab=VGND}
C {lab_pin.sym} 60 260 0 1 {name=l60_260 lab=VGND}
C {sky130_fd_pr/nfet_01v8.sym} 300 260 0 0 {name=MNB W=2 L=0.15 nf=1 mult=1 model=nfet_01v8 spiceprefix=X
ad=0.58 as=0.58 pd=4.58 ps=4.58 nrd=0.145 nrs=0.145 sa=0 sb=0 sd=0}
N 320 200 320 230 {lab=NAND_MID}
C {lab_pin.sym} 320 200 0 0 {name=l320_200 sig_type=std_logic lab=NAND_MID}
N 220 260 280 260 {lab=B}
C {lab_pin.sym} 220 260 0 0 {name=l220_260 sig_type=std_logic lab=B}
N 320 290 320 320 {lab=VGND}
C {lab_pin.sym} 320 320 0 0 {name=l320_320 sig_type=std_logic lab=VGND}
N 320 260 360 260 {lab=VGND}
C {lab_pin.sym} 360 260 0 1 {name=l360_260 lab=VGND}
C {sky130_fd_pr/pfet_01v8.sym} 600 100 0 0 {name=MTP W=1 L=0.15 nf=1 mult=1 model=pfet_01v8 spiceprefix=X
ad=0.29 as=0.29 pd=2.58 ps=2.58 nrd=0.29 nrs=0.29 sa=0 sb=0 sd=0}
N 620 40 620 70 {lab=VDD}
C {lab_pin.sym} 620 40 0 0 {name=l620_40 sig_type=std_logic lab=VDD}
N 520 100 580 100 {lab=T_BAR}
C {lab_pin.sym} 520 100 0 0 {name=l520_100 sig_type=std_logic lab=T_BAR}
N 620 130 620 160 {lab=T}
C {lab_pin.sym} 620 160 0 0 {name=l620_160 sig_type=std_logic lab=T}
N 620 100 660 100 {lab=VDD}
C {lab_pin.sym} 660 100 0 1 {name=l660_100 lab=VDD}
C {sky130_fd_pr/nfet_01v8.sym} 600 260 0 0 {name=MTN W=1 L=0.15 nf=1 mult=1 model=nfet_01v8 spiceprefix=X
ad=0.29 as=0.29 pd=2.58 ps=2.58 nrd=0.29 nrs=0.29 sa=0 sb=0 sd=0}
N 620 200 620 230 {lab=T}
C {lab_pin.sym} 620 200 0 0 {name=l620_200 sig_type=std_logic lab=T}
N 520 260 580 260 {lab=T_BAR}
C {lab_pin.sym} 520 260 0 0 {name=l520_260 sig_type=std_logic lab=T_BAR}
N 620 290 620 320 {lab=VGND}
C {lab_pin.sym} 620 320 0 0 {name=l620_320 sig_type=std_logic lab=VGND}
N 620 260 660 260 {lab=VGND}
C {lab_pin.sym} 660 260 0 1 {name=l660_260 lab=VGND}
C {sky130_fd_pr/pfet_01v8.sym} 900 100 0 0 {name=MCP W=1 L=0.15 nf=1 mult=1 model=pfet_01v8 spiceprefix=X
ad=0.29 as=0.29 pd=2.58 ps=2.58 nrd=0.29 nrs=0.29 sa=0 sb=0 sd=0}
N 920 40 920 70 {lab=VDD}
C {lab_pin.sym} 920 40 0 0 {name=l920_40 sig_type=std_logic lab=VDD}
N 820 100 880 100 {lab=C}
C {lab_pin.sym} 820 100 0 0 {name=l820_100 sig_type=std_logic lab=C}
N 920 130 920 160 {lab=C_BAR}
C {lab_pin.sym} 920 160 0 0 {name=l920_160 sig_type=std_logic lab=C_BAR}
N 920 100 960 100 {lab=VDD}
C {lab_pin.sym} 960 100 0 1 {name=l960_100 lab=VDD}
C {sky130_fd_pr/nfet_01v8.sym} 900 260 0 0 {name=MCN W=1 L=0.15 nf=1 mult=1 model=nfet_01v8 spiceprefix=X
ad=0.29 as=0.29 pd=2.58 ps=2.58 nrd=0.29 nrs=0.29 sa=0 sb=0 sd=0}
N 920 200 920 230 {lab=C_BAR}
C {lab_pin.sym} 920 200 0 0 {name=l920_200 sig_type=std_logic lab=C_BAR}
N 820 260 880 260 {lab=C}
C {lab_pin.sym} 820 260 0 0 {name=l820_260 sig_type=std_logic lab=C}
N 920 290 920 320 {lab=VGND}
C {lab_pin.sym} 920 320 0 0 {name=l920_320 sig_type=std_logic lab=VGND}
N 920 260 960 260 {lab=VGND}
C {lab_pin.sym} 960 260 0 1 {name=l960_260 lab=VGND}
C {sky130_fd_pr/nfet_01v8.sym} 1200 100 0 0 {name=MT0N W=1 L=0.15 nf=1 mult=1 model=nfet_01v8 spiceprefix=X
ad=0.29 as=0.29 pd=2.58 ps=2.58 nrd=0.29 nrs=0.29 sa=0 sb=0 sd=0}
N 1220 40 1220 70 {lab=C_OUT}
C {lab_pin.sym} 1220 40 0 0 {name=l1220_40 sig_type=std_logic lab=C_OUT}
N 1120 100 1180 100 {lab=T_BAR}
C {lab_pin.sym} 1120 100 0 0 {name=l1120_100 sig_type=std_logic lab=T_BAR}
N 1220 130 1220 160 {lab=C}
C {lab_pin.sym} 1220 160 0 0 {name=l1220_160 sig_type=std_logic lab=C}
N 1220 100 1260 100 {lab=VGND}
C {lab_pin.sym} 1260 100 0 1 {name=l1260_100 lab=VGND}
C {sky130_fd_pr/pfet_01v8.sym} 1200 260 0 0 {name=MT0P W=1 L=0.15 nf=1 mult=1 model=pfet_01v8 spiceprefix=X
ad=0.29 as=0.29 pd=2.58 ps=2.58 nrd=0.29 nrs=0.29 sa=0 sb=0 sd=0}
N 1220 200 1220 230 {lab=C}
C {lab_pin.sym} 1220 200 0 0 {name=l1220_200 sig_type=std_logic lab=C}
N 1120 260 1180 260 {lab=T}
C {lab_pin.sym} 1120 260 0 0 {name=l1120_260 sig_type=std_logic lab=T}
N 1220 290 1220 320 {lab=C_OUT}
C {lab_pin.sym} 1220 320 0 0 {name=l1220_320 sig_type=std_logic lab=C_OUT}
N 1220 260 1260 260 {lab=VDD}
C {lab_pin.sym} 1260 260 0 1 {name=l1260_260 lab=VDD}
C {sky130_fd_pr/nfet_01v8.sym} 1500 100 0 0 {name=MT1N W=1 L=0.15 nf=1 mult=1 model=nfet_01v8 spiceprefix=X
ad=0.29 as=0.29 pd=2.58 ps=2.58 nrd=0.29 nrs=0.29 sa=0 sb=0 sd=0}
N 1520 40 1520 70 {lab=C_OUT}
C {lab_pin.sym} 1520 40 0 0 {name=l1520_40 sig_type=std_logic lab=C_OUT}
N 1420 100 1480 100 {lab=T}
C {lab_pin.sym} 1420 100 0 0 {name=l1420_100 sig_type=std_logic lab=T}
N 1520 130 1520 160 {lab=C_BAR}
C {lab_pin.sym} 1520 160 0 0 {name=l1520_160 sig_type=std_logic lab=C_BAR}
N 1520 100 1560 100 {lab=VGND}
C {lab_pin.sym} 1560 100 0 1 {name=l1560_100 lab=VGND}
C {sky130_fd_pr/pfet_01v8.sym} 1500 260 0 0 {name=MT1P W=1 L=0.15 nf=1 mult=1 model=pfet_01v8 spiceprefix=X
ad=0.29 as=0.29 pd=2.58 ps=2.58 nrd=0.29 nrs=0.29 sa=0 sb=0 sd=0}
N 1520 200 1520 230 {lab=C_BAR}
C {lab_pin.sym} 1520 200 0 0 {name=l1520_200 sig_type=std_logic lab=C_BAR}
N 1420 260 1480 260 {lab=T_BAR}
C {lab_pin.sym} 1420 260 0 0 {name=l1420_260 sig_type=std_logic lab=T_BAR}
N 1520 290 1520 320 {lab=C_OUT}
C {lab_pin.sym} 1520 320 0 0 {name=l1520_320 sig_type=std_logic lab=C_OUT}
N 1520 260 1560 260 {lab=VDD}
C {lab_pin.sym} 1560 260 0 1 {name=l1560_260 lab=VDD}
T {Preserved outputs: 0 V sources model ideal wires (no buffering or parasitics).} 0 420 0 0 0.3 0.3 {}
C {vsource.sym} 0 510 0 0 {name=VKEEPA value=0}
C {lab_pin.sym} 0 480 0 0 {name=l0_480 sig_type=std_logic lab=A}
C {lab_pin.sym} 0 540 0 0 {name=l0_540 sig_type=std_logic lab=A_OUT}
C {vsource.sym} 300 510 0 0 {name=VKEEPB value=0}
C {lab_pin.sym} 300 480 0 0 {name=l300_480 sig_type=std_logic lab=B}
C {lab_pin.sym} 300 540 0 0 {name=l300_540 sig_type=std_logic lab=B_OUT}
