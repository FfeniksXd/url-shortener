import React, { useState } from 'react';
import { login, verify2FALogin } from '../api';

function LoginForm({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [tempToken, setTempToken] = useState(null);
  const [code, setCode] = useState('');

  // Первый этап: отправляем email и пароль
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await login(email, password);
      if (response.data.need_2fa) {
        // Требуется 2FA, сохраняем временный токен и показываем поле для кода
        setTempToken(response.data.temp_token);
      } else {
        // 2FA не включена, сохраняем обычный токен
        localStorage.setItem('token', response.data.access_token);
        onLogin();
      }
    } catch (err) {
      alert('Ошибка входа: ' + (err.response?.data?.detail || err.message));
    }
  };

  // Второй этап: подтверждаем код 2FA
  const handleVerifyCode = async (e) => {
    e.preventDefault();
    try {
      const response = await verify2FALogin(tempToken, code);
      localStorage.setItem('token', response.data.access_token);
      onLogin();
    } catch (err) {
      alert('Неверный код двухфакторной аутентификации');
    }
  };

  // Если есть временный токен, показываем форму для ввода кода
  if (tempToken) {
    return (
      <form onSubmit={handleVerifyCode}>
        <h2>Введите код из приложения-аутентификатора</h2>
        <input
          type="text"
          placeholder="Код"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          required
        />
        <button type="submit">Подтвердить</button>
      </form>
    );
  }

  // Иначе показываем обычную форму входа
  return (
    <form onSubmit={handleSubmit}>
      <h2>Вход</h2>
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Пароль"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <button type="submit">Войти</button>
    </form>
  );
}

export default LoginForm;