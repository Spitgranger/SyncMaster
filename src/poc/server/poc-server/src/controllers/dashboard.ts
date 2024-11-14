import {Request, Response} from "express";
import {v4 as uuidv4} from "uuid";
import {sessionIds} from "./users";

export const getDashboardData = async (req: Request, res: Response) => {
    res.status(200).json({
        stationNumber: 5,
        workOrderNumber: "WO2192741",
        entryExit: "None Specialized",
    });
}
