import { Tr } from '../lang';
import type { CSSProperties, ReactNode } from 'react';
import { Bullets, Contacts, Level, Photo, Row, hasAny, tint, type CvProps, ProjDesc } from '../parts';
import { useLevels } from '../levels';
import { dateRange, type CvData } from '@/lib/cv/types';

/**
 * Parametric layouts: one engine, many looks. A template is just an `Opt` (layout + colours + heading / skill / photo styles),
 * which keeps 20+ designs small and consistent. Hand-drawn one-offs live in a.tsx, b.tsx and c.tsx.
 */
export interface Opt {
  layout: 'side' | 'top' | 'cards' | 'bigname' | 'single';
  /** page background */
  bg?: string;
  /** sidebar look (layout 'side') */
  side?: 'accent' | 'tint' | 'dark' | 'light' | 'gradient';
  sideRight?: boolean;
  /** colour of text on an 'accent' sidebar (default white) */
  sideInk?: string;
  /** dark colour used by dark sidebars / headers */
  dark?: string;
  head?: 'bar' | 'underline' | 'pill' | 'dot' | 'caps' | 'box' | 'center';
  skill?: 'bar' | 'dots' | 'chips' | 'ring' | 'plain';
  photo?: 'circle' | 'rounded' | 'square' | 'arch' | 'blob';
  /** header look (layout 'top') */
  hdr?: 'band' | 'gradient' | 'dark' | 'arch' | 'plain';
  /** corner radius in em for cards */
  radius?: number;
  /** education sits in the sidebar / side column */
  eduSide?: boolean;
  /** body columns under a 'top' header */
  cols?: 1 | 2;
  /** single layout: centred header */
  center?: boolean;
  /** serif-ish roman numerals etc. are not needed; keep names in capitals */
  upper?: boolean;
  /** sidebar width in % (layout 'side', default 32) */
  sideW?: number;
  /** accent rule under the name block (layout 'side') */
  nameRule?: boolean;
  /** layout 'top': narrow column on the left instead of the right */
  asideLeft?: boolean;
}

interface C { accent: string; ink: string; muted: string; onDark: boolean; line: string }
const light: Omit<C, 'accent'> = { ink: '#1f2937', muted: '#6b7280', onDark: false, line: '#e5e7eb' };
const dark: Omit<C, 'accent'> = { ink: '#f1f5f9', muted: 'rgba(241,245,249,.7)', onDark: true, line: 'rgba(255,255,255,.2)' };

const RADIUS: Record<NonNullable<Opt['photo']>, string> = { circle: '50%', rounded: '1.6em', square: '0.35em', arch: '99em 99em 0.4em 0.4em', blob: '42% 58% 55% 45% / 52% 44% 56% 48%' };
const shape = (o: Opt) => RADIUS[o.photo || 'circle'];

function Head({ t, c, o }: { t: string; c: C; o: Opt }) {
  const col = c.onDark ? '#fff' : '#111827';
  const base: CSSProperties = { margin: '0 0 0.75em' };
  switch (o.head || 'bar') {
    case 'underline': return <div style={{ ...base, fontWeight: 800, fontSize: '1.08em', color: col, paddingBottom: '0.3em', borderBottom: `0.14em solid ${c.accent}` }}><Tr t={t} /></div>;
    case 'pill': return <div style={{ ...base, display: 'inline-block', background: c.accent, color: '#fff', fontWeight: 700, fontSize: '0.95em', padding: '0.28em 1.1em', borderRadius: '2em' }}><Tr t={t} /></div>;
    case 'dot': return <div style={{ ...base, fontWeight: 800, fontSize: '1.05em', color: c.onDark ? '#fff' : c.accent, display: 'flex', alignItems: 'center', gap: '0.5em' }}><span style={{ width: '0.65em', height: '0.65em', borderRadius: '50%', background: c.accent }} /><Tr t={t} /></div>;
    case 'caps': return <div style={{ ...base, fontWeight: 800, fontSize: '0.98em', letterSpacing: '0.16em', textTransform: 'uppercase', color: c.onDark ? '#fff' : c.accent }}><Tr t={t} /></div>;
    case 'box': return <div style={{ ...base, display: 'block', background: c.onDark ? 'rgba(255,255,255,.14)' : '#111827', color: '#fff', fontWeight: 700, fontSize: '0.9em', letterSpacing: '0.12em', textTransform: 'uppercase', padding: '0.35em 0.9em', borderLeft: `0.35em solid ${c.accent}` }}><Tr t={t} /></div>;
    case 'center': return <div style={{ ...base, display: 'flex', alignItems: 'center', gap: '0.9em', fontWeight: 700, letterSpacing: '0.2em', textTransform: 'uppercase', fontSize: '0.95em', color: c.onDark ? '#fff' : c.accent }}><span style={{ flex: 1, height: 1, background: c.line }} /><Tr t={t} /><span style={{ flex: 1, height: 1, background: c.line }} /></div>;
    default: return <div style={{ ...base, fontWeight: 800, fontSize: '1.08em', color: col, borderLeft: `0.3em solid ${c.accent}`, paddingLeft: '0.6em' }}><Tr t={t} /></div>;
  }
}

