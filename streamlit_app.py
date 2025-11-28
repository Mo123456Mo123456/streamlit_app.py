"""
🤖 AI-Powered Economic Analysis & Investment Insights Dashboard
Educational & Analysis Tool - NOT Financial Advice
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from ai_engine import EconomicAIAnalyzer

# Page configuration
st.set_page_config(
    page_title='AI Economic Analysis Dashboard',
    page_icon='🤖',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 2px solid #17a2b8;
        margin: 1rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 2px solid #28a745;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def get_gdp_data():
    """Load GDP data from CSV file"""
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)
    
    MIN_YEAR = 1960
    MAX_YEAR = 2022
    
    gdp_df = raw_gdp_df.melt(
        ['Country Code'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'GDP',
    )
    
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])
    
    return gdp_df

@st.cache_data
def get_country_names():
    """Load country names mapping"""
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)
    return dict(zip(raw_gdp_df['Country Code'], raw_gdp_df['Country Name']))

# Load data
gdp_df = get_gdp_data()
country_names = get_country_names()

# Initialize AI analyzer
ai_analyzer = EconomicAIAnalyzer(gdp_df)

# Sidebar
with st.sidebar:
    st.markdown("## 🤖 AI Analysis Dashboard")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["🏠 Overview", "📊 AI Analysis", "🎯 Investment Insights", "🔮 Predictions", "ℹ️ About"]
    )
    
    st.markdown("---")
    st.markdown("### ⚠️ Important Disclaimer")
    st.warning("This is an **EDUCATIONAL TOOL** only. NOT financial advice. Do not make investment decisions based on this tool.")

# Main content
if page == "🏠 Overview":
    st.markdown('<p class="main-header">🤖 AI Economic Analysis Dashboard</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h3>🎯 What This Tool Does</h3>
        <p>This is an <strong>AI-powered economic analysis platform</strong> that uses machine learning 
        to analyze global GDP data and generate automated insights. It demonstrates the capabilities 
        of AI in financial analysis.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="warning-box">
        <h3>⚠️ Critical Warning</h3>
        <p><strong>This tool is for EDUCATIONAL and RESEARCH purposes ONLY.</strong></p>
        <ul>
            <li>❌ NOT a system to "automatically generate profits"</li>
            <li>❌ NOT financial advice or investment recommendations</li>
            <li>❌ NOT connected to any trading systems</li>
            <li>✅ Educational analysis tool using historical data</li>
            <li>✅ Demonstrates AI/ML capabilities</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats
    st.markdown("### 📈 Global Economic Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    latest_year = gdp_df['Year'].max()
    latest_data = gdp_df[gdp_df['Year'] == latest_year]
    
    with col1:
        total_countries = gdp_df['Country Code'].nunique()
        st.metric("Countries Analyzed", total_countries)
    
    with col2:
        years_data = gdp_df['Year'].nunique()
        st.metric("Years of Data", years_data)
    
    with col3:
        total_gdp = latest_data['GDP'].sum() / 1e12
        st.metric("Global GDP", f"${total_gdp:.1f}T")
    
    with col4:
        st.metric("Latest Year", int(latest_year))
    
    # Top economies
    st.markdown("### 🌍 Top 10 Economies (Latest Year)")
    
    top_10 = latest_data.nlargest(10, 'GDP').copy()
    top_10['Country Name'] = top_10['Country Code'].map(country_names)
    top_10['GDP (Trillions)'] = top_10['GDP'] / 1e12
    
    fig = px.bar(
        top_10,
        x='Country Name',
        y='GDP (Trillions)',
        title=f'Top 10 Economies by GDP ({int(latest_year)})',
        color='GDP (Trillions)',
        color_continuous_scale='viridis'
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

elif page == "📊 AI Analysis":
    st.markdown('<p class="main-header">📊 AI-Powered Analysis</p>', unsafe_allow_html=True)
    
    st.markdown("### Select Countries for Analysis")
    
    countries = sorted(gdp_df['Country Code'].unique())
    default_countries = ['USA', 'CHN', 'JPN', 'DEU', 'GBR', 'IND', 'FRA', 'BRA']
    
    selected_countries = st.multiselect(
        'Choose countries to analyze (max 10):',
        countries,
        default=[c for c in default_countries if c in countries][:8],
        max_selections=10
    )
    
    if selected_countries:
        # Year range
        min_year = gdp_df['Year'].min()
        max_year = gdp_df['Year'].max()
        
        year_range = st.slider(
            'Select year range:',
            min_value=int(min_year),
            max_value=int(max_year),
            value=(int(max_year-30), int(max_year))
        )
        
        # Filter data
        filtered_df = gdp_df[
            (gdp_df['Country Code'].isin(selected_countries)) &
            (gdp_df['Year'] >= year_range[0]) &
            (gdp_df['Year'] <= year_range[1])
        ]
        
        # GDP Over Time Chart
        st.markdown("### 📈 GDP Trends Over Time")
        
        fig = go.Figure()
        
        for country in selected_countries:
            country_data = filtered_df[filtered_df['Country Code'] == country]
            country_name = country_names.get(country, country)
            
            fig.add_trace(go.Scatter(
                x=country_data['Year'],
                y=country_data['GDP'] / 1e9,
                mode='lines+markers',
                name=country_name,
                hovertemplate=f'<b>{country_name}</b><br>Year: %{{x}}<br>GDP: $%{{y:.2f}}B<extra></extra>'
            ))
        
        fig.update_layout(
            title='GDP Comparison Over Time',
            xaxis_title='Year',
            yaxis_title='GDP (Billions USD)',
            hovermode='x unified',
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # AI Comparison Table
        st.markdown("### 🤖 AI-Generated Comparison Analysis")
        
        with st.spinner('AI analyzing economic data...'):
            comparison_df = ai_analyzer.compare_countries(selected_countries)
        
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
        
        # Automated Insights
        st.markdown("### 💡 Automated AI Insights")
        
        insights = ai_analyzer.generate_automated_insights(selected_countries)
        
        for insight in insights:
            st.markdown(insight)

elif page == "🎯 Investment Insights":
    st.markdown('<p class="main-header">🎯 Investment Analysis (Educational)</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="warning-box">
        <strong>⚠️ Educational Only:</strong> These scores are generated by AI for learning purposes. 
        They do NOT constitute investment advice and should NOT be used for actual investment decisions.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Country Investment Attractiveness Scores")
    st.markdown("*AI-generated scores based on growth rate and economic stability*")
    
    # Calculate scores for all countries
    countries = gdp_df['Country Code'].unique()
    
    with st.spinner('AI calculating investment scores...'):
        scores_data = []
        
        for country in countries:
            score = ai_analyzer.generate_investment_score(country)
            if score is not None:
                growth = ai_analyzer.calculate_growth_rate(country, years=5)
                volatility = ai_analyzer.calculate_volatility(country, years=10)
                trend = ai_analyzer.detect_trends(country)
                
                scores_data.append({
                    'Country': country_names.get(country, country),
                    'Code': country,
                    'AI Score': score,
                    'Growth Rate (%)': growth,
                    'Volatility': volatility,
                    'Trend': trend
                })
        
        scores_df = pd.DataFrame(scores_data).sort_values('AI Score', ascending=False)
    
    # Top 20
    st.markdown("#### 🏆 Top 20 by AI Score")
    top_20 = scores_df.head(20)
    
    fig = px.bar(
        top_20,
        x='Country',
        y='AI Score',
        color='AI Score',
        color_continuous_scale='RdYlGn',
        title='Top 20 Countries by AI Investment Score',
        hover_data=['Growth Rate (%)', 'Volatility', 'Trend']
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed table
    st.markdown("#### 📋 Detailed Analysis Table")
    st.dataframe(
        scores_df.style.background_gradient(subset=['AI Score'], cmap='RdYlGn'),
        use_container_width=True,
        hide_index=True
    )
    
    # Risk-Return Scatter
    st.markdown("#### 📊 Risk vs Return Analysis")
    
    fig = px.scatter(
        scores_df,
        x='Volatility',
        y='Growth Rate (%)',
        size='AI Score',
        color='AI Score',
        hover_name='Country',
        color_continuous_scale='RdYlGn',
        title='Economic Risk vs Growth Rate',
        labels={'Volatility': 'Economic Volatility (Risk)', 'Growth Rate (%)': 'Growth Rate (Return)'}
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

elif page == "🔮 Predictions":
    st.markdown('<p class="main-header">🔮 AI Predictions (Educational)</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="warning-box">
        <strong>⚠️ Educational Predictions:</strong> These are ML-based projections for learning purposes only. 
        Economic predictions are inherently uncertain and should NOT be used for real decisions.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Future GDP Predictions")
    
    countries = sorted(gdp_df['Country Code'].unique())
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_country = st.selectbox(
            'Select country for prediction:',
            countries,
            index=countries.index('USA') if 'USA' in countries else 0
        )
    
    with col2:
        years_ahead = st.slider('Years to predict:', 1, 10, 5)
    
    if selected_country:
        country_name = country_names.get(selected_country, selected_country)
        
        # Get historical data
        historical = gdp_df[
            (gdp_df['Country Code'] == selected_country) &
            (gdp_df['GDP'].notna())
        ].sort_values('Year')
        
        # Get predictions
        with st.spinner(f'AI predicting future GDP for {country_name}...'):
            future_years, predictions, confidence = ai_analyzer.predict_future_gdp(
                selected_country,
                years_ahead
            )
        
        if predictions is not None:
            # Create visualization
            fig = go.Figure()
            
            # Historical data
            fig.add_trace(go.Scatter(
                x=historical['Year'],
                y=historical['GDP'] / 1e9,
                mode='lines+markers',
                name='Historical Data',
                line=dict(color='blue'),
                hovertemplate='Year: %{x}<br>GDP: $%{y:.2f}B<extra></extra>'
            ))
            
            # Predictions
            fig.add_trace(go.Scatter(
                x=future_years,
                y=predictions / 1e9,
                mode='lines+markers',
                name='AI Predictions',
                line=dict(color='red', dash='dash'),
                hovertemplate='Year: %{x}<br>Predicted GDP: $%{y:.2f}B<extra></extra>'
            ))
            
            fig.update_layout(
                title=f'GDP Prediction for {country_name}',
                xaxis_title='Year',
                yaxis_title='GDP (Billions USD)',
                height=600,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Prediction details
            st.markdown("### 📊 Prediction Details")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                current_gdp = historical.iloc[-1]['GDP'] / 1e9
                st.metric("Current GDP", f"${current_gdp:.1f}B")
            
            with col2:
                future_gdp = predictions[-1] / 1e9
                st.metric(f"Predicted GDP ({int(future_years[-1])})", f"${future_gdp:.1f}B")
            
            with col3:
                growth = ((predictions[-1] - historical.iloc[-1]['GDP']) / historical.iloc[-1]['GDP']) * 100
                st.metric("Predicted Growth", f"{growth:.1f}%")
            
            st.info(f"📈 Model Confidence Score: {confidence*100:.1f}% (based on historical fit)")
            
        else:
            st.warning("Insufficient data for predictions")

else:  # About page
    st.markdown('<p class="main-header">ℹ️ About This Tool</p>', unsafe_allow_html=True)
    
    st.markdown("""
    ## 🤖 AI Economic Analysis Dashboard
    
    ### What is this?
    
    This is an **educational demonstration** of AI and machine learning capabilities applied to economic analysis. 
    It uses real historical GDP data from the World Bank to generate insights, predictions, and analysis.
    
    ### 🛠️ Technologies Used
    
    - **Python** - Programming language
    - **Streamlit** - Web application framework
    - **Scikit-learn** - Machine learning library
    - **Pandas & NumPy** - Data analysis
    - **Plotly** - Interactive visualizations
    
    ### 🧠 AI Features
    
    1. **Growth Rate Analysis** - Calculates compound annual growth rates (CAGR)
    2. **Volatility Detection** - Measures economic stability
    3. **Trend Analysis** - Identifies economic trends using statistical methods
    4. **ML Predictions** - Uses linear regression to project future GDP
    5. **Investment Scoring** - Generates educational scores based on multiple factors
    6. **Automated Insights** - AI-generated analysis of economic data
    
    ### ⚠️ Important Disclaimers
    """)
    
    st.markdown("""
    <div class="warning-box">
        <h4>This Tool is NOT:</h4>
        <ul>
            <li>❌ A system to "automatically generate profits"</li>
            <li>❌ Financial advice or investment recommendations</li>
            <li>❌ Connected to any real trading or financial systems</li>
            <li>❌ Guaranteed to be accurate - predictions are estimates</li>
            <li>❌ A replacement for professional financial advisors</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="success-box">
        <h4>This Tool IS:</h4>
        <ul>
            <li>✅ An educational platform for learning about AI in finance</li>
            <li>✅ A demonstration of machine learning techniques</li>
            <li>✅ A tool for exploring economic data</li>
            <li>✅ Useful for research and educational purposes</li>
            <li>✅ Open source and transparent</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 📚 Data Source
    
    - **GDP Data**: World Bank Open Data (https://data.worldbank.org/)
    - **Years Covered**: 1960-2022
    - **Update Frequency**: Data is historical and not real-time
    
    ### 🔒 Ethics & Responsibility
    
    **There is no such thing as a legitimate "automatic profit generation system."** 
    Any tool claiming to automatically generate guaranteed profits is misleading or fraudulent. 
    
    This tool is designed to:
    - Educate about AI and machine learning
    - Demonstrate data analysis techniques
    - Promote transparency in AI systems
    - Encourage critical thinking about economic data
    
    **Always:**
    - Consult with qualified financial professionals
    - Do your own research
    - Understand the risks before investing
    - Be skeptical of "get rich quick" schemes
    
    ### 📖 License
    
    Open source - for educational and research purposes
    
    ### 💬 Feedback
    
    This tool was created as an educational alternative to unrealistic "automatic profit" systems.
    It demonstrates what AI can actually do (analysis and insights) vs. what it cannot do (guarantee profits).
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🤖 AI Economic Analysis Dashboard | Educational Tool Only | Not Financial Advice</p>
    <p>Data source: World Bank Open Data | Created with Streamlit + Python</p>
</div>
""", unsafe_allow_html=True)
