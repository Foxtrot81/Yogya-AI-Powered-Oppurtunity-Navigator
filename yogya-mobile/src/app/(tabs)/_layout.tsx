/**
 * Tabs Layout — Yogya
 *
 * Bottom tab bar configuration for the four main app destinations:
 * - Home (Dashboard, search, category filters, featured list)
 * - Explore (Curated pathways and category discovery)
 * - Saved (Student bookmarks, persisted locally)
 * - Profile (Student details, education, goals, edit capability)
 *
 * Styled with handcrafted outline SVG icons, muted sage active states,
 * warm gray inactive states, warm stone dividers, and safe-area handling.
 */

import { Tabs } from 'expo-router';
import React from 'react';
import { Platform, StyleSheet, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import {
  ExploreIcon,
  HomeIcon,
  ProfileIcon,
  SavedIcon,
} from '@/components/icons/NavIcons';
import {
  FontSize,
  FontWeight,
  Palette,
  Shadows,
} from '@/constants/theme';
import { useSavedOpportunities } from '@/hooks/useSavedOpportunities';

export default function TabLayout() {
  const insets = useSafeAreaInsets();
  const { savedIds } = useSavedOpportunities();
  const savedCount = savedIds.length;

  const tabHeight = 60 + Math.max(insets.bottom, Platform.select({ ios: 16, default: 8 }));
  const tabPaddingBottom = Math.max(insets.bottom, Platform.select({ ios: 14, default: 8 }));

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: Palette.sageDark,
        tabBarInactiveTintColor: Palette.warmGray,
        tabBarStyle: {
          backgroundColor: Palette.softWhite,
          borderTopColor: Palette.warmStone,
          borderTopWidth: 1,
          height: tabHeight,
          paddingBottom: tabPaddingBottom,
          paddingTop: 8,
          ...Shadows.sm,
        },
        tabBarLabelStyle: {
          fontSize: FontSize.xs,
          fontWeight: FontWeight.semibold,
          marginTop: 2,
        },
      }}
    >
      <Tabs.Screen
        name="home"
        options={{
          title: 'Home',
          tabBarAccessibilityLabel: 'Home tab',
          tabBarIcon: ({ focused }) => (
            <TabIconContainer focused={focused}>
              <HomeIcon
                size={22}
                color={focused ? Palette.sageDark : Palette.warmGray}
                strokeWidth={focused ? 2.2 : 1.8}
              />
            </TabIconContainer>
          ),
        }}
      />
      <Tabs.Screen
        name="explore"
        options={{
          title: 'Explore',
          tabBarAccessibilityLabel: 'Explore tab',
          tabBarIcon: ({ focused }) => (
            <TabIconContainer focused={focused}>
              <ExploreIcon
                size={22}
                color={focused ? Palette.sageDark : Palette.warmGray}
                strokeWidth={focused ? 2.2 : 1.8}
              />
            </TabIconContainer>
          ),
        }}
      />
      <Tabs.Screen
        name="saved"
        options={{
          title: 'Saved',
          tabBarAccessibilityLabel: 'Saved opportunities tab',
          tabBarBadge: savedCount > 0 ? savedCount : undefined,
          tabBarBadgeStyle: {
            backgroundColor: Palette.terracotta,
            color: Palette.softWhite,
            fontSize: 10,
            fontWeight: FontWeight.bold,
            minWidth: 16,
            height: 16,
            borderRadius: 8,
            lineHeight: 14,
          },
          tabBarIcon: ({ focused }) => (
            <TabIconContainer focused={focused}>
              <SavedIcon
                size={22}
                color={focused ? Palette.sageDark : Palette.warmGray}
                strokeWidth={focused ? 2.2 : 1.8}
                filled={focused}
              />
            </TabIconContainer>
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarAccessibilityLabel: 'Student profile tab',
          tabBarIcon: ({ focused }) => (
            <TabIconContainer focused={focused}>
              <ProfileIcon
                size={22}
                color={focused ? Palette.sageDark : Palette.warmGray}
                strokeWidth={focused ? 2.2 : 1.8}
              />
            </TabIconContainer>
          ),
        }}
      />
    </Tabs>
  );
}

// ─── Tab Icon Wrapper ────────────────────────────────────────────────────────

function TabIconContainer({
  focused,
  children,
}: {
  focused: boolean;
  children: React.ReactNode;
}) {
  return (
    <View style={styles.tabIconWrapper}>
      <View style={[styles.iconPill, focused && styles.iconPillFocused]}>
        {children}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  tabIconWrapper: {
    alignItems: 'center',
    justifyContent: 'center',
    height: 30,
  },
  iconPill: {
    paddingHorizontal: 12,
    paddingVertical: 3,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconPillFocused: {
    backgroundColor: Palette.sageSurface,
  },
});
