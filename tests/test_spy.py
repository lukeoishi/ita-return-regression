import unittest
import numpy as np
from compare_spy import predict, ALPHA

class SpyTests(unittest.TestCase):
    def test_smoothing_timing(self):
        p=predict([100,110,120,130,140])
        self.assertEqual(p['exponential'][1],100)
        self.assertAlmostEqual(p['exponential'][2],ALPHA*110+(1-ALPHA)*100)
        self.assertAlmostEqual(p['linear'][4],140)

    def test_future_independence(self):
        p=np.arange(100.,130.);q=p.copy();q[20:]+=50
        for name,values in predict(p).items():
            np.testing.assert_allclose(values[:21],predict(q)[name][:21])
