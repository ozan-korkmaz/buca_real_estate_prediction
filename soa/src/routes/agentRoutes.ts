import express from 'express';
import { getAgentById } from '../controllers/agentController';

const router = express.Router();

router.get('/:id', getAgentById);

export default router;