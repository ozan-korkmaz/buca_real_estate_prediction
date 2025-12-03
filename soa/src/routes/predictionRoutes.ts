import { Router } from 'express';
import { predictPrice } from '../controllers/predictionController';
// import { protect } from '../middleware/auth'; // Eğer sadece üyeler tahmin yapsın istersen bunu aç

const router = Router();

// URL: /api/predict
router.post('/', predictPrice);

export default router;