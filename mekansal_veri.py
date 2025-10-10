import requests
import time
import pandas as pd

# --- GELİŞMİŞ FONKSİYON TANIMI ---
def get_place_data(api_key, lat, lon, radius, place_type):
    """
    Belirtilen koordinat etrafında, bir mekan türü için hem toplam sayıyı 
    hem de bu mekanların toplam yorum sayısını döndürür.
    """
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius={radius}&type={place_type}&key={api_key}"
    
    total_results_count = 0
    total_ratings_sum = 0
    
    while True:
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] not in ['OK', 'ZERO_RESULTS']:
                print(f"     -> HATA: API durumu '{data['status']}'. Sebep: {data.get('error_message', 'Bilinmiyor')}")
                return None, None

            results = data.get('results', [])
            total_results_count += len(results)
            
            # Her mekanın yorum sayısını topla
            for place in results:
                total_ratings_sum += place.get('user_ratings_total', 0)
            
            next_page_token = data.get('next_page_token')
            if next_page_token:
                time.sleep(2)
                url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={next_page_token}&key={api_key}"
            else:
                break
                
        except requests.exceptions.RequestException as e:
            print(f"❌ HATA: API'ye bağlanırken bir sorun oluştu: {e}")
            return None, None
            
    return total_results_count, total_ratings_sum

# --- ANA KOD BÖLÜMÜ ---

# 1. ADIM: YENİ ve GÜVENLİ API anahtarınızı buraya yapıştırın.
API_KEY = "AIzaSyAv6WSjeGC2uo11VGnoGiUNTBvA_TgBcjQ"

# 2. ADIM: Üsküdar'ın mahalleleri ve koordinatları (Tam Liste)
mahalle_verileri = [
    {"mahalle": "ACIBADEM", "lat": 41.007, "lon": 29.056}, {"mahalle": "AHMEDİYE", "lat": 41.023, "lon": 29.020},
    {"mahalle": "ALTUNİZADE", "lat": 41.020, "lon": 29.043}, {"mahalle": "AZİZ MAHMUT HÜDAYİ", "lat": 41.025, "lon": 29.017},
    {"mahalle": "BAHÇELİEVLER", "lat": 41.050, "lon": 29.071}, {"mahalle": "BARBAROS", "lat": 41.025, "lon": 29.040},
    {"mahalle": "BEYLERBEYİ", "lat": 41.045, "lon": 29.043}, {"mahalle": "BULGURLU", "lat": 41.020, "lon": 29.083},
    {"mahalle": "BURHANİYE", "lat": 41.033, "lon": 29.051}, {"mahalle": "CUMHURİYET", "lat": 41.025, "lon": 29.098},
    {"mahalle": "ÇENGELKÖY", "lat": 41.056, "lon": 29.062}, {"mahalle": "FERAH", "lat": 41.041, "lon": 29.073},
    {"mahalle": "GÜZELTEPE", "lat": 41.059, "lon": 29.069}, {"mahalle": "İCADİYE", "lat": 41.032, "lon": 29.030},
    {"mahalle": "KANDİLLİ", "lat": 41.066, "lon": 29.059}, {"mahalle": "KISIKLI", "lat": 41.030, "lon": 29.065},
    {"mahalle": "KİRAZLITEPE", "lat": 41.042, "lon": 29.055}, {"mahalle": "KULELİ", "lat": 41.051, "lon": 29.053},
    {"mahalle": "KUZGUNCUK", "lat": 41.038, "lon": 29.026}, {"mahalle": "KÜÇÜK ÇAMLICA", "lat": 41.018, "lon": 29.062},
    {"mahalle": "KÜÇÜKSU", "lat": 41.074, "lon": 29.071}, {"mahalle": "KÜPLÜCE", "lat": 41.040, "lon": 29.049},
    {"mahalle": "MEHMET AKİF ERSOY", "lat": 41.047, "lon": 29.062}, {"mahalle": "MİMAR SİNAN", "lat": 41.026, "lon": 29.023},
    {"mahalle": "MURATREIS", "lat": 41.021, "lon": 29.032}, {"mahalle": "SALACAK", "lat": 41.019, "lon": 29.010},
    {"mahalle": "SELAMİ ALİ", "lat": 41.028, "lon": 29.034}, {"mahalle": "SELİMİYE", "lat": 41.012, "lon": 29.019},
    {"mahalle": "SULTANTEPE", "lat": 41.033, "lon": 29.023}, {"mahalle": "ÜNALAN", "lat": 41.011, "lon": 29.068},
    {"mahalle": "VALİDE-İ ATİK", "lat": 41.018, "lon": 29.027}, {"mahalle": "YAVUZTÜRK", "lat": 41.044, "lon": 29.081},
    {"mahalle": "ZEYNEP KAMİL", "lat": 41.016, "lon": 29.023}
]

# 3. ADIM: Parametreler
arama_yaricapi_metre = 1500
aranacak_mekan_turleri = ['restaurant', 'cafe', 'supermarket', 'bakery', 'school', 'shopping_mall', 'transit_station']

sonuclar = []

if "YENİ_VE_GÜVENLİ" in API_KEY:
    print("Lütfen yukarıdaki `API_KEY` değişkenini kendi yeni ve güvenli anahtarınızla güncelleyin.")
else:
    # Tüm mahalleler için ana döngü
    for i, mahalle in enumerate(mahalle_verileri):
        mahalle_adi = mahalle['mahalle']
        print(f"\n({i+1}/{len(mahalle_verileri)}) '{mahalle_adi}' mahallesi işleniyor...")
        
        mahalle_sonuclari = {'mahalle': mahalle_adi}
        mahalle_toplam_yorum = 0
        
        # O mahalle için her mekan türünü ara
        for mekan_turu in aranacak_mekan_turleri:
            count, ratings = get_place_data(API_KEY, mahalle['lat'], mahalle['lon'], arama_yaricapi_metre, mekan_turu)
            
            if count is not None:
                # Her mekan türü için ayrı bir sütun oluştur
                mahalle_sonuclari[f'{mekan_turu}_sayisi'] = count
                mahalle_toplam_yorum += ratings
        
        # Mahallenin toplam popülerlik skorunu ekle
        mahalle_sonuclari['toplam_yorum_sayisi'] = mahalle_toplam_yorum
        sonuclar.append(mahalle_sonuclari)
        print(f"-> '{mahalle_adi}' için sonuçlar: {mahalle_sonuclari}")

    # Sonuçları bir Pandas DataFrame'e dönüştür ve CSV dosyasına kaydet
    df_sonuc = pd.DataFrame(sonuclar)
    dosya_adi = "uskudar_gelismis_yogunluk.csv"
    df_sonuc.to_csv(dosya_adi, index=False)

    print(f"\n--- İŞLEM TAMAMLANDI ---")
    print(f"Tüm Üsküdar mahalleleri için gelişmiş yoğunluk verileri '{dosya_adi}' dosyasına kaydedildi.")
    print("\nSonuçların ilk 5 satırı:")
    print(df_sonuc.head())