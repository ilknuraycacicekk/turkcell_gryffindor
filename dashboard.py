import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Akıllı Atık Yönetimi Dashboard'u",
    page_icon="🚛",
    layout="wide"
)

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("final_model_data.csv")
        df['tarih'] = pd.to_datetime(df['tarih'])
        return df
    except FileNotFoundError:
        st.error("'final_model_data.csv' dosyası bulunamadı.")
        return None

@st.cache_resource
def train_model(df):
    df_processed = pd.get_dummies(df, columns=['mahalle'], drop_first=True)
    df_processed.drop('tarih', axis=1, inplace=True)
    df_processed.fillna(df_processed.mean(), inplace=True)
    
    y = df_processed['gunluk_sikayet_sayisi']
    X = df_processed.drop('gunluk_sikayet_sayisi', axis=1)
    
    final_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    final_model.fit(X, y)
    return final_model, X.columns

@st.cache_data
def predict_future_risks(_model, _columns):
    df_mahalleler = load_data()[['mahalle', 'nufus', 'toplam_yorum_sayisi', 'restaurant_sayisi', 'cafe_sayisi', 'supermarket_sayisi', 'school_sayisi', 'shopping_mall_sayisi', 'transit_station_sayisi']].drop_duplicates('mahalle')
    tahmin_tarihleri = [datetime.now().date() + timedelta(days=i) for i in range(1, 8)]
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
    tahmin_icin_df_processed = tahmin_icin_df_processed.reindex(columns=_columns, fill_value=0)
    
    tahmin_icin_df['risk_skoru'] = _model.predict(tahmin_icin_df_processed)
    return tahmin_icin_df

# *** HATANIN OLDUĞU BÖLÜM DÜZELTİLDİ ***
mahalle_koordinatlari = {
    "ACIBADEM": [41.007, 29.056], "AHMEDİYE": [41.023, 29.020], "ALTUNİZADE": [41.020, 29.043],
    "AZİZ MAHMUT HÜDAYİ": [41.025, 29.017], "BAHÇELİEVLER": [41.050, 29.071], "BARBAROS": [41.025, 29.040],
    "BEYLERBEYİ": [41.045, 29.043], "BULGURLU": [41.020, 29.083], "BURHANİYE": [41.033, 29.051],
    "CUMHURİYET": [41.025, 29.098], "ÇENGELKÖY": [41.056, 29.062], "FERAH": [41.041, 29.073],
    "GÜZELTEPE": [41.059, 29.069], "İCADİYE": [41.032, 29.030], "KANDİLLİ": [41.066, 29.059],
    "KISIKLI": [41.030, 29.065], "KİRAZLITEPE": [41.042, 29.055], "KULELİ": [41.051, 29.053],
    "KUZGUNCUK": [41.038, 29.026], "KÜÇÜK ÇAMLICA": [41.018, 29.062], "KÜÇÜKSU": [41.074, 29.071],
    "KÜPLÜCE": [41.040, 29.049], "MEHMET AKİF ERSOY": [41.047, 29.062], "MİMAR SİNAN": [41.026, 29.023],
    "MURATREIS": [41.021, 29.032], "SALACAK": [41.019, 29.010], "SELAMİ ALİ": [41.028, 29.034],
    "SELİMİYE": [41.012, 29.019], "SULTANTEPE": [41.033, 29.023], "ÜNALAN": [41.011, 29.068],
    "VALİDE-İ ATİK": [41.018, 29.027], "YAVUZTÜRK": [41.044, 29.081], "ZEYNEP KAMİL": [41.016, 29.023]
}
DEPO_KOORDINATI = [41.026, 29.023]
# *** DÜZELTME SONU ***

