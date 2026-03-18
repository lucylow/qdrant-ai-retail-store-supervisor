import { GoogleGenAI, Type } from "@google/genai";

export type Language = 'en' | 'de' | 'fr' | 'it' | 'rm';

export interface Attachment {
  id: string;
  name: string;
  type: string; // mimeType
  data: string; // base64
  url?: string; // data URL for preview
}

export interface Message {
  id: string;
  role: 'user' | 'model';
  text: string;
  timestamp: number;
  model?: string;
  citations?: string[];
  attachments?: Attachment[];
  thought?: string;
  sources?: { title: string, url: string }[];
}

export interface Agent {
  id: string;
  name: string;
  description: string;
  systemPrompt: string;
  outputFormat: 'short' | 'medium' | 'long';
  structure: 'bullet' | 'paragraph';
  guardrail?: string;
  models: string[];
  tools: string[];
  ragDocuments: string[];
  access: 'private' | 'groups' | 'public' | 'team';
  createdAt?: number;
  author?: string;
  usageCount?: number;
  rating?: number;
}

export interface RAGDocument {
  id: string;
  name: string;
  type: string;
  size: string;
  uploadedAt: number;
  uploadedBy: string;
  content?: string;
  fileData?: string;
  metadata?: Record<string, any>;
}

export const INITIAL_AGENTS: Agent[] = [
  {
    id: '1',
    name: 'Scoping Assistant',
    description: 'Helps translate high-level ideas or client goals into structured, actionable project scopes.',
    systemPrompt: 'You are a domain-aware AI project scoping assistant. Your job is to take high-level business goals or initiative descriptions and produce a structured, implementation-ready scope.',
    outputFormat: 'medium',
    structure: 'bullet',
    models: ['gemini-3.1-pro-preview'],
    tools: ['googleSearch', 'webScraper'],
    ragDocuments: [],
    access: 'private'
  },
  {
    id: '2',
    name: 'Legal Researcher',
    description: 'Analyzes legal documents and provides summaries based on case law.',
    systemPrompt: 'You are a legal research assistant. You provide precise, cited information from legal documents. Always maintain a professional and objective tone.',
    outputFormat: 'long',
    structure: 'paragraph',
    models: ['gemini-3.1-pro-preview'],
    tools: ['googleSearch'],
    ragDocuments: [],
    access: 'private'
  },
  {
    id: '3',
    name: 'Code Reviewer',
    description: 'Specializes in reviewing code for security, performance, and best practices.',
    systemPrompt: 'You are an expert software engineer. Review the provided code for security vulnerabilities, performance bottlenecks, and adherence to clean code principles.',
    outputFormat: 'medium',
    structure: 'bullet',
    models: ['gemini-3-flash-preview'],
    tools: [],
    ragDocuments: [],
    access: 'private'
  }
];

export const AVAILABLE_MODELS = [
  { id: 'gemini-3.1-pro-preview', name: 'GPT 4.1 (Europe)', provider: 'OpenAI (Azure)' },
  { id: 'gemini-3.1-flash-lite-preview', name: 'GPT 4.1 mini (Worldwide)', provider: 'OpenAI (Azure)' },
  { id: 'gemini-3-flash-preview', name: 'GPT 5 (Europe)', provider: 'OpenAI (Azure)' },
  { id: 'gemini-2.5-flash-image', name: 'GPT 5 nano (Worldwide)', provider: 'OpenAI (Azure)' },
];

export const AVAILABLE_TOOLS = [
  { id: 'webScraper', name: 'Web Scraper', description: 'Fetches a URL from the internet and extracts its contents as markdown.' },
  { id: 'googleSearch', name: 'Google Search', description: 'Search the web for real-time information.' },
];
