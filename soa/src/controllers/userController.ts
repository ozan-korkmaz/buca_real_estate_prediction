import { Request, Response } from 'express';
import User from '../models/User';
import mongoose from 'mongoose';
import { AuthRequest } from "../middleware/auth"; // Correct import of AuthRequest

export const getUserById = async (req: Request, res: Response): Promise<void> => {
    try {
        const userId = req.params.id; 

        if (!mongoose.Types.ObjectId.isValid(userId)) {
            res.status(400).json({ status: 'error', message: 'Geçersiz Kullanıcı ID formatı.' });
            return;
        }

        const user = await User.findById(userId).select('name email phone role');         

        console.log('DEBUG (getUserById): Fetched User Data:', user);

        if (!user) {
            res.status(404).json({ status: 'error', message: 'Kullanıcı bulunamadı.' });
            return;
        }

        res.status(200).json({ status: 'success', data: user }); 
    
    } catch (error) {
        console.error('Kullanıcı çekme hatası (getUserById):', error);
        const errorMessage = error instanceof Error ? error.message : 'Bilinmeyen bir hata oluştu';
        res.status(500).json({ status: 'error', message: 'Sunucu hatası', error: errorMessage });
    }
};

export const getMe = async (req: AuthRequest, res: Response) => {
    // req.user'ın var olduğunu kontrol ediyoruz
    if (!req.user) {
        return res.status(401).json({ status: 'error', message: "Yetkisiz islem." });
    }

    res.status(200).json({
        status: "success",
        data: req.user
    });
};

export const updateMe = async (req: AuthRequest, res: Response) => {
    // 🚨 Hata düzeltildi: req.user'ın varlığını kontrol et
    if (!req.user) {
        return res.status(401).json({ status: 'error', message: "Yetkilendirme gerekli." });
    }
    
    const userId = req.user.id; // Artık güvenli bir şekilde ID'ye erişebiliriz

    const updates: any = {};

    if (req.body.name) updates.name = req.body.name;
    if (req.body.email) updates.email = req.body.email;
    if (req.body.password) updates.password = req.body.password;
    if (req.body.phone) updates.phone = req.body.phone;

    try {
        const updatedUser = await User.findByIdAndUpdate(
            userId, 
            updates,
            { new: true, runValidators: true }
        ).select("name email role phone");

        if (!updatedUser) {
             return res.status(404).json({ status: 'error', message: 'Kullanıcı bulunamadı (güncelleme başarısız).' });
        }

        res.status(200).json({
            status: "success",
            data: updatedUser
        });
    } catch (error: any) {
        console.error('DEBUG HATA (updateMe):', error);
        res.status(500).json({ status: 'error', message: 'Güncelleme başarısız.', error: error.message });
    }
};