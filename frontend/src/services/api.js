import axios from 'axios';

// Base API configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const client = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2 minutes for AI generation
});

export const apiService = {
  // Brand profiles
  async getBrandProfiles() {
    const response = await client.get('/brand-profiles/');
    return response.data;
  },

  // Start new generation thread (Round 1)
  async createThread({ app_name, image_type, prompt, custom_width, custom_height, custom_unit }) {
    const payload = {
      app_name,
      image_type,
      prompt,
    };
    if (image_type === 'custom') {
      payload.custom_width = custom_width;
      payload.custom_height = custom_height;
      payload.custom_unit = custom_unit;
    }
    const response = await client.post('/threads/', payload);
    return response.data;
  },

  // Refine chosen image (Round 2+)
  async refineThread(threadId, { selected_image_id, refinement_instruction }) {
    const response = await client.post(`/threads/${threadId}/refine/`, {
      selected_image_id,
      refinement_instruction,
    });
    return response.data;
  },

  // Get full thread history
  async getThreadDetail(threadId) {
    const response = await client.get(`/threads/${threadId}/`);
    return response.data;
  },

  // Image library
  async getImageLibrary(params = {}) {
    const cleanParams = {};
    if (params.app_name && params.app_name !== 'All') {
      cleanParams.app_name = params.app_name;
    }
    if (params.image_type && params.image_type !== 'All') {
      cleanParams.image_type = params.image_type;
    }
    const response = await client.get('/images/', { params: cleanParams });
    return response.data;
  },

  // Finalize / select image
  async selectImage(imageId) {
    const response = await client.post(`/images/${imageId}/select/`);
    return response.data;
  },
};

// Helper: Calculate pixels at 96 DPI for UI hints
export function calculateCustomPixels(width, height, unit) {
  const w = parseFloat(width);
  const h = parseFloat(height);
  if (isNaN(w) || isNaN(h) || w <= 0 || h <= 0) {
    return { widthPx: 0, heightPx: 0, valid: false };
  }
  let wPx = w;
  let hPx = h;
  if (unit === 'cm') {
    wPx = Math.round((w / 2.54) * 96);
    hPx = Math.round((h / 2.54) * 96);
  } else if (unit === 'ft') {
    wPx = Math.round((w * 12 / 2.54) * 96);
    hPx = Math.round((h * 12 / 2.54) * 96);
  } else {
    wPx = Math.round(w);
    hPx = Math.round(h);
  }
  return {
    widthPx: Math.max(64, Math.min(4000, wPx)),
    heightPx: Math.max(64, Math.min(4000, hPx)),
    valid: true,
  };
}
