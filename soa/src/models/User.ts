import mongoose, { Schema, Document } from 'mongoose';

export interface IUser extends Document {
    name: string;
    email: string;
    password: string;
    phone?: string;
    role: 'user';
    createdAt: Date;
    updatedAt: Date;
}

const UserSchema = new Schema<IUser>(
    {
        name: { type: String, required: true },
        email: { type: String, required: true, unique: true },
        password: { type: String, required: true },
        phone: { type: String, required: true },
        role: { type: String, default: 'user' }
    },
    { timestamps: true }
);

UserSchema.set('toJSON', {
    transform(_doc, ret) {
        delete ret.password;
        return ret;
    }
});

export default mongoose.model<IUser>('User', UserSchema, 'Users');
