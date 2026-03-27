import React, { useEffect, useState } from 'react';
import { getLinks, createLink } from '../api';

function LinkList() {
  const [links, setLinks] = useState([]);
  const [newUrl, setNewUrl] = useState('');
  const [customCode, setCustomCode] = useState(''); 


  // Загружаем список ссылок при монтировании компонента
  const fetchLinks = async () => {
    try {
      const response = await getLinks();
      setLinks(response.data);
    } catch (err) {
      alert('Не удалось загрузить ссылки');
    }
  };

  useEffect(() => {
    fetchLinks();
  }, []);

  // Создание новой ссылки
const handleCreate = async (e) => {
  e.preventDefault();
  try {
    await createLink(newUrl, customCode || undefined);
    setNewUrl('');
    setCustomCode('');
    fetchLinks();
  } catch (err) {
    if (err.response && err.response.status === 422) {
      const detail = err.response.data.detail;
      if (detail && detail[0] && detail[0].msg) {
        alert(`Ошибка: ${detail[0].msg}`);
      } else {
        alert('Некорректный формат кастомного кода');
      }
    } else {
      alert('Ошибка при создании ссылки: ' + (err.response?.data?.detail || err.message));
    }
  }
};

  return (
    <div>
      <h2>Мои ссылки</h2>
      <form onSubmit={handleCreate}>
        <input
          type="url"
          placeholder="Введите длинный URL"
          value={newUrl}
          onChange={(e) => setNewUrl(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Желаемый короткий код (необязательно)"
          value={customCode}
          onChange={(e) => setCustomCode(e.target.value)}
          pattern="[a-zA-Z0-9_-]{3,30}"
          title="3-30 символов, только латиница, цифры, дефис, подчёркивание. Нельзя начинать или заканчивать на - или _."
        />

        <button type="submit">Сократить</button>
      </form>
      <ul>
        {links.map(link => (
          <li key={link.id}>
            <a href={`http://localhost:8000/${link.short_code}`} target="_blank" rel="noopener noreferrer">
              {link.short_code}
            </a> → {link.original_url} (кликов: {link.clicks})
          </li>
        ))}
      </ul>
    </div>
  );
}

export default LinkList;