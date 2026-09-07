#!/usr/bin/env python3
"""Netlist the three Xschem testbenches, check logic and measure timing.

Run inside IIC-OSIC-TOOLS after `iic-pdk sky130A`. Requires numpy.
No schematic or stimulus is synthesized here: simulations use Xschem netlists.
"""
import argparse
import csv
import itertools
import os
from pathlib import Path
import re
import subprocess
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parent


def logic(gate, bits):
    if gate == 'not':
        return (1 - bits[0],)
    if gate == 'cnot':
        a, b = bits
        return (a, a ^ b)
    a, b, c = bits
    return (a, b, c ^ (a & b))


def crossing(t, v, level, rising):
    indices = np.flatnonzero((v[:-1] < level) & (v[1:] >= level) if rising
                             else (v[:-1] > level) & (v[1:] <= level))
    if len(indices) != 1:
        raise AssertionError(f'Expected one crossing of {level}, found {len(indices)}')
    i = indices[0]
    return t[i] + (level - v[i]) * (t[i+1] - t[i]) / (v[i+1] - v[i])


def run(command, cwd):
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    output = result.stdout + result.stderr
    if result.returncode or re.search(r'\b(error|fatal)\b|IS MISSING|blabla', output, re.I):
        raise RuntimeError(f'{command}\n{output}')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extracted-dir', type=Path,
                        help='Use <dir>/<cell>/<cell>.pex.spice instead of schematic devices')
    parser.add_argument('--output-dir', type=Path, default=ROOT)
    args = parser.parse_args()
    if args.extracted_dir and args.output_dir.resolve() == ROOT:
        parser.error('Set --output-dir to preserve the schematic characterization results')
    if os.environ.get('PDK') != 'sky130A':
        raise SystemExit('First run iic-pdk sky130A in this shell.')
    rc = Path(os.environ['PDK_ROOT']) / 'sky130A/libs.tech/xschem/xschemrc'
    timing, summary = [], []
    for gate, n in [('not', 1), ('cnot', 2), ('toffoli', 3)]:
        name = 'rev_' + gate
        inputs = list('ABC'[:n])
        outputs = ['Y'] if n == 1 else [p + '_OUT' for p in inputs]
        states = list(itertools.product([0, 1], repeat=n))
        cases = [(s, tuple(b ^ (j == i) for j, b in enumerate(s)))
                 for s in states for i in range(n)]
        with tempfile.TemporaryDirectory(prefix=name+'-') as directory:
            work = Path(directory)
            run(['xschem', '-n', '-q', '-x', '-b', '--rcfile', str(rc),
                 '-o', directory, 'tb_'+name+'.sch'], ROOT/name)
            netlist = (work/('tb_'+name+'.spice')).read_text()
            if any(s in netlist for s in ['IS MISSING', 'blabla', '$::env']):
                raise AssertionError('Unresolved symbol or model path in Xschem netlist')
            if args.extracted_dir:
                extracted = (args.extracted_dir/name/(name+'.pex.spice')).read_text()
                pattern = rf'^\.subckt {name}\b.*?^\.ends[^\n]*'
                original = re.search(pattern, netlist, re.M | re.S)
                replacement = re.search(pattern, extracted, re.M | re.S)
                if not original or not replacement:
                    raise AssertionError('Missing schematic or extracted subcircuit')
                old_pins = original[0].splitlines()[0].split()[2:]
                new_pins = replacement[0].splitlines()[0].split()[2:]
                if set(old_pins) != set(new_pins):
                    raise AssertionError('Extracted pin interface differs from schematic')
                netlist = netlist[:original.start()]+replacement[0]+netlist[original.end():]
                # These benches label each DUT net with its matching pin name.
                netlist = re.sub(rf'^XDUT .* {name}$',
                                 'XDUT '+' '.join(new_pins)+' '+name, netlist, flags=re.M)
            for corner, (voltage, temp) in itertools.product(
                    ['tt', 'ss', 'ff', 'sf', 'fs'], [(1.8, 27), (1.62, 125), (1.98, -40)]):
                spice = netlist.replace('.param VDDVAL=1.8', f'.param VDDVAL={voltage}')
                spice = spice.replace('.temp 27', f'.temp {temp}')
                spice, count = re.subn(r'(\.lib .*sky130\.lib\.spice) tt', rf'\1 {corner}', spice)
                if count != 1:
                    raise AssertionError('Expected exactly one SKY130 corner statement')
                # quit avoids ngspice batch's "no .plot/.print" exit after .control.
                spice = spice.replace('.endc', 'quit\n.endc')
                (work/'run.spice').write_text(spice)
                wave = work/'wave.txt'
                wave.unlink(missing_ok=True)
                run(['ngspice', '-b', 'run.spice'], work)
                data = np.loadtxt(wave, skiprows=1)
                if data.shape[1] != 1+n+len(outputs) or not np.isfinite(data).all():
                    raise AssertionError('Invalid waveform data')
                t = data[:, 0]
                if t[-1] < len(cases)*20e-9 - 1e-12:
                    raise AssertionError('Transient did not complete')
                rows = []
                for k, (before, after) in enumerate(cases):
                    for when, state in [(k*20+5, before), (k*20+15, after)]:
                        actual = [np.interp(when*1e-9, t, data[:, j+1])/voltage
                                  for j in range(n+len(outputs))]
                        expected = state + logic(gate, state)
                        for value, bit in zip(actual, expected):
                            if not (-.1 <= value <= .1 if bit == 0 else .9 <= value <= 1.1):
                                raise AssertionError(f'{name} {corner} {voltage}V {temp}C '
                                                     f'case {before}->{after}: {actual} != {expected}')
                    changed = next(i for i in range(n) if before[i] != after[i])
                    window = (t >= (k*20+9.9)*1e-9) & (t <= (k*20+19)*1e-9)
                    wt, wd = t[window], data[window]
                    trigger = crossing(wt, wd[:, 1+changed], voltage/2, bool(after[changed]))
                    for j, (old, new) in enumerate(zip(logic(gate, before), logic(gate, after))):
                        if old == new:
                            continue
                        v = wd[:, 1+n+j]
                        arrival = crossing(wt, v, voltage/2, bool(new))
                        lo = crossing(wt, v, voltage*.2, bool(new))
                        hi = crossing(wt, v, voltage*.8, bool(new))
                        row = dict(cell=name, corner=corner, vdd_V=voltage, temp_C=temp,
                                   input=inputs[changed], output=outputs[j],
                                   before=''.join(map(str, before)), after=''.join(map(str, after)),
                                   output_edge='rise' if new else 'fall',
                                   delay_ps=round((arrival-trigger)*1e12, 4),
                                   slew_20_80_ps=round(abs(hi-lo)*1e12, 4),
                                   ideal_wire=(n > 1 and j < n-1))
                        rows.append(row)
                timing.extend(rows)
                active = [r for r in rows if not r['ideal_wire']]
                summary.append(dict(cell=name, corner=corner, vdd_V=voltage, temp_C=temp,
                                    truth_rows=len(states), directed_transitions=len(cases),
                                    status='PASS', max_delay_ps=max(r['delay_ps'] for r in active),
                                    max_slew_20_80_ps=max(r['slew_20_80_ps'] for r in active)))
                print(summary[-1], flush=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, rows in [('timing.csv', timing), ('summary.csv', summary)]:
        with (args.output_dir/filename).open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    print(f'PASS: all 45 simulations; results in {args.output_dir}')


if __name__ == '__main__':
    main()
