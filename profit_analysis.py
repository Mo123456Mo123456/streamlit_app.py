import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title='💰 نظام الأرباح الآلي المتكامل',
    page_icon='💰',
    layout='wide'
)

# -----------------------------------------------------------------------------
# Data Loading and Caching
# -----------------------------------------------------------------------------

@st.cache_data
def load_financial_data():
    """Load financial data from CSV file."""
    DATA_FILENAME = Path(__file__).parent / 'data/financial_data.csv'
    df = pd.read_csv(DATA_FILENAME)
    
    # Calculate automated profit metrics
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
    
    # Create date column
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month'].astype(str) + '-01')
    
    return df

# -----------------------------------------------------------------------------
# Automated Profit Forecasting
# -----------------------------------------------------------------------------

def forecast_profits(df, company, periods=6):
    """Generate automated profit forecasts using trend analysis."""
    company_data = df[df['Company'] == company].sort_values('Date')
    
    if len(company_data) < 3:
        return None
    
    # Get recent trend
    recent_data = company_data.tail(6)
    
    # Calculate average growth rates
    revenue_growth = recent_data['Revenue'].pct_change().mean()
    profit_growth = recent_data['Net_Profit'].pct_change().mean()
    
    # Generate forecasts
    last_date = company_data['Date'].max()
    last_revenue = company_data['Revenue'].iloc[-1]
    last_profit = company_data['Net_Profit'].iloc[-1]
    
    forecasts = []
    for i in range(1, periods + 1):
        forecast_date = last_date + timedelta(days=30 * i)
        forecast_revenue = last_revenue * (1 + revenue_growth) ** i
        forecast_profit = last_profit * (1 + profit_growth) ** i
        
        forecasts.append({
            'Date': forecast_date,
            'Revenue_Forecast': forecast_revenue,
            'Profit_Forecast': forecast_profit,
            'Type': 'Forecast'
        })
    
    return pd.DataFrame(forecasts)

# -----------------------------------------------------------------------------
# Load Data
# -----------------------------------------------------------------------------

df = load_financial_data()

# -----------------------------------------------------------------------------
# Main Dashboard
# -----------------------------------------------------------------------------

st.title('💰 نظام الأرباح الآلي المتكامل')
st.markdown('### Real Integrated Automated Profit System')

st.markdown("""
هذا النظام يوفر تحليلاً شاملاً ومتكاملاً للأرباح مع حسابات آلية في الوقت الفعلي
#### Automated Features:
- 📊 Real-time profit calculations
- 📈 Automated growth analysis
- 🎯 ROI tracking
- 🔮 Profit forecasting
- 💹 Comprehensive financial metrics
""")

st.markdown("---")

# -----------------------------------------------------------------------------
# Sidebar Filters
# -----------------------------------------------------------------------------

st.sidebar.header('⚙️ إعدادات التحليل | Settings')

# Company selection
companies = df['Company'].unique()
selected_companies = st.sidebar.multiselect(
    '🏢 اختر الشركات | Select Companies',
    companies,
    default=companies.tolist()
)

# Date range
min_date = df['Date'].min()
max_date = df['Date'].max()

