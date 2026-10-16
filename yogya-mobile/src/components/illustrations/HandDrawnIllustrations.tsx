/**
 * HandDrawnIllustrations — Editorial, handcrafted SVG illustration components.
 *
 * Warm, approachable visuals inspired by:
 * - Education (open books, graduation cap)
 * - Growth (seedling / sprouting plant)
 * - Applications (document with pencil)
 * - Vocational skills (toolbox, craft tools)
 * - Career exploration (person on pathway toward goal)
 * - Saved bookmarks (stack of papers / journals)
 * - Welcome landscape & empty states (friendly sun over terraced hills)
 */

import React from 'react';
import Svg, {
  Circle,
  Ellipse,
  G,
  Line,
  Path,
  Polygon,
  Rect,
} from 'react-native-svg';

import { Palette } from '@/constants/theme';

interface IllustrationProps {
  width?: number;
  height?: number;
  style?: any;
}

/**
 * Welcome Hero Illustration:
 * Handcrafted sunrise over gentle terraced hills with a sprouting plant and open book.
 */
export function WelcomeHeroIllustration({
  width = 220,
  height = 140,
  style,
}: IllustrationProps) {
  return (
    <Svg
      width={width}
      height={height}
      viewBox="0 0 220 140"
      fill="none"
      style={style}
      accessible={false}
      importantForAccessibility="no"
    >
      {/* Warm gentle sun */}
      <Circle
        cx="110"
        cy="52"
        r="28"
        fill={Palette.terracottaSurface}
        stroke={Palette.terracotta}
        strokeWidth="1.5"
      />
      {/* Sun rays */}
      <Line
        x1="110"
        y1="16"
        x2="110"
        y2="10"
        stroke={Palette.terracotta}
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <Line
        x1="138"
        y1="26"
        x2="143"
        y2="21"
        stroke={Palette.terracotta}
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <Line
        x1="82"
        y1="26"
        x2="77"
        y2="21"
        stroke={Palette.terracotta}
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <Line
        x1="146"
        y1="52"
        x2="152"
        y2="52"
        stroke={Palette.terracotta}
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <Line
        x1="74"
        y1="52"
        x2="68"
        y2="52"
        stroke={Palette.terracotta}
        strokeWidth="1.5"
        strokeLinecap="round"
      />

      {/* Background gentle hill */}
      <Path
        d="M20 135 C60 85, 100 80, 160 115 L200 135 Z"
        fill={Palette.sageSurface}
        opacity={0.8}
      />

      {/* Foreground terrace hill */}
      <Path
        d="M10 135 C70 95, 140 95, 210 135 L210 140 L10 140 Z"
        fill={Palette.warmStoneLight}
        stroke={Palette.warmStone}
        strokeWidth="1.5"
      />

      {/* Open notebook / journal at the center */}
      <G transform="translate(68, 78)">
        {/* Left page */}
        <Path
          d="M42 32 C30 32, 12 36, 4 40 L4 12 C12 8, 30 5, 42 6 Z"
          fill={Palette.softWhite}
          stroke={Palette.charcoal}
          strokeWidth="1.5"
          strokeLinejoin="round"
        />
        {/* Right page */}
        <Path
          d="M42 32 C54 32, 72 36, 80 40 L80 12 C72 8, 54 5, 42 6 Z"
          fill={Palette.softWhite}
          stroke={Palette.charcoal}
          strokeWidth="1.5"
          strokeLinejoin="round"
        />
        {/* Spine */}
        <Line
          x1="42"
          y1="5"
          x2="42"
          y2="33"
          stroke={Palette.charcoal}
          strokeWidth="1.5"
        />
        {/* Subtle text lines on left page */}
        <Line x1="12" y1="16" x2="34" y2="15" stroke={Palette.warmStoneDark} strokeWidth="1" strokeLinecap="round" />
        <Line x1="12" y1="22" x2="30" y2="21" stroke={Palette.warmStoneDark} strokeWidth="1" strokeLinecap="round" />
        {/* Subtle text lines on right page */}
        <Line x1="50" y1="15" x2="72" y2="16" stroke={Palette.warmStoneDark} strokeWidth="1" strokeLinecap="round" />
        <Line x1="50" y1="21" x2="68" y2="22" stroke={Palette.warmStoneDark} strokeWidth="1" strokeLinecap="round" />

        {/* Small sprouting seedling in front of the book */}
        <Path
          d="M42 22 Q42 12, 40 2"
          stroke={Palette.forestGreen}
          strokeWidth="1.5"
          strokeLinecap="round"
        />
        {/* Left leaf */}
        <Path
          d="M40 8 C34 5, 33 0, 40 4 Z"
          fill={Palette.forestGreenSurface}
          stroke={Palette.forestGreen}
          strokeWidth="1.2"
        />
        {/* Right leaf */}
        <Path
          d="M40 5 C46 2, 47 -2, 40 2 Z"
          fill={Palette.forestGreenSurface}
          stroke={Palette.forestGreen}
          strokeWidth="1.2"
        />
      </G>
    </Svg>
  );
}

