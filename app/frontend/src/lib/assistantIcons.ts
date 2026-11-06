import { Shuffle, BookOpen, Building2, Feather, FlaskConical, Gavel, Headset, HeartPulse, Inbox, MapPin, Microscope, Plane, School, Wallet, Bot, Briefcase, GraduationCap, Languages, PenLine, Sparkles, ClipboardCheck, Calculator, CalendarCheck, FileText, Kanban, Landmark, Layers, ListChecks, NotebookPen, Presentation, Scale, ShieldCheck, Terminal, TrendingUp, Users, type LucideIcon } from 'lucide-react'

/** Tên icon (kiểu lucide, kebab-case) do máy chủ trả về -> component React. Không có thì dùng Bot. */
const MAP: Record<string, LucideIcon> = {
  'file-text': FileText, landmark: Landmark, layers: Layers, 'calendar-check': CalendarCheck, calculator: Calculator, users: Users,
  presentation: Presentation, kanban: Kanban, scale: Scale, terminal: Terminal, bot: Bot, 'shield-check': ShieldCheck,
  'notebook-pen': NotebookPen, 'trending-up': TrendingUp, 'list-checks': ListChecks, 'graduation-cap': GraduationCap, languages: Languages, 'pen-line': PenLine, briefcase: Briefcase, sparkles: Sparkles, 'clipboard-check': ClipboardCheck,
  'book-open': BookOpen, 'building-2': Building2, feather: Feather, 'flask-conical': FlaskConical, gavel: Gavel, headset: Headset, 'heart-pulse': HeartPulse,
  shuffle: Shuffle, inbox: Inbox, 'map-pin': MapPin, microscope: Microscope, plane: Plane, school: School, wallet: Wallet,
}

export const assistantIcon = (name: string): LucideIcon => MAP[name] ?? Bot
