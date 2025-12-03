import { Request, Response } from 'express';
import Listing from '../models/Listing';
import { AuthRequest } from '../middleware/auth';

export const getListings = async (req: Request, res: Response) => {
    try {
        const listings = await Listing.find().sort({ created_at: -1 });
        res.status(200).json({ status: 'success', data: listings });
    } catch (error) {
        res.status(500).json({ status: 'error', message: 'Hata oluştu' });
    }
};

export const createListing = async (req: AuthRequest, res: Response) => {
    try {
        // new Listing() kullanarak TypeScript hatasını engelliyoruz
        const newListing = new Listing({
            ...req.body,
            user: req.user.id // Token'dan gelen user id
        });

        await newListing.save();

        res.status(201).json({
            status: 'success',
            message: 'İlan oluşturuldu.',
            data: { id: newListing._id }
        });
    } catch (error) {
        res.status(400).json({ status: 'error', message: 'Kayıt başarısız', error });
    }
};

export const getListingById = async (req: Request, res: Response) => {
    try {
        const listing = await Listing.findById(req.params.id);
        if (!listing) return res.status(404).json({ status: 'error', message: 'İlan bulunamadı' });
        res.json({ status: 'success', data: listing });
    } catch (error) {
        res.status(500).json({ status: 'error', message: 'Sunucu hatası' });
    }
};

export const deleteListing = async (req: Request, res: Response) => {
    try {
        await Listing.findByIdAndDelete(req.params.id);
        res.json({ status: 'success', message: 'İlan silindi.' });
    } catch (error) {
        res.status(500).json({ status: 'error', message: 'Silinemedi.' });
    }
};

export const updateListing = async (req: Request, res: Response) => {
    try {
        // findByIdAndUpdate: ID'yi bul ve gelen veriyle (req.body) değiştir
        // { new: true }: Güncellenmiş veriyi geri döndür demektir
        const updatedListing = await Listing.findByIdAndUpdate(
            req.params.id,
            req.body,
            { new: true, runValidators: true }
        );

        if (!updatedListing) {
            return res.status(404).json({ status: 'error', message: 'İlan bulunamadı.' });
        }

        res.status(200).json({
            status: 'success',
            message: 'İlan bilgileri güncellendi.',
            data: updatedListing
        });
    } catch (error: any) {
        res.status(500).json({ status: 'error', message: 'Güncelleme başarısız.', error: error.message });
    }
};