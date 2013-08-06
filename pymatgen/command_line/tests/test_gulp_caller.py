'''
Created on Jan 22, 2013

@author: wenhao
'''
import unittest

from nose.exc import SkipTest

from pymatgen.command_line.gulp_caller import *
from pymatgen.core.structure import Lattice, Structure
from pymatgen.core.periodic_table import Element
from pymatgen.util.io_utils import which
from pymatgen.io.vaspio.vasp_input import Poscar
import os
import sys

test_dir = os.path.join(os.path.dirname(__file__))
gulp_present = which('gulp')

class GulpCallerInitTest(unittest.TestCase):
    def test_default_init(self):
        gulp_caller = GulpCaller()

    def test_explicit_path(self):
        gulp_caller = GulpCaller(gulp_present)

class GulpCallerTest(unittest.TestCase):
    def setUp(self):
        mgo_latt = [[4.212, 0, 0], [0, 4.212, 0], [0, 0, 4.212]]
        mgo_specie = ["Mg"]*4 + ["O"]*4
        mgo_frac_cord = [[0,0,0], [0.5,0.5,0], [0.5,0,0.5], [0,0.5,0.5],
                         [0.5,0,0], [0,0.5,0], [0,0,0.5], [0.5,0.5,0.5]]
        mgo_uc = Structure(mgo_latt, mgo_specie, mgo_frac_cord, True, True)
        self.gio = GulpIO()
        gin = self.gio.keyword_line('optimise', 'conp')
        gin += self.gio.structure_lines(mgo_uc, symm_flg=False)
        #gin += self.gc.gulp_lib('catlow.lib')
        gin += "species\nMg    core  2.00000\nO core  0.86902\nO shel -2.86902\n"
        gin += "buck\n"
        gin += "Mg core O shel   946.627 0.31813  0.00000 0.0 10.0\n"
        gin += "O  shel O shel 22764.000 0.14900 27.87900 0.0 12.0\n"
        self.gin = gin
        self.gc = GulpCaller()

    def test_run(self):
        """Some inherent checks are in the run_gulp function itself.
        They should be suffcient for raising errors."""
        gout = self.gc.run(self.gin)



