import express from 'express';
import { getListingComments } from '../controllers/commentController';

const router = express.Router();
router.get('/', getListingComments); // Route: GET /api/comments?listing_id=...
export default router;

