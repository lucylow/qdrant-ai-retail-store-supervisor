import React from 'react';
import { motion } from 'motion/react';
import { Star, Quote, CheckCircle2 } from 'lucide-react';

interface Review {
  user: string;
  rating: number;
  comment: string;
  isVerified?: boolean;
}

interface ReviewsSectionProps {
  title: string;
  subtitle?: string;
  content: Review[];
  onAction: (action: any) => void;
}

export function ReviewsSection({ title, subtitle, content, onAction }: ReviewsSectionProps) {
  return (
    <section className="mb-12">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
        {subtitle && <p className="text-gray-500">{subtitle}</p>}
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {content.map((review, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="p-6 bg-white rounded-2xl border border-gray-100 shadow-sm relative overflow-hidden"
          >
            <Quote className="absolute top-4 right-4 w-8 h-8 text-gray-50" />
            
            <div className="flex items-center gap-2 mb-4">
              <div className="flex text-amber-400">
                {Array.from({ length: 5 }).map((_, j) => (
                  <Star 
                    key={j} 
                    className={`w-4 h-4 ${j < review.rating ? 'fill-current' : 'text-gray-200'}`} 
                  />
                ))}
              </div>
              <span className="text-sm font-bold text-gray-900">{review.rating}.0</span>
            </div>
            
            <p className="text-gray-600 italic mb-6 relative z-10">
              "{review.comment}"
            </p>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center font-bold text-gray-400 text-xs">
                  {review.user.split(' ').map(n => n[0]).join('')}
                </div>
                <div>
                  <div className="text-sm font-bold text-gray-900">{review.user}</div>
                  <div className="text-xs text-emerald-600 flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" />
                    Verifizierter Käufer
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
