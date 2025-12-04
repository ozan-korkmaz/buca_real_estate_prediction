import express from 'express';
import dotenv from 'dotenv';
import cors from 'cors';
import { connectDB } from './config/db';
import authRoutes from './routes/authRoutes';
import listingRoutes from './routes/listingRoutes';
import predictionRoutes from './routes/predictionRoutes';
import agentRoutes from './routes/agentRoutes'; // Bu satır ekli olmalı
import commentRoutes from './routes/commentRoutes'; // <-- Yorum rotası
import userRoutes from './routes/userRoutes';     // <-- Kullanıcı rotası

dotenv.config();
connectDB();

const app = express();

app.use(cors());
app.use(express.json());

// Rotalar
app.use('/api', authRoutes);
app.use('/api/listings', listingRoutes);
app.use('/api/predict', predictionRoutes);
app.use('/api/agents', agentRoutes); // <-- Bu satır, '/api/agents' yoluyla Agent rotasını etkinleştirir.
app.use('/api/comments', commentRoutes); // <-- Eklendi       // <-- Eklendi
app.use('/api/users', userRoutes);
const PORT = process.env.PORT || 5001;

app.listen(PORT, () => {
    console.log(`Server çalışıyor: http://localhost:${PORT}`);
});