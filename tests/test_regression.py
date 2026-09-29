import unittest
import numpy as np
from regression import forecast, walk_forward

class RegressionTests(unittest.TestCase):
    def test_linear_extrapolation(self):
        self.assertAlmostEqual(forecast(100+2*np.arange(10)),120)

    def test_quadratic_extrapolation(self):
        t=np.arange(10)
        self.assertAlmostEqual(forecast(100+2*t+t*t,2),220)

    def test_future_cannot_change_prediction(self):
        prices=100+np.arange(40,dtype=float)
        altered=prices.copy();altered[20:]+=30
        for degree in (1,2):
            np.testing.assert_allclose(walk_forward(prices,degree)[:21],
                                       walk_forward(altered,degree)[:21])

    def test_only_last_ten_prices_matter(self):
        prices=100+np.arange(40,dtype=float)
        altered=prices.copy();altered[:10]+=50
        for degree in (1,2):
            self.assertAlmostEqual(walk_forward(prices,degree)[20],
                                   walk_forward(altered,degree)[20])

    def test_invalid_window(self):
        with self.assertRaises(ValueError):
            forecast([100]*9)
