import express from 'express';
import dotenv from 'dotenv';
import cors from 'cors';
import { connectDB } from './config/db';
import authRoutes from './routes/authRoutes';
import listingRoutes from './routes/listingRoutes';
import predictionRoutes from './routes/predictionRoutes';

dotenv.config();
connectDB();

const app = express();

app.use(cors());
app.use(express.json());

// Rotalar
app.use('/api', authRoutes);
app.use('/api/listings', listingRoutes);
app.use('/api/predict', predictionRoutes);
const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
    console.log(`Server çalışıyor: http://localhost:${PORT}`);
});