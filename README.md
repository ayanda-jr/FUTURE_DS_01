# FUTURE_DS_01

This project loads cleaned retail data, runs revenue analysis, and generates a sales dashboard.

## Run the full workflow

```bash
python data_analysis.py
```

## Generated output

- `summary_statistics.csv`
- `revenue_by_month.csv`
- `top_products.csv`
- `revenue_by_country.csv`
- `sales_dashboard.png`

## Notes

- `data_analysis.py` now runs the full analysis and also generates `sales_dashboard.png` by importing `visualisations.py`.
- You can regenerate only the dashboard with:

```bash
python visualisations.py
```
