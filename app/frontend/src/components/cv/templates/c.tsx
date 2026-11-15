import { Tr } from '../lang';
import { Bullets, Contacts, Level, Photo, Row, hasAny, tint, type CvProps, ProjDesc, linkText } from '../parts';
import { useLevels } from '../levels';
import { dateRange, lines } from '@/lib/cv/types';

const initials = (n: string) => n.trim().split(/\s+/).slice(-2).map((w) => w[0]?.toUpperCase() || '').join('');
const Dates = ({ a, b }: { a: string; b: string }) => <span style={{ color: '#6b7280', fontSize: '0.9em', whiteSpace: 'nowrap' }}>{dateRange(a, b)}</span>;

/** 11. Soft: light tinted left column, rounded photo, pill headings. */
export function Soft({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  const T = (t: string) => <div style={{ fontWeight: 800, fontSize: '1em', color: accent, margin: '0 0 0.7em', display: 'flex', alignItems: 'center', gap: '0.5em' }}><span style={{ width: '0.7em', height: '0.7em', borderRadius: '50%', background: accent }} /><Tr t={t} /></div>;
  return (
    <div style={{ display: 'flex', minHeight: 'inherit', lineHeight: 1.5, color: '#1f2937' }}>
      <aside style={{ width: '33%', background: tint(accent, 0.09), padding: '2.6em 1.6em', display: 'flex', flexDirection: 'column', gap: '1.6em' }}>
        {showPhoto && d.photo && <Photo src={d.photo} size={9} radius="1.8em" style={{ alignSelf: 'center' }} />}
        <section>{T('Liên hệ')}<Contacts d={d} color="#374151" iconColor={accent} /></section>
        {h.skills && <section>{T('Kỹ năng')}<div style={{ display: 'flex', flexDirection: 'column', gap: '0.7em' }}>{d.skills.map((s) => <div key={s.id}><div style={{ fontSize: '0.93em', fontWeight: 600, marginBottom: '0.25em' }}>{s.name}</div><Level level={s.level} kind="bar" color={accent} track={tint(accent, 0.2)} /></div>)}</div></section>}
        {h.lang && <section>{T('Ngoại ngữ')}{d.languages.map((l) => <div key={l.id} style={{ marginBottom: '0.4em' }}><b>{l.name}</b>{l.level && <div style={{ color: '#6b7280', fontSize: '0.92em' }}>{l.level}</div>}</div>)}</section>}
        {h.awards && <section>{T('Thành tích')}<Bullets text={d.awards} /></section>}
      </aside>
      <main style={{ flex: 1, padding: '2.6em 2.2em' }}>
        <div style={{ fontSize: '2.5em', fontWeight: 800, margin: 0, lineHeight: 1.1, color: '#0f172a' }}>{d.name}</div>
        <div style={{ display: 'inline-block', marginTop: '0.6em', background: accent, color: '#fff', borderRadius: '2em', padding: '0.25em 1em', fontWeight: 700 }}>{d.title}</div>
        {d.summary && <p style={{ margin: '1.2em 0 0', color: '#4b5563' }}>{d.summary}</p>}
        {h.exp && <section style={{ marginTop: '1.7em' }}>{T('Kinh nghiệm')}{d.experience.map((e) => <Row key={e.id} style={{ marginBottom: '1.1em' }}><div style={{ display: 'flex', justifyContent: 'space-between', gap: '1em' }}><b style={{ fontSize: '1.07em' }}>{e.role}</b><Dates a={e.from} b={e.to} /></div><div style={{ color: accent, fontWeight: 600 }}>{e.company}</div><Bullets text={e.desc} /></Row>)}</section>}
        {h.edu && <section style={{ marginTop: '1.4em' }}>{T('Học vấn')}{d.education.map((e) => <Row key={e.id} style={{ marginBottom: '0.8em' }}><div style={{ display: 'flex', justifyContent: 'space-between', gap: '1em' }}><b>{e.school}</b><Dates a={e.from} b={e.to} /></div><div>{e.degree}</div></Row>)}</section>}
        {h.proj && <section style={{ marginTop: '1.4em' }}>{T('Dự án')}{d.projects.map((p) => <Row key={p.id} style={{ marginBottom: '0.6em' }}><b>{p.name}</b><div style={{ color: '#4b5563' }}><ProjDesc p={p} /></div></Row>)}</section>}
      </main>
    </div>
  );
}

/** 12. Split: coloured name block on the left of the header, contacts on the right. */
export function Split({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  const T = (t: string) => <div style={{ fontWeight: 800, fontSize: '1.05em', textTransform: 'uppercase', letterSpacing: '0.1em', color: '#111827', borderLeft: `0.3em solid ${accent}`, paddingLeft: '0.6em', margin: '0 0 0.8em' }}><Tr t={t} /></div>;
  return (
    <div style={{ lineHeight: 1.5, color: '#1f2937' }}>
      <header style={{ display: 'flex' }}>
        <div style={{ flex: 1.5, background: accent, color: '#fff', padding: '2.4em 2.4em' }}>
          <div style={{ fontSize: '2.6em', fontWeight: 800, margin: 0, lineHeight: 1.08 }}>{d.name}</div>
          <div style={{ fontSize: '1.15em', marginTop: '0.4em', opacity: 0.95 }}>{d.title}</div>
        </div>
        <div style={{ flex: 1, background: '#111827', color: '#e5e7eb', padding: '2em 1.8em', display: 'flex', alignItems: 'center', gap: '1.2em' }}>
          {showPhoto && d.photo && <Photo src={d.photo} size={5.4} />}
          <Contacts d={d} color="#e5e7eb" iconColor={accent} size={0.88} />
        </div>
      </header>
      <div style={{ padding: '2em 2.8em 2.6em' }}>
        {d.summary && <section style={{ marginBottom: '1.6em' }}>{T('Giới thiệu')}<p style={{ margin: 0, color: '#4b5563' }}>{d.summary}</p></section>}
        {h.exp && <section style={{ marginBottom: '1.5em' }}>{T('Kinh nghiệm')}{d.experience.map((e) => <Row key={e.id} style={{ marginBottom: '1.1em' }}><div style={{ display: 'flex', justifyContent: 'space-between', gap: '1em' }}><span><b style={{ fontSize: '1.07em' }}>{e.role}</b> · <span style={{ color: accent, fontWeight: 600 }}>{e.company}</span></span><Dates a={e.from} b={e.to} /></div><Bullets text={e.desc} /></Row>)}</section>}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2em' }}>
          {h.edu && <section>{T('Học vấn')}{d.education.map((e) => <Row key={e.id} style={{ marginBottom: '0.8em' }}><b>{e.school}</b><div>{e.degree}</div><Dates a={e.from} b={e.to} /></Row>)}</section>}
          {h.skills && <section>{T('Kỹ năng')}<div style={{ display: 'flex', flexDirection: 'column', gap: '0.55em' }}>{d.skills.map((s) => <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}><span>{s.name}</span><Level level={s.level} kind="dots" color={accent} track="#d1d5db" /></div>)}</div></section>}
          {h.lang && <section>{T('Ngoại ngữ')}{d.languages.map((l) => <div key={l.id}><b>{l.name}</b>{l.level && <span style={{ color: '#6b7280' }}> · {l.level}</span>}</div>)}</section>}
          {h.proj && <section>{T('Dự án')}{d.projects.map((p) => <Row key={p.id} style={{ marginBottom: '0.5em' }}><b>{p.name}</b><div style={{ color: '#4b5563', fontSize: '0.95em' }}><ProjDesc p={p} /></div></Row>)}</section>}
          {h.awards && <section>{T('Thành tích')}<Bullets text={d.awards} /></section>}
        </div>
      </div>
    </div>
  );
}

/** 13. Midnight: a dark page with light text and glowing accents. */
export function Midnight({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  const T = (t: string) => <div style={{ fontWeight: 800, fontSize: '0.98em', textTransform: 'uppercase', letterSpacing: '0.16em', color: accent, margin: '0 0 0.8em' }}><Tr t={t} /></div>;
  return (
    <div style={{ minHeight: 'inherit', background: '#0b1120', color: '#cbd5e1', lineHeight: 1.5, padding: '2.8em' }}>
      <header style={{ display: 'flex', alignItems: 'center', gap: '1.6em', paddingBottom: '1.5em', borderBottom: `0.12em solid ${accent}` }}>
        {showPhoto && d.photo && <Photo src={d.photo} size={7.6} style={{ boxShadow: `0 0 0 0.25em ${accent}` }} />}
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '2.7em', fontWeight: 800, margin: 0, lineHeight: 1.08, color: '#fff' }}>{d.name}</div>
          <div style={{ fontSize: '1.15em', color: accent, fontWeight: 600, margin: '0.3em 0 0.9em' }}>{d.title}</div>
          <Contacts d={d} row color="#94a3b8" iconColor={accent} size={0.9} />
        </div>
      </header>
      <div style={{ display: 'flex', gap: '2.2em', marginTop: '1.8em' }}>
        <main style={{ flex: 1.8 }}>
          {d.summary && <section style={{ marginBottom: '1.5em' }}>{T('Giới thiệu')}<p style={{ margin: 0 }}>{d.summary}</p></section>}
          {h.exp && <section style={{ marginBottom: '1.5em' }}>{T('Kinh nghiệm')}{d.experience.map((e) => <Row key={e.id} style={{ marginBottom: '1.1em' }}><div style={{ display: 'flex', justifyContent: 'space-between', gap: '1em' }}><b style={{ color: '#fff', fontSize: '1.07em' }}>{e.role}</b><span style={{ color: '#64748b', fontSize: '0.9em', whiteSpace: 'nowrap' }}>{dateRange(e.from, e.to)}</span></div><div style={{ color: accent }}>{e.company}</div><Bullets text={e.desc} /></Row>)}</section>}
          {h.proj && <section>{T('Dự án')}{d.projects.map((p) => <Row key={p.id} style={{ marginBottom: '0.6em' }}><b style={{ color: '#fff' }}>{p.name}</b><div><ProjDesc p={p} /></div></Row>)}</section>}
        </main>
        <aside style={{ flex: 1 }}>
          {h.skills && <section style={{ marginBottom: '1.5em' }}>{T('Kỹ năng')}<div style={{ display: 'flex', flexDirection: 'column', gap: '0.7em' }}>{d.skills.map((s) => <div key={s.id}><div style={{ fontSize: '0.93em', marginBottom: '0.25em', color: '#e2e8f0' }}>{s.name}</div><Level level={s.level} kind="bar" color={accent} track="rgba(255,255,255,.12)" /></div>)}</div></section>}
          {h.edu && <section style={{ marginBottom: '1.5em' }}>{T('Học vấn')}{d.education.map((e) => <Row key={e.id} style={{ marginBottom: '0.8em' }}><b style={{ color: '#fff' }}>{e.school}</b><div>{e.degree}</div><div style={{ color: '#64748b', fontSize: '0.9em' }}>{dateRange(e.from, e.to)}</div></Row>)}</section>}
          {h.lang && <section style={{ marginBottom: '1.5em' }}>{T('Ngoại ngữ')}{d.languages.map((l) => <div key={l.id}><b style={{ color: '#fff' }}>{l.name}</b>{l.level && <span> · {l.level}</span>}</div>)}</section>}
          {h.awards && <section>{T('Thành tích')}<Bullets text={d.awards} /></section>}
        </aside>
      </div>
    </div>
  );
}

