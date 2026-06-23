import argparse
import pandas as pd
from pathlib import Path


def load_data(path: Path) -> pd.DataFrame:
    print(f'Loading cleaned dataset from: {path}')
    try:
        df = pd.read_csv(path, low_memory=False, dtype={'InvoiceNo': str})
    except FileNotFoundError:
        raise FileNotFoundError(f"Data file not found at {path}")
    except Exception as e:
        raise Exception(f"Error loading data from {path}: {str(e)}")
    
    if df.empty:
        raise ValueError("Loaded dataset is empty")
    
    print(df.head())
    return df


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    required_columns = ['InvoiceDate', 'Quantity', 'UnitPrice']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
    
    df = df.copy()  # Avoid SettingWithCopyWarning
    
    try:
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    except Exception as e:
        raise ValueError(f"Error converting InvoiceDate: {str(e)}")
    
    # Handle null values in Quantity or UnitPrice
    if df[['Quantity', 'UnitPrice']].isnull().any().any():
        print("Warning: Found null values in Quantity or UnitPrice. Dropping rows.")
        df = df.dropna(subset=['Quantity', 'UnitPrice'])
    
    if 'TotalRevenue' not in df.columns:
        df['TotalRevenue'] = df['Quantity'] * df['UnitPrice']
    
    df['MonthYear'] = df['InvoiceDate'].dt.to_period('M').astype(str)
    return df


