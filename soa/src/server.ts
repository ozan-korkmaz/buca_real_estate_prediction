import dotenv from 'dotenv';
dotenv.config();   // ENV kesinlikle ilk sırada

import express from 'express';
import cors from 'cors';
import { connectDB } from './config/db';

import { initSoapService } from './soapService';
import { grpcClient } from './grpcClient';

import authRoutes from './routes/authRoutes';
import listingRoutes from './routes/listingRoutes';
import predictionRoutes from './routes/predictionRoutes';
import agentRoutes from './routes/agentRoutes';
import commentRoutes from './routes/commentRoutes';
import userRoutes from './routes/userRoutes';


// --- DB BAĞLANTI ---
connectDB();

const app = express();

app.use(cors({
    origin: "http://127.0.0.1:8000",
    credentials: true
}));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// --- ROUTES ---
app.use('/api', authRoutes);
app.use('/api/listings', listingRoutes);
app.use('/api/predict', predictionRoutes);
app.use('/api/agents', agentRoutes);
app.use('/api/comments', commentRoutes);
app.use('/api/users', userRoutes);

app.get('/grpc', (req, res) => {
    // Örnek veri: 100m2, 5 yaşında bina
    const istek = { metrekare: 100, bina_yasi: 5 };

    console.log("Python'a gRPC ile soruluyor...");

    grpcClient.HizliFiyatHesapla(istek, (error: any, response: any) => {
        if (error) {
            console.error("gRPC Hatası:", error);
            res.status(500).json({ error: "Python servisine ulaşılamadı", detay: error });
        } else {
            console.log("Python'dan Cevap:", response);
            res.json(response);
        }
    });
});



initSoapService(app);
const PORT = process.env.PORT || 5001;
app.listen(PORT, () => console.log(`🚀 Server çalışıyor: http://localhost:${PORT}`));
