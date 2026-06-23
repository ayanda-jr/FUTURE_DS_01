import pandas as pd
from pathlib import Path


def validate_input_path(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Raw data file not found: {path}")


def validate_required_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    raw_path = script_dir / 'data' / 'raw' / 'data.csv'
    output_path = script_dir / 'data' / 'processed' / 'cleaned_data.csv'

    validate_input_path(raw_path)

    print(f"Loading dataset from: {raw_path}")
    df = pd.read_csv(raw_path, encoding='ISO-8859-1')

    required_columns = ['Quantity', 'UnitPrice', 'InvoiceDate']
    validate_required_columns(df, required_columns)

    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
    df['TotalRevenue'] = df['Quantity'] * df['UnitPrice']
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format='%m/%d/%Y %H:%M')
    df['Year'] = df['InvoiceDate'].dt.year
    df['Month'] = df['InvoiceDate'].dt.month

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Data cleaning complete. Cleaned data saved to '{output_path}'.")


if __name__ == '__main__':
    main()
