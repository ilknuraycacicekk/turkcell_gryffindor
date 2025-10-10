import json
import pandas as pd
import numpy as np
import datetime
import random

# --- 1. PROJE PARAMETRELERİ ---
# Bu bölümdeki değişkenleri projenizin ihtiyacına göre değiştirebilirsiniz.

# 21 aylık periyot için üretilecek toplam şikayet sayısı
# (Yıllık 334,339 şikayet baz alınarak 21 ay için ölçeklendirilmiştir)
TOPLAM_SIKAYET_SAYISI = 585093

# Veri üretilecek tarih aralığı
BASLANGIC_TARIHI = '2024-01-01'
BITIS_TARIHI = '2025-09-30'

# Oluşturulacak JSON dosyasının adı
CIKTI_DOSYA_ADI = "uskudar_sikayet_veriseti_2024-2025.json"

print(f"{TOPLAM_SIKAYET_SAYISI} adet şikayet verisi '{CIKTI_DOSYA_ADI}' dosyasına üretiliyor.")
print(f"Tarih Aralığı: {BASLANGIC_TARIHI} - {BITIS_TARIHI}")
print("Bu işlem bilgisayarınızın hızına göre birkaç dakika sürebilir...")


# --- 2. TEMEL VERİLER (RAPOR VE ARAŞTIRMALARA DAYALI) ---

