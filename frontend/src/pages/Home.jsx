import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';

const relativeFormatter = new Intl.RelativeTimeFormat('fr', { numeric: 'auto' });

function relativeTime(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  const minutes = Math.round((date.getTime() - Date.now()) / 60000);
  if (Math.abs(minutes) < 60) return relativeFormatter.format(minutes, 'minute');
  const hours = Math.round(minutes / 60);
  if (Math.abs(hours) < 24) return relativeFormatter.format(hours, 'hour');
  return relativeFormatter.format(Math.round(hours / 24), 'day');
}

export default function Home() {
  const [news, setNews] = useState(null);
  const [status, setStatus] = useState('loading');
  const [error, setError] = useState('');
  const [attempt, setAttempt] = useState(0);
  const [press, setPress] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    setStatus('loading');
    setError('');

    api('/api/football/news?days=7&limit=5', { signal: controller.signal })
      .then((payload) => {
        setNews(payload);
        setStatus('success');
      })
      .catch((requestError) => {
        if (requestError.name === 'AbortError') return;
        setError(requestError.message);
        setStatus('error');
      });

    return () => controller.abort();
  }, [attempt]);

  useEffect(() => {
    // Bloc non bloquant : toute erreur masque simplement la section.
    const controller = new AbortController();

    api('/api/football/press?limit=5', { signal: controller.signal })
      .then((payload) => setPress(payload))
      .catch(() => setPress(null));

    return () => controller.abort();
  }, []);

  const items = news?.items || [];
  const pressItems = press?.available ? press.items : [];

  return (
    <>
      <section className="hero">
        <div>
          <span className="eyebrow">PROJET FINAL QA</span>
          <h1>Le football,<br /><strong>simplement.</strong></h1>
          <p>Consulte les grands championnats européens, les classements, les matchs et garde tes équipes favorites.</p>
          <Link className="primary" to="/championships">Explorer les championnats →</Link>
        </div>
        <div className="hero-card"><div aria-hidden="true">⚽</div><h2>Football QA</h2><p>Une application pour découvrir les championnats, consulter les classements et enregistrer tes équipes préférées.</p></div>
      </section>

      <section className="news" aria-labelledby="news-title">
        <div className="news-head">
          <div>
            <span className="eyebrow">ACTUALITÉS</span>
            <h2 id="news-title">Résultats récents</h2>
          </div>
          <span className="muted">
            {news?.window?.days ? `Les ${news.window.days} derniers jours` : 'Derniers jours'}
          </span>
        </div>
        {status === 'loading' && <p className="notice" role="status">Chargement des actualités…</p>}
        {status === 'error' && (
          <div className="error" role="alert">Impossible de charger les actualités : {error}</div>
        )}
        {status === 'error' && (
          <button className="primary small" onClick={() => setAttempt((value) => value + 1)}>Réessayer</button>
        )}
        {status === 'success' && items.length === 0 && (
          <p className="empty">Aucun résultat récent disponible.</p>
        )}
        {status === 'success' && items.length > 0 && (
          <ul className="news-list">
            {items.map((item) => (
              <li className="card news-item" key={item.id}>
                <div className="news-meta">
                  <span className="eyebrow">{item.competition.name}</span>
                  <time dateTime={item.utcDate || undefined}>{relativeTime(item.utcDate)}</time>
                  <Link className="news-link" to={`/matches/${item.id}`}>Voir le match</Link>
                </div>
                <p className="news-headline">{item.headline}</p>
                <span className="news-score" aria-label={`Score ${item.score.home} à ${item.score.away}`}>
                  {item.score.home} – {item.score.away}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      {pressItems.length > 0 && (
        <section className="press" aria-labelledby="press-title">
          <div className="news-head">
            <div>
              <span className="eyebrow">PRESSE</span>
              <h2 id="press-title">À la une</h2>
            </div>
            <span className="muted">Source : {press.source.name}</span>
          </div>
          <ul className="news-list">
            {pressItems.map((item) => (
              <li className="card news-item press-item" key={item.link}>
                <a
                  className="press-link"
                  href={item.link}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {item.title}
                  <span aria-hidden="true"> ↗</span>
                </a>
                {item.publishedAt && (
                  <time dateTime={item.publishedAt}>{relativeTime(item.publishedAt)}</time>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}
    </>
  );
}
