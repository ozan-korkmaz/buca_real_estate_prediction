import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 1. Veri Setini Yükleme (df14 olarak)
df14 = pd.read_csv('3-dataset-cleaned.csv')

# 2. Hedef ve Özelliklerin Ayrılması
y = df14['Price']
X = df14.drop('Price', axis=1)

# 3. Eğitim ve Test Setlerine Ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Veri Ölçeklendirme (SVR için Kritiktir)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 5. SVR Modelini Kurma
# kernel='rbf' -> Doğrusal olmayan veriler için en yaygın kullanılan çekirdek (kernel).
# C=100000 -> Ceza parametresi. Fiyatlar büyük olduğu için C'yi yüksek tutmak gerekebilir, 
# yoksa model düz bir çizgi çekip bırakabilir. 
# Not: SVR büyük veride yavaş çalışabilir.
svr_model = SVR(kernel='rbf', C=100000) 
svr_model.fit(X_train_scaled, y_train)

# 6. Tahmin
y_pred = svr_model.predict(X_test_scaled)

# 7. Başarı Metrikleri
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print("-" * 30)
print("Algoritma 11: SVR Sonuçları (df14)")
print("-" * 30)
print(f"MAE: {mae:,.2f}")
print(f"RMSE: {rmse:,.2f}")
print(f"R2 Score: {r2:.4f}")
print("-" * 30)