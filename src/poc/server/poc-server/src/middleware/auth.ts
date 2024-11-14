import {Request, Response, NextFunction} from "express";
import {jwtVerify} from "jose";
import {createSecretKey} from "node:crypto";

const auth = async (req: Request, res: Response, next: NextFunction) => {
    try {
        const token = req?.headers?.authorization?.split(" ")[1];
        if (token !== undefined) {
            let decodedData;
            decodedData = await jwtVerify(token, createSecretKey(process.env.JWT_SECRET || "1234567891011121314151617181920212223242526272829303132"));
            console.log(decodedData);
            next();
        } else {
            res.status(500).json("Error when parsing access token");
            return
        }
    } catch (error) {
        console.log(error);
        res.status(403).json("must be logged in and/or invalid token");
        return
    }
}