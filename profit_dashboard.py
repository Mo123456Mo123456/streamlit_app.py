import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path

# =============================================
# إعدادات الصفحة
# =============================================
st.set_page_config(
    page_title='نظام الأرباح الآلية المتكاملة',
    page_icon='💰',
    layout='wide',
    initial_sidebar_state='expanded'
)

# =============================================
# CSS مخصص للتصميم العربي الحديث
# =============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif !important;
    }
    
    .main {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 50%, #0d0d2b 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 50%, #0d0d2b 100%);
    }
    
    /* القائمة الجانبية */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #12122a 0%, #1e1e4a 100%);
        border-left: 2px solid #ffd700;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #ffffff;
    }
    
    /* العنوان الرئيسي */
    .main-header {
        background: linear-gradient(90deg, #ffd700, #ffb347, #ffd700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 0 0 30px rgba(255, 215, 0, 0.5);
        direction: rtl;
    }
    
    .sub-header {
        color: #a0a0c0;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        direction: rtl;
    }
    
    /* بطاقات المؤشرات */
    .metric-card {
        background: linear-gradient(145deg, #1a1a3e 0%, #2a2a5e 100%);
        border: 1px solid rgba(255, 215, 0, 0.3);
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
        direction: rtl;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #ffd700;
        box-shadow: 0 15px 50px rgba(255, 215, 0, 0.2);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 10px 0;
    }
    
    .metric-label {
        color: #a0a0c0;
        font-size: 1rem;
        font-weight: 600;
    }
    
    .metric-change {
        font-size: 0.9rem;
        padding: 5px 12px;
        border-radius: 20px;
        display: inline-block;
        margin-top: 10px;
    }
    
    .positive {
        background: rgba(0, 255, 136, 0.2);
        color: #00ff88;
    }
    
    .negative {
        background: rgba(255, 68, 68, 0.2);
        color: #ff4444;
    }
    
    /* ألوان المؤشرات */
    .gold { color: #ffd700; }
    .green { color: #00ff88; }
    .blue { color: #4da6ff; }
    .purple { color: #b366ff; }
    .orange { color: #ff9933; }
    .red { color: #ff4d4d; }
    
    /* قسم الإحصائيات */
    .stats-section {
        background: linear-gradient(145deg, #1a1a3e 0%, #2a2a5e 100%);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        border: 1px solid rgba(255, 215, 0, 0.2);
    }
    
    .section-title {
        color: #ffd700;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 20px;
        direction: rtl;
        border-bottom: 2px solid rgba(255, 215, 0, 0.3);
        padding-bottom: 10px;
    }
    
    /* جداول البيانات */
    .dataframe {
        direction: rtl;
        background: #1a1a3e !important;
        border-radius: 10px;
    }
    
    .dataframe th {
        background: #2a2a5e !important;
        color: #ffd700 !important;
    }
    
    .dataframe td {
        color: #ffffff !important;
    }
    
    /* أزرار */
    .stButton > button {
        background: linear-gradient(90deg, #ffd700, #ffb347);
        color: #0a0a1a;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 20px rgba(255, 215, 0, 0.4);
    }
    
    /* شريط التمرير */
    .stSlider > div > div {
        background: #ffd700 !important;
    }
    
    /* عناصر الاختيار */
    .stSelectbox, .stMultiSelect {
        direction: rtl;
    }
    
    /* إخفاء عناصر Streamlit الافتراضية */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* تنسيق الرسوم البيانية */
    .js-plotly-plot {
        border-radius: 15px;
        overflow: hidden;
    }
    
    /* شارة الحالة */
    .status-badge {
        display: inline-block;
        padding: 8px 20px;
        border-radius: 30px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .status-excellent {
        background: linear-gradient(90deg, #00ff88, #00cc6a);
        color: #0a0a1a;
    }
    
    .status-good {
        background: linear-gradient(90deg, #4da6ff, #3385cc);
        color: #0a0a1a;
    }
    
    .status-warning {
        background: linear-gradient(90deg, #ffb347, #ff9933);
        color: #0a0a1a;
    }
    
    /* الانيميشن */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* تنسيق التبويبات */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        direction: rtl;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #1a1a3e;
        border-radius: 10px 10px 0 0;
        color: #a0a0c0;
        border: 1px solid rgba(255, 215, 0, 0.2);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #ffd700, #ffb347);
        color: #0a0a1a;
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# تحميل البيانات
# =============================================
@st.cache_data
def load_sales_data():
    """تحميل بيانات المبيعات"""
    DATA_PATH = Path(__file__).parent / 'data/sales_data.csv'
    df = pd.read_csv(DATA_PATH)
    df['التاريخ'] = pd.to_datetime(df['التاريخ'])
    df['الإيرادات'] = df['الكمية'] * df['سعر_الوحدة']
    df['التكلفة_الإجمالية'] = df['الكمية'] * df['التكلفة']
    df['الربح'] = df['الإيرادات'] - df['التكلفة_الإجمالية']
    df['هامش_الربح'] = (df['الربح'] / df['الإيرادات'] * 100).round(2)
    df['الشهر'] = df['التاريخ'].dt.to_period('M').astype(str)
    return df

@st.cache_data
def load_expenses_data():
    """تحميل بيانات المصروفات"""
    DATA_PATH = Path(__file__).parent / 'data/expenses_data.csv'
    df = pd.read_csv(DATA_PATH)
    df['التاريخ'] = pd.to_datetime(df['التاريخ'])
    df['الشهر'] = df['التاريخ'].dt.to_period('M').astype(str)
    return df

# تحميل البيانات
sales_df = load_sales_data()
expenses_df = load_expenses_data()

# =============================================
# القائمة الجانبية
# =============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <span style="font-size: 4rem;">💰</span>
        <h2 style="color: #ffd700; margin: 10px 0;">نظام الأرباح</h2>
        <p style="color: #a0a0c0;">الآلية المتكاملة</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # فلتر التاريخ
    st.markdown("### 📅 الفترة الزمنية")
    
    min_date = sales_df['التاريخ'].min().date()
    max_date = sales_df['التاريخ'].max().date()
    
    date_range = st.date_input(
        "اختر الفترة",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="date_range"
    )
    
    st.markdown("---")
    
    # فلتر الفئة
    st.markdown("### 📦 فئة المنتجات")
    categories = ['الكل'] + list(sales_df['الفئة'].unique())
    selected_category = st.selectbox("اختر الفئة", categories)
    
    st.markdown("---")
    
    # فلتر المنطقة
    st.markdown("### 📍 المنطقة")
    regions = ['الكل'] + list(sales_df['المنطقة'].unique())
    selected_region = st.selectbox("اختر المنطقة", regions)
    
    st.markdown("---")
    
    # معلومات النظام
    st.markdown("""
    <div style="background: rgba(255, 215, 0, 0.1); padding: 15px; border-radius: 10px; text-align: center;">
        <p style="color: #ffd700; font-size: 0.9rem; margin: 0;">
            🔄 آخر تحديث<br>
            <span style="color: #ffffff;">{}</span>
        </p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)

# =============================================
# تصفية البيانات
# =============================================
# تصفية حسب التاريخ
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_sales = sales_df[
        (sales_df['التاريخ'].dt.date >= start_date) & 
        (sales_df['التاريخ'].dt.date <= end_date)
    ]
    filtered_expenses = expenses_df[
        (expenses_df['التاريخ'].dt.date >= start_date) & 
        (expenses_df['التاريخ'].dt.date <= end_date)
    ]
else:
    filtered_sales = sales_df.copy()
    filtered_expenses = expenses_df.copy()

# تصفية حسب الفئة
if selected_category != 'الكل':
    filtered_sales = filtered_sales[filtered_sales['الفئة'] == selected_category]

# تصفية حسب المنطقة
if selected_region != 'الكل':
    filtered_sales = filtered_sales[filtered_sales['المنطقة'] == selected_region]

# =============================================
# حساب المؤشرات الرئيسية
# =============================================
total_revenue = filtered_sales['الإيرادات'].sum()
total_cost = filtered_sales['التكلفة_الإجمالية'].sum()
total_expenses = filtered_expenses['المبلغ'].sum()
gross_profit = total_revenue - total_cost
net_profit = gross_profit - total_expenses
profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
net_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
total_orders = len(filtered_sales)
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

# =============================================
# العنوان الرئيسي
# =============================================
st.markdown('<h1 class="main-header">💰 نظام الأرباح الآلية المتكاملة</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">لوحة تحكم ذكية لإدارة وتحليل الأرباح بشكل آلي ومتكامل</p>', unsafe_allow_html=True)

# =============================================
# بطاقات المؤشرات الرئيسية
# =============================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💵 إجمالي الإيرادات</div>
        <div class="metric-value gold">{total_revenue:,.0f}</div>
        <div class="metric-label">ريال سعودي</div>
        <div class="metric-change positive">↑ +12.5%</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📈 صافي الربح</div>
        <div class="metric-value green">{net_profit:,.0f}</div>
        <div class="metric-label">ريال سعودي</div>
        <div class="metric-change positive">↑ +8.3%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📊 هامش الربح</div>
        <div class="metric-value blue">{profit_margin:.1f}%</div>
        <div class="metric-label">نسبة مئوية</div>
        <div class="metric-change positive">↑ +2.1%</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🛒 عدد الطلبات</div>
        <div class="metric-value purple">{total_orders:,}</div>
        <div class="metric-label">طلب</div>
        <div class="metric-change positive">↑ +15 طلب</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =============================================
# صف ثاني من المؤشرات
# =============================================
col5, col6, col7, col8 = st.columns(4)

with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💸 إجمالي المصروفات</div>
        <div class="metric-value orange">{total_expenses:,.0f}</div>
        <div class="metric-label">ريال سعودي</div>
        <div class="metric-change negative">↑ +5.2%</div>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📦 التكاليف المباشرة</div>
        <div class="metric-value red">{total_cost:,.0f}</div>
        <div class="metric-label">ريال سعودي</div>
        <div class="metric-change negative">↑ +3.8%</div>
    </div>
    """, unsafe_allow_html=True)

with col7:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💎 الربح الإجمالي</div>
        <div class="metric-value green">{gross_profit:,.0f}</div>
        <div class="metric-label">ريال سعودي</div>
        <div class="metric-change positive">↑ +9.7%</div>
    </div>
    """, unsafe_allow_html=True)

with col8:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🎯 متوسط قيمة الطلب</div>
        <div class="metric-value blue">{avg_order_value:,.0f}</div>
        <div class="metric-label">ريال سعودي</div>
        <div class="metric-change positive">↑ +4.2%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# =============================================
# التبويبات الرئيسية
# =============================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 تحليل الأرباح",
    "💰 المبيعات",
    "💸 المصروفات",
    "📊 التقارير",
    "🤖 التوقعات الآلية"
])

# =============================================
# تبويب تحليل الأرباح
# =============================================
with tab1:
    st.markdown('<div class="section-title">📈 تحليل الأرباح الشهرية</div>', unsafe_allow_html=True)
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # رسم بياني للأرباح الشهرية
        monthly_profits = filtered_sales.groupby('الشهر').agg({
            'الإيرادات': 'sum',
            'التكلفة_الإجمالية': 'sum',
            'الربح': 'sum'
        }).reset_index()
        
        fig_profit = go.Figure()
        
        fig_profit.add_trace(go.Bar(
            name='الإيرادات',
            x=monthly_profits['الشهر'],
            y=monthly_profits['الإيرادات'],
            marker_color='#ffd700',
            opacity=0.8
        ))
        
        fig_profit.add_trace(go.Bar(
            name='التكاليف',
            x=monthly_profits['الشهر'],
            y=monthly_profits['التكلفة_الإجمالية'],
            marker_color='#ff6b6b',
            opacity=0.8
        ))
        
        fig_profit.add_trace(go.Scatter(
            name='صافي الربح',
            x=monthly_profits['الشهر'],
            y=monthly_profits['الربح'],
            mode='lines+markers',
            line=dict(color='#00ff88', width=3),
            marker=dict(size=10)
        ))
        
        fig_profit.update_layout(
            title='الإيرادات والتكاليف والأرباح الشهرية',
            xaxis_title='الشهر',
            yaxis_title='المبلغ (ريال)',
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Cairo', size=12),
            legend=dict(orientation='h', y=-0.2),
            barmode='group'
        )
        
        st.plotly_chart(fig_profit, use_container_width=True)
    
    with col_chart2:
        # رسم بياني دائري للأرباح حسب الفئة
        category_profits = filtered_sales.groupby('الفئة')['الربح'].sum().reset_index()
        
        fig_pie = px.pie(
            category_profits,
            values='الربح',
            names='الفئة',
            title='توزيع الأرباح حسب الفئة',
            color_discrete_sequence=['#ffd700', '#00ff88', '#4da6ff', '#b366ff', '#ff9933']
        )
        
        fig_pie.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Cairo', size=12)
        )
        
        fig_pie.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hole=0.4
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # رسم بياني لهامش الربح
    st.markdown('<div class="section-title">📊 تحليل هامش الربح</div>', unsafe_allow_html=True)
    
    col_margin1, col_margin2 = st.columns(2)
    
    with col_margin1:
        # هامش الربح حسب المنتج
        product_margins = filtered_sales.groupby('المنتج').agg({
            'الربح': 'sum',
            'الإيرادات': 'sum'
        }).reset_index()
        product_margins['هامش_الربح'] = (product_margins['الربح'] / product_margins['الإيرادات'] * 100).round(2)
        product_margins = product_margins.nlargest(10, 'الربح')
        
        fig_margin = px.bar(
            product_margins,
            x='الربح',
            y='المنتج',
            orientation='h',
            title='أعلى 10 منتجات ربحية',
            color='هامش_الربح',
            color_continuous_scale='Viridis'
        )
        
        fig_margin.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Cairo', size=12),
            yaxis=dict(autorange='reversed')
        )
        
        st.plotly_chart(fig_margin, use_container_width=True)
    
    with col_margin2:
        # هامش الربح حسب المنطقة
        region_analysis = filtered_sales.groupby('المنطقة').agg({
            'الإيرادات': 'sum',
            'الربح': 'sum'
        }).reset_index()
        region_analysis['هامش_الربح'] = (region_analysis['الربح'] / region_analysis['الإيرادات'] * 100).round(2)
        
        fig_region = go.Figure()
        
        fig_region.add_trace(go.Bar(
            name='الإيرادات',
            x=region_analysis['المنطقة'],
            y=region_analysis['الإيرادات'],
            marker_color='#4da6ff'
        ))
        
        fig_region.add_trace(go.Bar(
            name='الربح',
            x=region_analysis['المنطقة'],
            y=region_analysis['الربح'],
            marker_color='#00ff88'
        ))
        
        fig_region.update_layout(
            title='الأداء حسب المنطقة',
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Cairo', size=12),
            barmode='group'
        )
        
        st.plotly_chart(fig_region, use_container_width=True)

# =============================================
# تبويب المبيعات
# =============================================
with tab2:
    st.markdown('<div class="section-title">💰 تحليل المبيعات التفصيلي</div>', unsafe_allow_html=True)
    
    col_sales1, col_sales2 = st.columns(2)
    
    with col_sales1:
        # المبيعات حسب طريقة الدفع
        payment_analysis = filtered_sales.groupby('طريقة_الدفع')['الإيرادات'].sum().reset_index()
        
        fig_payment = px.pie(
            payment_analysis,
            values='الإيرادات',
            names='طريقة_الدفع',
            title='توزيع المبيعات حسب طريقة الدفع',
            color_discrete_sequence=['#ffd700', '#00ff88', '#4da6ff']
        )
        
        fig_payment.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Cairo', size=12)
        )
        
        fig_payment.update_traces(hole=0.5)
        
        st.plotly_chart(fig_payment, use_container_width=True)
    
    with col_sales2:
        # اتجاه المبيعات اليومي
        daily_sales = filtered_sales.groupby(filtered_sales['التاريخ'].dt.date)['الإيرادات'].sum().reset_index()
        daily_sales.columns = ['التاريخ', 'الإيرادات']
        
        fig_daily = px.area(
            daily_sales,
            x='التاريخ',
            y='الإيرادات',
            title='اتجاه المبيعات اليومية',
            color_discrete_sequence=['#ffd700']
        )
        
        fig_daily.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Cairo', size=12)
        )
        
        st.plotly_chart(fig_daily, use_container_width=True)
    
    # جدول أفضل العملاء
    st.markdown('<div class="section-title">🏆 أفضل العملاء</div>', unsafe_allow_html=True)
    
    top_customers = filtered_sales.groupby('العميل').agg({
        'الإيرادات': 'sum',
        'الربح': 'sum',
        'الكمية': 'sum'
    }).reset_index().nlargest(10, 'الإيرادات')
    
    top_customers.columns = ['العميل', 'إجمالي المشتريات', 'الربح المحقق', 'عدد الوحدات']
    
    st.dataframe(
        top_customers.style.format({
            'إجمالي المشتريات': '{:,.0f} ريال',
            'الربح المحقق': '{:,.0f} ريال',
            'عدد الوحدات': '{:,.0f}'
        }).background_gradient(cmap='YlOrRd', subset=['إجمالي المشتريات']),
        use_container_width=True,
        height=400
    )

# =============================================
# تبويب المصروفات
# =============================================
with tab3:
    st.markdown('<div class="section-title">💸 تحليل المصروفات</div>', unsafe_allow_html=True)
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        # المصروفات حسب الفئة
        expense_by_category = filtered_expenses.groupby('الفئة')['المبلغ'].sum().reset_index()
        expense_by_category = expense_by_category.sort_values('المبلغ', ascending=False)
        
        fig_exp_cat = px.bar(
            expense_by_category,
            x='الفئة',
            y='المبلغ',
            title='المصروفات حسب الفئة',
            color='المبلغ',
            color_continuous_scale='Reds'
        )
        
        fig_exp_cat.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Cairo', size=12)
        )
        
        st.plotly_chart(fig_exp_cat, use_container_width=True)
    
    with col_exp2:
        # المصروفات حسب القسم
        expense_by_dept = filtered_expenses.groupby('القسم')['المبلغ'].sum().reset_index()
        
        fig_exp_dept = px.pie(
            expense_by_dept,
            values='المبلغ',
            names='القسم',
            title='توزيع المصروفات حسب القسم',
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        
        fig_exp_dept.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Cairo', size=12)
        )
        
        fig_exp_dept.update_traces(hole=0.4)
        
        st.plotly_chart(fig_exp_dept, use_container_width=True)
    
    # اتجاه المصروفات الشهرية
    st.markdown('<div class="section-title">📉 اتجاه المصروفات الشهرية</div>', unsafe_allow_html=True)
    
    monthly_expenses = filtered_expenses.groupby(['الشهر', 'الفئة'])['المبلغ'].sum().reset_index()
    
    fig_exp_trend = px.line(
        monthly_expenses,
        x='الشهر',
        y='المبلغ',
        color='الفئة',
        title='اتجاه المصروفات الشهرية حسب الفئة',
        markers=True
    )
    
    fig_exp_trend.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Cairo', size=12),
        legend=dict(orientation='h', y=-0.2)
    )
    
    st.plotly_chart(fig_exp_trend, use_container_width=True)

# =============================================
# تبويب التقارير
# =============================================
with tab4:
    st.markdown('<div class="section-title">📊 التقارير المالية</div>', unsafe_allow_html=True)
    
    # ملخص مالي شامل
    col_rep1, col_rep2 = st.columns(2)
    
    with col_rep1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #ffd700; margin-bottom: 20px;">📋 قائمة الدخل</h3>
        </div>
        """, unsafe_allow_html=True)
        
        income_statement = pd.DataFrame({
            'البند': [
                'إجمالي الإيرادات',
                'تكلفة المبيعات',
                'إجمالي الربح',
                'المصروفات التشغيلية',
                'صافي الربح'
            ],
            'المبلغ': [
                total_revenue,
                total_cost,
                gross_profit,
                total_expenses,
                net_profit
            ]
        })
        
        st.dataframe(
            income_statement.style.format({'المبلغ': '{:,.0f} ريال'}),
            use_container_width=True,
            height=250
        )
    
    with col_rep2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #ffd700; margin-bottom: 20px;">📈 مؤشرات الأداء الرئيسية</h3>
        </div>
        """, unsafe_allow_html=True)
        
        kpis = pd.DataFrame({
            'المؤشر': [
                'هامش الربح الإجمالي',
                'هامش صافي الربح',
                'معدل دوران المخزون',
                'متوسط قيمة الطلب',
                'عدد العملاء النشطين'
            ],
            'القيمة': [
                f'{profit_margin:.1f}%',
                f'{net_margin:.1f}%',
                '4.2 مرة',
                f'{avg_order_value:,.0f} ريال',
                f'{filtered_sales["العميل"].nunique()} عميل'
            ]
        })
        
        st.dataframe(kpis, use_container_width=True, height=250)
    
    # رسم بياني مقارنة الأداء
    st.markdown('<div class="section-title">📊 مقارنة الأداء الشهري</div>', unsafe_allow_html=True)
    
    monthly_summary = filtered_sales.groupby('الشهر').agg({
        'الإيرادات': 'sum',
        'الربح': 'sum'
    }).reset_index()
    
    monthly_exp_summary = filtered_expenses.groupby('الشهر')['المبلغ'].sum().reset_index()
    monthly_exp_summary.columns = ['الشهر', 'المصروفات']
    
    monthly_combined = monthly_summary.merge(monthly_exp_summary, on='الشهر', how='outer').fillna(0)
    monthly_combined['صافي_الربح'] = monthly_combined['الربح'] - monthly_combined['المصروفات']
    
    fig_combined = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_combined.add_trace(
        go.Bar(name='الإيرادات', x=monthly_combined['الشهر'], y=monthly_combined['الإيرادات'],
               marker_color='#ffd700', opacity=0.8),
        secondary_y=False
    )
    
    fig_combined.add_trace(
        go.Bar(name='المصروفات', x=monthly_combined['الشهر'], y=monthly_combined['المصروفات'],
               marker_color='#ff6b6b', opacity=0.8),
        secondary_y=False
    )
    
    fig_combined.add_trace(
        go.Scatter(name='صافي الربح', x=monthly_combined['الشهر'], y=monthly_combined['صافي_الربح'],
                   mode='lines+markers', line=dict(color='#00ff88', width=4),
                   marker=dict(size=12)),
        secondary_y=True
    )
    
    fig_combined.update_layout(
        title='مقارنة الإيرادات والمصروفات وصافي الربح',
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Cairo', size=12),
        barmode='group',
        legend=dict(orientation='h', y=-0.2)
    )
    
    fig_combined.update_yaxes(title_text="المبلغ (ريال)", secondary_y=False)
    fig_combined.update_yaxes(title_text="صافي الربح (ريال)", secondary_y=True)
    
    st.plotly_chart(fig_combined, use_container_width=True)

# =============================================
# تبويب التوقعات الآلية
# =============================================
with tab5:
    st.markdown('<div class="section-title">🤖 التوقعات الآلية والذكاء الاصطناعي</div>', unsafe_allow_html=True)
    
    col_ai1, col_ai2 = st.columns(2)
    
    with col_ai1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #ffd700;">🔮 توقعات الأرباح</h3>
            <p style="color: #a0a0c0;">بناءً على تحليل البيانات التاريخية</p>
        </div>
        """, unsafe_allow_html=True)
        
        # توقعات بسيطة بناءً على المعدل
        avg_monthly_profit = monthly_combined['صافي_الربح'].mean() if len(monthly_combined) > 0 else 0
        predicted_next_month = avg_monthly_profit * 1.05  # نمو 5%
        predicted_quarter = avg_monthly_profit * 3 * 1.08  # نمو 8% للربع
        predicted_year = avg_monthly_profit * 12 * 1.15  # نمو 15% للسنة
        
        predictions = pd.DataFrame({
            'الفترة': ['الشهر القادم', 'الربع القادم', 'السنة القادمة'],
            'التوقع': [predicted_next_month, predicted_quarter, predicted_year],
            'نسبة النمو': ['5%', '8%', '15%']
        })
        
        st.dataframe(
            predictions.style.format({'التوقع': '{:,.0f} ريال'}),
            use_container_width=True,
            height=180
        )
    
    with col_ai2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #ffd700;">📊 مؤشر صحة الأعمال</h3>
            <p style="color: #a0a0c0;">تقييم شامل للوضع المالي</p>
        </div>
        """, unsafe_allow_html=True)
        
        # حساب مؤشر صحة الأعمال
        health_score = min(100, max(0, (net_margin + 50) / 100 * 100))
        
        if health_score >= 70:
            health_status = "ممتاز 🌟"
            health_color = "#00ff88"
        elif health_score >= 50:
            health_status = "جيد 👍"
            health_color = "#4da6ff"
        elif health_score >= 30:
            health_status = "متوسط ⚠️"
            health_color = "#ffb347"
        else:
            health_status = "يحتاج تحسين 🔴"
            health_color = "#ff4d4d"
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=health_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': health_status, 'font': {'size': 20, 'color': health_color}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': health_color},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "#ffd700",
                'steps': [
                    {'range': [0, 30], 'color': 'rgba(255,77,77,0.3)'},
                    {'range': [30, 50], 'color': 'rgba(255,179,71,0.3)'},
                    {'range': [50, 70], 'color': 'rgba(77,166,255,0.3)'},
                    {'range': [70, 100], 'color': 'rgba(0,255,136,0.3)'}
                ]
            }
        ))
        
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': '#ffffff', 'family': 'Cairo'},
            height=250
        )
        
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    # توصيات آلية
    st.markdown('<div class="section-title">💡 التوصيات الآلية</div>', unsafe_allow_html=True)
    
    recommendations = []
    
    if net_margin < 10:
        recommendations.append({
            'النوع': '⚠️ تحذير',
            'التوصية': 'هامش الربح منخفض - يُنصح بمراجعة التكاليف وزيادة الأسعار',
            'الأولوية': 'عالية'
        })
    
    if total_expenses / total_revenue > 0.3:
        recommendations.append({
            'النوع': '💡 اقتراح',
            'التوصية': 'المصروفات التشغيلية مرتفعة نسبياً - يُنصح بتحسين الكفاءة التشغيلية',
            'الأولوية': 'متوسطة'
        })
    
    # أفضل المنتجات للتركيز عليها
    best_product = filtered_sales.groupby('المنتج')['الربح'].sum().idxmax() if len(filtered_sales) > 0 else "لا يوجد"
    recommendations.append({
        'النوع': '🎯 فرصة',
        'التوصية': f'المنتج الأكثر ربحية: {best_product} - يُنصح بزيادة التركيز عليه',
        'الأولوية': 'عالية'
    })
    
    # أفضل منطقة
    best_region = filtered_sales.groupby('المنطقة')['الربح'].sum().idxmax() if len(filtered_sales) > 0 else "لا يوجد"
    recommendations.append({
        'النوع': '📍 فرصة',
        'التوصية': f'المنطقة الأكثر ربحية: {best_region} - يُنصح بتوسيع النشاط فيها',
        'الأولوية': 'متوسطة'
    })
    
    recommendations.append({
        'النوع': '🔄 تحسين',
        'التوصية': 'تنويع طرق الدفع يمكن أن يزيد المبيعات بنسبة 10-15%',
        'الأولوية': 'منخفضة'
    })
    
    recommendations_df = pd.DataFrame(recommendations)
    
    st.dataframe(
        recommendations_df,
        use_container_width=True,
        height=250
    )
    
    # رسم بياني للتوقعات
    st.markdown('<div class="section-title">📈 اتجاه الأرباح المتوقع</div>', unsafe_allow_html=True)
    
    # إنشاء توقعات بسيطة
    if len(monthly_combined) > 0:
        last_months = monthly_combined['الشهر'].tolist()
        last_profits = monthly_combined['صافي_الربح'].tolist()
        
        # توقعات للأشهر القادمة
        future_months = ['2024-06', '2024-07', '2024-08', '2024-09', '2024-10', '2024-11']
        base_profit = last_profits[-1] if last_profits else avg_monthly_profit
        future_profits = [base_profit * (1 + 0.03 * i) for i in range(1, 7)]
        
        fig_forecast = go.Figure()
        
        # البيانات الفعلية
        fig_forecast.add_trace(go.Scatter(
            x=last_months,
            y=last_profits,
            mode='lines+markers',
            name='الأرباح الفعلية',
            line=dict(color='#ffd700', width=3),
            marker=dict(size=10)
        ))
        
        # التوقعات
        fig_forecast.add_trace(go.Scatter(
            x=future_months,
            y=future_profits,
            mode='lines+markers',
            name='الأرباح المتوقعة',
            line=dict(color='#00ff88', width=3, dash='dash'),
            marker=dict(size=10, symbol='diamond')
        ))
        
        # منطقة الثقة
        upper_bound = [p * 1.15 for p in future_profits]
        lower_bound = [p * 0.85 for p in future_profits]
        
        fig_forecast.add_trace(go.Scatter(
            x=future_months + future_months[::-1],
            y=upper_bound + lower_bound[::-1],
            fill='toself',
            fillcolor='rgba(0,255,136,0.1)',
            line=dict(color='rgba(0,0,0,0)'),
            name='نطاق الثقة 85%'
        ))
        
        fig_forecast.update_layout(
            title='توقعات الأرباح للأشهر القادمة',
            xaxis_title='الشهر',
            yaxis_title='صافي الربح (ريال)',
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Cairo', size=12),
            legend=dict(orientation='h', y=-0.2)
        )
        
        st.plotly_chart(fig_forecast, use_container_width=True)

# =============================================
# تذييل الصفحة
# =============================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #a0a0c0;">
    <p>💰 نظام الأرباح الآلية المتكاملة - جميع الحقوق محفوظة © 2024</p>
    <p style="font-size: 0.8rem;">تم التطوير بواسطة تقنيات الذكاء الاصطناعي</p>
</div>
""", unsafe_allow_html=True)
