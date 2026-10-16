/**
 * Welcome Screen — Yogya
 *
 * The initial landing screen with an editorial, handcrafted visual identity:
 * - Yogya branding and Hindi identity (योग्य)
 * - Tasteful hand-drawn illustration suggesting learning, opportunity, and personal growth
 * - Prominent call-to-action in muted sage
 * - Warm ivory canvas and soft white surfaces
 */

import { router } from 'expo-router';
import React, { useEffect, useRef } from 'react';
import {
  Animated,
  Dimensions,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { CheckIcon, ShieldIcon, SparkleIcon } from '@/components/icons/NavIcons';
import { WelcomeHeroIllustration } from '@/components/illustrations/HandDrawnIllustrations';
import { YButton } from '@/components/ui';
import { useStudentProfile } from '@/hooks/useStudentProfile';
import {
  BorderRadius,
  FontSize,
  FontWeight,
  Palette,
  Spacing,
} from '@/constants/theme';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

export default function WelcomeScreen() {
  const { hasCompletedOnboarding, profile } = useStudentProfile();

  // ─── Entrance animations ────────────────────────────────────────────────
  const heroOpacity = useRef(new Animated.Value(0)).current;
  const heroTranslateY = useRef(new Animated.Value(-16)).current;
  const contentOpacity = useRef(new Animated.Value(0)).current;
  const contentTranslateY = useRef(new Animated.Value(24)).current;
  const buttonOpacity = useRef(new Animated.Value(0)).current;
  const buttonTranslateY = useRef(new Animated.Value(16)).current;

  useEffect(() => {
    Animated.stagger(200, [
      Animated.parallel([
        Animated.timing(heroOpacity, {
          toValue: 1,
          duration: 550,
          useNativeDriver: true,
        }),
        Animated.timing(heroTranslateY, {
          toValue: 0,
          duration: 550,
          useNativeDriver: true,
        }),
      ]),
      Animated.parallel([
        Animated.timing(contentOpacity, {
          toValue: 1,
          duration: 500,
          useNativeDriver: true,
        }),
        Animated.timing(contentTranslateY, {
          toValue: 0,
          duration: 500,
          useNativeDriver: true,
        }),
      ]),
      Animated.parallel([
        Animated.timing(buttonOpacity, {
          toValue: 1,
          duration: 450,
          useNativeDriver: true,
        }),
        Animated.timing(buttonTranslateY, {
          toValue: 0,
          duration: 450,
          useNativeDriver: true,
        }),
      ]),
    ]).start();
  }, [buttonOpacity, buttonTranslateY, contentOpacity, contentTranslateY, heroOpacity, heroTranslateY]);

  const handleGetStarted = () => {
    if (hasCompletedOnboarding) {
      router.push('/home');
    } else {
      router.push('/onboarding');
    }
  };

  return (
    <View style={styles.screen}>
      <SafeAreaView style={styles.container}>
        {/* ─── Top Earth Accent Band ───────────────────────────────── */}
        <View style={styles.topBand}>
          <View style={styles.bandStripe1} />
          <View style={styles.bandStripe2} />
          <View style={styles.bandStripe3} />
        </View>

        {/* ─── Hero & Brand Identity ──────────────────────────────── */}
        <Animated.View
          style={[
            styles.heroSection,
            {
              opacity: heroOpacity,
              transform: [{ translateY: heroTranslateY }],
            },
          ]}
        >
          <View style={styles.illustrationWrapper}>
            <WelcomeHeroIllustration width={Math.min(SCREEN_WIDTH - 64, 260)} height={150} />
          </View>

          <View style={styles.brandTitleRow}>
            <Text style={styles.brandName}>Yogya</Text>
            <View style={styles.hindiBadge}>
              <Text style={styles.brandTagline}>योग्य</Text>
            </View>
          </View>
          <Text style={styles.brandSubtitle}>Empowering Every Student’s Future</Text>
        </Animated.View>

        {/* ─── Content Section ─────────────────────────────────────── */}
        <Animated.View
          style={[
            styles.contentSection,
            {
              opacity: contentOpacity,
              transform: [{ translateY: contentTranslateY }],
            },
          ]}
        >
          <Text style={styles.headline}>
            Your AI-Powered{'\n'}Opportunity Navigator
          </Text>
          <Text style={styles.subheadline}>
            Discover verified scholarships, government youth schemes, and vocational skill
            training tailored for your aspirations.
          </Text>

          {/* Handcrafted feature chips */}
          <View style={styles.features}>
            <FeatureChip
              icon={<ShieldIcon size={15} color={Palette.sageDark} />}
              text="Verified Programs"
            />
            <FeatureChip
              icon={<CheckIcon size={14} color={Palette.forestGreen} />}
              text="Smart Eligibility"
            />
            <FeatureChip
              icon={<Text style={styles.scriptChipIcon}>अ/A</Text>}
              text="Multilingual Support"
            />
          </View>
        </Animated.View>

        {/* ─── Bottom CTA ─────────────────────────────────────────── */}
        <Animated.View
          style={[
            styles.ctaSection,
            {
              opacity: buttonOpacity,
              transform: [{ translateY: buttonTranslateY }],
            },
          ]}
        >
          <YButton
            title={hasCompletedOnboarding ? 'Continue to Opportunities' : 'Get Started'}
            onPress={handleGetStarted}
            size="lg"
            fullWidth
          />
          {hasCompletedOnboarding ? (
            <Pressable
              onPress={() => router.push('/onboarding')}
              hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
              accessibilityRole="button"
              accessibilityLabel="Update student profile"
            >
              <Text style={styles.updateProfileLink}>
                {profile?.displayName ? `Student: ${profile.displayName}` : 'Active Profile'} •{' '}
                <Text style={styles.updateProfileHighlight}>Update Details</Text>
              </Text>
            </Pressable>
          ) : null}
          <Text style={styles.footerNote}>
            Designed for students across rural & urban India 🇮🇳
          </Text>
        </Animated.View>
      </SafeAreaView>
    </View>
  );
}

// ─── Feature Chip Sub-component ───────────────────────────────────────────────

function FeatureChip({ icon, text }: { icon: React.ReactNode; text: string }) {
  return (
    <View style={styles.chip}>
      <View style={styles.chipIconContainer}>{icon}</View>
      <Text style={styles.chipText}>{text}</Text>
    </View>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: Palette.ivory,
  },
  container: {
    flex: 1,
    paddingHorizontal: Spacing.four,
    justifyContent: 'space-between',
  },

  // Subtle top earthy accent stripe
  topBand: {
    flexDirection: 'row',
    height: 3,
    borderRadius: 1.5,
    overflow: 'hidden',
    marginTop: Spacing.one,
  },
  bandStripe1: {
    flex: 1,
    backgroundColor: Palette.terracotta,
  },
  bandStripe2: {
    flex: 1,
    backgroundColor: Palette.warmStone,
  },
  bandStripe3: {
    flex: 1,
    backgroundColor: Palette.sage,
  },

  // Hero section
  heroSection: {
    alignItems: 'center',
    paddingTop: Spacing.four,
  },
  illustrationWrapper: {
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.two,
  },
  brandTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.two,
  },
  brandName: {
    fontSize: FontSize['4xl'],
    fontWeight: FontWeight.bold,
    color: Palette.charcoal,
    letterSpacing: -0.5,
  },
  hindiBadge: {
    backgroundColor: Palette.terracottaSurface,
    paddingHorizontal: Spacing.two,
    paddingVertical: 2,
    borderRadius: BorderRadius.sm,
    borderWidth: 1,
    borderColor: Palette.terracottaLight,
  },
  brandTagline: {
    fontSize: FontSize.base,
    color: Palette.terracottaDark,
    fontWeight: FontWeight.semibold,
  },
  brandSubtitle: {
    fontSize: FontSize.xs,
    color: Palette.warmGray,
    marginTop: Spacing.half,
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  },

  // Content section
  contentSection: {
    alignItems: 'center',
    paddingHorizontal: Spacing.two,
  },
  headline: {
    fontSize: FontSize['2xl'],
    fontWeight: FontWeight.bold,
    color: Palette.charcoal,
    textAlign: 'center',
    lineHeight: FontSize['2xl'] * 1.3,
  },
  subheadline: {
    fontSize: FontSize.sm,
    color: Palette.warmGray,
    textAlign: 'center',
    marginTop: Spacing.twoHalf,
    lineHeight: FontSize.sm * 1.55,
    paddingHorizontal: Spacing.two,
  },
  features: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: Spacing.two,
    marginTop: Spacing.four,
  },

  // Feature chips
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Palette.softWhite,
    paddingHorizontal: Spacing.three,
    paddingVertical: Spacing.one * 1.5,
    borderRadius: BorderRadius.full,
    borderWidth: 1,
    borderColor: Palette.warmStone,
    gap: Spacing.one * 1.5,
  },
  chipIconContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  scriptChipIcon: {
    fontSize: 11,
    fontWeight: FontWeight.bold,
    color: Palette.terracottaDark,
  },
  chipText: {
    fontSize: FontSize.xs,
    fontWeight: FontWeight.medium,
    color: Palette.charcoal,
  },

  // CTA section
  ctaSection: {
    paddingBottom: Spacing.five,
    gap: Spacing.twoHalf,
    alignItems: 'center',
  },
  footerNote: {
    fontSize: FontSize.xs,
    color: Palette.warmGray,
    textAlign: 'center',
  },
  updateProfileLink: {
    fontSize: FontSize.xs,
    color: Palette.warmGray,
    textAlign: 'center',
    marginTop: Spacing.half,
  },
  updateProfileHighlight: {
    color: Palette.sageDark,
    fontWeight: FontWeight.bold,
  },
});
