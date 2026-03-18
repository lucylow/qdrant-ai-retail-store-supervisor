import { 
  QueryRequest, 
  QueryResponse, 
  Product, 
  PickupWindow, 
  Metrics, 
  ComplianceScore, 
  Order 
} from '../types/retail';
import { AIStorefrontRequest, AIStorefrontPayload } from '../types/storefront';
import { MarketingRequest, MarketingResponse, MarketingTemplate } from '../types/marketing';
import { MOCK_STOREFRONTS } from '../mocks/storefront.mock';
import { MOCK_MARKETING_TEMPLATES, MOCK_CAMPAIGN_RESPONSE } from '../mocks/marketing.mock';

const BASE_URL = (import.meta as any).env.VITE_BACKEND_URL || 'http://localhost:8000';
const API_V1 = `${BASE_URL}/api/v1`;

// Mock Data for fallback
const MOCK_PRODUCTS: Product[] = [
  { sku: '12345678', name: 'Migros Bio-Milch 1L', priceChf: 2.95, stock: 42, category: 'dairy', holidayMultiplier: 4.0, imageUrl: 'https://picsum.photos/seed/milk/400/400' },
  { sku: '23456789', name: 'Raclette Käse 500g', priceChf: 8.95, stock: 15, category: 'cheese', holidayMultiplier: 1.5, safetyStock: 20, imageUrl: 'https://picsum.photos/seed/cheese/400/400' },
  { sku: '34567890', name: 'Lindt Excellence 70% Kakao', priceChf: 4.50, stock: 85, category: 'chocolate', holidayMultiplier: 3.5, imageUrl: 'https://picsum.photos/seed/chocolate/400/400' },
  { sku: '45678901', name: 'M-Budget Pizza Margherita 400g', priceChf: 3.95, stock: 5, category: 'frozen', safetyStock: 15, imageUrl: 'https://picsum.photos/seed/pizza/400/400' },
  { sku: '56789012', name: 'Migros Mountain Water 1.5L', priceChf: 1.20, stock: 120, category: 'beverages', imageUrl: 'https://picsum.photos/seed/water/400/400' },
  { sku: '67890123', name: 'Appenzeller Alpenbitter', priceChf: 29.90, stock: 12, category: 'spirits', holidayMultiplier: 1.2, imageUrl: 'https://picsum.photos/seed/spirits/400/400' },
  { sku: '78901234', name: 'M Classic Fondue Set', priceChf: 18.90, stock: 3, category: 'kitchen', holidayMultiplier: 1.5, safetyStock: 10, imageUrl: 'https://picsum.photos/seed/fondue/400/400' },
  { sku: '89012345', name: 'Salomon Ski Goggles', priceChf: 189.00, stock: 7, category: 'ski_gear', holidayMultiplier: 2.8, safetyStock: 15, imageUrl: 'https://picsum.photos/seed/ski/400/400' },
  { sku: '90123456', name: 'Migros Bio Eggs 6pcs', priceChf: 4.20, stock: 24, category: 'organic', imageUrl: 'https://picsum.photos/seed/eggs/400/400' },
  { sku: '01234567', name: 'M-Budget Pasta 500g', priceChf: 0.95, stock: 200, category: 'm_budget', imageUrl: 'https://picsum.photos/seed/pasta/400/400' },
];

const MOCK_STORES = [
  { id: 'migros_zh_stockerhof', name: 'Zürich HB (Stockerhof)', capacity: 120 },
  { id: 'migros_be_bahnhof', name: 'Bern HB', capacity: 95 },
  { id: 'migros_appenzell', name: 'Appenzell (Rural)', capacity: 35 },
  { id: 'migros_vs_sion', name: 'Valais Sion', capacity: 52 },
  { id: 'migros_ge_carouge', name: 'Geneva Carouge', capacity: 78 },
];

const MOCK_METRICS: Metrics = {
  stockoutsPrevented: 142,
  chfSaved: 24567.00,
  co2SavedKg: 18200,
  managerHoursReclaimed: 48,
  twintConversion: 58.0,
  pickupEfficiency: 94.0
};

