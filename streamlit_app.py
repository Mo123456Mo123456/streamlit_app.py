import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# إعداد الصفحة
st.set_page_config(
    page_title='نظام التداول الذكي بالذكاء الاصطناعي',
    page_icon='🤖',
    layout='wide',
    initial_sidebar_state='expanded'
)

# CSS مخصص للتصميم الحديث
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .profit-positive {
        color: #00ff88;
        font-weight: bold;
    }
    .profit-negative {
        color: #ff4444;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# مسار حفظ البيانات
DATA_DIR = Path(__file__).parent / 'data'
DATA_DIR.mkdir(exist_ok=True)
TRADES_FILE = DATA_DIR / 'trades.json'
PROFITS_FILE = DATA_DIR / 'profits.json'
CONFIG_FILE = DATA_DIR / 'config.json'

# تحميل/إنشاء البيانات
def load_data():
    """تحميل البيانات المحفوظة"""
    if TRADES_FILE.exists():
        with open(TRADES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'trades': [], 'balance': 10000.0, 'initial_balance': 10000.0}

def save_data(data):
    """حفظ البيانات"""
    with open(TRADES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_profits():
    """تحميل سجل الأرباح"""
    if PROFITS_FILE.exists():
        with open(PROFITS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'daily_profits': [], 'total_profit': 0.0}

def save_profits(profits):
    """حفظ سجل الأرباح"""
    with open(PROFITS_FILE, 'w', encoding='utf-8') as f:
        json.dump(profits, f, ensure_ascii=False, indent=2)

def load_config():
    """تحميل الإعدادات"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'auto_trading': False,
        'risk_level': 'medium',
        'max_trades_per_day': 10,
        'stop_loss': 0.05,
        'take_profit': 0.10
    }

def save_config(config):
    """حفظ الإعدادات"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# نموذج الذكاء الاصطناعي للتنبؤ
class AITradingModel:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def generate_market_data(self, days=30):
        """إنشاء بيانات سوق محاكاة"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        np.random.seed(42)
        
        # محاكاة بيانات السوق
        base_price = 100
        prices = []
        volumes = []
        trends = []
        
        for i in range(days):
            trend = np.sin(i / 10) + np.random.normal(0, 0.1)
            price = base_price * (1 + trend * 0.02)
            volume = np.random.uniform(1000, 10000)
            
            prices.append(price)
            volumes.append(volume)
            trends.append(trend)
        
        df = pd.DataFrame({
            'date': dates,
            'price': prices,
            'volume': volumes,
            'trend': trends,
            'sma_7': pd.Series(prices).rolling(7).mean(),
            'sma_14': pd.Series(prices).rolling(14).mean(),
            'rsi': 50 + np.random.normal(0, 10, days)
        })
        
        df = df.bfill()
        return df
    
    def train_model(self, market_data):
        """تدريب النموذج"""
        df = market_data.copy()
        df['price_change'] = df['price'].pct_change().shift(-1)
        df = df.dropna()
        
        features = ['price', 'volume', 'trend', 'sma_7', 'sma_14', 'rsi']
        X = df[features].values
        y = df['price_change'].values
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
    
    def predict(self, market_data):
        """التنبؤ بالاتجاه"""
        if not self.is_trained:
            self.train_model(market_data)
        
        latest = market_data.iloc[-1:]
        features = ['price', 'volume', 'trend', 'sma_7', 'sma_14', 'rsi']
        X = latest[features].values
        X_scaled = self.scaler.transform(X)
        
        prediction = self.model.predict(X_scaled)[0]
        confidence = abs(prediction) * 100
        
        return {
            'direction': 'buy' if prediction > 0 else 'sell',
            'confidence': min(confidence, 95),
            'expected_change': prediction * 100
        }

# نظام التداول التلقائي
class AutoTradingSystem:
    def __init__(self, ai_model, config):
        self.ai_model = ai_model
        self.config = config
        self.market_data = ai_model.generate_market_data(60)
        ai_model.train_model(self.market_data)
    
    def should_trade(self, prediction):
        """تحديد ما إذا كان يجب التداول"""
        if not self.config['auto_trading']:
            return False
        
        min_confidence = {
            'low': 40,
            'medium': 60,
            'high': 80
        }.get(self.config['risk_level'], 60)
        
        return prediction['confidence'] >= min_confidence
    
    def execute_trade(self, data, prediction):
        """تنفيذ صفقة"""
        trades = data['trades']
        balance = data['balance']
        
        # فحص عدد الصفقات اليوم
        today = datetime.now().date()
        today_trades = [t for t in trades if datetime.fromisoformat(t['timestamp']).date() == today]
        
        if len(today_trades) >= self.config['max_trades_per_day']:
            return None, "تم الوصول للحد الأقصى من الصفقات اليوم"
        
        # حساب حجم الصفقة
        trade_amount = balance * 0.1  # 10% من الرصيد
        
        if trade_amount < 10:
            return None, "الرصيد غير كافٍ"
        
        # إنشاء صفقة
        current_price = self.market_data.iloc[-1]['price']
        trade = {
            'id': len(trades) + 1,
            'type': prediction['direction'],
            'amount': trade_amount,
            'price': current_price,
            'timestamp': datetime.now().isoformat(),
            'confidence': prediction['confidence'],
            'expected_change': prediction['expected_change'],
            'status': 'open'
        }
        
        trades.append(trade)
        data['balance'] -= trade_amount
        
        # محاكاة إغلاق الصفقة بعد فترة
        if prediction['direction'] == 'buy':
            profit_multiplier = 1 + (prediction['expected_change'] / 100)
        else:
            profit_multiplier = 1 - (prediction['expected_change'] / 100)
        
        # تطبيق stop loss و take profit
        if abs(prediction['expected_change']) < self.config['stop_loss'] * 100:
            profit_multiplier = 1 - self.config['stop_loss']
        elif abs(prediction['expected_change']) > self.config['take_profit'] * 100:
            profit_multiplier = 1 + self.config['take_profit']
        
        profit = trade_amount * (profit_multiplier - 1)
        trade['profit'] = profit
        trade['status'] = 'closed'
        trade['close_timestamp'] = (datetime.now() + timedelta(hours=1)).isoformat()
        
        data['balance'] += trade_amount + profit
        
        return trade, "تم تنفيذ الصفقة بنجاح"

# تحميل البيانات
data = load_data()
profits = load_profits()
config = load_config()

# تهيئة النموذج
if 'ai_model' not in st.session_state:
    st.session_state.ai_model = AITradingModel()
    st.session_state.ai_model.train_model(st.session_state.ai_model.generate_market_data(60))

if 'trading_system' not in st.session_state:
    st.session_state.trading_system = AutoTradingSystem(st.session_state.ai_model, config)

# الواجهة الرئيسية
st.markdown('<h1 class="main-header">🤖 نظام التداول الذكي بالذكاء الاصطناعي</h1>', unsafe_allow_html=True)

# الشريط الجانبي للإعدادات
with st.sidebar:
    st.header('⚙️ الإعدادات')
    
    auto_trading = st.toggle('التداول التلقائي', value=config['auto_trading'])
    risk_level = st.selectbox('مستوى المخاطرة', ['low', 'medium', 'high'], 
                             index=['low', 'medium', 'high'].index(config['risk_level']))
    max_trades = st.slider('الحد الأقصى للصفقات يومياً', 1, 50, config['max_trades_per_day'])
    stop_loss = st.slider('Stop Loss %', 0.01, 0.20, config['stop_loss'], 0.01)
    take_profit = st.slider('Take Profit %', 0.05, 0.30, config['take_profit'], 0.01)
    
    if st.button('💾 حفظ الإعدادات'):
        config.update({
            'auto_trading': auto_trading,
            'risk_level': risk_level,
            'max_trades_per_day': max_trades,
            'stop_loss': stop_loss,
            'take_profit': take_profit
        })
        save_config(config)
        st.session_state.trading_system.config = config
        st.success('تم حفظ الإعدادات!')
    
    st.divider()
    
    if st.button('🔄 تحديث البيانات'):
        st.session_state.ai_model = AITradingModel()
        market_data = st.session_state.ai_model.generate_market_data(60)
        st.session_state.ai_model.train_model(market_data)
        st.session_state.trading_system.market_data = market_data
        st.rerun()

# الأقسام الرئيسية
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_profit = data['balance'] - data['initial_balance']
    profit_pct = (total_profit / data['initial_balance']) * 100
    st.metric(
        '💰 الرصيد الحالي',
        f"${data['balance']:,.2f}",
        delta=f"{profit_pct:.2f}%"
    )

with col2:
    st.metric(
        '📈 إجمالي الأرباح',
        f"${total_profit:,.2f}",
        delta=f"{len([t for t in data['trades'] if t.get('profit', 0) > 0])} صفقة رابحة"
    )

with col3:
    total_trades = len(data['trades'])
    st.metric(
        '📊 إجمالي الصفقات',
        total_trades,
        delta=f"{len([t for t in data['trades'] if t['status'] == 'open'])} مفتوحة"
    )

with col4:
    win_rate = 0
    if total_trades > 0:
        winning_trades = len([t for t in data['trades'] if t.get('profit', 0) > 0])
        win_rate = (winning_trades / total_trades) * 100
    st.metric(
        '🎯 معدل النجاح',
        f"{win_rate:.1f}%",
        delta="AI Powered"
    )

st.divider()

# التنبؤات والتحليل
st.header('🔮 تحليل السوق والتنبؤات')

market_data = st.session_state.trading_system.market_data
prediction = st.session_state.ai_model.predict(market_data)

col1, col2 = st.columns(2)

with col1:
    st.subheader('📊 بيانات السوق')
    
    # رسم بياني للسعر
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=market_data['date'],
        y=market_data['price'],
        mode='lines',
        name='السعر',
        line=dict(color='#667eea', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=market_data['date'],
        y=market_data['sma_7'],
        mode='lines',
        name='المتوسط المتحرك 7 أيام',
        line=dict(color='#ff6b6b', width=1, dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=market_data['date'],
        y=market_data['sma_14'],
        mode='lines',
        name='المتوسط المتحرك 14 يوم',
        line=dict(color='#4ecdc4', width=1, dash='dash')
    ))
    
    fig.update_layout(
        title='تطور السعر',
        xaxis_title='التاريخ',
        yaxis_title='السعر',
        height=400,
        template='plotly_dark'
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader('🤖 توصية الذكاء الاصطناعي')
    
    direction_emoji = '🟢' if prediction['direction'] == 'buy' else '🔴'
    direction_text = 'شراء' if prediction['direction'] == 'buy' else 'بيع'
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem; border-radius: 15px; color: white; text-align: center;">
        <h2 style="margin: 0; font-size: 3rem;">{direction_emoji}</h2>
        <h3 style="margin: 1rem 0;">{direction_text}</h3>
        <p style="font-size: 1.5rem; margin: 0.5rem 0;">
            الثقة: <strong>{prediction['confidence']:.1f}%</strong>
        </p>
        <p style="font-size: 1.2rem; margin: 0.5rem 0;">
            التغيير المتوقع: <strong>{prediction['expected_change']:.2f}%</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # زر التداول اليدوي
    if st.button('⚡ تنفيذ صفقة الآن', type='primary', use_container_width=True):
        trade, message = st.session_state.trading_system.execute_trade(data, prediction)
        if trade:
            save_data(data)
            st.success(f"✅ {message}")
            st.json(trade)
            st.rerun()
        else:
            st.warning(f"⚠️ {message}")
    
    # التداول التلقائي
    if config['auto_trading']:
        if st.session_state.trading_system.should_trade(prediction):
            if st.button('🤖 تنفيذ تلقائي', use_container_width=True):
                trade, message = st.session_state.trading_system.execute_trade(data, prediction)
                if trade:
                    save_data(data)
                    st.success(f"✅ {message}")
                    st.rerun()

st.divider()

# سجل الصفقات
st.header('📋 سجل الصفقات')

if data['trades']:
    trades_df = pd.DataFrame(data['trades'])
    trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
    trades_df = trades_df.sort_values('timestamp', ascending=False)
    
    # عرض الصفقات
    for idx, trade in trades_df.head(10).iterrows():
        with st.expander(f"صفقة #{trade['id']} - {trade['type']} - {trade['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**النوع:** {trade['type']}")
                st.write(f"**المبلغ:** ${trade['amount']:,.2f}")
            
            with col2:
                st.write(f"**السعر:** ${trade['price']:,.2f}")
                st.write(f"**الثقة:** {trade['confidence']:.1f}%")
            
            with col3:
                profit = trade.get('profit', 0)
                profit_class = 'profit-positive' if profit > 0 else 'profit-negative'
                st.markdown(f"**الربح:** <span class='{profit_class}'>${profit:,.2f}</span>", unsafe_allow_html=True)
                st.write(f"**الحالة:** {trade['status']}")
            
            with col4:
                st.write(f"**التغيير المتوقع:** {trade['expected_change']:.2f}%")
                if trade['status'] == 'closed':
                    st.write(f"**وقت الإغلاق:** {pd.to_datetime(trade.get('close_timestamp', trade['timestamp'])).strftime('%H:%M')}")
    
    # رسم بياني للأرباح
    st.subheader('📈 تطور الأرباح')
    
    trades_df['cumulative_profit'] = trades_df.get('profit', 0).fillna(0).cumsum()
    trades_df['cumulative_profit'] += data['initial_balance']
    
    fig_profit = px.line(
        trades_df,
        x='timestamp',
        y='cumulative_profit',
        title='الرصيد التراكمي',
        labels={'cumulative_profit': 'الرصيد ($)', 'timestamp': 'التاريخ'}
    )
    fig_profit.update_layout(template='plotly_dark', height=400)
    st.plotly_chart(fig_profit, use_container_width=True)
    
    # إحصائيات مفصلة
    st.subheader('📊 إحصائيات مفصلة')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_profit_trades = trades_df[trades_df.get('profit', 0) > 0]
        st.metric('الصفقات الرابحة', len(total_profit_trades))
    
    with col2:
        avg_profit = trades_df.get('profit', 0).fillna(0).mean()
        st.metric('متوسط الربح', f"${avg_profit:,.2f}")
    
    with col3:
        best_trade = trades_df.loc[trades_df.get('profit', 0).idxmax()] if len(trades_df) > 0 else None
        if best_trade is not None:
            st.metric('أفضل صفقة', f"${best_trade.get('profit', 0):,.2f}")
else:
    st.info('لا توجد صفقات حتى الآن. ابدأ التداول الآن!')

# التحديث التلقائي
if config['auto_trading']:
    st.info('🤖 التداول التلقائي نشط - سيتم تنفيذ الصفقات تلقائياً عند توفر الفرص المناسبة')

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🤖 نظام التداول الذكي بالذكاء الاصطناعي | يعمل تلقائياً 24/7</p>
    <p>⚠️ تحذير: هذا تطبيق محاكاة للأغراض التعليمية فقط</p>
</div>
""", unsafe_allow_html=True)
