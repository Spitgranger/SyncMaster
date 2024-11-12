import { v4 as uuidv4 } from "uuid";
const { createSecretKey } = require('crypto');
import dotenv from "dotenv";
import { Request, Response } from "express";
import haversine from 'haversine-distance';
import * as jose from 'jose';
import { io } from "../index";
export const sessionIds: string[] = [];
export const ITBLocation = {
    latitude: 43.25898815315478,
    longitude: -79.92086378832343
};

dotenv.config();
const secretKey = createSecretKey(process.env.JWT_SECRET, 'utf-8');

/**
 * Route to create session.
 * @name /api/users/create-session
 * @function
 */
export const createSession = async (req: Request, res: Response) => {
    const uuid: string = uuidv4();
    console.log(uuid);
    sessionIds.push(uuid);
    res.status(200).json({ uuid });
}

/**
 * Route to verify a users location
 * @name /api/users/verify-location
 * @function
 */
export const verifyLocation = async (req: Request, res: Response) => {
    const uuid: string = req.body.userId;
    try {
        if (!sessionIds.includes(uuid)) {
            res.status(401).json({ message: "User does not exist" });
            return;
        }

        console.log(
            "User [%s] exists at [%d] longitude and [%d] latitude",
            uuid,
            req.body.longitude,
            req.body.latitude
        );
        const userLocation = {
            latitude: req.body.latitude,
            longitude: req.body.longitude
        };

        const distance: number = haversine(userLocation, ITBLocation)

        console.log("User [%s], is [%d] meters from the site", uuid, distance)

        if (distance > 10) {
            console.log(
                "User [%s], is too far from the site, failed to authenticate",
                uuid
            );
            res.status(401).json({ message: "User is not on a registered site" });
            return;
        }
        const token = await new jose.SignJWT(userLocation)
            .setProtectedHeader({ alg: "HS256" })
            .setSubject(uuid)
            .setIssuedAt()
            .setExpirationTime("1h")
            .sign(secretKey);
        io.to(uuid).emit("authSuccess", token);
        res.status(200).json({ token: token });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: "Internal Server Error" });
    }
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
    res.status(200).json({ message: "Connection established" });
}