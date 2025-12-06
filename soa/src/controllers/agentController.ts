// soa/src/controllers/agentController.ts
import { Request, Response } from 'express';
import  Agent  from '../models/Agent'; 
import mongoose from 'mongoose';

export const getAgentById = async (req: Request, res: Response): Promise<void> => {
    try {
        const agentId = req.params.id;

        if (!mongoose.Types.ObjectId.isValid(agentId)) {
            res.status(400).json({ status: 'error', message: 'Geçersiz Agent ID formatı' });
            return;
        }

        // Listings'ten gelen agency_id'yi Agent koleksiyonundaki _id ile buluyoruz
        const agent = await Agent.findById(agentId);

        if (!agent) {
            res.status(404).json({ status: 'error', message: 'Agent bulunamadı' });
            return;
        }

        // Başarılı yanıt: Agent verisini döndür
        res.status(200).json({ status: 'success', data: agent });

    } catch (error) {
        console.error('Agent çekme hatası:', error);
        // TSError hatasını çözen güvenli erişim:
        const errorMessage = error instanceof Error ? error.message : 'Bilinmeyen bir hata oluştu';
        res.status(500).json({ status: 'error', message: 'Sunucu hatası', error: errorMessage });
    }
};