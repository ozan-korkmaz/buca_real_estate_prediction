import express from 'express';
import { protect } from "../middleware/auth";
import { getMe, updateMe, getUserById } from "../controllers/userController";

const router = express.Router();
router.get("/me", protect, getMe);
router.patch("/me", protect, updateMe);
router.get("/:id", getUserById);


export default router;
