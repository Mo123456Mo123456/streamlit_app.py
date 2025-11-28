#!/usr/bin/env python3
"""
سكريبت التشغيل الرئيسي
يمكن استخدامه لتشغيل النظام بطرق مختلفة
"""

import argparse
import sys
from pathlib import Path

def run_streamlit():
    """تشغيل واجهة Streamlit"""
    import subprocess
    subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])

def run_bot_cli():
    """تشغيل البوت من سطر الأوامر"""
    from ai_trading_bot import AITradingBot
    from config import get_config
    
    config = get_config()
    bot = AITradingBot(initial_balance=config['trading']['initial_balance'])
    bot.load_state()
    
    print("🤖 نظام التداول الآلي الذكي")
    print("=" * 50)
    
    symbols = input("أدخل الرموز للتداول (مفصولة بفواصل، Enter للافتراضي): ").strip()
    if not symbols:
        symbols = config['default_symbols']
    else:
        symbols = [s.strip().upper() for s in symbols.split(',')]
    
    iterations = input("عدد الدورات (افتراضي: 5): ").strip()
    iterations = int(iterations) if iterations.isdigit() else 5
    
    bot.run_automated_trading(symbols=symbols, iterations=iterations)
    
    # عرض النتائج النهائية
    metrics = bot.get_performance_metrics()
    print("\n" + "=" * 50)
    print("📊 النتائج النهائية:")
    print(f"  قيمة المحفظة: ${metrics['portfolio_value']:,.2f}")
    print(f"  العائد الإجمالي: {metrics['total_return_pct']:.2f}%")
    print(f"  إجمالي الأرباح/الخسائر: ${metrics['total_profit_loss']:,.2f}")
    print(f"  معدل الفوز: {metrics['win_rate']:.1f}%")
    print(f"  إجمالي العمليات: {metrics['total_trades']}")

def run_scheduler():
    """تشغيل الجدولة الآلية"""
    from automated_scheduler import AutomatedScheduler
    from ai_trading_bot import AITradingBot
    from config import get_config
    
    config = get_config()
    
    bot = AITradingBot(initial_balance=config['trading']['initial_balance'])
    bot.max_position_size = config['trading']['max_position_size']
    bot.stop_loss_percentage = config['trading']['stop_loss_percentage']
    bot.take_profit_percentage = config['trading']['take_profit_percentage']
    bot.load_state()
    
    scheduler = AutomatedScheduler(
        bot=bot,
        symbols=config['default_symbols']
    )
    
    interval = input("فترة التداول بالدقائق (افتراضي: 15): ").strip()
    interval = int(interval) if interval.isdigit() else 15
    
    print(f"\n🚀 بدء الجدولة الآلية (كل {interval} دقيقة)...")
    print("اضغط Ctrl+C للإيقاف\n")
    
    scheduler.start(interval_minutes=interval)
    
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ إيقاف النظام...")
        scheduler.stop()

def main():
    parser = argparse.ArgumentParser(description='نظام التداول الآلي الذكي')
    parser.add_argument(
        'mode',
        choices=['ui', 'bot', 'scheduler'],
        help='وضع التشغيل: ui (واجهة), bot (سطر الأوامر), scheduler (جدولة)'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'ui':
        run_streamlit()
    elif args.mode == 'bot':
        run_bot_cli()
    elif args.mode == 'scheduler':
        run_scheduler()

if __name__ == "__main__":
    main()
