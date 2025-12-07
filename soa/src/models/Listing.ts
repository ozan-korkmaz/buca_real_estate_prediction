import mongoose, { Schema, Document } from 'mongoose';

export interface IListing extends Document {
    title: string;
    description: string;
    price: number;
    currency: string;
    status: string;
    tags: string[];
    property_specs: {
        gross_m2: number;
        net_m2: number;
        room_count: string;
        floor: number;
        heating: string;
        building_age: number;
    };
    location_details: {
        street_name: string;
        site_name?: string;
        coordinates?: {
            lat: number;
            lon: number;
        };
    };
    agency_id?: string;
    neighborhood_id?: string;
    created_at?: Date;
    agency_name?: string;
    user?: mongoose.Types.ObjectId | string;
}

const ListingSchema: Schema = new Schema(
    {
        title: { type: String, required: true },
        description: { type: String },
        price: { type: Number, required: true },
        currency: { type: String, default: 'TRY' },
        status: { type: String, default: 'active' },
        tags: [{ type: String }],

        // Özellikler (property_specs)
        property_specs: {
            gross_m2: { type: Number },
            net_m2: { type: Number },
            room_count: { type: String },
            floor: { type: Number },
            heating: { type: String },
            building_age: { type: Number, required: true }
        },

        // Konum
        location_details: {
            street_name: { type: String },
            site_name: { type: String },
            coordinates: {
                lat: { type: Number },
                lon: { type: Number }
            }
        },

        agency_id: { type: String },
        agency_name: { type: String },
        neighborhood_id: { type: String },
        user: { type: mongoose.Schema.Types.ObjectId, ref: 'User' }
    },
    { timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' } }
);

ListingSchema.set('toJSON', {
    virtuals: true,
    versionKey: false,
    transform: function (doc, ret) { delete ret._id; }
});

export default mongoose.model<IListing>('Listing', ListingSchema, 'Listings');