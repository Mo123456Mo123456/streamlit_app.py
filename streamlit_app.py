import streamlit as st
import pandas as pd
import math
from pathlib import Path

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='GDP dashboard',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_gdp_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)

    MIN_YEAR = 1960
    MAX_YEAR = 2022

    # The data above has columns like:
    # - Country Name
    # - Country Code
    # - [Stuff I don't care about]
    # - GDP for 1960
    # - GDP for 1961
    # - GDP for 1962
    # - ...
    # - GDP for 2022
    #
    # ...but I want this instead:
    # - Country Name
    # - Country Code
    # - Year
    # - GDP
    #
    # So let's pivot all those year-columns into two: Year and GDP
    gdp_df = raw_gdp_df.melt(
        ['Country Code'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'GDP',
    )

    # Convert years from string to integers
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])

    return gdp_df

@st.cache_data
def calculate_growth_rate(gdp_data, country_code, start_year, end_year):
    """Calculate annual growth rate for a country."""
    country_data = gdp_data[
        (gdp_data['Country Code'] == country_code) &
        (gdp_data['Year'] >= start_year) &
        (gdp_data['Year'] <= end_year)
    ].sort_values('Year')
    
    if len(country_data) < 2:
        return None
    
    country_data = country_data.dropna(subset=['GDP'])
    if len(country_data) < 2:
        return None
    
    first_gdp = country_data.iloc[0]['GDP']
    last_gdp = country_data.iloc[-1]['GDP']
    years = country_data.iloc[-1]['Year'] - country_data.iloc[0]['Year']
    
    if first_gdp <= 0 or years <= 0:
        return None
    
    # Calculate CAGR (Compound Annual Growth Rate)
    cagr = ((last_gdp / first_gdp) ** (1 / years)) - 1
    return cagr

def calculate_profit(investment_amount, growth_rate, years):
    """Calculate profit based on investment and growth rate."""
    if growth_rate is None or math.isnan(growth_rate):
        return None
    final_value = investment_amount * ((1 + growth_rate) ** years)
    profit = final_value - investment_amount
    return profit, final_value

def calculate_annual_profits(gdp_data, country_code, start_year, end_year, investment_amount):
    """Calculate annual profits for each year."""
    country_data = gdp_data[
        (gdp_data['Country Code'] == country_code) &
        (gdp_data['Year'] >= start_year) &
        (gdp_data['Year'] <= end_year)
    ].sort_values('Year').dropna(subset=['GDP'])
    
    if len(country_data) < 2:
        return None
    
    profits = []
    for i in range(1, len(country_data)):
        prev_gdp = country_data.iloc[i-1]['GDP']
        curr_gdp = country_data.iloc[i]['GDP']
        year = country_data.iloc[i]['Year']
        
        if prev_gdp > 0:
            growth_rate = (curr_gdp - prev_gdp) / prev_gdp
            year_profit = investment_amount * growth_rate
            cumulative_profit = investment_amount * ((curr_gdp / country_data.iloc[0]['GDP']) - 1)
            
            profits.append({
                'Year': year,
                'Growth Rate': growth_rate,
                'Annual Profit': year_profit,
                'Cumulative Profit': cumulative_profit,
                'Total Value': investment_amount + cumulative_profit
            })
    
    return pd.DataFrame(profits)

def predict_future_profits(gdp_data, country_code, start_year, end_year, investment_amount, future_years):
    """Predict future profits based on historical growth."""
    growth_rate = calculate_growth_rate(gdp_data, country_code, start_year, end_year)
    
    if growth_rate is None:
        return None
    
    predictions = []
    current_value = investment_amount
    
    for year in range(1, future_years + 1):
        future_year = end_year + year
        annual_profit = current_value * growth_rate
        current_value = current_value * (1 + growth_rate)
        cumulative_profit = current_value - investment_amount
        
        predictions.append({
            'Year': future_year,
            'Predicted Growth Rate': growth_rate,
            'Annual Profit': annual_profit,
            'Cumulative Profit': cumulative_profit,
            'Total Value': current_value
        })
    
    return pd.DataFrame(predictions)

gdp_df = get_gdp_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# 💰 نظام الأرباح الآلية المتكاملة - GDP Profit System

