import React from 'react';
import { AIStorefrontSection } from '../../types/storefront';
import { HeroSection } from './HeroSection';
import { ProductsGrid } from './ProductsGrid';
import { PickupSlots } from './PickupSlots';
import { UpsellCarousel } from './UpsellCarousel';
import { ReviewsSection } from './ReviewsSection';
import { TWINTCheckoutZone } from './TWINTCheckoutZone';

const sectionRenderers: Record<string, React.FC<any>> = {
  hero: HeroSection,
  products: ProductsGrid,
  slots: PickupSlots,
  upsells: UpsellCarousel,
  reviews: ReviewsSection,
  checkout: TWINTCheckoutZone
};

interface AISectionProps {
  section: AIStorefrontSection;
  onAction: (action: any) => void;
}

export function AISection({ section, onAction }: AISectionProps) {
  const Component = sectionRenderers[section.type];
  
  if (!Component) {
    console.warn(`No renderer found for section type: ${section.type}`);
    return null;
  }
  
  return <Component {...section} onAction={onAction} />;
}
