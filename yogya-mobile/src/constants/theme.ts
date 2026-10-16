/**
 * Yogya Design System
 *
 * A warm, neutral, student-friendly visual identity with an editorial,
 * handcrafted aesthetic designed for students across rural and urban India.
 *
 * Muted earth-tone palette:
 * - Main background: warm ivory (#F7F4ED)
 * - Card surface: soft white (#FFFDF8)
 * - Primary text: charcoal (#383A36)
 * - Secondary text: warm gray (#77766E)
 * - Primary accent: muted sage (#747D68) / soft sage surface (#E4E5D8)
 * - Secondary accent: muted terracotta (#B77C5C) / soft terracotta surface (#EADBCB)
 * - Borders & dividers: warm stone (#E3DED4)
 * - Semantic alerts: muted forest green, muted ochre, restrained brick red
 */

import { Platform } from 'react-native';

// ─── Color Palette ──────────────────────────────────────────────────────────

export const Palette = {
  // Main backgrounds & surfaces
  ivory: '#F7F4ED',
  softWhite: '#FFFDF8',
  warmStoneLight: '#EFECE6',
  warmStone: '#E3DED4',
  warmStoneDark: '#D4CDC2',

  // Primary text & neutrals
  charcoal: '#383A36',
  charcoalDark: '#262824',
  charcoalLight: '#4E504B',
  warmGray: '#77766E',
  warmGrayMuted: '#949289',

  // Primary accent: Muted Sage
  sage: '#747D68',
  sageDark: '#565E4C',
  sageLight: '#8E9982',
  sageSurface: '#E4E5D8',

  // Secondary accent: Muted Terracotta
  terracotta: '#B77C5C',
  terracottaDark: '#965C3E',
  terracottaLight: '#C99071',
  terracottaSurface: '#EADBCB',

  // Semantic Colors (accessible contrast against softWhite / ivory)
  forestGreen: '#3D683A',
  forestGreenDark: '#2D4E2A',
  forestGreenSurface: '#E4EDE2',

  ochre: '#8C5F1E',
  ochreDark: '#6E4913',
  ochreSurface: '#F5ECDB',

  brickRed: '#9E433C',
  brickRedDark: '#7F312B',
  brickRedSurface: '#F6E4E2',

  // General utilities
  white: '#FFFFFF',
  black: '#383A36', // Charcoal replaces harsh pure-black for accessible, softer shadows
  overlay: 'rgba(56, 58, 54, 0.45)',
  divider: '#E3DED4',
  cardBorder: '#E3DED4',

  // ─── Backward-compatibility aliases (mapped to the new earth palette) ────
  offWhite: '#F7F4ED',
  warmGray50: '#EFECE6',
  warmGray100: '#E3DED4',
  warmGray200: '#D4CDC2',
  warmGray300: '#949289',

  textPrimary: '#383A36',
  textSecondary: '#77766E',
  textMuted: '#77766E',
  textOnDark: '#F7F4ED',
  textOnTeal: '#FFFDF8',

  indigo: '#383A36',
  indigoDark: '#262824',
  indigoLight: '#565E4C',

  teal: '#747D68',
  tealDark: '#565E4C',
  tealLight: '#8E9982',
  tealSubtle: '#E4E5D8',

  saffron: '#B77C5C',
  saffronDark: '#965C3E',
  saffronLight: '#C99071',
  saffronSubtle: '#EADBCB',

  success: '#3D683A',
  successSubtle: '#E4EDE2',
  warning: '#8C5F1E',
  warningSubtle: '#F5ECDB',
  error: '#9E433C',
  errorSubtle: '#F6E4E2',
  info: '#747D68',
  infoSubtle: '#E4E5D8',
} as const;

// ─── Theme Colors ───────────────────────────────────────────────────────────

export const Colors = {
  light: {
    // Canvas & Surfaces
    background: Palette.ivory,
    backgroundElement: Palette.warmStoneLight,
    backgroundSelected: Palette.sageSurface,
    card: Palette.softWhite,
    cardBorder: Palette.warmStone,
    divider: Palette.warmStone,

    // Typography
    text: Palette.charcoal,
    textSecondary: Palette.warmGray,
    textMuted: Palette.warmGray,

    // Primary Brand (Sage)
    primary: Palette.sage,
    primaryDark: Palette.sageDark,
    primaryLight: Palette.sageLight,
    primarySubtle: Palette.sageSurface,

    // Secondary Accent (Terracotta)
    accent: Palette.terracotta,
    accentDark: Palette.terracottaDark,
    accentLight: Palette.terracottaLight,
    accentSubtle: Palette.terracottaSurface,

    // Editorial Brand Identity
    brand: Palette.charcoal,
    brandLight: Palette.sage,

    // Semantic States
    success: Palette.forestGreen,
    successSubtle: Palette.forestGreenSurface,
    warning: Palette.ochre,
    warningSubtle: Palette.ochreSurface,
    error: Palette.brickRed,
    errorSubtle: Palette.brickRedSurface,
  },
} as const;

export type ThemeColor = keyof typeof Colors.light;

// ─── Typography ─────────────────────────────────────────────────────────────

export const Fonts = Platform.select({
  ios: {
    sans: 'System',
    serif: 'Georgia',
    mono: 'Menlo',
  },
  default: {
    sans: 'normal',
    serif: 'serif',
    mono: 'monospace',
  },
});

export const FontSize = {
  xs: 12,
  sm: 14,
  base: 16,
  lg: 18,
  xl: 20,
  '2xl': 24,
  '3xl': 30,
  '4xl': 36,
  '5xl': 48,
} as const;

export const FontWeight = {
  normal: '400' as const,
  medium: '500' as const,
  semibold: '600' as const,
  bold: '700' as const,
  extrabold: '800' as const,
};

export const LineHeight = {
  tight: 1.2,
  snug: 1.35,
  normal: 1.5,
  relaxed: 1.65,
} as const;

// ─── Spacing ────────────────────────────────────────────────────────────────

export const Spacing = {
  /** 2px */
  half: 2,
  /** 4px */
  one: 4,
  /** 8px */
  two: 8,
  /** 12px */
  twoHalf: 12,
  /** 16px */
  three: 16,
  /** 20px */
  threeHalf: 20,
  /** 24px */
  four: 24,
  /** 32px */
  five: 32,
  /** 40px */
  fiveHalf: 40,
  /** 48px */
  six: 48,
  /** 64px */
  seven: 64,
  /** 80px */
  eight: 80,
} as const;

// ─── Border Radius ──────────────────────────────────────────────────────────

export const BorderRadius = {
  sm: 6,
  md: 10,
  lg: 14,
  xl: 20,
  '2xl': 28,
  full: 9999,
} as const;

// ─── Restrained Earthy Shadows ──────────────────────────────────────────────

export const Shadows = {
  sm: {
    shadowColor: Palette.charcoal,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
    elevation: 1,
  },
  md: {
    shadowColor: Palette.charcoal,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.07,
    shadowRadius: 6,
    elevation: 2,
  },
  lg: {
    shadowColor: Palette.charcoal,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.09,
    shadowRadius: 12,
    elevation: 4,
  },
} as const;

// ─── Layout ─────────────────────────────────────────────────────────────────

export const BottomTabInset = Platform.select({ ios: 50, android: 80 }) ?? 0;
export const MaxContentWidth = 600;
export const ScreenPadding = Spacing.four;
