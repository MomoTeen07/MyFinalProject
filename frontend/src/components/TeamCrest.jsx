import { useEffect, useState } from 'react';

export default function TeamCrest({ src, name, small = false }) {
  const [failed, setFailed] = useState(false);

  useEffect(() => setFailed(false), [src]);

  const className = small ? 'crest small' : 'crest';
  if (src && !failed) {
    return <img className={`${className} team-crest`} src={src} alt={`Écusson de ${name}`} loading="lazy" onError={() => setFailed(true)} />;
  }
  return <span className={className} aria-hidden="true">⚽</span>;
}
