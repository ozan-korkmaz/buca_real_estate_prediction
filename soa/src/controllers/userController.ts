import { Request, Response } from 'express';
import User from '../models/User';
import mongoose from 'mongoose';
import { AuthRequest } from "../middleware/auth";

export const getUserById = async (req: Request, res: Response): Promise<void> => {
    try {
  
        const userId = req.params.id; 

        if (!mongoose.Types.ObjectId.isValid(userId)) {
            res.status(400).json({ status: 'error', message: 'Geçersiz Kullanıcı ID formatı.' });
            return;
        }

        //phone eklendi
        const user = await User.findById(userId).select('name email phone role');         

        console.log('DEBUG: Fetched User Data (Updated Projection):', user);

        if (!user) {
            res.status(404).json({ status: 'error', message: 'Kullanıcı bulunamadı.' });
            return;
        }

        // Dönen nesnede artık 'phone' alanı bulunacaktır.
        res.status(200).json({ status: 'success', data: user }); 
    
    } catch (error) {
        console.error('Kullanıcı çekme hatası:', error);

        const errorMessage = error instanceof Error ? error.message : 'Bilinmeyen bir hata oluştu';
        res.status(500).json({ status: 'error', message: 'Sunucu hatası', error: errorMessage });
    }
};

export const getMe = async (req: AuthRequest, res: Response) => {
    if (!req.user) {
        return res.status(401).json({ message: "Yetkisiz" });
    }

    res.status(200).json({
        status: "success",
        data: req.user
    });
};

export const updateMe = async (req: AuthRequest, res: Response) => {
    const updates: any = {};

    if (req.body.name) updates.name = req.body.name;
    if (req.body.email) updates.email = req.body.email;
    if (req.body.password) updates.password = req.body.password;

    const updatedUser = await User.findByIdAndUpdate(
        req.user._id,
        updates,
        { new: true }
    ).select("name email role phone");

    res.status(200).json({
        status: "success",
        data: updatedUser
    });
};