date_range = st.sidebar.date_input(
    '📅 نطاق التاريخ | Date Range',
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Metric selection
st.sidebar.subheader('📊 المقاييس المالية | Financial Metrics')
show_revenue = st.sidebar.checkbox('الإيرادات | Revenue', value=True)
show_gross_profit = st.sidebar.checkbox('الربح الإجمالي | Gross Profit', value=True)
show_net_profit = st.sidebar.checkbox('صافي الربح | Net Profit', value=True)
show_roi = st.sidebar.checkbox('عائد الاستثمار | ROI', value=True)

# Forecast settings
st.sidebar.subheader('🔮 إعدادات التنبؤ | Forecast Settings')
enable_forecast = st.sidebar.checkbox('تفعيل التنبؤات | Enable Forecasts', value=True)
forecast_periods = st.sidebar.slider('عدد الأشهر للتنبؤ | Forecast Months', 1, 12, 6)

# Filter data
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[
        (df['Company'].isin(selected_companies)) &
        (df['Date'] >= pd.to_datetime(start_date)) &
        (df['Date'] <= pd.to_datetime(end_date))
    ]
else:
    filtered_df = df[df['Company'].isin(selected_companies)]

# -----------------------------------------------------------------------------
# Key Metrics Overview
# -----------------------------------------------------------------------------

st.header('📊 المؤشرات الرئيسية | Key Performance Indicators')

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_revenue = filtered_df['Revenue'].sum()
    revenue_change = filtered_df.groupby('Company')['Revenue'].sum().pct_change().mean() * 100
    st.metric(
        label="إجمالي الإيرادات | Total Revenue",
        value=f"${total_revenue:,.0f}",
        delta=f"{revenue_change:.1f}%" if not np.isnan(revenue_change) else "N/A"
    )

with col2:
    total_net_profit = filtered_df['Net_Profit'].sum()
    profit_change = filtered_df.groupby('Company')['Net_Profit'].sum().pct_change().mean() * 100
    st.metric(
        label="صافي الربح | Net Profit",
        value=f"${total_net_profit:,.0f}",
        delta=f"{profit_change:.1f}%" if not np.isnan(profit_change) else "N/A"
    )

with col3:
    avg_margin = filtered_df['Net_Margin'].mean()
    st.metric(
        label="متوسط هامش الربح | Avg Net Margin",
        value=f"{avg_margin:.1f}%"
    )

with col4:
    avg_roi = filtered_df['ROI'].mean()
    st.metric(
        label="متوسط ROI | Average ROI",
        value=f"{avg_roi:.1f}%"
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# Revenue and Profit Trends
# -----------------------------------------------------------------------------

st.header('📈 اتجاهات الإيرادات والأرباح | Revenue & Profit Trends')

# Create tabs for different views
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 الأرباح | Profits", 
    "💰 الإيرادات | Revenue",
    "📉 الهوامش | Margins",
    "🔮 التنبؤات | Forecasts"
])

