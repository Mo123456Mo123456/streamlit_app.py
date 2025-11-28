"""
AI-Powered Economic Analysis Engine
Educational purposes only - Not financial advice
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class EconomicAIAnalyzer:
    """AI-powered economic analysis engine using machine learning"""
    
    def __init__(self, gdp_df):
        self.gdp_df = gdp_df
        self.scaler = StandardScaler()
        
    def calculate_growth_rate(self, country_code, years=5):
        """Calculate compound annual growth rate (CAGR)"""
        country_data = self.gdp_df[self.gdp_df['Country Code'] == country_code].sort_values('Year')
        
        if len(country_data) < 2:
            return None
            
        recent_data = country_data.tail(years)
        if len(recent_data) < 2:
            return None
            
        start_gdp = recent_data.iloc[0]['GDP']
        end_gdp = recent_data.iloc[-1]['GDP']
        n_years = recent_data.iloc[-1]['Year'] - recent_data.iloc[0]['Year']
        
        if start_gdp <= 0 or end_gdp <= 0 or n_years <= 0:
            return None
            
        cagr = ((end_gdp / start_gdp) ** (1/n_years) - 1) * 100
        return cagr
    
    def predict_future_gdp(self, country_code, years_ahead=5):
        """Use ML to predict future GDP trends (educational only)"""
        country_data = self.gdp_df[
            (self.gdp_df['Country Code'] == country_code) & 
            (self.gdp_df['GDP'].notna())
        ].sort_values('Year')
        
        if len(country_data) < 10:
            return None, None
            
        # Prepare data for ML model
        X = country_data['Year'].values.reshape(-1, 1)
        y = country_data['GDP'].values
        
        # Train linear regression model
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict future
        last_year = country_data['Year'].max()
        future_years = np.array([last_year + i for i in range(1, years_ahead + 1)]).reshape(-1, 1)
        predictions = model.predict(future_years)
        
        # Calculate confidence
        r2_score = model.score(X, y)
        
        return future_years.flatten(), predictions, r2_score
    
    def calculate_volatility(self, country_code, years=10):
        """Calculate economic volatility (standard deviation of growth rates)"""
        country_data = self.gdp_df[
            (self.gdp_df['Country Code'] == country_code) & 
            (self.gdp_df['GDP'].notna())
        ].sort_values('Year').tail(years)
        
        if len(country_data) < 3:
            return None
            
        # Calculate year-over-year growth rates
        gdp_values = country_data['GDP'].values
        growth_rates = []
        
        for i in range(1, len(gdp_values)):
            if gdp_values[i-1] > 0:
                growth_rate = ((gdp_values[i] - gdp_values[i-1]) / gdp_values[i-1]) * 100
                growth_rates.append(growth_rate)
        
        if len(growth_rates) < 2:
            return None
            
        return np.std(growth_rates)
    
    def generate_investment_score(self, country_code):
        """
        Generate AI-powered investment attractiveness score (0-100)
        EDUCATIONAL ONLY - NOT FINANCIAL ADVICE
        """
        growth_rate = self.calculate_growth_rate(country_code, years=5)
        volatility = self.calculate_volatility(country_code, years=10)
        
        if growth_rate is None or volatility is None:
            return None
            
        # Score components
        growth_score = min(max(growth_rate * 10, 0), 50)  # Max 50 points
        stability_score = max(50 - volatility * 2, 0)     # Max 50 points
        
        total_score = growth_score + stability_score
        return min(total_score, 100)
    
    def detect_trends(self, country_code):
        """Detect economic trends using statistical analysis"""
        country_data = self.gdp_df[
            (self.gdp_df['Country Code'] == country_code) & 
            (self.gdp_df['GDP'].notna())
        ].sort_values('Year').tail(20)
        
        if len(country_data) < 5:
            return "Insufficient data"
            
        gdp_values = country_data['GDP'].values
        
        # Calculate recent trend
        recent_5 = gdp_values[-5:]
        older_5 = gdp_values[-10:-5] if len(gdp_values) >= 10 else gdp_values[:-5]
        
        if len(older_5) > 0:
            recent_avg = np.mean(recent_5)
            older_avg = np.mean(older_5)
            
            change = ((recent_avg - older_avg) / older_avg) * 100
            
            if change > 15:
                return "🚀 Strong Growth"
            elif change > 5:
                return "📈 Moderate Growth"
            elif change > -5:
                return "➡️ Stable"
            elif change > -15:
                return "📉 Declining"
            else:
                return "⚠️ Sharp Decline"
        
        return "Unknown"
    
    def compare_countries(self, country_codes):
        """Compare multiple countries across key metrics"""
        results = []
        
        for country in country_codes:
            growth = self.calculate_growth_rate(country, years=5)
            volatility = self.calculate_volatility(country, years=10)
            score = self.generate_investment_score(country)
            trend = self.detect_trends(country)
            
            # Get latest GDP
            country_data = self.gdp_df[
                (self.gdp_df['Country Code'] == country) & 
                (self.gdp_df['GDP'].notna())
            ].sort_values('Year')
            
            latest_gdp = country_data.iloc[-1]['GDP'] if len(country_data) > 0 else None
            
            results.append({
                'Country': country,
                'Latest GDP (B)': f"${latest_gdp/1e9:.1f}B" if latest_gdp else "N/A",
                'Growth Rate': f"{growth:.2f}%" if growth else "N/A",
                'Volatility': f"{volatility:.2f}" if volatility else "N/A",
                'AI Score': f"{score:.1f}/100" if score else "N/A",
                'Trend': trend
            })
        
        return pd.DataFrame(results)
    
    def generate_automated_insights(self, country_codes):
        """Generate automated AI insights for selected countries"""
        insights = []
        
        for country in country_codes[:5]:  # Limit to 5 for performance
            growth = self.calculate_growth_rate(country, years=5)
            volatility = self.calculate_volatility(country, years=10)
            score = self.generate_investment_score(country)
            
            if growth and volatility and score:
                insight = f"**{country}**: "
                
                if score > 70:
                    insight += f"✅ High potential (Score: {score:.1f}) - "
                elif score > 50:
                    insight += f"⚡ Moderate potential (Score: {score:.1f}) - "
                else:
                    insight += f"⚠️ Lower potential (Score: {score:.1f}) - "
                
                insight += f"Growth: {growth:.2f}%, Volatility: {volatility:.2f}"
                
                insights.append(insight)
        
        return insights
