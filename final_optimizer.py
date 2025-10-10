import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

print("Kapasite Kısıtlı Nihai Tahmin ve Rota Optimizasyon Sistemi Başlatılıyor...")

# --- 1. VERİ YÜKLEME VE MODEL EĞİTİMİ (Değişiklik yok) ---
try:
    df = pd.read_csv("final_model_data.csv")
    print("✅ 'final_model_data.csv' başarıyla yüklendi.")
except FileNotFoundError:
    print("❌ HATA: 'final_model_data.csv' dosyası bulunamadı.")
    exit()

df = pd.get_dummies(df, columns=['mahalle'], drop_first=True)
df.drop('tarih', axis=1, inplace=True)
df.fillna(df.mean(), inplace=True)
y = df['gunluk_sikayet_sayisi']
X = df.drop('gunluk_sikayet_sayisi', axis=1)

print("-> En başarılı model (Random Forest) tüm veriyle yeniden eğitiliyor...")
final_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
final_model.fit(X, y)
print("✅ Model başarıyla eğitildi.")

# --- 2. GELECEK HAFTANIN TAHMİN VERİSİNİ OLUŞTURMA (Değişiklik yok) ---
print("\n-> Gelecek hafta için tahmin verisi hazırlanıyor...")
df_mahalleler = pd.read_csv("final_model_data.csv")[['mahalle', 'nufus', 'toplam_yorum_sayisi', 'restaurant_sayisi', 'cafe_sayisi', 'supermarket_sayisi', 'school_sayisi', 'shopping_mall_sayisi', 'transit_station_sayisi']].drop_duplicates('mahalle')
tahmin_tarihleri = [datetime.now().date() + timedelta(days=i) for i in range(3, 10)]
hava_tahminleri = {
    0: {'ortalama_sicaklik_c': 18.0, 'yagis_mm': 0.0}, 1: {'ortalama_sicaklik_c': 17.5, 'yagis_mm': 1.2},
    2: {'ortalama_sicaklik_c': 19.0, 'yagis_mm': 0.0}, 3: {'ortalama_sicaklik_c': 20.0, 'yagis_mm': 0.0},
    4: {'ortalama_sicaklik_c': 16.0, 'yagis_mm': 5.5}, 5: {'ortalama_sicaklik_c': 15.0, 'yagis_mm': 2.0},
    6: {'ortalama_sicaklik_c': 17.0, 'yagis_mm': 0.0}
}
gelecek_hafta_df_list = []
for tarih in tahmin_tarihleri:
    temp_df = df_mahalleler.copy()
    temp_df['tarih'] = pd.to_datetime(tarih)
    temp_df['ay'] = temp_df['tarih'].dt.month
    temp_df['haftanin_gunu'] = temp_df['tarih'].dt.dayofweek
    temp_df['yilin_gunu'] = temp_df['tarih'].dt.dayofyear
    temp_df['hafta_sonu_mu'] = (temp_df['haftanin_gunu'] >= 5).astype(int)
    temp_df['resmi_tatil_mi'] = 0
    gunun_havasi = hava_tahminleri[tarih.weekday()]
    temp_df['ortalama_sicaklik_c'] = gunun_havasi['ortalama_sicaklik_c']
    temp_df['yagis_mm'] = gunun_havasi['yagis_mm']
    gelecek_hafta_df_list.append(temp_df)
tahmin_icin_df = pd.concat(gelecek_hafta_df_list)
tahmin_icin_df_processed = pd.get_dummies(tahmin_icin_df, columns=['mahalle'], drop_first=True)
tahmin_icin_df_processed = tahmin_icin_df_processed.reindex(columns=X.columns, fill_value=0)

# --- 3. RİSK SKORLARINI TAHMİN ETME (Değişiklik yok) ---
print("-> Gelecek haftanın risk skorları tahmin ediliyor...")
tahmin_icin_df['risk_skoru'] = final_model.predict(tahmin_icin_df_processed)
print("✅ Risk skorları başarıyla tahmin edildi.")

