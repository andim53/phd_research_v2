from scripts.build_mgo_stack import build_mgo_stack
from scripts.build_fe_stack import build_fe_stack
from scripts.build_heteroStruct import build_heteroStruct

from ase.build import surface, bulk
from ase.io import read, write

supercell = (5, 5, 1)
a_mgo = 4.212            
vacuum = 20           

mgo_layer_number = 1
fe_layer_number = 1

path_xsf = f"."


bulk_mgo = bulk('MgO', 'rocksalt', a=a_mgo, cubic=True)
slab_mgo = surface(bulk_mgo, (0, 0, 1), layers=1, vacuum=vacuum)
slab_fe_base = surface('Fe', (0, 0, 1), layers=1, vacuum=vacuum)

slab_mgofe = build_mgo_stack(slab_fe_base, num_layers=mgo_layer_number, vacuum=vacuum, output_path=f"{path_xsf}/slab_mgofe.xsf")
slab_mgo = slab_mgofe[[atom.symbol != 'Fe' for atom in slab_mgofe]].repeat(supercell)
slab_fe = build_fe_stack(slab_fe_base, num_layers=fe_layer_number, vacuum=vacuum, output_path=f"{path_xsf}/slab_fe.xsf").repeat(supercell)

slab_substrate = slab_mgo.copy()
slab_deposition = slab_fe.copy()
slab_heteroStruct, slab_substrate, slab_deposition, substrate_layer_heights, deposition_layer_heights = build_heteroStruct(slab_substrate, slab_deposition, output_path=f'{path_xsf}/heteroStruct.xsf')

write(f'{path_xsf}/hetero.xsf',slab_heteroStruct)