#!/usr/bin/env python

from openmm.app import *
from openmm import *
from openmm.unit import *

pdb_in = "/PATH/TO/INPUT/PDB"
pdb_out = "/PATH/TO/OUTPUT/PDB"

pdb = PDBFile(pdb_in)
forcefield = ForceField('amber14/RNA.Shaw_charmm22-ions.xml', 'amber14/tip4pd_desres.xml')
modeller = Modeller(pdb.topology, pdb.positions)
modeller.addExtraParticles(forcefield)

PDBFile.writeFile(modeller.topology, modeller.positions, 
                  open(pdb_out, 'w'))
