import { Tr } from '../lang';
import { Bullets, Contacts, Level, Photo, Row, hasAny, tint, type CvProps, ProjDesc, linkText } from '../parts';
import { dateRange, lines } from '@/lib/cv/types';

/** 6. Timeline: vertical line with dots for experience and education, chips for skills. */
export function Timeline({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  const T = (t: string) => <div style={{ fontSize: '1.15em', fontWeight: 800, color: '#0f172a', margin: '0 0 0.9em' }}><Tr t={t} /><span style={{ display: 'block', width: '2.2em', height: '0.22em', background: accent, borderRadius: 2, marginTop: '0.3em' }} /></div>;
  const Line = ({ items }: { items: { id: string; title: string; sub: string; date: string; desc: string }[] }) => (
    <div style={{ borderLeft: `0.16em solid ${tint(accent, 0.3)}`, marginLeft: '0.5em', paddingLeft: '1.5em' }}>
      {items.map((e) => <Row key={e.id} style={{ position: 'relative', marginBottom: '1.15em' }}>
        <span style={{ position: 'absolute', left: '-2.05em', top: '0.3em', width: '0.9em', height: '0.9em', borderRadius: '50%', background: '#fff', border: `0.22em solid ${accent}` }} />
        <div style={{ fontSize: '0.88em', fontWeight: 700, color: accent }}>{e.date}</div>
        <b style={{ fontSize: '1.06em' }}>{e.title}</b>{e.sub && <div style={{ color: '#6b7280' }}>{e.sub}</div>}
        {e.desc && (e.desc.includes('\n') ? <Bullets text={e.desc} /> : <div style={{ color: '#4b5563', marginTop: '0.2em' }}>{e.desc}</div>)}</Row>)}
    </div>
  );
  return (
    <div style={{ lineHeight: 1.5, color: '#1f2937' }}>
      <header style={{ display: 'flex', alignItems: 'center', gap: '1.6em', padding: '2.5em 2.8em 1.6em', borderLeft: `0.8em solid ${accent}` }}>
        {showPhoto && d.photo && <Photo src={d.photo} size={7.4} />}
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '2.6em', fontWeight: 800, margin: 0, lineHeight: 1.1, color: '#0f172a' }}>{d.name}</div>
          <div style={{ fontSize: '1.15em', color: accent, fontWeight: 600, margin: '0.3em 0 0.8em' }}>{d.title}</div>
          <Contacts d={d} row color="#4b5563" iconColor={accent} size={0.92} />
        </div>
      </header>
      <div style={{ padding: '0.6em 2.8em 2.6em' }}>
        {d.summary && <p style={{ margin: '0 0 1.6em', color: '#4b5563', padding: '0.9em 1.1em', background: tint(accent, 0.07), borderRadius: '0.6em' }}>{d.summary}</p>}
        {h.exp && <section style={{ marginBottom: '1.4em' }}>{T('Kinh nghiệm làm việc')}<Line items={d.experience.map((e) => ({ id: e.id, title: e.role, sub: e.company, date: dateRange(e.from, e.to), desc: e.desc }))} /></section>}
        {h.edu && <section style={{ marginBottom: '1.4em' }}>{T('Học vấn')}<Line items={d.education.map((e) => ({ id: e.id, title: e.school, sub: e.degree, date: dateRange(e.from, e.to), desc: e.desc }))} /></section>}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2em' }}>
          {h.skills && <section>{T('Kỹ năng')}<div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.45em' }}>{d.skills.map((s) => <span key={s.id} style={{ background: tint(accent, 0.12), color: '#1f2937', borderRadius: '0.4em', padding: '0.22em 0.7em', fontWeight: 600, fontSize: '0.93em' }}>{s.name}</span>)}</div></section>}
          {h.lang && <section>{T('Ngoại ngữ')}{d.languages.map((l) => <div key={l.id} style={{ marginBottom: '0.3em' }}><b>{l.name}</b>{l.level && <span style={{ color: '#6b7280' }}> · {l.level}</span>}</div>)}</section>}
          {h.proj && <section>{T('Dự án')}{d.projects.map((p) => <Row key={p.id} style={{ marginBottom: '0.6em' }}><b>{p.name}</b><div style={{ color: '#4b5563', fontSize: '0.95em' }}><ProjDesc p={p} /></div></Row>)}</section>}
          {h.awards && <section>{T('Thành tích')}<Bullets text={d.awards} /></section>}
        </div>
      </div>
    </div>
  );
}

