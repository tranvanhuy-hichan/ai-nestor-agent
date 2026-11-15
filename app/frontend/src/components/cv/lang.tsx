'use client';
import { createContext, useContext } from 'react';
import { trLabel, type CvLang } from '@/lib/cv/i18n';

/** Language of the CV being drawn. Provided by CvPaper from the style. */
export const LangCtx = createContext<CvLang>('vi');
export const useCvLang = () => useContext(LangCtx);
/** A fixed heading written in Vietnamese in the template, shown in the CV language. */
export const Tr = ({ t }: { t: string }) => <>{trLabel(useContext(LangCtx), t)}</>;
