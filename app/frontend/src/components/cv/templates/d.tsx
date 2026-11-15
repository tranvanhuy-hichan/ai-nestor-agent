import { Tr } from '../lang';
import type { CSSProperties, ReactNode } from 'react';
import { Bullets, Contacts, Level, Photo, Row, hasAny, tint, type CvProps, ProjDesc } from '../parts';
import { useLevels } from '../levels';
import { dateRange, lines, type CvData } from '@/lib/cv/types';

/**
 * Eight structurally different layouts (not recolours): infographic with headline numbers, three columns, numbered rail,
 * portfolio with a tall photo, clinical boxes, formal grid, diagonal header, and a student layout that leads with education.
 * Each factory takes a small variant object so one layout can serve several industries.
 */
const initials = (n: string) => n.trim().split(/\s+/).slice(-2).map((w) => w[0]?.toUpperCase() || '').join('');
const D = ({ a, b }: { a: string; b: string }) => <span style={{ color: '#6b7280', fontSize: '0.9em', whiteSpace: 'nowrap' }}>{dateRange(a, b)}</span>;
const ink = '#1f2937';

const Skill = ({ d, accent, kind: want, onDark }: { d: CvData; accent: string; kind: 'bar' | 'ring' | 'chips' | 'dots'; onDark?: boolean }) => {
  const lv = useLevels();
  const kind = lv ? want : 'chips';
  const col = onDark ? '#fff' : accent, track = onDark ? 'rgba(255,255,255,.25)' : tint(accent, 0.18), txt = onDark ? '#fff' : ink;
  if (kind === 'chips') return <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4em' }}>{d.skills.map((s) => <span key={s.id} style={{ background: onDark ? 'rgba(255,255,255,.16)' : tint(accent, 0.12), color: txt, borderRadius: '2em', padding: '0.15em 0.8em', fontSize: '0.92em', fontWeight: 600 }}>{s.name}</span>)}</div>;
  if (kind === 'ring') { const r = 15, len = 2 * Math.PI * r; return <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.8em 0.4em' }}>{d.skills.map((s) => <div key={s.id} style={{ textAlign: 'center' }}><svg width="3em" height="3em" viewBox="0 0 40 40"><circle cx="20" cy="20" r={r} fill="none" stroke={track} strokeWidth="4" /><circle cx="20" cy="20" r={r} fill="none" stroke={col} strokeWidth="4" strokeLinecap="round" strokeDasharray={`${(len * s.level) / 5} ${len}`} transform="rotate(-90 20 20)" /></svg><div style={{ fontSize: '0.8em', fontWeight: 600, lineHeight: 1.2, color: txt }}>{s.name}</div></div>)}</div>; }
  return <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65em' }}>{d.skills.map((s) => kind === 'bar'
    ? <div key={s.id}><div style={{ fontSize: '0.93em', fontWeight: 600, marginBottom: '0.22em', color: txt }}>{s.name}</div><Level level={s.level} kind="bar" color={col} track={track} /></div>
    : <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: txt }}><span style={{ fontSize: '0.95em' }}>{s.name}</span><Level level={s.level} kind="dots" color={col} track={track} /></div>)}</div>;
};
const Langs = ({ d, onDark }: { d: CvData; onDark?: boolean }) => <>{d.languages.map((l) => <div key={l.id} style={{ marginBottom: '0.35em', color: onDark ? '#fff' : ink }}><b>{l.name}</b>{l.level && <span style={{ opacity: 0.7 }}> · {l.level}</span>}</div>)}</>;
const Interests = ({ d, onDark }: { d: CvData; onDark?: boolean }) => <div style={{ color: onDark ? '#fff' : ink }}>{lines(d.interests).map((l, i) => <div key={i} style={{ marginBottom: '0.2em' }}>{l}</div>)}</div>;
const Label = ({ t, c, onDark, style }: { t: string; c: string; onDark?: boolean; style?: CSSProperties }) => <div style={{ fontWeight: 800, fontSize: '0.95em', letterSpacing: '0.14em', textTransform: 'uppercase', color: onDark ? '#fff' : c, margin: '0 0 0.7em', ...style }}><Tr t={t} /></div>;
const Sec = ({ t, c, children, onDark, style }: { t: string; c: string; children: ReactNode; onDark?: boolean; style?: CSSProperties }) => <section style={{ marginBottom: '1.5em', ...style }}><Label t={t} c={c} onDark={onDark} />{children}</section>;
const ExpList = ({ d, c, dot }: { d: CvData; c: string; dot?: boolean }) => <>{d.experience.map((e) => (
  <Row key={e.id} style={{ marginBottom: '1.05em', position: 'relative', paddingLeft: dot ? '1.4em' : 0 }}>
    {dot && <span style={{ position: 'absolute', left: 0, top: '0.35em', width: '0.75em', height: '0.75em', borderRadius: '50%', background: '#fff', border: `0.2em solid ${c}` }} />}
    <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1em' }}><b style={{ fontSize: '1.07em', color: '#111827' }}>{e.role}</b><D a={e.from} b={e.to} /></div>
    <div style={{ color: c, fontWeight: 600 }}>{e.company}</div><Bullets text={e.desc} />
  </Row>))}</>;
