import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import User from "../models/User";

// Request tipini genişletiyoruz
export interface AuthRequest extends Request {
    user?: any;
}


export const protect = async (req: AuthRequest, res: Response, next: NextFunction) => {
    let token;

    if (req.headers.authorization && req.headers.authorization.startsWith("Bearer")) {
        try {
            token = req.headers.authorization.split(" ")[1];

            const decoded = jwt.verify(
                token,
                process.env.JWT_SECRET as string
            ) as { sub: string };

            const user = await User.findById(decoded.sub)
                .select("name surname email role phone");

            if (!user) {
                return res.status(401).json({ message: "User bulunamadi" });
            }

            req.user = user;
            next();
        } catch (error) {
            return res.status(401).json({ message: "Gecersiz token" });
        }
    }

    if (!token) {
        return res.status(401).json({ message: "Token yok" });
    }
};
