import unittest
from maksukortti import Maksukortti

class TestMaksukortti(unittest.TestCase):
    def setUp(self):
        self.maksukortti = Maksukortti(1000)

    def test_luotu_kortti_on_olemassa(self):
        self.assertNotEqual(self.maksukortti, None)

    def test_kortin_saldo_oikein(self):
        self.assertEqual(self.maksukortti.saldo_euroina(), 10)

    def test_rahan_lataaminen_toimii(self):
        self.maksukortti.lataa_rahaa(50)

        self.assertEqual(self.maksukortti.saldo_euroina(), 10.5)

    def test_rahan_ottaminen_toimii_jos_saldoa_riittaa(self):
        saldo_riitti = self.maksukortti.ota_rahaa(50)

        self.assertEqual(self.maksukortti.saldo_euroina(), 9.5)
        self.assertTrue(saldo_riitti)

    def test_rahan_ottaminen_ei_toimi_jos_saldo_ei_riita(self):
        saldo_riitti = self.maksukortti.ota_rahaa(1500)
        
        self.assertEqual(self.maksukortti.saldo_euroina(), 10)
        self.assertFalse(saldo_riitti)