const EduList = ({ d }: { d: CvData }) => <>{d.education.map((e) => <Row key={e.id} style={{ marginBottom: '0.8em' }}><b style={{ color: '#111827' }}>{e.school}</b><div style={{ fontSize: '0.95em' }}>{e.degree}</div><div style={{ color: '#6b7280', fontSize: '0.88em' }}>{dateRange(e.from, e.to)}</div>{e.desc && <div style={{ color: '#6b7280', fontSize: '0.9em' }}>{e.desc}</div>}</Row>)}</>;
const ProjList = ({ d }: { d: CvData }) => <>{d.projects.map((p) => <Row key={p.id} style={{ marginBottom: '0.55em' }}><b style={{ color: '#111827' }}>{p.name}</b><div style={{ color: '#4b5563' }}><ProjDesc p={p} /></div></Row>)}</>;

type Skin = { dark?: string; skill?: 'bar' | 'ring' | 'chips' | 'dots'; hdr?: 'dark' | 'accent' | 'light'; bg?: string };

/** A. Infographic: headline numbers under the header, timeline on the left, gauges on the right. */
export const infographic = (v: Skin = {}) => function Infographic({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  const hb = v.hdr === 'light' ? '#fff' : v.hdr === 'accent' ? accent : (v.dark || '#0f172a'), hc = v.hdr === 'light' ? '#0f172a' : '#fff';
  return (
    <div style={{ minHeight: 'inherit', background: v.bg || '#fff', lineHeight: 1.5, color: ink }}>
      <header style={{ background: hb, color: hc, padding: '2.2em 2.6em', display: 'flex', alignItems: 'center', gap: '1.6em', borderBottom: v.hdr === 'light' ? `0.25em solid ${accent}` : undefined }}>
        {showPhoto && d.photo && <Photo src={d.photo} size={7} style={{ border: '0.22em solid rgba(255,255,255,.6)' }} />}
        <div style={{ flex: 1 }}><div style={{ fontSize: '2.6em', fontWeight: 800, margin: 0, lineHeight: 1.08 }}>{d.name}</div><div style={{ fontSize: '1.15em', color: v.hdr === 'accent' ? '#fff' : accent, fontWeight: 600, margin: '0.3em 0 0.8em' }}>{d.title}</div><Contacts d={d} row color={v.hdr === 'light' ? '#4b5563' : '#e5e7eb'} iconColor={v.hdr === 'light' ? accent : '#fff'} size={0.9} /></div>
      </header>
      {d.highlights.length > 0 && <div style={{ display: 'grid', gridTemplateColumns: `repeat(${d.highlights.length}, 1fr)`, background: tint(accent, 0.09) }}>
        {d.highlights.map((x, i) => <div key={x.id} style={{ padding: '1em 0.8em', textAlign: 'center', borderLeft: i ? `0.08em solid ${tint(accent, 0.25)}` : undefined }}><div style={{ fontSize: '2em', fontWeight: 800, color: accent, lineHeight: 1.1 }}>{x.value}</div><div style={{ fontSize: '0.82em', color: '#4b5563', fontWeight: 600 }}>{x.label}</div></div>)}
      </div>}
      <div style={{ display: 'flex', gap: '2em', padding: '1.8em 2.6em 2.4em' }}>
        <main style={{ flex: 1.8 }}>
          {d.summary && <Sec t="Giới thiệu" c={accent}><p style={{ margin: 0, color: '#4b5563' }}>{d.summary}</p></Sec>}
          {h.exp && <Sec t="Kinh nghiệm" c={accent}><div style={{ borderLeft: `0.15em solid ${tint(accent, 0.3)}`, marginLeft: '0.35em', paddingLeft: '0.9em' }}><ExpList d={d} c={accent} dot /></div></Sec>}
          {h.proj && <Sec t="Dự án" c={accent}><ProjList d={d} /></Sec>}
        </main>
        <aside style={{ flex: 1 }}>
          {h.skills && <Sec t="Kỹ năng" c={accent}><Skill d={d} accent={accent} kind={v.skill || 'ring'} /></Sec>}
          {h.edu && <Sec t="Học vấn" c={accent}><EduList d={d} /></Sec>}
          {h.lang && <Sec t="Ngoại ngữ" c={accent}><Langs d={d} /></Sec>}
          {h.awards && <Sec t="Thành tích" c={accent}><Bullets text={d.awards} /></Sec>}
        </aside>
      </div>
    </div>
  );
};

/** B. Three columns: dark rail with photo and contact, wide centre, light skills rail. */
export const threeCol = (v: Skin = {}) => function ThreeCol({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d), dk = v.dark || '#111827';
  return (
    <div style={{ display: 'flex', minHeight: 'inherit', background: v.bg || '#fff', lineHeight: 1.5, color: ink }}>
      <aside style={{ width: '23%', background: dk, color: '#fff', padding: '2.4em 1.3em', display: 'flex', flexDirection: 'column', gap: '1.5em' }}>
        {showPhoto && d.photo && <Photo src={d.photo} size={6.4} radius="0.8em" style={{ alignSelf: 'center' }} />}
        <section><Label t="Liên hệ" c={accent} /><Contacts d={d} color="#e5e7eb" iconColor={accent} size={0.88} /></section>
        {h.lang && <section><Label t="Ngoại ngữ" c={accent} /><Langs d={d} onDark /></section>}
        {lines(d.interests).length > 0 && <section><Label t="Sở thích" c={accent} /><Interests d={d} onDark /></section>}
      </aside>
      <main style={{ flex: 1, padding: '2.4em 1.8em' }}>
        <div style={{ fontSize: '2.3em', fontWeight: 800, margin: 0, lineHeight: 1.08, color: '#0f172a' }}>{d.name}</div>
        <div style={{ fontSize: '1.1em', color: accent, fontWeight: 700, margin: '0.3em 0 0.9em' }}>{d.title}</div>
        {d.summary && <p style={{ margin: '0 0 1.4em', color: '#4b5563' }}>{d.summary}</p>}
        {h.exp && <Sec t="Kinh nghiệm" c={accent}><ExpList d={d} c={accent} /></Sec>}
        {h.proj && <Sec t="Dự án" c={accent}><ProjList d={d} /></Sec>}
      </main>
      <aside style={{ width: '25%', background: tint(accent, 0.08), padding: '2.4em 1.3em', display: 'flex', flexDirection: 'column', gap: '1.4em' }}>
        {h.skills && <section><Label t="Kỹ năng" c={accent} /><Skill d={d} accent={accent} kind={v.skill || 'bar'} /></section>}
        {h.edu && <section><Label t="Học vấn" c={accent} /><EduList d={d} /></section>}
        {h.awards && <section><Label t="Chứng chỉ" c={accent} /><Bullets text={d.awards} /></section>}
      </aside>
    </div>
  );
};

/** C. Numbered: huge name, sections introduced by 01 / 02 in a left rail. */
export const numbered = (v: Skin = {}) => function Numbered({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  const rows: [string, ReactNode][] = [];
  if (d.summary) rows.push(['Giới thiệu', <p key="s" style={{ margin: 0, color: '#4b5563' }}>{d.summary}</p>]);
  if (h.exp) rows.push(['Kinh nghiệm', <ExpList key="e" d={d} c={accent} />]);
  if (h.edu) rows.push(['Học vấn', <EduList key="u" d={d} />]);
  if (h.skills) rows.push(['Kỹ năng', <Skill key="k" d={d} accent={accent} kind={v.skill || 'chips'} />]);
  if (h.proj) rows.push(['Dự án', <ProjList key="p" d={d} />]);
  if (h.awards || h.lang) rows.push(['Khác', <div key="o">{h.lang && <div style={{ marginBottom: '0.5em' }}><Langs d={d} /></div>}{h.awards && <Bullets text={d.awards} />}</div>]);
  return (
    <div style={{ minHeight: 'inherit', background: v.bg || '#fff', padding: '2.8em 3em', lineHeight: 1.5, color: ink }}>
      <header style={{ display: 'flex', alignItems: 'flex-end', gap: '1.6em', paddingBottom: '1.3em', borderBottom: '0.12em solid #111827' }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '3.1em', fontWeight: 800, margin: 0, lineHeight: 1.02, color: '#0b0f19', letterSpacing: '-0.01em' }}>{d.name}</div>
          <div style={{ fontSize: '1.15em', color: accent, fontWeight: 700, margin: '0.4em 0 0.9em' }}>{d.title}</div>
          <Contacts d={d} row color="#4b5563" iconColor={accent} size={0.9} />
        </div>
        {showPhoto && d.photo && <Photo src={d.photo} size={6.4} radius="0.3em" />}
      </header>
      {rows.map(([t, node], i) => (
        <section key={t} style={{ display: 'grid', gridTemplateColumns: '7.2em 1fr', gap: '1.4em', padding: '1.25em 0', borderBottom: '0.06em solid #e5e7eb' }}>
          <div><div style={{ fontSize: '1.9em', fontWeight: 300, color: accent, lineHeight: 1 }}>{String(i + 1).padStart(2, '0')}</div><div style={{ fontSize: '0.85em', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', marginTop: '0.4em' }}><Tr t={t} /></div></div>
          <div>{node}</div>
        </section>
      ))}
    </div>
  );
};

/** D. Portfolio: a tall photo panel on the left, content on the right. */
export const portfolio = (v: Skin = {}) => function Portfolio({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d), dk = v.dark || accent;
  return (
    <div style={{ display: 'flex', minHeight: 'inherit', background: v.bg || '#fff', lineHeight: 1.5, color: ink }}>
      <aside style={{ width: '37%', background: dk, color: '#fff', display: 'flex', flexDirection: 'column' }}>
        <div style={{ position: 'relative', flex: 'none' }}>
          {showPhoto && d.photo ? <Photo src={d.photo} size={22.6} radius="0" style={{ width: '100%', height: '21em' }} /> : <div style={{ height: '16em', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '4.5em', fontWeight: 800, background: 'rgba(0,0,0,.18)' }}>{initials(d.name)}</div>}
          <div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, padding: '2.6em 1.4em 1em', background: 'linear-gradient(transparent, rgba(0,0,0,.65))' }}>
            <div style={{ fontSize: '2em', fontWeight: 800, margin: 0, lineHeight: 1.1 }}>{d.name}</div><div style={{ opacity: 0.9, fontWeight: 600 }}>{d.title}</div>
          </div>
        </div>
        <div style={{ padding: '1.5em 1.4em', display: 'flex', flexDirection: 'column', gap: '1.4em' }}>
          <section><Label t="Liên hệ" c="#fff" onDark /><Contacts d={d} color="#fff" size={0.9} /></section>
          {h.skills && <section><Label t="Kỹ năng" c="#fff" onDark /><Skill d={d} accent={accent} kind={v.skill || 'bar'} onDark /></section>}
          {h.lang && <section><Label t="Ngoại ngữ" c="#fff" onDark /><Langs d={d} onDark /></section>}
          {lines(d.interests).length > 0 && <section><Label t="Sở thích" c="#fff" onDark /><Interests d={d} onDark /></section>}
        </div>
      </aside>
      <main style={{ flex: 1, padding: '2.6em 2.2em' }}>
        {d.summary && <Sec t="Về tôi" c={accent}><p style={{ margin: 0, color: '#4b5563', fontSize: '1.03em' }}>{d.summary}</p></Sec>}
        {h.exp && <Sec t="Kinh nghiệm" c={accent}><ExpList d={d} c={accent} /></Sec>}
        {h.proj && <Sec t="Dự án tiêu biểu" c={accent}><ProjList d={d} /></Sec>}
        {h.edu && <Sec t="Học vấn" c={accent}><EduList d={d} /></Sec>}
        {h.awards && <Sec t="Giải thưởng" c={accent}><Bullets text={d.awards} /></Sec>}
      </main>
    </div>
  );
};

/** E. Clinical: boxed sections, licences and certificates come first. */
export const clinical = (v: Skin = {}) => function Clinical({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  const Box = ({ t, children }: { t: string; children: ReactNode }) => <section style={{ border: `0.08em solid ${tint(accent, 0.35)}`, borderRadius: '0.6em', overflow: 'hidden', marginBottom: '1.1em', breakInside: 'avoid' }}><div style={{ background: tint(accent, 0.12), color: accent, fontWeight: 800, fontSize: '0.95em', padding: '0.45em 1em', textTransform: 'uppercase', letterSpacing: '0.08em' }}><Tr t={t} /></div><div style={{ padding: '0.9em 1em' }}>{children}</div></section>;
  return (
    <div style={{ minHeight: 'inherit', background: v.bg || '#fff', lineHeight: 1.5, color: ink }}>
      <div style={{ height: '0.8em', background: accent }} />
      <header style={{ display: 'flex', alignItems: 'center', gap: '1.5em', padding: '1.8em 2.6em 1.2em' }}>
        {showPhoto && d.photo && <Photo src={d.photo} size={7} />}
        <div style={{ flex: 1 }}><div style={{ fontSize: '2.4em', fontWeight: 800, margin: 0, lineHeight: 1.1, color: '#0f172a' }}>{d.name}</div><div style={{ fontSize: '1.15em', color: accent, fontWeight: 700, marginTop: '0.25em' }}>{d.title}</div></div>
        <div style={{ borderLeft: `0.12em solid ${tint(accent, 0.4)}`, paddingLeft: '1.2em' }}><Contacts d={d} color="#374151" iconColor={accent} size={0.88} /></div>
      </header>
      <div style={{ padding: '0 2.6em 2.4em' }}>
        {d.summary && <p style={{ margin: '0 0 1.2em', color: '#4b5563' }}>{d.summary}</p>}
        {h.awards && <Box t="Chứng chỉ và giấy phép hành nghề"><Bullets text={d.awards} /></Box>}
        {h.exp && <Box t="Quá trình công tác"><ExpList d={d} c={accent} /></Box>}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1em' }}>
          {h.edu && <Box t="Học vấn"><EduList d={d} /></Box>}
          {h.skills && <Box t="Chuyên môn"><Skill d={d} accent={accent} kind={v.skill || 'dots'} /></Box>}
          {h.lang && <Box t="Ngoại ngữ"><Langs d={d} /></Box>}
          {lines(d.interests).length > 0 && <Box t="Hoạt động"><Interests d={d} /></Box>}
        </div>
      </div>
    </div>
  );
};

/** F. Formal: centred name, ruled contact table, narrow right column. */
export const formal = (v: Skin = {}) => function Formal({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  const T = (t: string) => <div style={{ fontSize: '1em', fontWeight: 800, letterSpacing: '0.18em', textTransform: 'uppercase', color: '#111827', borderBottom: `0.1em solid ${accent}`, paddingBottom: '0.3em', margin: '0 0 0.8em' }}><Tr t={t} /></div>;
  const cells = [d.email, d.phone, d.address, d.website].filter(Boolean);
  return (
    <div style={{ minHeight: 'inherit', background: v.bg || '#fff', padding: '2.6em 2.8em', lineHeight: 1.5, color: ink }}>
      <header style={{ textAlign: 'center', position: 'relative' }}>
        {showPhoto && d.photo && <Photo src={d.photo} size={5.6} radius="0.3em" style={{ position: 'absolute', right: 0, top: 0 }} />}
        <div style={{ fontSize: '2.5em', fontWeight: 700, margin: 0, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#0b0f19' }}>{d.name}</div>
        <div style={{ fontSize: '1.05em', letterSpacing: '0.2em', textTransform: 'uppercase', color: accent, margin: '0.5em 0 1em', fontWeight: 600 }}>{d.title}</div>
      </header>
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${Math.max(1, cells.length)}, 1fr)`, borderTop: `0.08em solid ${accent}`, borderBottom: `0.08em solid ${accent}`, margin: '0 0 1.5em' }}>
        {cells.map((c, i) => <div key={i} style={{ padding: '0.55em 0.6em', textAlign: 'center', fontSize: '0.86em', borderLeft: i ? '0.06em solid #d1d5db' : undefined, wordBreak: 'break-word' }}>{c}</div>)}
      </div>
      {d.summary && <p style={{ margin: '0 0 1.4em', color: '#374151', textAlign: 'justify' }}>{d.summary}</p>}
      <div style={{ display: 'flex', gap: '1.8em' }}>
        <main style={{ flex: 1.9, paddingRight: '1.8em', borderRight: '0.06em solid #d1d5db' }}>
          {h.exp && <section style={{ marginBottom: '1.4em' }}>{T('Kinh nghiệm làm việc')}<ExpList d={d} c={accent} /></section>}
          {h.edu && <section style={{ marginBottom: '1.4em' }}>{T('Học vấn')}<EduList d={d} /></section>}
          {h.proj && <section>{T('Dự án')}<ProjList d={d} /></section>}
        </main>
        <aside style={{ flex: 1 }}>
          {h.skills && <section style={{ marginBottom: '1.4em' }}>{T('Kỹ năng')}<Skill d={d} accent={accent} kind={v.skill || 'dots'} /></section>}
          {h.lang && <section style={{ marginBottom: '1.4em' }}>{T('Ngoại ngữ')}<Langs d={d} /></section>}
          {h.awards && <section>{T('Chứng chỉ')}<Bullets text={d.awards} /></section>}
        </aside>
      </div>
    </div>
  );
};

/** G. Diagonal: slanted coloured header, photo overlapping the edge. */
export const diagonal = (v: Skin = {}) => function Diagonal({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d), dk = v.dark || '#0f172a';
  return (
    <div style={{ minHeight: 'inherit', background: v.bg || '#fff', lineHeight: 1.5, color: ink }}>
      <header style={{ position: 'relative', height: '12.5em', background: `linear-gradient(120deg, ${accent}, ${dk})`, clipPath: 'polygon(0 0, 100% 0, 100% 78%, 0 100%)', color: '#fff', padding: '2.3em 2.8em 0 15em' }}>
        <div style={{ fontSize: '2.6em', fontWeight: 800, margin: 0, lineHeight: 1.08 }}>{d.name}</div>
        <div style={{ fontSize: '1.15em', opacity: 0.95, fontWeight: 600, marginTop: '0.3em' }}>{d.title}</div>
      </header>
      {showPhoto && d.photo && <Photo src={d.photo} size={9.6} style={{ position: 'absolute', left: '2.4em', top: '4.6em', border: '0.3em solid #fff', boxShadow: '0 0.3em 1em rgba(0,0,0,.2)' }} />}
      <div style={{ display: 'flex', gap: '2em', padding: '0.4em 2.6em 2.4em', marginTop: showPhoto && d.photo ? '1.8em' : '-1em' }}>
        <aside style={{ width: '31%', paddingTop: showPhoto && d.photo ? '3.2em' : 0 }}>
          <Sec t="Liên hệ" c={accent}><Contacts d={d} color="#374151" iconColor={accent} size={0.9} /></Sec>
          {h.skills && <Sec t="Kỹ năng" c={accent}><Skill d={d} accent={accent} kind={v.skill || 'chips'} /></Sec>}
          {h.lang && <Sec t="Ngoại ngữ" c={accent}><Langs d={d} /></Sec>}
          {lines(d.interests).length > 0 && <Sec t="Sở thích" c={accent}><Interests d={d} /></Sec>}
        </aside>
        <main style={{ flex: 1, paddingTop: '1.6em' }}>
          {d.summary && <Sec t="Giới thiệu" c={accent}><p style={{ margin: 0, color: '#4b5563' }}>{d.summary}</p></Sec>}
          {h.exp && <Sec t="Kinh nghiệm" c={accent}><ExpList d={d} c={accent} /></Sec>}
          {h.edu && <Sec t="Học vấn" c={accent}><EduList d={d} /></Sec>}
          {h.awards && <Sec t="Thành tích" c={accent}><Bullets text={d.awards} /></Sec>}
        </main>
      </div>
    </div>
  );
};

/** H. Student: objective box, education before work, activities and interests. */
export const student = (v: Skin = {}) => function Student({ data: d, accent, showPhoto }: CvProps) {
  const h = hasAny(d);
  const T = (t: string) => <div style={{ fontWeight: 800, fontSize: '1.08em', color: '#111827', margin: '0 0 0.7em', display: 'flex', alignItems: 'center', gap: '0.6em' }}><span style={{ width: '1.7em', height: '0.3em', borderRadius: '0.2em', background: accent }} /><Tr t={t} /></div>;
  return (
    <div style={{ minHeight: 'inherit', background: v.bg || '#fff', lineHeight: 1.5, color: ink }}>
      <header style={{ display: 'flex', alignItems: 'center', gap: '1.6em', padding: '2.4em 2.8em 1.4em' }}>
        {showPhoto && d.photo && <Photo src={d.photo} size={8} radius="1.4em" style={{ boxShadow: `0.4em 0.4em 0 ${tint(accent, 0.35)}` }} />}
        <div style={{ flex: 1 }}><div style={{ fontSize: '2.5em', fontWeight: 800, margin: 0, lineHeight: 1.08, color: '#0f172a' }}>{d.name}</div><div style={{ fontSize: '1.1em', color: accent, fontWeight: 700, margin: '0.3em 0 0.9em' }}>{d.title}</div><Contacts d={d} row color="#4b5563" iconColor={accent} size={0.9} /></div>
      </header>
      <div style={{ padding: '0 2.8em 2.4em' }}>
        {d.summary && <div style={{ background: tint(accent, 0.1), borderLeft: `0.35em solid ${accent}`, borderRadius: '0.4em', padding: '0.9em 1.2em', marginBottom: '1.5em' }}><b style={{ color: accent }}><Tr t="Mục tiêu nghề nghiệp" /></b><div style={{ color: '#374151', marginTop: '0.2em' }}>{d.summary}</div></div>}
        {h.edu && <section style={{ marginBottom: '1.5em' }}>{T('Học vấn')}{d.education.map((e) => <Row key={e.id} style={{ marginBottom: '0.7em', display: 'flex', justifyContent: 'space-between', gap: '1em' }}><div><b style={{ fontSize: '1.05em' }}>{e.school}</b><div>{e.degree}</div>{e.desc && <div style={{ color: accent, fontWeight: 600, fontSize: '0.95em' }}>{e.desc}</div>}</div><D a={e.from} b={e.to} /></Row>)}</section>}
        {h.exp && <section style={{ marginBottom: '1.5em' }}>{T('Kinh nghiệm và hoạt động')}<ExpList d={d} c={accent} /></section>}
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '2em' }}>
          <div>{h.skills && <section style={{ marginBottom: '1.4em' }}>{T('Kỹ năng')}<Skill d={d} accent={accent} kind={v.skill || 'chips'} /></section>}{h.lang && <section>{T('Ngoại ngữ')}<Langs d={d} /></section>}</div>
          <div>{h.awards && <section style={{ marginBottom: '1.4em' }}>{T('Giải thưởng, học bổng')}<Bullets text={d.awards} /></section>}{lines(d.interests).length > 0 && <section>{T('Sở thích')}<Interests d={d} /></section>}</div>
        </div>
      </div>
    </div>
  );
};
