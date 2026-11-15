import { Tr } from '../lang';
import { Bullets, Contacts, Level, Photo, Row, hasAny, tint, type CvProps, ProjDesc } from '../parts';
import { dateRange } from '@/lib/cv/types';

const H = (c: string): React.CSSProperties => ({ fontSize: '1.05em', fontWeight: 800, letterSpacing: '0.12em', textTransform: 'uppercase', color: c, margin: '0 0 0.7em' });

/** 1. Modern: coloured sidebar on the left with photo, contact and skills; story on the right. */
export function Modern({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  return (
    <div style={{ display: 'flex', minHeight: 'inherit', lineHeight: 1.5, color: '#1f2937' }}>
      <aside style={{ width: '31%', background: accent, color: '#fff', padding: '2.6em 1.7em', display: 'flex', flexDirection: 'column', gap: '1.8em' }}>
        {showPhoto && d.photo && <div style={{ display: 'flex', justifyContent: 'center' }}><Photo src={d.photo} size={8.4} style={{ border: '0.28em solid rgba(255,255,255,.55)' }} /></div>}
        <section><div style={H('#fff')}><Tr t="Liên hệ" /></div><Contacts d={d} color="#fff" /></section>
        {h.skills && <section><div style={H('#fff')}><Tr t="Kỹ năng" /></div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8em' }}>{d.skills.map((s) => <div key={s.id}><div style={{ fontSize: '0.95em', fontWeight: 600, marginBottom: '0.3em' }}>{s.name}</div><Level level={s.level} kind="bar" color="#fff" track="rgba(255,255,255,.28)" /></div>)}</div></section>}
        {h.lang && <section><div style={H('#fff')}><Tr t="Ngoại ngữ" /></div>{d.languages.map((l) => <div key={l.id} style={{ fontSize: '0.95em', marginBottom: '0.45em' }}><b>{l.name}</b>{l.level && <div style={{ opacity: 0.85 }}>{l.level}</div>}</div>)}</section>}
      </aside>
      <main style={{ flex: 1, padding: '2.6em 2.2em' }}>
        <div style={{ fontSize: '2.7em', fontWeight: 800, lineHeight: 1.1, margin: 0, color: '#0f172a' }}>{d.name}</div>
        <div style={{ fontSize: '1.2em', fontWeight: 600, color: accent, marginTop: '0.35em' }}>{d.title}</div>
        {d.summary && <p style={{ margin: '1.1em 0 0', color: '#4b5563' }}>{d.summary}</p>}
        {h.exp && <section style={{ marginTop: '1.9em' }}><div style={H(accent)}><Tr t="Kinh nghiệm làm việc" /></div>
          {d.experience.map((e) => <Row key={e.id} style={{ marginBottom: '1.15em' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1em' }}><b style={{ fontSize: '1.08em' }}>{e.role}</b><span style={{ color: '#6b7280', fontSize: '0.92em', whiteSpace: 'nowrap' }}>{dateRange(e.from, e.to)}</span></div>
            <div style={{ color: accent, fontWeight: 600 }}>{e.company}</div><Bullets text={e.desc} /></Row>)}</section>}
        {h.edu && <section style={{ marginTop: '1.5em' }}><div style={H(accent)}><Tr t="Học vấn" /></div>
          {d.education.map((e) => <Row key={e.id} style={{ marginBottom: '0.9em' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1em' }}><b>{e.school}</b><span style={{ color: '#6b7280', fontSize: '0.92em', whiteSpace: 'nowrap' }}>{dateRange(e.from, e.to)}</span></div>
            <div>{e.degree}</div>{e.desc && <div style={{ color: '#6b7280', fontSize: '0.95em' }}>{e.desc}</div>}</Row>)}</section>}
        {h.proj && <section style={{ marginTop: '1.5em' }}><div style={H(accent)}><Tr t="Dự án" /></div>{d.projects.map((p) => <Row key={p.id} style={{ marginBottom: '0.7em' }}><b>{p.name}</b><div style={{ color: '#4b5563' }}><ProjDesc p={p} /></div></Row>)}</section>}
        {h.awards && <section style={{ marginTop: '1.5em' }}><div style={H(accent)}><Tr t="Thành tích và chứng chỉ" /></div><Bullets text={d.awards} /></section>}
      </main>
    </div>
  );
}

const S = (c: string): React.CSSProperties => ({ fontSize: '0.98em', fontWeight: 800, letterSpacing: '0.18em', textTransform: 'uppercase', color: c, borderBottom: `0.14em solid ${c}`, paddingBottom: '0.35em', margin: '0 0 0.8em' });

/** 2. Executive: single column, small caps headings with a rule, dates on the right. */
export function Executive({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  return (
    <div style={{ padding: '2.9em 3em', lineHeight: 1.5, color: '#1f2937' }}>
      <header style={{ display: 'flex', alignItems: 'center', gap: '1.6em', paddingBottom: '1.4em', borderBottom: `0.22em solid ${accent}` }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '2.6em', fontWeight: 800, letterSpacing: '0.04em', textTransform: 'uppercase', margin: 0, color: '#0f172a', lineHeight: 1.1 }}>{d.name}</div>
          <div style={{ fontSize: '1.15em', color: accent, fontWeight: 600, margin: '0.35em 0 0.8em', letterSpacing: '0.06em' }}>{d.title}</div>
          <Contacts d={d} row color="#4b5563" iconColor={accent} />
        </div>
        {showPhoto && d.photo && <Photo src={d.photo} size={7.6} radius="0.5em" />}
      </header>
      {d.summary && <p style={{ margin: '1.3em 0 0', color: '#374151' }}>{d.summary}</p>}
      {h.exp && <section style={{ marginTop: '1.6em' }}><div style={S(accent)}><Tr t="Kinh nghiệm làm việc" /></div>
        {d.experience.map((e) => <Row key={e.id} style={{ marginBottom: '1.1em' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1em' }}><span><b style={{ fontSize: '1.07em' }}>{e.role}</b> <span style={{ color: '#6b7280' }}>· {e.company}</span></span><span style={{ color: '#6b7280', fontSize: '0.92em', whiteSpace: 'nowrap' }}>{dateRange(e.from, e.to)}</span></div>
          <Bullets text={e.desc} /></Row>)}</section>}
      {h.edu && <section style={{ marginTop: '1.4em' }}><div style={S(accent)}><Tr t="Học vấn" /></div>
        {d.education.map((e) => <Row key={e.id} style={{ marginBottom: '0.8em' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1em' }}><span><b>{e.school}</b> <span style={{ color: '#6b7280' }}>· {e.degree}</span></span><span style={{ color: '#6b7280', fontSize: '0.92em' }}>{dateRange(e.from, e.to)}</span></div>
          {e.desc && <div style={{ color: '#6b7280', fontSize: '0.95em' }}>{e.desc}</div>}</Row>)}</section>}
      {(h.skills || h.lang) && <section style={{ marginTop: '1.4em', display: 'grid', gridTemplateColumns: h.skills && h.lang ? '1.4fr 1fr' : '1fr', gap: '2em' }}>
        {h.skills && <div><div style={S(accent)}><Tr t="Kỹ năng" /></div><div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.45em' }}>{d.skills.map((s) => <span key={s.id} style={{ background: tint(accent, 0.1), color: '#1f2937', borderRadius: '0.3em', padding: '0.2em 0.7em', fontWeight: 500 }}>{s.name}</span>)}</div></div>}
        {h.lang && <div><div style={S(accent)}><Tr t="Ngoại ngữ" /></div>{d.languages.map((l) => <div key={l.id}><b>{l.name}</b>{l.level && <span style={{ color: '#6b7280' }}> · {l.level}</span>}</div>)}</div>}
      </section>}
      {h.proj && <section style={{ marginTop: '1.4em' }}><div style={S(accent)}><Tr t="Dự án" /></div>{d.projects.map((p) => <Row key={p.id} style={{ marginBottom: '0.6em' }}><b>{p.name}</b> <span style={{ color: '#4b5563' }}>– <ProjDesc p={p} /></span></Row>)}</section>}
      {h.awards && <section style={{ marginTop: '1.4em' }}><div style={S(accent)}><Tr t="Thành tích và chứng chỉ" /></div><Bullets text={d.awards} /></section>}
    </div>
  );
}

/** 3. Clean: main column left, light grey sidebar right. */
export function CleanRight({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  const T = (t: string) => <div style={{ fontSize: '1.05em', fontWeight: 800, color: '#0f172a', margin: '0 0 0.7em', display: 'flex', alignItems: 'center', gap: '0.6em' }}><span style={{ width: '1.3em', height: '0.22em', background: accent, borderRadius: 2 }} /><Tr t={t} /></div>;
  return (
    <div style={{ display: 'flex', minHeight: 'inherit', lineHeight: 1.5, color: '#1f2937' }}>
      <main style={{ flex: 1, padding: '2.8em 2.2em 2.8em 2.8em' }}>
        <div style={{ fontSize: '2.5em', fontWeight: 800, margin: 0, lineHeight: 1.1, color: '#0f172a' }}>{d.name}</div>
        <div style={{ fontSize: '1.15em', color: accent, fontWeight: 600, marginTop: '0.3em' }}>{d.title}</div>
        {d.summary && <p style={{ margin: '1.1em 0 0', color: '#4b5563' }}>{d.summary}</p>}
        {h.exp && <section style={{ marginTop: '1.8em' }}>{T('Kinh nghiệm')}
          {d.experience.map((e) => <Row key={e.id} style={{ marginBottom: '1.1em' }}>
            <b style={{ fontSize: '1.07em' }}>{e.role}</b>
            <div style={{ color: '#6b7280', fontSize: '0.93em' }}>{e.company} · {dateRange(e.from, e.to)}</div><Bullets text={e.desc} /></Row>)}</section>}
        {h.proj && <section style={{ marginTop: '1.5em' }}>{T('Dự án')}{d.projects.map((p) => <Row key={p.id} style={{ marginBottom: '0.7em' }}><b>{p.name}</b><div style={{ color: '#4b5563' }}><ProjDesc p={p} /></div></Row>)}</section>}
      </main>
      <aside style={{ width: '34%', background: '#f1f5f9', padding: '2.8em 1.8em', display: 'flex', flexDirection: 'column', gap: '1.7em' }}>
        {showPhoto && d.photo && <Photo src={d.photo} size={8.6} radius="0.9em" style={{ alignSelf: 'center' }} />}
        <section>{T('Liên hệ')}<Contacts d={d} color="#334155" iconColor={accent} /></section>
        {h.edu && <section>{T('Học vấn')}{d.education.map((e) => <Row key={e.id} style={{ marginBottom: '0.8em' }}><b>{e.school}</b><div style={{ fontSize: '0.95em' }}>{e.degree}</div><div style={{ color: '#6b7280', fontSize: '0.9em' }}>{dateRange(e.from, e.to)}</div></Row>)}</section>}
        {h.skills && <section>{T('Kỹ năng')}<div style={{ display: 'flex', flexDirection: 'column', gap: '0.65em' }}>{d.skills.map((s) => <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.8em' }}><span style={{ fontSize: '0.95em' }}>{s.name}</span><Level level={s.level} kind="dots" color={accent} track="#cbd5e1" /></div>)}</div></section>}
        {h.lang && <section>{T('Ngoại ngữ')}{d.languages.map((l) => <div key={l.id} style={{ marginBottom: '0.35em' }}><b>{l.name}</b>{l.level && <span style={{ color: '#6b7280' }}> · {l.level}</span>}</div>)}</section>}
        {h.awards && <section>{T('Thành tích')}<Bullets text={d.awards} /></section>}
      </aside>
    </div>
  );
}

/** 4. Banner: full-width coloured header, two columns underneath. */
export function Banner({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  const T = (t: string) => <div style={{ fontSize: '1.08em', fontWeight: 800, color: accent, margin: '0 0 0.7em', textTransform: 'uppercase', letterSpacing: '0.1em' }}><Tr t={t} /></div>;
  return (
    <div style={{ lineHeight: 1.5, color: '#1f2937' }}>
      <header style={{ background: `linear-gradient(120deg, ${accent}, ${accent}cc)`, color: '#fff', padding: '2.6em 2.8em', display: 'flex', alignItems: 'center', gap: '1.8em' }}>
        {showPhoto && d.photo && <Photo src={d.photo} size={7.8} style={{ border: '0.25em solid rgba(255,255,255,.6)' }} />}
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '2.7em', fontWeight: 800, margin: 0, lineHeight: 1.1 }}>{d.name}</div>
          <div style={{ fontSize: '1.2em', marginTop: '0.3em', opacity: 0.95, fontWeight: 500 }}>{d.title}</div>
          <div style={{ marginTop: '0.9em' }}><Contacts d={d} row color="#fff" size={0.92} /></div>
        </div>
      </header>
      <div style={{ display: 'flex', gap: '2.2em', padding: '2em 2.8em' }}>
        <main style={{ flex: 1.9 }}>
          {d.summary && <section style={{ marginBottom: '1.6em' }}>{T('Giới thiệu')}<p style={{ margin: 0, color: '#4b5563' }}>{d.summary}</p></section>}
          {h.exp && <section>{T('Kinh nghiệm')}{d.experience.map((e) => <Row key={e.id} style={{ marginBottom: '1.1em' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1em' }}><b style={{ fontSize: '1.07em' }}>{e.role}</b><span style={{ color: '#6b7280', fontSize: '0.92em', whiteSpace: 'nowrap' }}>{dateRange(e.from, e.to)}</span></div>
            <div style={{ color: '#6b7280' }}>{e.company}</div><Bullets text={e.desc} /></Row>)}</section>}
          {h.proj && <section style={{ marginTop: '1.4em' }}>{T('Dự án')}{d.projects.map((p) => <Row key={p.id} style={{ marginBottom: '0.7em' }}><b>{p.name}</b><div style={{ color: '#4b5563' }}><ProjDesc p={p} /></div></Row>)}</section>}
        </main>
        <aside style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1.6em' }}>
          {h.edu && <section>{T('Học vấn')}{d.education.map((e) => <Row key={e.id} style={{ marginBottom: '0.8em' }}><b>{e.school}</b><div style={{ fontSize: '0.95em' }}>{e.degree}</div><div style={{ color: '#6b7280', fontSize: '0.9em' }}>{dateRange(e.from, e.to)}</div></Row>)}</section>}
          {h.skills && <section>{T('Kỹ năng')}<div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4em' }}>{d.skills.map((s) => <span key={s.id} style={{ border: `0.1em solid ${accent}`, color: accent, borderRadius: '2em', padding: '0.12em 0.7em', fontSize: '0.92em', fontWeight: 600 }}>{s.name}</span>)}</div></section>}
          {h.lang && <section>{T('Ngoại ngữ')}{d.languages.map((l) => <div key={l.id} style={{ marginBottom: '0.3em' }}><b>{l.name}</b>{l.level && <div style={{ color: '#6b7280', fontSize: '0.92em' }}>{l.level}</div>}</div>)}</section>}
          {h.awards && <section>{T('Thành tích')}<Bullets text={d.awards} /></section>}
        </aside>
      </div>
    </div>
  );
}

/** 5. Minimal: centred name, hairlines, lots of air. */
export function Minimal({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  const T = (t: string) => <div style={{ textAlign: 'center', fontSize: '0.95em', letterSpacing: '0.32em', textTransform: 'uppercase', color: accent, fontWeight: 700, margin: '0 0 1em', display: 'flex', alignItems: 'center', gap: '1em' }}><span style={{ flex: 1, height: 1, background: '#e5e7eb' }} /><Tr t={t} /><span style={{ flex: 1, height: 1, background: '#e5e7eb' }} /></div>;
  return (
    <div style={{ padding: '3.2em 3.4em', lineHeight: 1.55, color: '#374151' }}>
      <header style={{ textAlign: 'center' }}>
        {showPhoto && d.photo && <Photo src={d.photo} size={6.4} style={{ margin: '0 auto 1em' }} />}
        <div style={{ fontSize: '2.7em', fontWeight: 300, letterSpacing: '0.14em', textTransform: 'uppercase', margin: 0, color: '#111827' }}>{d.name}</div>
        <div style={{ fontSize: '1.05em', letterSpacing: '0.28em', textTransform: 'uppercase', color: accent, marginTop: '0.6em', fontWeight: 500 }}>{d.title}</div>
        <div style={{ display: 'flex', justifyContent: 'center', marginTop: '1.2em' }}><Contacts d={d} row color="#6b7280" iconColor={accent} size={0.9} /></div>
      </header>
      {d.summary && <p style={{ textAlign: 'center', margin: '1.8em auto 0', maxWidth: '86%', color: '#4b5563' }}>{d.summary}</p>}
      {h.exp && <section style={{ marginTop: '2em' }}>{T('Kinh nghiệm')}{d.experience.map((e) => <Row key={e.id} style={{ marginBottom: '1.15em' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1em' }}><b style={{ color: '#111827' }}>{e.role} <span style={{ fontWeight: 400, color: '#6b7280' }}>/ {e.company}</span></b><span style={{ color: '#9ca3af', fontSize: '0.9em', whiteSpace: 'nowrap' }}>{dateRange(e.from, e.to)}</span></div><Bullets text={e.desc} /></Row>)}</section>}
      {h.edu && <section style={{ marginTop: '1.6em' }}>{T('Học vấn')}{d.education.map((e) => <Row key={e.id} style={{ marginBottom: '0.7em' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}><b style={{ color: '#111827' }}>{e.school} <span style={{ fontWeight: 400, color: '#6b7280' }}>/ {e.degree}</span></b><span style={{ color: '#9ca3af', fontSize: '0.9em' }}>{dateRange(e.from, e.to)}</span></div></Row>)}</section>}
      {(h.skills || h.lang) && <section style={{ marginTop: '1.6em' }}>{T('Kỹ năng')}<div style={{ textAlign: 'center', color: '#374151' }}>{[...d.skills.map((s) => s.name), ...d.languages.map((l) => `${l.name}${l.level ? ` (${l.level})` : ''}`)].join('  ·  ')}</div></section>}
      {h.proj && <section style={{ marginTop: '1.6em' }}>{T('Dự án')}{d.projects.map((p) => <Row key={p.id} style={{ marginBottom: '0.5em' }}><b style={{ color: '#111827' }}>{p.name}</b> – <ProjDesc p={p} /></Row>)}</section>}
      {h.awards && <section style={{ marginTop: '1.6em' }}>{T('Thành tích')}<Bullets text={d.awards} /></section>}
    </div>
  );
}
