import unittest
from kassapaate import Kassapaate
from maksukortti import Maksukortti

class TestKassapaate(unittest.TestCase):
    def setUp(self):
        self.kassapaate = Kassapaate()
        self.maksukortti = Maksukortti(1000)

    def test_kassan_rahamaara_alussa_oikein(self):
        self.assertEqual(self.kassapaate.kassassa_rahaa_euroina(), 1000)

    def test_lounaita_myyty_alussa_oikein(self):
        self.assertEqual(self.kassapaate.edulliset, 0)
        self.assertEqual(self.kassapaate.maukkaat, 0)

    def test_kateismaksu_edulliselle_toimii_jos_maksu_riittava(self):
        vaihtoraha = self.kassapaate.syo_edullisesti_kateisella(300)

        self.assertEqual(self.kassapaate.kassassa_rahaa_euroina(), 1002.40)
        self.assertEqual(vaihtoraha, 60)
        self.assertEqual(self.kassapaate.edulliset, 1)

    def test_kateismaksu_maukkaalle_toimii_jos_maksu_riittava(self):
        vaihtoraha = self.kassapaate.syo_maukkaasti_kateisella(500)

        self.assertEqual(self.kassapaate.kassassa_rahaa_euroina(), 1004)
        self.assertEqual(vaihtoraha, 100)
        self.assertEqual(self.kassapaate.maukkaat, 1)

    def test_kateismaksu_edulliselle_ei_toimi_jos_maksu_ei_riita(self):
        vaihtoraha = self.kassapaate.syo_edullisesti_kateisella(50)

        self.assertEqual(self.kassapaate.kassassa_rahaa_euroina(), 1000)
        self.assertEqual(vaihtoraha, 50)
        self.assertEqual(self.kassapaate.edulliset, 0)

    def test_kateismaksu_maukkaalle_ei_toimi_jos_maksu_ei_riita(self):
        vaihtoraha = self.kassapaate.syo_maukkaasti_kateisella(50)

        self.assertEqual(self.kassapaate.kassassa_rahaa_euroina(), 1000)
        self.assertEqual(vaihtoraha, 50)
        self.assertEqual(self.kassapaate.maukkaat, 0)

    def test_korttimaksu_edulliselle_toimii_jos_saldo_riittava(self):
        saldo_riitti = self.kassapaate.syo_edullisesti_kortilla(self.maksukortti)

        self.assertEqual(self.maksukortti.saldo_euroina(), 7.60)
        self.assertTrue(saldo_riitti)
        self.assertEqual(self.kassapaate.edulliset, 1)

    def test_korttimaksu_maukkaalle_toimii_jos_saldo_riittava(self):
        saldo_riitti = self.kassapaate.syo_maukkaasti_kortilla(self.maksukortti)

        self.assertEqual(self.maksukortti.saldo_euroina(), 6)
        self.assertTrue(saldo_riitti)
        self.assertEqual(self.kassapaate.maukkaat, 1)

    def test_korttimaksu_edulliselle_ei_toimi_jos_saldo_ei_riita(self):
        maksukortti = Maksukortti(100)
        saldo_riitti = self.kassapaate.syo_edullisesti_kortilla(maksukortti)

        self.assertEqual(maksukortti.saldo_euroina(), 1)
        self.assertFalse(saldo_riitti)
        self.assertEqual(self.kassapaate.edulliset, 0)

    def test_korttimaksu_maukkaalle_ei_toimi_jos_saldo_ei_riita(self):
        maksukortti = Maksukortti(100)
        saldo_riitti = self.kassapaate.syo_maukkaasti_kortilla(maksukortti)

        self.assertEqual(maksukortti.saldo_euroina(), 1)
        self.assertFalse(saldo_riitti)
        self.assertEqual(self.kassapaate.maukkaat, 0)

    def test_kortille_lataaminen_toimii(self):
        self.kassapaate.lataa_rahaa_kortille(self.maksukortti, 500)

        self.assertEqual(self.maksukortti.saldo_euroina(), 15)
        self.assertEqual(self.kassapaate.kassassa_rahaa_euroina(), 1005)

    def test_negatiivisen_maaran_lataaminen_kortille_ei_toimi(self):
        self.kassapaate.lataa_rahaa_kortille(self.maksukortti, -500)

        self.assertEqual(self.maksukortti.saldo_euroina(), 10)
        self.assertEqual(self.kassapaate.kassassa_rahaa_euroina(), 1000)
