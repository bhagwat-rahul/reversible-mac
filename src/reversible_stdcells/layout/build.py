#!/usr/bin/env python3
"""Generate compact SKY130 hard macros from the actual Xschem netlists.

Run in IIC-OSIC-TOOLS after iic-pdk sky130A. Uses installed SKY130 PCells
in facing NMOS/PMOS rows, shared body taps, and routed M2/M3 interconnect.
These are 5.44 um BLOCK macros with double-height met1 supply rails.
"""
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import klayout.db as k
from route import route

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / 'views'
PDK = Path(os.environ['PDK_ROOT']) / 'sky130A'
sys.path.insert(0, str(PDK / 'libs.tech/klayout/python'))
from cells import sky130

LAYERS = {'li1': (67, 20), 'mcon': (67, 44), 'met1': (68, 20),
          'via1': (68, 44), 'met2': (69, 20), 'via2': (69, 44),
          'met3': (70, 20), 'boundary': (235, 4)}


def schematic(name, directory):
    subprocess.run(['xschem', '-n', '-q', '-x', '-b', '--rcfile', str(ROOT/'xschemrc'),
                    '-o', str(directory), str(ROOT/name/(name+'.sch'))], check=True)
    text = (directory/(name+'.spice')).read_text()
    text = re.sub(r'\n\+\s*', ' ', text)
    pins = re.search(r'^\*\*\.subckt \S+ (.+)$', text, re.M).group(1).split()
    devices = []
    aliases = {}
    for line in text.splitlines():
        if line.startswith('X'):
            fields = line.split()
            assert fields[5] in ('sky130_fd_pr__nfet_01v8', 'sky130_fd_pr__pfet_01v8')
            params = dict(re.findall(r'(\w+)=([\d.]+)', line))
            assert float(params['L']) == .15 and float(params['nf']) == 1
            devices.append(dict(name=fields[0], nodes=fields[1:5], model=fields[5],
                                w=float(params['W']), l=float(params['L'])))
        elif line.startswith('VKEEP'):
            _, a, b, value = line.split()
            assert float(value) == 0
            aliases[b] = a
    return pins, devices, aliases, text


class Macro:
    def __init__(self, name):
        self.layout = k.Layout()
        self.layout.dbu = .001
        self.top = self.layout.create_cell(name)

    def box(self, layer, x1, y1, x2, y2):
        index = self.layout.layer(*LAYERS[layer]) if isinstance(layer, str) else self.layout.layer(*layer)
        self.top.shapes(index).insert(k.DBox(x1, y1, x2, y2))

    def pad(self, layer, x, y, width):
        self.box(layer, x-width/2, y-width/2, x+width/2, y+width/2)

    def wire(self, layer, x1, y1, x2, y2, width):
        assert x1 == x2 or y1 == y2
        self.box(layer, min(x1,x2)-width/2, min(y1,y2)-width/2,
                 max(x1,x2)+width/2, max(y1,y2)+width/2)

    def via(self, level, x, y):
        if level == 1:
            self.pad('met1', x, y, .34)
            self.pad('via1', x, y, .15)
            self.pad('met2', x, y, .34)
        else:
            self.pad('met2', x, y, .37)
            self.pad('via2', x, y, .20)
            self.pad('met3', x, y, .40)

    def text(self, layer, text, x, y):
        self.top.shapes(self.layout.layer(*layer)).insert(k.DText(text, k.DTrans(x,y)))


