// frontend/src/api.js
import axios from 'axios';

// Базовый URL нашего бэкенда (FastAPI)
const API_BASE = 'http://localhost:8000';

// Создаём экземпляр axios с предустановленным baseURL
const api = axios.create({
  baseURL: API_BASE,
});

// Добавляем перехватчик запросов, чтобы автоматически подставлять токен
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Функции для работы с API
export const register = (email, password) => 
  api.post('/auth/register', { email, password });

export const login = (email, password) => {
  // OAuth2 требует форму с username и password в формате form-data
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);
  return api.post('/auth/login', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

//2FA login verification 
export const verify2FALogin = (temp_token, code) => 
  api.post('/auth/verify-2fa-login', null, { params: { temp_token, code } });


export const getLinks = () => api.get('/links/');

export const createLink = (original_url,custom_code) => 
  api.post('/links/', { original_url, custom_code });

export const delete_link = (short_code) =>
  api.delete (`/links/${short_code}`);



// 2FA
export const enable2FA = () => api.get('/auth/enable-2fa', { responseType: 'blob' });

export const verify2FA = (code) => api.post('/auth/verify-2fa', null, { params: { code } });
export const disable2FA = () => api.post('/auth/disable-2fa');
export const get2FAStatus = () => api.get('/auth/2fa-status');


export const updateLink = (short_code, original_url) => 
  api.put(`/links/${short_code}`, { original_url });



export const getLinkStats = (short_code) => api.get(`/links/${short_code}/stats`);