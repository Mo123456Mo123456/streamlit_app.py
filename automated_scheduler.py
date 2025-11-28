"""
نظام الجدولة الآلية للتداول
يعمل في الخلفية لتنفيذ التداول تلقائيًا
"""

import schedule
import time
import threading
from datetime import datetime
from ai_trading_bot import AITradingBot
from config import get_config
import json
from pathlib import Path


class AutomatedScheduler:
    """نظام الجدولة الآلية"""
    
    def __init__(self, bot: AITradingBot, symbols: list):
        self.bot = bot
        self.symbols = symbols
        self.config = get_config()
        self.is_running = False
        self.thread = None
        
    def run_trading_cycle(self):
        """تنفيذ دورة تداول واحدة"""
        try:
            print(f"\n🔄 بدء دورة التداول الآلي - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # التأكد من تدريب النموذج
            if not self.bot.is_trained:
                print("🔄 تدريب النموذج...")
                self.bot.train_model()
            
            # تنفيذ التداول
            current_prices = {}
            
            for symbol in self.symbols:
                try:
                    # جلب بيانات السوق
                    df = self.bot.generate_market_data(symbol, 100)
                    current_price = df['close'].iloc[-1]
                    current_prices[symbol] = current_price
                    
                    # تحليل الإشارات
                    signal_data = self.bot.analyze_signal(df)
                    
                    # التحقق من مستوى الثقة
                    min_confidence = self.config['trading']['min_confidence']
                    if signal_data['confidence'] >= min_confidence:
                        # تنفيذ التداول
                        self.bot.execute_trade(symbol, signal_data, current_price)
                    
                except Exception as e:
                    print(f"⚠️ خطأ في معالجة {symbol}: {e}")
                    continue
            
            # تحديث قيمة المحفظة
            self.bot.update_portfolio_value(current_prices)
            
            # حفظ الحالة
            self.bot.save_state()
            
            # عرض النتائج
            metrics = self.bot.get_performance_metrics()
            print(f"✅ اكتملت دورة التداول")
            print(f"   قيمة المحفظة: ${metrics['portfolio_value']:,.2f}")
            print(f"   العائد: {metrics['total_return_pct']:.2f}%")
            
            # التحقق من حدود الخسارة اليومية
            daily_loss_limit = self.config['security']['max_daily_loss']
            if metrics['total_return_pct'] < -daily_loss_limit * 100:
                print(f"⚠️ تحذير: تجاوز حد الخسارة اليومية!")
                self.stop()
            
        except Exception as e:
            print(f"❌ خطأ في دورة التداول: {e}")
    
    def start(self, interval_minutes: int = 15):
        """بدء الجدولة الآلية"""
        if self.is_running:
            print("⚠️ الجدولة تعمل بالفعل!")
            return
        
        self.is_running = True
        
        # جدولة المهام
        schedule.every(interval_minutes).minutes.do(self.run_trading_cycle)
        
        # تشغيل في thread منفصل
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        
        print(f"✅ تم بدء الجدولة الآلية (كل {interval_minutes} دقيقة)")
    
    def _run_scheduler(self):
        """تشغيل الجدولة في حلقة"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # التحقق كل دقيقة
    
    def stop(self):
        """إيقاف الجدولة"""
        self.is_running = False
        schedule.clear()
        print("⏹️ تم إيقاف الجدولة الآلية")
    
    def run_once(self):
        """تشغيل دورة واحدة فقط"""
        self.run_trading_cycle()


# مثال على الاستخدام
if __name__ == "__main__":
    config = get_config()
    
    # إنشاء البوت
    bot = AITradingBot(initial_balance=config['trading']['initial_balance'])
    bot.max_position_size = config['trading']['max_position_size']
    bot.stop_loss_percentage = config['trading']['stop_loss_percentage']
    bot.take_profit_percentage = config['trading']['take_profit_percentage']
    bot.load_state()
    
    # إنشاء الجدولة
    scheduler = AutomatedScheduler(
        bot=bot,
        symbols=config['default_symbols']
    )
    
    # بدء الجدولة (كل 15 دقيقة)
    scheduler.start(interval_minutes=15)
    
    # الحفاظ على البرنامج يعمل
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ إيقاف النظام...")
        scheduler.stop()