/**
 * Education Illustration:
 * Hand-drawn graduation cap and open book in muted sage and charcoal.
 */
export function EducationIllustration({
  width = 64,
  height = 64,
  style,
}: IllustrationProps) {
  return (
    <Svg
      width={width}
      height={height}
      viewBox="0 0 64 64"
      fill="none"
      style={style}
      accessible={false}
      importantForAccessibility="no"
    >
      {/* Background circle badge */}
      <Circle cx="32" cy="32" r="28" fill={Palette.sageSurface} />

      {/* Graduation cap cap-top */}
      <Polygon
        points="32,16 50,23 32,30 14,23"
        fill={Palette.softWhite}
        stroke={Palette.charcoal}
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      {/* Skull cap underneath */}
      <Path
        d="M22 26.5 V33 C22 37, 42 37, 42 33 V26.5"
        fill={Palette.sageSurface}
        stroke={Palette.charcoal}
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      {/* Tassel */}
      <Path
        d="M48 23.5 C50 26, 52 29, 52 35"
        stroke={Palette.terracotta}
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <Circle cx="52" cy="36" r="1.5" fill={Palette.terracotta} />

      {/* Open book underneath */}
      <Path
        d="M32 46 C24 44, 16 46, 12 48 L12 39 C16 37, 24 37, 32 39 C40 37, 48 37, 52 39 L52 48 C48 46, 40 44, 32 46 Z"
        fill={Palette.softWhite}
        stroke={Palette.charcoal}
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      <Line x1="32" y1="39" x2="32" y2="46" stroke={Palette.charcoal} strokeWidth="1.5" />
    </Svg>
  );
}

/**
 * Growth / Seedling Illustration:
 * A healthy little sprout emerging from warm soil.
 */
export function GrowthIllustration({
  width = 64,
  height = 64,
  style,
}: IllustrationProps) {
  return (
    <Svg
      width={width}
      height={height}
      viewBox="0 0 64 64"
      fill="none"
      style={style}
      accessible={false}
      importantForAccessibility="no"
    >
      <Circle cx="32" cy="32" r="28" fill={Palette.forestGreenSurface} />

      {/* Soil mound */}
      <Path
        d="M16 48 C22 42, 42 42, 48 48 Z"
        fill={Palette.terracottaSurface}
        stroke={Palette.terracottaDark}
        strokeWidth="1.5"
      />

      {/* Stem */}
      <Path
        d="M32 44 Q31 32, 33 20"
        stroke={Palette.forestGreen}
        strokeWidth="2"
        strokeLinecap="round"
      />

      {/* Left Leaf */}
      <Path
        d="M32 32 C22 30, 18 20, 26 19 C31 18, 32 26, 32 32 Z"
        fill={Palette.softWhite}
        stroke={Palette.forestGreen}
        strokeWidth="1.5"
      />
      {/* Right Leaf */}
      <Path
        d="M33 26 C42 22, 46 14, 38 13 C33 12, 32 20, 33 26 Z"
        fill={Palette.softWhite}
        stroke={Palette.forestGreen}
        strokeWidth="1.5"
      />
    </Svg>
  );
}

/**
 * Vocational / Tool Illustration:
 * Hand-drawn tools (wrench, ruler, draft pencil) for skill training.
 */
export function VocationalIllustration({
  width = 64,
  height = 64,
  style,
}: IllustrationProps) {
  return (
    <Svg
      width={width}
      height={height}
      viewBox="0 0 64 64"
      fill="none"
      style={style}
      accessible={false}
      importantForAccessibility="no"
    >
      <Circle cx="32" cy="32" r="28" fill={Palette.terracottaSurface} />

      {/* Tool box container */}
      <Rect
        x="18"
        y="26"
        width="28"
        height="20"
        rx="4"
        fill={Palette.softWhite}
        stroke={Palette.charcoal}
        strokeWidth="1.5"
      />
      {/* Handle */}
      <Path
        d="M26 26 V20 C26 18, 38 18, 38 20 V26"
        stroke={Palette.charcoal}
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      {/* Center latch */}
      <Rect
        x="29"
        y="30"
        width="6"
        height="6"
        rx="1"
        fill={Palette.terracotta}
        stroke={Palette.charcoal}
        strokeWidth="1"
      />
      {/* Wrench head sticking out */}
      <Path
        d="M23 20 L21 14 C19 14, 18 16, 17 18 L20 22"
        stroke={Palette.sageDark}
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      {/* Screwdriver tip */}
      <Path
        d="M42 21 L45 13"
        stroke={Palette.terracottaDark}
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </Svg>
  );
}

