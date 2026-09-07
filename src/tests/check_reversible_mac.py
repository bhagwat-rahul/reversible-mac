#!/usr/bin/env python3
"""Run in IIC-OSIC-TOOLS after iic-pdk sky130A. No generated files retained."""
from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CELLS = ROOT/'reversible_stdcells/layout'


def run(args, directory):
    result = subprocess.run(args, cwd=directory, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stdout+result.stderr)
    return result.stdout


def main():
    assert os.environ.get('PDK') == 'sky130A', 'Run iic-pdk sky130A first'
    with tempfile.TemporaryDirectory() as temp:
        temp = Path(temp)
        for powered in (False, True):
            flags = ['-DUSE_POWER_PINS'] if powered else []
            run(['iverilog','-g2012',*flags,'-s','reversible_mac_tb','-o','sim',
                 str(CELLS/'reversible_cells.sim.v'),str(ROOT/'reversible_mac.v'),
                 str(ROOT/'tests/reversible_mac_tb.sv')],temp)
            print(f'USE_POWER_PINS={powered}\n'+run(['vvp','sim'],temp),flush=True)
            for w,s in [(1,2),(4,8),(4,12),(8,32)]:
                define = '-D USE_POWER_PINS' if powered else ''
                script = f'''
read_verilog -lib {define} {CELLS}/reversible_cells.blackbox.v
read_verilog -sv {define} {ROOT}/reversible_mac.v
chparam -set INPUT_WIDTH {w} -set ACC_WIDTH {s} reversible_mac
synth -top reversible_mac -flatten
check -assert
rename -top reversible_mac
write_json netlist.json
'''
                run(['yosys','-p',script],temp)
                cells = json.loads((temp/'netlist.json').read_text())['modules']['reversible_mac']['cells']
                # Newer Yosys retains $scopeinfo metadata after flattening;
                # it is not an electrical cell.
                counts = Counter(c['type'] for c in cells.values() if c['type'] != '$scopeinfo')
                ripple_bits = sum(s-row-1 for row in range(w))
                assert counts['rev_toffoli'] == 2*w*w+2*ripple_bits, counts
                assert counts['rev_cnot'] == 2*s+2*w+4*ripple_bits, counts
                assert all(n in ('rev_cnot','rev_toffoli') or n.startswith('$_SDFFE_')
                           for n in counts), counts
                assert sum(v for n,v in counts.items() if n.startswith('$_SDFFE_')) == s
                for cell in cells.values():
                    if cell['type'].startswith('rev_'):
                        assert ('VDD' in cell['connections']) == powered
                        assert ('VGND' in cell['connections']) == powered
                area = sum(counts[n]*json.loads((CELLS/f'views/{n}/geometry.json').read_text())['width_um']*
                           json.loads((CELLS/f'views/{n}/geometry.json').read_text())['height_um']
                           for n in ('rev_cnot','rev_toffoli'))
                print(f'PASS synthesis W={w} S={s}: {dict(counts)}; macro area {area:.2f} um^2',flush=True)


if __name__ == '__main__':
    main()
