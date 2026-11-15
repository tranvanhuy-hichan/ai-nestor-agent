'use client';
import { createContext, useContext } from 'react';

/** Whether skill ratings (bars, dots, rings) are drawn. Provided by CvPaper from the style; off by default. */
export const LevelsCtx = createContext(false);
export const useLevels = () => useContext(LevelsCtx);
