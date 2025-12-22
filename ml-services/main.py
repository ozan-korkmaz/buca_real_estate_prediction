import pandas as pd
import numpy as np
import joblib
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import uvicorn
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model yolu
model_path = os.path.join(os.path.dirname(__file__), 'ridge_model.joblib')

try:
    MODEL = joblib.load(model_path)
    MODEL_VERSION = "v1.0"
    logger.info("Ridge Model başarıyla yüklendi.")
except FileNotFoundError:
    MODEL = None
    MODEL_VERSION = "DEV_MODE (No Model)"
    logger.error(f"Model dosyası bulunamadı: {model_path}")

# 41 Sütunlu tam liste (Eğitim setindeki sıra çok önemli)
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

# Varsayılan değerler (Eğer formdan bir şey gelmezse devreye girer)
VARSAYILAN_DEGERLER = {
    'Bathrooms': 1,
    'Number_Of_Floors': 5,
    'Halls': 1,
    'Listing_Age_Days': 10, # Yeni ilan gibi düşün
    'Posted_Month': 6,
    'Location': 'other',
    'Heating_Type': 'Combi Boiler',
    'Title': 'Condominium',
    'Furnishing_Status': 'Not Furnished',
    'Usage_Status': 'Empty'
}

app = FastAPI(title="ML Ev Fiyat Tahmin Servisi")

# Genişletilmiş Request Modeli
class RequestFeatures(BaseModel):
    room_count: int
    hall_count: int = 1
    net_area: float
    floor: int
    total_floors: int = 5
    building_age: int
    bathroom_count: int = 1
    location: str = "other"          # Formdan gelen "buca-koop"
    heating_type: str = "kombi"      # Formdan gelen "kombi"
    furnishing: str = "unfurnished"  # "furnished" / "unfurnished"
    usage_status: str = "empty"      # "empty" / "owner" / "tenanted"

@app.post("/predict", tags=["Tahmin Servisi"], status_code=status.HTTP_200_OK)
def predict(data: RequestFeatures):
    
    if MODEL is None:
        return {"predicted_price": 3500000.0, "currency": "TRY", "model_version": "dummy"}

    try:
        input_dict = data.model_dump()
        model_input = VARSAYILAN_DEGERLER.copy()
        
        # 1. Sayısal Değerleri Ata
        model_input['Rooms'] = input_dict['room_count']
        model_input['Halls'] = input_dict['hall_count']
        model_input['Net_m2'] = input_dict['net_area']
        model_input['Floor'] = input_dict['floor']
        model_input['Property_Age'] = input_dict['building_age']
        model_input['Number_Of_Floors'] = input_dict['total_floors']
        model_input['Bathrooms'] = input_dict['bathroom_count']

        # 2. Kategorik Mapping (Form String -> Model String)
        
        # Lokasyon
        # Formdan gelen "buca-koop" -> Modeldeki sütun "Location_buca-koop"
        # O yüzden buraya sadece raw değerini koyuyoruz, get_dummies halledecek.
        model_input['Location'] = input_dict['location']

        # Isıtma
        heating_map = {
            "kombi": "Combi Boiler",
            "merkezi": "Central",
            "klima": "Air Conditioning",
            "yerden isitma": "Underfloor Heating",
            "soba": "Stove" # Modelde soba sütunu yoksa diğer/hiçbiri olacak
        }
        model_input['Heating_Type'] = heating_map.get(input_dict['heating_type'], "Combi Boiler")

        # Eşya
        if input_dict['furnishing'] == 'furnished':
            model_input['Furnishing_Status'] = 'Furnished'
        else:
            model_input['Furnishing_Status'] = 'Not Furnished'

        # Kullanım Durumu
        usage_map = {
            "empty": "Empty",
            "owner": "Owner",
            "tenanted": "Tenanted"
        }
        model_input['Usage_Status'] = usage_map.get(input_dict['usage_status'], "Empty")

        # 3. DataFrame ve OHE
        ham_veri_df = pd.DataFrame([model_input])
        
        # OHE yaparken kullanacağımız sütunlar
        kategorik_sutunlar = ['Location', 'Heating_Type', 'Title', 'Furnishing_Status', 'Usage_Status']
        
        # Veriyi OHE'ye sok
        ohe_df = pd.get_dummies(ham_veri_df, columns=kategorik_sutunlar, dtype=int)
        
        # 4. Eksik Sütunları Tamamla (Model 41 sütun bekliyor)
        final_df = pd.DataFrame(columns=MODEL_SUTUNLARI, data=np.zeros((1, len(MODEL_SUTUNLARI))), dtype=float)
        
        for col in ohe_df.columns:
            if col in final_df.columns:
                final_df[col] = ohe_df[col]
        
        # Sıralamanın doğru olduğundan emin ol
        final_input = final_df[MODEL_SUTUNLARI]

        # 5. Tahmin
        predicted_price = MODEL.predict(final_input)[0]
        predicted_price = max(1000.0, predicted_price)

        return {
            "predicted_price": round(float(predicted_price), 2),
            "currency": "TRY",
            "model_version": MODEL_VERSION,
            "confidence_score": 1.0
        }

    except Exception as e:
        logger.error(f"Prediction Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)