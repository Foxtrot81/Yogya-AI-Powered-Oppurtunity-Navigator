/**
 * useTheme hook — returns the current Yogya theme colors.
 *
 * Currently light-mode only (matching the warm off-white design direction).
 * Dark mode can be added later by extending Colors in theme.ts.
 */

import { Colors } from '@/constants/theme';

export function useTheme() {
  // For this initial version, we use light mode consistently.
  // Dark mode support can be added by extending the Colors object
  // and using useColorScheme from react-native here.
  return Colors.light;
}
