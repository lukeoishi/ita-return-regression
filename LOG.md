# Experiment log

## 29 September 2026 — final simple comparison

Scope: SPY next-day adjusted closing price, comparing a last-close baseline, rolling linear regression and exponential smoothing.

Fixed settings selected using 2018–2021 normalised RMSE:

- Linear: four preceding trading closes; best tested window among 2–504.
- Exponential smoothing: alpha 0.827; best tested weight on a 0.001 grid from 0.001 to 1.000. The earlier 0.05 grid selected 0.85.
- Baseline: previous close.

The prediction for a date is calculated before observing that date's close. Smoothing begins at the first input close and updates sequentially; linear regression is refitted daily. Neither uses future observations.

Later evaluation: 1,181 targets from 3 January 2022 to 17 September 2026. Normalised RMSE: baseline 1.095142%, linear 1.366071%, smoothing 1.107005%. Dollar RMSE: 5.318415, 6.574250 and 5.367244 respectively. Finer smoothing calibration did not improve later-period performance over the previous 0.85 weight. No performance advantage is claimed.

Source snapshot SHA-256: `98a5ce795f92201b1924a742b1904a019b00758c96b50db2ca56baac2a2a096c`.

The later period has been reused during exploration. Selection used earlier data, but the overall research process is exploratory. Previous ITA, quadratic and anchoring experiments have been removed from the current working files to keep this project focused; their history remains in Git.