# --- 4. ROTA OPTİMiZASYONU (Kapasite Kısıtı Eklendi) ---
print("\n-> Kapasite Kısıtlı Rota Optimizasyonu başlıyor...")
mahalle_koordinatlari = {
    "ACIBADEM": (41.007, 29.056), "AHMEDİYE": (41.023, 29.020), "ALTUNİZADE": (41.020, 29.043),
    "AZİZ MAHMUT HÜDAYİ": (41.025, 29.017), "BAHÇELİEVLER": (41.050, 29.071), "BARBAROS": (41.025, 29.040),
    "BEYLERBEYİ": (41.045, 29.043), "BULGURLU": (41.020, 29.083), "BURHANİYE": (41.033, 29.051),
    "CUMHURİYET": (41.025, 29.098), "ÇENGELKÖY": (41.056, 29.062), "FERAH": (41.041, 29.073),
    "GÜZELTEPE": (41.059, 29.069), "İCADİYE": (41.032, 29.030), "KANDİLLİ": (41.066, 29.059),
    "KISIKLI": (41.030, 29.065), "KİRAZLITEPE": (41.042, 29.055), "KULELİ": (41.051, 29.053),
    "KUZGUNCUK": (41.038, 29.026), "KÜÇÜK ÇAMLICA": (41.018, 29.062), "KÜÇÜKSU": (41.074, 29.071),
    "KÜPLÜCE": (41.040, 29.049), "MEHMET AKİF ERSOY": (41.047, 29.062), "MİMAR SİNAN": (41.026, 29.023),
    "MURATREIS": (41.021, 29.032), "SALACAK": (41.019, 29.010), "SELAMİ ALİ": (41.028, 29.034),
    "SELİMİYE": (41.012, 29.019), "SULTANTEPE": (41.033, 29.023), "ÜNALAN": (41.011, 29.068),
    "VALİDE-İ ATİK": (41.018, 29.027), "YAVUZTÜRK": (41.044, 29.081), "ZEYNEP KAMİL": (41.016, 29.023)
}
DEPO_KOORDINATI = (41.026, 29.023)

def create_data_model(locations, demands):
    data = {}
    data['locations'] = [DEPO_KOORDINATI] + [locations[loc] for loc in demands]
    data['demands'] = [0] + list(demands.values())
    data['num_vehicles'] = 23
    data['depot'] = 0
    data['location_names'] = ['DEPO'] + list(demands.keys())
    # *** YENİ EKLENEN KISIM BAŞLANGICI ***
    # Her kamyon için bir kapasite belirliyoruz. Bu değer, bir kamyonun bir günde ne kadar "risk puanı" toplayabileceğini belirtir.
    # Toplam talebe göre dinamik bir kapasite belirlemek daha iyi sonuçlar verebilir ama başlangıç için sabit bir değer işimizi görecektir.
    total_demand = sum(demands.values())
    avg_capacity = total_demand / data['num_vehicles']
    # Ortalama kapasitenin biraz üzerinde bir değer atayalım ki tüm noktalar ziyaret edilebilsin.
    vehicle_capacity = int(avg_capacity * 1.5) if avg_capacity > 0 else 100
    data['vehicle_capacities'] = [vehicle_capacity] * data['num_vehicles']
    # *** YENİ EKLENEN KISIM SONU ***
    return data

def compute_distance_matrix(locations):
    # (Bu fonksiyon aynı kaldı)
    distance_matrix = {}
    for from_node in range(len(locations)):
        distance_matrix[from_node] = {}
        for to_node in range(len(locations)):
            if from_node == to_node:
                distance_matrix[from_node][to_node] = 0
            else:
                x1, y1 = locations[from_node]
                x2, y2 = locations[to_node]
                distance_matrix[from_node][to_node] = int(np.hypot(x1 - x2, y1 - y2) * 10000)
    return distance_matrix

def print_solution(data, manager, routing, solution):
    # (Bu fonksiyon aynı kaldı)
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = f'Kamyon {vehicle_id+1} Rotası: '
        route = []
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route.append(data['location_names'][node_index])
            index = solution.Value(routing.NextVar(index))
        route.append(data['location_names'][manager.IndexToNode(index)])
        if len(route) > 2:
            plan_output += ' -> '.join(route)
            print(plan_output)

# Her gün için ayrı ayrı optimizasyon yap
for tarih in tahmin_tarihleri:
    tarih_str = tarih.strftime('%Y-%m-%d (%A)')
    print("\n" + "="*50)
    print(f"🗓️  EYLEM PLANI: {tarih_str}")
    print("="*50)

    gunun_verisi = tahmin_icin_df[tahmin_icin_df['tarih'] == pd.to_datetime(tarih)]
    riskli_mahalleler = gunun_verisi[gunun_verisi['risk_skoru'] > 20]
    
    if riskli_mahalleler.empty:
        print("Bugün için yüksek riskli mahalle bulunmuyor. Standart operasyon uygulanabilir.")
        continue

    demands = {row['mahalle']: int(row['risk_skoru']) for index, row in riskli_mahalleler.iterrows()}
    locations = {name: mahalle_koordinatlari[name] for name in demands}

    data = create_data_model(locations, demands)
    manager = pywrapcp.RoutingIndexManager(len(data['locations']), data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)
    distance_matrix = compute_distance_matrix(data['locations'])

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # *** YENİ EKLENEN KISIM BAŞLANGICI ***
    # Her mahallenin talebini (risk skorunu) tanımlayan bir callback fonksiyonu
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    # Talepleri ve kapasite kısıtını modele ekliyoruz
    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # slack_max, bekleme süresi yok
        data['vehicle_capacities'],  # Her kamyonun kapasitesi
        True,  # start_cumul_to_zero, depodan başlarken yük 0'dır
        'Kapasite')
    # *** YENİ EKLENEN KISIM SONU ***

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(1)

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        print_solution(data, manager, routing, solution)
    else:
        print("Bu gün için bir çözüm bulunamadı.")