const Skills = ({ d, c, o }: { d: CvData; c: C; o: Opt }) => {
  const lv = useLevels();
  // without ratings, bar / dot / ring styles fall back to plain skill tags
  const k = lv ? o.skill || 'bar' : o.skill === 'plain' ? 'plain' : 'chips';
  const track = c.onDark ? 'rgba(255,255,255,.25)' : tint(c.accent, 0.18);
  if (k === 'chips') return <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4em' }}>{d.skills.map((s) => <span key={s.id} style={{ background: c.onDark ? 'rgba(255,255,255,.16)' : tint(c.accent, 0.12), color: c.ink, borderRadius: '2em', padding: '0.15em 0.8em', fontSize: '0.92em', fontWeight: 600 }}>{s.name}</span>)}</div>;
  if (k === 'plain') return <div style={{ color: c.ink }}>{d.skills.map((s) => <div key={s.id} style={{ marginBottom: '0.25em' }}>{s.name}</div>)}</div>;
  if (k === 'ring') {
    const r = 15, len = 2 * Math.PI * r;
    return <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.8em 0.5em' }}>{d.skills.map((s) => (
      <div key={s.id} style={{ textAlign: 'center' }}>
        <svg width="2.8em" height="2.8em" viewBox="0 0 40 40"><circle cx="20" cy="20" r={r} fill="none" stroke={track} strokeWidth="4" /><circle cx="20" cy="20" r={r} fill="none" stroke={c.onDark ? '#fff' : c.accent} strokeWidth="4" strokeLinecap="round" strokeDasharray={`${(len * s.level) / 5} ${len}`} transform="rotate(-90 20 20)" /></svg>
        <div style={{ fontSize: '0.8em', fontWeight: 600, lineHeight: 1.2, color: c.ink }}>{s.name}</div>
      </div>))}</div>;
  }
  return <div style={{ display: 'flex', flexDirection: 'column', gap: k === 'bar' ? '0.7em' : '0.5em' }}>{d.skills.map((s) => k === 'bar'
    ? <div key={s.id}><div style={{ fontSize: '0.93em', fontWeight: 600, marginBottom: '0.25em', color: c.ink }}>{s.name}</div><Level level={s.level} kind="bar" color={c.onDark ? '#fff' : c.accent} track={track} /></div>
    : <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.8em', color: c.ink }}><span style={{ fontSize: '0.95em' }}>{s.name}</span><Level level={s.level} kind="dots" color={c.onDark ? '#fff' : c.accent} track={track} /></div>)}</div>;
};

const Exp = ({ d, c }: { d: CvData; c: C }) => <>{d.experience.map((e) => (
  <Row key={e.id} style={{ marginBottom: '1.05em' }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1em' }}><b style={{ fontSize: '1.07em', color: c.onDark ? '#fff' : '#111827' }}>{e.role}</b><span style={{ color: c.muted, fontSize: '0.9em', whiteSpace: 'nowrap' }}>{dateRange(e.from, e.to)}</span></div>
    <div style={{ color: c.accent, fontWeight: 600 }}>{e.company}</div><Bullets text={e.desc} color={c.ink} />
  </Row>))}</>;
const Edu = ({ d, c }: { d: CvData; c: C }) => <>{d.education.map((e) => (
  <Row key={e.id} style={{ marginBottom: '0.8em' }}><b style={{ color: c.onDark ? '#fff' : '#111827' }}>{e.school}</b><div style={{ fontSize: '0.95em', color: c.ink }}>{e.degree}</div><div style={{ color: c.muted, fontSize: '0.88em' }}>{dateRange(e.from, e.to)}</div>{e.desc && <div style={{ color: c.muted, fontSize: '0.9em' }}>{e.desc}</div>}</Row>))}</>;
const Proj = ({ d, c }: { d: CvData; c: C }) => <>{d.projects.map((p) => <Row key={p.id} style={{ marginBottom: '0.6em' }}><b style={{ color: c.onDark ? '#fff' : '#111827' }}>{p.name}</b><div style={{ color: c.ink, opacity: 0.85 }}><ProjDesc p={p} /></div></Row>)}</>;
const Lang = ({ d, c }: { d: CvData; c: C }) => <>{d.languages.map((l) => <div key={l.id} style={{ marginBottom: '0.35em', color: c.ink }}><b>{l.name}</b>{l.level && <span style={{ color: c.muted }}> · {l.level}</span>}</div>)}</>;

/** The sections of a CV as [title, node] so layouts can place them anywhere. */
function parts(d: CvData, c: C, o: Opt) {
  const h = hasAny(d);
  return {
    contact: ['Liên hệ', <Contacts key="c" d={d} color={c.ink} iconColor={c.onDark ? '#fff' : c.accent} />] as const,
    exp: h.exp ? ['Kinh nghiệm làm việc', <Exp key="e" d={d} c={c} />] as const : null,
    edu: h.edu ? ['Học vấn', <Edu key="u" d={d} c={c} />] as const : null,
    skills: h.skills ? ['Kỹ năng', <Skills key="s" d={d} c={c} o={o} />] as const : null,
    lang: h.lang ? ['Ngoại ngữ', <Lang key="l" d={d} c={c} />] as const : null,
    proj: h.proj ? ['Dự án', <Proj key="p" d={d} c={c} />] as const : null,
    awards: h.awards ? ['Thành tích và chứng chỉ', <Bullets key="a" text={d.awards} color={c.ink} />] as const : null,
  };
}
type Sec = readonly [string, ReactNode] | null;
const Secs = ({ list, c, o, gap = '1.5em' }: { list: Sec[]; c: C; o: Opt; gap?: string }) => <>{list.filter(Boolean).map((s) => <section key={s![0]} style={{ marginBottom: gap }}><Head t={s![0]} c={c} o={o} />{s![1]}</section>)}</>;

const nameCss = (o: Opt, color: string, size = '2.6em'): CSSProperties => ({ fontSize: size, fontWeight: 800, margin: 0, lineHeight: 1.08, color, textTransform: o.upper ? 'uppercase' : 'none', letterSpacing: o.upper ? '0.03em' : undefined });

export function Engine({ data: d, accent, showPhoto, o }: CvProps & { o: Opt }) {
  const L: C = { ...light, accent };
  const photoOn = showPhoto && !!d.photo;
  const pic = (size: number, style?: CSSProperties) => photoOn ? <Photo src={d.photo} size={size} radius={shape(o)} style={o.photo === 'arch' ? { height: `${size * 1.3}em`, ...style } : style} /> : null;
  const darkBg = o.dark || '#0f172a';

  if (o.layout === 'side') {
    const sideBg = { accent: accent, tint: tint(accent, 0.1), dark: darkBg, light: '#f3f4f6', gradient: `linear-gradient(165deg, ${accent}, ${darkBg})` }[o.side || 'tint'];
    const onDark = o.side === 'accent' || o.side === 'dark' || o.side === 'gradient';
    const SC: C = onDark ? { ...dark, accent: o.side === 'dark' ? accent : '#fff', ink: o.side === 'accent' ? (o.sideInk || '#fff') : dark.ink } : { ...light, accent };
    const sp = parts(d, SC, o), mp = parts(d, L, o);
    const side = (
      <aside style={{ width: `${o.sideW ?? 32}%`, background: sideBg, padding: '2.6em 1.6em', display: 'flex', flexDirection: 'column', gap: '1.5em', color: SC.ink }}>
        {pic(8.6, { alignSelf: 'center', border: onDark ? '0.25em solid rgba(255,255,255,.5)' : undefined })}
        <section><Head t="Liên hệ" c={SC} o={o} />{sp.contact[1]}</section>
        {o.eduSide && sp.edu && <section><Head t={sp.edu[0]} c={SC} o={o} />{sp.edu[1]}</section>}
        {sp.skills && <section><Head t={sp.skills[0]} c={SC} o={o} />{sp.skills[1]}</section>}
        {sp.lang && <section><Head t={sp.lang[0]} c={SC} o={o} />{sp.lang[1]}</section>}
      </aside>
    );
    const main = (
      <main style={{ flex: 1, padding: '2.6em 2.2em' }}>
        <div style={nameCss(o, L.onDark ? '#fff' : '#0f172a')}>{d.name}</div>
        <div style={{ fontSize: '1.15em', fontWeight: 600, color: accent, margin: '0.35em 0 1em', paddingBottom: o.nameRule ? '0.8em' : 0, borderBottom: o.nameRule ? `0.16em solid ${accent}` : undefined }}>{d.title}</div>
        {d.summary && <p style={{ margin: '0 0 1.6em', color: '#4b5563' }}>{d.summary}</p>}
        <Secs c={L} o={o} list={[mp.exp, o.eduSide ? null : mp.edu, mp.proj, mp.awards]} />
      </main>
    );
    return <div style={{ display: 'flex', minHeight: 'inherit', background: o.bg || '#fff', color: '#1f2937', lineHeight: 1.5 }}>{o.sideRight ? <>{main}{side}</> : <>{side}{main}</>}</div>;
  }

  if (o.layout === 'top') {
    const hdr = o.hdr || 'band';
    const hdrBg = { band: accent, gradient: `linear-gradient(115deg, ${accent}, ${darkBg})`, dark: darkBg, arch: tint(accent, 0.12), plain: 'transparent' }[hdr];
    const HC: C = hdr === 'arch' || hdr === 'plain' ? L : { ...dark, accent: hdr === 'dark' ? accent : '#fff', ink: '#fff', muted: 'rgba(255,255,255,.8)' };
    const mp = parts(d, L, o);
    const two = (o.cols ?? 2) === 2;
    return (
      <div style={{ minHeight: 'inherit', background: o.bg || '#fff', color: '#1f2937', lineHeight: 1.5 }}>
        <header style={{ background: hdrBg, padding: '2.4em 2.8em', display: 'flex', alignItems: 'center', gap: '1.7em', borderBottom: hdr === 'plain' ? `0.2em solid ${accent}` : undefined }}>
          {hdr !== 'arch' && pic(7.4, { border: HC.onDark ? '0.22em solid rgba(255,255,255,.55)' : undefined })}
          <div style={{ flex: 1 }}>
            <div style={nameCss(o, HC.onDark ? '#fff' : '#0f172a', '2.7em')}>{d.name}</div>
            <div style={{ fontSize: '1.18em', fontWeight: 600, color: HC.onDark && hdr !== 'dark' ? 'rgba(255,255,255,.95)' : accent, margin: '0.3em 0 0.9em' }}>{d.title}</div>
            <Contacts d={d} row color={HC.onDark ? '#fff' : '#4b5563'} iconColor={HC.onDark ? (hdr === 'dark' ? accent : '#fff') : accent} size={0.9} />
          </div>
          {hdr === 'arch' && pic(8.6, { alignSelf: 'flex-end', marginBottom: '-2.4em', border: `0.25em solid #fff` })}
        </header>
        <div style={{ display: 'flex', gap: '2.2em', padding: '2em 2.8em 2.6em', paddingTop: hdr === 'arch' ? '3.4em' : '2em' }}>
          <main style={{ flex: two ? 1.75 : 1 }}>
            {d.summary && <section style={{ marginBottom: '1.5em' }}><Head t="Giới thiệu" c={L} o={o} /><p style={{ margin: 0, color: '#4b5563' }}>{d.summary}</p></section>}
            <Secs c={L} o={o} list={[mp.exp, ...(two ? [mp.proj] : [mp.edu, mp.skills, mp.lang, mp.proj, mp.awards])]} />
          </main>
          {two && <aside style={{ flex: 1, order: o.asideLeft ? -1 : 0, ...(o.side === 'tint' ? { background: tint(accent, 0.08), padding: '1.4em', borderRadius: '0.8em', alignSelf: 'flex-start' } : {}) }}><Secs c={L} o={o} list={[mp.edu, mp.skills, mp.lang, mp.awards]} /></aside>}
        </div>
      </div>
    );
  }

  if (o.layout === 'cards') {
    const mp = parts(d, L, o);
    const r = `${o.radius ?? 1}em`;
    const Card = ({ s }: { s: Sec }) => s ? <section style={{ background: '#fff', borderRadius: r, padding: '1.15em 1.35em', boxShadow: '0 1px 3px rgba(15,23,42,.1)', breakInside: 'avoid' }}><Head t={s[0]} c={L} o={o} />{s[1]}</section> : null;
    return (
      <div style={{ minHeight: 'inherit', background: o.bg || '#eef1f6', padding: '1.7em', display: 'flex', flexDirection: 'column', gap: '1em', color: '#1f2937', lineHeight: 1.5 }}>
        <header style={{ background: accent, color: '#fff', borderRadius: r, padding: '1.7em 2em', display: 'flex', alignItems: 'center', gap: '1.5em' }}>
          {pic(7, { border: '0.22em solid rgba(255,255,255,.6)' })}
          <div style={{ flex: 1 }}><div style={nameCss(o, '#fff', '2.4em')}>{d.name}</div><div style={{ fontSize: '1.12em', opacity: 0.95, margin: '0.3em 0 0.8em' }}>{d.title}</div><Contacts d={d} row color="#fff" size={0.88} /></div>
        </header>
        {d.summary && <Card s={['Giới thiệu', <p key="s" style={{ margin: 0, color: '#4b5563' }}>{d.summary}</p>]} />}
        <div style={{ display: 'flex', gap: '1em', alignItems: 'flex-start' }}>
          <div style={{ flex: 1.75, display: 'flex', flexDirection: 'column', gap: '1em' }}><Card s={mp.exp} /><Card s={mp.proj} /></div>
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1em' }}><Card s={mp.edu} /><Card s={mp.skills} /><Card s={mp.lang} /><Card s={mp.awards} /></div>
        </div>
      </div>
    );
  }

  if (o.layout === 'bigname') {
    const mp = parts(d, L, o);
    const words = d.name.trim().split(/\s+/);
    const last = words.length > 1 ? words.slice(-1)[0] : '', first = words.length > 1 ? words.slice(0, -1).join(' ') : d.name;
    return (
      <div style={{ minHeight: 'inherit', background: o.bg || '#f3ebe3', padding: '2.6em 2.8em', color: '#3f3a36', lineHeight: 1.5 }}>
        <header style={{ display: 'flex', alignItems: 'center', gap: '1.6em' }}>
          {o.sideRight ? null : pic(8.6)}
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: '2.2em', fontWeight: 300, lineHeight: 1, textTransform: 'uppercase', letterSpacing: '0.04em', color: '#3f3a36' }}>{first}</div>
            {last && <div style={{ fontSize: '3.5em', fontWeight: 800, lineHeight: 1.02, textTransform: 'uppercase', color: accent }}>{last}</div>}
            <div style={{ marginTop: '0.7em', fontWeight: 700, letterSpacing: '0.18em', textTransform: 'uppercase', fontSize: '0.95em' }}>{d.title}</div>
          </div>
          {o.sideRight ? pic(8.6) : null}
        </header>
        {d.summary && <p style={{ margin: '1.3em 0 0', color: '#57534e' }}>{d.summary}</p>}
        <div style={{ height: '0.1em', background: tint(accent, 0.35), margin: '1.5em 0' }} />
        <div style={{ display: 'flex', gap: '2em' }}>
          <aside style={{ flex: 1 }}>
            <section style={{ marginBottom: '1.5em' }}><Head t="Liên hệ" c={L} o={o} /><Contacts d={d} color="#3f3a36" iconColor={accent} size={0.92} /></section>
            <Secs c={L} o={o} list={[mp.edu, mp.skills, mp.lang]} />
          </aside>
          <main style={{ flex: 1.9 }}><Secs c={L} o={o} list={[mp.exp, mp.proj, mp.awards]} /></main>
        </div>
      </div>
    );
  }

  // single column
  const mp = parts(d, L, o);
  const centered = !!o.center;
  return (
    <div style={{ minHeight: 'inherit', background: o.bg || '#fff', padding: '2.8em 3em', color: '#1f2937', lineHeight: 1.5 }}>
      <header style={{ display: 'flex', flexDirection: centered ? 'column' : 'row', alignItems: 'center', gap: '1.4em', textAlign: centered ? 'center' : 'left', paddingBottom: '1.3em', borderBottom: `0.18em solid ${accent}` }}>
        {pic(7)}
        <div style={{ flex: 1 }}>
          <div style={nameCss(o, '#0f172a', '2.6em')}>{d.name}</div>
          <div style={{ fontSize: '1.15em', fontWeight: 600, color: accent, margin: '0.3em 0 0.8em' }}>{d.title}</div>
          <div style={{ display: 'flex', justifyContent: centered ? 'center' : 'flex-start' }}><Contacts d={d} row color="#4b5563" iconColor={accent} size={0.9} /></div>
        </div>
      </header>
      {d.summary && <p style={{ margin: '1.3em 0 1.5em', color: '#4b5563' }}>{d.summary}</p>}
      <Secs c={L} o={o} list={[mp.exp, mp.edu, mp.skills, mp.lang, mp.proj, mp.awards]} />
    </div>
  );
}

export const mk = (o: Opt) => function Tpl(p: CvProps) { return <Engine {...p} o={o} />; };
