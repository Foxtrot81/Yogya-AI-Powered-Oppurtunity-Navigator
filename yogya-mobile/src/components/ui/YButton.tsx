/**
 * YButton — Primary reusable button component for Yogya.
 *
 * Designed with a warm, handcrafted aesthetic:
 * - Primary variant: muted sage with accessible white/ivory text
 * - Secondary variant: muted terracotta
 * - Outline variant: warm stone/sage border with sage text
 * - Ghost variant: subtle text button
 * - Includes tactile press animation via Animated API
 */

import React, { useRef } from 'react';
import {
  ActivityIndicator,
  Animated,
  Pressable,
  StyleSheet,
  Text,
  View,
  type TextStyle,
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
import type { ButtonSize, ButtonVariant } from '@/types';

interface YButtonProps {
  title: string;
  onPress: () => void;
  variant?: ButtonVariant;
  size?: ButtonSize;
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  icon?: React.ReactNode;
}

const VARIANT_STYLES: Record<ButtonVariant, { container: ViewStyle; text: TextStyle }> = {
  primary: {
    container: {
      backgroundColor: Palette.sageDark,
      borderWidth: 1,
      borderColor: Palette.sageDark,
    },
    text: {
      color: Palette.softWhite,
    },
  },
  secondary: {
    container: {
      backgroundColor: Palette.terracotta,
      borderWidth: 1,
      borderColor: Palette.terracottaDark,
    },
    text: {
      color: Palette.softWhite,
    },
  },
  outline: {
    container: {
      backgroundColor: 'transparent',
      borderWidth: 1.5,
      borderColor: Palette.warmStoneDark,
    },
    text: {
      color: Palette.charcoal,
    },
  },
  ghost: {
    container: {
      backgroundColor: 'transparent',
    },
    text: {
      color: Palette.sageDark,
    },
  },
};

const SIZE_STYLES: Record<ButtonSize, { container: ViewStyle; text: TextStyle }> = {
  sm: {
    container: {
      paddingVertical: Spacing.two,
      paddingHorizontal: Spacing.three,
      borderRadius: BorderRadius.md,
      minHeight: 38,
    },
    text: {
      fontSize: FontSize.sm,
    },
  },
  md: {
    container: {
      paddingVertical: Spacing.twoHalf,
      paddingHorizontal: Spacing.four,
      borderRadius: BorderRadius.lg,
      minHeight: 46,
    },
    text: {
      fontSize: FontSize.base,
    },
  },
  lg: {
    container: {
      paddingVertical: Spacing.three,
      paddingHorizontal: Spacing.five,
      borderRadius: BorderRadius.lg,
      minHeight: 52,
    },
    text: {
      fontSize: FontSize.lg,
    },
  },
};

export function YButton({
  title,
  onPress,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  fullWidth = false,
  icon,
}: YButtonProps) {
  const scaleAnim = useRef(new Animated.Value(1)).current;

  const handlePressIn = () => {
    Animated.spring(scaleAnim, {
      toValue: 0.97,
      useNativeDriver: true,
      speed: 50,
      bounciness: 4,
    }).start();
  };

  const handlePressOut = () => {
    Animated.spring(scaleAnim, {
      toValue: 1,
      useNativeDriver: true,
      speed: 30,
      bounciness: 6,
    }).start();
  };

  const variantStyle = VARIANT_STYLES[variant];
  const sizeStyle = SIZE_STYLES[size];

  return (
    <Animated.View style={[{ transform: [{ scale: scaleAnim }] }, fullWidth && styles.fullWidth]}>
      <Pressable
        onPress={onPress}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        disabled={disabled || loading}
        style={[
          styles.base,
          variantStyle.container,
          sizeStyle.container,
          fullWidth && styles.fullWidth,
          disabled && styles.disabled,
        ]}
        accessibilityRole="button"
        accessibilityLabel={title}
        accessibilityState={{ disabled: disabled || loading }}
      >
        {loading ? (
          <ActivityIndicator
            size="small"
            color={variantStyle.text.color as string}
          />
        ) : (
          <>
            {icon != null && <View style={styles.iconContainer}>{icon}</View>}
            <Text
              style={[
                styles.text,
                variantStyle.text,
                sizeStyle.text,
                icon != null && styles.textWithIcon,
              ]}
            >
              {title}
            </Text>
          </>
        )}
      </Pressable>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  base: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    alignSelf: 'flex-start',
  },
  fullWidth: {
    alignSelf: 'stretch',
    width: '100%',
  },
  disabled: {
    opacity: 0.5,
  },
  iconContainer: {
    marginRight: Spacing.two,
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    fontWeight: FontWeight.semibold,
    textAlign: 'center',
    letterSpacing: 0.2,
  },
  textWithIcon: {
    marginLeft: 0,
  },
});
