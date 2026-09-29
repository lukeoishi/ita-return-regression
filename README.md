# SPY price forecasts

Three simple ways to predict the next trading day's adjusted closing price:

- **Baseline:** use today's close.
- **Linear regression:** fit a line to the last four closes and extend it one day.
- **Exponential smoothing:** update the estimate with 82.7% of the latest close and 17.3% of the previous estimate.

One Python script, NumPy only. No parameter search when running it.

## Run

```sh
python -m pip install -r requirements.txt
python compare_spy.py --data /path/to/spy_daily_adjusted.csv
python -m unittest discover -s tests
```

Supply a CSV with sorted, unique `Date` and positive adjusted `Close` columns. Include price history before 2022 to initialise the models. The complete source price file is not included.

## Results

1,181 forecasts, 3 January 2022–17 September 2026. Lower RMSE is better.

| Model | RMSE (USD) | Normalised RMSE |
|---|---:|---:|
| Baseline | 5.3184 | 1.0951% |
| Linear | 6.5743 | 1.3661% |
| Exponential smoothing | 5.3672 | 1.1070% |

**Neither model beat the baseline.** Normalised error divides each price error by the previous close before calculating RMSE.

The four-day window and 0.827 smoothing weight were selected on 2018–2021 data using normalised RMSE. Windows 2–504 and weights 0.001–1.000 were tested. They are fixed settings, not universal optima. See [the experiment log](LOG.md).

`compare_spy.py` contains the models and evaluation. `tests/test_spy.py` checks forecast timing and independence from future prices. `results/spy/` contains settings, scores and every prediction.

This is a retrospective experiment using cached Yahoo/yfinance adjusted prices. The later period was inspected during development, so it is not an untouched holdout. The data are not independently verified point-in-time records. No live feed, trading returns or transaction costs are modelled.