def build(name, lib, directory):
    pins, devices, aliases, netlist = schematic(name, directory)
    rows = [[d for d in devices if kind in d['model']] for kind in ['nfet','pfet']]
    assert len(rows[0]) == len(rows[1])
    columns = len(rows[0])
    ny = 8
    height = 5.44
    macro = Macro(name)
    positions = []
    terminals = {}
    # Followpin-aligned met1 access plus straps onto the body-tap landings at
    # x=0.86 um. Toffoli 2 um NMOS gate metal reaches y=2.90 at x>=1.71, so
    # the VDD followpin landing stays in the tap column.
    power_rails = {
        'VDD': [[0, 2.48, 1.50, 3.22], [.69, 3.22, 1.03, 4.71]],
        'VGND': [[0, 0, None, .24], [.69, 0, 1.03, 1.21]],
    }

    def point(ix, iy):
        return .35+.51*ix, .34+.7*iy

    def terminal(net, ix, iy, layer=0):
        terminals.setdefault(net, set()).add((ix, iy, layer))

    # Shared well and one tap per body domain, rather than one isolated tie
    # per transistor. Keep the original device widths, including 2 um NAND N.
    for pmos, row in enumerate(rows):
        for i, d in enumerate(row):
            x, y = point(3+3*i,0)[0]-.15, 4.9 if pmos else .55
            kind = 'pfet' if pmos else 'nfet'
            pcell = macro.layout.create_cell(kind, 'skywater130', {
                'type': d['model'], 'w': d['w'], 'l': d['l'], 'nf': 1,
                'bulk': 'None', 'gate_con_pos': 'top'})
            trans = k.DTrans(0, bool(pmos), x, y)
            macro.top.insert(k.DCellInstArray(pcell.cell_index(), trans))
            metal = k.Region(pcell.begin_shapes_rec(macro.layout.layer(68,20))).merged()
            boxes = [p.bbox().to_dtype(.001) for p in metal.each()]
            assert len(boxes) == 3
            gate = max(boxes, key=lambda b: b.center().y)
            sd = sorted((b for b in boxes if b != gate), key=lambda b:b.center().x)
            for j, (box, net) in enumerate(zip(sd+[gate],
                                             [d['nodes'][0],d['nodes'][2],d['nodes'][1]])):
                pos = trans*box.center()
                ix = 3+3*i+j
                iy = (5 if pmos else (3 if d['w']==2 else 2)) if j==2 else (6 if pmos else 1)
                px, py = point(ix,iy)
                macro.wire('met1',pos.x,pos.y,px,pos.y,.23)
                macro.wire('met1',px,pos.y,px,py,.34)
                macro.via(1,px,py)
                terminal(net,ix,iy)
            positions.append(dict(**d,x_um=x,y_um=y,mirror_x=bool(pmos)))
        net = 'VDD' if pmos else 'VGND'
        ix, iy = 1, 6 if pmos else 1
        bx, by = point(ix,iy)
        macro.box((65,44),bx-.15,by-.21,bx+.15,by+.21)
        macro.box((93,44) if pmos else (94,20),bx-.275,by-.335,bx+.275,by+.335)
        macro.pad((66,44),bx,by,.17)
        macro.box('li1',bx-.14,by-.17,bx+.14,by+.17)
        macro.pad('mcon',bx,by,.17)
        macro.via(1,bx,by)
        terminal(net,ix,iy)
    pin_tracks = {n:i for i,n in enumerate(dict.fromkeys(aliases.get(p,p) for p in pins))}
    # Try no extra right-hand routing column before spending another site.
    device_terminals = {n:set(p) for n,p in terminals.items()}
    for margin in (0,1):
        nx = 3*columns+3+margin
        width = math.ceil((.51*(nx-1)+.7)/.46)*.46
        terminals = {n:set(p) for n,p in device_terminals.items()}
        geometry = {}
        for p in pins:
            net = aliases.get(p,p)
            is_output = p == 'Y' or p.endswith('_OUT')
            # Separate the two M3 supply pins horizontally so alternating M4
            # PDN straps can contact both nets without a horizontal M3 rail.
            ix = nx-1 if is_output else 4 if p == 'VGND' else 0
            iy = pin_tracks[net]
            x, y = point(ix,iy)
            terminal(net,ix,iy,1)
            box = [x-.3, y-.2, x+.3, y+.2]
            geometry[p] = dict(net=net, layer='met3', rect_um=box,
                               direction='OUTPUT' if is_output else 'INPUT',
                               use='POWER' if p=='VDD' else 'GROUND' if p=='VGND' else 'SIGNAL')
        try:
            routes = route(terminals,nx,ny)
            break
        except RuntimeError:
            if margin == 1:
                raise
    # Match the SKY130 HD followpin pattern: VGND at the lower boundary and
    # VDD overlapping the rail centered at y=2.72 um. These power-pin shapes
    # open matching holes in the conservative met1 obstruction below.
    for net, rails in power_rails.items():
        for rail in rails:
            if rail[2] is None:
                rail[2] = width
            macro.box('met1', *rail)
    macro.box((64,20),.18,3.18,width-.18,5.28)
    for p, info in geometry.items():
        box = info['rect_um']
        macro.box('met3',*box)
        macro.box((70,16),*box)
        macro.text((70,5),p,(box[0]+box[2])/2,(box[1]+box[3])/2)
    for net, edges in routes.items():
        for a,b in sorted(edges):
            ax,ay = point(*a[:2])
            bx,by = point(*b[:2])
            if a[2] != b[2]:
                macro.via(2,ax,ay)
            else:
                macro.wire('met2' if a[2]==0 else 'met3',ax,ay,bx,by,.28 if a[2]==0 else .4)
    macro.box('boundary',0,0,width,height)
    macro.top.flatten(True)
    # Remove unused PCell library roots; deliver exactly one flat top per file.
    for cell in list(macro.layout.top_cells()):
        if cell.cell_index() != macro.top.cell_index():
            macro.layout.delete_cell(cell.cell_index())
    path = OUT/name
    path.mkdir(parents=True,exist_ok=True)
    macro.layout.write(str(path/(name+'.gds')))
    macro.layout.write(str(path/(name+'.oas')))
    metadata = dict(cell=name,width_um=width,height_um=height,pins=geometry,
                    power_rails=power_rails,
                    transistors=positions,physical_aliases=aliases)
    (path/'geometry.json').write_text(json.dumps(metadata,indent=2)+'\n')
    # Keep the independent schematic-derived reference, not a layout-derived one.
    reference = netlist.replace('**.subckt','.subckt').replace('**.ends','.ends')
    reference = re.sub(r'^\.end\s*$', '', reference, flags=re.M)
    (path/(name+'.schematic.spice')).write_text(reference)
    # Keep a conservative full LI blockage. On M1/M2/M3, expose the actual
    # internal metal as OBS; the detailed router applies its spacing rules.
    lef = f'VERSION 5.8 ;\nBUSBITCHARS "[]" ;\nDIVIDERCHAR "/" ;\nMACRO {name}\n  CLASS BLOCK ;\n  ORIGIN 0 0 ;\n  FOREIGN {name} 0 0 ;\n  SIZE {width:.3f} BY {height:.3f} ;\n  SYMMETRY X Y ;\n'
    for pin, info in geometry.items():
        lef += f'  PIN {pin}\n    DIRECTION {info["direction"] if info["use"]=="SIGNAL" else "INOUT"} ;\n    USE {info["use"]} ;\n'
        lef += '    PORT\n      LAYER met3 ;\n'
        lef += '      RECT '+ ' '.join(f'{v:.3f}' for v in info['rect_um'])+' ;\n'
        lef += '    END\n  END '+pin+'\n'
    lef += '  OBS\n'
    for layer in ['li1','met1','met2','met3']:
        boundary = k.Region(k.DBox(0,0,width,height).to_itype(.001))
        if layer in ('met1', 'met2', 'met3'):
            region = k.Region(macro.top.begin_shapes_rec(
                macro.layout.layer(*LAYERS[layer]))).merged() & boundary
        else:
            region = boundary
        if layer == 'met3':
            for info in geometry.values():
                # Leave one minimum-spacing margin around each access pin.  The
                # former 0.3 um opening let unrelated top-level routes enter the
                # macro and violate spacing to hidden internal M3 in the GDS.
                region -= k.Region(k.DBox(*info['rect_um']).enlarged(.06).to_itype(.001))
        lef += f'    LAYER {layer} ;\n'
        for polygon in region.decompose_trapezoids_to_region().each():
            b = polygon.bbox().to_dtype(.001)
            assert k.Region(polygon).area() == k.Region(polygon.bbox()).area()
            lef += f'    RECT {b.left:.3f} {b.bottom:.3f} {b.right:.3f} {b.top:.3f} ;\n'
    lef += f'  END\nEND {name}\nEND LIBRARY\n'
    (path/(name+'.lef')).write_text(lef)
    print(f'{name}: {len(devices)} MOS, {width:.2f} x {height:.2f} um',flush=True)


