import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil
from data_analysis import (
    load_data,
    prepare_data,
    compute_metrics,
    save_reports,
    format_insights,
)


@pytest.fixture
def sample_data():
    """Create a sample dataset for testing."""
    data = {
        'InvoiceNo': ['536365', '536365', '536366'],
        'StockCode': ['85123A', '71053', '85123A'],
        'Description': ['WHITE HANGING HEART T-LIGHT HOLDER', 'WHITE METAL LANTERN', 'WHITE HANGING HEART T-LIGHT HOLDER'],
        'Quantity': [6, 6, 2],
        'InvoiceDate': ['2010-12-01 08:26:00', '2010-12-01 08:26:00', '2010-12-02 08:26:00'],
        'UnitPrice': [2.55, 3.39, 2.55],
        'CustomerID': [17850.0, 17850.0, 17851.0],
        'Country': ['United Kingdom', 'United Kingdom', 'United Kingdom'],
    }
    return pd.DataFrame(data)


@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_csv_file(sample_data):
    """Create a temporary CSV file with sample data."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    sample_data.to_csv(temp_file.name, index=False)
    yield Path(temp_file.name)
    Path(temp_file.name).unlink()


class TestLoadData:
    def test_load_data_returns_dataframe(self, temp_csv_file):
        """Test that load_data returns a DataFrame."""
        df = load_data(temp_csv_file)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    def test_load_data_preserves_invoice_number(self, temp_csv_file):
        """Test that InvoiceNo is loaded as string."""
        df = load_data(temp_csv_file)
        assert pd.api.types.is_string_dtype(df['InvoiceNo'])


class TestPrepareData:
    def test_prepare_data_adds_total_revenue(self, sample_data):
        """Test that TotalRevenue column is created."""
        df = prepare_data(sample_data)
        assert 'TotalRevenue' in df.columns
        assert df['TotalRevenue'].notna().all()

    def test_prepare_data_adds_month_year(self, sample_data):
        """Test that MonthYear column is created."""
        df = prepare_data(sample_data)
        assert 'MonthYear' in df.columns
        assert df['MonthYear'].notna().all()

    def test_prepare_data_converts_invoice_date(self, sample_data):
        """Test that InvoiceDate is converted to datetime."""
        df = prepare_data(sample_data)
        assert pd.api.types.is_datetime64_any_dtype(df['InvoiceDate'])

    def test_total_revenue_calculation(self, sample_data):
        """Test that TotalRevenue = Quantity * UnitPrice."""
        df = prepare_data(sample_data)
        expected = df['Quantity'] * df['UnitPrice']
        pd.testing.assert_series_equal(df['TotalRevenue'], expected, check_names=False)


class TestComputeMetrics:
    def test_compute_metrics_returns_four_values(self, sample_data):
        """Test that compute_metrics returns exactly 4 values."""
        df = prepare_data(sample_data)
        result = compute_metrics(df)
        assert len(result) == 4

    def test_compute_metrics_monthly_revenue(self, sample_data):
        """Test that monthly_revenue is a DataFrame with correct columns."""
        df = prepare_data(sample_data)
        monthly_revenue, _, _, _ = compute_metrics(df)
        assert isinstance(monthly_revenue, pd.DataFrame)
        assert 'MonthYear' in monthly_revenue.columns
        assert 'TotalRevenue' in monthly_revenue.columns

    def test_compute_metrics_top_products(self, sample_data):
        """Test that top_products returns correct structure."""
        df = prepare_data(sample_data)
        _, top_products, _, _ = compute_metrics(df)
        assert isinstance(top_products, pd.DataFrame)
        assert 'Description' in top_products.columns
        assert 'TotalRevenue' in top_products.columns
        assert len(top_products) <= 10

    def test_compute_metrics_top_countries(self, sample_data):
        """Test that top_countries returns correct structure."""
        df = prepare_data(sample_data)
        _, _, top_countries, _ = compute_metrics(df)
        assert isinstance(top_countries, pd.DataFrame)
        assert 'Country' in top_countries.columns
        assert 'TotalRevenue' in top_countries.columns
        assert len(top_countries) <= 10

    def test_compute_metrics_dict_keys(self, sample_data):
        """Test that metrics dict contains all expected keys."""
        df = prepare_data(sample_data)
        _, _, _, metrics = compute_metrics(df)
        expected_keys = [
            'total_revenue', 'invoice_count', 'average_order_value',
            'total_items_sold', 'unique_products', 'unique_countries'
        ]
        for key in expected_keys:
            assert key in metrics


class TestSaveReports:
    def test_save_reports_creates_output_directory(self, sample_data, temp_output_dir):
        """Test that output directory is created."""
        df = prepare_data(sample_data)
        monthly_revenue, top_products, top_countries, metrics = compute_metrics(df)
        save_reports(temp_output_dir, monthly_revenue, top_products, top_countries, metrics)
        assert temp_output_dir.exists()

    def test_save_reports_creates_all_files(self, sample_data, temp_output_dir):
        """Test that all four CSV files are created."""
        df = prepare_data(sample_data)
        monthly_revenue, top_products, top_countries, metrics = compute_metrics(df)
        save_reports(temp_output_dir, monthly_revenue, top_products, top_countries, metrics)
        
        expected_files = [
            'summary_statistics.csv',
            'revenue_by_month.csv',
            'top_products.csv',
            'revenue_by_country.csv'
        ]
        for file in expected_files:
            assert (temp_output_dir / file).exists()

    def test_save_reports_creates_valid_csvs(self, sample_data, temp_output_dir):
        """Test that saved CSV files can be read back."""
        df = prepare_data(sample_data)
        monthly_revenue, top_products, top_countries, metrics = compute_metrics(df)
        save_reports(temp_output_dir, monthly_revenue, top_products, top_countries, metrics)
        
        summary = pd.read_csv(temp_output_dir / 'summary_statistics.csv')
        assert not summary.empty
        assert 'Metric' in summary.columns
        assert 'Value' in summary.columns


class TestFormatInsights:
    def test_format_insights_returns_dict(self, sample_data):
        """Test that format_insights returns a dictionary."""
        df = prepare_data(sample_data)
        monthly_revenue, top_products, top_countries, metrics = compute_metrics(df)
        insights = format_insights(df.columns.tolist(), monthly_revenue, top_products, top_countries, metrics)
        assert isinstance(insights, dict)

    def test_format_insights_contains_expected_keys(self, sample_data):
        """Test that insights dict contains all expected keys."""
        df = prepare_data(sample_data)
        monthly_revenue, top_products, top_countries, metrics = compute_metrics(df)
        insights = format_insights(df.columns.tolist(), monthly_revenue, top_products, top_countries, metrics)
        
        expected_keys = [
            'total_revenue', 'best_month_label', 'best_month_value',
            'worst_month_label', 'worst_month_value', 'trend_sentence',
            'top_product', 'top_product_revenue', 'top_product_share',
            'top_country', 'top_country_revenue', 'top_country_share',
            'average_order_value', 'total_items_sold', 'category_note'
        ]
        for key in expected_keys:
            assert key in insights

    def test_format_insights_handles_missing_category(self, sample_data):
        """Test that format_insights handles missing Category column."""
        df = prepare_data(sample_data)
        monthly_revenue, top_products, top_countries, metrics = compute_metrics(df)
        insights = format_insights(df.columns.tolist(), monthly_revenue, top_products, top_countries, metrics)
        assert 'does not include a category column' in insights['category_note']

    def test_format_insights_percentages_valid(self, sample_data):
        """Test that share percentages are between 0 and 100."""
        df = prepare_data(sample_data)
        monthly_revenue, top_products, top_countries, metrics = compute_metrics(df)
        insights = format_insights(df.columns.tolist(), monthly_revenue, top_products, top_countries, metrics)
        
        assert 0 <= insights['top_product_share'] <= 100
        assert 0 <= insights['top_country_share'] <= 100
