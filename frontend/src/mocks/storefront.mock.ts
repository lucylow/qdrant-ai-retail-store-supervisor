import { AIStorefrontPayload } from '../types/storefront';

export const MOCK_STOREFRONTS: Record<string, AIStorefrontPayload> = {
  'default': {
    title: 'Migros Online Storefront',
    description: 'Ihr personalisiertes Einkaufserlebnis bei der Migros.',
    heroImageUrl: 'https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&q=80&w=1200&h=400',
    sections: [
      {
        type: 'hero',
        title: 'Willkommen bei Migros',
        subtitle: 'Entdecken Sie unsere frischen Produkte und regionalen Spezialitäten.',
        content: {
          imageUrl: 'https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&q=80&w=800&h=400',
          ctaText: 'Jetzt einkaufen'
        }
      },
      {
        type: 'products',
        title: 'Beliebte Produkte',
        content: [
          { sku: '12345678', name: 'Migros Bio-Milch 1L', priceChf: 2.95, stock: 42, category: 'dairy', holidayMultiplier: 1.0, imageUrl: 'https://images.unsplash.com/photo-1563636619-e9107da5a163?auto=format&fit=crop&q=80&w=400&h=400', score: 0.98, vectorId: 'point-101' },
          { sku: '23456789', name: 'Raclette Käse 500g', priceChf: 8.95, stock: 15, category: 'cheese', holidayMultiplier: 1.5, safetyStock: 20, imageUrl: 'https://images.unsplash.com/photo-1485962391945-448fa2144d70?auto=format&fit=crop&q=80&w=400&h=400', score: 0.92, vectorId: 'point-102' },
          { sku: '34567890', name: 'Lindt Excellence 70% Kakao', priceChf: 4.50, stock: 85, category: 'chocolate', holidayMultiplier: 1.2, imageUrl: 'https://images.unsplash.com/photo-1511381939415-e44015466834?auto=format&fit=crop&q=80&w=400&h=400', score: 0.85, vectorId: 'point-103' }
        ]
      }
    ],
    primaryAction: {
      type: 'add-to-cart',
      text: 'In den Warenkorb',
      payload: {}
    }
  },
  'Bio-Milch morgen 10h': {
    title: 'Ihre Bio-Milch für morgen 10h',
    description: 'Personalisierte Auswahl für Ihren Einkauf im Migros Zürich HB.',
    heroImageUrl: 'https://images.unsplash.com/photo-1550583760-d80305277440?auto=format&fit=crop&q=80&w=1200&h=400',
    sections: [
      {
        type: 'hero',
        title: 'Perfekt für morgen!',
        subtitle: 'Wir haben Ihre Bio-Milch und passende Ergänzungen reserviert.',
        content: {
          imageUrl: 'https://images.unsplash.com/photo-1550583760-d80305277440?auto=format&fit=crop&q=80&w=800&h=400',
          ctaText: 'Alles in den Warenkorb'
        }
      },
      {
        type: 'products',
        title: 'Empfohlene Produkte',
        content: [
          { sku: '12345678', name: 'Migros Bio-Milch 1L', priceChf: 2.95, stock: 42, category: 'dairy', holidayMultiplier: 1.0, imageUrl: 'https://images.unsplash.com/photo-1563636619-e9107da5a163?auto=format&fit=crop&q=80&w=400&h=400' },
          { sku: '90123456', name: 'Migros Bio Eier 6er', priceChf: 4.20, stock: 24, category: 'organic', imageUrl: 'https://images.unsplash.com/photo-1582722872445-44dc5f7e3cba?auto=format&fit=crop&q=80&w=400&h=400' }
        ]
      },
      {
        type: 'slots',
        title: 'Abholzeiten Zürich HB',
        subtitle: 'Nur noch 3 Plätze frei für morgen Vormittag!',
        content: [
          { id: 'W-10', start: '2026-03-19T10:00:00Z', end: '2026-03-19T11:00:00Z', capacity: 10, booked: 7, isRecommended: true },
          { id: 'W-11', start: '2026-03-19T11:00:00Z', end: '2026-03-19T12:00:00Z', capacity: 10, booked: 9 }
        ]
      },
      {
        type: 'upsells',
        title: 'Dazu passt auch...',
        content: [
          { sku: '01234567', name: 'M-Budget Pasta 500g', priceChf: 0.95, stock: 200, category: 'm_budget', imageUrl: 'https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&q=80&w=400&h=400' }
        ]
      },
      {
        type: 'reviews',
        title: 'Das sagen unsere Kunden',
        content: [
          { user: 'Lukas M.', rating: 5, comment: 'Die Bio-Milch ist immer frisch und lecker!' },
          { user: 'Sarah K.', rating: 4, comment: 'Super Service am HB Zürich.' }
        ]
      },
      {
        type: 'checkout',
        title: 'Schnell bezahlen mit TWINT',
        subtitle: '58% schneller als mit Karte',
        content: {
          totalChf: 7.15,
          qrCodeUrl: 'https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=TWINT_PAYMENT_MIGROS_7.15'
        }
      }
    ],
    primaryAction: {
      type: 'twint-checkout',
      text: 'Jetzt mit TWINT bezahlen',
      payload: { amount: 7.15 }
    }
  },
  'Abendessen für 4': {
    title: 'Abendessen für 4 Personen',
    description: 'Ein komplettes Menü für einen gemütlichen Abend.',
    heroImageUrl: 'https://images.unsplash.com/photo-1517093157656-b9424f461507?auto=format&fit=crop&q=80&w=1200&h=400',
    sections: [
      {
        type: 'hero',
        title: 'Gemütliches Abendessen',
        subtitle: 'Wir haben alles für Ihre Pizza-Nacht zusammengestellt.',
        content: {
          imageUrl: 'https://images.unsplash.com/photo-1517093157656-b9424f461507?auto=format&fit=crop&q=80&w=800&h=400',
          ctaText: 'Menü in den Warenkorb'
        }
      },
      {
        type: 'products',
        title: 'Hauptgang & Beilagen',
        content: [
          { sku: '45678901', name: 'M-Budget Pizza Margherita 400g', priceChf: 3.95, stock: 12, category: 'frozen', imageUrl: 'https://images.unsplash.com/photo-1574071318508-1cdbad80ad38?auto=format&fit=crop&q=80&w=400&h=400' },
          { sku: '56789012', name: 'Migros Mountain Water 1.5L', priceChf: 1.20, stock: 120, category: 'beverages', imageUrl: 'https://images.unsplash.com/photo-1523362628744-0c100150b504?auto=format&fit=crop&q=80&w=400&h=400' },
          { sku: '90123456', name: 'Gemischter Salat 250g', priceChf: 4.50, stock: 30, category: 'fresh', imageUrl: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&q=80&w=400&h=400' }
        ]
      },
      {
        type: 'upsells',
        title: 'Dessert & Wein',
        content: [
          { sku: '34567890', name: 'Lindt Excellence 70% Kakao', priceChf: 4.50, stock: 85, category: 'chocolate', imageUrl: 'https://images.unsplash.com/photo-1511381939415-e44015466834?auto=format&fit=crop&q=80&w=400&h=400' },
          { sku: '67890123', name: 'Appenzeller Alpenbitter', priceChf: 29.90, stock: 12, category: 'spirits', imageUrl: 'https://images.unsplash.com/photo-1569529465841-dfecdab7503b?auto=format&fit=crop&q=80&w=400&h=400' }
        ]
      },
      {
        type: 'checkout',
        title: 'Gesamtbetrag',
        subtitle: 'Inklusive aller Rabatte',
        content: {
          totalChf: 48.50,
          qrCodeUrl: 'https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=TWINT_PAYMENT_MIGROS_48.50'
        }
      }
    ],
    primaryAction: {
      type: 'twint-checkout',
      text: 'CHF 48.50 mit TWINT bezahlen',
      payload: { amount: 48.50 }
    }
  }
};
