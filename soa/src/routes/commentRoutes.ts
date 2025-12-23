import express from 'express';
import { getListingComments, createComment } from '../controllers/commentController';

const router = express.Router();

router.get('/', getListingComments); 
router.post('/', createComment);

export default router;