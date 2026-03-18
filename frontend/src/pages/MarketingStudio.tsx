import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Megaphone, 
  Layout, 
  Image as ImageIcon, 
  BarChart3, 
  Download, 
  Calendar,
  ChevronRight,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Smartphone,
  X
} from 'lucide-react';
import { CampaignWizard } from '../components/marketing/CampaignWizard';
import { AssetGrid } from '../components/marketing/AssetGrid';
import { GenerationSpinner } from '../components/marketing/GenerationSpinner';
import { MarketingRequest, MarketingResponse, MarketingAsset } from '../types/marketing';
import { api } from '../lib/api';
import JSZip from 'jszip';

export default function MarketingStudio() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [campaign, setCampaign] = useState<MarketingResponse | null>(null);
  const [selectedAsset, setSelectedAsset] = useState<MarketingAsset | null>(null);
  const [activeTab, setActiveTab] = useState<'campaigns' | 'templates' | 'assets' | 'analytics'>('campaigns');

  const handleGenerate = async (req: MarketingRequest) => {
    setIsGenerating(true);
    setCampaign(null);
    
    // Simulate 90s generation for demo, but shorter for UX
    setTimeout(async () => {
      try {
        const response = await api.generateMarketing(req);
        setCampaign(response);
      } catch (error) {
        console.error('Generation failed', error);
      } finally {
        setIsGenerating(false);
      }
    }, 5000);
  };

  const downloadAll = async () => {
    if (!campaign) return;
    const zip = new JSZip();
    
    const assetFolder = zip.folder("assets");
    for (const asset of campaign.assets) {
      try {
        const response = await fetch(asset.url);
        const blob = await response.blob();
        assetFolder?.file(`${asset.id}_${asset.type}.${asset.format}`, blob);
      } catch (e) {
        console.warn(`Failed to download asset ${asset.id}`, e);
      }
    }
    
    zip.file('campaign_data.json', JSON.stringify({
      campaignId: campaign.campaignId,
      copy: campaign.copy,
      analytics: campaign.analytics
    }, null, 2));

    const content = await zip.generateAsync({ type: "blob" });
    const url = window.URL.createObjectURL(content);
    const link = document.createElement('a');
    link.href = url;
    link.download = `migros_campaign_${campaign.campaignId}.zip`;
    link.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] pt-24 pb-32">
      <div className="max-w-7xl mx-auto px-8 lg:px-12">
        {/* Header */}
        <header className="mb-20 flex flex-col lg:flex-row lg:items-end justify-between gap-12">
          <div className="flex-1">
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-4 text-migros-orange font-black text-xs uppercase tracking-[0.4em] mb-6"
            >
              <div className="w-12 h-1.5 bg-migros-orange rounded-full shadow-lg shadow-orange-500/20" />
              <Megaphone className="w-5 h-5" />
              Marketing Studio
            </motion.div>
            <h1 className="text-6xl md:text-8xl font-black text-slate-900 tracking-tighter italic uppercase leading-[0.85] mb-8">
              AI Creative <br />
              <span className="text-gradient-orange">Factory</span>
            </h1>
            <p className="text-xl text-slate-500 max-w-2xl font-medium leading-relaxed">
              Generate production-grade social media, video, and print assets in 90 seconds. 
              Powered by Migros Brain AI.
            </p>
          </div>
          
          <div className="flex flex-col items-end gap-6">
            <div className="bento-card p-6 flex items-center gap-6 min-w-[320px]">
              <div className="w-14 h-14 bg-migros-blue/10 text-migros-blue rounded-2xl flex items-center justify-center shadow-inner">
                <Layout className="w-7 h-7" />
              </div>
              <div>
                <div className="text-[10px] text-slate-400 font-black uppercase tracking-widest mb-1">Active Campaigns</div>
                <div className="text-xl font-black text-slate-900 italic uppercase tracking-tighter">23 Live Assets</div>
              </div>
            </div>
            <div className="flex items-center gap-3 text-[10px] font-black text-emerald-500 uppercase tracking-widest bg-emerald-50 px-6 py-3 rounded-full border border-emerald-100 shadow-sm">
              <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shadow-lg shadow-emerald-500/50" />
              Migros Brand Compliance Active
            </div>
          </div>
        </header>

        {/* Sidebar Tabs */}
        <div className="flex flex-col lg:flex-row gap-16">
          <aside className="lg:w-72 space-y-3">
            {[
              { id: 'campaigns', icon: <Megaphone />, label: 'Campaigns' },
              { id: 'templates', icon: <Layout />, label: 'Templates' },
              { id: 'assets', icon: <ImageIcon />, label: 'Assets' },
              { id: 'analytics', icon: <BarChart3 />, label: 'Analytics' },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`w-full flex items-center gap-5 px-8 py-5 rounded-[2rem] text-xs font-black uppercase tracking-widest transition-all duration-300 group ${
                  activeTab === tab.id 
                    ? 'bg-white text-slate-900 shadow-2xl shadow-slate-200/50 border border-slate-100' 
                    : 'text-slate-400 hover:text-slate-600 hover:bg-slate-100/50'
                }`}
              >
                <div className={`w-10 h-10 rounded-2xl flex items-center justify-center transition-all group-hover:scale-110 ${activeTab === tab.id ? 'bg-orange-50 text-migros-orange shadow-inner' : 'bg-slate-100'}`}>
                  {React.cloneElement(tab.icon as React.ReactElement<any>, { className: 'w-5 h-5' })}
                </div>
                {tab.label}
              </button>
            ))}
          </aside>

          <main className="flex-1 space-y-16">
            <AnimatePresence mode="wait">
              {!campaign && !isGenerating && (
                <motion.div
                  key="wizard"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                >
                  <CampaignWizard onGenerate={handleGenerate} isGenerating={isGenerating} />
                </motion.div>
              )}

              {isGenerating && (
                <motion.div
                  key="spinner"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <GenerationSpinner />
                </motion.div>
              )}

              {campaign && !isGenerating && (
                <motion.div
                  key="results"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-16"
                >
                  {/* Campaign Summary */}
                  <div className="bento-card p-10 flex flex-col md:flex-row justify-between items-center gap-12">
                    <div className="flex-1">
                      <div className="flex items-center gap-4 mb-6">
                        <div className="px-4 py-1.5 bg-orange-50 text-migros-orange rounded-full text-[10px] font-black uppercase tracking-widest border border-orange-100">
                          New Campaign: {campaign.campaignId}
                        </div>
                        <div className="px-4 py-1.5 bg-emerald-50 text-emerald-600 rounded-full text-[10px] font-black uppercase tracking-widest flex items-center gap-2 border border-emerald-100">
                          <BarChart3 className="w-4 h-4" />
                          {campaign.analytics.predictedCTR}% Avg CTR
                        </div>
                      </div>
                      <h2 className="text-4xl font-black text-slate-900 italic uppercase tracking-tighter mb-4 leading-none">
                        {campaign.copy.headline}
                      </h2>
                      <p className="text-slate-500 font-medium text-lg leading-relaxed">{campaign.copy.subheadline}</p>
                      <div className="flex flex-wrap gap-4 mt-6">
                        {campaign.copy.hashtags.map(tag => (
                          <span key={tag} className="text-[10px] font-black text-migros-blue uppercase tracking-[0.2em] bg-blue-50 px-3 py-1 rounded-lg">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="flex flex-col sm:flex-row gap-4 w-full md:w-auto">
                      <button 
                        onClick={() => setCampaign(null)}
                        className="px-10 py-5 bg-slate-50 text-slate-400 rounded-[2rem] font-black text-xs uppercase tracking-widest hover:bg-slate-100 transition-all active:scale-95"
                      >
                        New Campaign
                      </button>
                      <button 
                        onClick={downloadAll}
                        className="px-10 py-5 bg-migros-orange text-white rounded-[2rem] font-black text-xs uppercase tracking-widest shadow-2xl shadow-orange-500/30 hover:scale-105 transition-all active:scale-95 flex items-center justify-center gap-4"
                      >
                        <Download className="w-5 h-5" />
                        Download ZIP (3.2MB)
                      </button>
                    </div>
                  </div>

                  {/* Asset Grid */}
                  <AssetGrid assets={campaign.assets} onPreview={setSelectedAsset} />

                  {/* Schedule CTA */}
                  <div className="bg-migros-blue rounded-[3rem] p-16 text-white flex flex-col lg:flex-row items-center justify-between gap-12 relative overflow-hidden shadow-2xl shadow-blue-900/40">
                    <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2 blur-[100px]" />
                    <div className="relative z-10 text-center lg:text-left">
                      <h2 className="text-5xl font-black italic uppercase tracking-tighter mb-6 leading-none">
                        Ready to go <span className="text-migros-orange">live?</span>
                      </h2>
                      <p className="text-blue-100 text-xl max-w-xl font-medium leading-relaxed">
                        Schedule your campaign across Meta, TikTok, and Google Display with one click. 
                        AI-optimized delivery windows included.
                      </p>
                    </div>
                    <button className="relative z-10 px-12 py-6 bg-white text-migros-blue rounded-[2.5rem] font-black text-2xl uppercase tracking-widest italic shadow-2xl shadow-blue-900/40 hover:scale-105 transition-all active:scale-95 flex items-center gap-6 group">
                      <Calendar className="w-8 h-8 group-hover:rotate-12 transition-transform" />
                      Schedule Posts
                      <ArrowRight className="w-8 h-8 group-hover:translate-x-2 transition-transform" />
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </main>
        </div>
      </div>

      {/* Preview Modal */}
      <AnimatePresence>
        {selectedAsset && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-8 md:p-16">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedAsset(null)}
              className="absolute inset-0 bg-slate-900/95 backdrop-blur-2xl"
            />
            <motion.div 
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
              className="relative w-full max-w-6xl bg-white rounded-[4rem] overflow-hidden shadow-2xl flex flex-col lg:flex-row"
            >
              <button 
                onClick={() => setSelectedAsset(null)}
                className="absolute top-8 right-8 z-10 w-14 h-14 bg-slate-100 hover:bg-slate-200 rounded-2xl flex items-center justify-center transition-all active:scale-90"
              >
                <X className="w-7 h-7 text-slate-900" />
              </button>

              <div className="flex-1 bg-slate-50 flex items-center justify-center p-12 border-r border-slate-100">
                {selectedAsset.type === 'video' ? (
                  <video 
                    src={selectedAsset.url} 
                    controls 
                    autoPlay 
                    className="max-h-[75vh] rounded-[2.5rem] shadow-[0_50px_100px_-20px_rgba(0,0,0,0.3)]"
                  />
                ) : (
                  <img 
                    src={selectedAsset.url} 
                    alt="Preview" 
                    className="max-h-[75vh] rounded-[2.5rem] shadow-[0_50px_100px_-20px_rgba(0,0,0,0.3)] object-contain"
                  />
                )}
              </div>

              <div className="w-full lg:w-[450px] p-16 space-y-12 flex flex-col justify-center">
                <div>
                  <div className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] mb-6">Asset Intelligence</div>
                  <h3 className="text-4xl font-black text-slate-900 italic uppercase tracking-tighter leading-none">
                    {selectedAsset.type} Ad
                  </h3>
                  <p className="text-slate-500 font-medium mt-4 text-lg">
                    {selectedAsset.width} x {selectedAsset.height} px &bull; {selectedAsset.format.toUpperCase()}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-6">
                  <div className="p-6 bg-emerald-50 rounded-[2rem] border border-emerald-100">
                    <div className="text-[10px] font-black text-emerald-600 uppercase tracking-widest mb-2">Predicted CTR</div>
                    <div className="text-3xl font-black text-emerald-700 italic tracking-tighter">{selectedAsset.analytics.predictedCTR}%</div>
                  </div>
                  <div className="p-6 bg-blue-50 rounded-[2rem] border border-blue-100">
                    <div className="text-[10px] font-black text-blue-600 uppercase tracking-widest mb-2">Est. Reach</div>
                    <div className="text-3xl font-black text-blue-700 italic tracking-tighter">{selectedAsset.analytics.estimatedReach.toLocaleString()}</div>
                  </div>
                </div>

                <div className="space-y-4">
                  <button className="w-full py-6 bg-migros-orange text-white rounded-[2rem] font-black text-xs uppercase tracking-widest shadow-2xl shadow-orange-500/30 flex items-center justify-center gap-4 hover:scale-105 transition-all active:scale-95">
                    <Download className="w-5 h-5" />
                    Download Asset
                  </button>
                  <button className="w-full py-6 bg-slate-50 text-slate-400 rounded-[2rem] font-black text-xs uppercase tracking-widest flex items-center justify-center gap-4 hover:bg-slate-100 transition-all active:scale-95">
                    <Sparkles className="w-5 h-5" />
                    Regenerate Copy
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Footer Branding */}
      <footer className="mt-40 pt-20 border-t border-slate-100 max-w-7xl mx-auto px-8 lg:px-12">
        <div className="flex flex-col md:flex-row justify-between items-center gap-12">
          <div className="flex items-center gap-6">
            <div className="w-16 h-16 bg-migros-orange rounded-[1.5rem] flex items-center justify-center shadow-2xl shadow-orange-500/30">
              <span className="text-3xl font-black text-white italic">M</span>
            </div>
            <div className="text-left">
              <div className="text-2xl font-black text-slate-900 italic uppercase tracking-tighter">Migros Marketing Studio</div>
              <div className="text-xs text-slate-400 font-bold uppercase tracking-widest">AI Creative Factory &bull; v2.5</div>
            </div>
          </div>
          
          <div className="flex gap-12">
            <div className="text-center md:text-right">
              <div className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mb-3">Compliance</div>
              <div className="flex items-center gap-3 text-slate-900 font-black text-sm uppercase italic">
                <ShieldCheck className="w-5 h-5 text-emerald-500" />
                Brand Safe AI
              </div>
            </div>
            <div className="text-center md:text-right">
              <div className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mb-3">Platform</div>
              <div className="flex items-center gap-3 text-slate-900 font-black text-sm uppercase italic text-migros-green">
                <Smartphone className="w-5 h-5" />
                Omnichannel Ready
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
