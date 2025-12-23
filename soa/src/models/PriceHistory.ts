import mongoose, { Schema, Document } from 'mongoose';

export interface IPriceHistory extends Document {
    listing_id: mongoose.Types.ObjectId;
    old_price: number;
    new_price: number;
    change_date: Date;
}

const PriceHistorySchema: Schema = new Schema({
    listing_id: { type: Schema.Types.ObjectId, ref: 'Listing', required: true },
    old_price: { type: Number, required: true },
    new_price: { type: Number, required: true },
    change_date: { type: Date, default: Date.now }
});

export default mongoose.model<IPriceHistory>('PriceHistory', PriceHistorySchema, 'PriceHistory');