نظام متكامل لحساب الأرباح التلقائية بناءً على بيانات الناتج المحلي الإجمالي من [World Bank Open Data](https://data.worldbank.org/)
'''

# Add some spacing
''
''

min_value = gdp_df['Year'].min()
max_value = gdp_df['Year'].max()

from_year, to_year = st.slider(
    'Which years are you interested in?',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

countries = gdp_df['Country Code'].unique()

if not len(countries):
    st.warning("Select at least one country")

selected_countries = st.multiselect(
    'Which countries would you like to view?',
    countries,
    ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN'])

''
''
''

# Filter the data
filtered_gdp_df = gdp_df[
    (gdp_df['Country Code'].isin(selected_countries))
    & (gdp_df['Year'] <= to_year)
    & (from_year <= gdp_df['Year'])
]

st.header('GDP over time', divider='gray')

''

st.line_chart(
    filtered_gdp_df,
    x='Year',
    y='GDP',
    color='Country Code',
)

''
''


first_year = gdp_df[gdp_df['Year'] == from_year]
last_year = gdp_df[gdp_df['Year'] == to_year]

st.header(f'GDP in {to_year}', divider='gray')

''

cols = st.columns(4)

for i, country in enumerate(selected_countries):
    col = cols[i % len(cols)]

    with col:
        first_gdp = first_year[first_year['Country Code'] == country]['GDP'].iat[0] / 1000000000
        last_gdp = last_year[last_year['Country Code'] == country]['GDP'].iat[0] / 1000000000

        if math.isnan(first_gdp):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_gdp / first_gdp:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{country} GDP',
            value=f'{last_gdp:,.0f}B',
            delta=growth,
            delta_color=delta_color
        )

# -----------------------------------------------------------------------------
# Automated Profit System Section
st.header('💰 نظام الأرباح الآلية المتكاملة', divider='green')

st.subheader('⚙️ إعدادات الاستثمار التلقائي')

col1, col2 = st.columns(2)

with col1:
    investment_amount = st.number_input(
        '💰 مبلغ الاستثمار الأولي (بالدولار)',
        min_value=1000.0,
        max_value=1000000000.0,
        value=100000.0,
        step=10000.0,
        format='%.0f'
    )

with col2:
    profit_calculation_method = st.selectbox(
        '📊 طريقة حساب الأرباح',
        ['معدل النمو السنوي المركب (CAGR)', 'النمو السنوي الفعلي', 'متوسط النمو']
    )

st.markdown('---')

# Calculate and display profits for each selected country
if selected_countries and len(selected_countries) > 0:
    st.subheader('📈 تقرير الأرباح التلقائي')
    
    profit_summary = []
    
    for country in selected_countries:
        growth_rate = calculate_growth_rate(gdp_df, country, from_year, to_year)
        
        if growth_rate is not None and not math.isnan(growth_rate):
            years = to_year - from_year
            profit, final_value = calculate_profit(investment_amount, growth_rate, years)
            
            if profit is not None:
                profit_summary.append({
                    'البلد': country,
                    'معدل النمو السنوي': f'{growth_rate * 100:.2f}%',
                    'الأرباح التراكمية': f'${profit:,.2f}',
                    'القيمة النهائية': f'${final_value:,.2f}',
                    'العائد على الاستثمار': f'{(profit/investment_amount)*100:.2f}%'
                })
    
    if profit_summary:
        profit_df = pd.DataFrame(profit_summary)
        st.dataframe(profit_df, use_container_width=True, hide_index=True)
        
        # Display profit metrics
        st.subheader('💵 مؤشرات الأرباح الرئيسية')
        profit_cols = st.columns(len(selected_countries))
        
        for i, country in enumerate(selected_countries):
            if i < len(profit_summary):
                growth_rate = calculate_growth_rate(gdp_df, country, from_year, to_year)
                if growth_rate is not None:
                    years = to_year - from_year
                    profit, final_value = calculate_profit(investment_amount, growth_rate, years)
                    
                    with profit_cols[i]:
                        st.metric(
                            label=f'{country} - الأرباح',
                            value=f'${profit:,.0f}',
                            delta=f'{growth_rate*100:.2f}% معدل النمو',
                            delta_color='normal'
                        )
        
        # Annual profit breakdown
        st.subheader('📅 تفصيل الأرباح السنوية')
        
        selected_country_for_detail = st.selectbox(
            'اختر بلد لعرض التفاصيل السنوية',
            selected_countries
        )
        
        annual_profits = calculate_annual_profits(
            gdp_df, selected_country_for_detail, from_year, to_year, investment_amount
        )
        
        if annual_profits is not None and len(annual_profits) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.line_chart(
                    annual_profits.set_index('Year')[['Annual Profit', 'Cumulative Profit']],
                    height=300
                )
            
            with col2:
                st.bar_chart(
                    annual_profits.set_index('Year')['Growth Rate'] * 100,
                    height=300
                )
            
            st.dataframe(
                annual_profits.style.format({
                    'Growth Rate': '{:.2%}',
                    'Annual Profit': '${:,.2f}',
                    'Cumulative Profit': '${:,.2f}',
                    'Total Value': '${:,.2f}'
                }),
                use_container_width=True,
                hide_index=True
            )
        
        # Future profit predictions
        st.subheader('🔮 توقعات الأرباح المستقبلية')
        
        col1, col2 = st.columns(2)
        
        with col1:
            prediction_country = st.selectbox(
                'البلد للتنبؤ',
                selected_countries,
                key='prediction_country'
            )
        
        with col2:
            future_years = st.slider(
                'عدد السنوات المستقبلية',
                min_value=1,
                max_value=20,
                value=5
            )
        
        future_profits = predict_future_profits(
            gdp_df, prediction_country, from_year, to_year, investment_amount, future_years
        )
        
        if future_profits is not None and len(future_profits) > 0:
            st.line_chart(
                future_profits.set_index('Year')[['Annual Profit', 'Cumulative Profit', 'Total Value']],
                height=400
            )
            
            st.dataframe(
                future_profits.style.format({
                    'Predicted Growth Rate': '{:.2%}',
                    'Annual Profit': '${:,.2f}',
                    'Cumulative Profit': '${:,.2f}',
                    'Total Value': '${:,.2f}'
                }),
                use_container_width=True,
                hide_index=True
            )
            
            # Summary metrics
            final_predicted_value = future_profits.iloc[-1]['Total Value']
            total_predicted_profit = future_profits.iloc[-1]['Cumulative Profit']
            
            summary_cols = st.columns(3)
            with summary_cols[0]:
                st.metric(
                    'القيمة المتوقعة النهائية',
                    f'${final_predicted_value:,.0f}'
                )
            with summary_cols[1]:
                st.metric(
                    'إجمالي الأرباح المتوقعة',
                    f'${total_predicted_profit:,.0f}'
                )
            with summary_cols[2]:
                st.metric(
                    'العائد المتوقع',
                    f'{(total_predicted_profit/investment_amount)*100:.2f}%'
                )
    
    else:
        st.warning('⚠️ لا توجد بيانات كافية لحساب الأرباح للبلدان المحددة')

st.markdown('---')
st.info('💡 **ملاحظة**: هذه الحسابات تستند إلى بيانات الناتج المحلي الإجمالي التاريخية ولا تشكل نصيحة استثمارية.')