class GulpIOTest(unittest.TestCase):
    def setUp(self):
        p = Poscar.from_file(os.path.join(test_dir, 'POSCAR'))
        self.structure = p.structure
        self.gio = GulpIO()

    def test_keyword_line_with_correct_keywords(self):
        kw = ('defect', 'property')
        inp_str = self.gio.keyword_line(*kw)
        for word in kw:
            self.assertIn(word, inp_str)

    def test_keyword_line_with_wrong_keywords(self):
        kw = ('defect', 'field')
        with self.assertRaises(GulpError):
            inp_str = self.gio.keyword_line(*kw)

    def test_structure_lines_default_options(self):
        inp_str = self.gio.structure_lines(self.structure)
        self.assertIn('cell', inp_str)
        self.assertIn('frac', inp_str)
        self.assertIn('space', inp_str)

    def test_structure_lines_no_unitcell(self):
        inp_str = self.gio.structure_lines(self.structure, cell_flg=False)
        self.assertNotIn('cell', inp_str)

    def test_structure_lines_no_frac_coords(self):
        inp_str = self.gio.structure_lines(
                self.structure, cell_flg=False, frac_flg=False
                )
        self.assertNotIn('cell', inp_str)
        self.assertIn('cart', inp_str)

    @unittest.skip("Not Implemented yet")
    def test_specie_potential(self):
        pass

    @unittest.expectedFailure
    def test_library_line_explicit_path(self):
        gin = self.gio.library_line(
                '/Users/mbkumar/Research/Defects/GulpExe/Libraries/catlow.lib'
                )
        self.assertIn('lib', gin)

    @unittest.expectedFailure
    def test_library_line_default_path(self):
        gin = self.gio.library_line('catlow.lib')
        self.assertIn('lib', gin)

    def test_library_line_wrong_file(self):
        with self.assertRaises(GulpError):
            gin = self.gio.library_line('temp_to_fail.lib')

    def test_buckingham_potential(self):
        mgo_latt = [[4.212, 0, 0], [0, 4.212, 0], [0, 0, 4.212]]
        mgo_specie = ["Mg",'O']*4 
        mgo_frac_cord = [[0,0,0], [0.5,0,0], [0.5,0.5,0], [0,0.5,0],
                         [0.5,0,0.5], [0,0,0.5], [0,0.5,0.5], [0.5,0.5,0.5]]
        mgo_uc = Structure(mgo_latt, mgo_specie, mgo_frac_cord, True, True)
        gin = self.gio.buckingham_potential(mgo_uc)
        self.assertIn('specie', gin)
        self.assertIn('buck', gin)
        self.assertIn('spring', gin)
        self.assertIn('Mg core', gin)
        self.assertIn('O  core', gin)
        self.assertIn('O  shel', gin)

        gin = self.gio.buckingham_potential(self.structure)
        self.assertIn('specie', gin)
        self.assertIn('buck', gin)
        self.assertIn('spring', gin)

    def test_buckingham_input(self):
        mgo_latt = [[4.212, 0, 0], [0, 4.212, 0], [0, 0, 4.212]]
        mgo_specie = ["Mg",'O']*4 
        mgo_frac_cord = [[0,0,0], [0.5,0,0], [0.5,0.5,0], [0,0.5,0],
                         [0.5,0,0.5], [0,0,0.5], [0,0.5,0.5], [0.5,0.5,0.5]]
        mgo_uc = Structure(mgo_latt, mgo_specie, mgo_frac_cord, True, True)
        gin = self.gio.buckingham_input(mgo_uc, keywords=('optimise', 'conp'))
        self.assertIn('optimise', gin)
        self.assertIn('cell', gin)
        self.assertIn('specie', gin)
        self.assertIn('buck', gin)
        self.assertIn('spring', gin)
        self.assertIn('Mg core', gin)
        self.assertIn('O  core', gin)
        self.assertIn('O  shel', gin)

    # Improve the test 
    def test_tersoff_potential(self):
        mgo_latt = [[4.212, 0, 0], [0, 4.212, 0], [0, 0, 4.212]]
        mgo_specie = ["Mg",'O']*4 
        mgo_frac_cord = [[0,0,0], [0.5,0,0], [0.5,0.5,0], [0,0.5,0],
                         [0.5,0,0.5], [0,0,0.5], [0,0.5,0.5], [0.5,0.5,0.5]]
        mgo_uc = Structure(mgo_latt, mgo_specie, mgo_frac_cord, True, True)
        gin = self.gio.tersoff_potential(mgo_uc)
        self.assertIn('specie', gin)
        self.assertIn('Mg core', gin)

    def test_get_energy(self):
        #Output string obtained from running GULP on a terminal
        out_str = """  Components of energy : 
--------------------------------------------------------------------------------
  Interatomic potentials     =           5.61135426 eV
  Monopole - monopole (real) =          -4.34238722 eV
  Monopole - monopole (recip)=         -43.45344934 eV
  Monopole - monopole (total)=         -47.79583656 eV
--------------------------------------------------------------------------------
  Total lattice energy : 
    Primitive unit cell      =         -42.18448230 eV
    Non-primitive unit cell  =        -168.73792920 eV
--------------------------------------------------------------------------------
  Total lattice energy (in kJmol-1): 
    Primitive unit cell      =           -4070.1577 kJ/(mole unit cells)
    Non-primitive unit cell  =          -16280.6308 kJ/(mole unit cells)
--------------------------------------------------------------------------------
  Components of energy : 

--------------------------------------------------------------------------------
  Interatomic potentials     =           6.79846039 eV
  Monopole - monopole (real) =          -4.45761741 eV
  Monopole - monopole (recip)=         -44.60653603 eV
  Monopole - monopole (total)=         -49.06415344 eV
--------------------------------------------------------------------------------
  Total lattice energy : 
    Primitive unit cell      =         -42.26569304 eV
    Non-primitive unit cell  =        -169.06277218 eV
--------------------------------------------------------------------------------
  Total lattice energy (in kJmol-1): 
    Primitive unit cell      =           -4077.9933 kJ/(mole unit cells)
    Non-primitive unit cell  =          -16311.9732 kJ/(mole unit cells)
--------------------------------------------------------------------------------"""
        energy = self.gio.get_energy(out_str)
        self.assertEqual(energy, -169.06277218)

    def test_get_relaxed_structure(self):
        #Output string obtained from running GULP on a terminal
        with open('example21.gout','r') as fp:
            out_str = fp.read()
        struct = self.gio.get_relaxed_structure(out_str)
        self.assertIsInstance(struct, Structure)
        self.assertEqual(8, len(struct.sites))
        self.assertEqual(4.212, struct.lattice.a)
        self.assertEqual(90, struct.lattice.alpha)

    @unittest.skip("Test later")
    def test_tersoff_inpt(self):
        gin =  self.gio.tersoff_input(self.structure)
        #print "--------BinaryOxide Tersoff"
        print gin

