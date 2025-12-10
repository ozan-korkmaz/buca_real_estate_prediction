import express from 'express';
import { getListingComments, createComment } from '../controllers/commentController';

const router = express.Router();

// Yorumları Getir
router.get('/', getListingComments); 

// YENİ EKLENEN: Yorum Kaydet
router.post('/', createComment);

export default router;