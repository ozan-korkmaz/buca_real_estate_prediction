import pandas as pd
import numpy as np
import joblib
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import uvicorn
import logging

# Logger'ı ayarlama
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- MODEL YÜKLEME VE TANIMLAR ---
# Model dosyanızın adını kontrol edin ve aynı dizine kaydedin!
try:
    MODEL = joblib.load('ridge_model.joblib')
    MODEL_VERSION = "v1.0"
    logger.info("Ridge Model başarıyla yüklendi.")
except FileNotFoundError:
    MODEL = None
    MODEL_VERSION = "DEV_MODE (No Model)"
    logger.error("Model dosyası bulunamadı! Servis tahmin yapamayacak.")

# Sizin 41 sütunluk nihai listeniz
MODEL_SUTUNLARI = [
    'Bathrooms', 'Number_Of_Floors', 'Floor', 'Property_Age', 'Location_akincilar', 
    'Location_ataturk', 'Location_baris', 'Location_buca-koop', 'Location_camlikule', 
    'Location_efeler', 'Location_firat', 'Location_goksu', 'Location_hurriyet', 
    'Location_inonu', 'Location_izkent', 'Location_kozagac', 'Location_kurucesme', 
    'Location_laleli', 'Location_menderes', 'Location_other', 'Location_yaylacik', 
    'Location_yenigun', 'Location_yesilbaglar', 'Location_yigitler', 'Location_yildiz', 
    'Listing_Age_Days', 'Posted_Month', 'Rooms', 'Halls', 'Net_m2', 
    'Heating_Type_Air Conditioning', 'Heating_Type_Central', 'Heating_Type_Combi Boiler', 
    'Heating_Type_Underfloor Heating', 'Title_Condominium', 'Title_Floor Easement', 
    'Furnishing_Status_Furnished', 'Furnishing_Status_Not Furnished', 
    'Usage_Status_Empty', 'Usage_Status_Owner', 'Usage_Status_Tenanted'
]

# API'den gelmeyen (veya modelde zorunlu olan) özellikler için varsayılan değerler
# Bu değerler, model eğitim setindeki en yaygın/ortalama değerler olmalıdır.
VARSAYILAN_DEGERLER = {
    'Bathrooms': 1,               # Varsayılan Banyo Sayısı
    'Number_Of_Floors': 5,        # Varsayılan Toplam Kat Sayısı
    'Halls': 1,                   # Varsayılan Salon Sayısı
    'Listing_Age_Days': 30,       # Varsayılan İlan Yaşı
    'Posted_Month': 6,            # Varsayılan İlan Ayı
    # Kategorik Varsayılanlar (OHE gerektirenler)
    'Location': 'other',          # En genel kategori
    'Title': 'Condominium',       # Varsayılan Tapu Durumu
    'Furnishing_Status': 'Not Furnished', # Varsayılan Eşya Durumu
    'Usage_Status': 'Owner'       # Varsayılan Kullanım Durumu
}

app = FastAPI(title="ML Ev Fiyat Tahmin Servisi")

# --- 2. BEKLENEN İSTEK FORMATI (Pydantic Modeli) ---
class RequestFeatures(BaseModel):
    # Zorunlu alanlar (API dokümanında belirtilenler)
    room_count: int = Field(..., description="Oda sayısı (Modelde 'Rooms' olarak kullanılır)")
    net_area: float = Field(..., description="Net metrekare (Modelde 'Net_m2' olarak kullanılır)")
    floor: int = Field(..., description="Bulunduğu kat (Modelde 'Floor' olarak kullanılır)")
    building_age: int = Field(..., description="Bina yaşı (Modelde 'Property_Age' olarak kullanılır)")
    
    # Opsiyonel alanlar
    gross_area: float | None = Field(None, description="Brüt metrekare (Modelde kullanılmıyor)")
    location_score: int | None = Field(None, description="Konum Skoru (Modelde kullanılmıyor)")
    # Isıtma tipi, None gelirse varsayılan atanacak
    heating_type: str | None = Field(None, description="Isıtma tipi (Örn: Kombi, Merkezi, Klima)")
    
    # API'den gelmeyen ancak modelde kullanılan diğer özellikler için geçici girdiler
    # Node.js backend'i bu alanları göndermeyeceği için, modelin çalışması amacıyla buraya eklenebilir
    # ya da bu alanlar için VARSAYILAN DEGERLER kullanılmalıdır. Biz varsayılanları kullanıyoruz.


