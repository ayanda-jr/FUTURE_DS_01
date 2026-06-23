# FUTURE_DS_01

This project loads cleaned retail data, runs revenue analysis, and generates a sales dashboard.

## Project structure

- `data/raw/` - raw source dataset files
- `data/processed/` - generated cleaned data files
- `data/output/` - generated analysis outputs and visualization files

## Run the full workflow

```bash
python data_prep.py
python data_analysis.py
```

## Generated output

Generated files are written to `data/output/`:

- `summary_statistics.csv`
- `revenue_by_month.csv`
- `top_products.csv`
- `revenue_by_country.csv`

## Notes

- `data_prep.py` reads raw source data from `data/raw/data.csv` and writes cleaned data to `data/processed/cleaned_data.csv`.
- `data_analysis.py` reads the cleaned dataset from `data/processed/cleaned_data.csv` and stores reports in `data/output/`.
- Visualizations are created separately using Power BI with the generated CSV reports.
