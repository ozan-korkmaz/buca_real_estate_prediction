// soa/src/controllers/listingController.ts

import { Request, Response } from 'express';
// Gerekli tipleri mongoose'tan import ediyoruz
import { PipelineStage } from 'mongoose'; 
import Listing from '../models/Listing';
// auth.ts'den genişlettiğimiz AuthRequest tipini import ediyoruz
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
        // req.user.id artık type-safe olmalı (auth.ts'de IUserDocument ile tanımlandı)
        const newListing = new Listing({
            ...req.body,
            // req.user varlığını ve içindeki id alanını biliyoruz
            user: req.user!.id, 
            agency_name: req.user!.agency_name || "Bireysel"
        });

        await newListing.save();

        res.status(201).json({
            status: 'success',
            message: 'İlan oluşturuldu.',
            data: { id: newListing._id }
        });
    } catch (error) {
        console.error('DEBUG HATA (createListing):', error);
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

        const requesterAgency = req.user!.agency_name; // ! ile req.user'ın var olduğunu varsayıyoruz (protect middleware'dan geldi)
        
        const isAgencyMatch = listing.agency_name && listing.agency_name === requesterAgency;
        const isUserMatch = listing.user && String(listing.user) === req.user!.id;

        if (isAgencyMatch || isUserMatch) {
            await Listing.findByIdAndDelete(req.params.id);
            res.json({ status: 'success', message: 'İlan silindi.' });
        } else {
            return res.status(403).json({ status: 'error', message: 'Bu ilanı silme yetkiniz yok (Farklı Ofis).' });
        }

    } catch (error) {
        console.error('DEBUG HATA (deleteListing):', error);
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

        const requesterAgency = req.user!.agency_name;
        const isAgencyMatch = listing.agency_name && listing.agency_name === requesterAgency;
        const isUserMatch = listing.user && String(listing.user) === req.user!.id;

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
        console.error('DEBUG HATA (updateListing):', error);
        res.status(500).json({ status: 'error', message: 'Güncelleme başarısız.', error: error.message });
    }
};


// YENİ FONKSİYON: Sokak Bazında İstatistikleri Getirir
export const getStreetStats = async (req: Request, res: Response) => {
  try {
    
    const pipeline: PipelineStage[] = [ // ✅ PipelineStage importu ile hata çözüldü
      // 1. Aşama: Veriyi gruplandır
      {
        $group: {
          _id: '$location_details.street_name', // Sokak adına göre grupla
          average_price: {
            $avg: '$price' // Ortalama fiyatı hesapla
          },
          count: {
            $sum: 1 
          }
        }
      },
      // 2. Aşama: Sıralama
      {
        $sort: {
          count: -1, 
          average_price: -1
        }
      },
      // 3. Aşama: Limit
      {
        $limit: 20 
      }
    ];

    // streetStats tipini de güvenli hale getirebiliriz:
    interface StreetStatResult {
        _id: string | null;
        average_price: number;
        count: number;
    }

    const streetStats = await Listing.aggregate<StreetStatResult>(pipeline);

    // Eğer sokak adı null veya boşsa, bunu "Diğer/Belirtilmemiş" olarak düzeltelim
    const formattedStats = streetStats.map(stat => ({
      street: stat._id || 'Diğer/Belirtilmemiş',
      averagePrice: Math.round(stat.average_price), 
      count: stat.count,
    }));

    res.status(200).json(formattedStats);
  } catch (error) {
    console.error('DEBUG HATA (getStreetStats): Sokak istatistikleri alınırken hata oluştu:', error);
    res.status(500).json({ message: 'Sokak istatistikleri alınamadı', error });
  }
};