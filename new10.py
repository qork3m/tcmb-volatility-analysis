import pandas as pd
import matplotlib.pyplot as plt
import evds
import yfinance as yf
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('EVDS_API_KEY')


def get_evds_series(api_key, series_codes, startdate, enddate, frequency=5):
    tcmb = evds.evdsAPI(api_key)
    df = tcmb.get_data(series_codes, startdate=startdate,
                       enddate=enddate, frequency=frequency)
    df["Tarih"] = pd.to_datetime(df["Tarih"])
    df.set_index("Tarih", inplace=True)
    return df


def get_stock_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end)
    return df


# USD/TRY verilerini Yfinance API'ını kullanarak çekiyoruz.
df_exchange_rates = get_stock_data('TRY=X', '2018-01-01', '2026-06-29')

# TCMB politika faiz oranlarını EVDS API'ını kullanarak çekiyoruz.
df_interest_rates = get_evds_series(
    api_key, ['TP.BISPOLFAIZ.TUR'], '01-01-2018', '29-06-2026')

# volatilite DataFrame'ini hesaplıyoruz.
volatility = df_exchange_rates['Close'].pct_change(1).rolling(30).std()

# "diff" değişkenine bir önceki döneme göre politika faiz kararında bir değişiklik var mı onu atıyoruz.
diff = df_interest_rates['TP_BISPOLFAIZ_TUR'].diff()

# Yukarıdaki diff değişkenine atadıklarımızı "NaN" içermeyecek ve "diff" 0 olmayacak şekilde atıyoruz.
df_interest_rate_change = df_interest_rates[(diff != 0) & (diff.notna())]

# çıkan verilerin tarihlerini farklı bir DF'e atıyoruz.
df_interest_rate_change_dates = df_interest_rate_change.index

# Volatilite için çizgi grafiği çiziyoruz.
plt.plot(volatility.index, volatility, color='blue')

# Her bir endeks için tarihleri döndürüp dikey çizgi ekliyoruz o tarihlere.
for tarih in df_interest_rate_change_dates:
    plt.axvline(x=tarih, color='red', linestyle='--', linewidth=1, alpha=0.5)

# Grafiğin Başlığı
plt.title("CBRT Rate Decisions and USD/TRY Volatility (2018-2026)",
          fontsize=14, fontweight='bold')

# Grafiğin Y ekseni labelı
plt.ylabel("USD/TRY 30-Day Rolling Volatility",
           color='blue', fontsize=11, fontstyle='italic')

# Kaynağı belirtiyoruz.
plt.figtext(0.5, 0.02, "Sources: TCMB, Yfinance",
            ha="center", fontsize=10, color="gray", fontstyle='italic')

plt.tight_layout()
plt.savefig(r'C:\Users\gkara\OneDrive\Desktop\Code\tcmb-volatility-analysis\tcmb-volatility-analysis\volatility.png',
            dpi=150, bbox_inches='tight')
plt.show()
