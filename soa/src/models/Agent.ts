// soa/src/models/Agent.ts
import mongoose, { Schema, Document } from 'mongoose';

export interface IAgent extends Document {
    name: string; // Satıcı (Agent) adı
    phone: string; // Satıcı (Agent) telefon numarası
    // MongoDB'deki diğer Agent alanları buraya eklenebilir
}

const AgentSchema: Schema = new Schema({
    name: { type: String, required: true },
    phone: { type: String, required: true },
    // agency_id'ye gerek yok, çünkü bu model Agent'ın kendisini temsil ediyor ve Listings'ten _id ile çağrılacak.
}, {
    timestamps: true 
});

export const Agent = mongoose.model<IAgent>('Agent', AgentSchema, 'Agencies');