# ITA: ten-day regression forecasts

Take the last ten adjusted closing prices, fit a straight line or quadratic against trading-day number, and extend it to the next day. Move the window forward and repeat.

- Linear: `price = a + b*t`.
- Quadratic: `price = a + b*t + c*t²`.
- Fit on `t = 0,...,9`; forecast at `t = 10`.

Every observation has equal weight. Each forecast gets a fresh fit using exactly ten preceding closes. No years-long coefficient training, extra signals, regularisation or parameter search. Historical prices are used to evaluate repeated forecasts, not to fit each individual line.

## Results

Evaluation covers 1,181 trading days from 3 January 2022 to 17 September 2026.

| Model | Normalised price RMSE |
|---|---:|
| Predict the previous close | 1.2813% |
| Ten-day linear fit | 1.8596% |
| Ten-day quadratic fit | 1.9477% |

Linear error was 45.1% higher than the baseline; quadratic error was 52.0% higher. Neither improved next-day predictions in this comparison. Error is `(prediction - actual close) / previous close`; RMSE is expressed as a percentage. It is not a return or trading profit.

This is exploratory retrospective evaluation on a period already inspected during development, not an untouched holdout. The source is a cached Yahoo/yfinance adjusted daily ITA series; its hash is recorded in the metrics. It is not an independently verified point-in-time archive. No transaction costs or trading strategy are evaluated.

## Run

```sh
python -m pip install -r requirements.txt
python regression.py --data /path/to/ita_daily_adjusted.csv
python -m unittest discover -s tests
```

Supply a CSV with sorted, unique `Date` and positive adjusted `Close` columns, including ten prior observations and dates from 2022 onward. The full source snapshot is not included. Results are written to `results/metrics.json` and `results/predictions.csv`.

`regression.py` contains the complete model and evaluation. Tests verify known line/curve extrapolation, the ten-observation window, and that future prices cannot affect earlier predictions.

## Anchoring the forecast at the latest price

`python anchored.py --data /path/to/ita_daily_adjusted.csv` tests:

`forecast = latest close + fraction × ten-day fitted slope`

The fraction is chosen from 0 to 1 in steps of 0.05 using 2018–2021 normalised prediction error only. The window stays fixed at ten days. Calibration chose **zero**, so the selected forecast is exactly the last-close baseline. On the later period, the full slope gave 1.3641% RMSE; the selected zero fraction gave 1.2813%. Anchoring reduced the original line's error, but this test did not establish a useful trend signal. No further parameter search was performed to force a win. Outputs are `results/anchored.json` and `results/anchored-predictions.csv`.
