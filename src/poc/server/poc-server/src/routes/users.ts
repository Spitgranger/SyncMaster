import express from 'express';
import {createSession, emitConnection} from '../controllers/users';

const router = express.Router();

// Route to create a session. It is GET for now as any user can create a seesion
router.get("/create-session", createSession);
router.post("/emit-connection", emitConnection);
export default router;