# Üsküdar'ın 33 mahallesine ait temel bilgiler
# Nüfus: Faaliyet Raporu Sayfa 10'dan alınmıştır.
# Ticari Yoğunluk: Mahallelerin karakteristiğine göre 1'den 5'e kadar atanmış bir skordur.
mahalle_verileri = [
    {"mahalle": "ACIBADEM", "nufus": 23385, "koordinatlar": {"enlem": 41.007, "boylam": 29.056}, "ticari_yogunluk": 4},
    {"mahalle": "AHMEDİYE", "nufus": 8411, "koordinatlar": {"enlem": 41.023, "boylam": 29.020}, "ticari_yogunluk": 4},
    {"mahalle": "ALTUNİZADE", "nufus": 12129, "koordinatlar": {"enlem": 41.020, "boylam": 29.043}, "ticari_yogunluk": 5},
    {"mahalle": "AZİZ MAHMUT HÜDAYİ", "nufus": 8246, "koordinatlar": {"enlem": 41.025, "boylam": 29.017}, "ticari_yogunluk": 5},
    {"mahalle": "BAHÇELİEVLER", "nufus": 23334, "koordinatlar": {"enlem": 41.050, "boylam": 29.071}, "ticari_yogunluk": 3},
    {"mahalle": "BARBAROS", "nufus": 16628, "koordinatlar": {"enlem": 41.025, "boylam": 29.040}, "ticari_yogunluk": 4},
    {"mahalle": "BEYLERBEYİ", "nufus": 5106, "koordinatlar": {"enlem": 41.045, "boylam": 29.043}, "ticari_yogunluk": 4},
    {"mahalle": "BULGURLU", "nufus": 30494, "koordinatlar": {"enlem": 41.020, "boylam": 29.083}, "ticari_yogunluk": 3},
    {"mahalle": "BURHANİYE", "nufus": 16290, "koordinatlar": {"enlem": 41.033, "boylam": 29.051}, "ticari_yogunluk": 2},
    {"mahalle": "CUMHURİYET", "nufus": 37895, "koordinatlar": {"enlem": 41.025, "boylam": 29.098}, "ticari_yogunluk": 3},
    {"mahalle": "ÇENGELKÖY", "nufus": 13447, "koordinatlar": {"enlem": 41.056, "boylam": 29.062}, "ticari_yogunluk": 4},
    {"mahalle": "FERAH", "nufus": 21661, "koordinatlar": {"enlem": 41.041, "boylam": 29.073}, "ticari_yogunluk": 2},
    {"mahalle": "GÜZELTEPE", "nufus": 13309, "koordinatlar": {"enlem": 41.059, "boylam": 29.069}, "ticari_yogunluk": 2},
    {"mahalle": "İCADİYE", "nufus": 15624, "koordinatlar": {"enlem": 41.032, "boylam": 29.030}, "ticari_yogunluk": 3},
    {"mahalle": "KANDİLLİ", "nufus": 1398, "koordinatlar": {"enlem": 41.066, "boylam": 29.059}, "ticari_yogunluk": 2},
    {"mahalle": "KISIKLI", "nufus": 20195, "koordinatlar": {"enlem": 41.030, "boylam": 29.065}, "ticari_yogunluk": 3},
    {"mahalle": "KİRAZLITEPE", "nufus": 9060, "koordinatlar": {"enlem": 41.042, "boylam": 29.055}, "ticari_yogunluk": 2},
    {"mahalle": "KULELİ", "nufus": 4092, "koordinatlar": {"enlem": 41.051, "boylam": 29.053}, "ticari_yogunluk": 2},
    {"mahalle": "KUZGUNCUK", "nufus": 3906, "koordinatlar": {"enlem": 41.038, "boylam": 29.026}, "ticari_yogunluk": 4},
    {"mahalle": "KÜÇÜK ÇAMLICA", "nufus": 11066, "koordinatlar": {"enlem": 41.018, "boylam": 29.062}, "ticari_yogunluk": 2},
    {"mahalle": "KÜÇÜKSU", "nufus": 18345, "koordinatlar": {"enlem": 41.074, "boylam": 29.071}, "ticari_yogunluk": 2},
    {"mahalle": "KÜPLÜCE", "nufus": 16782, "koordinatlar": {"enlem": 41.040, "boylam": 29.049}, "ticari_yogunluk": 2},
    {"mahalle": "MEHMET AKİF ERSOY", "nufus": 18615, "koordinatlar": {"enlem": 41.047, "boylam": 29.062}, "ticari_yogunluk": 2},
    {"mahalle": "MİMAR SİNAN", "nufus": 11344, "koordinatlar": {"enlem": 41.026, "boylam": 29.023}, "ticari_yogunluk": 5},
    {"mahalle": "MURATREIS", "nufus": 13558, "koordinatlar": {"enlem": 41.021, "boylam": 29.032}, "ticari_yogunluk": 3},
    {"mahalle": "SALACAK", "nufus": 9358, "koordinatlar": {"enlem": 41.019, "boylam": 29.010}, "ticari_yogunluk": 4},
    {"mahalle": "SELAMİ ALİ", "nufus": 13101, "koordinatlar": {"enlem": 41.028, "boylam": 29.034}, "ticari_yogunluk": 4},
    {"mahalle": "SELİMİYE", "nufus": 7922, "koordinatlar": {"enlem": 41.012, "boylam": 29.019}, "ticari_yogunluk": 3},
    {"mahalle": "SULTANTEPE", "nufus": 10647, "koordinatlar": {"enlem": 41.033, "boylam": 29.023}, "ticari_yogunluk": 3},
    {"mahalle": "ÜNALAN", "nufus": 34746, "koordinatlar": {"enlem": 41.011, "boylam": 29.068}, "ticari_yogunluk": 3},
    {"mahalle": "VALİDE-İ ATİK", "nufus": 19895, "koordinatlar": {"enlem": 41.018, "boylam": 29.027}, "ticari_yogunluk": 3},
    {"mahalle": "YAVUZTÜRK", "nufus": 31227, "koordinatlar": {"enlem": 41.044, "boylam": 29.081}, "ticari_yogunluk": 2},
    {"mahalle": "ZEYNEP KAMİL", "nufus": 11765, "koordinatlar": {"enlem": 41.016, "boylam": 29.023}, "ticari_yogunluk": 3},
]

pazar_yerleri = {
    "Pazartesi": ["BAHÇELİEVLER"], "Salı": ["ÇENGELKÖY"], "Çarşamba": ["ZEYNEP KAMİL"],
    "Perşembe": ["BULGURLU", "KÜPLÜCE"], "Cuma": ["AZİZ MAHMUT HÜDAYİ"], "Cumartesi": ["ACIBADEM"], "Pazar": ["ÜNALAN"]
}

