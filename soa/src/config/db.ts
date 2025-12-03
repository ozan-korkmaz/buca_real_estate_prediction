import mongoose from 'mongoose';

export const connectDB = async () => {
    try {
        // MongoDB bağlantısını başlat
        const conn = await mongoose.connect(process.env.MONGO_URI || '');
        console.log(`MongoDB Bağlandı: ${conn.connection.host}`);
    } catch (error) {
        console.error('Veritabanı hatası:', error);
        process.exit(1);
    }
};