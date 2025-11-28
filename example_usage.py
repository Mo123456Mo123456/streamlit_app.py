"""
Example Usage of the Automated Profit Analysis System
مثال على استخدام نظام تحليل الأرباح الآلي

This script demonstrates how to use the profit analysis functions programmatically.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

# Load the data
def load_data():
    """Load and process financial data."""
    DATA_FILE = Path(__file__).parent / 'data/financial_data.csv'
    df = pd.read_csv(DATA_FILE)
    
    # Calculate profit metrics
    df['Gross_Profit'] = df['Revenue'] - df['Costs']
    df['Operating_Profit'] = df['Gross_Profit'] - df['Operating_Expenses'] - df['Marketing'] - df['R&D']
    df['Net_Profit'] = df['Operating_Profit'] - df['Taxes']
    
    # Calculate margins
    df['Gross_Margin'] = (df['Gross_Profit'] / df['Revenue']) * 100
    df['Operating_Margin'] = (df['Operating_Profit'] / df['Revenue']) * 100
    df['Net_Margin'] = (df['Net_Profit'] / df['Revenue']) * 100
    
    # Calculate ROI
    df['Total_Investment'] = df['Costs'] + df['Operating_Expenses'] + df['Marketing'] + df['R&D']
    df['ROI'] = ((df['Net_Profit'] / df['Total_Investment']) * 100)
    
    return df

# Example 1: Get total profits by company
def example_1_company_profits():
    """Calculate total profits for each company."""
    print("=" * 60)
    print("Example 1: Total Profits by Company")
    print("مثال 1: إجمالي الأرباح حسب الشركة")
    print("=" * 60)
    
    df = load_data()
    
    company_profits = df.groupby('Company').agg({
        'Revenue': 'sum',
        'Gross_Profit': 'sum',
        'Operating_Profit': 'sum',
        'Net_Profit': 'sum'
    }).round(2)
    
    print("\nCompany Profit Summary:")
    print(company_profits)
    print("\n")

# Example 2: Calculate monthly growth rates
def example_2_growth_rates():
    """Calculate month-over-month growth rates."""
    print("=" * 60)
    print("Example 2: Monthly Growth Rates")
    print("مثال 2: معدلات النمو الشهرية")
    print("=" * 60)
    
    df = load_data()
    
    for company in df['Company'].unique():
        company_data = df[df['Company'] == company].sort_values(['Year', 'Month'])
        
        # Calculate growth rate
        company_data['Revenue_Growth'] = company_data['Revenue'].pct_change() * 100
        company_data['Profit_Growth'] = company_data['Net_Profit'].pct_change() * 100
        
        avg_revenue_growth = company_data['Revenue_Growth'].mean()
        avg_profit_growth = company_data['Profit_Growth'].mean()
        
        print(f"\n{company}:")
        print(f"  Average Revenue Growth: {avg_revenue_growth:.2f}%")
        print(f"  Average Profit Growth: {avg_profit_growth:.2f}%")
    
    print("\n")

# Example 3: Calculate average ROI
def example_3_average_roi():
    """Calculate average ROI for each company."""
    print("=" * 60)
    print("Example 3: Average Return on Investment (ROI)")
    print("مثال 3: متوسط عائد الاستثمار")
    print("=" * 60)
    
    df = load_data()
    
    avg_roi = df.groupby('Company')['ROI'].agg(['mean', 'min', 'max']).round(2)
    avg_roi.columns = ['Average ROI (%)', 'Min ROI (%)', 'Max ROI (%)']
    
    print("\nROI Statistics by Company:")
    print(avg_roi)
    print("\n")

# Example 4: Find most profitable months
def example_4_best_months():
    """Find the most profitable months for each company."""
    print("=" * 60)
    print("Example 4: Most Profitable Months")
    print("مثال 4: الأشهر الأكثر ربحية")
    print("=" * 60)
    
    df = load_data()
    
    for company in df['Company'].unique():
        company_data = df[df['Company'] == company]
        best_month = company_data.loc[company_data['Net_Profit'].idxmax()]
        
        print(f"\n{company}:")
        print(f"  Best Month: {best_month['Year']}-{best_month['Month']:02d}")
        print(f"  Revenue: ${best_month['Revenue']:,.0f}")
        print(f"  Net Profit: ${best_month['Net_Profit']:,.0f}")
        print(f"  Net Margin: {best_month['Net_Margin']:.2f}%")
    
    print("\n")

# Example 5: Cost analysis
def example_5_cost_analysis():
    """Analyze cost structure for each company."""
    print("=" * 60)
    print("Example 5: Cost Structure Analysis")
    print("مثال 5: تحليل هيكل التكاليف")
    print("=" * 60)
    
    df = load_data()
    
    for company in df['Company'].unique():
        company_data = df[df['Company'] == company]
        
        total_revenue = company_data['Revenue'].sum()
        total_costs = company_data['Costs'].sum()
        total_opex = company_data['Operating_Expenses'].sum()
        total_marketing = company_data['Marketing'].sum()
        total_rd = company_data['R&D'].sum()
        
        print(f"\n{company} - Cost Breakdown (% of Revenue):")
        print(f"  Production Costs: {(total_costs / total_revenue * 100):.2f}%")
        print(f"  Operating Expenses: {(total_opex / total_revenue * 100):.2f}%")
        print(f"  Marketing: {(total_marketing / total_revenue * 100):.2f}%")
        print(f"  R&D: {(total_rd / total_revenue * 100):.2f}%")
    
    print("\n")

# Example 6: Simple forecasting
def example_6_forecast():
    """Generate simple profit forecast."""
    print("=" * 60)
    print("Example 6: Profit Forecast (Next 3 Months)")
    print("مثال 6: توقع الأرباح (الأشهر الثلاثة القادمة)")
    print("=" * 60)
    
    df = load_data()
    
    for company in df['Company'].unique():
        company_data = df[df['Company'] == company].sort_values(['Year', 'Month'])
        
        # Get recent trend (last 6 months)
        recent_data = company_data.tail(6)
        
        # Calculate average growth rate
        profit_growth = recent_data['Net_Profit'].pct_change().mean()
        last_profit = company_data['Net_Profit'].iloc[-1]
        
        print(f"\n{company}:")
        print(f"  Last Month Profit: ${last_profit:,.0f}")
        print(f"  Average Growth Rate: {profit_growth * 100:.2f}%")
        print(f"  Forecasted Profits:")
        
        for month in range(1, 4):
            forecast_profit = last_profit * (1 + profit_growth) ** month
            print(f"    Month +{month}: ${forecast_profit:,.0f}")
    
    print("\n")

# Example 7: Compare companies
def example_7_company_comparison():
    """Compare key metrics across companies."""
    print("=" * 60)
    print("Example 7: Company Comparison")
    print("مثال 7: مقارنة الشركات")
    print("=" * 60)
    
    df = load_data()
    
    comparison = df.groupby('Company').agg({
        'Revenue': 'sum',
        'Net_Profit': 'sum',
        'Net_Margin': 'mean',
        'ROI': 'mean'
    }).round(2)
    
    comparison.columns = ['Total Revenue', 'Total Net Profit', 'Avg Net Margin (%)', 'Avg ROI (%)']
    
    # Calculate profitability score (simple example)
    comparison['Profitability Score'] = (
        comparison['Avg Net Margin (%)'] * 0.5 + 
        comparison['Avg ROI (%)'] * 0.5
    ).round(2)
    
    # Rank by profitability
    comparison = comparison.sort_values('Profitability Score', ascending=False)
    
    print("\nCompany Performance Comparison:")
    print(comparison)
    print("\n")

# Main execution
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("AUTOMATED PROFIT ANALYSIS - EXAMPLE USAGE")
    print("نظام تحليل الأرباح الآلي - أمثلة الاستخدام")
    print("=" * 60 + "\n")
    
    try:
        # Run all examples
        example_1_company_profits()
        example_2_growth_rates()
        example_3_average_roi()
        example_4_best_months()
        example_5_cost_analysis()
        example_6_forecast()
        example_7_company_comparison()
        
        print("=" * 60)
        print("All examples completed successfully! ✅")
        print("جميع الأمثلة اكتملت بنجاح! ✅")
        print("=" * 60 + "\n")
        
        print("Next steps:")
        print("1. Run 'streamlit run profit_analysis.py' for the full dashboard")
        print("2. Modify this script to analyze your own data")
        print("3. Check QUICKSTART.md for more information")
        print("\nالخطوات التالية:")
        print("1. شغّل 'streamlit run profit_analysis.py' للوحة التحكم الكاملة")
        print("2. عدّل هذا الملف لتحليل بياناتك الخاصة")
        print("3. راجع QUICKSTART.md للمزيد من المعلومات")
        
    except FileNotFoundError:
        print("Error: Could not find data/financial_data.csv")
        print("خطأ: لم يتم العثور على ملف data/financial_data.csv")
    except Exception as e:
        print(f"Error: {e}")
        print(f"خطأ: {e}")
