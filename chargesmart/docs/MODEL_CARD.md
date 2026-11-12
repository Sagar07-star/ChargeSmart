# Waiting-time demonstration model

Not suitable for real travel decisions. Run `python -m app.ml.train` from backend.

6,000 deterministic synthetic rows, seed 42. Features: hour, weekday, port count, assumed occupancy. Target: max(0, occupancy × 25 + evening × 12 + weekend × 4 − ports × 1.5 + Normal(0,3)). Evening is 17–21.

Random split: 4,800 training / 1,200 held-out rows. Random Forest: 80 trees, max depth 10, seed 42. MAE/RMSE are computed from predictions, never hard-coded as accuracy claims. They measure learning of this generator, not real-world reliability. Future historical training needs station/time-aware validation and leakage checks.

The script writes `synthetic_sessions.csv`, `wait_model.joblib`, `metrics.json`. Backend loads the model if present, otherwise labels estimates as rules. Browser demo always uses rules and shows no ML metrics. Occupancy is a user assumption, not measured utilization. No prediction intervals are claimed. Load joblib files only from trusted sources.