/** 14. Ledger: dates in a left column, content on the right; very easy to scan. */
export function Ledger({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  const Sec = ({ t, children }: { t: string; children: React.ReactNode }) => <section style={{ marginTop: '1.5em' }}><div style={{ fontWeight: 800, fontSize: '1.1em', color: accent, paddingBottom: '0.3em', borderBottom: '0.08em solid #d1d5db', marginBottom: '0.8em' }}><Tr t={t} /></div>{children}</section>;
  const Item = ({ date, children }: { date: React.ReactNode; children: React.ReactNode }) => <Row style={{ display: 'grid', gridTemplateColumns: '7.5em 1fr', gap: '1.2em', marginBottom: '0.95em' }}><div style={{ color: '#6b7280', fontSize: '0.9em', fontWeight: 600, paddingTop: '0.15em' }}>{date}</div><div>{children}</div></Row>;
  return (
    <div style={{ padding: '2.8em 3em', lineHeight: 1.5, color: '#1f2937' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1.5em' }}>
        <div><div style={{ fontSize: '2.5em', fontWeight: 800, margin: 0, lineHeight: 1.1, color: '#0f172a' }}>{d.name}</div><div style={{ fontSize: '1.15em', color: accent, fontWeight: 600, marginTop: '0.3em' }}>{d.title}</div></div>
        {showPhoto && d.photo && <Photo src={d.photo} size={6.8} radius="0.6em" />}
      </header>
      <div style={{ marginTop: '1em' }}><Contacts d={d} row color="#4b5563" iconColor={accent} size={0.92} /></div>
      {d.summary && <p style={{ margin: '1.2em 0 0', color: '#4b5563' }}>{d.summary}</p>}
      {h.exp && <Sec t="Kinh nghiệm làm việc">{d.experience.map((e) => <Item key={e.id} date={dateRange(e.from, e.to)}><b style={{ fontSize: '1.05em' }}>{e.role}</b><div style={{ color: '#6b7280' }}>{e.company}</div><Bullets text={e.desc} /></Item>)}</Sec>}
      {h.edu && <Sec t="Học vấn">{d.education.map((e) => <Item key={e.id} date={dateRange(e.from, e.to)}><b>{e.school}</b><div>{e.degree}</div>{e.desc && <div style={{ color: '#6b7280', fontSize: '0.95em' }}>{e.desc}</div>}</Item>)}</Sec>}
      {h.skills && <Sec t="Kỹ năng"><Item date={<Tr t="Chuyên môn" />}><div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4em' }}>{d.skills.map((s) => <span key={s.id} style={{ background: tint(accent, 0.1), borderRadius: '0.3em', padding: '0.15em 0.65em', fontWeight: 500 }}>{s.name}</span>)}</div></Item>{h.lang && <Item date="Ngoại ngữ">{d.languages.map((l) => `${l.name}${l.level ? ` (${l.level})` : ''}`).join(' · ')}</Item>}</Sec>}
      {h.proj && <Sec t="Dự án">{d.projects.map((p) => <Item key={p.id} date=""><b>{p.name}</b><div style={{ color: '#4b5563' }}><ProjDesc p={p} /></div></Item>)}</Sec>}
      {h.awards && <Sec t="Thành tích"><Item date="">{lines(d.awards).map((l, i) => <div key={i}>• {linkText(l)}</div>)}</Item></Sec>}
    </div>
  );
}

/** 15. Cards: soft grey page, every section is a white rounded card. */
export function Cards({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  const Card = ({ t, children, style }: { t: string; children: React.ReactNode; style?: React.CSSProperties }) => <section style={{ background: '#fff', borderRadius: '1em', padding: '1.2em 1.4em', boxShadow: '0 1px 3px rgba(15,23,42,.08)', ...style }}><div style={{ fontWeight: 800, fontSize: '1em', color: accent, margin: '0 0 0.7em' }}><Tr t={t} /></div>{children}</section>;
  return (
    <div style={{ minHeight: 'inherit', background: '#eef1f6', padding: '1.8em', lineHeight: 1.5, color: '#1f2937', display: 'flex', flexDirection: 'column', gap: '1em' }}>
      <header style={{ background: accent, color: '#fff', borderRadius: '1.1em', padding: '1.8em 2em', display: 'flex', alignItems: 'center', gap: '1.5em' }}>
        {showPhoto && d.photo && <Photo src={d.photo} size={7} style={{ border: '0.22em solid rgba(255,255,255,.6)' }} />}
        <div style={{ flex: 1 }}><div style={{ fontSize: '2.4em', fontWeight: 800, margin: 0, lineHeight: 1.1 }}>{d.name}</div><div style={{ fontSize: '1.1em', opacity: 0.95, margin: '0.3em 0 0.8em' }}>{d.title}</div><Contacts d={d} row color="#fff" size={0.88} /></div>
      </header>
      {d.summary && <Card t="Giới thiệu"><p style={{ margin: 0, color: '#4b5563' }}>{d.summary}</p></Card>}
      <div style={{ display: 'flex', gap: '1em', alignItems: 'flex-start' }}>
        <div style={{ flex: 1.8, display: 'flex', flexDirection: 'column', gap: '1em' }}>
          {h.exp && <Card t="Kinh nghiệm">{d.experience.map((e) => <Row key={e.id} style={{ marginBottom: '0.9em' }}><div style={{ display: 'flex', justifyContent: 'space-between', gap: '1em' }}><b>{e.role}</b><Dates a={e.from} b={e.to} /></div><div style={{ color: accent, fontWeight: 600 }}>{e.company}</div><Bullets text={e.desc} /></Row>)}</Card>}
          {h.proj && <Card t="Dự án">{d.projects.map((p) => <Row key={p.id} style={{ marginBottom: '0.5em' }}><b>{p.name}</b><div style={{ color: '#4b5563' }}><ProjDesc p={p} /></div></Row>)}</Card>}
        </div>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1em' }}>
          {h.edu && <Card t="Học vấn">{d.education.map((e) => <Row key={e.id} style={{ marginBottom: '0.7em' }}><b>{e.school}</b><div style={{ fontSize: '0.95em' }}>{e.degree}</div><Dates a={e.from} b={e.to} /></Row>)}</Card>}
          {h.skills && <Card t="Kỹ năng"><div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4em' }}>{d.skills.map((s) => <span key={s.id} style={{ background: tint(accent, 0.12), borderRadius: '2em', padding: '0.12em 0.7em', fontSize: '0.92em', fontWeight: 600 }}>{s.name}</span>)}</div></Card>}
          {h.lang && <Card t="Ngoại ngữ">{d.languages.map((l) => <div key={l.id}><b>{l.name}</b>{l.level && <span style={{ color: '#6b7280' }}> · {l.level}</span>}</div>)}</Card>}
          {h.awards && <Card t="Thành tích"><Bullets text={d.awards} /></Card>}
        </div>
      </div>
    </div>
  );
}

/** 16. Ring: skills as circular gauges under a photo-led left column. */
export function Ring({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  const T = (t: string) => <div style={{ fontWeight: 800, fontSize: '1.05em', color: '#0f172a', margin: '0 0 0.7em', paddingBottom: '0.3em', borderBottom: `0.14em solid ${accent}`, display: 'inline-block' }}><Tr t={t} /></div>;
  const lv = useLevels();
  const Gauge = ({ v }: { v: number }) => { if (!lv) return null; const r = 15, c = 2 * Math.PI * r; return <svg width="2.9em" height="2.9em" viewBox="0 0 40 40"><circle cx="20" cy="20" r={r} fill="none" stroke={tint(accent, 0.18)} strokeWidth="4" /><circle cx="20" cy="20" r={r} fill="none" stroke={accent} strokeWidth="4" strokeLinecap="round" strokeDasharray={`${(c * v) / 5} ${c}`} transform="rotate(-90 20 20)" /></svg>; };
  return (
    <div style={{ display: 'flex', minHeight: 'inherit', lineHeight: 1.5, color: '#1f2937' }}>
      <aside style={{ width: '32%', background: '#f8fafc', borderRight: `0.2em solid ${tint(accent, 0.25)}`, padding: '2.6em 1.6em', display: 'flex', flexDirection: 'column', gap: '1.6em' }}>
        {showPhoto && d.photo && <Photo src={d.photo} size={8.4} style={{ alignSelf: 'center', boxShadow: `0 0 0 0.3em ${tint(accent, 0.3)}` }} />}
        <section>{T('Liên hệ')}<Contacts d={d} color="#374151" iconColor={accent} /></section>
        {h.skills && <section>{T('Kỹ năng')}<div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.9em 0.6em' }}>{d.skills.map((s) => <div key={s.id} style={{ textAlign: 'center' }}><Gauge v={s.level} /><div style={{ fontSize: '0.82em', fontWeight: 600, lineHeight: 1.2 }}>{s.name}</div></div>)}</div></section>}
        {h.lang && <section>{T('Ngoại ngữ')}{d.languages.map((l) => <div key={l.id} style={{ marginBottom: '0.35em' }}><b>{l.name}</b>{l.level && <div style={{ color: '#6b7280', fontSize: '0.92em' }}>{l.level}</div>}</div>)}</section>}
      </aside>
      <main style={{ flex: 1, padding: '2.6em 2.2em' }}>
        <div style={{ fontSize: '2.6em', fontWeight: 800, margin: 0, lineHeight: 1.08, color: '#0f172a' }}>{d.name}</div>
        <div style={{ fontSize: '1.15em', color: accent, fontWeight: 700, margin: '0.3em 0 1em' }}>{d.title}</div>
        {d.summary && <p style={{ margin: 0, color: '#4b5563' }}>{d.summary}</p>}
        {h.exp && <section style={{ marginTop: '1.7em' }}>{T('Kinh nghiệm')}{d.experience.map((e) => <Row key={e.id} style={{ marginBottom: '1.1em' }}><div style={{ display: 'flex', justifyContent: 'space-between', gap: '1em' }}><b style={{ fontSize: '1.07em' }}>{e.role}</b><Dates a={e.from} b={e.to} /></div><div style={{ color: '#6b7280' }}>{e.company}</div><Bullets text={e.desc} /></Row>)}</section>}
        {h.edu && <section style={{ marginTop: '1.4em' }}>{T('Học vấn')}{d.education.map((e) => <Row key={e.id} style={{ marginBottom: '0.8em' }}><div style={{ display: 'flex', justifyContent: 'space-between' }}><b>{e.school}</b><Dates a={e.from} b={e.to} /></div><div>{e.degree}</div></Row>)}</section>}
        {h.proj && <section style={{ marginTop: '1.4em' }}>{T('Dự án')}{d.projects.map((p) => <Row key={p.id} style={{ marginBottom: '0.6em' }}><b>{p.name}</b><div style={{ color: '#4b5563' }}><ProjDesc p={p} /></div></Row>)}</section>}
        {h.awards && <section style={{ marginTop: '1.4em' }}>{T('Thành tích')}<Bullets text={d.awards} /></section>}
      </main>
    </div>
  );
}

/** 17. Monogram: initials in a framed square, centred and formal. */
export function Monogram({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  const T = (t: string) => <div style={{ textAlign: 'center', fontWeight: 700, letterSpacing: '0.25em', textTransform: 'uppercase', fontSize: '0.95em', color: accent, margin: '0 0 0.9em' }}><Tr t={t} /></div>;
  return (
    <div style={{ padding: '2.8em 3em', lineHeight: 1.55, color: '#374151' }}>
      <header style={{ textAlign: 'center' }}>
        {showPhoto && d.photo ? <Photo src={d.photo} size={6.4} radius="0" style={{ margin: '0 auto 1em', border: `0.15em solid ${accent}`, padding: '0.25em' }} />
          : <div style={{ width: '4.6em', height: '4.6em', margin: '0 auto 1em', border: `0.15em solid ${accent}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5em', fontWeight: 300, letterSpacing: '0.1em', color: accent }}>{initials(d.name)}</div>}
        <div style={{ fontSize: '2.5em', fontWeight: 400, letterSpacing: '0.1em', margin: 0, color: '#111827', textTransform: 'uppercase' }}>{d.name}</div>
        <div style={{ margin: '0.5em 0 1em', letterSpacing: '0.22em', textTransform: 'uppercase', fontSize: '0.95em', color: accent }}>{d.title}</div>
        <div style={{ display: 'flex', justifyContent: 'center' }}><Contacts d={d} row color="#6b7280" iconColor={accent} size={0.88} /></div>
      </header>
      {d.summary && <p style={{ textAlign: 'center', margin: '1.6em auto 0', maxWidth: '88%' }}>{d.summary}</p>}
      <div style={{ display: 'grid', gridTemplateColumns: '1.7fr 1fr', gap: '2.4em', marginTop: '2em' }}>
        <div>
          {h.exp && <section style={{ marginBottom: '1.5em' }}>{T('Kinh nghiệm')}{d.experience.map((e) => <Row key={e.id} style={{ marginBottom: '1.05em' }}><b style={{ color: '#111827' }}>{e.role}</b><div style={{ color: '#6b7280', fontSize: '0.93em' }}>{e.company} · {dateRange(e.from, e.to)}</div><Bullets text={e.desc} /></Row>)}</section>}
          {h.proj && <section>{T('Dự án')}{d.projects.map((p) => <Row key={p.id} style={{ marginBottom: '0.5em' }}><b style={{ color: '#111827' }}>{p.name}</b><div><ProjDesc p={p} /></div></Row>)}</section>}
        </div>
        <div style={{ borderLeft: '0.08em solid #e5e7eb', paddingLeft: '1.6em' }}>
          {h.edu && <section style={{ marginBottom: '1.5em' }}>{T('Học vấn')}{d.education.map((e) => <Row key={e.id} style={{ marginBottom: '0.7em', textAlign: 'center' }}><b style={{ color: '#111827' }}>{e.school}</b><div style={{ fontSize: '0.95em' }}>{e.degree}</div><div style={{ color: '#9ca3af', fontSize: '0.88em' }}>{dateRange(e.from, e.to)}</div></Row>)}</section>}
          {h.skills && <section style={{ marginBottom: '1.5em', textAlign: 'center' }}>{T('Kỹ năng')}{d.skills.map((s) => <div key={s.id}>{s.name}</div>)}</section>}
          {h.lang && <section style={{ marginBottom: '1.5em', textAlign: 'center' }}>{T('Ngoại ngữ')}{d.languages.map((l) => <div key={l.id}>{l.name}{l.level && <span style={{ color: '#9ca3af' }}> · {l.level}</span>}</div>)}</section>}
          {h.awards && <section style={{ textAlign: 'center' }}>{T('Thành tích')}{lines(d.awards).map((l, i) => <div key={i}>{linkText(l)}</div>)}</section>}
        </div>
      </div>
    </div>
  );
}

/** 18. Stripe: thick accent stripe down the left edge, headings in solid blocks. */
export function Stripe({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  const T = (t: string) => <div style={{ display: 'inline-block', background: '#111827', color: '#fff', fontWeight: 700, fontSize: '0.9em', letterSpacing: '0.14em', textTransform: 'uppercase', padding: '0.28em 0.9em', margin: '0 0 0.8em', borderLeft: `0.35em solid ${accent}` }}><Tr t={t} /></div>;
  return (
    <div style={{ display: 'flex', minHeight: 'inherit', lineHeight: 1.5, color: '#1f2937' }}>
      <div style={{ width: '1.6em', background: accent, flex: 'none' }} />
      <div style={{ flex: 1, padding: '2.6em 2.8em' }}>
        <header style={{ display: 'flex', alignItems: 'center', gap: '1.6em' }}>
          <div style={{ flex: 1 }}><div style={{ fontSize: '2.7em', fontWeight: 800, margin: 0, lineHeight: 1.05, color: '#0f172a' }}>{d.name}</div><div style={{ fontSize: '1.15em', color: accent, fontWeight: 700, margin: '0.3em 0 0.9em' }}>{d.title}</div><Contacts d={d} row color="#4b5563" iconColor={accent} size={0.9} /></div>
          {showPhoto && d.photo && <Photo src={d.photo} size={7.2} radius="0.4em" />}
        </header>
        {d.summary && <p style={{ margin: '1.3em 0 0', color: '#4b5563' }}>{d.summary}</p>}
        {h.exp && <section style={{ marginTop: '1.6em' }}>{T('Kinh nghiệm')}{d.experience.map((e) => <Row key={e.id} style={{ marginBottom: '1.1em' }}><div style={{ display: 'flex', justifyContent: 'space-between', gap: '1em' }}><b style={{ fontSize: '1.07em' }}>{e.role} <span style={{ color: accent }}>· {e.company}</span></b><Dates a={e.from} b={e.to} /></div><Bullets text={e.desc} /></Row>)}</section>}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2em', marginTop: '1.4em' }}>
          {h.edu && <section>{T('Học vấn')}{d.education.map((e) => <Row key={e.id} style={{ marginBottom: '0.8em' }}><b>{e.school}</b><div>{e.degree}</div><Dates a={e.from} b={e.to} /></Row>)}</section>}
          {h.skills && <section>{T('Kỹ năng')}<div style={{ display: 'flex', flexDirection: 'column', gap: '0.5em' }}>{d.skills.map((s) => <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}><span>{s.name}</span><Level level={s.level} kind="dots" color={accent} track="#d1d5db" /></div>)}</div></section>}
          {h.lang && <section>{T('Ngoại ngữ')}{d.languages.map((l) => <div key={l.id}><b>{l.name}</b>{l.level && <span style={{ color: '#6b7280' }}> · {l.level}</span>}</div>)}</section>}
          {h.proj && <section>{T('Dự án')}{d.projects.map((p) => <Row key={p.id} style={{ marginBottom: '0.5em' }}><b>{p.name}</b><div style={{ color: '#4b5563', fontSize: '0.95em' }}><ProjDesc p={p} /></div></Row>)}</section>}
        </div>
        {h.awards && <section style={{ marginTop: '1.4em' }}>{T('Thành tích')}<Bullets text={d.awards} /></section>}
      </div>
    </div>
  );
}
