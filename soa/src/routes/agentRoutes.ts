// soa/src/routes/agentRoutes.ts
import express from 'express';
import { getAgentById } from '../controllers/agentController';

const router = express.Router();

// Yeni Agent API endpoint'i: GET /api/agents/:id
router.get('/:id', getAgentById);

export default router;