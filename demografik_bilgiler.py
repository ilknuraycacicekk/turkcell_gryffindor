#Nüfus Bilgileri (2024 Üsküdar Faaliyet Raporuna Göre)
import pandas as pd

# Faaliyet raporundan aldığımız ve veri üretirken kullandığımız nüfus verileri
mahalle_nufus_verileri = {
    "ACIBADEM": 23385, "AHMEDİYE": 8411, "ALTUNİZADE": 12129, "AZİZ MAHMUT HÜDAYİ": 8246,
    "BAHÇELİEVLER": 23334, "BARBAROS": 16628, "BEYLERBEYİ": 5106, "BULGURLU": 30494,
    "BURHANİYE": 16290, "CUMHURİYET": 37895, "ÇENGELKÖY": 13447, "FERAH": 21661,
    "GÜZELTEPE": 13309, "İCADİYE": 15624, "KANDİLLİ": 1398, "KISIKLI": 20195,
    "KİRAZLITEPE": 9060, "KULELİ": 4092, "KUZGUNCUK": 3906, "KÜÇÜK ÇAMLICA": 11066,
    "KÜÇÜKSU": 18345, "KÜPLÜCE": 16782, "MEHMET AKİF ERSOY": 18615, "MİMAR SİNAN": 11344,
    "MURATREIS": 13558, "SALACAK": 9358, "SELAMİ ALİ": 13101, "SELİMİYE": 7922,
    "SULTANTEPE": 10647, "ÜNALAN": 34746, "VALİDE-İ ATİK": 19895, "YAVUZTÜRK": 31227,
    "ZEYNEP KAMİL": 11765
}

# Sözlüğü bir Pandas DataFrame'e dönüştür
df_nufus = pd.DataFrame(list(mahalle_nufus_verileri.items()), columns=['mahalle', 'nufus'])

# Veriyi bir CSV dosyasına kaydet
dosya_adi = "nufus_verisi.csv"
df_nufus.to_csv(dosya_adi, index=False)

print(f"✅ Nüfus verisi başarıyla '{dosya_adi}' dosyasına kaydedildi.")
print("\nVeri Örneği:")
print(df_nufus.head())

#Mekan Bilgileri -- mahalle bazlı nerde ne kadar kafe, okul vb. mekan var ??



#Takvime göre tatil,bayram vb bilgiler.

import pandas as pd
import holidays

print("-> 2024 ve 2025 yılları için resmi tatil günleri oluşturuluyor...")

# 2024 ve 2025 yılları için Türkiye'deki resmi tatilleri al
tr_holidays_2024 = holidays.Turkey(years=2024)
tr_holidays_2025 = holidays.Turkey(years=2025)

# İki yılın tatillerini birleştir
tum_tatiller = {**tr_holidays_2024, **tr_holidays_2025}

# Sözlüğü bir Pandas DataFrame'e dönüştür
df_tatiller = pd.DataFrame(list(tum_tatiller.items()), columns=['tarih', 'tatil_adi'])

# Tarih sütununu doğru formata çevir
df_tatiller['tarih'] = pd.to_datetime(df_tatiller['tarih'])

# Veriyi bir CSV dosyasına kaydet
dosya_adi = "resmi_tatiller.csv"
df_tatiller.to_csv(dosya_adi, index=False)

print(f"✅ Resmi tatil günleri '{dosya_adi}' dosyasına kaydedildi.")
print("\nVeri Örneği:")
print(df_tatiller.head())