/**
 * Document & Pencil Illustration:
 * Checklist application with pencil for applications & schemes.
 */
export function DocumentPencilIllustration({
  width = 64,
  height = 64,
  style,
}: IllustrationProps) {
  return (
    <Svg
      width={width}
      height={height}
      viewBox="0 0 64 64"
      fill="none"
      style={style}
      accessible={false}
      importantForAccessibility="no"
    >
      <Circle cx="32" cy="32" r="28" fill={Palette.warmStoneLight} />

      {/* Document page */}
      <Rect
        x="19"
        y="15"
        width="24"
        height="32"
        rx="3"
        fill={Palette.softWhite}
        stroke={Palette.charcoal}
        strokeWidth="1.5"
      />
      {/* Lines on page */}
      <Line x1="24" y1="22" x2="36" y2="22" stroke={Palette.warmStoneDark} strokeWidth="1.5" strokeLinecap="round" />
      <Line x1="24" y1="28" x2="34" y2="28" stroke={Palette.warmStoneDark} strokeWidth="1.5" strokeLinecap="round" />
      <Line x1="24" y1="34" x2="32" y2="34" stroke={Palette.warmStoneDark} strokeWidth="1.5" strokeLinecap="round" />

      {/* Checkmarks */}
      <Path d="M37 28 L39 30 L43 26" stroke={Palette.forestGreen} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />

      {/* Handcrafted pencil crossing at bottom right */}
      <G transform="rotate(40 42 42)">
        <Rect x="38" y="30" width="5" height="18" rx="1" fill={Palette.terracotta} stroke={Palette.charcoal} strokeWidth="1" />
        <Polygon points="38,48 43,48 40.5,52" fill={Palette.warmStoneDark} stroke={Palette.charcoal} strokeWidth="1" />
      </G>
    </Svg>
  );
}

/**
 * Career / Pathfinder Illustration:
 * Person walking along a winding path toward a goal or star.
 */
export function CareerIllustration({
  width = 64,
  height = 64,
  style,
}: IllustrationProps) {
  return (
    <Svg
      width={width}
      height={height}
      viewBox="0 0 64 64"
      fill="none"
      style={style}
      accessible={false}
      importantForAccessibility="no"
    >
      <Circle cx="32" cy="32" r="28" fill={Palette.sageSurface} />

      {/* Gentle winding path */}
      <Path
        d="M20 52 C24 40, 38 42, 36 28 C34 22, 40 18, 44 14"
        stroke={Palette.warmStoneDark}
        strokeWidth="3"
        strokeLinecap="round"
        strokeDasharray="2,3"
      />

      {/* Star / Goal at top */}
      <Polygon
        points="44,10 45.5,13.5 49,14 46.5,16.5 47,20 44,18 41,20 41.5,16.5 39,14 42.5,13.5"
        fill={Palette.ochreSurface}
        stroke={Palette.ochre}
        strokeWidth="1.2"
        strokeLinejoin="round"
      />

      {/* Student walking figure */}
      <Circle cx="24" cy="34" r="3" fill={Palette.charcoal} />
      <Path
        d="M24 38 L24 45 M24 41 L20 44 M24 41 L27 43 M24 45 L21 51 M24 45 L26 50"
        stroke={Palette.charcoal}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Svg>
  );
}

/**
 * Saved / Empty State Illustration:
 * A thoughtful stack of journals and notebooks with a warm bookmark ribbon.
 */
