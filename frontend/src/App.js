import React, { useState } from 'react';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import LinkList from './components/LinkList';
import './App.css'; // можно оставить как есть

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [showRegister, setShowRegister] = useState(false);

  const handleLogin = () => {
    setToken(localStorage.getItem('token'));
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  if (!token) {
    // Не авторизован – показываем формы входа/регистрации
    return (
      <div style={{ padding: '20px' }}>
        {showRegister ? (
          <>
            <RegisterForm onRegister={() => setShowRegister(false)} />
            <button onClick={() => setShowRegister(false)}>Назад к входу</button>
          </>
        ) : (
          <>
            <LoginForm onLogin={handleLogin} />
            <button onClick={() => setShowRegister(true)}>Зарегистрироваться</button>
          </>
        )}
      </div>
    );
  }

  // Авторизован – показываем список ссылок и кнопку выхода
  return (
    <div style={{ padding: '20px' }}>
      <button onClick={handleLogout}>Выйти</button>
      <LinkList />
    </div>
  );
}

export default App; 