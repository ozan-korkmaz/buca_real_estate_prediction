import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 1. Veri Yükleme
df_final = pd.read_csv('3-dataset-cleaned.csv')
X = df_final.drop('Price', axis=1)
y = df_final['Price']

# 2. Eğitim/Test Ayrımı
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Aranacak Parametreler (Alpha değerleri)
# 0.01'den 100'e kadar farklı ceza miktarlarını deneyeceğiz.
param_grid = {'alpha': [0.01, 0.1, 1, 5, 10, 20, 50, 100]}

# 4. Grid Search Başlatma
ridge = Ridge()
grid_search = GridSearchCV(estimator=ridge, param_grid=param_grid, cv=5, scoring='r2', verbose=1)

# 5. Modeli Eğit (En iyisini bul)
grid_search.fit(X_train, y_train)

# 6. En İyi Sonuçlar
best_model = grid_search.best_estimator_
y_pred = best_model.predict(X_test)

print("-" * 30)
print(f"En İyi Alpha Değeri: {grid_search.best_params_['alpha']}")
print("-" * 30)
print(f"Optimize Edilmiş R2 Score: {r2_score(y_test, y_pred):.4f}")
print(f"Optimize Edilmiş MAE: {mean_absolute_error(y_test, y_pred):,.0f} TL")
print("-" * 30)