import React from 'react';
import { motion } from 'motion/react';

export function StorefrontSkeleton() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 animate-pulse">
      {/* Header Skeleton */}
      <div className="mb-12 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-4">
          <div className="h-4 w-32 bg-gray-200 rounded-full" />
          <div className="h-10 w-64 bg-gray-200 rounded-xl" />
          <div className="h-6 w-96 bg-gray-200 rounded-lg" />
        </div>
        <div className="h-16 w-48 bg-gray-200 rounded-2xl" />
      </div>
      
      {/* Hero Skeleton */}
      <div className="h-[400px] w-full bg-gray-200 rounded-3xl mb-16" />
      
      {/* Products Grid Skeleton */}
      <div className="mb-16">
        <div className="h-8 w-48 bg-gray-200 rounded-lg mb-8" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="space-y-4">
              <div className="aspect-square bg-gray-200 rounded-2xl" />
              <div className="h-4 w-3/4 bg-gray-200 rounded-full" />
              <div className="h-4 w-1/2 bg-gray-200 rounded-full" />
              <div className="h-10 w-full bg-gray-200 rounded-xl" />
            </div>
          ))}
        </div>
      </div>
      
      {/* Slots Skeleton */}
      <div className="mb-16">
        <div className="h-8 w-48 bg-gray-200 rounded-lg mb-8" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-32 bg-gray-200 rounded-2xl" />
          ))}
        </div>
      </div>
    </div>
  );
}