# --- 3. TAHMİN ENDPOINT'İ: /predict ---
@app.post("/predict", 
          tags=["Tahmin Servisi"],
          status_code=status.HTTP_200_OK)
def predict(data: RequestFeatures):
    
    if MODEL is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": "Model servisi geçici olarak kullanılamıyor. Model yüklenemedi."}
        )

    try:
        # 1. Ham Girdiyi Sözlüğe Çevir ve Varsayılanlarla Birleştir
        input_dict = data.model_dump(exclude_none=True)
        
        # Temel verileri varsayılanlarla başlat
        model_input = VARSAYILAN_DEGERLER.copy()
        
        # API Girdilerini Eşleştirme ve Varsayılanları Ezme
        model_input['Rooms'] = input_dict.get('room_count')
        model_input['Net_m2'] = input_dict.get('net_area')
        model_input['Floor'] = input_dict.get('floor')
        model_input['Property_Age'] = input_dict.get('building_age')
        
        # Isıtma Tipi Eşleştirme (Gelen değeri modelin beklediği formata çevir)
        heating_map = {
            "kombi": "Combi Boiler",
            "merkezi": "Central",
            "klima": "Air Conditioning",
            "yerden isitma": "Underfloor Heating"
        }
        
        raw_heating = input_dict.get('heating_type', '').lower()
        # Eğer gelen değer haritada yoksa (veya None ise), varsayılanı kullan: Combi Boiler
        model_input['Heating_Type'] = heating_map.get(raw_heating, "Combi Boiler")

        # 2. DataFrame Oluşturma ve OHE Uygulama
        ham_veri_df = pd.DataFrame([model_input])
        
        kategorik_sutunlar = ['Location', 'Heating_Type', 'Title', 'Furnishing_Status', 'Usage_Status']
        ohe_df = pd.get_dummies(ham_veri_df, columns=kategorik_sutunlar, dtype=int)
        
        # 3. Nihai Giriş Matrisini Oluşturma (41 Sütun)
        final_df = pd.DataFrame(columns=MODEL_SUTUNLARI, data=np.zeros((1, len(MODEL_SUTUNLARI))), dtype=float)

        # OHE yapılmış girdileri, boş DataFrame'deki doğru konumlara kopyala
        for col in ohe_df.columns:
            if col in final_df.columns:
                final_df[col] = ohe_df[col]
                
        final_input = final_df[MODEL_SUTUNLARI]

        # 4. Tahmin Yapma
        predicted_price = MODEL.predict(final_input)[0]
        
        # Fiyat tahminleri pozitif olmalıdır
        predicted_price = max(1000.0, predicted_price) 

        # 5. İstenen Çıktı Formatını Oluşturma
        return {
            "predicted_price": round(float(predicted_price), 2),
            "currency": "TRY",
            "model_version": MODEL_VERSION,
            "confidence_score": 1.0 # Güven skoru sabit bırakıldı
        }

    except Exception as e:
        logger.error(f"Tahmin işlemi sırasında hata oluştu: {e}")
        # Hata Senaryosu (500)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Veri işleme sırasında beklenmedik bir hata oluştu: {e}"}
        )

# --- UYGULAMA ÇALIŞTIRMA ---
if __name__ == "__main__":
    # Kılavuzdaki PORT: 5001'de çalıştır
    # Eğer bu kodu kullanırsanız, terminalde 'python main.py' çalıştırmanız yeterlidir.
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)