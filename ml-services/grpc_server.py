import grpc
from concurrent import futures
import buca_pb2
import buca_pb2_grpc
import joblib
import pandas as pd
import numpy as np
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Model Yükleme
model_path = os.path.join(os.path.dirname(__file__), 'ridge_model.joblib')
MODEL = joblib.load(model_path)

# main.py'den alınan 41 Sütunlu tam liste
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

VARSAYILAN_DEGERLER = {
    'Bathrooms': 1, 'Number_Of_Floors': 5, 'Halls': 1, 'Listing_Age_Days': 10,
    'Posted_Month': 6, 'Location': 'other', 'Heating_Type': 'Combi Boiler',
    'Title': 'Condominium', 'Furnishing_Status': 'Not Furnished', 'Usage_Status': 'Empty'
}

class RealEstateServiceServicer(buca_pb2_grpc.RealEstateServiceServicer):
    def PredictPrice(self, request, context):
        try:
            # 2. Veri Hazırlama (main.py'deki mantık)
            model_input = VARSAYILAN_DEGERLER.copy()
            
            model_input['Rooms'] = int(request.room_count)
            model_input['Halls'] = int(request.hall_count)
            model_input['Net_m2'] = float(request.net_area)
            model_input['Floor'] = int(request.floor)
            model_input['Property_Age'] = int(request.building_age)
            model_input['Number_Of_Floors'] = int(request.total_floors)
            model_input['Bathrooms'] = int(request.bathroom_count)
            model_input['Location'] = str(request.location).lower()

            heating_map = {
                "kombi": "Combi Boiler", "merkezi": "Central", "klima": "Air Conditioning",
                "yerden isitma": "Underfloor Heating", "soba": "Stove"
            }
            model_input['Heating_Type'] = heating_map.get(request.heating_type, "Combi Boiler")
            model_input['Furnishing_Status'] = 'Furnished' if request.furnishing == 'furnished' else 'Not Furnished'
            
            usage_map = {"empty": "Empty", "owner": "Owner", "tenanted": "Tenanted"}
            model_input['Usage_Status'] = usage_map.get(request.usage_status, "Empty")

            # 3. DataFrame ve OHE (Sıralama Hatasını Çözen Kısım)
            df_raw = pd.DataFrame([model_input])
            kategorik_sutunlar = ['Location', 'Heating_Type', 'Title', 'Furnishing_Status', 'Usage_Status']
            df_ohe = pd.get_dummies(df_raw, columns=kategorik_sutunlar)

            # Modelin beklediği tüm sütunları 0 olarak oluştur
            final_df = pd.DataFrame(columns=MODEL_SUTUNLARI, data=np.zeros((1, len(MODEL_SUTUNLARI))))
            
            # Mevcut verileri eşleşen sütunlara yerleştir
            for col in df_ohe.columns:
                if col in final_df.columns:
                    final_df[col] = df_ohe[col]
            
            # SÜTUN SIRALAMASINI MODELİN BEKLEDİĞİ HALE GETİR (KRİTİK!)
            final_input = final_df[MODEL_SUTUNLARI]

            # 4. Tahmin
            prediction = MODEL.predict(final_input)[0]
            final_price = max(1000.0, float(prediction))

            logger.info(f"✅ Tahmin Başarılı: {final_price}")
            return buca_pb2.PredictionResponse(predicted_price=round(final_price, 2))

        except Exception as e:
            logger.error(f"❌ Tahmin Hatası: {str(e)}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return buca_pb2.PredictionResponse()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    buca_pb2_grpc.add_RealEstateServiceServicer_to_server(RealEstateServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info("🚀 gRPC Sunucusu 50051'de YENİ KODLA çalışıyor...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()