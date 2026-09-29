"""Test a ten-day slope added to today's close, with a calibrated fraction."""
import argparse
import csv
import json
from pathlib import Path
import numpy as np


def slope_changes(prices):
    prices = np.asarray(prices, dtype=float)
    if prices.ndim != 1 or len(prices) < 11 or not np.all(np.isfinite(prices) & (prices > 0)):
        raise ValueError('Need eleven or more finite positive prices.')
    changes = np.full(len(prices), np.nan)
    time = np.arange(10) - 4.5
    for t in range(10, len(prices)):
        changes[t] = time @ prices[t-10:t] / (time @ time)
    return changes


def choose_fraction(changes, actual_changes):
    # Fixed, small grid; zero means the last-price baseline.
    fractions = np.linspace(0, 1, 21)
    errors = [np.mean((actual_changes - f*changes)**2) for f in fractions]
    return float(fractions[np.argmin(errors)])


def run(source, output):
    with source.open() as f:
        rows = list(csv.DictReader(f))
    dates = np.array([r['Date'] for r in rows])
    if not np.all(dates[1:] > dates[:-1]):
        raise ValueError('Dates must be sorted and unique.')
    prices = np.array([float(r['Close']) for r in rows])
    changes = slope_changes(prices)
    previous = np.roll(prices, 1)
    valid = np.isfinite(changes)
    calibration = valid & (dates >= '2018-01-01') & (dates < '2022-01-01')
    test = valid & (dates >= '2022-01-01')
    if not calibration.any() or not test.any():
        raise ValueError('Need calibration and test observations.')
    signal = changes / previous
    actual = (prices - previous) / previous
    fraction = choose_fraction(signal[calibration], actual[calibration])
    def score(f):
        return float(100*np.sqrt(np.mean((actual[test]-f*signal[test])**2)))
    result = dict(window=10, calibration='2018–2021', fraction=fraction,
        fractions_tested=np.linspace(0,1,21).tolist(),
        evaluation_start=dates[test][0],evaluation_end=dates[test][-1],
        observations=int(test.sum()),baseline_rmse_pct=score(0),
        anchored_full_slope_rmse_pct=score(1),selected_rmse_pct=score(fraction),
        improvement_pct=100*(1-score(fraction)/score(0)),
        limitation='Retrospective exploratory test; later period previously inspected.')
    output.mkdir(parents=True,exist_ok=True)
    (output/'anchored.json').write_text(json.dumps(result,indent=2)+'\n')
    with (output/'anchored-predictions.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['date','actual_close','forecast','last_close'])
        w.writerows(zip(dates[test],prices[test],(previous+fraction*changes)[test],previous[test]))
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,required=True)
    p.add_argument('--output',type=Path,default=Path('results'))
    a=p.parse_args();run(a.data,a.output)
