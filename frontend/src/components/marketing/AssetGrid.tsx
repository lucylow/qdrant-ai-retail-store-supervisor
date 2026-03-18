import React from 'react';
import { motion } from 'motion/react';
import { MarketingAsset } from '../../types/marketing';
import { 
  Download, 
  Eye, 
  TrendingUp, 
  Users, 
  Play, 
  FileCode, 
  Mail, 
  ImageIcon 
} from 'lucide-react';

interface AssetCardProps {
  asset: MarketingAsset;
  onPreview: (asset: MarketingAsset) => void;
}

export function AssetCard({ asset, onPreview }: AssetCardProps) {
  const getIcon = () => {
    switch (asset.type) {
      case 'video': return <Play className="w-5 h-5" />;
      case 'html': return <FileCode className="w-5 h-5" />;
      case 'email': return <Mail className="w-5 h-5" />;
      default: return <ImageIcon className="w-5 h-5" />;
    }
  };

  return (
    <motion.div 
      whileHover={{ y: -12 }}
      className="bento-card overflow-hidden group border-slate-100/50"
    >
      <div className="relative aspect-[4/5] bg-slate-50 overflow-hidden">
        <img 
          src={asset.previewUrl} 
          alt={asset.type} 
          className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-110"
        />
        <div className="absolute inset-0 bg-slate-900/60 opacity-0 group-hover:opacity-100 transition-all duration-500 flex items-center justify-center gap-6 backdrop-blur-[2px]">
          <button 
            onClick={() => onPreview(asset)}
            className="w-16 h-16 bg-white text-slate-900 rounded-[1.5rem] flex items-center justify-center hover:scale-110 active:scale-95 transition-all shadow-2xl"
          >
            <Eye className="w-8 h-8" />
          </button>
          <a 
            href={asset.url} 
            download 
            className="w-16 h-16 bg-migros-orange text-white rounded-[1.5rem] flex items-center justify-center hover:scale-110 active:scale-95 transition-all shadow-2xl shadow-orange-500/40"
          >
            <Download className="w-8 h-8" />
          </a>
        </div>
        <div className="absolute top-6 left-6 px-4 py-2 bg-white/90 backdrop-blur-xl rounded-2xl flex items-center gap-3 text-[10px] font-black uppercase tracking-[0.2em] text-slate-900 shadow-2xl border border-white/50">
          <div className="text-migros-orange">
            {getIcon()}
          </div>
          {asset.type}
        </div>
      </div>

      <div className="p-8 space-y-6">
        <div className="flex items-center justify-between">
          <div className="text-[10px] font-black text-slate-400 italic uppercase tracking-widest">
            {asset.width} x {asset.height} px
          </div>
          <div className="px-4 py-2 bg-emerald-50 text-emerald-600 rounded-full text-[10px] font-black uppercase tracking-[0.2em] flex items-center gap-2 border border-emerald-100 shadow-sm">
            <TrendingUp className="w-3.5 h-3.5" />
            {asset.analytics.predictedCTR}% CTR
          </div>
        </div>

        <div className="flex items-center gap-6 pt-6 border-t border-slate-50">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-slate-50 rounded-xl flex items-center justify-center">
              <Users className="w-4 h-4 text-slate-400" />
            </div>
            <div>
              <div className="text-[10px] font-black text-slate-900 uppercase tracking-tight">
                {asset.analytics.estimatedReach.toLocaleString()}
              </div>
              <div className="text-[8px] text-slate-400 font-bold uppercase tracking-widest">
                Est. Reach
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

interface AssetGridProps {
  assets: MarketingAsset[];
  onPreview: (asset: MarketingAsset) => void;
}

export function AssetGrid({ assets, onPreview }: AssetGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {assets.map((asset, i) => (
        <AssetCard key={asset.id} asset={asset} onPreview={onPreview} />
      ))}
    </div>
  );
}
