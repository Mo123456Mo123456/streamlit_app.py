import streamlit as st
import pandas as pd
import math
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='نظام الأرباح الآلي المتكامل | Automated Profit System',
    page_icon='💰',
    layout='wide',
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_gdp_data():
    """Grab GDP data from a CSV file."""
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)

    MIN_YEAR = 1960
    MAX_YEAR = 2022

    gdp_df = raw_gdp_df.melt(
        ['Country Name', 'Country Code'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'GDP',
    )

    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])
    gdp_df['GDP'] = pd.to_numeric(gdp_df['GDP'], errors='coerce')

    return gdp_df

def calculate_growth_rate(df, country_code, years=5):
    """Calculate average GDP growth rate for a country."""
    country_data = df[df['Country Code'] == country_code].sort_values('Year')
    country_data = country_data.dropna(subset=['GDP'])
    
    if len(country_data) < 2:
        return 0
    
    recent_data = country_data.tail(years)
    if len(recent_data) < 2:
        recent_data = country_data.tail(min(10, len(country_data)))
    
    growth_rates = []
    for i in range(1, len(recent_data)):
        prev_gdp = recent_data.iloc[i-1]['GDP']
        curr_gdp = recent_data.iloc[i]['GDP']
        if prev_gdp > 0 and not math.isnan(prev_gdp) and not math.isnan(curr_gdp):
            growth_rate = (curr_gdp - prev_gdp) / prev_gdp * 100
            growth_rates.append(growth_rate)
    
    return np.mean(growth_rates) if growth_rates else 0

def calculate_profit(investment, growth_rate, years, compound=True):
    """Calculate potential profit from investment."""
    if compound:
        final_value = investment * ((1 + growth_rate/100) ** years)
    else:
        final_value = investment * (1 + (growth_rate/100) * years)
    profit = final_value - investment
    return profit, final_value

def generate_trading_signals(df, country_code):
    """Generate automated trading signals based on GDP trends."""
    country_data = df[df['Country Code'] == country_code].sort_values('Year')
    country_data = country_data.dropna(subset=['GDP'])
    
    if len(country_data) < 5:
        return "لا توجد بيانات كافية", "gray"
    
    recent = country_data.tail(5)
    short_term_growth = calculate_growth_rate(df, country_code, 3)
    long_term_growth = calculate_growth_rate(df, country_code, 10)
    
    # Calculate volatility
    gdp_values = recent['GDP'].values
    volatility = np.std(np.diff(gdp_values) / gdp_values[:-1]) * 100 if len(gdp_values) > 1 else 0
    
    # Signal logic
    if short_term_growth > 5 and long_term_growth > 3 and volatility < 10:
        return "إشارة شراء قوية 🟢", "green"
    elif short_term_growth > 2 and long_term_growth > 1:
        return "إشارة شراء 🟡", "normal"
    elif short_term_growth < -2 or volatility > 20:
        return "إشارة بيع 🔴", "red"
    else:
        return "انتظار ⚪", "gray"

def calculate_risk_score(df, country_code):
    """Calculate risk score (0-100, lower is better)."""
    country_data = df[df['Country Code'] == country_code].sort_values('Year')
    country_data = country_data.dropna(subset=['GDP'])
    
    if len(country_data) < 3:
        return 50
    
    recent = country_data.tail(10)
    gdp_values = recent['GDP'].values
    
    # Volatility component
    if len(gdp_values) > 1:
        returns = np.diff(gdp_values) / gdp_values[:-1]
        volatility = np.std(returns) * 100
    else:
        volatility = 0
    
    # Growth consistency
    growth_rates = []
    for i in range(1, len(recent)):
        if recent.iloc[i-1]['GDP'] > 0:
            gr = (recent.iloc[i]['GDP'] - recent.iloc[i-1]['GDP']) / recent.iloc[i-1]['GDP'] * 100
            growth_rates.append(gr)
    
    consistency = np.std(growth_rates) if growth_rates else 50
    
    # Combine factors
    risk_score = min(100, max(0, volatility * 2 + consistency))
    return risk_score