const MOCK_ORDERS: Order[] = [
  { id: 'ORD-1001', status: 'delivered', totalChf: 45.60, createdAt: new Date(Date.now() - 3600000).toISOString(), paymentProvider: 'twint', items: [{ sku: 'M-001', quantity: 2, priceAtOrder: 1.95 }], pickupWindowId: 'W-1' },
  { id: 'ORD-1002', status: 'pending', totalChf: 12.40, createdAt: new Date(Date.now() - 1800000).toISOString(), paymentProvider: 'stripe', items: [{ sku: 'M-003', quantity: 4, priceAtOrder: 2.50 }], pickupWindowId: 'W-2' },
  { id: 'ORD-1003', status: 'confirmed', totalChf: 8.90, createdAt: new Date().toISOString(), paymentProvider: 'twint', items: [{ sku: 'M-005', quantity: 5, priceAtOrder: 1.60 }], pickupWindowId: 'W-3' },
];

const MOCK_WINDOWS: PickupWindow[] = Array.from({ length: 24 }, (_, i) => ({
  id: `W-${i}`,
  storeId: 'migros_zh_stockerhof',
  start: new Date(new Date().setHours(8 + i, 0, 0, 0)).toISOString(),
  end: new Date(new Date().setHours(9 + i, 0, 0, 0)).toISOString(),
  capacity: 10,
  booked: Math.floor(Math.random() * 11)
}));

const MOCK_COMPLIANCE: ComplianceScore = {
  overallScore: 96,
  biasDrift: 1.2,
  privacyRisk: 0.5,
  humanOverrideRate: 4.2,
  lastAuditDate: new Date().toLocaleDateString()
};

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const error = await res.json().catch(() => ({ message: `API Error: ${res.status}` }));
    throw new Error(error.message || `API Error: ${res.status}`);
  }
  return res.json();
}

