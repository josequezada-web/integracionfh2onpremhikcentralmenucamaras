import React, {useEffect, useRef, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {createPortal} from 'react-dom';
import {Activity, ArrowUpRight, Camera, Check, CircleAlert, Clock3, Radio, RefreshCw, Search, X} from 'lucide-react';
import './dashboard.css';

const identity = e => e ? `${e.timestamp}-${e.camera_id}` : null;
const time = value => value || 'Sin eventos';
const coordinates = e => `${e.latitude ?? '—'}, ${e.longitude ?? '—'}`;
function Badge({ok, children}) { return <span className={`badge ${ok === true ? 'good' : ok === false ? 'bad' : ''}`}><span className="dot"/>{children}</span>; }
function App() {
  const [data, setData] = useState(null), [error, setError] = useState(false), [busy, setBusy] = useState(false);
  const [updated, setUpdated] = useState(null), [query, setQuery] = useState(''), [filter, setFilter] = useState('all');
  const [selected, setSelected] = useState(null), [notice, setNotice] = useState(null);
  const previous = useRef(undefined), request = useRef(null), closeButton = useRef(null), opener = useRef(null);
  async function refresh() {
    if (request.current) return;
    const controller = new AbortController(); request.current = controller; setBusy(true);
    const timeout = setTimeout(() => controller.abort(), 10000);
    try {
      const response = await fetch('/api/status', {signal: controller.signal, cache: 'no-store'});
      if (!response.ok) throw new Error('status');
      const next = await response.json();
      if (!Array.isArray(next.eventos) || !next.camaras || typeof next.middleware_status !== 'boolean') throw new Error('format');
      const id = identity(next.ultimo_evento);
      if (previous.current !== undefined && id && previous.current !== id) setNotice(next.ultimo_evento);
      previous.current = id; setData(next); setError(false); setUpdated(new Date());
    } catch { if (!controller.signal.aborted || request.current) setError(true); }
    finally { clearTimeout(timeout); request.current = null; setBusy(false); }
  }
  useEffect(() => { refresh(); const interval = setInterval(refresh, 5000); return () => {clearInterval(interval); request.current?.abort();}; }, []);
  useEffect(() => { if (!notice) return; const timeout = setTimeout(() => setNotice(null), 8000); return () => clearTimeout(timeout); }, [notice]);
  useEffect(() => {
    if (!selected) return;
    opener.current = document.activeElement; closeButton.current?.focus();
    const handler = e => { if (e.key === 'Escape') setSelected(null); if (e.key === 'Tab') {e.preventDefault(); closeButton.current?.focus();} };
    document.addEventListener('keydown', handler);
    return () => {document.removeEventListener('keydown', handler); opener.current?.focus();};
  }, [selected]);
  const last = data?.ultimo_evento;
  const cameras = Object.entries(data?.camaras || {}).filter(([id,c]) => `${id} ${c.name}`.toLocaleLowerCase().includes(query.toLocaleLowerCase()));
  const events = (data?.eventos || []).filter(e => filter === 'all' || (filter === 'success' ? e.fh2_status === 200 : e.fh2_status !== 200));
  return <>
    {createPortal(<Badge ok={error ? false : data ? data.middleware_status : undefined}>{error ? 'Sin conexión' : data ? data.middleware_status ? 'Middleware en línea' : 'Middleware sin conexión' : 'Conectando'}</Badge>, document.getElementById('header-status'))}
    <div className="page-heading"><div><div className="eyebrow">CONTROL Y MONITOREO</div><h1>Vista general<span>.</span></h1><p>Tu operación, en tiempo real.</p></div><button onClick={refresh} disabled={busy}><RefreshCw size={16} className={busy ? 'spin' : ''}/>{busy ? 'Actualizando' : 'Actualizar'}</button></div>
    {error && <div className="error-banner" role="alert"><CircleAlert size={18}/>{data ? 'No se pudo actualizar. Se muestran los últimos datos recibidos.' : 'No se pudo conectar con el dashboard. Vuelve a intentar con Actualizar.'}</div>}
    <section className="stats" aria-label="Resumen de hoy">{[
      ['Eventos hoy',data?.events_today,Activity,'blue','Actividad recibida'],['Exitosos hoy',data?.success_today,Check,'green','Respuesta 200 de FlightHub'],['Errores hoy',data?.errors_today,CircleAlert,'orange','Requieren revisión'],['Cámaras',data?.camera_count,Camera,'purple','Destinos configurados']
    ].map(([label,value,Icon,color,caption]) => <div className="stat" key={label}><div className="stat-top">{label}<span className={`icon-box ${color}`}><Icon size={19}/></span></div><strong>{value ?? '—'}</strong><small>{caption}</small></div>)}</section>
    <div className="overview-grid"><section className="panel latest"><div className="panel-heading"><h2><Radio size={17}/>Último evento</h2><span className="eyebrow">ACTIVIDAD RECIENTE</span></div>{last ? <><div className="event-main"><span className="event-icon"><Camera size={29}/></span><div><span className="muted small">{last.camera_id}</span><h3>{last.camera_name}</h3><Badge ok={last.fh2_status === 200}>{last.fh2_status === 200 ? 'Workflow enviado' : 'Error de workflow'}</Badge></div></div><div className="event-bottom"><span><Clock3 size={14}/>{time(last.timestamp)}</span><button className="text-button" onClick={() => setSelected(last)}>Ver detalle<ArrowUpRight size={16}/></button></div></> : <div className="empty"><Radio size={28}/><h3>{data ? 'A la espera del primer evento' : 'Cargando actividad…'}</h3><span>Los eventos aparecerán aquí automáticamente.</span></div>}</section>
    <section className="panel health"><div className="panel-heading"><h2><Activity size={17}/>Estado de integración</h2></div><div className="health-row"><span>Middleware</span><Badge ok={error ? false : data?.middleware_status}>{error ? 'Sin conexión' : data ? data.middleware_status ? 'En línea' : 'Sin conexión' : 'Consultando'}</Badge></div><div className="health-row"><span>Última respuesta FH2</span><Badge ok={last ? last.fh2_status === 200 : undefined}>{last ? String(last.fh2_status) : 'Sin datos'}</Badge></div><div className="health-row"><span>Actualizado</span><span className="mono">{updated?.toLocaleTimeString('es-MX') || '—'}</span></div><a className="settings-link" href="/settings">Abrir configuración<ArrowUpRight size={15}/></a></section></div>
    <section className="camera-section"><div className="section-heading"><h2>Cámaras <span className="count">{data?.camera_count ?? '—'}</span></h2><div className="section-actions"><label className="search"><Search size={16}/><input aria-label="Buscar cámaras" placeholder="Buscar cámara…" value={query} onChange={e => setQuery(e.target.value)}/></label><a className="text-button" href="/cameras">Administrar<ArrowUpRight size={16}/></a></div></div><div className="camera-grid">{cameras.map(([id,c]) => <article className={`camera-card ${notice?.camera_id === id ? 'highlight' : ''}`} key={id}><div className="camera-top"><span className="camera-symbol"><Camera size={20}/></span><Badge ok={c.last_event ? c.last_event.fh2_status === 200 : undefined}>{c.last_event ? c.last_event.fh2_status === 200 ? 'Último envío OK' : 'Error de envío' : 'Sin eventos'}</Badge></div><h3>{c.name}</h3><span className="camera-id">{id}</span><div className="coordinates">{coordinates(c)}</div><div className="camera-footer"><span><Clock3 size={13}/>{c.last_event ? time(c.last_event.timestamp) : 'Sin actividad registrada'}</span>{c.last_event && <button className="icon-button" aria-label={`Ver último evento de ${c.name}`} onClick={() => setSelected(c.last_event)}><ArrowUpRight size={17}/></button>}</div></article>)}</div>{!cameras.length && <div className="empty panel">{!data ? 'Cargando cámaras…' : query ? 'No hay cámaras que coincidan con tu búsqueda.' : <span>No hay cámaras configuradas. <a href="/cameras">Agregar cámara</a></span>}</div>}</section>
    <section className="panel events"><div className="section-heading"><h2>Eventos recientes</h2><div className="filters" aria-label="Filtrar eventos">{[['all','Todos'],['success','Exitosos'],['error','Errores']].map(([value,label]) => <button key={value} aria-pressed={filter === value} className={filter === value ? 'selected' : ''} onClick={() => setFilter(value)}>{label}</button>)}</div></div><div className="table-scroll"><table><thead><tr><th>Fecha y hora</th><th>Cámara</th><th>Destino</th><th>Resultado</th><th><span className="sr-only">Detalle</span></th></tr></thead><tbody>{events.map((e,i) => <tr key={`${identity(e)}-${i}`}><td className="mono">{e.timestamp}</td><td><strong>{e.camera_name}</strong><small>{e.camera_id}</small></td><td className="mono muted">{coordinates(e)}</td><td><Badge ok={e.fh2_status === 200}>{e.fh2_status === 200 ? 'Exitoso' : 'Error'}</Badge></td><td><button className="icon-button" aria-label={`Ver evento de ${e.camera_name} del ${e.timestamp}`} onClick={() => setSelected(e)}><ArrowUpRight size={17}/></button></td></tr>)}</tbody></table></div>{!events.length && <div className="empty">{!data ? 'Cargando eventos…' : 'No hay eventos para mostrar.'}</div>}<div className="table-footer">Últimos {data?.eventos.length ?? 0} eventos registrados<span>Actualización automática · 5 s</span></div></section>

    {notice && <div className="toast" role="status"><Radio size={20}/><div><strong>Nuevo evento · {notice.camera_name}</strong><small>{notice.fh2_status === 200 ? 'Workflow enviado' : 'Error al enviar workflow'}</small></div><button className="icon-button" aria-label="Cerrar notificación" onClick={() => setNotice(null)}><X size={18}/></button></div>}
    {selected && <div className="modal-backdrop" onClick={() => setSelected(null)}><section className="modal panel" role="dialog" aria-modal="true" aria-labelledby="event-title" onClick={e => e.stopPropagation()}><div className="panel-heading"><h2 id="event-title">Detalle del evento</h2><button ref={closeButton} className="icon-button" aria-label="Cerrar detalle" onClick={() => setSelected(null)}><X size={20}/></button></div><h3>{selected.camera_name}</h3><Badge ok={selected.fh2_status === 200}>{selected.fh2_status === 200 ? 'Workflow enviado' : 'Error de workflow'}</Badge><dl>{[['Cámara',selected.camera_id],['Fecha',selected.timestamp],['Destino',coordinates(selected)],['Respuesta FlightHub',selected.fh2_status],['Workflow UUID',selected.workflow_uuid || 'No registrado']].map(([label,value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl></section></div>}
  </>;
}
createRoot(document.getElementById('dashboard-root')).render(<App/>);
