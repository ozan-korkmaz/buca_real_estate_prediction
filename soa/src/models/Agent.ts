import mongoose, { Schema, Document } from 'mongoose';

export interface IAgent extends Document {
    full_name: string;
    agency_name: string;
    title: string;
    address: string;
    email: string;
    phone: string;
    password: string;
    role: 'agent';
    createdAt: Date;
    updatedAt: Date;
}

const AgentSchema = new Schema<IAgent>(
    {
        full_name: { type: String, required: true },
        agency_name: { type: String, required: true },
        title: { type: String, required: true },
        address: { type: String, required: true },
        email: { type: String, required: true, unique: true },
        phone: { type: String, required: true },
        password: { type: String, required: true },
        role: { type: String, default: 'agent' }
    },
    { timestamps: true }
);

AgentSchema.set('toJSON', {
    transform(_doc, ret) {
        delete ret.password;
        return ret;
    }
});

export default mongoose.model<IAgent>('Agent', AgentSchema, 'Agents');
