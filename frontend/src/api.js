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
  return api.post('/auth/token', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export const getLinks = () => api.get('/links/');

export const createLink = (original_url,custom_code) => 
  api.post('/links/', { original_url, custom_code });