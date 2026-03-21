import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Clinics
export const createClinic = async (clinicData) => {
  const response = await axios.post(`${API}/clinics`, clinicData);
  return response.data;
};

export const bulkImportClinics = async (clinics, source = 'Bulk Import') => {
  const response = await axios.post(`${API}/clinics/bulk`, { clinics, source });
  return response.data;
};

export const getClinics = async (skip = 0, limit = 100) => {
  const response = await axios.get(`${API}/clinics?skip=${skip}&limit=${limit}`);
  return response.data;
};

export const scoreClinic = async (clinicId) => {
  const response = await axios.post(`${API}/clinics/${clinicId}/score`);
  return response.data;
};

// Email Management
export const addEmailAccount = async (username, password) => {
  const response = await axios.post(`${API}/email-accounts`, { username, password });
  return response.data;
};

export const getEmailAccounts = async () => {
  const response = await axios.get(`${API}/email-accounts`);
  return response.data;
};

export const getEmailStats = async () => {
  const response = await axios.get(`${API}/email/stats`);
  return response.data;
};

export const getEmailQueue = async (status = null) => {
  const url = status ? `${API}/email/queue?status=${status}` : `${API}/email/queue`;
  const response = await axios.get(url);
  return response.data;
};

export const uploadAttachment = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await axios.post(`${API}/email/attachments`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

// Dashboard Stats
export const getDashboardStats = async () => {
  const response = await axios.get(`${API}/stats/dashboard`);
  return response.data;
};
