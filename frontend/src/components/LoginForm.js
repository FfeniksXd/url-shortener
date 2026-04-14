import React, { useState } from 'react';
import { login, verify2FALogin } from '../api';
import './LoginForm.css';

function LoginForm({ onLogin, onRegister }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [tempToken, setTempToken] = useState(null);
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const clearError = () => setError('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await login(email, password);
      if (response.data.need_2fa) {
        setTempToken(response.data.temp_token);
      } else {
        localStorage.setItem('token', response.data.access_token);
        onLogin();
      }
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Не удалось войти. Проверьте данные.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyCode = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await verify2FALogin(tempToken, code);
      localStorage.setItem('token', response.data.access_token);
      onLogin();
    } catch (err) {
      setError('Неверный код двухфакторной аутентификации');
    } finally {
      setLoading(false);
    }
  };

  const handleBackToLogin = () => {
    setTempToken(null);
    setCode('');
    setError('');
  };

  if (tempToken) {
    return (
      <div className="login-container">
        <form onSubmit={handleVerifyCode} className="login-form">
          <h2 className="login-title">Двухфакторная аутентификация</h2>
          <p className="login-subtitle">
            Введите код из вашего приложения-аутентификатора
          </p>

          {error && <div className="error-message">{error}</div>}

          <div className="input-group">
            <input
              type="text"
              placeholder="6-значный код"
              value={code}
              onChange={(e) => {
                setCode(e.target.value);
                clearError();
              }}
              required
              autoFocus
              className="login-input"
              maxLength="6"
              pattern="\d*"
              inputMode="numeric"
            />
          </div>

          <button type="submit" disabled={loading} className="login-button">
            {loading ? 'Проверка...' : 'Подтвердить'}
          </button>

          <button
            type="button"
            onClick={handleBackToLogin}
            className="secondary-button"
          >
            ← Вернуться к входу
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="login-container">
      <form onSubmit={handleSubmit} className="login-form">
        <h2 className="login-title">Вход в систему</h2>
        <p className="login-subtitle">
          Введите вашу электронную почту и пароль
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

        <button type="submit" disabled={loading} className="login-button">
          {loading ? 'Вход...' : 'Войти'}
        </button>

        {onRegister && (
          <div className="register-section">
            <span className="register-text">Нет аккаунта?</span>
            <button
              type="button"
              onClick={onRegister}
              className="register-button"
            >
              Зарегистрироваться
            </button>
          </div>
        )}
      </form>
    </div>
  );
}

export default LoginForm;