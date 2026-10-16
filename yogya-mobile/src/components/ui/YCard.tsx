/**
 * YCard — Reusable card container for Yogya.
 *
 * Supports default (bordered), elevated (subtle shadow), and outlined variants.
 * Uses the soft white (#FFFDF8) card surface on warm ivory (#F7F4ED) background,
 * framed with subtle warm stone (#E3DED4) borders.
 */

import React from 'react';
import { StyleSheet, View, type ViewProps, type ViewStyle } from 'react-native';

import {
  BorderRadius,
  Palette,
  Shadows,
  Spacing,
} from '@/constants/theme';
import type { CardVariant } from '@/types';

interface YCardProps extends ViewProps {
  variant?: CardVariant;
  noPadding?: boolean;
}

const VARIANT_STYLES: Record<CardVariant, ViewStyle> = {
  default: {
    backgroundColor: Palette.softWhite,
    borderWidth: 1,
    borderColor: Palette.warmStone,
  },
  elevated: {
    backgroundColor: Palette.softWhite,
    borderWidth: 1,
    borderColor: Palette.warmStone,
    ...Shadows.sm,
  },
  outlined: {
    backgroundColor: Palette.softWhite,
    borderWidth: 1.5,
    borderColor: Palette.warmStoneDark,
  },
};

export function YCard({
  variant = 'elevated',
  noPadding = false,
  style,
  children,
  ...rest
}: YCardProps) {
  return (
    <View
      style={[
        styles.base,
        VARIANT_STYLES[variant],
        !noPadding && styles.padded,
        style,
      ]}
      {...rest}
    >
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  base: {
    borderRadius: BorderRadius.lg,
    overflow: 'hidden',
  },
  padded: {
    padding: Spacing.threeHalf,
  },
});
