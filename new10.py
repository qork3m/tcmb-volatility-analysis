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


df_exchange_rates = get_stock_data('TRY=X', '2018-01-01', '2026-06-29')
df_interest_rates = get_evds_series(
    api_key, ['TP.BISPOLFAIZ.TUR'], '01-01-2018', '29-06-2026')
df_exchange_rates_monthly = df_exchange_rates['Close'].resample(
    'MS').mean()
df_merged = pd.merge(df_interest_rates, df_exchange_rates_monthly,
                     right_index=True, left_index=True, how='inner')

volatility = df_exchange_rates['Close'].pct_change(1).rolling(30).std()

diff = df_interest_rates['TP_BISPOLFAIZ_TUR'].diff()
df_interest_rate_change = df_interest_rates[(diff != 0) & (diff.notna())]
df_interest_rate_change_dates = df_interest_rate_change.index

plt.plot(volatility.index, volatility, color='blue')
for tarih in df_interest_rate_change_dates:
    plt.axvline(x=tarih, color='red', linestyle='--', linewidth=1, alpha=0.5)
plt.title("CBRT Rate Decisions and USD/TRY Volatility (2018-2026)",
          fontsize=14, fontweight='bold')
plt.ylabel("USD/TRY 30-Day Rolling Volatility",
           color='blue', fontsize=11, fontstyle='italic')
plt.figtext(0.5, 0.02, "Sources: TCMB, Yfinance",
            ha="center", fontsize=10, color="gray", fontstyle='italic')
plt.tight_layout()
plt.show()
