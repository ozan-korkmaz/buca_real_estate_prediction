import pandas as pd
import numpy as np
import joblib # joblib kütüphanesini içe aktarın
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 1. Veri Setini Yükleme (df5 olarak)
# Not: Bu satırın çalışması için '3-dataset-cleaned.csv' dosyasının mevcut olması gerekir.
try:
    df5 = pd.read_csv('3-dataset-cleaned.csv')
except FileNotFoundError:
    print("Hata: '3-dataset-cleaned.csv' dosyası bulunamadı. Lütfen dosya yolunu kontrol edin.")
    # Örnek bir DataFrame oluşturarak devam edelim
    df5 = pd.DataFrame({'Price': np.random.rand(100), 'Feature1': np.random.rand(100), 'Feature2': np.random.rand(100)})

# 2. Hedef ve Özelliklerin Ayrılması
y = df5['Price']
X = df5.drop('Price', axis=1)

# 3. Eğitim ve Test Setlerine Ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Ridge Modelini Kurma
ridge_model = Ridge(alpha=1.0)
ridge_model.fit(X_train, y_train)

# 5. Tahmin
y_pred = ridge_model.predict(X_test)

# 6. Başarı Metrikleri
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print("-" * 30)
print("Algoritma 2: Ridge Regression Sonuçları (df5)")
print("-" * 30)
print(f"MAE: {mae:,.2f}")
print(f"RMSE: {rmse:,.2f}")
print(f"R2 Score: {r2:.4f}")
print("-" * 30)

# 7. Modeli Dosyalama (Kaydetme) 🚀
joblib.dump(ridge_model, 'ridge_model.joblib')
print("Model başarıyla 'ridge_model.joblib' dosyasına kaydedildi.")