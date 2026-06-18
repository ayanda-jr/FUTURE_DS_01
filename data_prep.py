import pandas as pd
from pathlib import Path

script_dir = Path(__file__).resolve().parent
input_path = script_dir / 'Dataset' / 'data.csv'
output_path = script_dir / 'cleaned_data.csv'

# Load the dataset
print(f'Loading dataset from: {input_path}')
df = pd.read_csv(input_path, encoding='ISO-8859-1')
print(df.head())

# Only keep rows where the quantity and unit price are greater than 0
df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
print(df.head())

# Calculate the total revenue
df['TotalRevenue'] = df['Quantity'] * df['UnitPrice']

#Convert InvoiceDate to a proper datetime format
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format='%m/%d/%Y %H:%M')

#Extract the year and month from the InvoiceDate
df['Year'] = df['InvoiceDate'].dt.year
df['Month'] = df['InvoiceDate'].dt.month

# Save to a new file
df.to_csv(output_path, index=False)
print(f"Data cleaning complete. Cleaned data saved to '{output_path}'.")
