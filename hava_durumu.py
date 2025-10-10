from datetime import datetime
import pandas as pd
from meteostat import Point, Daily

# İstanbul için bir konum belirle (Sabiha Gökçen Havalimanı istasyonu LTFJ)
# Veya koordinat da kullanabilirsiniz: Point(41.025, 29.02)
istanbul = Point(41.025, 29.02, 70) # Enlem, Boylam, Yükseklik

# İstediğiniz tarih aralığını belirleyin
baslangic = datetime(2024, 1, 1)
bitis = datetime(2025, 12, 31)

print(f"{baslangic.strftime('%Y-%m-%d')} ile {bitis.strftime('%Y-%m-%d')} arası Meteostat verileri çekiliyor...")

# Veriyi çek ve bir Pandas DataFrame'e ata
# tavg: ortalama sıcaklık, tmin: min sıcaklık, tmax: max sıcaklık, prcp: yağış (mm)
data = Daily(istanbul, baslangic, bitis)
data = data.fetch()

# Sadece ihtiyacımız olan sütunları seçelim
data = data[['tavg', 'tmin', 'tmax', 'prcp']]
data.rename(columns={
    'tavg': 'ortalama_sicaklik_c',
    'tmin': 'en_dusuk_sicaklik_c',
    'tmax': 'en_yuksek_sicaklik_c',
    'prcp': 'yagis_mm'
}, inplace=True)


# Veriyi bir CSV dosyasına kaydetmek (daha sonra kolayca kullanmak için)
dosya_adi_csv = "istanbul_havadurumu_meteostat.csv"
data.to_csv(dosya_adi_csv)

print(f"\nİşlem tamamlandı! Veriler '{dosya_adi_csv}' dosyasına kaydedildi.")
# İlk 5 satırı görüntüle
print("\nVeri Örneği:")
print(data.head())