/** 7. Creative: rounded shapes, tinted panels and dotted ratings. */
export function Creative({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  const T = (t: string) => <div style={{ display: 'inline-block', background: accent, color: '#fff', fontWeight: 700, fontSize: '0.98em', padding: '0.28em 1em', borderRadius: '2em', margin: '0 0 0.9em' }}><Tr t={t} /></div>;
  return (
    <div style={{ position: 'relative', overflow: 'hidden', minHeight: 'inherit', lineHeight: 1.5, color: '#1f2937', background: '#fff' }}>
      <div style={{ position: 'absolute', top: '-7em', right: '-6em', width: '19em', height: '19em', borderRadius: '50%', background: tint(accent, 0.14) }} />
      <div style={{ position: 'absolute', top: '3em', right: '5em', width: '4.5em', height: '4.5em', borderRadius: '50%', background: tint(accent, 0.22) }} />
      <div style={{ position: 'relative', padding: '2.8em' }}>
        <header style={{ display: 'flex', alignItems: 'center', gap: '1.8em' }}>
          {showPhoto && d.photo && <Photo src={d.photo} size={8} radius="1.6em" style={{ boxShadow: `0.5em 0.5em 0 ${tint(accent, 0.35)}` }} />}
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: '2.7em', fontWeight: 800, margin: 0, lineHeight: 1.05, color: '#0f172a' }}>{d.name}</div>
            <div style={{ fontSize: '1.2em', color: accent, fontWeight: 700, marginTop: '0.3em' }}>{d.title}</div>
          </div>
        </header>
        <div style={{ marginTop: '1.2em', padding: '0.9em 1.2em', background: tint(accent, 0.08), borderRadius: '1em' }}><Contacts d={d} row color="#374151" iconColor={accent} size={0.92} /></div>
        {d.summary && <p style={{ margin: '1.3em 0 0', color: '#4b5563' }}>{d.summary}</p>}
        <div style={{ display: 'flex', gap: '2.2em', marginTop: '1.7em' }}>
          <main style={{ flex: 1.8 }}>
            {h.exp && <section style={{ marginBottom: '1.4em' }}>{T('Kinh nghiệm')}{d.experience.map((e) => <Row key={e.id} style={{ marginBottom: '1.1em' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1em' }}><b style={{ fontSize: '1.07em' }}>{e.role}</b><span style={{ color: accent, fontSize: '0.9em', fontWeight: 700, whiteSpace: 'nowrap' }}>{dateRange(e.from, e.to)}</span></div>
              <div style={{ color: '#6b7280' }}>{e.company}</div><Bullets text={e.desc} /></Row>)}</section>}
            {h.proj && <section>{T('Dự án')}{d.projects.map((p) => <Row key={p.id} style={{ marginBottom: '0.7em' }}><b>{p.name}</b><div style={{ color: '#4b5563' }}><ProjDesc p={p} /></div></Row>)}</section>}
          </main>
          <aside style={{ flex: 1 }}>
            {h.edu && <section style={{ marginBottom: '1.4em' }}>{T('Học vấn')}{d.education.map((e) => <Row key={e.id} style={{ marginBottom: '0.8em' }}><b>{e.school}</b><div style={{ fontSize: '0.95em' }}>{e.degree}</div><div style={{ color: '#6b7280', fontSize: '0.9em' }}>{dateRange(e.from, e.to)}</div></Row>)}</section>}
            {h.skills && <section style={{ marginBottom: '1.4em' }}>{T('Kỹ năng')}<div style={{ display: 'flex', flexDirection: 'column', gap: '0.6em' }}>{d.skills.map((s) => <div key={s.id}><div style={{ fontSize: '0.93em', fontWeight: 600, marginBottom: '0.2em' }}>{s.name}</div><Level level={s.level} kind="dots" color={accent} track={tint(accent, 0.2)} /></div>)}</div></section>}
            {h.lang && <section style={{ marginBottom: '1.4em' }}>{T('Ngoại ngữ')}{d.languages.map((l) => <div key={l.id} style={{ marginBottom: '0.3em' }}><b>{l.name}</b>{l.level && <div style={{ color: '#6b7280', fontSize: '0.92em' }}>{l.level}</div>}</div>)}</section>}
            {h.awards && <section>{T('Thành tích')}<Bullets text={d.awards} /></section>}
          </aside>
        </div>
      </div>
    </div>
  );
}

/** 8. Tech: dark header, monospaced section labels, skills first. */
export function Tech({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  const mono = "ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace";
  const T = (t: string) => <div style={{ fontFamily: mono, fontSize: '0.98em', fontWeight: 700, color: accent, margin: '0 0 0.8em' }}>{'// '}<Tr t={t} /></div>;
  return (
    <div style={{ lineHeight: 1.5, color: '#1f2937', minHeight: 'inherit' }}>
      <header style={{ background: '#0f172a', color: '#e2e8f0', padding: '2.4em 2.8em', display: 'flex', alignItems: 'center', gap: '1.6em' }}>
        {showPhoto && d.photo && <Photo src={d.photo} size={7.2} radius="0.8em" style={{ border: `0.22em solid ${accent}` }} />}
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: mono, fontSize: '0.9em', color: accent }}>{'<developer />'}</div>
          <div style={{ fontSize: '2.6em', fontWeight: 800, margin: '0.1em 0 0', lineHeight: 1.1, color: '#fff' }}>{d.name}</div>
          <div style={{ fontSize: '1.15em', color: '#94a3b8', margin: '0.3em 0 0.9em' }}>{d.title}</div>
          <Contacts d={d} row color="#cbd5e1" iconColor={accent} size={0.9} />
        </div>
      </header>
      <div style={{ padding: '1.8em 2.8em 2.6em' }}>
        {d.summary && <section style={{ marginBottom: '1.5em' }}>{T('about')}<p style={{ margin: 0, color: '#4b5563' }}>{d.summary}</p></section>}
        {h.skills && <section style={{ marginBottom: '1.5em' }}>{T('skills')}<div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5em' }}>{d.skills.map((s) => <span key={s.id} style={{ fontFamily: mono, fontSize: '0.86em', background: '#0f172a', color: '#e2e8f0', borderRadius: '0.35em', padding: '0.25em 0.75em', borderBottom: `0.18em solid ${accent}` }}>{s.name}</span>)}</div></section>}
        {h.exp && <section style={{ marginBottom: '1.5em' }}>{T('experience')}{d.experience.map((e) => <Row key={e.id} style={{ marginBottom: '1.1em' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1em' }}><span><b style={{ fontSize: '1.07em' }}>{e.role}</b> <span style={{ color: accent, fontWeight: 600 }}>@ {e.company}</span></span><span style={{ fontFamily: mono, fontSize: '0.82em', color: '#6b7280', whiteSpace: 'nowrap' }}>{dateRange(e.from, e.to)}</span></div><Bullets text={e.desc} /></Row>)}</section>}
        {h.proj && <section style={{ marginBottom: '1.5em' }}>{T('projects')}{d.projects.map((p) => <Row key={p.id} style={{ marginBottom: '0.6em' }}><b>{p.name}</b><div style={{ color: '#4b5563' }}><ProjDesc p={p} /></div></Row>)}</section>}
        <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: '2em' }}>
          {h.edu && <section>{T('education')}{d.education.map((e) => <Row key={e.id} style={{ marginBottom: '0.7em' }}><b>{e.school}</b><div>{e.degree}</div><div style={{ fontFamily: mono, fontSize: '0.82em', color: '#6b7280' }}>{dateRange(e.from, e.to)}</div></Row>)}</section>}
          <div>
            {h.lang && <section style={{ marginBottom: '1.2em' }}>{T('languages')}{d.languages.map((l) => <div key={l.id} style={{ marginBottom: '0.3em' }}><b>{l.name}</b>{l.level && <span style={{ color: '#6b7280' }}> · {l.level}</span>}</div>)}</section>}
            {h.awards && <section>{T('awards')}<Bullets text={d.awards} /></section>}
          </div>
        </div>
      </div>
    </div>
  );
}

/** 9. Serif: ornamental centred header, italic headings, classic and formal. */
export function Serif({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  const T = (t: string) => <div style={{ textAlign: 'center', fontSize: '1.25em', fontStyle: 'italic', fontWeight: 600, color: accent, margin: '0 0 0.7em' }}><Tr t={t} /></div>;
  const rule = <div style={{ height: '0.5em', borderTop: `0.1em solid ${accent}`, borderBottom: `0.1em solid ${accent}`, margin: '1.3em 0' }} />;
  return (
    <div style={{ padding: '3em 3.2em', lineHeight: 1.55, color: '#292524' }}>
      <header style={{ textAlign: 'center' }}>
        {showPhoto && d.photo && <Photo src={d.photo} size={6.6} style={{ margin: '0 auto 1em', border: `0.18em solid ${accent}`, padding: '0.2em', background: '#fff' }} />}
        <div style={{ fontSize: '2.9em', fontWeight: 700, margin: 0, lineHeight: 1.1, color: '#1c1917' }}>{d.name}</div>
        <div style={{ fontSize: '1.15em', fontStyle: 'italic', color: '#57534e', margin: '0.4em 0 0.9em' }}>{d.title}</div>
        <div style={{ display: 'flex', justifyContent: 'center' }}><Contacts d={d} row color="#57534e" iconColor={accent} size={0.9} /></div>
      </header>
      {rule}
      {d.summary && <p style={{ margin: '0 0 1.4em', textAlign: 'center', fontStyle: 'italic', color: '#44403c' }}>{d.summary}</p>}
      {h.exp && <section style={{ marginBottom: '1.4em' }}>{T('Kinh nghiệm làm việc')}{d.experience.map((e) => <Row key={e.id} style={{ marginBottom: '1.1em' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1em' }}><b style={{ fontSize: '1.07em' }}>{e.role}, {e.company}</b><i style={{ color: '#78716c', whiteSpace: 'nowrap' }}>{dateRange(e.from, e.to)}</i></div><Bullets text={e.desc} /></Row>)}</section>}
      {h.edu && <section style={{ marginBottom: '1.4em' }}>{T('Học vấn')}{d.education.map((e) => <Row key={e.id} style={{ marginBottom: '0.7em' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1em' }}><b>{e.school}</b><i style={{ color: '#78716c' }}>{dateRange(e.from, e.to)}</i></div><div>{e.degree}</div>{e.desc && <div style={{ color: '#78716c', fontSize: '0.95em' }}>{e.desc}</div>}</Row>)}</section>}
      {(h.skills || h.lang) && <section style={{ marginBottom: '1.4em' }}>{T('Kỹ năng và ngoại ngữ')}<div style={{ textAlign: 'center' }}>{d.skills.map((s) => s.name).join(' · ')}</div>{h.lang && <div style={{ textAlign: 'center', color: '#57534e', marginTop: '0.3em' }}>{d.languages.map((l) => `${l.name}${l.level ? ` (${l.level})` : ''}`).join(' · ')}</div>}</section>}
      {h.proj && <section style={{ marginBottom: '1.4em' }}>{T('Dự án')}{d.projects.map((p) => <Row key={p.id} style={{ marginBottom: '0.5em' }}><b>{p.name}.</b> <ProjDesc p={p} /></Row>)}</section>}
      {h.awards && <section>{T('Thành tích và chứng chỉ')}<div style={{ textAlign: 'center' }}>{lines(d.awards).map((l, i) => <div key={i}>{linkText(l)}</div>)}</div></section>}
    </div>
  );
}

/** 10. Bold: big accent name block, section labels in a left column. */
export function Bold({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  const Sec = ({ t, children }: { t: string; children: React.ReactNode }) => (
    <section style={{ display: 'grid', gridTemplateColumns: '9em 1fr', gap: '1.4em', padding: '1.3em 0', borderTop: '0.1em solid #e5e7eb' }}>
      <div style={{ fontWeight: 800, color: accent, textTransform: 'uppercase', letterSpacing: '0.08em', fontSize: '0.95em' }}><Tr t={t} /></div><div>{children}</div>
    </section>
  );
  return (
    <div style={{ lineHeight: 1.5, color: '#1f2937' }}>
      <header style={{ background: '#111827', color: '#fff', padding: '2.8em 2.8em 2.2em', position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', right: 0, top: 0, bottom: 0, width: '13em', background: accent, clipPath: 'polygon(35% 0, 100% 0, 100% 100%, 0 100%)' }} />
        <div style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: '1.6em' }}>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: '3em', fontWeight: 800, margin: 0, lineHeight: 1.05, textTransform: 'uppercase', letterSpacing: '0.02em' }}>{d.name}</div>
            <div style={{ fontSize: '1.2em', color: accent === '#111827' ? '#e5e7eb' : '#fff', opacity: 0.9, margin: '0.4em 0 1em', fontWeight: 500 }}>{d.title}</div>
            <Contacts d={d} row color="#e5e7eb" iconColor="#fff" size={0.9} />
          </div>
          {showPhoto && d.photo && <Photo src={d.photo} size={7.6} radius="0.6em" style={{ border: '0.25em solid #fff' }} />}
        </div>
      </header>
      <div style={{ padding: '0.4em 2.8em 2.6em' }}>
        {d.summary && <Sec t="Giới thiệu"><p style={{ margin: 0, color: '#4b5563' }}>{d.summary}</p></Sec>}
        {h.exp && <Sec t="Kinh nghiệm">{d.experience.map((e) => <Row key={e.id} style={{ marginBottom: '1.05em' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1em' }}><b style={{ fontSize: '1.07em' }}>{e.role}</b><span style={{ color: '#6b7280', fontSize: '0.9em', whiteSpace: 'nowrap' }}>{dateRange(e.from, e.to)}</span></div>
          <div style={{ color: accent, fontWeight: 600 }}>{e.company}</div><Bullets text={e.desc} /></Row>)}</Sec>}
        {h.edu && <Sec t="Học vấn">{d.education.map((e) => <Row key={e.id} style={{ marginBottom: '0.7em' }}><div style={{ display: 'flex', justifyContent: 'space-between' }}><b>{e.school}</b><span style={{ color: '#6b7280', fontSize: '0.9em' }}>{dateRange(e.from, e.to)}</span></div><div>{e.degree}</div></Row>)}</Sec>}
        {h.skills && <Sec t="Kỹ năng"><div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.55em 2em' }}>{d.skills.map((s) => <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.8em' }}><span style={{ fontWeight: 600 }}>{s.name}</span><Level level={s.level} kind="dots" color={accent} track="#d1d5db" /></div>)}</div></Sec>}
        {h.lang && <Sec t="Ngoại ngữ">{d.languages.map((l) => <span key={l.id} style={{ marginRight: '1.6em' }}><b>{l.name}</b>{l.level && <span style={{ color: '#6b7280' }}> · {l.level}</span>}</span>)}</Sec>}
        {h.proj && <Sec t="Dự án">{d.projects.map((p) => <Row key={p.id} style={{ marginBottom: '0.6em' }}><b>{p.name}</b><div style={{ color: '#4b5563' }}><ProjDesc p={p} /></div></Row>)}</Sec>}
        {h.awards && <Sec t="Thành tích"><Bullets text={d.awards} /></Sec>}
      </div>
    </div>
  );
}
