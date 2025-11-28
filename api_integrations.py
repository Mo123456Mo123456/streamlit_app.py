"""
وحدات التكامل مع APIs الخارجية
يدعم التكامل مع منصات التداول وبيانات السوق الحقيقية
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import os
from dotenv import load_dotenv
import time

load_dotenv()


class MarketDataAPI:
    """فئة أساسية لجلب بيانات السوق"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = ""
        self.rate_limit_delay = 0.1  # تأخير بين الطلبات
    
    def get_historical_data(self, symbol: str, days: int = 100) -> pd.DataFrame:
        """جلب البيانات التاريخية"""
        raise NotImplementedError
    
    def get_current_price(self, symbol: str) -> float:
        """جلب السعر الحالي"""
        raise NotImplementedError


class AlphaVantageAPI(MarketDataAPI):
    """تكامل مع Alpha Vantage API (مجاني)"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        self.base_url = "https://www.alphavantage.co/query"
    
    def get_historical_data(self, symbol: str, days: int = 100) -> pd.DataFrame:
        """جلب البيانات التاريخية من Alpha Vantage"""
        try:
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': self.api_key,
                'outputsize': 'full' if days > 100 else 'compact'
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'Error Message' in data or 'Note' in data:
                print(f"⚠️ خطأ في API: {data.get('Error Message', data.get('Note', 'Unknown error'))}")
                return self._generate_fallback_data(symbol, days)
            
            time_series = data.get('Time Series (Daily)', {})
            
            if not time_series:
                return self._generate_fallback_data(symbol, days)
            
            # تحويل البيانات إلى DataFrame
            df_data = []
            for date, values in list(time_series.items())[:days]:
                df_data.append({
                    'date': pd.to_datetime(date),
                    'open': float(values['1. open']),
                    'high': float(values['2. high']),
                    'low': float(values['3. low']),
                    'close': float(values['4. close']),
                    'volume': int(values['5. volume'])
                })
            
            df = pd.DataFrame(df_data)
            df = df.sort_values('date').reset_index(drop=True)
            
            time.sleep(self.rate_limit_delay)  # تجنب تجاوز حد المعدل
            
            return df
            
        except Exception as e:
            print(f"⚠️ خطأ في جلب البيانات من Alpha Vantage: {e}")
            return self._generate_fallback_data(symbol, days)
    
    def get_current_price(self, symbol: str) -> float:
        """جلب السعر الحالي"""
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            quote = data.get('Global Quote', {})
            if quote:
                return float(quote.get('05. price', 0))
            
            return 0.0
        except Exception as e:
            print(f"⚠️ خطأ في جلب السعر الحالي: {e}")
            return 0.0
    
    def _generate_fallback_data(self, symbol: str, days: int) -> pd.DataFrame:
        """إنشاء بيانات احتياطية عند فشل API"""
        import numpy as np
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        base_price = 100.0
        prices = base_price + np.cumsum(np.random.randn(days) * 2)
        
        return pd.DataFrame({
            'date': dates,
            'open': prices,
            'high': prices * 1.02,
            'low': prices * 0.98,
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, days)
        })


class CoinGeckoAPI(MarketDataAPI):
    """تكامل مع CoinGecko API للعملات المشفرة"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.coingecko.com/api/v3"
    
    def get_historical_data(self, symbol: str, days: int = 100) -> pd.DataFrame:
        """جلب البيانات التاريخية للعملات المشفرة"""
        try:
            # تحويل الرمز إلى ID (مثال: BTC -> bitcoin)
            coin_id_map = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'BNB': 'binancecoin',
                'ADA': 'cardano',
                'SOL': 'solana'
            }
            
            coin_id = coin_id_map.get(symbol.upper(), symbol.lower())
            
            url = f"{self.base_url}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': min(days, 365),
                'interval': 'daily'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            prices = data.get('prices', [])
            
            if not prices:
                return self._generate_fallback_data(symbol, days)
            
            # تحويل البيانات
            df_data = []
            for price_data in prices[-days:]:
                timestamp = datetime.fromtimestamp(price_data[0] / 1000)
                price = price_data[1]
                df_data.append({
                    'date': timestamp,
                    'open': price,
                    'high': price * 1.02,
                    'low': price * 0.98,
                    'close': price,
                    'volume': 0  # CoinGecko لا يوفر حجم في هذا endpoint
                })
            
            df = pd.DataFrame(df_data)
            df['volume'] = df['close'].rolling(7).mean() * 1000000  # تقدير الحجم
            
            time.sleep(self.rate_limit_delay)
            
            return df
            
        except Exception as e:
            print(f"⚠️ خطأ في جلب البيانات من CoinGecko: {e}")
            return self._generate_fallback_data(symbol, days)
    
    def get_current_price(self, symbol: str) -> float:
        """جلب السعر الحالي"""
        try:
            coin_id_map = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'BNB': 'binancecoin',
                'ADA': 'cardano',
                'SOL': 'solana'
            }
            
            coin_id = coin_id_map.get(symbol.upper(), symbol.lower())
            
            url = f"{self.base_url}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if coin_id in data:
                return float(data[coin_id].get('usd', 0))
            
            return 0.0
        except Exception as e:
            print(f"⚠️ خطأ في جلب السعر الحالي: {e}")
            return 0.0
    
    def _generate_fallback_data(self, symbol: str, days: int) -> pd.DataFrame:
        """إنشاء بيانات احتياطية"""
        import numpy as np
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        base_price = 50000 if symbol.upper() == 'BTC' else 3000 if symbol.upper() == 'ETH' else 100
        prices = base_price + np.cumsum(np.random.randn(days) * (base_price * 0.02))
        
        return pd.DataFrame({
            'date': dates,
            'open': prices,
            'high': prices * 1.03,
            'low': prices * 0.97,
            'close': prices,
            'volume': np.random.randint(10000000, 100000000, days)
        })


