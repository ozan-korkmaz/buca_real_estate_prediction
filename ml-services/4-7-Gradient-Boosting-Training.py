import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 1. Veri Setini Yükleme (df10 olarak)
df10 = pd.read_csv('3-dataset-cleaned.csv')

# 2. Hedef ve Özelliklerin Ayrılması
y = df10['Price']
X = df10.drop('Price', axis=1)

# 3. Eğitim ve Test Setlerine Ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Gradient Boosting Modelini Kurma
# n_estimators=100 -> 100 adımda düzeltme yapacak.
# learning_rate=0.1 -> Her adımın katkı oranı (küçük olması genelde iyidir ama daha çok ağaç gerekir).
gb_model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
gb_model.fit(X_train, y_train)

# 5. Tahmin
y_pred = gb_model.predict(X_test)

# 6. Başarı Metrikleri
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print("-" * 30)
print("Algorithm 7: Gradient Boosting Results (df10)")
print("-" * 30)
print(f"MAE: {mae:,.2f}")
print(f"RMSE: {rmse:,.2f}")
print(f"R2 Score: {r2:.4f}")
print("-" * 30)