import {Request, Response} from "express";

/**
 * Route to serve dummy data location GET request
 * @name /api/dashboard/
 * @function
 */
export const getDashboardData = async (req: Request, res: Response) => {
    res.status(200).json({
        stationNumber: 5,
        workOrderNumber: "WO2192741",
        entryExit: "None Specialized",
    });
}
