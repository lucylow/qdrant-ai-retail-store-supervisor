import React from 'react';
import { motion } from 'motion/react';
import { ShoppingCart, Plus, Sparkles } from 'lucide-react';
import { Product } from '../../types/retail';

interface UpsellCarouselProps {
  title: string;
  subtitle?: string;
  content: Product[];
  onAction: (action: any) => void;
}

export function UpsellCarousel({ title, subtitle, content, onAction }: UpsellCarouselProps) {
  return (
    <section className="mb-12 bg-indigo-50/50 p-8 rounded-3xl border border-indigo-100">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-indigo-600 text-white rounded-xl">
          <Sparkles className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
          {subtitle && <p className="text-gray-500">{subtitle}</p>}
        </div>
      </div>
      
      <div className="flex gap-6 overflow-x-auto pb-4 scrollbar-hide">
        {content.map((product, i) => (
          <motion.div
            key={product.sku}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.1 }}
            className="flex-shrink-0 w-64 bg-white rounded-2xl border border-indigo-100 shadow-sm hover:shadow-md transition-shadow overflow-hidden"
          >
            <div className="relative aspect-video overflow-hidden bg-gray-50">
              <img 
                src={product.imageUrl} 
                alt={product.name}
                className="w-full h-full object-cover"
                referrerPolicy="no-referrer"
              />
            </div>
            
            <div className="p-4">
              <h3 className="font-semibold text-gray-900 mb-1 line-clamp-1">
                {product.name}
              </h3>
              <div className="text-indigo-600 font-bold mb-3">
                CHF {product.priceChf.toFixed(2)}
              </div>
              
              <button 
                onClick={() => onAction({ type: 'add-to-cart', payload: product })}
                className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium flex items-center justify-center gap-2 transition-colors"
              >
                <Plus className="w-4 h-4" />
                Hinzufügen
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
