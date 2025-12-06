import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Modelleri içe aktar
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor

# XGBoost kontrolü (Yüklü değilse hata vermesin diye try-except bloğu)
try:
    from xgboost import XGBRegressor
    xgboost_exists = True
except ImportError:
    xgboost_exists = False
    print("UYARI: XGBoost kütüphanesi bulunamadı, listeye eklenmeyecek.")

# 1. Veri Setini Yükleme
df_final = pd.read_csv('3-dataset-cleaned.csv')

# 2. Hedef ve Özellikler
y = df_final['Price']
X = df_final.drop('Price', axis=1)

# 3. Eğitim ve Test Ayrımı
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Ölçeklendirme (Scaling) - Bazı modeller için zorunlu
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 5. Modeller Listesi
# (Model Adı, Model Nesnesi, Ölçeklenmiş Veri Gerekli mi?)
models = [
    ("Linear Regression", LinearRegression(), False),
    ("Ridge", Ridge(), False),
    ("Lasso", Lasso(), False),
    ("ElasticNet", ElasticNet(), False),
    ("Decision Tree", DecisionTreeRegressor(random_state=42), False),
    ("Random Forest", RandomForestRegressor(n_estimators=100, random_state=42), False),
    ("Gradient Boosting", GradientBoostingRegressor(random_state=42), False),
    ("SVR", SVR(kernel='rbf', C=100000), True), # Ölçekli veri ister
    ("KNN", KNeighborsRegressor(n_neighbors=5), True), # Ölçekli veri ister
    ("Neural Network (MLP)", MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42), True) # Ölçekli veri ister
]

# Eğer XGBoost varsa listeye ekle
if xgboost_exists:
    models.append(("XGBoost", XGBRegressor(n_estimators=1000, learning_rate=0.05, n_jobs=-1, random_state=42), False))

# 6. Döngü ile Tüm Modelleri Eğitme ve Test Etme
results = []

print("Modeller eğitiliyor, lütfen bekleyiniz...\n")

for name, model, need_scaling in models:
    # Veri setini seç (Normal mi, Ölçekli mi?)
    if need_scaling:
        X_tr, X_te = X_train_scaled, X_test_scaled
    else:
        X_tr, X_te = X_train, X_test
        
    # Eğit
    model.fit(X_tr, y_train)
    
    # Tahmin Et
    y_pred = model.predict(X_te)
    
    # Skorları Hesapla
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    results.append({
        "Model": name,
        "R2 Score": r2,
        "MAE": mae,
        "RMSE": rmse
    })
    print(f"--> {name} tamamlandı.")

# 7. Sonuçları Tabloya Dökme ve Sıralama
results_df = pd.DataFrame(results)
results_df = results_df.sort_values(by="R2 Score", ascending=False).reset_index(drop=True)

print("\n" + "="*50)
print("TÜM MODELLERİN PERFORMANS KARŞILAŞTIRMASI")
print("="*50)
print(results_df)
print("="*50)

# En iyi modeli seç
best_model = results_df.iloc[0]
print(f"\nEN BAŞARILI MODEL: {best_model['Model']}")
print(f"Açıklayıcılık Oranı (R2): %{best_model['R2 Score']*100:.2f}")