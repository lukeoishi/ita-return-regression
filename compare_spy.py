"""Three next-day SPY forecasts with fixed, previously selected settings."""
import argparse
import csv
import json
from pathlib import Path
import numpy as np

ALPHA = 0.827
LINEAR_WINDOW = 4


def predict(prices):
    prices = np.asarray(prices, dtype=float)
    if prices.ndim != 1 or len(prices) < 5 or not np.all(np.isfinite(prices) & (prices > 0)):
        raise ValueError('Need five or more positive finite closes.')
    baseline = np.roll(prices, 1); baseline[0] = np.nan
    smooth = np.full(len(prices), np.nan)
    linear = np.full(len(prices), np.nan)
    level = prices[0]
    for t in range(1, len(prices)):
        smooth[t] = level
        level = ALPHA*prices[t] + (1-ALPHA)*level
        if t >= LINEAR_WINDOW:
            coef = np.polynomial.polynomial.polyfit(
                np.arange(LINEAR_WINDOW), prices[t-LINEAR_WINDOW:t], 1)
            linear[t] = np.polynomial.polynomial.polyval(LINEAR_WINDOW, coef)
    return {'baseline': baseline, 'linear': linear, 'exponential': smooth}


def run(source, output):
    with source.open() as f:
        rows = list(csv.DictReader(f))
    dates = np.array([r['Date'] for r in rows])
    if not np.all(dates[1:] > dates[:-1]):
        raise ValueError('Dates must be unique and increasing.')
    prices = np.array([float(r['Close']) for r in rows])
    forecasts = predict(prices)
    test = (dates >= '2022-01-01') & (np.arange(len(prices)) >= LINEAR_WINDOW)
    if not test.any():
        raise ValueError('No evaluation dates from 2022 onward.')
    result = dict(alpha=ALPHA,linear_window=LINEAR_WINDOW,
                  start=dates[test][0],end=dates[test][-1],observations=int(test.sum()),models={})
    for name,pred in forecasts.items():
        error = pred[test]-prices[test]
        result['models'][name] = dict(rmse_usd=float(np.sqrt(np.mean(error**2))),
            normalised_rmse_pct=float(100*np.sqrt(np.mean((error/forecasts['baseline'][test])**2))))
    output.mkdir(parents=True,exist_ok=True)
    (output/'three-models.json').write_text(json.dumps(result,indent=2)+'\n')
    with (output/'three-model-predictions.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['date','actual','baseline','linear','exponential'])
        w.writerows(zip(dates[test],prices[test],*(pred[test] for pred in forecasts.values())))
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=Path('results/spy'))
    args=parser.parse_args();run(args.data,args.output)
