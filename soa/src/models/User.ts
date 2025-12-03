import mongoose, { Schema, Document } from 'mongoose';

export interface IUser extends Document {
    name: string;       // first_name, last_name yerine tek bir name
    email: string;
    password: string;
    phone?: string;     // Veritabanında var
    role?: string;      // Veritabanında var
}

const UserSchema: Schema = new Schema(
    {
        name: { type: String, required: true },
        email: { type: String, required: true, unique: true },
        password: { type: String, required: true },
        phone: { type: String, required: false },
        role: { type: String, default: 'user' }
    },
    { timestamps: true }
);

// 'Users' koleksiyonunu kullanmaya devam ediyoruz
export default mongoose.model<IUser>('User', UserSchema, 'Users');