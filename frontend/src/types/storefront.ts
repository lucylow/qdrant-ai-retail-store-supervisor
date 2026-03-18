import { Language } from '../translations';

export interface AIStorefrontRequest {
  query?: string;
  storeId?: string;
  customerPrefs?: {
    language: Language;
    budget?: number;
    pickupTime?: string;
  };
}

export type SectionType = 'hero' | 'products' | 'slots' | 'upsells' | 'reviews' | 'checkout';

export interface AIStorefrontSection {
  type: SectionType;
  title: string;
  subtitle?: string;
  content: any; // Products, slots, etc.
}

export interface AIStorefrontPayload {
  title: string;
  description: string;
  heroImageUrl: string;
  sections: AIStorefrontSection[];
  primaryAction: {
    type: 'add-to-cart' | 'reserve-pickup' | 'twint-checkout';
    text: string;
    payload: any;
  };
}
