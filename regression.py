"""Fit the last ten ITA closes and extrapolate one trading day ahead."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np


def forecast(prices, degree=1):
    """Equal-weight least squares on ten prices; time is the only input."""
    prices = np.asarray(prices, dtype=float)
    if prices.shape != (10,) or not np.all(np.isfinite(prices) & (prices > 0)):
        raise ValueError('Provide exactly ten finite positive prices.')
    if degree not in (1, 2):
        raise ValueError('Degree must be 1 or 2.')
    coefficients = np.polynomial.polynomial.polyfit(np.arange(10), prices, degree)
    return float(np.polynomial.polynomial.polyval(10, coefficients))


def walk_forward(prices, degree=1):
    predictions = np.full(len(prices), np.nan)
    for t in range(10, len(prices)):
        predictions[t] = forecast(prices[t-10:t], degree)
    return predictions


def run(source, output):
    with source.open() as f:
        rows = list(csv.DictReader(f))
    dates = np.array([r['Date'] for r in rows])
    prices = np.array([float(r['Close']) for r in rows])
    if len(prices) < 11 or not np.all(dates[1:] > dates[:-1]):
        raise ValueError('Need at least eleven prices with unique sorted dates.')
    predictions = {name: walk_forward(prices, degree)
                   for name, degree in [('linear', 1), ('quadratic', 2)]}
    previous = np.roll(prices, 1)
    test = (dates >= '2022-01-01') & (np.arange(len(prices)) >= 10)
    if not test.any():
        raise ValueError('No evaluation observations from 2022 onward.')
    def score(prediction):
        error = (prediction[test] - prices[test]) / previous[test]
        return float(100 * np.sqrt(np.mean(error**2)))
    baseline = score(previous)
    scores = {name: score(pred) for name, pred in predictions.items()}
    result = dict(window=10, horizon=1, weighting='equal',
        evaluation_start=dates[test][0], evaluation_end=dates[test][-1],
        observations=int(test.sum()), rmse_pct=scores, baseline_rmse_pct=baseline,
        improvement_pct={k:100*(1-v/baseline) for k,v in scores.items()},
        metric='RMSE of (predicted close - actual close) / previous close, percent',
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        limitation='Exploratory retrospective comparison; this period has been examined before.')
    output.mkdir(parents=True, exist_ok=True)
    (output/'metrics.json').write_text(json.dumps(result, indent=2)+'\n')
    with (output/'predictions.csv').open('w', newline='') as f:
        w=csv.writer(f)
        w.writerow(['target_date','actual_close','linear','quadratic','last_close_baseline'])
        w.writerows(zip(dates[test],prices[test],predictions['linear'][test],
                       predictions['quadratic'][test],previous[test]))
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=Path('results'))
    args=parser.parse_args()
    run(args.data,args.output)
