import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 1. Veri Setini Yükleme (df11 olarak)
df11 = pd.read_csv('3-dataset-cleaned.csv')

# 2. Hedef ve Özelliklerin Ayrılması
y = df11['Price']
X = df11.drop('Price', axis=1)

# 3. Eğitim ve Test Setlerine Ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. XGBoost Modelini Kurma
# XGBoost, Gradient Boosting'in daha optimize edilmiş ve hızlı halidir.
xgb_model = XGBRegressor(
    n_estimators=1000,     # Ağaç sayısı (genelde yüksek tutulur, early_stopping ile durdurulabilir)
    learning_rate=0.05,    # Öğrenme oranı
    max_depth=6,           # Ağaç derinliği
    random_state=42,
    n_jobs=-1              # Tüm işlemci çekirdeklerini kullanması için
)

xgb_model.fit(X_train, y_train)

# 5. Tahmin
y_pred = xgb_model.predict(X_test)

# 6. Başarı Metrikleri
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print("-" * 30)
print("Algoritma 8: XGBoost Sonuçları (df11)")
print("-" * 30)
print(f"MAE: {mae:,.2f}")
print(f"RMSE: {rmse:,.2f}")
print(f"R2 Score: {r2:.4f}")
print("-" * 30)