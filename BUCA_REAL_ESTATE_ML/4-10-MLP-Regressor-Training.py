import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 1. Veri Setini Yükleme (df13 olarak)
df13 = pd.read_csv('3-dataset-cleaned.csv')

# 2. Hedef ve Özelliklerin Ayrılması
y = df13['Price']
X = df13.drop('Price', axis=1)

# 3. Eğitim ve Test Setlerine Ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Veri Ölçeklendirme (Yapay Sinir Ağları için Zorunludur)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 5. MLP (Yapay Sinir Ağı) Modelini Kurma
# hidden_layer_sizes=(100, 50) -> İki gizli katman olsun; birinde 100, diğerinde 50 nöron.
# max_iter=1000 -> Modelin ağırlıkları öğrenmesi için döngü sayısı (yüksek tutmak iyidir).
mlp_model = MLPRegressor(
    hidden_layer_sizes=(100, 50), 
    activation='relu', 
    solver='adam', 
    max_iter=1000, 
    random_state=42
)

mlp_model.fit(X_train_scaled, y_train)

# 6. Tahmin
y_pred = mlp_model.predict(X_test_scaled)

# 7. Başarı Metrikleri
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print("-" * 30)
print("Algoritma 10: MLP Regressor Sonuçları (df13)")
print("-" * 30)
print(f"MAE: {mae:,.2f}")
print(f"RMSE: {rmse:,.2f}")
print(f"R2 Score: {r2:.4f}")
print("-" * 30)