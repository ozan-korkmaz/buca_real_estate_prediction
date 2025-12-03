import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

// Request tipini genişletiyoruz
export interface AuthRequest extends Request {
    user?: any;
}

export const protect = (req: AuthRequest, res: Response, next: NextFunction) => {
    let token;

    if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
        try {
            token = req.headers.authorization.split(' ')[1];
            const decoded = jwt.verify(token, process.env.JWT_SECRET as string);
            req.user = decoded;
            next();
        } catch (error) {
            return res.status(401).json({ status: 'error', message: 'Geçersiz token.' });
        }
    }

    if (!token) {
        return res.status(401).json({ status: 'error', message: 'Yetkisiz erişim, token yok.' });
    }
};