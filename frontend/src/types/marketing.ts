export type CampaignType = 'social' | 'banner' | 'video' | 'print' | 'email';
export type Language = 'de' | 'fr' | 'it';

export interface MarketingRequest {
  campaignType: CampaignType;
  products: string[];      // Array of SKUs
  storeId?: string;
  theme?: string;          // "Christmas", "Fondue", "Summer BBQ"
  language: Language;
  format?: string;         // "instagram-square", "youtube-16x9"
}

export interface MarketingAsset {
  id: string;
  type: 'image' | 'video' | 'html' | 'email';
  url: string;             // CDN/S3 URL
  width: number;
  height: number;
  format: string;          // "png", "mp4", "html"
  previewUrl: string;      // Lower-res preview
  analytics: {
    predictedCTR: number;    // e.g., 2.3
    estimatedReach: number;  // e.g., 12450
  };
}

export interface MarketingResponse {
  campaignId: string;
  assets: MarketingAsset[];
  copy: {
    headline: string;
    subheadline: string;
    cta: string;
    hashtags: string[];
  };
  analytics: {
    predictedCTR: number;
    estimatedReach: number;
  };
}

export interface MarketingTemplate {
  id: string;
  name: string;
  theme: string;
  previewUrl: string;
  description: string;
}
