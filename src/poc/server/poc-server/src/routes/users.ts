import express from 'express';
import { createSession, emitConnection, verifyLocation } from '../controllers/users';

const router = express.Router();

// Route to create a session. It is GET for now as any user can create a seesion
router.get("/create-session", createSession);
router.post("/emit-connection", emitConnection);
router.post("/verify-location", verifyLocation);
export default router;