class GlobalFunctionsTest(unittest.TestCase):
    def setUp(self):
        mgo_latt = [[4.212, 0, 0], [0, 4.212, 0], [0, 0, 4.212]]
        mgo_specie = ["Mg",'O']*4 
        mgo_frac_cord = [[0,0,0], [0.5,0,0], [0.5,0.5,0], [0,0.5,0],
                         [0.5,0,0.5], [0,0,0.5], [0,0.5,0.5], [0.5,0.5,0.5]]
        self.mgo_uc = Structure(mgo_latt, mgo_specie, mgo_frac_cord, True, True)
        bv = BVAnalyzer()
        val = bv.get_valences(self.mgo_uc)
        el = [site.species_string for site in self.mgo_uc.sites]
        self.val_dict = dict(zip(el, val))

    def test_get_energy_tersoff(self):
        p = Poscar.from_file(os.path.join(test_dir, 'POSCAR'))
        structure = p.structure
        enrgy = get_energy_tersoff(structure)
        self.assertIsInstance(enrgy, float)
        print "tersoff energy", enrgy

    def test_get_energy_buckingham(self):
        enrgy = get_energy_buckingham(self.mgo_uc)
        self.assertIsInstance(enrgy, float)
        print "Buckingham energy for charge neutral structure", enrgy
        #test with vacancy structure
        self.mgo_uc.remove(0)
        energy = get_energy_buckingham(self.mgo_uc, 
                keywords=('qok','optimise','conp'), valence_dict=self.val_dict)
        self.assertIsInstance(enrgy, float)
        print "Buckingham energy charged defect structure", enrgy

    def test_get_energy_relax_structure_buckingham(self):
        enrgy, struct = get_energy_relax_structure_buckingham(self.mgo_uc)
        self.assertIsInstance(enrgy, float)
        self.assertIsInstance(struct, Structure)
        site_len = len(struct.sites)
        self.assertEqual(site_len, len(self.mgo_uc.sites))
        print "Buckingham energy", enrgy
        print struct
        print self.mgo_uc

class BuckinghamPotLewisTest(unittest.TestCase):
    def setUp(self):
        self.bpl = BuckinghamPotLewis()

    def test_existing_element(self):
        self.assertIn("Sc_2+", self.bpl.pot_dict.keys())
        self.assertIn("Sc_2+", self.bpl.species_dict.keys())
        self.assertIn("O", self.bpl.pot_dict.keys())
        self.assertIn("O_core", self.bpl.species_dict.keys())
        self.assertIn("O_shel", self.bpl.species_dict.keys())

    def test_non_exisitng_element(self):
        self.assertNotIn("Li_1+", self.bpl.pot_dict.keys())
        self.assertNotIn("Li_1+", self.bpl.species_dict.keys())

    def test_element_different_valence(self):
        self.assertNotIn("Sc_4+", self.bpl.species_dict.keys())

    def test_values(self):
        self.assertNotEqual('', self.bpl.species_dict['Sc_2+'])
        self.assertNotEqual('', self.bpl.pot_dict['Sc_2+'])

    def test_spring(self):
        self.assertNotIn('Li', self.bpl.spring_dict.keys())
        self.assertNotEqual('', self.bpl.spring_dict['O'])

class BuckinghamPotBushTest(unittest.TestCase):
    def setUp(self):
        self.bpb = BuckinghamPotBush()
    def test_existing_element(self):
        self.assertIn("Li", self.bpb.pot_dict.keys())
        self.assertIn("Li", self.bpb.species_dict.keys())
        self.assertIn("O", self.bpb.pot_dict.keys())
        self.assertIn("O", self.bpb.species_dict.keys())
    def test_non_exisitng_element(self):
        self.assertNotIn("Mn", self.bpb.pot_dict.keys())
        self.assertNotIn("Mn", self.bpb.species_dict.keys())
    def test_element_different_valence(self):
        self.assertNotEqual(2, self.bpb.species_dict["Li"]['oxi'])
    def test_spring(self):
        self.assertEqual('', self.bpb.spring_dict["Li"])
        self.assertNotEqual('', self.bpb.spring_dict['O'])


if __name__ == '__main__':
    #suite = unittest.TestLoader().loadTestsFromTestCase(GlobalFunctionsTest)
    #suite = unittest.TestLoader().loadTestsFromTestCase(GulpIOTest)
    #suite = unittest.TestLoader().loadTestsFromTestCase(BuckinghamPotLewisTest)
    #suite = unittest.TestLoader().loadTestsFromTestCase(BuckinghamPotBushTest)
    #unittest.TextTestRunner(verbosity=3).run(suite)
    unittest.main()
