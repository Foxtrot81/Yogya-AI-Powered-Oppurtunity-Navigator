/**
 * YInput — Reusable text input component for Yogya.
 *
 * Styled to match the warm, handcrafted Yogya palette:
 * - Neutral soft white (#FFFDF8) background
 * - Warm stone (#E3DED4) border with muted sage focus state
 * - Clear charcoal typography and warm gray placeholder
 * - Restrained brick red error states with accessible contrast
 */

import React, { useState } from 'react';
import {
  StyleSheet,
  Text,
  TextInput,
  View,
  type TextInputProps,
  type ViewStyle,
} from 'react-native';

import {
  BorderRadius,
  Colors,
  FontSize,
  FontWeight,
  Palette,
  Spacing,
} from '@/constants/theme';
import { AlertCircleIcon } from '@/components/icons/NavIcons';

export interface YInputProps extends TextInputProps {
  label?: string;
  helperText?: string;
  error?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  containerStyle?: ViewStyle;
  inputContainerStyle?: ViewStyle;
}

export function YInput({
  label,
  helperText,
  error,
  leftIcon,
  rightIcon,
  containerStyle,
  inputContainerStyle,
  style,
  onFocus,
  onBlur,
  ...rest
}: YInputProps) {
  const [isFocused, setIsFocused] = useState(false);

  const handleFocus = (e: Parameters<NonNullable<TextInputProps['onFocus']>>[0]) => {
    setIsFocused(true);
    onFocus?.(e);
  };

  const handleBlur = (e: Parameters<NonNullable<TextInputProps['onBlur']>>[0]) => {
    setIsFocused(false);
    onBlur?.(e);
  };

  const borderColor = error
    ? Palette.brickRed
    : isFocused
      ? Palette.sage
      : Palette.warmStone;

  return (
    <View style={[styles.wrapper, containerStyle]}>
      {label != null && <Text style={styles.label}>{label}</Text>}
      <View
        style={[
          styles.inputContainer,
          { borderColor },
          isFocused && styles.inputFocused,
          error != null && styles.inputError,
          inputContainerStyle,
        ]}
      >
        {leftIcon != null && <View style={styles.leftIconWrapper}>{leftIcon}</View>}
        <TextInput
          style={[styles.input, style]}
          placeholderTextColor={Palette.warmGrayMuted}
          onFocus={handleFocus}
          onBlur={handleBlur}
          accessibilityLabel={label}
          {...rest}
        />
        {rightIcon != null && <View style={styles.rightIconWrapper}>{rightIcon}</View>}
      </View>
      {error != null && (
        <View style={styles.errorRow}>
          <AlertCircleIcon size={14} color={Palette.brickRed} />
          <Text style={styles.error}>{error}</Text>
        </View>
      )}
      {helperText != null && error == null && (
        <Text style={styles.helper}>{helperText}</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    gap: Spacing.half,
  },
  label: {
    fontSize: FontSize.sm,
    fontWeight: FontWeight.semibold,
    color: Palette.charcoal,
    marginBottom: Spacing.half,
    letterSpacing: 0.1,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1.5,
    borderRadius: BorderRadius.md,
    backgroundColor: Palette.softWhite,
    paddingHorizontal: Spacing.three,
    minHeight: 48,
  },
  inputFocused: {
    borderWidth: 1.5,
    backgroundColor: Palette.softWhite,
  },
  inputError: {
    backgroundColor: Palette.brickRedSurface,
  },
  input: {
    flex: 1,
    paddingVertical: Spacing.twoHalf,
    fontSize: FontSize.base,
    color: Palette.charcoal,
    paddingHorizontal: 0,
  },
  leftIconWrapper: {
    marginRight: Spacing.two,
    justifyContent: 'center',
    alignItems: 'center',
  },
  rightIconWrapper: {
    marginLeft: Spacing.two,
    justifyContent: 'center',
    alignItems: 'center',
  },
  helper: {
    fontSize: FontSize.xs,
    color: Palette.warmGray,
    marginTop: Spacing.half,
  },
  errorRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.half,
    marginTop: Spacing.half,
  },
  error: {
    fontSize: FontSize.xs,
    color: Palette.brickRed,
    fontWeight: FontWeight.medium,
  },
});
