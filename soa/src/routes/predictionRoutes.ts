import { Router } from 'express';
import { predictPrice } from '../controllers/predictionController';

const router = Router();

router.post('/', predictPrice);

export default router;