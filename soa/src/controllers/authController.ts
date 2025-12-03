import { Request, Response } from 'express';
import jwt from 'jsonwebtoken';
import User from '../models/User';

// --- REGISTER ---
export const register = async (req: Request, res: Response) => {
    try {
        // Frontend first_name ve last_name gönderiyor, bunları alıyoruz
        const { first_name, last_name, email, password, phone } = req.body;

        const existingUser = await User.findOne({ email });
        if (existingUser) return res.status(400).json({ status: 'error', message: 'Email kayıtlı.' });

        // İsimleri birleştirip 'name' olarak kaydediyoruz
        await User.create({
            name: `${first_name} ${last_name}`,
            email,
            password,
            phone: phone || "", // Telefon opsiyonel
            role: 'user'
        });

        res.status(201).json({ status: 'success', message: 'Kullanıcı oluşturuldu.' });
    } catch (error) {
        res.status(500).json({ status: 'error', message: 'Sunucu hatası' });
    }
};

// --- LOGIN ---
export const login = async (req: Request, res: Response) => {
    try {
        const { email, password } = req.body;
        const user = await User.findOne({ email });

        // Debug Logları (İstersen silebilirsin)
        console.log("Gelen Şifre:", password);
        if (user) console.log("DB Şifre:", user.password);

        // Şifre Kontrolü (Hashsiz)
        if (!user || password !== user.password) {
            return res.status(401).json({ status: 'error', message: 'Hatalı giriş bilgileri.' });
        }

        const token = jwt.sign(
            { id: user._id, role: user.role }, // Role bilgisini de token'a ekledik
            process.env.JWT_SECRET as string,
            { expiresIn: '1d' }
        );

        res.json({
            status: 'success',
            data: {
                access_token: token,
                token_type: 'bearer',
                user_name: user.name // DÜZELTME: first_name yerine user.name kullanıyoruz
            }
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({ status: 'error', message: 'Sunucu hatası' });
    }
};