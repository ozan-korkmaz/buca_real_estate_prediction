import { Request, Response } from 'express';
import axios from 'axios';
import client from '../grpcClient';

export const predictPrice = async (req: Request, res: Response) => {
    try {
        const houseData = req.body;
        console.log('🤖 ML Servisine (gRPC) Giden Veri:', houseData);

        client.PredictPrice(houseData, (error: any, response: any) => {
            if (error) {
                console.error('❌ gRPC Hatası:', error);
                return res.status(503).json({
                    status: 'error',
                    message: 'gRPC servisine ulaşılamadı.'
                });
            }

            // python gRPC'den gelen saf fiyat
            const price = response.predicted_price;

            // fiyat arslığı hesapla 
            const margin = 0.03;
            const minPrice = Math.floor(price * (1 - margin));
            const maxPrice = Math.ceil(price * (1 + margin));

            const finalResponse = {
                predicted_price: price,
                price_range: {
                    min: minPrice,
                    max: maxPrice
                },
                currency: "TRY"
            };

            console.log("✅ gRPC'den Gelen ve Hesaplanan Yanıt:", finalResponse);

            res.status(200).json({
                status: 'success',
                data: finalResponse
            });
        });

    } catch (error: any) {
        console.error('❌ ML Servis Hatası:', error.message);
        res.status(500).json({ status: 'error', message: 'İşlem sırasında hata oluştu.' });
    }
};