gdp_df = get_gdp_data()

# -----------------------------------------------------------------------------
# Main Application - نظام الأرباح الآلي المتكامل

st.title('💰 نظام الأرباح الآلي المتكامل')
st.markdown('### Automated Integrated Profit System')
st.markdown('---')

# Sidebar for investment parameters
with st.sidebar:
    st.header('⚙️ إعدادات الاستثمار')
    
    investment_amount = st.number_input(
        'مبلغ الاستثمار ($)',
        min_value=1000,
        max_value=1000000000,
        value=100000,
        step=10000,
        format='%d'
    )
    
    investment_years = st.slider(
        'مدة الاستثمار (سنوات)',
        min_value=1,
        max_value=20,
        value=5,
        step=1
    )
    
    compound_interest = st.checkbox('فائدة مركبة', value=True)
    
    st.markdown('---')
    st.header('📊 تحليل البيانات')
    
    min_value = gdp_df['Year'].min()
    max_value = gdp_df['Year'].max()
    
    from_year, to_year = st.slider(
        'نطاق السنوات',
        min_value=int(min_value),
        max_value=int(max_value),
        value=[int(min_value), int(max_value)]
    )

# Country selection (available for all tabs)
countries = gdp_df['Country Code'].unique()
selected_countries = st.multiselect(
    'اختر الدول للتحليل',
    countries,
    ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN', 'USA', 'CHN']
)

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs([
    '📈 لوحة الأرباح الرئيسية',
    '🎯 إشارات التداول الآلية',
    '📊 تحليل الأداء',
    '🌍 مقارنة الدول'
])

