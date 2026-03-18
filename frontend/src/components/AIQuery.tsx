import React, { useState, useRef, useEffect } from 'react';
import { api } from '../lib/api';
import { QueryResponse } from '../types/retail';
import { Send, Bot, User, Sparkles, ShoppingCart, Package, Clock, ShieldCheck, AlertCircle, ChevronRight, Tag } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import Markdown from 'react-markdown';

export function AIQuery({ tenant, storeId, t, subView }: { tenant: string, storeId: string, t: any, subView?: string }) {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant', content: string, data?: QueryResponse }>>([]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const getSuggestions = () => {
    if (subView === 'ai-query-stock') return ["Which products are low on stock in Zürich?", "Show me dairy stock levels.", "Analyze holiday demand for chocolate."];
    if (subView === 'ai-query-capacity') return ["Analyze pickup capacity for Easter weekend.", "Show me wait times for tomorrow.", "Optimize staff for Saturday morning."];
    return [
      "Which products are low on stock in Zürich?",
      "Analyze pickup capacity for Easter weekend.",
      "Generate a restock report for dairy.",
      "Show me the most popular items today."
    ];
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim() || loading) return;

    const userMsg = query;
    setQuery('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const response = await api.postQuery({ text: userMsg, tenant, storeId });
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.messages?.[0] || "I've processed your request.",
        data: response
      }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I encountered an error processing your retail query." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-50 overflow-hidden">
      {/* Chat Header */}
      <div className="p-6 bg-white border-b border-slate-200 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-blue-600 rounded-2xl shadow-lg shadow-blue-500/20">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900">{t.aiQuery}</h2>
            <p className="text-xs text-slate-500 font-medium flex items-center gap-1.5">
              <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
              Connected to Migros Qdrant Vector DB
            </p>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-8 space-y-8">
        {messages.length === 0 && (
          <div className="max-w-2xl mx-auto text-center space-y-6 pt-12">
            <div className="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mx-auto">
              <Sparkles className="w-10 h-10 text-blue-500" />
            </div>
            <div className="space-y-2">
              <h3 className="text-2xl font-bold text-slate-900">How can I help you today?</h3>
              <p className="text-slate-500">Ask about stock levels, pickup capacity, or Swiss holiday demand.</p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4">
              {getSuggestions().map((q, i) => (
                <button
                  key={i}
                  onClick={() => { setQuery(q); handleSend(); }}
                  className="p-4 bg-white border border-slate-200 rounded-2xl text-sm font-medium text-slate-700 hover:border-blue-500 hover:bg-blue-50/50 hover:text-blue-600 transition-all text-left shadow-sm"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex gap-4 ${msg.role === 'assistant' ? 'max-w-4xl' : 'max-w-2xl ml-auto flex-row-reverse'}`}
          >
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 shadow-sm ${
              msg.role === 'assistant' ? 'bg-blue-600 text-white' : 'bg-white border border-slate-200 text-slate-600'
            }`}>
              {msg.role === 'assistant' ? <Bot className="w-6 h-6" /> : <User className="w-6 h-6" />}
            </div>
            <div className={`space-y-4 ${msg.role === 'user' ? 'text-right' : ''}`}>
              <div className={`p-6 rounded-3xl shadow-sm ${
                msg.role === 'assistant' ? 'bg-white border border-slate-200 text-slate-800' : 'bg-blue-600 text-white'
              }`}>
                <div className="markdown-body prose prose-slate max-w-none">
                  <Markdown>{msg.content}</Markdown>
                </div>
              </div>

              {/* Assistant Data Visualizations */}
              {msg.data && (
                <div className="space-y-4">
                  {/* Products List */}
                  {msg.data.products && msg.data.products.length > 0 && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {msg.data.products.map((p) => (
                        <div key={p.sku} className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
                          <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center shrink-0">
                            <Package className="w-6 h-6 text-slate-400" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-bold text-slate-900 truncate text-sm">{p.name}</p>
                            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Stock: {p.stock}</p>
                          </div>
                          <p className="font-bold text-blue-600 text-sm">CHF {p.priceChf.toFixed(2)}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Pickup Window */}
                  {msg.data.pickupWindow && (
                    <div className="bg-blue-50 p-6 rounded-2xl border border-blue-100 flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="p-3 bg-blue-100 rounded-xl">
                          <Clock className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                          <p className="text-[10px] font-bold text-blue-600 uppercase tracking-widest mb-1">Pickup Window Found</p>
                          <p className="font-bold text-blue-900">
                            {new Date(msg.data.pickupWindow.start).toLocaleTimeString()} - {new Date(msg.data.pickupWindow.end).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-xl font-bold text-blue-900">{msg.data.pickupWindow.booked} / {msg.data.pickupWindow.capacity}</p>
                        <p className="text-[10px] font-bold text-blue-400 uppercase tracking-widest">Booked</p>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        ))}

        {loading && (
          <div className="flex gap-4 max-w-2xl">
            <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center shrink-0 animate-pulse">
              <Bot className="w-6 h-6" />
            </div>
            <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-sm flex items-center gap-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.3s]" />
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" />
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-6 bg-white border-t border-slate-200">
        <form onSubmit={handleSend} className="max-w-4xl mx-auto flex gap-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask the Migros AI Supervisor..."
            className="flex-1 px-6 py-4 bg-slate-50 border-none rounded-2xl focus:ring-2 focus:ring-blue-500/20 focus:bg-white transition-all text-slate-900 placeholder:text-slate-400 font-medium"
          />
          <button
            type="submit"
            disabled={!query.trim() || loading}
            className="p-4 bg-blue-600 text-white rounded-2xl shadow-lg shadow-blue-500/20 hover:bg-blue-700 transition-all disabled:opacity-50 disabled:shadow-none"
          >
            <Send className="w-6 h-6" />
          </button>
        </form>
      </div>
    </div>
  );
}
