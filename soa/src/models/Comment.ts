import mongoose, { Schema, Document } from 'mongoose';

export interface IComment extends Document {
    listing_id: mongoose.Types.ObjectId;
    user_id: mongoose.Types.ObjectId;
    text: string; 
    rating: number; 
    created_at: Date;
}

const CommentSchema: Schema = new Schema({
    listing_id: { type: Schema.Types.ObjectId, ref: 'Listing', required: true },
    user_id: { type: Schema.Types.ObjectId, ref: 'User', required: true },
    text: { type: String, required: true },
    rating: { type: Number, required: true, min: 1, max: 5 },
    created_at: { type: Date, default: Date.now },
});

export const Comment = mongoose.model<IComment>('Comment', CommentSchema, 'Comments'); 