sikayet_turleri_agirliklari = {
    "Konteyner Dolu/Taşmış": 0.45, "Genel Kirlilik": 0.25, "Moloz/İnşaat Atığı": 0.10,
    "Koku Şikayeti": 0.10, "Hasarlı Konteyner/Ekipman": 0.05, "Diğer": 0.05
}

# --- 3. AĞIRLIKLANDIRMA VE SİMÜLASYON MANTIĞI ---

# Mahalle verilerini daha kolay işlemek için bir Pandas DataFrame'e dönüştür
df = pd.DataFrame(mahalle_verileri)

# Nüfus ve ticari yoğunluk verilerini 0-1 arasına ölçeklendirerek normalize et
df['nufus_norm'] = df['nufus'] / df['nufus'].max()
df['ticari_yogunluk_norm'] = df['ticari_yogunluk'] / df['ticari_yogunluk'].max()

# Her mahallenin temel şikayet üretme ağırlığını hesapla (nüfus %60, ticari yoğunluk %40 etkili)
df['temel_agirlik'] = df['nufus_norm'] * 0.60 + df['ticari_yogunluk_norm'] * 0.40

# Zamansal Ağırlıklar (Haftanın günleri ve aylar için şikayet yoğunluk katsayıları)
gun_agirliklari = {"Pazartesi": 1.5, "Salı": 1.0, "Çarşamba": 1.1, "Perşembe": 1.1, "Cuma": 1.3, "Cumartesi": 1.2, "Pazar": 1.2}
ay_agirliklari = {1:1.0, 2:0.9, 3:1.0, 4:1.1, 5:1.2, 6:1.3, 7:1.4, 8:1.4, 9:1.2, 10:1.1, 11:1.0, 12:1.1}

# İngilizce gün adlarını Türkçe'ye çevirmek için kullanılacak sözlük (Hata düzeltmesi)
gun_ceviri = {
    "Monday": "Pazartesi", "Tuesday": "Salı", "Wednesday": "Çarşamba", "Thursday": "Perşembe",
    "Friday": "Cuma", "Saturday": "Cumartesi", "Sunday": "Pazar"
}

# Belirtilen tarih aralığındaki tüm günleri içeren bir liste oluştur
tarih_listesi = pd.to_datetime(pd.date_range(start=BASLANGIC_TARIHI, end=BITIS_TARIHI))

# Her bir gün için, o günün ve ayın ağırlığını çarparak genel bir zaman ağırlığı hesapla
tarih_agirliklari = [gun_agirliklari[gun_ceviri[t.day_name()]] * ay_agirliklari[t.month] for t in tarih_listesi]


# --- 4. VERİ ÜRETİM DÖNGÜSÜ ---

tum_sikayetler = []

# Toplam şikayet sayısı kadar, ağırlıklandırılmış tarih listesinden rastgele tarihler seç
# Bu, şikayetlerin yıl içinde gerçekçi bir şekilde dağılmasını sağlar
olasi_tarihler = random.choices(tarih_listesi, weights=tarih_agirliklari, k=TOPLAM_SIKAYET_SAYISI)

