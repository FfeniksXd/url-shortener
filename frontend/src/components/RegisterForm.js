import React, { useState } from 'react';
import { register } from '../api';
import './RegisterForm.css'; // Используем тот же файл стилей, что и для логина, либо отдельный

function RegisterForm({ onRegister, onSwitchToLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const clearError = () => setError('');

  const validateForm = () => {
    if (!email || !password || !confirmPassword) {
      setError('Все поля обязательны для заполнения');
      return false;
    }
    if (password.length < 6) {
      setError('Пароль должен содержать минимум 6 символов');
      return false;
    }
    if (password !== confirmPassword) {
      setError('Пароли не совпадают');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      await register(email, password);
      // Успешная регистрация
      onRegister(); // переключаем на форму логина
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Ошибка регистрации. Попробуйте другой email.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit} className="login-form">
        <h2 className="login-title">Регистрация</h2>
        <p className="login-subtitle">
          Создайте аккаунт для доступа к сервису
        </p>

        {error && <div className="error-message">{error}</div>}

        <div className="input-group">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              clearError();
            }}
            required
            className="login-input"
            autoFocus
          />
        </div>

        <div className="input-group">
          <input
            type="password"
            placeholder="Пароль"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              clearError();
            }}
            required
            className="login-input"
          />
        </div>

        <div className="input-group">
          <input
            type="password"
            placeholder="Подтвердите пароль"
            value={confirmPassword}
            onChange={(e) => {
              setConfirmPassword(e.target.value);
              clearError();
            }}
            required
            className="login-input"
          />
        </div>

        <button type="submit" disabled={loading} className="login-button">
          {loading ? 'Регистрация...' : 'Зарегистрироваться'}
        </button>

        {onSwitchToLogin && (
          <div className="register-section">
            <span className="register-text">Уже есть аккаунт?</span>
            <button
              type="button"
              onClick={onSwitchToLogin}
              className="register-button"
            >
              Войти
            </button>
          </div>
        )}
      </form>
    </div>
  );
}

export default RegisterForm;