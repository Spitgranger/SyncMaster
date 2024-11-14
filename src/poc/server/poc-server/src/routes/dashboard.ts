import express from 'express';
import {getDashboardData} from "../controllers/dashboard";
import auth from "../middleware/auth";

const router = express.Router();

router.get("/", auth, getDashboardData);

export default router;
