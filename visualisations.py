import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def generate_dashboard(input_path: Path, output_path: Path) -> None:
    df = pd.read_csv(input_path, low_memory=False)

    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    if 'TotalRevenue' not in df.columns:
        df['TotalRevenue'] = df['Quantity'] * df['UnitPrice']
    df['MonthYear'] = df['InvoiceDate'].dt.to_period('M').astype(str)

    monthly_revenue = df.groupby('MonthYear')['TotalRevenue'].sum().reset_index()

    top_products = (
        df.groupby('Description')['TotalRevenue']
          .sum()
          .reset_index()
          .nlargest(10, 'TotalRevenue')
          .sort_values(by='TotalRevenue')
    )

    top_countries = (
        df.groupby('Country')['TotalRevenue']
          .sum()
          .reset_index()
          .nlargest(10, 'TotalRevenue')
          .sort_values(by='TotalRevenue')
    )

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('Sales Performance Dashboard', fontsize=16)

    axes[0, 0].plot(monthly_revenue['MonthYear'], monthly_revenue['TotalRevenue'], marker='o', linewidth=2)
    axes[0, 0].set_title('Monthly Revenue Trend')
    axes[0, 0].set_xlabel('Month')
    axes[0, 0].set_ylabel('Revenue ($)')
    axes[0, 0].tick_params(axis='x', rotation=45)
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].barh(top_products['Description'], top_products['TotalRevenue'], color='skyblue')
    axes[0, 1].set_title('Top 10 Products by Revenue')
    axes[0, 1].set_xlabel('Revenue ($)')
    axes[0, 1].tick_params(axis='y', labelsize=8)

    axes[1, 0].barh(top_countries['Country'], top_countries['TotalRevenue'], color='lightgreen')
    axes[1, 0].set_title('Top 10 Countries by Revenue')
    axes[1, 0].set_xlabel('Revenue ($)')
    axes[1, 0].tick_params(axis='y', labelsize=8)

    axes[1, 1].axis('off')
    summary_text = (
        f"Total Revenue: ${df['TotalRevenue'].sum():,.2f}\n"
        f"Total Transactions: {len(df):,}\n"
        f"Unique Products: {df['Description'].nunique():,}\n"
        f"Unique Countries: {df['Country'].nunique():,}\n"
        f"Date range: {df['InvoiceDate'].min().date()} to {df['InvoiceDate'].max().date()}"
    )
    axes[1, 1].text(
        0.5,
        0.5,
        summary_text,
        fontsize=12,
        ha='center',
        va='center',
        bbox=dict(boxstyle='round', facecolor='lightgrey', alpha=0.5),
    )

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Dashboard saved to '{output_path}'.")


if __name__ == '__main__':
    script_dir = Path(__file__).resolve().parent
    generate_dashboard(script_dir / 'cleaned_data.csv', script_dir / 'sales_dashboard.png')
