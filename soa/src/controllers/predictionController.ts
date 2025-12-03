import { Request, Response } from 'express';
import axios from 'axios';

export const predictPrice = async (req: Request, res: Response) => {
    try {
        // 1. Frontend'den gelen veriyi al (oda sayısı, m2 vb.)
        const houseData = req.body;

        console.log('🤖 ML Servisine Giden Veri:', houseData);

        // 2. Python API'ye POST isteği at
        // (Arkadaşının API'si JSON bekliyordur)
        const response = await axios.post(process.env.ML_API_URL as string, houseData);

        // 3. Python'dan gelen cevabı al
        const predictionResult = response.data;

        console.log('✅ ML Servisinden Gelen Cevap:', predictionResult);

        // 4. Sonucu Frontend'e ilet
        res.status(200).json({
            status: 'success',
            data: predictionResult
        });

    } catch (error: any) {
        console.error('❌ ML Servis Hatası:', error.message);

        // Python servisi kapalıysa veya hata verdiyse
        res.status(503).json({
            status: 'error',
            message: 'Tahmin servisine ulaşılamadı. Lütfen Python sunucusunun çalıştığından emin olun.'
        });
    }
};