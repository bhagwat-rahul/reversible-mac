#!/usr/bin/env python3
"""Check Boolean models, blackbox synthesis, and LEF placement/signal routing."""
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent


def run(command, log):
    result = subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    log.write_text(result.stdout+result.stderr)
    if result.returncode or '[ERROR' in log.read_text():
        raise RuntimeError(f'Command failed: {command}; see {log}')


if __name__ == '__main__':
    assert os.environ.get('PDK') == 'sky130A', 'Run iic-pdk sky130A first'
    out = ROOT/'integration'
    out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for power in [False,True]:
            flags = ['-DUSE_POWER_PINS'] if power else []
            exe = str(Path(tmp)/'sim')
            run(['iverilog','-g2012','-DTESTBENCH',*flags,'-s','testbench','-o',exe,
                 'reversible_cells.sim.v','smoke.v'],out/f'compile_{power}.log')
            run(['vvp',exe],out/f'simulation_{power}.log')
            assert 'PASS:' in (out/f'simulation_{power}.log').read_text()
            define = '-D USE_POWER_PINS' if power else ''
            tag = 'powered' if power else 'smoke'
            script = f'''read_verilog -lib {define} reversible_cells.blackbox.v
read_verilog {define} smoke.v
synth -top reversible_cells_smoke
select -assert-count 1 t:rev_not
select -assert-count 1 t:rev_cnot
select -assert-count 1 t:rev_toffoli
select *
write_json integration/{tag}_netlist.json
write_verilog -noattr -noexpr integration/{tag}_netlist.v
'''
            run(['yosys','-p',script],out/f'yosys_{power}.log')
            module = json.loads((out/f'{tag}_netlist.json').read_text())['modules']['reversible_cells_smoke']
            assert sorted(c['type'] for c in module['cells'].values()) == ['rev_cnot','rev_not','rev_toffoli']
            for cell in module['cells'].values():
                assert ('VDD' in cell['connections']) == power
                assert ('VGND' in cell['connections']) == power
    run(['openroad','-exit','smoke.tcl'],out/'openroad.log')
    assert 'PASS:' in (out/'openroad.log').read_text()
    print('PASS: powered/unpowered simulation and blackbox synthesis; OpenROAD placement/signal routing')
