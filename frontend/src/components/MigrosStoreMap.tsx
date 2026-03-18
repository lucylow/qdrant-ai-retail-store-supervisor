import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Store } from '../data/migros-zurich-stores';
import { HeatmapLayer } from 'react-leaflet-heatmap-layer-v3';

// Fix for Leaflet default icon issue in React
const icon = 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png';
const iconShadow = 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

// Custom Migros Icon
const migrosIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

interface MigrosStoreMapProps {
  stores: Store[];
  center: [number, number];
  zoom?: number;
  onStoreSelect?: (store: Store) => void;
  showHeatmap?: boolean;
}

function MapUpdater({ center, zoom }: { center: [number, number], zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
}

export function MigrosStoreMap({ stores, center, zoom = 13, onStoreSelect, showHeatmap = true }: MigrosStoreMapProps) {
  const getCapacityColor = (utilization: number) => {
    if (utilization > 0.8) return '#ef4444'; // Red
    if (utilization > 0.5) return '#f59e0b'; // Amber
    return '#10b981'; // Green
  };

  return (
    <div className="relative w-full h-full rounded-[2rem] overflow-hidden border border-gray-100 shadow-2xl shadow-blue-900/5">
      <MapContainer 
        center={center} 
        zoom={zoom} 
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />
        
        <MapUpdater center={center} zoom={zoom} />

        {showHeatmap && (
          <HeatmapLayer
            fitBoundsOnLoad
            fitBoundsOnUpdate
            points={stores}
            longitudeExtractor={(s: Store) => s.lng}
            latitudeExtractor={(s: Store) => s.lat}
            intensityExtractor={(s: Store) => (s.capacity / s.maxCapacity)}
            radius={40}
            blur={20}
            max={1.0}
          />
        )}

        {stores.map(store => {
          const utilization = store.capacity / store.maxCapacity;
          return (
            <React.Fragment key={store.id}>
              <Marker 
                position={[store.lat, store.lng]} 
                icon={migrosIcon}
                eventHandlers={{
                  click: () => onStoreSelect?.(store)
                }}
              >
                <Popup className="migros-popup">
                  <div className="p-2 min-w-[200px]">
                    <h3 className="text-sm font-black text-gray-900 italic uppercase tracking-tight mb-1">{store.name}</h3>
                    <p className="text-[10px] text-gray-500 mb-2">{store.address}</p>
                    
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-widest">
                        <span>Capacity</span>
                        <span style={{ color: getCapacityColor(utilization) }}>
                          {store.capacity} / {store.maxCapacity}
                        </span>
                      </div>
                      <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
                        <div 
                          className="h-full transition-all duration-500"
                          style={{ 
                            width: `${utilization * 100}%`,
                            backgroundColor: getCapacityColor(utilization)
                          }}
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-2 mt-4">
                      <a 
                        href={`maps://maps.apple.com/?q=${encodeURIComponent(store.name)}&ll=${store.lat},${store.lng}`}
                        className="px-3 py-2 bg-gray-50 text-gray-900 rounded-xl text-[10px] font-black uppercase tracking-widest text-center hover:bg-gray-100 transition-all"
                      >
                        Route
                      </a>
                      <button 
                        onClick={() => window.location.href = `/schedule?storeId=${store.id}`}
                        className="px-3 py-2 bg-[#FF6C00] text-white rounded-xl text-[10px] font-black uppercase tracking-widest text-center shadow-lg shadow-orange-500/20 hover:scale-105 transition-all"
                      >
                        Book
                      </button>
                    </div>
                  </div>
                </Popup>
              </Marker>
            </React.Fragment>
          );
        })}
      </MapContainer>

      <style dangerouslySetInnerHTML={{ __html: `
        .migros-popup .leaflet-popup-content-wrapper {
          border-radius: 1.5rem;
          padding: 0;
          overflow: hidden;
          box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
        }
        .migros-popup .leaflet-popup-content {
          margin: 0;
        }
        .migros-popup .leaflet-popup-tip-container {
          display: none;
        }
      `}} />
    </div>
  );
}
