import { Request, Response } from 'express';
import { Comment } from '../models/Comment';
import mongoose from 'mongoose';

// Yorumları Listele
export const getListingComments = async (req: Request, res: Response): Promise<void> => {
    try {
        const { listing_id } = req.query;

        if (!listing_id) {
            res.status(400).json({ status: 'error', message: 'listing_id parametresi gerekli.' });
            return;
        }

        let query: any = { listing_id: listing_id };
        if (mongoose.Types.ObjectId.isValid(listing_id as string)) {
            query = { 
                $or: [
                    { listing_id: listing_id },
                    { listing_id: new mongoose.Types.ObjectId(listing_id as string) }
                ] 
            };
        }

        // DEĞİŞİKLİK BURADA: .populate('user_id', 'name') eklendi.
        // Bu komut, 'user_id' alanındaki ID'yi alıp User tablosuna gider ve 'name' bilgisini getirir.
        const comments = await Comment.find(query)
            .populate('user_id', 'name email') // User tablosundan 'name' ve 'email' alanlarını çek
            .sort({ created_at: -1 })
            .lean();

        res.status(200).json({ status: 'success', data: comments });

    } catch (error) {
        console.error('Yorum çekme hatası:', error);
        res.status(500).json({ status: 'error', message: 'Sunucu hatası.' });
    }
};

// Yorum Ekle
export const createComment = async (req: Request, res: Response): Promise<void> => {
    try {
        const { listing_id, user_id, content, rating } = req.body;

        console.log("📝 Yorum Kayıt İsteği:", req.body);

        if (!listing_id || !user_id || !content || !rating) {
            res.status(400).json({ status: 'error', message: 'Eksik veri: listing_id, user_id, content ve rating zorunludur.' });
            return;
        }

        const newComment = new Comment({
            listing_id,
            user_id,
            text: content, // Modelde 'text', formda 'content'
            rating,
            created_at: new Date()
        });

        await newComment.save();
        console.log("✅ Yorum Kaydedildi:", newComment._id);

        res.status(201).json({
            status: 'success',
            message: 'Yorum başarıyla eklendi.',
            data: newComment
        });

    } catch (error) {
        console.error('❌ Yorum ekleme hatası:', error);
        res.status(500).json({ status: 'error', message: 'Yorum kaydedilemedi.' });
    }
};