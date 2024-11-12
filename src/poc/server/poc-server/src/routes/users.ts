import express from 'express';
import { createSession } from '../controllers/users';

const router = express.Router();

// Route to create a session. It is get for now as any user can create a seesion
router.get("/create-session", createSession);
export default router;