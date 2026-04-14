import React, { useEffect, useState } from 'react';
import { getLinks, createLink, delete_link, updateLink } from '../api';
import './LinkList.css';

// Базовый URL вашего бэкенда (можно вынести в .env)
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function LinkList() {
  const [links, setLinks] = useState([]);
  const [newUrl, setNewUrl] = useState('');
  const [customCode, setCustomCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [editModal, setEditModal] = useState({ open: false, short_code: '', currentUrl: '' });

  const fetchLinks = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await getLinks();
      setLinks(response.data);
    } catch (err) {
      setError('Не удалось загрузить ссылки');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLinks();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await createLink(newUrl, customCode || undefined);
      setNewUrl('');
      setCustomCode('');
      await fetchLinks();
    } catch (err) {
      if (err.response?.status === 422) {
        const detail = err.response.data.detail;
        const msg = detail?.[0]?.msg || 'Некорректный формат кастомного кода';
        setError(msg);
      } else {
        setError(err.response?.data?.detail || 'Ошибка при создании ссылки');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (short_code) => {
    if (!window.confirm('Вы уверены, что хотите удалить эту ссылку?')) return;
    setError('');
    setLoading(true);
    try {
      await delete_link(short_code);
      await fetchLinks();
    } catch (err) {
      setError('Ошибка при удалении: ' + (err.response?.data?.detail || err.message));
      setLoading(false);
    }
  };

  const handleEditClick = (short_code, currentUrl) => {
    setEditModal({ open: true, short_code, currentUrl });
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    const newUrlValue = e.target.newUrl.value;
    if (!newUrlValue || newUrlValue === editModal.currentUrl) {
      setEditModal({ open: false, short_code: '', currentUrl: '' });
      return;
    }
    setError('');
    setLoading(true);
    try {
      await updateLink(editModal.short_code, newUrlValue);
      setEditModal({ open: false, short_code: '', currentUrl: '' });
      await fetchLinks();
    } catch (err) {
      setError('Ошибка редактирования: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (short_code) => {
    const url = `${API_BASE_URL}/${short_code}`;
    navigator.clipboard.writeText(url);
    alert('Ссылка скопирована!');
  };

  return (
    <div className="linklist-container">
      <div className="linklist-card">
        <h2 className="linklist-title">Мои ссылки</h2>

        {error && <div className="linklist-error">{error}</div>}

        <form onSubmit={handleCreate} className="linklist-form">
          <div className="input-group">
            <input
              type="url"
              placeholder="Введите длинный URL"
              value={newUrl}
              onChange={(e) => setNewUrl(e.target.value)}
              required
              className="linklist-input"
              disabled={loading}
            />
          </div>
          <div className="input-group">
            <input
              type="text"
              placeholder="Короткий код (опционально)"
              value={customCode}
              onChange={(e) => setCustomCode(e.target.value)}
              pattern="[a-zA-Z0-9_-]{3,30}"
              title="3-30 символов: латиница, цифры, дефис, подчёркивание"
              className="linklist-input"
              disabled={loading}
            />
          </div>
          <button type="submit" disabled={loading} className="linklist-button primary">
            {loading ? 'Создание...' : 'Сократить'}
          </button>
        </form>

        {loading && <div className="linklist-loader">Загрузка...</div>}

        {!loading && links.length === 0 && (
          <div className="linklist-empty">У вас пока нет сокращённых ссылок</div>
        )}

        {links.length > 0 && (
          <ul className="linklist-list">
            {links.map((link) => (
              <li key={link.id} className="linklist-item">
                <div className="link-info">
                  <div className="link-short">
                    <span className="link-code">{link.short_code}</span>
                    <button
                      className="icon-button copy"
                      onClick={() => copyToClipboard(link.short_code)}
                      title="Копировать"
                    >
                      📋
                    </button>
                    <a
                      href={`${API_BASE_URL}/${link.short_code}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="link-open"
                      title="Открыть ссылку в новой вкладке"
                    >
                      🔗
                    </a>
                  </div>
                  <div className="link-original" title={link.original_url}>
                    {link.original_url.length > 40
                      ? link.original_url.substring(0, 40) + '…'
                      : link.original_url}
                  </div>
                  <div className="link-stats">
                    <span className="clicks">👁 {link.clicks}</span>
                  </div>
                </div>
                <div className="link-actions">
                  <button
                    className="icon-button edit"
                    onClick={() => handleEditClick(link.short_code, link.original_url)}
                    title="Редактировать"
                  >
                    ✏️
                  </button>
                  <button
                    className="icon-button delete"
                    onClick={() => handleDelete(link.short_code)}
                    title="Удалить"
                  >
                    🗑️
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Модальное окно редактирования */}
      {editModal.open && (
        <div className="modal-overlay" onClick={() => setEditModal({ open: false })}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Редактировать ссылку</h3>
            <form onSubmit={handleEditSubmit}>
              <input
                type="url"
                name="newUrl"
                defaultValue={editModal.currentUrl}
                required
                className="linklist-input"
                autoFocus
              />
              <div className="modal-actions">
                <button type="submit" className="linklist-button primary">Сохранить</button>
                <button
                  type="button"
                  className="linklist-button secondary"
                  onClick={() => setEditModal({ open: false })}
                >
                  Отмена
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default LinkList;