with tab1:
    fig = go.Figure()
    
    for company in selected_companies:
        company_data = filtered_df[filtered_df['Company'] == company]
        
        if show_gross_profit:
            fig.add_trace(go.Scatter(
                x=company_data['Date'],
                y=company_data['Gross_Profit'],
                name=f'{company} - Gross Profit',
                mode='lines+markers',
                line=dict(width=2)
            ))
        
        if show_net_profit:
            fig.add_trace(go.Scatter(
                x=company_data['Date'],
                y=company_data['Net_Profit'],
                name=f'{company} - Net Profit',
                mode='lines+markers',
                line=dict(width=2, dash='dash')
            ))
    
    fig.update_layout(
        title='تحليل الأرباح الآلي | Automated Profit Analysis',
        xaxis_title='التاريخ | Date',
        yaxis_title='الربح | Profit ($)',
        hovermode='x unified',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig = px.line(
        filtered_df,
        x='Date',
        y='Revenue',
        color='Company',
        title='اتجاه الإيرادات | Revenue Trend',
        markers=True
    )
    fig.update_layout(
        xaxis_title='التاريخ | Date',
        yaxis_title='الإيرادات | Revenue ($)',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    fig = go.Figure()
    
    for company in selected_companies:
        company_data = filtered_df[filtered_df['Company'] == company]
        
        fig.add_trace(go.Scatter(
            x=company_data['Date'],
            y=company_data['Net_Margin'],
            name=f'{company} - Net Margin',
            mode='lines+markers'
        ))
        
        fig.add_trace(go.Scatter(
            x=company_data['Date'],
            y=company_data['Operating_Margin'],
            name=f'{company} - Operating Margin',
            mode='lines',
            line=dict(dash='dot')
        ))
    
    fig.update_layout(
        title='هوامش الربح | Profit Margins',
        xaxis_title='التاريخ | Date',
        yaxis_title='الهامش | Margin (%)',
        hovermode='x unified',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    if enable_forecast:
        st.subheader('🔮 التنبؤ الآلي بالأرباح | Automated Profit Forecasting')
        
        for company in selected_companies:
            st.markdown(f"#### {company}")
            
            company_data = filtered_df[filtered_df['Company'] == company]
            forecasts = forecast_profits(df, company, forecast_periods)
            
            if forecasts is not None:
                fig = go.Figure()
                
                # Historical data
                fig.add_trace(go.Scatter(
                    x=company_data['Date'],
                    y=company_data['Net_Profit'],
                    name='Historical Net Profit',
                    mode='lines+markers',
                    line=dict(color='blue', width=2)
                ))
                
                # Forecast data
                fig.add_trace(go.Scatter(
                    x=forecasts['Date'],
                    y=forecasts['Profit_Forecast'],
                    name='Forecasted Net Profit',
                    mode='lines+markers',
                    line=dict(color='red', width=2, dash='dash')
                ))
                
                fig.update_layout(
                    title=f'التنبؤ بالأرباح - {company} | Profit Forecast - {company}',
                    xaxis_title='التاريخ | Date',
                    yaxis_title='صافي الربح | Net Profit ($)',
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show forecast table
                forecast_display = forecasts.copy()
                forecast_display['Date'] = forecast_display['Date'].dt.strftime('%Y-%m')
                forecast_display['Revenue_Forecast'] = forecast_display['Revenue_Forecast'].apply(lambda x: f"${x:,.0f}")
                forecast_display['Profit_Forecast'] = forecast_display['Profit_Forecast'].apply(lambda x: f"${x:,.0f}")
                st.dataframe(forecast_display, hide_index=True)
            else:
                st.warning(f'Not enough data for {company} to generate forecasts.')
    else:
        st.info('Enable forecasts in the sidebar to see automated profit predictions.')

st.markdown("---")

# -----------------------------------------------------------------------------
# ROI Analysis
# -----------------------------------------------------------------------------

if show_roi:
    st.header('💹 تحليل عائد الاستثمار | ROI Analysis')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # ROI over time
        fig = px.line(
            filtered_df,
            x='Date',
            y='ROI',
            color='Company',
            title='عائد الاستثمار عبر الزمن | ROI Over Time',
            markers=True
        )
        fig.update_layout(
            xaxis_title='التاريخ | Date',
            yaxis_title='ROI (%)',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Average ROI by company
        avg_roi_by_company = filtered_df.groupby('Company')['ROI'].mean().reset_index()
        fig = px.bar(
            avg_roi_by_company,
            x='Company',
            y='ROI',
            title='متوسط ROI حسب الشركة | Average ROI by Company',
            color='ROI',
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(
            xaxis_title='الشركة | Company',
            yaxis_title='متوسط ROI | Average ROI (%)',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# Cost Breakdown Analysis
# -----------------------------------------------------------------------------

st.header('💸 تحليل التكاليف | Cost Breakdown Analysis')

for company in selected_companies:
    with st.expander(f"📊 {company} - تفصيل التكاليف | Cost Details"):
        company_data = filtered_df[filtered_df['Company'] == company]
        
        # Calculate totals
        total_costs = company_data['Costs'].sum()
        total_opex = company_data['Operating_Expenses'].sum()
        total_marketing = company_data['Marketing'].sum()
        total_rd = company_data['R&D'].sum()
        total_taxes = company_data['Taxes'].sum()
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=['Production Costs', 'Operating Expenses', 'Marketing', 'R&D', 'Taxes'],
            values=[total_costs, total_opex, total_marketing, total_rd, total_taxes],
            hole=.3
        )])
        
        fig.update_layout(
            title=f'توزيع التكاليف | Cost Distribution - {company}',
            height=400
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 📊 Cost Summary")
            st.metric("Production Costs", f"${total_costs:,.0f}")
            st.metric("Operating Expenses", f"${total_opex:,.0f}")
            st.metric("Marketing", f"${total_marketing:,.0f}")
            st.metric("R&D", f"${total_rd:,.0f}")
            st.metric("Taxes", f"${total_taxes:,.0f}")

st.markdown("---")

# -----------------------------------------------------------------------------
# Detailed Data Table
# -----------------------------------------------------------------------------

st.header('📋 البيانات التفصيلية | Detailed Data')

# Format the dataframe for display
display_df = filtered_df.copy()
display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m')

# Select columns to display
columns_to_display = [
    'Date', 'Company', 'Revenue', 'Gross_Profit', 'Operating_Profit', 
    'Net_Profit', 'Gross_Margin', 'Net_Margin', 'ROI'
]

display_df = display_df[columns_to_display]

# Format numeric columns
for col in ['Revenue', 'Gross_Profit', 'Operating_Profit', 'Net_Profit']:
    display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")

for col in ['Gross_Margin', 'Net_Margin', 'ROI']:
    display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}%")

st.dataframe(display_df, hide_index=True, use_container_width=True)

# Download button
csv = filtered_df.to_csv(index=False)
st.download_button(
    label="📥 تحميل البيانات | Download Data CSV",
    data=csv,
    file_name=f"profit_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>💰 <strong>نظام الأرباح الآلي المتكامل</strong> | Real Integrated Automated Profit System</p>
    <p>تحليل شامل ودقيق في الوقت الفعلي | Comprehensive Real-Time Analysis</p>
</div>
""", unsafe_allow_html=True)