def compute_metrics(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    required_columns = ['MonthYear', 'TotalRevenue', 'Description', 'Country', 'InvoiceNo', 'Quantity']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns for metrics computation: {', '.join(missing_cols)}")
    
    monthly_revenue = (
        df.groupby('MonthYear')['TotalRevenue']
          .sum()
          .reset_index()
          .sort_values('MonthYear')
    )

    top_products = (
        df.groupby('Description')['TotalRevenue']
          .sum()
          .reset_index()
          .sort_values('TotalRevenue', ascending=False)
          .head(10)
    )

    top_countries = (
        df.groupby('Country')['TotalRevenue']
          .sum()
          .reset_index()
          .sort_values('TotalRevenue', ascending=False)
          .head(10)
    )

    invoice_totals = df.groupby('InvoiceNo')['TotalRevenue'].sum()
    total_revenue = df['TotalRevenue'].sum()

    metrics = {
        'total_revenue': total_revenue,
        'invoice_count': invoice_totals.shape[0],
        'average_order_value': invoice_totals.mean(),
        'total_items_sold': df['Quantity'].sum(),
        'unique_products': df['Description'].nunique(),
        'unique_countries': df['Country'].nunique(),
        'monthly_revenue': monthly_revenue,
        'top_products': top_products,
        'top_countries': top_countries,
    }
    return monthly_revenue, top_products, top_countries, metrics


def save_reports(output_dir: Path, monthly_revenue: pd.DataFrame, top_products: pd.DataFrame, top_countries: pd.DataFrame, metrics: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_output_path = output_dir / 'summary_statistics.csv'
    summary_stats = {
        'Metric': [
            'Total Revenue',
            'Average Order Value',
            'Total Transactions',
            'Unique Products',
            'Unique Countries',
            'Average Revenue per Month',
        ],
        'Value': [
            metrics['total_revenue'],
            metrics['average_order_value'],
            metrics['invoice_count'],
            metrics['unique_products'],
            metrics['unique_countries'],
            monthly_revenue['TotalRevenue'].mean(),
        ],
    }
    pd.DataFrame(summary_stats).to_csv(summary_output_path, index=False)
    print(f"Summary statistics saved to '{summary_output_path}'.")

    revenue_by_month_path = output_dir / 'revenue_by_month.csv'
    monthly_revenue.to_csv(revenue_by_month_path, index=False)
    print(f"Revenue by month saved to '{revenue_by_month_path}'.")

    top_products_path = output_dir / 'top_products.csv'
    top_products.to_csv(top_products_path, index=False)
    print(f"Top products saved to '{top_products_path}'.")

    revenue_by_country_path = output_dir / 'revenue_by_country.csv'
    top_countries.to_csv(revenue_by_country_path, index=False)
    print(f"Top countries saved to '{revenue_by_country_path}'.")


def format_insights(df_columns: list[str], monthly_revenue: pd.DataFrame, top_products: pd.DataFrame, top_countries: pd.DataFrame, metrics: dict) -> dict:
    if monthly_revenue.empty or top_products.empty or top_countries.empty:
        raise ValueError("Cannot format insights: missing data in monthly_revenue, top_products, or top_countries")
    
    best_month = monthly_revenue.loc[monthly_revenue['TotalRevenue'].idxmax()]
    worst_month = monthly_revenue.loc[monthly_revenue['TotalRevenue'].idxmin()]
    
    trend_change = monthly_revenue.iloc[-1]['TotalRevenue'] - monthly_revenue.iloc[0]['TotalRevenue']
    if monthly_revenue.iloc[0]['TotalRevenue'] == 0:
        trend_pct = 0
    else:
        trend_pct = (trend_change / monthly_revenue.iloc[0]['TotalRevenue']) * 100
    trend_direction = 'rising' if trend_change > 0 else 'falling'

    if 'Category' not in df_columns:
        category_note = (
            'This dataset does not include a category column, so the analysis focuses on products and regions.'
        )
    else:
        category_note = 'Category-level analysis is available in this dataset.'

    return {
        'total_revenue': metrics['total_revenue'],
        'best_month_label': best_month['MonthYear'],
        'best_month_value': best_month['TotalRevenue'],
        'worst_month_label': worst_month['MonthYear'],
        'worst_month_value': worst_month['TotalRevenue'],
        'trend_sentence': (
            f"Revenue is {trend_direction} over time, changing by {abs(trend_pct):.1f}% "
            f"from {monthly_revenue.iloc[0]['MonthYear']} to {monthly_revenue.iloc[-1]['MonthYear']}.")
        ,
        'top_product': top_products.iloc[0]['Description'],
        'top_product_revenue': top_products.iloc[0]['TotalRevenue'],
        'top_product_share': (top_products.iloc[0]['TotalRevenue'] / metrics['total_revenue']) * 100 if metrics['total_revenue'] > 0 else 0,
        'top_country': top_countries.iloc[0]['Country'],
        'top_country_revenue': top_countries.iloc[0]['TotalRevenue'],
        'top_country_share': (top_countries.iloc[0]['TotalRevenue'] / metrics['total_revenue']) * 100 if metrics['total_revenue'] > 0 else 0,
        'average_order_value': metrics['average_order_value'],
        'total_items_sold': metrics['total_items_sold'],
        'category_note': category_note,
    }


def print_summary(insights: dict) -> None:
    print('\n' + '=' * 60)
    print('BUSINESS INSIGHTS SUMMARY')
    print('=' * 60)
    print(f"Total Revenue: ${insights['total_revenue']:,.2f}")
    print(f"Best Month: {insights['best_month_label']} (${insights['best_month_value']:,.2f})")
    print(f"Worst Month: {insights['worst_month_label']} (${insights['worst_month_value']:,.2f})")
    print(insights['trend_sentence'])
    print(
        f"Top Product: {insights['top_product']} with ${insights['top_product_revenue']:,.2f} "
        f"({insights['top_product_share']:.2f}% of total revenue)"
    )
    print(
        f"Top Country: {insights['top_country']} with ${insights['top_country_revenue']:,.2f} "
        f"({insights['top_country_share']:.2f}% of total revenue)"
    )
    print(f"Average Order Value: ${insights['average_order_value']:,.2f}")
    print(f"Total Items Sold: {insights['total_items_sold']:,}")
    print(insights['category_note'])
    print('\nACTIONABLE RECOMMENDATIONS')
    print(
        f"- Focus marketing and inventory on the top-performing products, especially {insights['top_product']}."
    )
    print(
        f"- Prioritize the {insights['top_country']} market since it generates {insights['top_country_share']:.1f}% of total revenue."
    )
    print(
        f"- Prepare promotions or special campaigns for low-revenue months like {insights['worst_month_label']}."
    )
    print('=' * 60)


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Analyze cleaned retail data and generate reports.'
    )
    parser.add_argument(
        '--input',
        type=Path,
        default=None,
        help='Path to cleaned data CSV file (default: data/processed/cleaned_data.csv)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=None,
        help='Output directory for reports (default: data/output)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress summary output'
    )
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).resolve().parent
    input_path = args.input or (script_dir / 'data' / 'processed' / 'cleaned_data.csv')
    output_dir = args.output or (script_dir / 'data' / 'output')

    try:
        df = load_data(input_path)
        df = prepare_data(df)
        monthly_revenue, top_products, top_countries, metrics = compute_metrics(df)
        save_reports(output_dir, monthly_revenue, top_products, top_countries, metrics)

        if not args.quiet:
            insights = format_insights(df.columns.tolist(), monthly_revenue, top_products, top_countries, metrics)
            print_summary(insights)
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
        exit(1)
    except ValueError as e:
        print(f"Error: {str(e)}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        exit(1)

if __name__ == '__main__':
    main()
