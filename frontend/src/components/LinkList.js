import React, { useEffect, useState } from 'react';
import { getLinks, createLink } from '../api';

function LinkList() {
  const [links, setLinks] = useState([]);
  const [newUrl, setNewUrl] = useState('');

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
      await createLink(newUrl);
      setNewUrl(''); // очищаем поле
      fetchLinks(); // обновляем список
    } catch (err) {
      alert('Ошибка при создании ссылки');
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