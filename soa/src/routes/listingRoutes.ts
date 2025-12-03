import { Router } from 'express';
// updateListing'i import listesine eklemeyi unutma!
import { getListings, createListing, getListingById, deleteListing, updateListing } from '../controllers/listingController';
import { protect } from '../middleware/auth';

const router = Router();

router.get('/', getListings);
router.get('/:id', getListingById);

// Korumalı Rotalar
router.post('/', protect, createListing);
router.delete('/:id', protect, deleteListing);
router.put('/:id', protect, updateListing); // YENİ EKLENEN SATIR

export default router;