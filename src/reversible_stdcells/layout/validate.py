#!/usr/bin/env python3
"""Macro-level Magic + KLayout DRC, and Magic extraction + Netgen LVS."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

import klayout.db as k

ROOT = Path(__file__).resolve().parent
PDK = Path(os.environ['PDK_ROOT'])/'sky130A'


def run(args, cwd, log):
    result = subprocess.run(args,cwd=cwd,capture_output=True,text=True)
    log.write_text(result.stdout+result.stderr)
    if result.returncode:
        raise RuntimeError(f'{args[0]} failed ({result.returncode}); see {log}')


def main():
    assert os.environ.get('PDK') == 'sky130A', 'Run iic-pdk sky130A first'
    results = []
    for name in ['rev_not','rev_cnot','rev_toffoli']:
        view = ROOT/'views'/name
        metadata = json.loads((view/'geometry.json').read_text())
        report = view/'verification'
        report.mkdir(exist_ok=True)
        # The installed macro deck checks FEOL, BEOL, grid, pin and zero-area
        # rules, not full-chip metal density or antenna closure.
        run(['iic-drc.sh','-b','-l','macro','-w',str(report),str(view/(name+'.gds'))],
            report,report/'drc.log')
        # Keep aliased logical ports. This generates zero-volt short models
        # directly from the connected GDS labels, matching the Xschem VKEEPs.
        for caps in [False,True]:
            suffix = 'pex' if caps else 'lvs'
            output = view/(name+'.'+suffix+'.spice')
            script = f'''drc off
gds read {view/(name+'.gds')}
load {name}
select top cell
extract path {report}
extract {'all' if caps else 'no capacitance'}
'''
            if not caps:
                script += 'extract no coupling\nextract no resistance\nextract all\n'
            script += f'''ext2spice lvs
ext2spice short voltage
ext2spice cthresh {'0' if caps else 'infinite'}
ext2spice -p {report} -o {output}
quit -noprompt
'''
            tcl = report/(suffix+'.tcl')
            tcl.write_text(script)
            run(['magic','-dnull','-noconsole','-rcfile',str(PDK/'libs.tech/magic/sky130A.magicrc'),
                 str(tcl)],report,report/(suffix+'.extract.log'))
            if not output.exists() or '.subckt '+name not in output.read_text():
                raise AssertionError('Missing extracted subcircuit')
            # A physical short has no polarity or preferred node name. Magic
            # can put all device terminals on A_OUT, whereas Xschem puts them
            # on A. Canonicalize ONLY independently extracted zero-V aliases,
            # retaining every named external pin and the short device itself.
            raw = output.read_text()
            (report/(suffix+'.raw.spice')).write_text(raw)
            shorts = {}
            for line in raw.splitlines():
                if line.startswith('V'):
                    fields = line.split()
                    assert len(fields)==4 and float(fields[3])==0
                    a,b = sorted(fields[1:3])
                    shorts[b] = a
            assert shorts == metadata['physical_aliases'], 'Unexpected or missing physical pin short'
            lines = []
            for line in raw.splitlines():
                if line.startswith('V'):
                    fields = line.split()
                    a,b = sorted(fields[1:3])
                    line = f'{fields[0]} {a} {b} 0'
                elif line and not line.startswith(('.', '*')):
                    line = re.sub(r'[^\s]+',lambda m:shorts.get(m[0],m[0]),line)
                lines.append(line)
            output.write_text('\n'.join(lines)+'\n')
        run(['netgen','-batch','lvs',f'{view/(name+".schematic.spice")} {name}',
             f'{view/(name+".lvs.spice")} {name}',str(PDK/'libs.tech/netgen/sky130A_setup.tcl'),
             str(report/'lvs.out')],report,report/'netgen.log')
        lvs = (report/'lvs.out').read_text()
        if 'Circuits match uniquely.' not in lvs or 'failed' in lvs.lower():
            raise AssertionError(f'LVS did not pass: {report/"lvs.out"}')
        # Re-read the actual delivered streams, checking geometry and labels.
        layouts = []
        boundary = k.Region(k.DBox(0,0,metadata['width_um'],metadata['height_um']).to_itype(.001))
        for suffix in ['gds','oas']:
            layout = k.Layout()
            layout.read(str(view/(name+'.'+suffix)))
            assert [c.name for c in layout.top_cells()] == [name]
            for idx in layout.layer_indexes():
                iterator = layout.top_cell().begin_shapes_rec(idx)
                # Text objects are labels, not physical polygons. Region can
                # retain text placeholders even though their bbox is empty.
                iterator.shape_flags = k.Shapes.SBoxes | k.Shapes.SPolygons | k.Shapes.SPaths
                shapes = k.Region(iterator)
                assert (shapes-boundary).is_empty(), f'{suffix}: geometry outside LEF boundary'
            layouts.append(layout)
        a,b = layouts
        for idx in a.layer_indexes():
            info = a.get_info(idx)
            ra = k.Region(a.top_cell().begin_shapes_rec(idx))
            rb = k.Region(b.top_cell().begin_shapes_rec(b.layer(info)))
            assert (ra ^ rb).is_empty(), f'GDS/OAS mismatch: {info}'
        labels = {s.text.string for s in a.top_cell().shapes(a.layer(70,5)).each() if s.is_text()}
        assert labels == set(metadata['pins'])
        conductor = k.Region(a.top_cell().begin_shapes_rec(a.layer(70,20)))
        for pin in metadata['pins'].values():
            r = k.Region(k.DBox(*pin['rect_um']).to_itype(a.dbu))
            assert (r-conductor).is_empty(), 'LEF pin not covered by metal'
        results.append(dict(cell=name,magic_drc='PASS',klayout_macro_drc='PASS',lvs='PASS',
                            gds_oas_geometry='IDENTICAL',
                            gds_sha256=hashlib.sha256((view/(name+'.gds')).read_bytes()).hexdigest()))
        print(name, 'DRC + LVS + view consistency PASS',flush=True)
    (ROOT/'verification.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__ == '__main__':
    main()
