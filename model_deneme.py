import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Modellerimizi import edelim
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

print("Model deneme script'i başlıyor...")

# --- 1. VERİYİ YÜKLEME VE HAZIRLAMA ---
try:
    df = pd.read_csv("final_model_data.csv")
    print("✅ 'final_model_data.csv' dosyası başarıyla yüklendi.")
except FileNotFoundError:
    print("❌ HATA: 'final_model_data.csv' dosyası bulunamadı. Lütfen bir önceki adımı (veri birleştirme) tamamladığınızdan emin olun.")
    exit()

# Modelin anlayabilmesi için kategorik olan 'mahalle' sütununu sayısal sütunlara çeviriyoruz (One-Hot Encoding)
df = pd.get_dummies(df, columns=['mahalle'], drop_first=True)

# Tarih sütunu artık bir özellik değil, çünkü ondan 'ay', 'haftanin_gunu' gibi özellikleri zaten türettik.
df.drop('tarih', axis=1, inplace=True)

# Eksik veri varsa (çok olası değil ama önlem olarak) basitçe ortalama ile dolduralım.
df.fillna(df.mean(), inplace=True)

# --- 2. VERİYİ EĞİTİM VE TEST OLARAK AYIRMA ---
# Bu adım, modelin başarısını görmediği veriler üzerinde adil bir şekilde ölçmemizi sağlar.

# 'y' (hedef değişkenimiz): Tahmin etmeye çalıştığımız şey
y = df['gunluk_sikayet_sayisi']

# 'X' (özellikler): Tahmin yapmak için kullanacağımız tüm diğer bilgiler
X = df.drop('gunluk_sikayet_sayisi', axis=1)

# Veri setini %80 eğitim, %20 test olacak şekilde ayır
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"\nVeri seti modellere hazırlanmıştır. Eğitim verisi: {len(X_train)} satır, Test verisi: {len(X_test)} satır.")


# --- 3. MODELLERİ TANIMLAMA VE DENEME ---

# Deneyeceğimiz modelleri bir sözlük yapısında tanımlıyoruz
modeller = {
    "Linear Regression": LinearRegression(),
    "Ridge Regression": Ridge(),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1), # n_jobs=-1 tüm işlemci çekirdeklerini kullanır, hızlandırır.
    "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42)
}

# Sonuçları kaydedeceğimiz bir DataFrame oluşturalım
sonuc_df = pd.DataFrame(columns=['Model', 'MAE', 'RMSE'])

print("\n--- Model Eğitimi ve Değerlendirmesi Başlıyor ---")

# Her bir modeli döngüyle deneyelim
for ad, model in modeller.items():
    print(f"\n-> '{ad}' modeli eğitiliyor...")
    
    # Modeli eğitim verisiyle eğit
    model.fit(X_train, y_train)
    
    print(f"-> '{ad}' modeli ile test verisi üzerinde tahmin yapılıyor...")
    # Eğitilmiş model ile test setindeki şikayet sayılarını tahmin et
    tahminler = model.predict(X_test)
    
    # Hata metriklerini hesapla
    mae = mean_absolute_error(y_test, tahminler)
    rmse = np.sqrt(mean_squared_error(y_test, tahminler))
    
    print(f"✅ '{ad}' modeli tamamlandı. Sonuçlar:")
    print(f"   Ortalama Mutlak Hata (MAE): {mae:.2f}")
    print(f"   Kök Ortalama Kare Hata (RMSE): {rmse:.2f}")

    # Sonucu DataFrame'e ekle
    sonuc_df.loc[len(sonuc_df)] = [ad, mae, rmse]

# --- 4. SONUÇLARI GÖSTERME ---
print("\n" + "="*40)
print("     TÜM MODELLERİN KARŞILAŞTIRMASI")
print("="*40)
# Sonuçları en başarılıdan (en düşük RMSE) en başarsıza doğru sırala
sonuc_df_sirali = sonuc_df.sort_values(by='RMSE')
print(sonuc_df_sirali)
print("="*40)
print("\n(MAE ve RMSE metriklerinde daha düşük skor daha iyi model anlamına gelir)")


# --- 5. EN İYİ MODELİN ÖZELLİK ÖNEMİNİ GÖSTERME (BONUS) ---
# Genellikle Random Forest veya Gradient Boosting en iyi sonucu verir.
# Bu modeller bize hangi özelliğin tahminde ne kadar etkili olduğunu söyleyebilir.
en_iyi_model_adi = sonuc_df_sirali.iloc[0]['Model']
if 'Random Forest' in en_iyi_model_adi or 'Gradient Boosting' in en_iyi_model_adi:
    en_iyi_model = modeller[en_iyi_model_adi]
    
    print(f"\n--- En Başarılı Model Olan '{en_iyi_model_adi}' İçin Özellik Önem Sıralaması ---")
    
    feature_importances = pd.DataFrame(en_iyi_model.feature_importances_,
                                       index = X_train.columns,
                                       columns=['onem_skoru']).sort_values('onem_skoru', ascending=False)
    
    print(feature_importances.head(10)) # En önemli 10 özelliği göster
    print("\n(Bu tablo, şikayet sayısını tahmin ederken modelin en çok hangi veriye güvendiğini gösterir)")