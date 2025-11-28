"""
نظام التداول الآلي الذكي - AI Trading Bot
يعمل تلقائيًا لتحليل الأسواق واتخاذ قرارات التداول وجمع الأرباح
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_squared_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available. Using simplified prediction model.")


class AITradingBot:
    """نظام التداول الآلي الذكي"""
    
    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.portfolio_value = initial_balance
        self.positions = {}  # {symbol: {'quantity': int, 'avg_price': float}}
        self.trade_history = []
        self.profit_loss = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        
        # AI Model
        self.model = None
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.is_trained = False
        
        # Risk Management
        self.max_position_size = 0.2  # 20% of portfolio per position
        self.stop_loss_percentage = 0.05  # 5% stop loss
        self.take_profit_percentage = 0.10  # 10% take profit
        
        # Data storage
        self.data_dir = Path(__file__).parent / 'trading_data'
        self.data_dir.mkdir(exist_ok=True)
        
    def generate_market_data(self, symbol: str, days: int = 100) -> pd.DataFrame:
        """إنشاء بيانات سوق محاكاة (يمكن استبدالها ببيانات حقيقية من API)"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # محاكاة حركة السعر مع اتجاهات عشوائية
        np.random.seed(hash(symbol) % 2**32)
        base_price = 100.0
        returns = np.random.normal(0.001, 0.02, days)  # متوسط عائد يومي 0.1%
        prices = [base_price]
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        # إضافة مؤشرات تقنية
        df = pd.DataFrame({
            'date': dates,
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, days)
        })
        
        # حساب المؤشرات التقنية
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['rsi'] = self._calculate_rsi(df['close'], 14)
        df['macd'], df['macd_signal'] = self._calculate_macd(df['close'])
        df['bb_upper'], df['bb_lower'] = self._calculate_bollinger_bands(df['close'])
        
        return df.fillna(method='bfill').fillna(method='ffill')
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """حساب مؤشر RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        """حساب مؤشر MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        return macd, macd_signal
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> tuple:
        """حساب Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, lower
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """تحضير الميزات للتدريب"""
        features_df = df.copy()
        
        # ميزات إضافية
        features_df['price_change'] = features_df['close'].pct_change()
        features_df['volume_change'] = features_df['volume'].pct_change()
        features_df['price_volatility'] = features_df['close'].rolling(10).std()
        features_df['sma_cross'] = (features_df['sma_20'] > features_df['sma_50']).astype(int)
        
        # إزالة القيم المفقودة
        features_df = features_df.dropna()
        
        return features_df
    
    def train_model(self, symbol: str = 'BTC', days: int = 200):
        """تدريب نموذج الذكاء الاصطناعي"""
        if not SKLEARN_AVAILABLE:
            self.is_trained = True
            return
        
        print(f"🔄 تدريب النموذج على بيانات {symbol}...")
        
        # الحصول على البيانات
        df = self.generate_market_data(symbol, days)
        df = self.prepare_features(df)
        
        # إعداد البيانات للتدريب
        feature_columns = ['sma_20', 'sma_50', 'rsi', 'macd', 'macd_signal', 
                          'bb_upper', 'bb_lower', 'price_change', 'volume_change', 
                          'price_volatility', 'sma_cross']
        
        # الهدف: السعر المستقبلي (بعد 5 أيام)
        future_days = 5
        df['future_price'] = df['close'].shift(-future_days)
        df = df.dropna()
        
        X = df[feature_columns].values
        y = df['future_price'].values
        
        if len(X) < 50:
            print("⚠️ بيانات غير كافية للتدريب")
            self.is_trained = False
            return
        
        # تقسيم البيانات
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # تطبيع البيانات
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # تدريب النموذج
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # تقييم النموذج
        y_pred = self.model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"✅ تم تدريب النموذج بنجاح!")
        print(f"   MSE: {mse:.2f}, R² Score: {r2:.3f}")
        
        self.is_trained = True
    
    def predict_price(self, df: pd.DataFrame) -> Optional[float]:
        """التنبؤ بالسعر المستقبلي باستخدام الذكاء الاصطناعي"""
        if not self.is_trained or self.model is None:
            # استخدام نموذج بسيط إذا لم يكن النموذج مدربًا
            current_price = df['close'].iloc[-1]
            sma_20 = df['sma_20'].iloc[-1]
            trend = 1.02 if sma_20 > current_price else 0.98
            return current_price * trend
        
        try:
            df_features = self.prepare_features(df)
            if len(df_features) == 0:
                return None
            
            feature_columns = ['sma_20', 'sma_50', 'rsi', 'macd', 'macd_signal', 
                            'bb_upper', 'bb_lower', 'price_change', 'volume_change', 
                            'price_volatility', 'sma_cross']
            
            latest_features = df_features[feature_columns].iloc[-1].values.reshape(1, -1)
            latest_features_scaled = self.scaler.transform(latest_features)
            
            predicted_price = self.model.predict(latest_features_scaled)[0]
            return predicted_price
        except Exception as e:
            print(f"⚠️ خطأ في التنبؤ: {e}")
            return df['close'].iloc[-1] * 1.01
    
    def analyze_signal(self, df: pd.DataFrame) -> Dict[str, float]:
        """تحليل إشارات التداول"""
        if len(df) < 50:
            return {'signal': 0, 'confidence': 0}
        
        current_price = df['close'].iloc[-1]
        predicted_price = self.predict_price(df)
        
        # حساب الإشارة
        price_change_pct = (predicted_price - current_price) / current_price
        
        # تحليل المؤشرات
        rsi = df['rsi'].iloc[-1]
        macd = df['macd'].iloc[-1]
        macd_signal = df['macd_signal'].iloc[-1]
        sma_20 = df['sma_20'].iloc[-1]
        sma_50 = df['sma_50'].iloc[-1]
        
        # حساب الثقة
        confidence = 0.5
        
        # RSI
        if rsi < 30:  # Oversold
            confidence += 0.15
        elif rsi > 70:  # Overbought
            confidence -= 0.15
        
        # MACD
        if macd > macd_signal:
            confidence += 0.1
        else:
            confidence -= 0.1
        
        # Moving Average Crossover
        if sma_20 > sma_50:
            confidence += 0.1
        
        confidence = max(0.1, min(0.95, confidence))
        
        # تحديد الإشارة
        if price_change_pct > 0.02 and confidence > 0.6:  # Buy signal
            signal = 1
        elif price_change_pct < -0.02 and confidence > 0.6:  # Sell signal
            signal = -1
        else:
            signal = 0  # Hold
        
        return {
            'signal': signal,
            'confidence': confidence,
            'predicted_change': price_change_pct,
            'current_price': current_price,
            'predicted_price': predicted_price
        }
    
    def execute_trade(self, symbol: str, signal_data: Dict, current_price: float):
        """تنفيذ عملية التداول"""
        signal = signal_data['signal']
        confidence = signal_data['confidence']
        
        if signal == 0:  # Hold
            return
        
        # حساب حجم المركز
        max_investment = self.balance * self.max_position_size
        position_value = max_investment * confidence
        
        if signal == 1:  # Buy
            if symbol in self.positions:
                # إضافة إلى المركز الموجود
                existing = self.positions[symbol]
                total_value = existing['quantity'] * existing['avg_price'] + position_value
                total_quantity = existing['quantity'] + (position_value / current_price)
                self.positions[symbol] = {
                    'quantity': total_quantity,
                    'avg_price': total_value / total_quantity
                }
            else:
                # مركز جديد
                quantity = position_value / current_price
                self.positions[symbol] = {
                    'quantity': quantity,
                    'avg_price': current_price
                }
            
            self.balance -= position_value
            self.total_trades += 1
            
            trade_record = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'action': 'BUY',
                'quantity': position_value / current_price,
                'price': current_price,
                'value': position_value,
                'confidence': confidence
            }
            self.trade_history.append(trade_record)
            print(f"✅ شراء {symbol}: {position_value:.2f} @ {current_price:.2f}")
        
        elif signal == -1:  # Sell
            if symbol in self.positions:
                position = self.positions[symbol]
                quantity_to_sell = min(position['quantity'], position_value / current_price)
                
                if quantity_to_sell > 0:
                    sell_value = quantity_to_sell * current_price
                    profit = (current_price - position['avg_price']) * quantity_to_sell
                    
                    self.balance += sell_value
                    self.profit_loss += profit
                    
                    if profit > 0:
                        self.winning_trades += 1
                    else:
                        self.losing_trades += 1
                    
                    # تحديث المركز
                    remaining_quantity = position['quantity'] - quantity_to_sell
                    if remaining_quantity > 0.001:
                        self.positions[symbol]['quantity'] = remaining_quantity
                    else:
                        del self.positions[symbol]
                    
                    self.total_trades += 1
                    
                    trade_record = {
                        'timestamp': datetime.now().isoformat(),
                        'symbol': symbol,
                        'action': 'SELL',
                        'quantity': quantity_to_sell,
                        'price': current_price,
                        'value': sell_value,
                        'profit': profit,
                        'confidence': confidence
                    }
                    self.trade_history.append(trade_record)
                    print(f"✅ بيع {symbol}: {quantity_to_sell:.4f} @ {current_price:.2f} | ربح: {profit:.2f}")
    
    def update_portfolio_value(self, current_prices: Dict[str, float]):
        """تحديث قيمة المحفظة"""
        portfolio_value = self.balance
        
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                portfolio_value += position['quantity'] * current_prices[symbol]
        
        self.portfolio_value = portfolio_value
    
    def get_performance_metrics(self) -> Dict:
        """الحصول على مقاييس الأداء"""
        total_return = ((self.portfolio_value - self.initial_balance) / self.initial_balance) * 100
        
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        return {
            'initial_balance': self.initial_balance,
            'current_balance': self.balance,
            'portfolio_value': self.portfolio_value,
            'total_profit_loss': self.profit_loss,
            'total_return_pct': total_return,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            'positions': len(self.positions)
        }
    
    def save_state(self):
        """حفظ حالة النظام"""
        state = {
            'balance': self.balance,
            'portfolio_value': self.portfolio_value,
            'positions': self.positions,
            'trade_history': self.trade_history[-100:],  # آخر 100 عملية
            'profit_loss': self.profit_loss,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades
        }
        
        state_file = self.data_dir / 'bot_state.json'
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def load_state(self):
        """تحميل حالة النظام"""
        state_file = self.data_dir / 'bot_state.json'
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                self.balance = state.get('balance', self.initial_balance)
                self.portfolio_value = state.get('portfolio_value', self.initial_balance)
                self.positions = state.get('positions', {})
                self.trade_history = state.get('trade_history', [])
                self.profit_loss = state.get('profit_loss', 0.0)
                self.total_trades = state.get('total_trades', 0)
                self.winning_trades = state.get('winning_trades', 0)
                self.losing_trades = state.get('losing_trades', 0)
    
    def run_automated_trading(self, symbols: List[str] = ['BTC', 'ETH', 'AAPL'], iterations: int = 10):
        """تشغيل التداول الآلي"""
        print("🚀 بدء التداول الآلي...")
        
        if not self.is_trained:
            self.train_model()
        
        for iteration in range(iterations):
            print(f"\n📊 التكرار {iteration + 1}/{iterations}")
            
            current_prices = {}
            
            for symbol in symbols:
                # الحصول على بيانات السوق
                df = self.generate_market_data(symbol, 100)
                current_price = df['close'].iloc[-1]
                current_prices[symbol] = current_price
                
                # تحليل الإشارات
                signal_data = self.analyze_signal(df)
                
                print(f"\n{symbol}:")
                print(f"  السعر الحالي: {current_price:.2f}")
                print(f"  السعر المتوقع: {signal_data['predicted_price']:.2f}")
                print(f"  الإشارة: {'شراء' if signal_data['signal'] == 1 else 'بيع' if signal_data['signal'] == -1 else 'انتظار'}")
                print(f"  الثقة: {signal_data['confidence']*100:.1f}%")
                
                # تنفيذ التداول
                self.execute_trade(symbol, signal_data, current_price)
            
            # تحديث قيمة المحفظة
            self.update_portfolio_value(current_prices)
            
            # حفظ الحالة
            self.save_state()
            
            # عرض الأداء
            metrics = self.get_performance_metrics()
            print(f"\n💰 الأداء:")
            print(f"  قيمة المحفظة: ${metrics['portfolio_value']:.2f}")
            print(f"  العائد الإجمالي: {metrics['total_return_pct']:.2f}%")
            print(f"  إجمالي الأرباح/الخسائر: ${metrics['total_profit_loss']:.2f}")
            print(f"  معدل الفوز: {metrics['win_rate']:.1f}%")
        
        print("\n✅ اكتمل التداول الآلي!")


if __name__ == "__main__":
    # إنشاء وتشغيل البوت
    bot = AITradingBot(initial_balance=10000.0)
    bot.load_state()
    bot.run_automated_trading(symbols=['BTC', 'ETH', 'AAPL'], iterations=5)