def run_optimization(gunun_riskleri):
    if gunun_riskleri.empty:
        return None
    demands = {row['mahalle']: int(row['risk_skoru']) for _, row in gunun_riskleri.iterrows()}
    locations = {name: mahalle_koordinatlari[name] for name in demands}
    data = {}
    data['locations'] = [DEPO_KOORDINATI] + list(locations.values())
    data['demands'] = [0] + list(demands.values())
    data['num_vehicles'] = 23
    data['depot'] = 0
    data['location_names'] = ['DEPO'] + list(demands.keys())
    total_demand = sum(demands.values())
    avg_capacity = total_demand / data['num_vehicles'] if data['num_vehicles'] > 0 else 0
    max_demand = max(demands.values()) if demands else 0
    vehicle_capacity = max(max_demand, int(avg_capacity * 1.5)) if avg_capacity > 0 else 100
    if vehicle_capacity == 0: vehicle_capacity = 1
    data['vehicle_capacities'] = [vehicle_capacity] * data['num_vehicles']
    manager = pywrapcp.RoutingIndexManager(len(data['locations']), data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        loc1 = data['locations'][from_node]
        loc2 = data['locations'][to_node]
        return int(np.hypot(loc1[0] - loc2[0], loc1[1] - loc2[1]) * 10000)
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]
    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index, 0, data['vehicle_capacities'], True, 'Kapasite'
    )
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(1)
    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        routes = []
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            route = []
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route.append(data['location_names'][node_index])
                index = solution.Value(routing.NextVar(index))
            route.append(data['location_names'][manager.IndexToNode(index)])
            if len(route) > 2:
                routes.append(route)
        return routes
    return None

st.title("🚛 Akıllı Atık Yönetimi Karar Destek Sistemi")
st.markdown("Bu dashboard, Üsküdar ilçesi için gelecek haftanın atık yoğunluk risklerini tahmin eder ve temizlik kamyonları için günlük optimize edilmiş rotalar sunar.")

df_full = load_data()
if df_full is not None:
    model, feature_columns = train_model(df_full)
    predictions_df = predict_future_risks(model, feature_columns)
    st.sidebar.title("🗓️ Kontrol Paneli")
    selected_date_str = st.sidebar.selectbox(
        "Görüntülemek istediğiniz günü seçin:",
        options=[d.strftime("%Y-%m-%d (%A)") for d in predictions_df['tarih'].dt.date.unique()]
    )
    selected_date = datetime.strptime(selected_date_str.split(' ')[0], '%Y-%m-%d').date()
    st.sidebar.markdown("---")
    risk_threshold = st.sidebar.slider(
        "Risk Eşiği (Sadece bu skorun üzerindeki mahalleler rotaya dahil edilsin):",
        min_value=0, max_value=100, value=20, step=5
    )
    st.header(f"Eylem Planı: {selected_date_str}")
    gunun_verisi = predictions_df[predictions_df['tarih'].dt.date == selected_date]
    riskli_mahalleler = gunun_verisi[gunun_verisi['risk_skoru'] > risk_threshold].sort_values(by='risk_skoru', ascending=False)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Risk Tahminleri")
        st.dataframe(riskli_mahalleler[['mahalle', 'risk_skoru']].rename(columns={'mahalle': 'Mahalle', 'risk_skoru': 'Risk Skoru'}))
    with col2:
        st.subheader("Günün Özeti")
        st.metric("Toplam Yüksek Riskli Mahalle", f"{len(riskli_mahalleler)} adet")
        st.metric("Ortalama Risk Skoru", f"{riskli_mahalleler['risk_skoru'].mean():.2f}" if not riskli_mahalleler.empty else "N/A")
    st.markdown("---")
    st.subheader("Optimize Edilmiş Günlük Rotalar Haritası")
    optimized_routes = run_optimization(riskli_mahalleler)
    m = folium.Map(location=DEPO_KOORDINATI, zoom_start=12)
    folium.Marker(DEPO_KOORDINATI, popup="DEPO", tooltip="DEPO", icon=folium.Icon(color='red', icon='warehouse')).add_to(m)
    if optimized_routes:
        colors = ['blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'lightgray', 'black']
        for _, row in riskli_mahalleler.iterrows():
            mahalle_adi = row['mahalle']
            folium.Marker(
                mahalle_koordinatlari[mahalle_adi],
                popup=f"<b>{mahalle_adi}</b><br>Risk: {row['risk_skoru']:.2f}",
                tooltip=mahalle_adi,
                icon=folium.Icon(color='lightblue', icon='trash')
            ).add_to(m)
        for i, route in enumerate(optimized_routes):
            route_coords = [mahalle_koordinatlari.get(loc, DEPO_KOORDINATI) for loc in route]
            folium.PolyLine(route_coords, color=colors[i % len(colors)], weight=4, opacity=0.8, tooltip=f'Kamyon {i+1} Rotası').add_to(m)
        st_folium(m, width='100%', height=500)
        st.subheader("Metin Olarak Rota Planı")
        for i, route in enumerate(optimized_routes):
            st.write(f"**Kamyon {i+1} Rotası:** {' -> '.join(route)}")
    else:
        st.warning("Seçilen risk eşiğine göre bugün için optimize edilecek yüksek riskli mahalle bulunmuyor.")