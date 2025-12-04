import { Request, Response } from 'express';
import  User  from '../models/User';
import mongoose from 'mongoose';

export const getUserById = async (req: Request, res: Response): Promise<void> => {
    try {
        const userId = req.params.id;

        if (!mongoose.Types.ObjectId.isValid(userId)) {
            res.status(400).json({ status: 'error', message: 'Geçersiz Kullanıcı ID formatı.' });
            return;
        }

        const objectId = new mongoose.Types.ObjectId(userId);
        const user = await User.findById(userId).select('name');
        console.log('DEBUG: Fetched User Data:', user);

        if (!user) {
            res.status(404).json({ status: 'error', message: 'Kullanıcı bulunamadı.' });
            return;
        }

        res.status(200).json({ status: 'success', data: user }); // <-- Bu satır doğru olmalı
    
    } catch (error) {
        console.error('Kullanıcı çekme hatası:', error);

        const errorMessage = error instanceof Error ? error.message : 'Bilinmeyen bir hata oluştu';
        res.status(500).json({ status: 'error', message: 'Sunucu hatası', error: errorMessage });
    }
};