def functional_liberty():
    # Deliberately no invented capacitances or timing arcs. This is for
    # linking/physical import only; STA must not treat it as characterized.
    functions = {'rev_not': {'Y':'!A'}, 'rev_cnot': {'A_OUT':'A','B_OUT':'A ^ B'},
                 'rev_toffoli': {'A_OUT':'A','B_OUT':'B','C_OUT':'C ^ (A & B)'}}
    text = '''/* FUNCTIONAL/PHYSICAL IMPORT ONLY. NO TIMING OR POWER MODEL.
 * Not usable for timing closure, buffering, sizing, or tapeout signoff. */
library (reversible_functional_only) {
  technology (cmos);
  delay_model : table_lookup;
  time_unit : "1ns";
  voltage_unit : "1V";
  current_unit : "1mA";
  capacitive_load_unit (1,pf);
  nom_voltage : 1.8;
  nom_temperature : 27;
  nom_process : 1;
'''
    for name, funcs in functions.items():
        meta = json.loads((OUT/name/'geometry.json').read_text())
        text += f'  cell ({name}) {{\n    area : {meta["width_um"]*meta["height_um"]:.6f};\n    dont_use : true;\n'
        text += '    pg_pin (VDD) { voltage_name : VDD; pg_type : primary_power; }\n'
        text += '    pg_pin (VGND) { voltage_name : VGND; pg_type : primary_ground; }\n'
        for p, info in meta['pins'].items():
            if info['use'] != 'SIGNAL':
                continue
            text += f'    pin ({p}) {{ direction : {info["direction"].lower()}; related_power_pin : VDD; related_ground_pin : VGND;'
            if p in funcs:
                text += f' function : "{funcs[p]}";'
            text += ' }\n'
        text += '  }\n'
    text += '}\n'
    (OUT/'reversible_cells.functional_only.lib').write_text(text)


if __name__ == '__main__':
    if os.environ.get('PDK') != 'sky130A':
        raise SystemExit('Run iic-pdk sky130A first.')
    library = sky130()
    with tempfile.TemporaryDirectory() as tmp:
        for name in ['rev_not','rev_cnot','rev_toffoli']:
            build(name,library,Path(tmp))
    functional_liberty()
