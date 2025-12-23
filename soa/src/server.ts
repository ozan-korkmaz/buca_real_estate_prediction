import dotenv from 'dotenv';
dotenv.config();

import express from 'express';
import cors from 'cors';
import { connectDB } from './config/db';
import { startListingSoapService } from "./soap/listingSoapService";

import authRoutes from './routes/authRoutes';
import listingRoutes from './routes/listingRoutes';
import predictionRoutes from './routes/predictionRoutes';
import agentRoutes from './routes/agentRoutes';
import commentRoutes from './routes/commentRoutes';
import userRoutes from './routes/userRoutes';

connectDB();
const app = express();

// 1 SOAP 
startListingSoapService(app);

// 2 Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cors({ origin: "http://127.0.0.1:8000", credentials: true }));

// 3 Api rotaları
app.use('/api', authRoutes);
app.use('/api/listings', listingRoutes);
app.use('/api/predict', predictionRoutes);
app.use('/api/agents', agentRoutes);
app.use('/api/comments', commentRoutes);
app.use('/api/users', userRoutes);

const PORT = process.env.PORT || 5001;
app.listen(PORT, () => console.log(`🚀 Server çalışıyor: http://localhost:${PORT}`));