import { Request, Response } from 'express';
import jwt from 'jsonwebtoken';
import User from '../models/User';
import Agent from '../models/Agent';

const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret';

// ---------- REGISTER ----------
export const register = async (req: Request, res: Response) => {
    try {
        const {
            first_name,
            last_name,
            email,
            password,
            phone,
            account_type,
            agency_name,
            title,
            address
        } = req.body;

        if (!first_name || !last_name || !email || !password || !account_type) {
            return res.status(400).json({
                status: 'error',
                message: 'Zorunlu alanlar eksik.'
            });
        }

        const fullName = `${first_name} ${last_name}`.trim();

        // 🟢 BİREYSEL → Users
        if (account_type === 'individual') {
            const existingUser = await User.findOne({ email });
            if (existingUser) {
                return res.status(400).json({
                    status: 'error',
                    message: 'Bu email ile bireysel kullanıcı zaten kayıtlı.'
                });
            }

            await User.create({
                name: fullName,
                email,
                password,
                phone,
                role: 'user'
            });

            return res.status(201).json({
                status: 'success',
                message: 'Bireysel kullanıcı başarıyla oluşturuldu.'
            });
        }

        // 🟠 TİCARİ → Agents
        if (account_type === 'commercial') {
            if (!agency_name || !title || !address || !phone) {
                return res.status(400).json({
                    status: 'error',
                    message: 'Ticari hesap için ofis adı, unvan, adres ve telefon zorunludur.'
                });
            }

            const existingAgent = await Agent.findOne({ email });
            if (existingAgent) {
                return res.status(400).json({
                    status: 'error',
                    message: 'Bu email ile ticari kullanıcı zaten kayıtlı.'
                });
            }

            await Agent.create({
                full_name: fullName,
                agency_name,
                title,
                address,
                email,
                phone,
                password,
                role: 'agent'
            });

            return res.status(201).json({
                status: 'success',
                message: 'Ticari kullanıcı başarıyla oluşturuldu.'
            });
        }

        return res.status(400).json({
            status: 'error',
            message: 'Geçersiz hesap tipi.'
        });
    } catch (err: any) {
        console.error('REGISTER ERROR:', err);
        return res.status(500).json({
            status: 'error',
            message: 'Sunucu hatası.'
        });
    }
};

// ---------- LOGIN ----------
export const login = async (req: Request, res: Response) => {
    try {
        const { email, password, account_type } = req.body;

        console.log('LOGIN BODY:', req.body);

        if (!email || !password || !account_type) {
            return res.status(400).json({
                status: 'error',
                message: 'Email, şifre ve hesap tipi zorunludur.'
            });
        }

        // ---------------- BİREYSEL GİRİŞ (Users) ----------------
        if (account_type === 'individual') {
            // email + password ile direkt sorgu
            const user = await User.findOne({ email, password });

            if (!user) {
                return res.status(404).json({
                    status: 'error',
                    message: 'Bireysel kullanıcı bulunamadı veya şifre hatalı.'
                });
            }

            const token = jwt.sign(
                { sub: String(user._id), role: 'user', type: 'user' },
                JWT_SECRET,
                { expiresIn: '1d' }
            );

            return res.status(200).json({
                status: 'success',
                data: {
                    access_token: token,
                    token_type: 'bearer',
                    role: 'user',
                    user_name: user.name
                }
            });
        }

        // ---------------- TİCARİ GİRİŞ (Agents) ----------------
        if (account_type === 'commercial') {
            const agent = await Agent.findOne({ email, password });

            if (!agent) {
                return res.status(404).json({
                    status: 'error',
                    message: 'Ticari kullanıcı bulunamadı veya şifre hatalı.'
                });
            }

            const token = jwt.sign(
                { sub: String(agent._id), role: 'agent', type: 'agent' },
                JWT_SECRET,
                { expiresIn: '1d' }
            );

            return res.status(200).json({
                status: 'success',
                data: {
                    access_token: token,
                    token_type: 'bearer',
                    role: 'agent',
                    user_name: agent.full_name
                }
            });
        }

        return res.status(400).json({
            status: 'error',
            message: 'Geçersiz hesap tipi.'
        });
    } catch (err: any) {
        console.error('LOGIN ERROR:', err);
        return res.status(500).json({
            status: 'error',
            message: 'Sunucu hatası.'
        });
    }
};
