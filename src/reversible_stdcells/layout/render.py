"""Run with klayout -e -b -r render.py after iic-pdk sky130A."""
import os
from pathlib import Path
import pya

root = Path(__file__).resolve().parent
for name in ['rev_not','rev_cnot','rev_toffoli']:
    view = pya.LayoutView()
    view.load_layout(str(root/'views'/name/(name+'.oas')),False)
    view.load_layer_props(os.environ['PDK_ROOT']+'/sky130A/libs.tech/klayout/tech/sky130A.lyp')
    # Presentation only: keep the delivered OAS untouched and hide the
    # filled boundary hatch so the device geometry remains readable.
    layout = view.active_cellview().layout()
    top = layout.top_cell()
    iterator = view.begin_layers()
    while not iterator.at_end():
        props = iterator.current()
        if props.source_layer == 235:
            props.visible = False
            view.set_layer_properties(iterator,props)
        if props.source_layer == 70 and props.source_datatype == 5:
            props.fill_color = 0xffffff
            props.frame_color = 0xffffff
            view.set_layer_properties(iterator,props)
        iterator.next()
    view.max_hier()
    view.zoom_box(top.dbbox().enlarged(.8))
    view.save_image(str(root/'views'/name/(name+'.png')),1800,900)
    view.destroy()
