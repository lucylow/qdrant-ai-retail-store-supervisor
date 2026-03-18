import { MarketingResponse, MarketingTemplate } from '../types/marketing';

export const MOCK_MARKETING_TEMPLATES: MarketingTemplate[] = [
  { id: 't-1', name: 'Migros Christmas Classic', theme: 'Christmas', previewUrl: 'https://images.unsplash.com/photo-1544273677-c433136021d4?auto=format&fit=crop&q=80&w=400&h=400', description: 'Traditional Swiss Christmas aesthetic with dairy focus.' },
  { id: 't-2', name: 'Fondue Season 2026', theme: 'Fondue', previewUrl: 'https://images.unsplash.com/photo-1553621042-f6e147245754?auto=format&fit=crop&q=80&w=400&h=400', description: 'Cozy winter vibes for cheese lovers.' },
  { id: 't-3', name: 'M-Budget Summer BBQ', theme: 'Summer BBQ', previewUrl: 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&q=80&w=400&h=400', description: 'High-energy, budget-friendly summer campaign.' },
  { id: 't-4', name: 'Bio-Milch Freshness', theme: 'Organic', previewUrl: 'https://images.unsplash.com/photo-1550583760-d80305277440?auto=format&fit=crop&q=80&w=400&h=400', description: 'Clean, minimalist design highlighting organic quality.' },
];

export const MOCK_CAMPAIGN_RESPONSE: MarketingResponse = {
  campaignId: 'camp-12345',
  assets: [
    { 
      id: 'a-1', 
      type: 'image', 
      url: 'https://images.unsplash.com/photo-1544273677-c433136021d4?auto=format&fit=crop&q=80&w=1080&h=1080', 
      width: 1080, 
      height: 1080, 
      format: 'png', 
      previewUrl: 'https://images.unsplash.com/photo-1544273677-c433136021d4?auto=format&fit=crop&q=80&w=400&h=400',
      analytics: { predictedCTR: 3.2, estimatedReach: 12450 }
    },
    { 
      id: 'a-2', 
      type: 'video', 
      url: 'https://assets.mixkit.co/videos/preview/mixkit-pouring-milk-into-a-glass-34433-large.mp4', 
      width: 1080, 
      height: 1920, 
      format: 'mp4', 
      previewUrl: 'https://images.unsplash.com/photo-1550583760-d80305277440?auto=format&fit=crop&q=80&w=400&h=711',
      analytics: { predictedCTR: 8.1, estimatedReach: 45000 }
    },
    { 
      id: 'a-3', 
      type: 'image', 
      url: 'https://images.unsplash.com/photo-1544273677-c433136021d4?auto=format&fit=crop&q=80&w=300&h=250', 
      width: 300, 
      height: 250, 
      format: 'png', 
      previewUrl: 'https://images.unsplash.com/photo-1544273677-c433136021d4?auto=format&fit=crop&q=80&w=300&h=250',
      analytics: { predictedCTR: 2.7, estimatedReach: 8500 }
    },
  ],
  copy: {
    headline: 'Bio-Milch für Weihnachten!',
    subheadline: 'Jetzt reservieren und morgen abholen im Migros Zürich HB.',
    cta: 'Jetzt reservieren',
    hashtags: ['#Migros', '#BioMilch', '#Weihnachten', '#ZürichHB']
  },
  analytics: {
    predictedCTR: 4.6,
    estimatedReach: 65950
  }
};
