import { enable2FA, verify2FA, disable2FA, get2FAStatus } from '../api';
import React, { useState, useEffect } from 'react';
export default TwoFactorSetup;


function TwoFactorSetup() {
  const [qrCodeUrl, setQrCodeUrl] = useState(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [message, setMessage] = useState('');
  const [isEnabled, setIsEnabled] = useState(false); //  будем получать из профиля

  // Запрос на включение 2FA (получение QR)
  const handleEnable = async () => {
    try {
      const response = await enable2FA(); // ожидаем blob с изображением
      const url = URL.createObjectURL(response.data);
      setQrCodeUrl(url);
      setMessage('Отсканируйте QR-код в приложении-аутентификаторе');
    } catch (err) {
      setMessage('Ошибка при включении 2FA');
    }
  };

  // Подтверждение кода и активация
  const handleVerify = async () => {
    try {
      await verify2FA(verificationCode);
      setMessage('2FA успешно включена!');
      setIsEnabled(true);
      setQrCodeUrl(null);
      setVerificationCode('');
    } catch (err) {
      setMessage('Неверный код. Попробуйте снова.');
    }
  };

  // Отключение 2FA
  const handleDisable = async () => {
    try {
      await disable2FA();
      setMessage('2FA отключена');
      setIsEnabled(false);
    } catch (err) {
      setMessage('Ошибка при отключении 2FA');
    }
  };

// Получение статуса 2FA при загрузке компонента
useEffect(() => {
  const fetchStatus = async () => {
    try {
      const response = await get2FAStatus();
      setIsEnabled(response.data.is_2fa_enabled);
    } catch (err) {
      console.error(err);
    }
  };
  fetchStatus();
}, []);


  return (
    <div>
      <h3>Двухфакторная аутентификация (2FA)</h3>
      {!isEnabled ? (
        <div>
          {!qrCodeUrl ? (
            <button onClick={handleEnable}>Включить 2FA</button>
          ) : (
            <div>
              <img src={qrCodeUrl} alt="QR Code" />
              <input
                type="text"
                placeholder="Введите код из приложения"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
              />
              <button onClick={handleVerify}>Подтвердить</button>
            </div>
          )}
        </div>
      ) : (
        <div>
          <p>2FA включена</p>
          <button onClick={handleDisable}>Отключить 2FA</button>
        </div>
      )}
      {message && <p>{message}</p>}
    </div>
  );
}
