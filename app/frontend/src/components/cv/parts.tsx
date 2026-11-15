import type { CSSProperties, ReactNode } from 'react';
import { useLevels } from './levels';
import { Mail, MapPin, Phone, Globe } from 'lucide-react';
import { lines, safeUrl, shortUrl, type CvData, type CvProject, type CvStyle } from '@/lib/cv/types';

/** What every template receives. All sizes inside templates are `em`, so one font-size on the page scales the whole CV. */
export interface CvProps { data: CvData; accent: string; showPhoto: boolean }

const linkStyle: CSSProperties = { color: 'inherit', textDecoration: 'underline', textUnderlineOffset: '0.12em', wordBreak: 'break-all' };
/** One achievement / certificate line. "Name | link" makes the name clickable; a bare link in the text is clickable too. */
export function linkText(l: string): ReactNode {
  const cut = l.lastIndexOf('|');
  if (cut > 0) {
    const url = safeUrl(l.slice(cut + 1));
    if (url) return <a href={url} target="_blank" rel="noopener noreferrer" style={linkStyle}>{l.slice(0, cut).trim() || shortUrl(url)}</a>;
  }
  return l.split(/(https?:\/\/[^\s]+)/g).map((t, i) => (i % 2 && safeUrl(t) ? <a key={i} href={safeUrl(t)} target="_blank" rel="noopener noreferrer" style={linkStyle}>{shortUrl(t)}</a> : t));
}

/** Project description followed by its links (GitHub, product page...). */
export const ProjDesc = ({ p }: { p: CvProject }) => {
  const links = (p.links || []).map((k) => ({ ...k, url: safeUrl(k.url) })).filter((k) => k.url); // never trust a half-typed address
  return (
  <>
    {p.desc}
    {links.length ? (
      <span style={{ display: 'block', marginTop: '0.15em' }}>
        {links.map((k, i) => (
          <span key={k.id}>{i > 0 && '  ·  '}{k.label && `${k.label}: `}<a href={k.url} target="_blank" rel="noopener noreferrer" style={linkStyle}>{shortUrl(k.url)}</a></span>
        ))}
      </span>
    ) : null}
  </>
  );
};

export const Bullets = ({ text, gap = 0.25, color }: { text: string; gap?: number; color?: string }) => {
  const items = lines(text);
  if (!items.length) return null;
  return (
    <ul style={{ margin: '0.35em 0 0', paddingLeft: '1.1em', listStyle: 'disc', color }}>
      {items.map((l, i) => <li key={i} style={{ marginTop: `${gap}em` }}>{linkText(l)}</li>)}
    </ul>
  );
};

export const Photo = ({ src, size, radius = '50%', style }: { src: string; size: number; radius?: string; style?: CSSProperties }) => (
  // eslint-disable-next-line @next/next/no-img-element
  <img src={src} alt="" style={{ width: `${size}em`, height: `${size}em`, objectFit: 'cover', borderRadius: radius, display: 'block', ...style }} />
);

const ICONS = [Mail, Phone, MapPin, Globe];
/** Contact rows with a small icon each; `color` tints text and icons. */
export const Contacts = ({ d, color, iconColor, size = 0.95, gap = 0.55, row = false }: { d: CvData; color?: string; iconColor?: string; size?: number; gap?: number; row?: boolean }) => {
  const items = [d.email, d.phone, d.address, d.website].map((v, i) => ({ v, Icon: ICONS[i] })).filter((x) => x.v);
  return (
    <div style={{ display: 'flex', flexDirection: row ? 'row' : 'column', flexWrap: 'wrap', gap: row ? `${gap}em 1.4em` : `${gap}em`, fontSize: `${size}em`, color }}>
      {items.map(({ v, Icon }, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.55em', wordBreak: 'break-word', lineHeight: 1.35 }}>
          <Icon size={13} strokeWidth={2.2} color={iconColor || color} style={{ flex: 'none', marginTop: '0.18em' }} />
          <span>{v}</span>
        </div>
      ))}
    </div>
  );
};

/** Skill rating: horizontal bar or dots; draws nothing unless the CV style turns ratings on. */
export const Level = ({ level, kind, color, track = 'rgba(0,0,0,.12)' }: { level: number; kind: 'bar' | 'dots'; color: string; track?: string }) => {
  const on = useLevels();
  if (!on) return null;
  return kind === 'bar' ? (
    <div style={{ height: '0.4em', borderRadius: '0.4em', background: track, overflow: 'hidden' }}><div style={{ width: `${level * 20}%`, height: '100%', background: color, borderRadius: '0.4em' }} /></div>
  ) : (
    <div style={{ display: 'flex', gap: '0.28em' }}>
      {[1, 2, 3, 4, 5].map((i) => <span key={i} style={{ width: '0.62em', height: '0.62em', borderRadius: '50%', background: i <= level ? color : track }} />)}
    </div>
  );
};

export const Row = ({ children, style }: { children: ReactNode; style?: CSSProperties }) => <div style={{ breakInside: 'avoid', ...style }}>{children}</div>;

export const hasAny = (d: CvData) => ({
  exp: d.experience.length > 0, edu: d.education.length > 0, skills: d.skills.length > 0, lang: d.languages.length > 0, proj: d.projects.length > 0, awards: lines(d.awards).length > 0,
});

/** Soft tint of the accent for backgrounds. */
export const tint = (hex: string, a = 0.1) => {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`;
};

export type StyleProps = Pick<CvStyle, 'accent' | 'showPhoto'>;
