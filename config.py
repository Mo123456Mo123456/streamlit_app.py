"""
ملف الإعدادات والتكوين للنظام
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# مسارات الملفات
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'trading_data'
DATA_DIR.mkdir(exist_ok=True)

# إعدادات التداول
TRADING_CONFIG = {
    'initial_balance': float(os.getenv('INITIAL_BALANCE', '10000.0')),
    'max_position_size': float(os.getenv('MAX_POSITION_SIZE', '0.2')),  # 20%
    'stop_loss_percentage': float(os.getenv('STOP_LOSS', '0.05')),  # 5%
    'take_profit_percentage': float(os.getenv('TAKE_PROFIT', '0.10')),  # 10%
    'min_confidence': float(os.getenv('MIN_CONFIDENCE', '0.6')),  # 60%
    'trading_fee': float(os.getenv('TRADING_FEE', '0.001')),  # 0.1%
}

# إعدادات APIs
API_CONFIG = {
    'alpha_vantage_key': os.getenv('ALPHA_VANTAGE_API_KEY', 'demo'),
    'binance_api_key': os.getenv('BINANCE_API_KEY', ''),
    'binance_api_secret': os.getenv('BINANCE_API_SECRET', ''),
    'use_testnet': os.getenv('USE_TESTNET', 'true').lower() == 'true',
}

# إعدادات النموذج
MODEL_CONFIG = {
    'training_days': int(os.getenv('TRAINING_DAYS', '200')),
    'prediction_days': int(os.getenv('PREDICTION_DAYS', '5')),
    'model_type': os.getenv('MODEL_TYPE', 'gradient_boosting'),  # 'random_forest' or 'gradient_boosting'
    'n_estimators': int(os.getenv('N_ESTIMATORS', '100')),
    'learning_rate': float(os.getenv('LEARNING_RATE', '0.1')),
    'max_depth': int(os.getenv('MAX_DEPTH', '5')),
}

# إعدادات الواجهة
UI_CONFIG = {
    'theme': os.getenv('UI_THEME', 'light'),
    'language': os.getenv('UI_LANGUAGE', 'ar'),
    'refresh_interval': int(os.getenv('REFRESH_INTERVAL', '60')),  # ثواني
    'max_trades_display': int(os.getenv('MAX_TRADES_DISPLAY', '100')),
}

# الرموز الافتراضية
DEFAULT_SYMBOLS = os.getenv('DEFAULT_SYMBOLS', 'BTC,ETH,AAPL,GOOGL,MSFT').split(',')

# إعدادات الأمان
SECURITY_CONFIG = {
    'encrypt_trade_data': os.getenv('ENCRYPT_TRADE_DATA', 'false').lower() == 'true',
    'require_2fa': os.getenv('REQUIRE_2FA', 'false').lower() == 'true',
    'max_daily_loss': float(os.getenv('MAX_DAILY_LOSS', '0.20')),  # 20%
    'max_daily_trades': int(os.getenv('MAX_DAILY_TRADES', '50')),
}

# إعدادات الإشعارات
NOTIFICATION_CONFIG = {
    'email_enabled': os.getenv('EMAIL_NOTIFICATIONS', 'false').lower() == 'true',
    'email_smtp_server': os.getenv('EMAIL_SMTP_SERVER', ''),
    'email_smtp_port': int(os.getenv('EMAIL_SMTP_PORT', '587')),
    'email_username': os.getenv('EMAIL_USERNAME', ''),
    'email_password': os.getenv('EMAIL_PASSWORD', ''),
    'email_recipient': os.getenv('EMAIL_RECIPIENT', ''),
    'telegram_enabled': os.getenv('TELEGRAM_NOTIFICATIONS', 'false').lower() == 'true',
    'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
    'telegram_chat_id': os.getenv('TELEGRAM_CHAT_ID', ''),
}

def get_config():
    """الحصول على جميع الإعدادات"""
    return {
        'trading': TRADING_CONFIG,
        'api': API_CONFIG,
        'model': MODEL_CONFIG,
        'ui': UI_CONFIG,
        'security': SECURITY_CONFIG,
        'notifications': NOTIFICATION_CONFIG,
        'default_symbols': DEFAULT_SYMBOLS,
    }
