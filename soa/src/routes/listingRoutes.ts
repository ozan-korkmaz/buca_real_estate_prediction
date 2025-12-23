import { Router } from 'express';
import { getListings, createListing, getListingById, deleteListing, updateListing, getStreetStats } from '../controllers/listingController';
import { protect} from '../middleware/auth';

const router = Router();

router.get('/', getListings);
router.get('/:id', getListingById);
router.route('/stats/street').get(getStreetStats)

router.post('/', protect, createListing);
router.delete('/:id', protect, deleteListing);
router.put('/:id', protect, updateListing); // YENİ EKLENEN SATIR

export default router;