export const api = {
  // AI Query
  async postQuery(req: QueryRequest): Promise<QueryResponse> {
    try {
      const res = await fetch(`${API_V1}/query/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req),
      });
      return await handleResponse<QueryResponse>(res);
    } catch (e) {
      console.warn("Backend unavailable, using mock response", e);
      return {
        messages: ["I'm currently in demo mode. Based on our retail data, your Zürich store is performing 12% above target this week. Dairy stock is healthy, but we recommend restocking Rösti soon."],
        products: MOCK_PRODUCTS.slice(0, 2),
        pickupWindow: MOCK_WINDOWS[0]
      };
    }
  },

  // Products
  async searchProducts(params: { query?: string; category?: string; tenant?: string; storeId?: string }): Promise<Product[]> {
    try {
      const res = await fetch(`${API_V1}/search/semantic`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          text: params.query || '', 
          category: params.category,
          tenant: params.tenant,
          store_id: params.storeId 
        }),
      });
      return await handleResponse<Product[]>(res);
    } catch (e) {
      console.warn("Backend unavailable, using mock products", e);
      const q = params.query?.toLowerCase() || '';
      return MOCK_PRODUCTS.filter(p => p.name.toLowerCase().includes(q) || p.category.toLowerCase().includes(q));
    }
  },

  async getLowStockProducts(storeId: string): Promise<Product[]> {
    try {
      const res = await fetch(`${API_V1}/inventory/low-stock?store_id=${storeId}`);
      return await handleResponse<Product[]>(res);
    } catch (e) {
      console.warn("Backend unavailable, using mock low stock", e);
      return MOCK_PRODUCTS.filter(p => p.stock < (p.safetyStock || 10));
    }
  },

  // Scheduling
  async parseSwissTime(text: string): Promise<{ start: string; end: string }> {
    try {
      const res = await fetch(`${API_V1}/schedule/parse`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      return await handleResponse<{ start: string; end: string }>(res);
    } catch (e) {
      return { start: new Date().toISOString(), end: new Date(Date.now() + 3600000).toISOString() };
    }
  },

  async getPickupWindows(storeId: string, days: number = 7): Promise<PickupWindow[]> {
    try {
      const res = await fetch(`${API_V1}/schedule/windows?store_id=${storeId}&days=${days}`);
      return await handleResponse<PickupWindow[]>(res);
    } catch (e) {
      console.warn("Backend unavailable, using mock windows", e);
      return MOCK_WINDOWS;
    }
  },

  // Checkout & Orders
  async createStripePayment(orderId: string): Promise<{ client_secret: string }> {
    try {
      const res = await fetch(`${API_V1}/checkout/stripe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ order_id: orderId }),
      });
      return await handleResponse<{ client_secret: string }>(res);
    } catch (e) {
      return { client_secret: 'mock_secret' };
    }
  },

  async createTwintPayment(orderId: string): Promise<{ qrCodeUrl: string; paymentId: string }> {
    try {
      const res = await fetch(`${API_V1}/checkout/twint`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ order_id: orderId }),
      });
      return await handleResponse<{ qrCodeUrl: string; paymentId: string }>(res);
    } catch (e) {
      return { qrCodeUrl: 'https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=TWINT_MOCK_QR', paymentId: 'mock_twint_id' };
    }
  },

  async getOrders(storeId: string): Promise<Order[]> {
    try {
      const res = await fetch(`${API_V1}/orders?store_id=${storeId}`);
      return await handleResponse<Order[]>(res);
    } catch (e) {
      console.warn("Backend unavailable, using mock orders", e);
      return MOCK_ORDERS;
    }
  },

  // Metrics
  async getImpactMetrics(): Promise<Metrics> {
    try {
      const res = await fetch(`${API_V1}/metrics/impact`);
      return await handleResponse<Metrics>(res);
    } catch (e) {
      console.warn("Backend unavailable, using mock metrics", e);
      return MOCK_METRICS;
    }
  },

  // Governance
  async getComplianceScore(): Promise<ComplianceScore> {
    try {
      const res = await fetch(`${API_V1}/grc/compliance`);
      return await handleResponse<ComplianceScore>(res);
    } catch (e) {
      console.warn("Backend unavailable, using mock compliance", e);
      return MOCK_COMPLIANCE;
    }
  },

  // AI Storefront
  async generateStorefront(req: AIStorefrontRequest): Promise<AIStorefrontPayload> {
    try {
      const res = await fetch(`${API_V1}/storefront/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req),
      });
      return await handleResponse<AIStorefrontPayload>(res);
    } catch (e) {
      console.warn("Backend AI Storefront unavailable, using mock", e);
      return MOCK_STOREFRONTS[req.query || 'default'] || MOCK_STOREFRONTS['default'];
    }
  },

  // AI Marketing
  async generateMarketing(req: MarketingRequest): Promise<MarketingResponse> {
    try {
      const res = await fetch(`${API_V1}/ai-marketing/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req),
      });
      return await handleResponse<MarketingResponse>(res);
    } catch (e) {
      console.warn("Backend AI Marketing unavailable, using mock", e);
      // Simulate 90s delay in a real app, but for demo we'll just return mock
      return MOCK_CAMPAIGN_RESPONSE;
    }
  },

  async getMarketingTemplates(): Promise<MarketingTemplate[]> {
    try {
      const res = await fetch(`${API_V1}/marketing/templates`);
      return await handleResponse<MarketingTemplate[]>(res);
    } catch (e) {
      console.warn("Backend Marketing Templates unavailable, using mock", e);
      return MOCK_MARKETING_TEMPLATES;
    }
  },

  async scheduleMarketing(campaignId: string, schedule: any): Promise<{ status: string }> {
    try {
      const res = await fetch(`${API_V1}/marketing/schedule`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ campaignId, schedule }),
      });
      return await handleResponse<{ status: string }>(res);
    } catch (e) {
      return { status: 'scheduled' };
    }
  },

  // Stores
  async getStores(): Promise<any[]> {
    return MOCK_STORES;
  },

  async getProducts(): Promise<Product[]> {
    return MOCK_PRODUCTS;
  }
};
