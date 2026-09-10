import {useEffect,useState} from 'react';
import {Link} from 'react-router-dom';
import {api} from '../api/client';

export default function Championships(){
  const [data,setData]=useState([]);
  const [status,setStatus]=useState('loading');
  const [error,setError]=useState('');

  useEffect(()=>{
    let active=true;
    api('/api/football/leagues')
      .then(leagues=>{
        if(!active)return;
        setData(Array.isArray(leagues)?leagues:[]);
        setStatus('success');
      })
      .catch(requestError=>{
        if(!active)return;
        setError(requestError.message||'Impossible de charger les championnats.');
        setStatus('error');
      });
    return()=>{active=false};
  },[]);

  return <section>
    <span className="eyebrow">FOOTBALL</span>
    <h1>Championnats</h1>
    <p className="muted">Choisis un championnat pour consulter son classement et ses matchs.</p>
    {status==='loading'&&<p className="notice" data-testid="championships-loading">Chargement des championnats…</p>}
    {status==='error'&&<div className="error" data-testid="championships-error">Impossible de charger les championnats : {error}</div>}
    {status==='success'&&data.length===0&&<div className="empty" data-testid="championships-empty"><div>⚽</div><p>Aucun championnat disponible</p></div>}
    {status==='success'&&data.length>0&&<div className="grid" data-testid="championship-list">{data.map(l=><Link className="card league" data-testid="championship-card" key={l.code} to={`/championships/${l.code}`}><span className="league-icon">🏆</span><div><h3>{l.name}</h3><p>{l.country}</p></div><span>→</span></Link>)}</div>}
  </section>;
}
