import { Request, Response } from 'express';
import { Comment } from '../models/Comment';
import mongoose from 'mongoose';

export const getListingComments = async (req: Request, res: Response): Promise<void> => {
    try {
        const { listing_id } = req.query;

        if (!listing_id || !mongoose.Types.ObjectId.isValid(listing_id as string)) {
            res.status(400).json({ status: 'error', message: 'Geçersiz veya eksik listing_id.' });
            return;
        }

        const comments = await Comment.find({ listing_id: listing_id }).lean();

        res.status(200).json({ status: 'success', data: comments });

    } catch (error) {
        console.error('Yorum çekme hatası:', error);
        const errorMessage = error instanceof Error ? error.message : 'Bilinmeyen bir hata oluştu';
        res.status(500).json({ status: 'error', message: 'Sunucu hatası', error: errorMessage });
    }
};