drc off
gds read /foss/designs/current-designs/reversible-mac/src/reversible_stdcells/layout/views/rev_toffoli/rev_toffoli.gds
load rev_toffoli
select top cell
extract path /foss/designs/current-designs/reversible-mac/src/reversible_stdcells/layout/views/rev_toffoli/verification
extract no capacitance
extract no coupling
extract no resistance
extract all
ext2spice lvs
ext2spice short voltage
ext2spice cthresh infinite
ext2spice -p /foss/designs/current-designs/reversible-mac/src/reversible_stdcells/layout/views/rev_toffoli/verification -o /foss/designs/current-designs/reversible-mac/src/reversible_stdcells/layout/views/rev_toffoli/rev_toffoli.lvs.spice
quit -noprompt
