export interface Product {
  sku: string;
  name: string;
  category: string;
  priceChf: number;
  stock: number;
  holidayMultiplier?: number;
  safetyStock?: number;
  description?: string;
  imageUrl?: string;
  score?: number;
  vectorId?: string;
}

export interface PickupWindow {
  id: string;
  start: string;
  end: string;
  storeId: string;
  capacity: number;
  booked: number;
}

export interface Order {
  id: string;
  status: 'pending' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled';
  totalChf: number;
  paymentProvider: 'stripe' | 'twint' | 'postfinance';
  pickupWindowId: string;
  items: Array<{
    sku: string;
    quantity: number;
    priceAtOrder: number;
  }>;
  createdAt: string;
}

export interface Metrics {
  stockoutsPrevented: number;
  chfSaved: number;
  co2SavedKg: number;
  managerHoursReclaimed: number;
  pickupEfficiency: number;
  twintConversion: number;
}

export interface ComplianceScore {
  overallScore: number;
  biasDrift: number;
  privacyRisk: number;
  humanOverrideRate: number;
  lastAuditDate: string;
}

export interface QueryRequest {
  text: string;
  tenant: string;
  storeId: string;
}

export interface QueryResponse {
  products?: Product[];
  pickupWindow?: PickupWindow;
  payment?: {
    provider: "twint" | "stripe" | "postfinance";
    paymentId: string;
    qrCodeUrl?: string;
    redirectUrl?: string;
    status: string;
  };
  messages?: string[];
}