# Her bir şikayet için döngü başlat
for i in range(TOPLAM_SIKAYET_SAYISI):
    # Kullanıcıyı bilgilendirme mesajı
    if (i + 1) % 25000 == 0:
        print(f"  -> {i+1} / {TOPLAM_SIKAYET_SAYISI} kayıt oluşturuldu...")

    secilen_tarih = olasi_tarihler[i]
    gun_adi_tr = gun_ceviri[secilen_tarih.day_name()]

    # Mahallelerin temel ağırlıklarını kopyala
    anlik_agirliklar = df['temel_agirlik'].copy()
    # Eğer o gün bir pazar kuruluyorsa, ilgili mahallenin şikayet ağırlığını geçici olarak artır
    if gun_adi_tr in pazar_yerleri:
        for pazar_mahallesi in pazar_yerleri[gun_adi_tr]:
            anlik_agirliklar[df['mahalle'] == pazar_mahallesi] *= 1.5 # Pazar günü ağırlığını 1.5 kat artır

    # Ağırlıklandırılmış mahalle listesinden rastgele bir mahalle seç
    secilen_mahalle_bilgisi = df.sample(weights=anlik_agirliklar).iloc[0]
    
    # Ağırlıklandırılmış şikayet türlerinden rastgele bir tür seç
    sikayet_turu = random.choices(list(sikayet_turleri_agirliklari.keys()), weights=list(sikayet_turleri_agirliklari.values()))[0]
    
    # Şikayet türüne ve gününe göre gerçekçi metinler oluştur
    metin = f"{secilen_mahalle_bilgisi['mahalle']} mahallesinde {sikayet_turu} sorunu yaşanmaktadır. Ekiplerin yönlendirilmesini rica ederiz."
    if sikayet_turu == "Konteyner Dolu/Taşmış":
        metin = f"{secilen_mahalle_bilgisi['mahalle']} mahallesindeki konteynerler tamamen dolu ve etrafına taşmış durumda. Toplanmasını talep ediyorum."
    elif sikayet_turu == "Genel Kirlilik":
         metin = f"{secilen_mahalle_bilgisi['mahalle']} mahallesinde sokaklar çok kirli, yerlerde ambalaj atıkları var. Genel bir temizlik gerekiyor."
         if gun_adi_tr in pazar_yerleri and secilen_mahalle_bilgisi['mahalle'] in pazar_yerleri[gun_adi_tr]:
             metin = f"{secilen_mahalle_bilgisi['mahalle']} mahallesindeki semt pazarı sonrası temizlik yetersiz kalmış."
    elif sikayet_turu == "Moloz/İnşaat Atığı":
        metin = f"{secilen_mahalle_bilgisi['mahalle']} mahallesinde kaldırıma bırakılmış inşaat atıkları ve moloz çuvalları var."

    # %15 olasılıkla şikayetin sosyal medyadan geldiğini simüle et
    sosyal_medya_mi = random.random() < 0.15
    sosyal_medya_yorum = None
    if sosyal_medya_mi:
        kullanici_adi = f"@vatandas_{random.randint(100,999)}"
        yorum = f"@uskudarbld {secilen_mahalle_bilgisi['mahalle']} yine çöp içinde! Bu duruma bir son verin artık. #{secilen_mahalle_bilgisi['mahalle'].lower().replace(' ', '')}"
        sosyal_medya_yorum = {"kullanici": kullanici_adi, "yorum": yorum, "platform": random.choice(["X", "Instagram"])}

    # Tüm bilgileri bir JSON nesnesinde topla
    sikayet = {
        "sikayet_id": f"USK-{(secilen_tarih.year)}-{i+1:06d}",
        "tarih": secilen_tarih.strftime('%Y-%m-%d'),
        "saat": f"{random.randint(8, 22):02d}:{random.randint(0, 59):02d}",
        "gun": gun_adi_tr,
        "ilce": "Üsküdar",
        "mahalle": secilen_mahalle_bilgisi['mahalle'],
        "koordinatlar": secilen_mahalle_bilgisi['koordinatlar'],
        "sikayet_turu": sikayet_turu,
        "sikayet_metni": metin,
        "sosyal_medya_mi": sosyal_medya_mi,
        "sosyal_medya_yorum": sosyal_medya_yorum
    }
    # Oluşturulan şikayeti ana listeye ekle
    tum_sikayetler.append(sikayet)

# --- 5. JSON DOSYASINA YAZMA ---
with open(CIKTI_DOSYA_ADI, 'w', encoding='utf-8') as f:
    # Tüm şikayetler listesini JSON formatında dosyaya yaz
    json.dump(tum_sikayetler, f, ensure_ascii=False, indent=2)

print(f"\nİşlem tamamlandı! {TOPLAM_SIKAYET_SAYISI} adet şikayet verisi '{CIKTI_DOSYA_ADI}' dosyasına başarıyla kaydedildi.")