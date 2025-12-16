import { Request, Response, NextFunction } from 'express';
import jwt, { JwtPayload } from 'jsonwebtoken';
import { Document } from 'mongoose';
// Agent ve User modellerini import ediyoruz
import User from "../models/User";
import Agent from "../models/Agent"; 


// 1. TİP TANIMLAMALARI: User ve Agent'ların ortak taşıdığı alanları tanımlıyoruz
interface IUserDocument extends Document {
    id: string; // ListingController'ın kullandığı alan
    email: string;
    role: string;
    name: string;
    phone?: string; 
    agency_name?: string; // ListingController'ın kullandığı alan
}

interface DecodedToken extends JwtPayload {
    sub?: string; 
    id?: string;  
}

// Request tipini genişletiyoruz (UserController'daki TSError'ı engeller)
export interface AuthRequest extends Request {
    user?: IUserDocument; 
}


export const protect = async (req: AuthRequest, res: Response, next: NextFunction) => {
    let token: string | undefined;
    let user: IUserDocument | null = null;
    let userId: string | undefined;

    // 1. Token'ı Header'dan al
    if (req.headers.authorization && req.headers.authorization.startsWith("Bearer")) {
        try {
            token = req.headers.authorization.split(" ")[1];

            const decoded = jwt.verify(
                token,
                process.env.JWT_SECRET as string
            ) as DecodedToken;

            const decodedId = decoded.sub || decoded.id; 
            userId = decodedId ? String(decodedId) : undefined; 

            if (!userId) {
                console.error("DEBUG HATA (auth.ts - 1): Token'da geçerli kullanıcı ID (sub/id) alanı bulunamadı.");
                return res.status(401).json({ status: 'error', message: "Gecersiz token: Kullanici ID'si eksik" });
            }
            
            console.log(`DEBUG (auth.ts - 1): Token'dan Çıkarılan User ID: ${userId}`);

            // 🚨 KRİTİK DÜZELTME: Önce Agent koleksiyonunda ara (İlan ekleyen Agent olabilir)
            // Agent modelinden çekilen veriyi IUserDocument tipine cast ediyoruz
            user = await Agent.findById(userId)
                .select("name email role phone agency_name") as (IUserDocument | null);

            if (user) {
                console.log(`DEBUG (auth.ts - 2A): Agent BULUNDU. Email: ${user.email}, Rol: ${user.role}`);
            } else {
                // Eğer Agent değilse, normal Users koleksiyonunda ara
                user = await User.findById(userId)
                    .select("name surname email role phone") as (IUserDocument | null);
                
                if (user) {
                    // Normal kullanıcıların agency_name alanı olmayabilir, bu sorun değil.
                    console.log(`DEBUG (auth.ts - 2B): Normal Kullanıcı BULUNDU. Email: ${user.email}, Rol: ${user.role}`);
                }
            }

            if (!user) {
                // Her iki koleksiyonda da bulunamadıysa hata ver
                console.error(`DEBUG HATA (auth.ts - 3): Veritabaninda ID'si ${userId} olan kullanici (User veya Agent) BULUNAMADI.`);
                return res.status(401).json({ status: 'error', message: "User bulunamadi" });
            }

            req.user = user;
            next();
        } catch (error: any) {
            const errorMessage = error.name === 'TokenExpiredError' 
                ? "Token süresi doldu. Lutfen tekrar giris yapin." 
                : "Gecersiz token veya imza hatasi.";
            
            console.error(`DEBUG HATA (auth.ts - Catch): JWT dogrulama hatasi: ${errorMessage}. Hata detayi: ${error.message}`);
            return res.status(401).json({ status: 'error', message: errorMessage });
        }
    }

    if (!token) {
        return res.status(401).json({ status: 'error', message: "Token yok (Bearer şeması eksik)." });
    }
};

// ... Diğer restrictTo gibi fonksiyonlar