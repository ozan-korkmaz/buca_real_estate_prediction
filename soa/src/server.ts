import dotenv from 'dotenv';
dotenv.config();   // ENV kesinlikle ilk sırada

import express from 'express';
import cors from 'cors';
import { connectDB } from './config/db';

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

const PORT = process.env.PORT || 5001;
app.listen(PORT, () => console.log(`🚀 Server çalışıyor: http://localhost:${PORT}`));
