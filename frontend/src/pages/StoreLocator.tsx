import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  MapPin, 
  Navigation, 
  Clock, 
  Phone, 
  Globe, 
  ChevronRight, 
  Search, 
  Filter, 
  TrendingUp, 
  ShieldCheck, 
  Smartphone,
  X,
  ArrowRight,
  Zap,
  Layout,
  Megaphone
} from 'lucide-react';
import { MigrosStoreMap } from '../components/MigrosStoreMap';
import { migrosZurichStores, Store } from '../data/migros-zurich-stores';

export default function StoreLocator() {
  const [selectedStore, setSelectedStore] = useState<Store | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [mapCenter, setMapCenter] = useState<[number, number]>([47.3784, 8.5359]);
  const [mapZoom, setMapZoom] = useState(13);
  const [isBottomSheetOpen, setIsBottomSheetOpen] = useState(false);
  const [activeFilter, setActiveFilter] = useState<'all' | 'high' | 'low'>('all');

  const filteredStores = migrosZurichStores.filter(store => {
    const matchesSearch = store.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                         store.address.toLowerCase().includes(searchQuery.toLowerCase());
    
    const utilization = store.capacity / store.maxCapacity;
    if (activeFilter === 'high') return matchesSearch && utilization > 0.8;
    if (activeFilter === 'low') return matchesSearch && utilization < 0.5;
    return matchesSearch;
  });

  const handleStoreSelect = (store: Store) => {
    setSelectedStore(store);
    setMapCenter([store.lat, store.lng]);
    setMapZoom(15);
    setIsBottomSheetOpen(true);
  };

  const handleMyLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((position) => {
        const { latitude, longitude } = position.coords;
        setMapCenter([latitude, longitude]);
        setMapZoom(15);
      });
    }
  };

  return (
    <div className="min-h-screen bg-slate-50/50 pt-24 pb-32 overflow-hidden flex flex-col">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full flex-1 flex flex-col">
        {/* Header */}
        <header className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-10">
          <div className="flex-1">
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-4 text-migros-orange font-black text-[10px] uppercase tracking-[0.4em] mb-6"
            >
              <div className="w-12 h-1 bg-migros-orange rounded-full" />
              <MapPin className="w-5 h-5" />
              Store Finder Zürich
            </motion.div>
            <h1 className="text-6xl md:text-8xl font-black text-slate-900 tracking-tighter italic uppercase leading-[0.85]">
              Find Your <span className="text-migros-orange">Migros</span>
            </h1>
            <p className="text-xl text-slate-500 mt-8 max-w-2xl font-medium leading-relaxed">
              Discover 12+ premium locations in Zürich with live capacity heatmaps and real-time status.
            </p>
          </div>
          
          <div className="flex flex-col items-end gap-6">
            <div className="bento-card p-6 flex items-center gap-6 min-w-[320px] border-slate-100 shadow-2xl shadow-blue-900/5">
              <div className="w-16 h-16 bg-blue-50 text-migros-blue rounded-[1.5rem] flex items-center justify-center shadow-inner">
                <Navigation className="w-8 h-8" />
              </div>
              <div>
                <div className="text-[10px] text-slate-400 font-black uppercase tracking-[0.2em] mb-1">Active Stores</div>
                <div className="text-xl font-black text-slate-900 italic uppercase tracking-tight">12 Zürich Locations</div>
              </div>
            </div>
            <div className="flex items-center gap-3 text-[10px] font-black text-emerald-500 uppercase tracking-[0.2em] bg-emerald-50 px-6 py-3 rounded-full border border-emerald-100 shadow-sm">
              <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
              94% Pickup Punctuality
            </div>
          </div>
        </header>

        {/* Search and Filter */}
        <div className="flex flex-col md:flex-row gap-6 mb-12">
          <div className="flex-1 relative group">
            <Search className="absolute left-8 top-1/2 -translate-y-1/2 w-6 h-6 text-slate-400 group-focus-within:text-migros-orange transition-colors" />
            <input 
              type="text" 
              placeholder="Search by store name or address..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-20 pr-10 py-7 bg-white rounded-[2.5rem] border border-slate-100 shadow-2xl shadow-blue-900/5 text-sm font-bold text-slate-900 focus:ring-4 focus:ring-migros-orange/10 focus:border-migros-orange/30 outline-none transition-all placeholder:text-slate-300"
            />
          </div>
          <div className="flex gap-3">
            <button 
              onClick={() => setActiveFilter('all')}
              className={`px-8 py-7 rounded-[2.5rem] font-black text-[10px] uppercase tracking-[0.2em] transition-all duration-300 border ${
                activeFilter === 'all' 
                  ? 'bg-migros-orange text-white border-migros-orange shadow-2xl shadow-orange-500/30 scale-105' 
                  : 'bg-white text-slate-400 border-slate-100 hover:bg-slate-50'
              }`}
            >
              All
            </button>
            <button 
              onClick={() => setActiveFilter('high')}
              className={`px-8 py-7 rounded-[2.5rem] font-black text-[10px] uppercase tracking-[0.2em] transition-all duration-300 border ${
                activeFilter === 'high' 
                  ? 'bg-red-500 text-white border-red-500 shadow-2xl shadow-red-500/30 scale-105' 
                  : 'bg-white text-slate-400 border-slate-100 hover:bg-slate-50'
              }`}
            >
              High Capacity
            </button>
            <button 
              onClick={() => setActiveFilter('low')}
              className={`px-8 py-7 rounded-[2.5rem] font-black text-[10px] uppercase tracking-[0.2em] transition-all duration-300 border ${
                activeFilter === 'low' 
                  ? 'bg-emerald-500 text-white border-emerald-500 shadow-2xl shadow-emerald-500/30 scale-105' 
                  : 'bg-white text-slate-400 border-slate-100 hover:bg-slate-50'
              }`}
            >
              Low Capacity
            </button>
            <button 
              onClick={handleMyLocation}
              className="p-7 bg-blue-50 text-migros-blue rounded-[2.5rem] border border-blue-100 hover:bg-blue-100 transition-all shadow-lg shadow-blue-500/5 active:scale-95"
            >
              <Navigation className="w-7 h-7" />
            </button>
          </div>
        </div>

        {/* Map and List Layout */}
        <div className="flex-1 flex flex-col lg:flex-row gap-10 min-h-[700px]">
          {/* Store List */}
          <aside className="lg:w-[450px] flex flex-col gap-6 overflow-y-auto pr-4 custom-scrollbar">
            {filteredStores.map(store => {
              const utilization = store.capacity / store.maxCapacity;
              const isSelected = selectedStore?.id === store.id;
              
              return (
                <motion.button
                  key={store.id}
                  onClick={() => handleStoreSelect(store)}
                  whileHover={{ x: 8 }}
                  className={`w-full p-8 rounded-[3rem] border text-left transition-all duration-500 relative overflow-hidden group ${
                    isSelected 
                      ? 'bg-white border-migros-orange shadow-[0_32px_64px_-16px_rgba(255,108,0,0.15)]' 
                      : 'bg-white/50 border-slate-100 hover:border-slate-200 hover:bg-white hover:shadow-xl'
                  }`}
                >
                  {isSelected && (
                    <div className="absolute top-0 left-0 w-2 h-full bg-migros-orange" />
                  )}
                  <div className="flex items-start justify-between gap-6 mb-6">
                    <div className="flex-1">
                      <h3 className="text-xl font-black text-slate-900 italic uppercase tracking-tighter truncate leading-tight">
                        {store.name}
                      </h3>
                      <p className="text-[10px] text-slate-400 font-bold uppercase tracking-[0.2em] truncate mt-2">
                        {store.address}
                      </p>
                    </div>
                    <div className={`px-4 py-2 rounded-full text-[10px] font-black uppercase tracking-[0.2em] border ${
                      utilization > 0.8 ? 'bg-red-50 text-red-600 border-red-100' : 
                      utilization > 0.5 ? 'bg-amber-50 text-amber-600 border-amber-100' : 
                      'bg-emerald-50 text-emerald-600 border-emerald-100'
                    }`}>
                      {Math.round(utilization * 100)}% Full
                    </div>
                  </div>

                  <div className="flex items-center gap-6 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
                    <div className="flex items-center gap-2.5">
                      <Clock className="w-4 h-4 text-slate-300" />
                      {store.openingHours}
                    </div>
                    <div className="flex items-center gap-2.5">
                      <Zap className="w-4 h-4 text-slate-300" />
                      {store.capacity} Slots
                    </div>
                  </div>
                </motion.button>
              );
            })}
          </aside>

          {/* Map Container */}
          <main className="flex-1 relative rounded-[4rem] overflow-hidden border-4 border-white shadow-2xl shadow-slate-900/10">
            <MigrosStoreMap 
              stores={filteredStores} 
              center={mapCenter} 
              zoom={mapZoom} 
              onStoreSelect={handleStoreSelect}
            />
          </main>
        </div>
      </div>

      {/* Mobile Bottom Sheet */}
      <AnimatePresence>
        {isBottomSheetOpen && selectedStore && (
          <div className="fixed inset-0 z-[100] flex items-end justify-center pointer-events-none">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsBottomSheetOpen(false)}
              className="absolute inset-0 bg-slate-900/60 backdrop-blur-md pointer-events-auto"
            />
            <motion.div 
              initial={{ y: '100%' }}
              animate={{ y: 0 }}
              exit={{ y: '100%' }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
              className="relative w-full max-w-4xl bg-white rounded-t-[5rem] shadow-[0_-32px_128px_-32px_rgba(0,0,0,0.3)] p-12 md:p-20 pointer-events-auto"
            >
              <div className="w-20 h-2 bg-slate-100 rounded-full mx-auto mb-12" />
              
              <button 
                onClick={() => setIsBottomSheetOpen(false)}
                className="absolute top-12 right-12 w-16 h-16 bg-slate-50 text-slate-400 rounded-full flex items-center justify-center hover:bg-slate-100 hover:text-slate-600 transition-all active:scale-90"
              >
                <X className="w-8 h-8" />
              </button>

              <div className="flex flex-col md:flex-row gap-16">
                <div className="w-full md:w-80 h-80 bg-slate-100 rounded-[4rem] overflow-hidden flex-shrink-0 shadow-2xl border-8 border-white">
                  <img 
                    src={selectedStore.imageUrl} 
                    alt={selectedStore.name} 
                    className="w-full h-full object-cover"
                  />
                </div>

                <div className="flex-1 space-y-10">
                  <div>
                    <div className="text-[10px] font-black text-migros-orange uppercase tracking-[0.4em] mb-4">Selected Store</div>
                    <h2 className="text-5xl font-black text-slate-900 italic uppercase tracking-tighter leading-none">
                      {selectedStore.name}
                    </h2>
                    <p className="text-xl text-slate-500 font-medium mt-6 leading-relaxed">{selectedStore.address}</p>
                  </div>

                  <div className="grid grid-cols-2 gap-6">
                    <div className="p-8 bg-emerald-50 rounded-[2.5rem] border border-emerald-100 shadow-sm">
                      <div className="text-[10px] font-black text-emerald-600 uppercase tracking-[0.2em] mb-2">Capacity</div>
                      <div className="text-4xl font-black text-emerald-700 italic tracking-tighter">{selectedStore.capacity} / {selectedStore.maxCapacity}</div>
                    </div>
                    <div className="p-8 bg-blue-50 rounded-[2.5rem] border border-blue-100 shadow-sm">
                      <div className="text-[10px] font-black text-blue-600 uppercase tracking-[0.2em] mb-2">Status</div>
                      <div className="text-4xl font-black text-blue-700 italic tracking-tighter">OPEN</div>
                    </div>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-6">
                    <a 
                      href={`maps://maps.apple.com/?q=${encodeURIComponent(selectedStore.name)}&ll=${selectedStore.lat},${selectedStore.lng}`}
                      className="flex-1 py-8 bg-migros-orange text-white rounded-[3rem] font-black text-2xl uppercase tracking-[0.2em] italic shadow-2xl shadow-orange-500/40 hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-6"
                    >
                      <Navigation className="w-8 h-8" />
                      Route
                    </a>
                    <button 
                      onClick={() => window.location.href = `/schedule?storeId=${selectedStore.id}`}
                      className="flex-1 py-8 bg-migros-blue text-white rounded-[3rem] font-black text-2xl uppercase tracking-[0.2em] italic shadow-2xl shadow-blue-900/40 hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-6"
                    >
                      <Zap className="w-8 h-8" />
                      Book Now
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Footer Branding */}
      <footer className="mt-auto pt-20 border-t border-slate-100 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full pb-12">
        <div className="flex flex-col md:flex-row justify-between items-center gap-12">
          <div className="flex items-center gap-6">
            <div className="w-16 h-16 bg-migros-orange rounded-[1.5rem] flex items-center justify-center shadow-2xl shadow-orange-500/30">
              <span className="text-3xl font-black text-white italic">M</span>
            </div>
            <div className="text-left">
              <div className="text-2xl font-black text-slate-900 italic uppercase tracking-tighter">Migros Store Finder</div>
              <div className="text-[10px] text-slate-400 font-bold uppercase tracking-[0.3em] mt-1">Zürich Edition</div>
            </div>
          </div>
          
          <div className="flex gap-12">
            <div className="text-center md:text-right">
              <div className="text-[10px] text-slate-400 font-bold uppercase tracking-[0.3em] mb-3">Punctuality</div>
              <div className="flex items-center gap-3 text-slate-900 font-black text-base uppercase italic tracking-tight">
                <ShieldCheck className="w-5 h-5 text-emerald-500" />
                94% Verified
              </div>
            </div>
            <div className="text-center md:text-right">
              <div className="text-[10px] text-slate-400 font-bold uppercase tracking-[0.3em] mb-3">Platform</div>
              <div className="flex items-center gap-3 text-slate-900 font-black text-base uppercase italic tracking-tight text-emerald-600">
                <Smartphone className="w-5 h-5" />
                Mobile First
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
