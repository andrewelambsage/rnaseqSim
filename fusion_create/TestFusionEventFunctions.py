# -*- coding: utf-8 -*-
from Bio.SeqFeature import SeqFeature
from Bio.SeqFeature import FeatureLocation
from Bio.SeqFeature import ExactPosition
import FusionEventFunctions as FEV
import unittest
import random

class TestFusionEventFunctions(unittest.TestCase):
    
    def setUp(self):
        self.exon1 = SeqFeature(FeatureLocation(ExactPosition(100), 
                                                ExactPosition(500), 
                                                strand = -1),
                          type = 'exon', id = 'exon_1')
        self.exon2 = SeqFeature(FeatureLocation(ExactPosition(800), 
                                                ExactPosition(1000), 
                                                strand = -1),
                          type = 'exon', id = 'exon_2')
        self.exon3 = SeqFeature(FeatureLocation(ExactPosition(1500), 
                                                ExactPosition(2000), 
                                                strand = -1),
                          type = 'exon', id = 'exon_3')
        self.exons1 = [self.exon1, self.exon2, self.exon3]
        
    def test_get_direction(self):
        self.assertEqual(FEV.get_direction("donor", "+"), "forward")
        self.assertEqual(FEV.get_direction("acceptor", "-"), "forward")
        self.assertEqual(FEV.get_direction("donor", "-"), "reverse")
        self.assertEqual(FEV.get_direction("acceptor", "+"), "reverse")
        
    def test_create_mid_exon_breakage(self):
        # exons are cut to the right of the junction exon, and the junction is
        # a random base in that exon   
        random.seed(1)
        res1 = FEV.create_mid_exon_breakage(self.exons1, 0, "forward")
        self.assertEqual(res1[0], ExactPosition(154))
        self.assertEqual(res1[1][0].location.start, ExactPosition(100))
        self.assertEqual(res1[1][0].location.end, ExactPosition(154))
        self.setUp()
        
        random.seed(1)
        res2 = FEV.create_mid_exon_breakage(self.exons1, 1, "forward")
        self.assertEqual(res2[0], ExactPosition(827))
        self.assertEqual(res2[1][0].location.start, ExactPosition(100))
        self.assertEqual(res2[1][0].location.end, ExactPosition(500))
        self.assertEqual(res2[1][1].location.start, ExactPosition(800))
        self.assertEqual(res2[1][1].location.end, ExactPosition(827))
        self.setUp()
        
        # exons are cut to the left of the junction exon, and the junction is
        # a random base in that exon   
        random.seed(2)
        res3 = FEV.create_mid_exon_breakage(self.exons1, 0, "reverse")
        self.assertEqual(res3[0], ExactPosition(482))
        self.assertEqual(res3[1][0].location.start, ExactPosition(482))
        self.assertEqual(res3[1][0].location.end, ExactPosition(500))
        self.assertEqual(res3[1][1].location.start, ExactPosition(800))
        self.assertEqual(res3[1][1].location.end, ExactPosition(1000))
        self.assertEqual(res3[1][2].location.start, ExactPosition(1500))
        self.assertEqual(res3[1][2].location.end, ExactPosition(2000))
        self.setUp()
        
        random.seed(2)
        res4 = FEV.create_mid_exon_breakage(self.exons1, 1, "reverse")
        self.assertEqual(res4[0], ExactPosition(991))
        self.assertEqual(res4[1][0].location.start, ExactPosition(991))
        self.assertEqual(res4[1][0].location.end, ExactPosition(1000))
        self.assertEqual(res4[1][1].location.start, ExactPosition(1500))
        self.assertEqual(res4[1][1].location.end, ExactPosition(2000))
        self.setUp()

        
    def test_create_exon_breakage(self):
        # exons are cut to the right of the junction exon, and the junction is
        # the end of that exon
        self.assertEqual(FEV.create_exon_breakage(self.exons1, 0, "forward"), 
                         (ExactPosition(500), [self.exon1]))
        self.assertEqual(FEV.create_exon_breakage(self.exons1, 1, "forward"), 
                         (ExactPosition(1000), [self.exon1, self.exon2]))
        self.assertEqual(FEV.create_exon_breakage(self.exons1, 2, "forward"), 
                         (ExactPosition(2000), self.exons1))
        # exons are cut to the left of the junction exon, and the junction is
        # the start of that exon
        self.assertEqual(FEV.create_exon_breakage(self.exons1, 0, "reverse"), 
                         (ExactPosition(100), self.exons1))
        self.assertEqual(FEV.create_exon_breakage(self.exons1, 1, "reverse"), 
                         (ExactPosition(800), [self.exon2, self.exon3]))
        self.assertEqual(FEV.create_exon_breakage(self.exons1, 2, "reverse"), 
                         (ExactPosition(1500), [self.exon3]))
    
    def test_slice_exons_at_fusion_exon(self):
        # these exon lists remian unchanged
        self.assertEqual(FEV.slice_exons_at_fusion_exon(
            self.exons1, 2, "forward"), self.exons1)
        self.assertEqual(FEV.slice_exons_at_fusion_exon(
            self.exons1, 0, "reverse"), self.exons1)
        # these are cut down to one exon
        self.assertEqual(FEV.slice_exons_at_fusion_exon(
            self.exons1, 0, "forward"), [self.exon1])
        self.assertEqual(FEV.slice_exons_at_fusion_exon(
            self.exons1, 2, "reverse"), [self.exon3])
        self.setUp()

    def test_create_new_exon(self):
        new_exon1 = FEV.create_new_exon(self.exon1, "start", 150)
        new_exon2 = FEV.create_new_exon(self.exon2, "end", 900)
        self.assertEqual(new_exon1.location.start, 150)
        self.assertEqual(new_exon1.location.end, 500)
        self.assertEqual(new_exon2.location.start, 800)
        self.assertEqual(new_exon2.location.end, 900)
        self.setUp()

if __name__ == '__main__':
    unittest.main()