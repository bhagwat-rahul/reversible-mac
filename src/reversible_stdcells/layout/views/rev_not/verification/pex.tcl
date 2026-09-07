drc off
gds read /foss/designs/current-designs/reversible-mac/src/reversible_stdcells/layout/views/rev_not/rev_not.gds
load rev_not
select top cell
extract path /foss/designs/current-designs/reversible-mac/src/reversible_stdcells/layout/views/rev_not/verification
extract all
ext2spice lvs
ext2spice short voltage
ext2spice cthresh 0
ext2spice -p /foss/designs/current-designs/reversible-mac/src/reversible_stdcells/layout/views/rev_not/verification -o /foss/designs/current-designs/reversible-mac/src/reversible_stdcells/layout/views/rev_not/rev_not.pex.spice
quit -noprompt
