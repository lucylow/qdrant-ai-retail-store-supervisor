import React, { useState, useEffect } from 'react';
import { api } from '../lib/api';
import { Product } from '../types/retail';
import { Search, Package, ShoppingCart, Info, AlertCircle, ChevronRight, Tag } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

export function ProductSearch({ tenant, storeId, t, subView }: { tenant: string, storeId: string, t: any, subView?: string }) {
  const [query, setQuery] = useState('');
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);
    try {
      let results = await api.searchProducts({ query, storeId, tenant });
      
      // Apply subView filters
      if (subView === 'products-low-stock') {
        results = results.filter(p => p.stock < (p.safetyStock || 10));
      } else if (subView === 'products-holiday') {
        results = results.filter(p => (p.holidayMultiplier || 1) > 1);
      } else if (subView === 'products-categories') {
        // Maybe group by category or just show all
      }
      
      setProducts(results);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleSearch();
  }, [storeId, tenant, subView]);

  return (
    <div className="flex h-full overflow-hidden bg-[#F8FAFC]">
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Search Header */}
        <div className="p-8 bg-white/50 backdrop-blur-xl border-b border-slate-200/60 z-10">
          <form onSubmit={handleSearch} className="max-w-4xl mx-auto relative group">
            <div className="absolute inset-y-0 left-6 flex items-center pointer-events-none">
              <Search className="w-6 h-6 text-slate-400 group-focus-within:text-migros-orange transition-all duration-300" />
            </div>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={t.semanticSearchPlaceholder}
              className="w-full pl-16 pr-6 py-6 bg-white border border-slate-200 rounded-[2rem] focus:ring-4 focus:ring-migros-orange/10 focus:border-migros-orange/30 transition-all text-lg text-slate-900 placeholder:text-slate-400 font-black italic uppercase tracking-tight shadow-xl shadow-slate-200/50"
            />
            {loading && (
              <div className="absolute right-6 inset-y-0 flex items-center">
                <div className="w-6 h-6 border-3 border-migros-orange/20 border-t-migros-orange rounded-full animate-spin" />
              </div>
            )}
          </form>
        </div>

        {/* Results Grid */}
        <div className="flex-1 overflow-y-auto p-12 custom-scrollbar">
          <div className="max-w-7xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-10">
            <AnimatePresence mode="popLayout">
              {products.map((p, idx) => (
                <motion.div
                  key={p.sku}
                  layout
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ delay: idx * 0.05 }}
                  onClick={() => setSelectedProduct(p)}
                  className="bento-card p-6 cursor-pointer group flex flex-col gap-6"
                >
                  <div className="aspect-square bg-slate-50 rounded-[2rem] overflow-hidden relative border border-slate-100">
                    {p.imageUrl ? (
                      <img src={p.imageUrl} alt={p.name} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" referrerPolicy="no-referrer" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <Package className="w-12 h-12 text-slate-200" />
                      </div>
                    )}
                    <div className="absolute top-4 right-4">
                      <div className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest shadow-lg backdrop-blur-md ${
                        p.stock < 10 ? 'bg-red-500/90 text-white' : 'bg-emerald-500/90 text-white'
                      }`}>
                        {p.stock} Units
                      </div>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-4">
                      <h4 className="font-black text-slate-900 italic uppercase tracking-tighter line-clamp-2 leading-[1.1] text-lg group-hover:text-migros-orange transition-colors">{p.name}</h4>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-[10px] text-slate-400 font-black uppercase tracking-widest">
                        <Tag className="w-3 h-3" />
                        {p.category}
                      </div>
                      <p className="font-black text-slate-900 italic uppercase tracking-tighter text-xl">CHF {p.priceChf.toFixed(2)}</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Product Detail Sidebar */}
      <AnimatePresence>
        {selectedProduct && (
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            className="w-[450px] bg-white border-l border-slate-200 shadow-2xl flex flex-col z-30"
          >
            <div className="p-8 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
              <div>
                <h3 className="text-xl font-black text-slate-900 italic uppercase tracking-tighter">Product Intelligence</h3>
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mt-1">SKU: {selectedProduct.sku}</p>
              </div>
              <button onClick={() => setSelectedProduct(null)} className="p-3 hover:bg-slate-200 rounded-2xl transition-all active:scale-90">
                <ChevronRight className="w-6 h-6 text-slate-900" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-8 space-y-10 custom-scrollbar">
              <div className="aspect-square bg-slate-50 rounded-[3rem] overflow-hidden border border-slate-100 shadow-xl">
                {selectedProduct.imageUrl ? (
                  <img src={selectedProduct.imageUrl} alt={selectedProduct.name} className="w-full h-full object-cover" referrerPolicy="no-referrer" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Package className="w-24 h-24 text-slate-200" />
                  </div>
                )}
              </div>
              
              <div className="space-y-8">
                <div>
                  <h2 className="text-3xl font-black text-slate-900 italic uppercase tracking-tighter leading-none mb-4">{selectedProduct.name}</h2>
                  <p className="text-slate-500 font-medium leading-relaxed">{selectedProduct.description || 'Premium Migros product data synchronized with central inventory systems.'}</p>
                </div>

                <div className="grid grid-cols-2 gap-6">
                  <div className="bg-slate-50 p-6 rounded-[2rem] border border-slate-100">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Category</p>
                    <p className="font-black text-slate-900 italic uppercase tracking-tighter text-lg">{selectedProduct.category}</p>
                  </div>
                  <div className="bg-slate-50 p-6 rounded-[2rem] border border-slate-100">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Unit Price</p>
                    <p className="font-black text-slate-900 italic uppercase tracking-tighter text-lg">CHF {selectedProduct.priceChf.toFixed(2)}</p>
                  </div>
                </div>

                <div className="bg-migros-blue/5 p-8 rounded-[2.5rem] border border-migros-blue/10">
                  <div className="flex items-center justify-between mb-4">
                    <p className="text-[10px] font-black text-migros-blue uppercase tracking-widest">Inventory Status</p>
                    <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${
                      selectedProduct.stock < 10 ? 'bg-red-100 text-red-600' : 'bg-emerald-100 text-emerald-600'
                    }`}>
                      {selectedProduct.stock < 10 ? 'Critical' : 'Healthy'}
                    </span>
                  </div>
                  <p className="text-4xl font-black text-migros-blue italic uppercase tracking-tighter">{selectedProduct.stock} Units</p>
                </div>

                {selectedProduct.holidayMultiplier && (
                  <div className="bg-amber-50 p-8 rounded-[2.5rem] border border-amber-100 flex items-center gap-6">
                    <div className="w-14 h-14 bg-amber-100 rounded-2xl flex items-center justify-center shrink-0">
                      <AlertCircle className="w-7 h-7 text-amber-600" />
                    </div>
                    <div>
                      <p className="text-[10px] font-black text-amber-600 uppercase tracking-widest mb-1">Demand Forecast</p>
                      <p className="text-sm font-bold text-amber-900 leading-tight">Seasonal demand is {selectedProduct.holidayMultiplier}x higher than baseline.</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
            <div className="p-8 border-t border-slate-100 bg-white">
              <button className="w-full py-6 bg-migros-orange hover:bg-orange-600 text-white font-black italic uppercase tracking-tighter text-xl rounded-[2rem] shadow-2xl shadow-orange-500/30 transition-all active:scale-[0.98] flex items-center justify-center gap-4">
                <ShoppingCart className="w-6 h-6" />
                Restock Order
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