with tab1:
    st.header('💰 حساب الأرباح التلقائي')
    
    if len(selected_countries) > 0:
        st.markdown('---')
        
        # Calculate profits for each country
        profit_data = []
        
        for country in selected_countries:
            growth_rate = calculate_growth_rate(gdp_df, country)
            profit, final_value = calculate_profit(
                investment_amount,
                growth_rate,
                investment_years,
                compound_interest
            )
            risk_score = calculate_risk_score(gdp_df, country)
            signal, signal_color = generate_trading_signals(gdp_df, country)
            
            country_name = gdp_df[gdp_df['Country Code'] == country]['Country Name'].iloc[0] if len(gdp_df[gdp_df['Country Code'] == country]) > 0 else country
            
            profit_data.append({
                'Country': country,
                'Country Name': country_name,
                'Growth Rate': growth_rate,
                'Profit': profit,
                'Final Value': final_value,
                'ROI': (profit / investment_amount) * 100,
                'Risk Score': risk_score,
                'Signal': signal
            })
        
        profit_df = pd.DataFrame(profit_data)
        profit_df = profit_df.sort_values('Profit', ascending=False)
        
        # Display top performers
        st.subheader('🏆 أفضل الفرص الاستثمارية')
        
        cols = st.columns(min(4, len(profit_df)))
        for idx, row in profit_df.head(4).iterrows():
            col_idx = profit_df.index.get_loc(idx) % len(cols)
            with cols[col_idx]:
                roi_color = 'normal' if row['ROI'] > 0 else 'inverse'
                st.metric(
                    label=f"{row['Country']} - {row['Country Name'][:20]}",
                    value=f"${row['Final Value']:,.0f}",
                    delta=f"{row['ROI']:.1f}% ROI",
                    delta_color=roi_color
                )
                st.caption(f"نمو سنوي: {row['Growth Rate']:.2f}%")
                st.caption(f"مخاطر: {row['Risk Score']:.1f}/100")
        
        # Detailed table
        st.markdown('---')
        st.subheader('📋 جدول تفصيلي للأرباح')
        
        display_df = profit_df[['Country', 'Country Name', 'Growth Rate', 'Profit', 'Final Value', 'ROI', 'Risk Score', 'Signal']].copy()
        display_df['Growth Rate'] = display_df['Growth Rate'].apply(lambda x: f"{x:.2f}%")
        display_df['Profit'] = display_df['Profit'].apply(lambda x: f"${x:,.0f}")
        display_df['Final Value'] = display_df['Final Value'].apply(lambda x: f"${x:,.0f}")
        display_df['ROI'] = display_df['ROI'].apply(lambda x: f"{x:.2f}%")
        display_df['Risk Score'] = display_df['Risk Score'].apply(lambda x: f"{x:.1f}")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Profit visualization
        st.markdown('---')
        st.subheader('📊 تصور الأرباح المتوقعة')
        
        fig = go.Figure()
        
        for _, row in profit_df.iterrows():
            years_range = np.arange(0, investment_years + 1)
            if compound_interest:
                values = investment_amount * ((1 + row['Growth Rate']/100) ** years_range)
            else:
                values = investment_amount * (1 + (row['Growth Rate']/100) * years_range)
            
            fig.add_trace(go.Scatter(
                x=years_range,
                y=values,
                mode='lines+markers',
                name=f"{row['Country']} ({row['Growth Rate']:.2f}%)",
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title='نمو الاستثمار عبر الزمن',
            xaxis_title='السنوات',
            yaxis_title='قيمة الاستثمار ($)',
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning('يرجى اختيار دولة واحدة على الأقل من القائمة أعلاه')

with tab2:
    st.header('🎯 إشارات التداول الآلية')
    
    if len(selected_countries) > 0:
        st.info('💡 يتم توليد الإشارات تلقائياً بناءً على تحليل اتجاهات الناتج المحلي الإجمالي')
        
        signal_cols = st.columns(3)
        
        for idx, country in enumerate(selected_countries):
            col = signal_cols[idx % 3]
            
            with col:
                signal, signal_color = generate_trading_signals(gdp_df, country)
                growth_rate = calculate_growth_rate(gdp_df, country)
                risk_score = calculate_risk_score(gdp_df, country)
                
                country_name = gdp_df[gdp_df['Country Code'] == country]['Country Name'].iloc[0] if len(gdp_df[gdp_df['Country Code'] == country]) > 0 else country
                
                st.markdown(f"### {country}")
                st.markdown(f"**{country_name}**")
                
                if signal_color == 'green':
                    st.success(signal)
                elif signal_color == 'red':
                    st.error(signal)
                elif signal_color == 'normal':
                    st.warning(signal)
                else:
                    st.info(signal)
                
                st.metric('معدل النمو', f"{growth_rate:.2f}%")
                st.metric('مستوى المخاطر', f"{risk_score:.1f}/100")
                
                # Risk indicator
                if risk_score < 20:
                    risk_level = "منخفضة جداً 🟢"
                elif risk_score < 40:
                    risk_level = "منخفضة 🟡"
                elif risk_score < 60:
                    risk_level = "متوسطة 🟠"
                else:
                    risk_level = "عالية 🔴"
                
                st.caption(f"المخاطر: {risk_level}")
                st.markdown('---')
    else:
        st.warning('يرجى اختيار دولة واحدة على الأقل من القائمة أعلاه')

with tab3:
    st.header('📊 تحليل الأداء التفصيلي')
    
    if len(selected_countries) > 0:
        analysis_country = st.selectbox(
            'اختر دولة للتحليل التفصيلي',
            selected_countries
        )
        
        country_data = gdp_df[
            (gdp_df['Country Code'] == analysis_country) &
            (gdp_df['Year'] >= from_year) &
            (gdp_df['Year'] <= to_year)
        ].sort_values('Year')
        country_data = country_data.dropna(subset=['GDP'])
        
        if len(country_data) > 0:
            country_name = country_data['Country Name'].iloc[0]
            
            st.subheader(f'تحليل {country_name} ({analysis_country})')
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                latest_gdp = country_data.iloc[-1]['GDP'] / 1e9
                st.metric('الناتج المحلي الحالي', f"${latest_gdp:,.0f}B")
            
            with col2:
                growth_rate = calculate_growth_rate(gdp_df, analysis_country)
                st.metric('معدل النمو السنوي', f"{growth_rate:.2f}%")
            
            with col3:
                risk_score = calculate_risk_score(gdp_df, analysis_country)
                st.metric('مستوى المخاطر', f"{risk_score:.1f}/100")
            
            with col4:
                profit, final_value = calculate_profit(
                    investment_amount,
                    growth_rate,
                    investment_years,
                    compound_interest
                )
                st.metric('الأرباح المتوقعة', f"${profit:,.0f}")
            
            # GDP trend chart
            st.markdown('---')
            st.subheader('اتجاه الناتج المحلي الإجمالي')
            
            fig = px.line(
                country_data,
                x='Year',
                y='GDP',
                title=f'نمو الناتج المحلي الإجمالي - {country_name}',
                markers=True
            )
            fig.update_layout(
                xaxis_title='السنة',
                yaxis_title='الناتج المحلي الإجمالي ($)',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Growth rate over time
            st.markdown('---')
            st.subheader('معدل النمو عبر الزمن')
            
            growth_rates = []
            years = []
            for i in range(1, len(country_data)):
                prev_gdp = country_data.iloc[i-1]['GDP']
                curr_gdp = country_data.iloc[i]['GDP']
                if prev_gdp > 0:
                    gr = (curr_gdp - prev_gdp) / prev_gdp * 100
                    growth_rates.append(gr)
                    years.append(country_data.iloc[i]['Year'])
            
            if growth_rates:
                growth_df = pd.DataFrame({'Year': years, 'Growth Rate': growth_rates})
                fig2 = px.bar(
                    growth_df,
                    x='Year',
                    y='Growth Rate',
                    title='معدل النمو السنوي',
                    color='Growth Rate',
                    color_continuous_scale='RdYlGn'
                )
                fig2.update_layout(height=400)
                fig2.add_hline(y=0, line_dash="dash", line_color="gray")
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning('لا توجد بيانات كافية للدولة المختارة')
    else:
        st.warning('يرجى اختيار دولة واحدة على الأقل من القائمة أعلاه')

with tab4:
    st.header('🌍 مقارنة بين الدول')
    
    if len(selected_countries) >= 2:
        # Filter data
        filtered_gdp_df = gdp_df[
            (gdp_df['Country Code'].isin(selected_countries)) &
            (gdp_df['Year'] <= to_year) &
            (from_year <= gdp_df['Year'])
        ]
        
        st.subheader('مقارنة الناتج المحلي الإجمالي')
        
        fig = px.line(
            filtered_gdp_df,
            x='Year',
            y='GDP',
            color='Country Code',
            title='مقارنة الناتج المحلي الإجمالي بين الدول',
            markers=True
        )
        fig.update_layout(
            xaxis_title='السنة',
            yaxis_title='الناتج المحلي الإجمالي ($)',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Comparison table
        st.markdown('---')
        st.subheader('جدول المقارنة')
        
        comparison_data = []
        for country in selected_countries:
            growth_rate = calculate_growth_rate(gdp_df, country)
            profit, final_value = calculate_profit(
                investment_amount,
                growth_rate,
                investment_years,
                compound_interest
            )
            risk_score = calculate_risk_score(gdp_df, country)
            
            country_name = gdp_df[gdp_df['Country Code'] == country]['Country Name'].iloc[0] if len(gdp_df[gdp_df['Country Code'] == country]) > 0 else country
            
            comparison_data.append({
                'الدولة': country_name,
                'الكود': country,
                'معدل النمو (%)': f"{growth_rate:.2f}",
                'الأرباح ($)': f"{profit:,.0f}",
                'القيمة النهائية ($)': f"{final_value:,.0f}",
                'العائد (%)': f"{(profit/investment_amount)*100:.2f}",
                'المخاطر': f"{risk_score:.1f}"
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    else:
        st.warning('يرجى اختيار دولتين على الأقل للمقارنة')

# Footer
st.markdown('---')
st.markdown('''
<div style="text-align: center; color: gray;">
    <p>نظام الأرباح الآلي المتكامل | Automated Integrated Profit System</p>
    <p>⚠️ تنبيه: هذا النظام للتحليل التعليمي فقط. استشر مستشاراً مالياً قبل اتخاذ قرارات استثمارية.</p>
</div>
''', unsafe_allow_html=True)
