import unittest
import numpy as np
from anchored import slope_changes, choose_fraction

class AnchoredTests(unittest.TestCase):
    def test_known_slope(self):
        np.testing.assert_allclose(slope_changes(100+2*np.arange(30))[10:],2)

    def test_no_future_prices(self):
        p=100+np.arange(30,dtype=float)
        q=p.copy();q[20:]+=100
        np.testing.assert_allclose(slope_changes(p)[:21],slope_changes(q)[:21])

    def test_fraction_selection(self):
        x=np.arange(10,dtype=float)
        self.assertAlmostEqual(choose_fraction(x,.3*x),.3)
        self.assertEqual(choose_fraction(x,-x),0)
