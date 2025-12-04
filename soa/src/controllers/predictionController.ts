import { Request, Response } from 'express';
import axios from 'axios';

export const predictPrice = async (req: Request, res: Response) => {
    try {
        const houseData = req.body;
        console.log('🤖 ML Servisine Giden Veri:', houseData);

        // 1. Python API'ye istek at
        // (Python'dan sadece {"predicted_price": 3500000} gibi saf bir cevap bekliyoruz)
        const response = await axios.post(process.env.ML_API_URL as string, houseData);

        const predictionResult = response.data;
        const price = predictionResult.predicted_price;

        // 2. Fiyat Aralığı Hesapla (Örn: %3 aşağısı ve %3 yukarısı)
        // Eğer Python servisi zaten min/max dönmüyorsa biz oluşturuyoruz.
        const margin = 0.03; // %3 sapma payı
        const minPrice = Math.floor(price * (1 - margin));
        const maxPrice = Math.ceil(price * (1 + margin));

        // 3. İstenen Response Formatını Hazırla
        const finalResponse = {
            predicted_price: price,
            price_range: {
                min: minPrice,
                max: maxPrice
            },
            currency: "TRY"
        };

        console.log('✅ Hesaplanmış Yanıt:', finalResponse);

        res.status(200).json({
            status: 'success',
            data: finalResponse
        });

    } catch (error: any) {
        console.error('❌ ML Servis Hatası:', error.message);
        res.status(503).json({
            status: 'error',
            message: 'Tahmin servisine ulaşılamadı veya model yüklenemedi.'
        });
    }
};