export function SavedEmptyIllustration({
  width = 120,
  height = 100,
  style,
}: IllustrationProps) {
  return (
    <Svg
      width={width}
      height={height}
      viewBox="0 0 120 100"
      fill="none"
      style={style}
      accessible={false}
      importantForAccessibility="no"
    >
      {/* Background warm soft circle */}
      <Circle cx="60" cy="50" r="42" fill={Palette.sageSurface} opacity={0.6} />

      {/* Bottom book */}
      <Rect
        x="30"
        y="62"
        width="60"
        height="14"
        rx="3"
        fill={Palette.softWhite}
        stroke={Palette.charcoal}
        strokeWidth="1.5"
      />
      <Line x1="30" y1="67" x2="90" y2="67" stroke={Palette.warmStone} strokeWidth="1" />

      {/* Middle book tilted slightly */}
      <G transform="rotate(-4 60 52)">
        <Rect
          x="32"
          y="48"
          width="56"
          height="14"
          rx="3"
          fill={Palette.terracottaSurface}
          stroke={Palette.charcoal}
          strokeWidth="1.5"
        />
        <Line x1="32" y1="53" x2="88" y2="53" stroke={Palette.terracotta} strokeWidth="1" />
      </G>

      {/* Top open journal */}
      <Path
        d="M60 42 C52 38, 42 40, 36 42 L36 30 C42 28, 52 26, 60 28 C68 26, 78 28, 84 30 L84 42 C78 40, 68 38, 60 42 Z"
        fill={Palette.softWhite}
        stroke={Palette.charcoal}
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      <Line x1="60" y1="28" x2="60" y2="42" stroke={Palette.charcoal} strokeWidth="1.5" />

      {/* Bookmark ribbon hanging out */}
      <Path
        d="M66 28 V56 L69 53 L72 56 V28"
        fill={Palette.terracotta}
        stroke={Palette.charcoal}
        strokeWidth="1"
      />
    </Svg>
  );
}

/**
 * Search Empty State Illustration:
 * Hand-drawn magnifying compass over open notes.
 */
export function SearchEmptyIllustration({
  width = 110,
  height = 90,
  style,
}: IllustrationProps) {
  return (
    <Svg
      width={width}
      height={height}
      viewBox="0 0 110 90"
      fill="none"
      style={style}
      accessible={false}
      importantForAccessibility="no"
    >
      <Circle cx="55" cy="45" r="38" fill={Palette.warmStoneLight} />

      {/* Notepad outline */}
      <Rect
        x="30"
        y="22"
        width="44"
        height="50"
        rx="4"
        fill={Palette.softWhite}
        stroke={Palette.charcoal}
        strokeWidth="1.5"
      />
      <Line x1="38" y1="32" x2="56" y2="32" stroke={Palette.warmStoneDark} strokeWidth="1.5" strokeLinecap="round" />
      <Line x1="38" y1="40" x2="62" y2="40" stroke={Palette.warmStoneDark} strokeWidth="1.5" strokeLinecap="round" />
      <Line x1="38" y1="48" x2="52" y2="48" stroke={Palette.warmStoneDark} strokeWidth="1.5" strokeLinecap="round" />

      {/* Magnifying glass */}
      <Circle
        cx="62"
        cy="46"
        r="14"
        fill={Palette.sageSurface}
        stroke={Palette.charcoal}
        strokeWidth="2"
      />
      <Line
        x1="72"
        y1="56"
        x2="85"
        y2="69"
        stroke={Palette.charcoal}
        strokeWidth="3"
        strokeLinecap="round"
      />
      {/* Glint in glass */}
      <Path
        d="M56 42 A 8 8 0 0 1 66 38"
        stroke={Palette.softWhite}
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </Svg>
  );
}

/**
 * Scheme / Government Institution Illustration:
 * Architectural pillars & sunburst representing public youth schemes.
 */
export function SchemeIllustration({
  width = 64,
  height = 64,
  style,
}: IllustrationProps) {
  return (
    <Svg
      width={width}
      height={height}
      viewBox="0 0 64 64"
      fill="none"
      style={style}
      accessible={false}
      importantForAccessibility="no"
    >
      <Circle cx="32" cy="32" r="28" fill={Palette.sageSurface} />

      {/* Roof pediment */}
      <Polygon
        points="32,16 50,26 14,26"
        fill={Palette.softWhite}
        stroke={Palette.charcoal}
        strokeWidth="1.5"
        strokeLinejoin="round"
      />

      {/* Pillars */}
      <Line x1="20" y1="26" x2="20" y2="44" stroke={Palette.charcoal} strokeWidth="2" strokeLinecap="round" />
      <Line x1="28" y1="26" x2="28" y2="44" stroke={Palette.charcoal} strokeWidth="2" strokeLinecap="round" />
      <Line x1="36" y1="26" x2="36" y2="44" stroke={Palette.charcoal} strokeWidth="2" strokeLinecap="round" />
      <Line x1="44" y1="26" x2="44" y2="44" stroke={Palette.charcoal} strokeWidth="2" strokeLinecap="round" />

      {/* Base steps */}
      <Rect
        x="12"
        y="44"
        width="40"
        height="5"
        rx="1"
        fill={Palette.softWhite}
        stroke={Palette.charcoal}
        strokeWidth="1.5"
      />
    </Svg>
  );
}
