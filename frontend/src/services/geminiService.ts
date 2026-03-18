import { GoogleGenAI, GenerateContentResponse, Part, Modality } from "@google/genai";
import { Attachment } from "../types";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || '' });

export async function chatWithGemini(
  prompt: string, 
  modelName: string = "gemini-3-flash-preview", 
  attachments: Attachment[] = [], 
  language: string = 'en',
  useSearch: boolean = false,
  ragContent?: string,
  systemInstruction?: string
) {
  try {
    const parts: Part[] = [];

    // Add RAG context if provided
    if (ragContent) {
      parts.push({ text: `CONTEXT FROM DOCUMENTS:\n${ragContent}\n\nUse the above context to help answer the user's request if relevant.` });
    }

    // Add text prompt
    parts.push({ text: prompt });

    // Add attachments
    attachments.forEach(att => {
      parts.push({
        inlineData: {
          mimeType: att.type,
          data: att.data
        }
      });
    });

    const baseSystemInstruction = systemInstruction || "You are a helpful enterprise AI assistant.";

    const response: GenerateContentResponse = await ai.models.generateContent({
      model: modelName,
      contents: { parts },
      config: {
        systemInstruction: `${baseSystemInstruction} Please respond in the following language: ${language}.`,
        tools: useSearch ? [{ googleSearch: {} }] : undefined
      }
    });
    
    // Extract grounding URLs if search was used
    const groundingUrls = response.candidates?.[0]?.groundingMetadata?.groundingChunks?.map(chunk => ({
      title: chunk.web?.title || 'Source',
      url: chunk.web?.uri || ''
    })).filter(c => c.url) || [];

    return {
      text: response.text || "I'm sorry, I couldn't generate a response.",
      thought: response.candidates?.[0]?.content?.parts?.find(p => p.thought)?.text,
      sources: groundingUrls
    };
  } catch (error) {
    console.error("Gemini API Error:", error);
    return { text: "Error: Failed to connect to AI service." };
  }
}

export async function generateSpeech(text: string, language: string = 'en') {
  try {
    // Map language to a suitable voice
    const voiceMap: Record<string, string> = {
      'en': 'Zephyr',
      'de': 'Charon',
      'fr': 'Kore',
      'it': 'Fenrir',
      'rm': 'Puck'
    };

    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash-preview-tts",
      contents: [{ parts: [{ text: `Speak this in ${language}: ${text}` }] }],
      config: {
        responseModalities: [Modality.AUDIO],
        speechConfig: {
          voiceConfig: {
            prebuiltVoiceConfig: { voiceName: voiceMap[language] || 'Zephyr' },
          },
        },
      },
    });

    const base64Audio = response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
    if (base64Audio) {
      return `data:audio/mp3;base64,${base64Audio}`;
    }
    return null;
  } catch (error) {
    console.error("Speech Generation Error:", error);
    return null;
  }
}

export async function generateImage(prompt: string) {
  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash-image',
      contents: {
        parts: [{ text: prompt }],
      },
    });
    
    for (const part of response.candidates?.[0]?.content?.parts || []) {
      if (part.inlineData) {
        return `data:image/png;base64,${part.inlineData.data}`;
      }
    }
    return null;
  } catch (error) {
    console.error("Image Generation Error:", error);
    return null;
  }
}

export async function chatWithGeminiStream(
  prompt: string, 
  modelName: string = "gemini-3-flash-preview", 
  attachments: Attachment[] = [], 
  language: string = 'en',
  useSearch: boolean = false,
  ragContents: { name: string, content: string }[] = [],
  systemInstruction?: string,
  onChunk?: (text: string) => void
) {
  try {
    const parts: Part[] = [];

    // Add RAG context if provided
    if (ragContents.length > 0) {
      let contextText = "CONTEXT FROM DOCUMENTS:\n\n";
      ragContents.forEach(doc => {
        contextText += `--- DOCUMENT: ${doc.name} ---\n${doc.content}\n\n`;
      });
      parts.push({ text: `${contextText}\nUse the above context to help answer the user's request if relevant. Cite your sources by document name when possible.` });
    }

    // Add text prompt
    parts.push({ text: prompt });

    // Add attachments
    attachments.forEach(att => {
      parts.push({
        inlineData: {
          mimeType: att.type,
          data: att.data
        }
      });
    });

    const baseSystemInstruction = systemInstruction || "You are a helpful enterprise AI assistant.";

    const responseStream = await ai.models.generateContentStream({
      model: modelName,
      contents: { parts },
      config: {
        systemInstruction: `${baseSystemInstruction} Please respond in the following language: ${language}.`,
        tools: useSearch ? [{ googleSearch: {} }] : undefined
      }
    });

    let fullText = "";
    let thoughtText = "";
    let groundingUrls: { title: string, url: string }[] = [];

    for await (const chunk of responseStream) {
      const chunkText = chunk.text || "";
      fullText += chunkText;
      
      if (onChunk) {
        onChunk(chunkText);
      }

      // Extract thought if available (usually in first chunk or specific part)
      const thoughtPart = chunk.candidates?.[0]?.content?.parts?.find(p => p.thought);
      if (thoughtPart) {
        thoughtText += thoughtPart.text;
      }

      // Extract grounding metadata if available
      const chunks = chunk.candidates?.[0]?.groundingMetadata?.groundingChunks;
      if (chunks) {
        const urls = chunks.map(c => ({
          title: c.web?.title || 'Source',
          url: c.web?.uri || ''
        })).filter(c => c.url);
        groundingUrls = [...groundingUrls, ...urls];
      }
    }

    return {
      text: fullText,
      thought: thoughtText || undefined,
      sources: groundingUrls.length > 0 ? groundingUrls : undefined
    };
  } catch (error) {
    console.error("Gemini Streaming Error:", error);
    throw error;
  }
}

export async function transcribeAudio(audioData: string, mimeType: string, language: string = 'en') {
  try {
    const response = await ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: {
        parts: [
          {
            inlineData: {
              mimeType: mimeType,
              data: audioData
            }
          },
          {
            text: `Please transcribe this audio exactly as spoken. The audio is likely in ${language}. Just return the transcription text, nothing else.`
          }
        ]
      }
    });
    return response.text?.trim() || "";
  } catch (error) {
    console.error("Transcription Error:", error);
    return "";
  }
}
