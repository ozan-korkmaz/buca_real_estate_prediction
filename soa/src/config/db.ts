import mongoose from "mongoose";
import dotenv from "dotenv";

dotenv.config(); // ENV dosyası en üste yüklenecek

export const connectDB = async () => {
    try {
        const uri = process.env.MONGO_URI;

        if (!uri) {
            console.error("❌ MONGO_URI bulunamadı. .env dosyasını kontrol et.");
            process.exit(1);
        }

        const conn = await mongoose.connect(uri, {
            dbName: "realEstateDb"
        } as mongoose.ConnectOptions);

        console.log(`✅ MongoDB Bağlandı: ${conn.connection.name}`);

    } catch (error) {
        console.error("❌ Veritabanı bağlantı hatası:", error);
        process.exit(1);
    }
};
