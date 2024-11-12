import {v4 as uuidv4} from "uuid";
import { Request, Response } from "express";
import { io } from "../index";
export const sessionIds: string[] = [];

/**
 * Route to create session.
 * @name /api/users/create-session
 * @function
 */
export const createSession = async (req: Request, res: Response) => {
    const uuid: string = uuidv4();
    console.log(uuid);
    sessionIds.push(uuid);
    res.status(200).json({uuid});
}

/**
 * Route to test emitting event to a specific connection. Given a uuid, it emits an event to that connection.
 * POST request. Body should contain the uuid.
 * @name /api/users/emit-connection
 * @function
 */
export const emitConnection = async (req: Request, res: Response) => {
    const { uuid } = req.body;
    io.to(uuid).emit("event");
    res.status(200).json({message: "Connection established"});
}