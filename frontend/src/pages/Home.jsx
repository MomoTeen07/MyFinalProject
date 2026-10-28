import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <section className="hero">
      <div>
        <span className="eyebrow">PROJET FINAL QA</span>
        <h1>Le football,<br /><strong>simplement.</strong></h1>
        <p>Consulte les grands championnats européens, les classements, les matchs et garde tes équipes favorites.</p>
        <Link className="primary" to="/championships">Explorer les championnats →</Link>
      </div>
      <div className="hero-card"><div aria-hidden="true">⚽</div><h2>Football QA</h2><p>Une application pour découvrir les championnats, consulter les classements et enregistrer tes équipes préférées.</p></div>
    </section>
  );
}