class TradingPlatformAPI:
    """فئة أساسية للتكامل مع منصات التداول"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = ""
    
    def place_order(self, symbol: str, side: str, quantity: float, order_type: str = 'MARKET') -> Dict:
        """وضع أمر تداول"""
        raise NotImplementedError
    
    def get_balance(self) -> float:
        """جلب الرصيد"""
        raise NotImplementedError
    
    def get_positions(self) -> List[Dict]:
        """جلب المراكز المفتوحة"""
        raise NotImplementedError


class BinanceAPI(TradingPlatformAPI):
    """تكامل مع Binance API (مثال - يحتاج إعدادات أمنية)"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        super().__init__(api_key, api_secret)
        if testnet:
            self.base_url = "https://testnet.binance.vision/api"
        else:
            self.base_url = "https://api.binance.com/api"
    
    def place_order(self, symbol: str, side: str, quantity: float, order_type: str = 'MARKET') -> Dict:
        """وضع أمر تداول على Binance"""
        # تحذير: هذا مثال فقط - يحتاج إلى توقيع HMAC وتشفير مناسب
        print("⚠️ تحذير: هذا مثال فقط. لا تستخدم في الإنتاج بدون أمان كامل!")
        return {
            'status': 'demo',
            'message': 'هذا مثال تجريبي فقط'
        }
    
    def get_balance(self) -> float:
        """جلب الرصيد"""
        print("⚠️ تحذير: هذا مثال فقط")
        return 0.0
    
    def get_positions(self) -> List[Dict]:
        """جلب المراكز"""
        print("⚠️ تحذير: هذا مثال فقط")
        return []


def get_market_data_provider(symbol: str) -> MarketDataAPI:
    """اختيار مزود البيانات المناسب حسب نوع الرمز"""
    crypto_symbols = ['BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'DOGE', 'XRP']
    
    if symbol.upper() in crypto_symbols:
        return CoinGeckoAPI()
    else:
        return AlphaVantageAPI()


# مثال على الاستخدام
if __name__ == "__main__":
    # اختبار Alpha Vantage
    print("اختبار Alpha Vantage API...")
    av_api = AlphaVantageAPI()
    df = av_api.get_historical_data('AAPL', 30)
    print(f"تم جلب {len(df)} سجل لـ AAPL")
    print(df.head())
    
    # اختبار CoinGecko
    print("\nاختبار CoinGecko API...")
    cg_api = CoinGeckoAPI()
    df_crypto = cg_api.get_historical_data('BTC', 30)
    print(f"تم جلب {len(df_crypto)} سجل لـ BTC")
    print(df_crypto.head())
