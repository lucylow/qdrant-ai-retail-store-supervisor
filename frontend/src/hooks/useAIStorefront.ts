import { useState, useEffect } from 'react';
import { api } from '../lib/api';
import { AIStorefrontPayload, AIStorefrontRequest } from '../types/storefront';
import { Language } from '../translations';

export function useAIStorefront(query: string, storeId: string, language: Language) {
  const [storefront, setStorefront] = useState<AIStorefrontPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchStorefront() {
      setLoading(true);
      setError(null);
      try {
        const req: AIStorefrontRequest = {
          query,
          storeId,
          customerPrefs: {
            language
          }
        };
        const data = await api.generateStorefront(req);
        setStorefront(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to generate storefront');
      } finally {
        setLoading(false);
      }
    }

    fetchStorefront();
  }, [query, storeId, language]);

  return { storefront, loading, error };
}
