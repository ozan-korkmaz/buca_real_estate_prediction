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
            user: req.user.id, // Token'dan gelen user id
            agency_name: (req.user as any).agency_name || "Bireysel"
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

export const deleteListing = async (req: AuthRequest, res: Response) => {
    try {
        const listing = await Listing.findById(req.params.id);
        
        if (!listing) {
            return res.status(404).json({ status: 'error', message: 'İlan bulunamadı.' });
        }

        // KONTROL: İlanın ofis adı ile silmek isteyenin ofis adı aynı mı?
        const requesterAgency = (req.user as any).agency_name;
        
        // Eğer ajans adı varsa ve eşleşiyorsa VEYA bireysel kullanıcı kendi ilanını siliyorsa
        const isAgencyMatch = listing.agency_name && listing.agency_name === requesterAgency;
        const isUserMatch = listing.user && String(listing.user) === req.user.id;

        if (isAgencyMatch || isUserMatch) {
            await Listing.findByIdAndDelete(req.params.id);
            res.json({ status: 'success', message: 'İlan silindi.' });
        } else {
            return res.status(403).json({ status: 'error', message: 'Bu ilanı silme yetkiniz yok (Farklı Ofis).' });
        }

    } catch (error) {
        res.status(500).json({ status: 'error', message: 'Silinemedi.', error });
    }
};

// --- UPDATE (GÜNCELLENDİ - OFİS KONTROLÜ) ---
export const updateListing = async (req: AuthRequest, res: Response) => {
    try {
        const listing = await Listing.findById(req.params.id);

        if (!listing) {
            return res.status(404).json({ status: 'error', message: 'İlan bulunamadı.' });
        }

        // KONTROL (Delete ile aynı mantık)
        const requesterAgency = (req.user as any).agency_name;
        const isAgencyMatch = listing.agency_name && listing.agency_name === requesterAgency;
        const isUserMatch = listing.user && String(listing.user) === req.user.id;

        if (!isAgencyMatch && !isUserMatch) {
            return res.status(403).json({ status: 'error', message: 'Bu ilanı düzenleme yetkiniz yok.' });
        }

        const updatedListing = await Listing.findByIdAndUpdate(
            req.params.id,
            req.body,
            { new: true, runValidators: true }
        );

        res.status(200).json({
            status: 'success',
            message: 'İlan güncellendi.',
            data: updatedListing
        });

    } catch (error: any) {
        res.status(500).json({ status: 'error', message: 'Güncelleme başarısız.', error: error.message });
    }
};