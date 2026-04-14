import React, { useState, useEffect } from 'react';
import { enable2FA, verify2FA, disable2FA, get2FAStatus } from '../api';
import './TwoFactorSetup.css';

function TwoFactorSetup({ onBack }) {
  const [qrCodeUrl, setQrCodeUrl] = useState(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isEnabled, setIsEnabled] = useState(false);
  const [loading, setLoading] = useState(false);

  // Загрузка статуса 2FA
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await get2FAStatus();
        setIsEnabled(response.data.is_2fa_enabled);
      } catch (err) {
        console.error('Ошибка получения статуса 2FA:', err);
      }
    };
    fetchStatus();
  }, []);

  const clearMessages = () => {
    setMessage('');
    setError('');
  };

  const handleEnable = async () => {
    clearMessages();
    setLoading(true);
    try {
      const response = await enable2FA();
      const url = URL.createObjectURL(response.data);
      setQrCodeUrl(url);
      setMessage('Отсканируйте QR-код в приложении-аутентификаторе');
    } catch (err) {
      setError('Не удалось получить QR-код. Попробуйте позже.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    if (!verificationCode) {
      setError('Введите код из приложения');
      return;
    }
    clearMessages();
    setLoading(true);
    try {
      await verify2FA(verificationCode);
      setMessage('2FA успешно включена!');
      setIsEnabled(true);
      setQrCodeUrl(null);
      setVerificationCode('');
    } catch (err) {
      setError('Неверный код. Попробуйте снова.');
    } finally {
      setLoading(false);
    }
  };

  const handleDisable = async () => {
    if (!window.confirm('Вы уверены, что хотите отключить двухфакторную аутентификацию?')) return;
    clearMessages();
    setLoading(true);
    try {
      await disable2FA();
      setMessage('2FA успешно отключена');
      setIsEnabled(false);
    } catch (err) {
      setError('Ошибка при отключении 2FA');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setQrCodeUrl(null);
    setVerificationCode('');
    clearMessages();
  };

  return (
    <div className="twofa-container">
      <div className="twofa-card">
        <div className="twofa-header">
          <h2 className="twofa-title">Двухфакторная аутентификация</h2>
          {onBack && (
            <button className="back-button" onClick={onBack}>
              ← Назад
            </button>
          )}
        </div>

        {message && <div className="twofa-success">{message}</div>}
        {error && <div className="twofa-error">{error}</div>}

        {!isEnabled ? (
          <div className="twofa-setup">
            {!qrCodeUrl ? (
              <>
                <p className="twofa-description">
                  Двухфакторная аутентификация добавляет дополнительный уровень защиты вашей учётной записи.
                  После включения при входе потребуется вводить одноразовый код из приложения-аутентификатора.
                </p>
                <button
                  className="twofa-button primary"
                  onClick={handleEnable}
                  disabled={loading}
                >
                  {loading ? 'Загрузка...' : 'Включить 2FA'}
                </button>
              </>
            ) : (
              <form onSubmit={handleVerify} className="twofa-verify-form">
                <div className="qr-section">
                  <img src={qrCodeUrl} alt="QR-код для настройки 2FA" className="qr-code" />
                  <p className="qr-hint">
                    Отсканируйте QR-код в приложении Google Authenticator, Authy или любом другом.
                  </p>
                </div>
                <div className="input-group">
                  <input
                    type="text"
                    placeholder="Введите 6-значный код"
                    value={verificationCode}
                    onChange={(e) => {
                      setVerificationCode(e.target.value);
                      clearMessages();
                    }}
                    required
                    className="twofa-input"
                    maxLength="6"
                    pattern="\d*"
                    inputMode="numeric"
                    autoFocus
                  />
                </div>
                <div className="twofa-actions">
                  <button type="submit" className="twofa-button primary" disabled={loading}>
                    {loading ? 'Проверка...' : 'Подтвердить'}
                  </button>
                  <button
                    type="button"
                    className="twofa-button secondary"
                    onClick={handleCancel}
                    disabled={loading}
                  >
                    Отмена
                  </button>
                </div>
              </form>
            )}
          </div>
        ) : (
          <div className="twofa-enabled">
            <div className="twofa-status">
              <span className="status-badge enabled">✓ 2FA включена</span>
            </div>
            <p className="twofa-description">
              Ваша учётная запись защищена двухфакторной аутентификацией.
              При входе потребуется вводить код из приложения-аутентификатора.
            </p>
            <button
              className="twofa-button danger"
              onClick={handleDisable}
              disabled={loading}
            >
              {loading ? 'Отключение...' : 'Отключить 2FA'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default TwoFactorSetup;