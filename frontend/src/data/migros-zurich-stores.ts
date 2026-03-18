export interface Store {
  id: string;
  name: string;
  lat: number;
  lng: number;
  address: string;
  capacity: number;
  maxCapacity: number;
  openingHours: string;
  phone: string;
  website: string;
  imageUrl?: string;
}

export const migrosZurichStores: Store[] = [
  {
    id: 'migros_zh_hb_sihlquai',
    name: 'Migros Zürich HB Sihlquai',
    lat: 47.3784,
    lng: 8.5359,
    address: 'Hauptbahnhof, Passage Sihlquai, 8001 Zürich',
    capacity: 120,
    maxCapacity: 120,
    openingHours: '06:30-22:00',
    phone: '+41 44 225 44 00',
    website: 'migros.ch/hb-sihlquai',
    imageUrl: 'https://picsum.photos/seed/migros-hb/400/300'
  },
  {
    id: 'migros_seefeld',
    name: 'Migros Seefeld (Kreis 8)',
    lat: 47.3652,
    lng: 8.5461,
    address: 'Seefeldstrasse 111, 8008 Zürich',
    capacity: 85,
    maxCapacity: 100,
    openingHours: '08:00-20:00',
    phone: '+41 44 384 84 84',
    website: 'migros.ch/seefeld',
    imageUrl: 'https://picsum.photos/seed/migros-seefeld/400/300'
  },
  {
    id: 'migros_burgwies',
    name: 'Migros Burgwies (Kreis 6)',
    lat: 47.3901,
    lng: 8.5123,
    address: 'Burgwiesstrasse 18, 8050 Zürich',
    capacity: 65,
    maxCapacity: 80,
    openingHours: '08:00-20:00',
    phone: '+41 44 317 66 66',
    website: 'migros.ch/burgwies',
    imageUrl: 'https://picsum.photos/seed/migros-burgwies/400/300'
  },
  {
    id: 'migros_stockerhof',
    name: 'Migros Stockerhof (flagship)',
    lat: 47.3685,
    lng: 8.5392,
    address: 'Stockerstrasse 45, 8002 Zürich',
    capacity: 150,
    maxCapacity: 150,
    openingHours: '07:30-20:00',
    phone: '+41 44 204 11 11',
    website: 'migros.ch/stockerhof',
    imageUrl: 'https://picsum.photos/seed/migros-stockerhof/400/300'
  },
  {
    id: 'migros_oerlikon',
    name: 'Migros Oerlikon',
    lat: 47.4178,
    lng: 8.5197,
    address: 'Wallisellenstrasse 333, 8050 Zürich',
    capacity: 95,
    maxCapacity: 120,
    openingHours: '08:00-20:00',
    phone: '+41 44 317 61 11',
    website: 'migros.ch/oerlikon',
    imageUrl: 'https://picsum.photos/seed/migros-oerlikon/400/300'
  },
  {
    id: 'migros_hoengg',
    name: 'Migros Höngg',
    lat: 47.3921,
    lng: 8.4882,
    address: 'Vulkanstrasse 290, 8048 Zürich',
    capacity: 72,
    maxCapacity: 100,
    openingHours: '08:00-20:00',
    phone: '+41 44 434 22 22',
    website: 'migros.ch/hoengg',
    imageUrl: 'https://picsum.photos/seed/migros-hoengg/400/300'
  },
  {
    id: 'migros_altstetten',
    name: 'Migros Altstetten',
    lat: 47.3865,
    lng: 8.4885,
    address: 'Badenerstrasse 680, 8048 Zürich',
    capacity: 88,
    maxCapacity: 110,
    openingHours: '08:00-20:00',
    phone: '+41 44 434 21 11',
    website: 'migros.ch/altstetten',
    imageUrl: 'https://picsum.photos/seed/migros-altstetten/400/300'
  },
  {
    id: 'migros_city',
    name: 'Migros City (Löwenstrasse)',
    lat: 47.3802,
    lng: 8.5264,
    address: 'Löwenstrasse 35, 8001 Zürich',
    capacity: 110,
    maxCapacity: 130,
    openingHours: '09:00-20:00',
    phone: '+41 44 225 11 11',
    website: 'migros.ch/city',
    imageUrl: 'https://picsum.photos/seed/migros-city/400/300'
  },
  {
    id: 'migros_zuerichberg',
    name: 'Migros Zürichberg',
    lat: 47.3701,
    lng: 8.5623,
    address: 'Universitätsspital Zürich',
    capacity: 45,
    maxCapacity: 60,
    openingHours: '07:00-19:00',
    phone: '+41 44 255 11 11',
    website: 'migros.ch/zuerichberg',
    imageUrl: 'https://picsum.photos/seed/migros-zuerichberg/400/300'
  },
  {
    id: 'migros_klusplatz',
    name: 'Migros Klusplatz',
    lat: 47.3832,
    lng: 8.5034,
    address: 'Klusplatz 12, 8038 Zürich',
    capacity: 58,
    maxCapacity: 80,
    openingHours: '08:00-20:00',
    phone: '+41 44 384 81 11',
    website: 'migros.ch/klusplatz',
    imageUrl: 'https://picsum.photos/seed/migros-klusplatz/400/300'
  },
  {
    id: 'migros_letzigraben',
    name: 'Migros Letzigraben',
    lat: 47.3856,
    lng: 8.5218,
    address: 'Letzigraben 91, 8003 Zürich',
    capacity: 76,
    maxCapacity: 100,
    openingHours: '08:00-20:00',
    phone: '+41 44 497 11 11',
    website: 'migros.ch/letzigraben',
    imageUrl: 'https://picsum.photos/seed/migros-letzigraben/400/300'
  },
  {
    id: 'migros_schwamendingen',
    name: 'Migros Schwamendingen',
    lat: 47.4102,
    lng: 8.5498,
    address: 'Neugutstrasse 127, 8050 Zürich',
    capacity: 62,
    maxCapacity: 90,
    openingHours: '08:00-20:00',
    phone: '+41 44 317 62 11',
    website: 'migros.ch/schwamendingen',
    imageUrl: 'https://picsum.photos/seed/migros-schwamendingen/400/300'
  }
];
