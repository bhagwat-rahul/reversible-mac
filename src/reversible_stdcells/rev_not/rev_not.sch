v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 0 -60 0 60 {lab=A}
N 30 -100 30 100 {lab=Y}
N -30 -100 0 -100 {lab=VDD}
N -30 100 0 100 {lab=VGND}
N 0 -190 0 -100 {lab=VDD}
N -0 100 0 180 {lab=VGND}
N -60 0 -0 0 {lab=A}
N 30 -0 80 0 {lab=Y}
C {iopin.sym} 0 -190 0 0 {name=VDD lab=VDD}
C {iopin.sym} 0 180 0 0 {name=VGND lab=VGND}
C {sky130_fd_pr/pfet_01v8.sym} 0 -80 3 0 {name=MP
W=1
L=0.15
nf=1
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 0 80 1 0 {name=MN
W=1
L=0.15
nf=1 
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {ipin.sym} -60 0 0 0 {name=A lab=A}
C {opin.sym} 80 0 0 0 {name=Y lab=Y}
