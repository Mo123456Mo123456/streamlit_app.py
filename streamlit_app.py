"""
تطبيق التداول الآلي الذكي - واجهة المستخدم
نظام متكامل يعمل تلقائيًا لتحليل الأسواق وجمع الأرباح
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
from pathlib import Path
from ai_trading_bot import AITradingBot
import time

# إعدادات الصفحة
st.set_page_config(
    page_title='نظام التداول الآلي الذكي',
    page_icon='🤖',
    layout='wide',
    initial_sidebar_state='expanded'
)

# CSS مخصص للواجهة العربية
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .profit-positive {
        color: #00cc00;
        font-weight: bold;
    }
    .profit-negative {
        color: #ff3333;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# العنوان الرئيسي
st.markdown('<h1 class="main-header">🤖 نظام التداول الآلي الذكي</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">نظام ذكي يعمل تلقائيًا لتحليل الأسواق واتخاذ قرارات التداول وجمع الأرباح</p>', unsafe_allow_html=True)

# الشريط الجانبي
with st.sidebar:
    st.header("⚙️ الإعدادات")
    
    initial_balance = st.number_input(
        "رأس المال الأولي ($)",
        min_value=1000.0,
        max_value=1000000.0,
        value=10000.0,
        step=1000.0
    )
    
    symbols_input = st.text_input(
        "الرموز للتداول (مفصولة بفواصل)",
        value="BTC,ETH,AAPL,GOOGL,MSFT"
    )
    symbols = [s.strip().upper() for s in symbols_input.split(',') if s.strip()]
    
    max_position_size = st.slider(
        "الحد الأقصى لحجم المركز (%)",
        min_value=5,
        max_value=50,
        value=20,
        step=5
    ) / 100
    
    auto_trading_enabled = st.checkbox("تفعيل التداول الآلي", value=False)
    
    if auto_trading_enabled:
        trading_interval = st.selectbox(
            "فترة التداول",
            ["كل دقيقة", "كل 5 دقائق", "كل 15 دقيقة", "كل ساعة", "كل يوم"]
        )
    
    st.markdown("---")
    st.header("📊 الإحصائيات السريعة")
    
    # تحميل حالة البوت
    bot_state_file = Path('trading_data/bot_state.json')
    if bot_state_file.exists():
        with open(bot_state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
            current_balance = state.get('portfolio_value', initial_balance)
            total_return = ((current_balance - initial_balance) / initial_balance) * 100
            
            st.metric("قيمة المحفظة", f"${current_balance:,.2f}")
            st.metric("العائد الإجمالي", f"{total_return:.2f}%")
            st.metric("إجمالي العمليات", state.get('total_trades', 0))

# تهيئة البوت
@st.cache_resource
def initialize_bot(initial_balance, max_position_size):
    bot = AITradingBot(initial_balance=initial_balance)
    bot.max_position_size = max_position_size
    bot.load_state()
    return bot

bot = initialize_bot(initial_balance, max_position_size)

# تبويبات الصفحة
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 الرئيسية",
    "📈 التداول الآلي",
    "💰 الأرباح والأداء",
    "📊 التحليلات",
    "⚙️ الإعدادات المتقدمة"
])

# تبويب الرئيسية
with tab1:
    st.header("مرحبًا بك في نظام التداول الآلي الذكي")
    
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = bot.get_performance_metrics()
    
    with col1:
        st.metric(
            "💰 قيمة المحفظة",
            f"${metrics['portfolio_value']:,.2f}",
            delta=f"{metrics['total_return_pct']:.2f}%"
        )
    
    with col2:
        profit_color = "normal" if metrics['total_profit_loss'] >= 0 else "inverse"
        st.metric(
            "💵 إجمالي الأرباح/الخسائر",
            f"${metrics['total_profit_loss']:,.2f}",
            delta_color=profit_color
        )
    
    with col3:
        st.metric(
            "📊 إجمالي العمليات",
            metrics['total_trades'],
            delta=f"{metrics['winning_trades']} فوز"
        )
    
    with col4:
        st.metric(
            "🎯 معدل الفوز",
            f"{metrics['win_rate']:.1f}%",
            delta=f"{metrics['losing_trades']} خسارة"
        )
    
    st.markdown("---")
    
    # الرسم البياني للأداء
    st.subheader("📈 أداء المحفظة")
    
    if len(bot.trade_history) > 0:
        # إنشاء بيانات الأداء التاريخي
        history_df = pd.DataFrame(bot.trade_history)
        history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
        
        # حساب قيمة المحفظة بمرور الوقت
        portfolio_values = []
        running_balance = bot.initial_balance
        running_profit = 0
        
        for trade in bot.trade_history:
            if trade['action'] == 'BUY':
                running_balance -= trade['value']
            elif trade['action'] == 'SELL':
                running_balance += trade['value']
                running_profit += trade.get('profit', 0)
            
            portfolio_values.append({
                'timestamp': trade['timestamp'],
                'portfolio_value': running_balance + running_profit,
                'profit': running_profit
            })
        
        if portfolio_values:
            perf_df = pd.DataFrame(portfolio_values)
            perf_df['timestamp'] = pd.to_datetime(perf_df['timestamp'])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=perf_df['timestamp'],
                y=perf_df['portfolio_value'],
                mode='lines',
                name='قيمة المحفظة',
                line=dict(color='#1f77b4', width=2)
            ))
            fig.add_trace(go.Scatter(
                x=perf_df['timestamp'],
                y=perf_df['profit'],
                mode='lines',
                name='الأرباح المتراكمة',
                line=dict(color='#00cc00', width=2)
            ))
            
            fig.update_layout(
                title="تطور قيمة المحفظة والأرباح",
                xaxis_title="التاريخ",
                yaxis_title="القيمة ($)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد بيانات تداول حتى الآن. ابدأ التداول الآلي من تبويب 'التداول الآلي'")
    
    # المراكز المفتوحة
    st.subheader("📦 المراكز المفتوحة")
    if bot.positions:
        positions_data = []
        for symbol, position in bot.positions.items():
            positions_data.append({
                'الرمز': symbol,
                'الكمية': f"{position['quantity']:.4f}",
                'متوسط السعر': f"${position['avg_price']:.2f}",
                'القيمة': f"${position['quantity'] * position['avg_price']:.2f}"
            })
        
        positions_df = pd.DataFrame(positions_data)
        st.dataframe(positions_df, use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد مراكز مفتوحة حالياً")

# تبويب التداول الآلي
with tab2:
    st.header("🤖 التداول الآلي")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 بدء التداول الآلي", type="primary", use_container_width=True):
            if not bot.is_trained:
                with st.spinner("🔄 تدريب النموذج..."):
                    bot.train_model()
                    st.success("✅ تم تدريب النموذج بنجاح!")
            
            st.info("🔄 جاري تشغيل التداول الآلي...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            iterations = 5
            for i in range(iterations):
                status_text.text(f"التكرار {i+1}/{iterations}")
                progress_bar.progress((i + 1) / iterations)
                
                # محاكاة التداول
                for symbol in symbols[:3]:  # حد أقصى 3 رموز للعرض
                    df = bot.generate_market_data(symbol, 100)
                    current_price = df['close'].iloc[-1]
                    signal_data = bot.analyze_signal(df)
                    bot.execute_trade(symbol, signal_data, current_price)
                
                bot.update_portfolio_value({s: bot.generate_market_data(s, 100)['close'].iloc[-1] for s in symbols[:3]})
                bot.save_state()
                time.sleep(0.5)
            
            st.success("✅ اكتمل التداول الآلي!")
            st.rerun()
    
    with col2:
        if st.button("⏹️ إيقاف التداول", use_container_width=True):
            st.warning("تم إيقاف التداول الآلي")
    
    st.markdown("---")
    
    # تحليل السوق الحالي
    st.subheader("📊 تحليل السوق الحالي")
    
    selected_symbol = st.selectbox("اختر الرمز للتحليل", symbols)
    
    if st.button("🔄 تحديث التحليل"):
        with st.spinner("جاري تحليل السوق..."):
            df = bot.generate_market_data(selected_symbol, 100)
            signal_data = bot.analyze_signal(df)
            current_price = df['close'].iloc[-1]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("السعر الحالي", f"${current_price:.2f}")
            
            with col2:
                st.metric("السعر المتوقع", f"${signal_data['predicted_price']:.2f}")
            
            with col3:
                signal_text = {
                    1: "🟢 شراء",
                    -1: "🔴 بيع",
                    0: "🟡 انتظار"
                }
                st.metric("الإشارة", signal_text[signal_data['signal']])
            
            with col4:
                st.metric("مستوى الثقة", f"{signal_data['confidence']*100:.1f}%")
            
            # الرسم البياني للسعر
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['close'],
                mode='lines',
                name='السعر',
                line=dict(color='#1f77b4')
            ))
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['sma_20'],
                mode='lines',
                name='المتوسط المتحرك 20',
                line=dict(color='orange', dash='dash')
            ))
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['sma_50'],
                mode='lines',
                name='المتوسط المتحرك 50',
                line=dict(color='red', dash='dash')
            ))
            
            fig.add_hline(
                y=signal_data['predicted_price'],
                line_dash="dot",
                line_color="green",
                annotation_text="السعر المتوقع"
            )
            
            fig.update_layout(
                title=f"تحليل {selected_symbol}",
                xaxis_title="التاريخ",
                yaxis_title="السعر ($)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)

# تبويب الأرباح والأداء
with tab3:
    st.header("💰 الأرباح والأداء")
    
    metrics = bot.get_performance_metrics()
    
    # بطاقات الأداء
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "رأس المال الأولي",
            f"${metrics['initial_balance']:,.2f}"
        )
        st.metric(
            "القيمة الحالية",
            f"${metrics['portfolio_value']:,.2f}"
        )
    
    with col2:
        return_color = "normal" if metrics['total_return_pct'] >= 0 else "inverse"
        st.metric(
            "العائد الإجمالي",
            f"{metrics['total_return_pct']:.2f}%",
            delta=f"${metrics['portfolio_value'] - metrics['initial_balance']:,.2f}",
            delta_color=return_color
        )
        st.metric(
            "إجمالي الأرباح/الخسائر",
            f"${metrics['total_profit_loss']:,.2f}"
        )
    
    with col3:
        st.metric(
            "معدل الفوز",
            f"{metrics['win_rate']:.1f}%"
        )
        st.metric(
            "إجمالي العمليات",
            metrics['total_trades']
        )
    
    st.markdown("---")
    
    # تفاصيل العمليات
    st.subheader("📋 سجل العمليات")
    
    if len(bot.trade_history) > 0:
        trades_df = pd.DataFrame(bot.trade_history)
        trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
        trades_df = trades_df.sort_values('timestamp', ascending=False)
        
        # تنسيق البيانات للعرض
        display_df = trades_df[['timestamp', 'symbol', 'action', 'quantity', 'price', 'value', 'confidence']].copy()
        display_df.columns = ['التاريخ', 'الرمز', 'الإجراء', 'الكمية', 'السعر', 'القيمة', 'الثقة']
        display_df['التاريخ'] = display_df['التاريخ'].dt.strftime('%Y-%m-%d %H:%M:%S')
        display_df['السعر'] = display_df['السعر'].apply(lambda x: f"${x:.2f}")
        display_df['القيمة'] = display_df['القيمة'].apply(lambda x: f"${x:.2f}")
        display_df['الثقة'] = display_df['الثقة'].apply(lambda x: f"{x*100:.1f}%")
        
        if 'profit' in trades_df.columns:
            display_df['الربح'] = trades_df['profit'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "-")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # إحصائيات العمليات
        st.subheader("📊 إحصائيات العمليات")
        
        col1, col2 = st.columns(2)
        
        with col1:
            buy_trades = len(trades_df[trades_df['action'] == 'BUY'])
            sell_trades = len(trades_df[trades_df['action'] == 'SELL'])
            
            fig = px.pie(
                values=[buy_trades, sell_trades],
                names=['شراء', 'بيع'],
                title="توزيع العمليات"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'profit' in trades_df.columns:
                profitable_trades = len(trades_df[(trades_df['action'] == 'SELL') & (trades_df['profit'] > 0)])
                losing_trades = len(trades_df[(trades_df['action'] == 'SELL') & (trades_df['profit'] <= 0)])
                
                if profitable_trades + losing_trades > 0:
                    fig = px.pie(
                        values=[profitable_trades, losing_trades],
                        names=['مربحة', 'خاسرة'],
                        title="نسبة العمليات المربحة"
                    )
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد عمليات تداول حتى الآن")

# تبويب التحليلات
with tab4:
    st.header("📊 التحليلات المتقدمة")
    
    selected_symbol = st.selectbox("اختر الرمز للتحليل", symbols, key="analysis_symbol")
    
    if st.button("🔄 إنشاء تحليل شامل"):
        with st.spinner("جاري إنشاء التحليل..."):
            df = bot.generate_market_data(selected_symbol, 200)
            df = df.fillna(method='bfill').fillna(method='ffill')
            
            # المؤشرات التقنية
            st.subheader("📈 المؤشرات التقنية")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                rsi = df['rsi'].iloc[-1]
                rsi_status = "مفرط الشراء" if rsi > 70 else "مفرط البيع" if rsi < 30 else "عادي"
                st.metric("RSI", f"{rsi:.2f}", rsi_status)
            
            with col2:
                macd = df['macd'].iloc[-1]
                macd_signal = df['macd_signal'].iloc[-1]
                macd_status = "إيجابي" if macd > macd_signal else "سلبي"
                st.metric("MACD", f"{macd:.2f}", macd_status)
            
            with col3:
                sma_20 = df['sma_20'].iloc[-1]
                sma_50 = df['sma_50'].iloc[-1]
                sma_status = "صاعد" if sma_20 > sma_50 else "هابط"
                st.metric("المتوسطات المتحركة", sma_status)
            
            with col4:
                current_price = df['close'].iloc[-1]
                bb_upper = df['bb_upper'].iloc[-1]
                bb_lower = df['bb_lower'].iloc[-1]
                bb_status = "قريب من الأعلى" if current_price > bb_upper * 0.95 else "قريب من الأسفل" if current_price < bb_lower * 1.05 else "وسطي"
                st.metric("Bollinger Bands", bb_status)
            
            # الرسم البياني الشامل
            fig = go.Figure()
            
            # السعر
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['close'],
                mode='lines',
                name='السعر',
                line=dict(color='#1f77b4', width=2)
            ))
            
            # المتوسطات المتحركة
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['sma_20'],
                mode='lines',
                name='SMA 20',
                line=dict(color='orange', dash='dash')
            ))
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['sma_50'],
                mode='lines',
                name='SMA 50',
                line=dict(color='red', dash='dash')
            ))
            
            # Bollinger Bands
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['bb_upper'],
                mode='lines',
                name='BB Upper',
                line=dict(color='gray', width=1, dash='dot'),
                fill=None
            ))
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['bb_lower'],
                mode='lines',
                name='BB Lower',
                line=dict(color='gray', width=1, dash='dot'),
                fill='tonexty',
                fillcolor='rgba(128,128,128,0.1)'
            ))
            
            fig.update_layout(
                title=f"التحليل الفني الشامل - {selected_symbol}",
                xaxis_title="التاريخ",
                yaxis_title="السعر ($)",
                height=500,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # RSI Chart
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(
                x=df['date'],
                y=df['rsi'],
                mode='lines',
                name='RSI',
                line=dict(color='purple', width=2)
            ))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="مفرط الشراء")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="مفرط البيع")
            fig_rsi.update_layout(
                title="مؤشر RSI",
                xaxis_title="التاريخ",
                yaxis_title="RSI",
                height=300,
                yaxis_range=[0, 100]
            )
            st.plotly_chart(fig_rsi, use_container_width=True)

# تبويب الإعدادات المتقدمة
with tab5:
    st.header("⚙️ الإعدادات المتقدمة")
    
    st.subheader("إدارة المخاطر")
    
    col1, col2 = st.columns(2)
    
    with col1:
        stop_loss = st.slider(
            "نسبة Stop Loss (%)",
            min_value=1,
            max_value=20,
            value=int(bot.stop_loss_percentage * 100),
            step=1
        ) / 100
        
        take_profit = st.slider(
            "نسبة Take Profit (%)",
            min_value=5,
            max_value=50,
            value=int(bot.take_profit_percentage * 100),
            step=5
        ) / 100
    
    with col2:
        bot.stop_loss_percentage = stop_loss
        bot.take_profit_percentage = take_profit
        
        st.info(f"Stop Loss: {stop_loss*100:.1f}%")
        st.info(f"Take Profit: {take_profit*100:.1f}%")
    
    st.markdown("---")
    
    st.subheader("إدارة البيانات")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 حفظ الحالة الحالية", use_container_width=True):
            bot.save_state()
            st.success("✅ تم حفظ الحالة بنجاح!")
    
    with col2:
        if st.button("🔄 إعادة تعيين النظام", use_container_width=True):
            bot.__init__(initial_balance=initial_balance)
            bot.save_state()
            st.success("✅ تم إعادة تعيين النظام!")
            st.rerun()
    
    st.markdown("---")
    
    st.subheader("معلومات النظام")
    
    st.json({
        "النموذج المدرب": bot.is_trained,
        "رأس المال الأولي": f"${bot.initial_balance:,.2f}",
        "الحد الأقصى لحجم المركز": f"{bot.max_position_size*100:.0f}%",
        "Stop Loss": f"{bot.stop_loss_percentage*100:.1f}%",
        "Take Profit": f"{bot.take_profit_percentage*100:.1f}%",
        "عدد المراكز المفتوحة": len(bot.positions),
        "إجمالي العمليات": bot.total_trades
    })
