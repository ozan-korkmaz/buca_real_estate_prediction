
import { Request, Response } from 'express';
import { PipelineStage } from 'mongoose'; 
import Listing from '../models/Listing';
import { AuthRequest } from '../middleware/auth'; 
import PriceHistory from '../models/PriceHistory';


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
        const newListing = new Listing({
            ...req.body,
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

        // ! ile req.user'ın var olduğunu varsayıyoruz (protect middleware'dan geldi)
        const requesterAgency = req.user!.agency_name; 
        
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

// User Defined Function UDF 
const trackPriceChange = async (listing: any, newPrice?: number) => {
    if (!newPrice) return;

    if (Number(newPrice) !== listing.price) {
        console.log(`UDF: Price change detected ${listing.price} -> ${newPrice}`);

        await PriceHistory.create({
            listing_id: listing._id,
            old_price: listing.price,
            new_price: Number(newPrice),
            change_date: new Date()
        });
    }
};

export const updateListing = async (req: AuthRequest, res: Response) => {
    try {
        const listing = await Listing.findById(req.params.id);

        if (!listing) {
            return res.status(404).json({ status: 'error', message: 'Ilan bulunamadi.' });
        }

        const requesterAgency = req.user!.agency_name;
        const isAgencyMatch = listing.agency_name && listing.agency_name === requesterAgency;
        const isUserMatch = listing.user && String(listing.user) === req.user!.id;

        if (!isAgencyMatch && !isUserMatch) {
            return res.status(403).json({ status: 'error', message: 'Bu ilani duzenleme yetkiniz yok.' });
        }

        // UDF işlemi 
        await trackPriceChange(listing, req.body.price);

        const updatedListing = await Listing.findByIdAndUpdate(
            req.params.id,
            req.body,
            { new: true, runValidators: true }
        );

        res.status(200).json({
            status: 'success',
            message: 'Ilan guncellendi ve price history kaydedildi.',
            data: updatedListing
        });

    } catch (error: any) {
        console.error('DEBUG ERROR (updateListing):', error);
        res.status(500).json({
            status: 'error',
            message: 'Update failed.',
            error: error.message
        });
    }
};


// Sokok bazlı istatistikler fonksiyonu
export const getStreetStats = async (req: Request, res: Response) => {
  try {
    
    const pipeline: PipelineStage[] = [ 
      // 1 Veriyi gruplandır
      {
        $group: {
          _id: '$location_details.street_name', // sokak adına göre grupla
          average_price: {
            $avg: '$price' // ortalama fiyatı hesapla
          },
          count: {
            $sum: 1 
          }
        }
      },
      // 2 Sıralama
      {
        $sort: {
          count: -1, 
          average_price: -1
        }
      },
      // 3 Limit
      {
        $limit: 20 
      }
    ];

    
    interface StreetStatResult {
        _id: string | null;
        average_price: number;
        count: number;
    }

    const streetStats = await Listing.aggregate<StreetStatResult>(pipeline);

    // sokak adi null veya bossa Diğer/Belirtilmemiş olarak varsayıyoruz
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