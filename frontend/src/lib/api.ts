import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api',
});

export const getDocuments = async () => {
  const res = await api.get('/documents');
  return res.data;
};

export const uploadDocument = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
};

export const deleteDocument = async (id: string) => {
  const res = await api.delete(`/documents/${id}`);
  return res.data;
};

export const queryDocuments = async (question: string, docIds: string[], sessionId?: string, compareMode = false) => {
  const res = await api.post('/chat/query', {
    question,
    doc_ids: docIds,
    session_id: sessionId,
    compare_mode: compareMode
  });
  return res.data;
};

export const getSessions = async () => {
  const res = await api.get('/sessions');
  return res.data;
};

export const getSession = async (id: string) => {
  const res = await api.get(`/sessions/${id}`);
  return res.data;
};
