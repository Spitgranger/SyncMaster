import {v4 as uuidv4} from "uuid";
import { Request, Response } from "express";

export const createSession = async (req: Request, res: Response) => {
    const uuid: string | Uint8Array  = uuidv4();
    console.log(uuid);
    //req.session.chatId = uuid;
    res.status(200).json({uuid});
}