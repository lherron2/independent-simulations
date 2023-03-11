#!/usr/bin/env python

from pdbfixer import PDBFixer
from openmm.app import PDBFile

def repair_pdb(pdb_in, pdb_out):
    fixer = PDBFixer(filename=pdb_in)
    fixer.findMissingResidues()
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.removeHeterogens(True)
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(7)
    PDBFile.writeFile(fixer.topology, fixer.positions, open(pdb_out, 'w'))
    
pdbid = "1anr"
# paths to pdb files -- change as needed
pdb_in = f'/Users/lukasherron/research/RNAfold/{pdbid}/rosetta/{pdbid}_struct{i}.pdb'
pdb_out = f'/Users/lukasherron/research/RNAfold/{pdbid}/rosetta/fixed/{pdbid}_struct{i}.pdb'
repair_pdb(pdb_in, pdb_out)
