import React, { useState, useEffect } from 'react';
import { api } from '../lib/api';
import { Order } from '../types/retail';
import { ShoppingBag, Clock, CheckCircle, XCircle, CreditCard, QrCode, ExternalLink, ChevronRight, Package, Search } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

export function Orders({ storeId, t, subView }: { storeId: string, t: any, subView?: string }) {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [filter, setFilter] = useState<Order['status'] | 'all'>('all');

  useEffect(() => {
    async function load() {
      try {
        let results = await api.getOrders(storeId);
        
        // Apply subView filters
        if (subView === 'orders-pending') {
          setFilter('pending');
        } else if (subView === 'orders-history') {
          setFilter('delivered');
        } else if (subView === 'orders-returns') {
          setFilter('cancelled');
        } else {
          setFilter('all');
        }
        
        setOrders(results);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [storeId, subView]);

  const filteredOrders = filter === 'all' ? orders : orders.filter(o => o.status === filter);

  const statusColors = {
    pending: 'bg-amber-100 text-amber-600',
    confirmed: 'bg-blue-100 text-blue-600',
    shipped: 'bg-indigo-100 text-indigo-600',
    delivered: 'bg-emerald-100 text-emerald-600',
    cancelled: 'bg-red-100 text-red-600'
  };

  const statusIcons = {
    pending: Clock,
    confirmed: CheckCircle,
    shipped: Package,
    delivered: CheckCircle,
    cancelled: XCircle
  };

  return (
    <div className="flex h-full overflow-hidden bg-slate-50">
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Orders Header */}
        <div className="p-6 bg-white border-b border-slate-200 shadow-sm flex items-center justify-between">
          <div className="flex items-center gap-6">
            <h2 className="text-xl font-bold text-slate-900">{t.ordersCheckout}</h2>
            <div className="flex bg-slate-100 p-1 rounded-xl">
              {['all', 'pending', 'confirmed', 'delivered'].map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f as any)}
                  className={`px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-widest transition-all ${
                    filter === f ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-400 hover:text-slate-600'
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search order ID..." 
              className="pl-10 pr-4 py-2 bg-slate-50 border-none rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20"
            />
          </div>
        </div>

        {/* Orders List */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-5xl mx-auto space-y-4">
            {loading ? (
              <div className="p-12 text-center text-slate-400 animate-pulse">Loading orders...</div>
            ) : filteredOrders.length > 0 ? (
              filteredOrders.map((order) => {
                const StatusIcon = statusIcons[order.status];
                return (
                  <motion.div
                    key={order.id}
                    layout
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    onClick={() => setSelectedOrder(order)}
                    className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md hover:border-blue-200 transition-all cursor-pointer group flex items-center gap-6"
                  >
                    <div className={`p-4 rounded-xl ${statusColors[order.status].replace('text-', 'bg-').replace('600', '50')}`}>
                      <StatusIcon className={`w-6 h-6 ${statusColors[order.status]}`} />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-1">
                        <span className="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest">#{order.id}</span>
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${statusColors[order.status]}`}>
                          {order.status}
                        </span>
                      </div>
                      <p className="font-bold text-slate-900">{order.items.length} items • CHF {order.totalChf.toFixed(2)}</p>
                      <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        Placed on {new Date(order.createdAt).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Payment</p>
                        <div className="flex items-center gap-1.5 text-slate-700 font-bold text-sm">
                          {order.paymentProvider === 'twint' ? <QrCode className="w-4 h-4 text-blue-500" /> : <CreditCard className="w-4 h-4 text-slate-400" />}
                          {order.paymentProvider.toUpperCase()}
                        </div>
                      </div>
                      <ChevronRight className="w-5 h-5 text-slate-300 group-hover:text-blue-500 group-hover:translate-x-1 transition-all" />
                    </div>
                  </motion.div>
                );
              })
            ) : (
              <div className="p-12 text-center bg-white rounded-2xl border border-dashed border-slate-200 text-slate-400">
                No orders found for this filter.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Order Detail Sidebar */}
      <AnimatePresence>
        {selectedOrder && (
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            className="w-[450px] bg-white border-l border-slate-200 shadow-2xl flex flex-col z-20"
          >
            <div className="p-6 border-b border-slate-100 flex items-center justify-between">
              <h3 className="font-bold text-slate-900">Order Details</h3>
              <button onClick={() => setSelectedOrder(null)} className="p-2 hover:bg-slate-100 rounded-xl transition-colors">
                <ChevronRight className="w-5 h-5 text-slate-400" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-6 space-y-8">
              {/* Order Summary */}
              <div className="bg-slate-50 p-6 rounded-2xl space-y-4">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Order ID</p>
                    <p className="font-mono font-bold text-slate-900 text-lg">#{selectedOrder.id}</p>
                  </div>
                  <div className={`px-3 py-1 rounded-lg text-xs font-bold uppercase tracking-wider ${statusColors[selectedOrder.status]}`}>
                    {selectedOrder.status}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-6 pt-4 border-t border-slate-200">
                  <div>
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Payment</p>
                    <p className="font-bold text-slate-900 flex items-center gap-2">
                      <CreditCard className="w-4 h-4 text-slate-400" />
                      {selectedOrder.paymentProvider.toUpperCase()}
                    </p>
                  </div>
                  <div>
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Total</p>
                    <p className="font-bold text-slate-900 text-lg">CHF {selectedOrder.totalChf.toFixed(2)}</p>
                  </div>
                </div>
              </div>

              {/* Items List */}
              <div className="space-y-4">
                <h4 className="font-bold text-slate-900 flex items-center gap-2">
                  <ShoppingBag className="w-5 h-5 text-blue-500" />
                  Items ({selectedOrder.items.length})
                </h4>
                <div className="space-y-3">
                  {selectedOrder.items.map((item, i) => (
                    <div key={i} className="flex items-center gap-4 p-3 rounded-xl hover:bg-slate-50 transition-colors border border-transparent hover:border-slate-100">
                      <div className="w-12 h-12 bg-slate-100 rounded-lg flex items-center justify-center">
                        <Package className="w-6 h-6 text-slate-300" />
                      </div>
                      <div className="flex-1">
                        <p className="font-bold text-slate-900 text-sm">SKU: {item.sku}</p>
                        <p className="text-xs text-slate-500">{item.quantity} units @ CHF {item.priceAtOrder.toFixed(2)}</p>
                      </div>
                      <p className="font-bold text-slate-900">CHF {(item.quantity * item.priceAtOrder).toFixed(2)}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="space-y-3 pt-4">
                <button className="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-2xl shadow-lg shadow-emerald-500/20 transition-all flex items-center justify-center gap-2">
                  <CheckCircle className="w-5 h-5" />
                  Mark as Delivered
                </button>
                <button className="w-full py-4 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 font-bold rounded-2xl transition-all flex items-center justify-center gap-2">
                  <ExternalLink className="w-5 h-5" />
                  View Invoice
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
