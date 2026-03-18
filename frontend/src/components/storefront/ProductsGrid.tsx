import React from 'react';
import { motion } from 'motion/react';
import { ShoppingCart, Calendar, AlertCircle, Mountain } from 'lucide-react';
import { Product } from '../../types/retail';

interface ProductsGridProps {
  title: string;
  subtitle?: string;
  content: Product[];
  onAction: (action: any) => void;
}

export function ProductsGrid({ title, subtitle, content, onAction }: ProductsGridProps) {
  return (
    <section className="mb-16">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
        <div>
          <h2 className="text-3xl font-black text-gray-900 tracking-tight uppercase italic">{title}</h2>
          {subtitle && <p className="text-gray-500 font-medium">{subtitle}</p>}
        </div>
        <button className="text-[#0066CC] font-bold flex items-center gap-2 hover:underline">
          Alle anzeigen
          <ShoppingCart className="w-4 h-4" />
        </button>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
        {content.map((product, i) => (
          <motion.div
            key={product.sku}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="bg-white rounded-[2rem] border border-gray-100 shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden group flex flex-col"
          >
            <div className="relative aspect-[4/5] overflow-hidden bg-gray-50">
              <img 
                src={product.imageUrl} 
                alt={product.name}
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                referrerPolicy="no-referrer"
              />
              
              {/* Brand Badge */}
              <div className="absolute top-4 left-4 flex flex-col gap-2">
                {product.name.toLowerCase().includes('bio') && (
                  <div className="bg-emerald-600 text-white px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest shadow-lg">
                    Migros Bio
                  </div>
                )}
                {product.name.toLowerCase().includes('m-budget') && (
                  <div className="bg-emerald-500 text-white px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest shadow-lg">
                    M-Budget
                  </div>
                )}
              </div>

              {product.holidayMultiplier && product.holidayMultiplier > 1 && (
                <div className="absolute top-4 right-4 bg-indigo-600 text-white px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest shadow-lg flex items-center gap-1">
                  <Mountain className="w-3 h-3" />
                  {product.holidayMultiplier}x Holiday
                </div>
              )}
              
              <div className="absolute inset-x-0 bottom-0 p-4 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                <button 
                  onClick={() => onAction({ type: 'quick-view', payload: product })}
                  className="w-full py-2 bg-white/20 backdrop-blur-md text-white rounded-xl text-xs font-bold uppercase tracking-wider"
                >
                  Schnellansicht
                </button>
              </div>
            </div>
            
            <div className="p-6 flex-1 flex flex-col">
              <div className="flex justify-between items-start mb-2">
                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">SKU {product.sku}</span>
                {product.stock > (product.safetyStock || 10) ? (
                  <span className="text-emerald-500 font-bold text-[10px] uppercase tracking-widest">Vorrätig</span>
                ) : (
                  <span className="text-amber-500 font-bold text-[10px] uppercase tracking-widest">Fast ausverkauft</span>
                )}
              </div>
              
              <h3 className="font-bold text-gray-900 mb-4 line-clamp-2 text-lg leading-tight group-hover:text-[#0066CC] transition-colors">
                {product.name}
              </h3>
              
              <div className="mt-auto pt-4 border-t border-gray-50 flex items-center justify-between">
                <div>
                  <div className="text-2xl font-black text-gray-900">
                    CHF {product.priceChf.toFixed(2)}
                  </div>
                  <div className="text-[10px] text-gray-400 font-medium">inkl. MwSt.</div>
                </div>
                <div className="flex gap-2">
                  <button 
                    onClick={() => onAction({ type: 'add-to-cart', payload: product })}
                    disabled={product.stock === 0}
                    className="w-12 h-12 bg-[#FF6C00] hover:bg-[#e66100] text-white rounded-2xl flex items-center justify-center transition-all hover:scale-110 active:scale-90 disabled:opacity-50 disabled:grayscale shadow-lg shadow-orange-500/20"
                  >
                    <ShoppingCart className="w-6 h-6" />
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
