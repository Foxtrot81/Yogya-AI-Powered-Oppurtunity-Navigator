/**
 * Onboarding Screen — Yogya
 *
 * A multi-step, mobile-first onboarding flow designed for students across India:
 * - Step 1: Basic details (Name, Language, State, District)
 * - Step 2: Education (Education level, Stream, Institution type)
 * - Step 3: Goals & Interests (Main goal, Multi-select interests, Learning mode)
 * - Step 4: Final Profile Review & Confirmation
 *
 * Visual design:
 * - Warm ivory canvas (#F7F4ED) and soft white surfaces (#FFFDF8)
 * - Charcoal typography and warm gray secondary text
 * - Muted sage progress tracking (#747D68 / #E4E5D8)
 * - Multi-attribute selection indicators (not relying on color alone)
 * - Touch-friendly options (48px+ targets)
 * - Preserves all validation, draft state, and persistence
 */

import React, { useMemo, useState } from 'react';
import {
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router } from 'expo-router';

import {
  ArrowLeftIcon,
  CheckIcon,
  ShieldIcon,
} from '@/components/icons/NavIcons';
import { YButton, YCard, YInput } from '@/components/ui';
import {
  BorderRadius,
  FontSize,
  FontWeight,
  Palette,
  Shadows,
  Spacing,
} from '@/constants/theme';
import { useStudentProfile } from '@/hooks/useStudentProfile';
import type {
  EducationLevel,
  InstitutionType,
  LearningMode,
  MainGoal,
  OnboardingFormData,
} from '@/types';

// ─── Available Option Constants ──────────────────────────────────────────────

const LANGUAGES: Array<{ code: string; label: string; native: string }> = [
  { code: 'English', label: 'English', native: 'English' },
  { code: 'Hindi', label: 'Hindi', native: 'हिंदी' },
  { code: 'Tamil', label: 'Tamil', native: 'தமிழ்' },
  { code: 'Kannada', label: 'Kannada', native: 'ಕನ್ನಡ' },
  { code: 'Telugu', label: 'Telugu', native: 'తెలుగు' },
  { code: 'Marathi', label: 'Marathi', native: 'मराठी' },
  { code: 'Bengali', label: 'Bengali', native: 'বাংলা' },
  { code: 'Other', label: 'Other', native: 'अन्य' },
];

const POPULAR_STATES = [
  'Uttar Pradesh',
  'Bihar',
  'Rajasthan',
  'Madhya Pradesh',
  'Maharashtra',
  'Karnataka',
  'Tamil Nadu',
  'West Bengal',
  'Andhra Pradesh',
  'Odisha',
  'Gujarat',
  'Punjab',
  'Kerala',
  'Assam',
  'Jharkhand',
  'Chhattisgarh',
  'Other',
];

const EDUCATION_LEVELS: Array<{ value: EducationLevel; label: string; badge: string }> = [
  { value: 'Class 9', label: 'Class 9', badge: 'IX' },
  { value: 'Class 10', label: 'Class 10 (Secondary)', badge: 'X' },
  { value: 'Class 11', label: 'Class 11', badge: 'XI' },
  { value: 'Class 12', label: 'Class 12 (Higher Secondary)', badge: 'XII' },
  { value: 'Diploma', label: 'Polytechnic / Diploma', badge: 'DIP' },
  { value: 'Undergraduate', label: 'College / Undergrad (BA, BSc, BTech)', badge: 'UG' },
  { value: 'Other', label: 'Other / Vocational Certificate', badge: 'CERT' },
];

const STREAMS = [
  'Science (PCM / PCB)',
  'Commerce',
  'Arts & Humanities',
  'Engineering & Tech',
  'Agriculture & Rural Studies',
  'Vocational / ITI Trades',
  'General / Foundation',
  'Other',
];

const INSTITUTION_TYPES: Array<{ value: InstitutionType; label: string }> = [
  { value: 'Government', label: 'Government School / College' },
  { value: 'Aided', label: 'Government-Aided' },
  { value: 'Private', label: 'Private Institution' },
  { value: 'Other', label: 'Vocational / Open School / Other' },
];

const MAIN_GOALS: Array<{ value: MainGoal; label: string; desc: string; tag: string }> = [
  {
    value: 'Scholarship',
    label: 'Scholarship & Fee Waiver',
    desc: 'Financial grants to cover tuition, examination fees, and study expenses',
    tag: 'Financial Aid',
  },
  {
    value: 'Vocational Training',
    label: 'Vocational Skill Training',
    desc: 'Practical job-ready certificate courses under PMKVY and Sector Councils',
    tag: 'Skill Courses',
  },
  {
    value: 'Apprenticeship',
    label: 'Apprenticeship & On-Job Training',
    desc: 'Stipend-supported hands-on learning with recognized industry partners',
    tag: 'Work & Learn',
  },
  {
    value: 'Career Exploration',
    label: 'Career Exploration & Guidance',
    desc: 'Discover higher education and career roadmaps matched to your strengths',
    tag: 'Guidance',
  },
  {
    value: 'Other',
    label: 'Other Opportunities',
    desc: 'Competitions, mentorship programs, and special state welfare schemes',
    tag: 'General',
  },
];

const INTEREST_OPTIONS = [
  'STEM & Computers',
  'Agriculture & Farming',
  'Healthcare & Nursing',
  'Electrical & Solar Trades',
  'Teaching & Education',
  'Banking & Commerce',
  'Defense & Police Forces',
  'Crafts & Handloom',
  'Government Job Exams',
  'Digital Marketing & Media',
  'Automobile & Mechanics',
  'Construction & Carpentry',
];

const LEARNING_MODES: Array<{ value: LearningMode; label: string; badge: string }> = [
  { value: 'Offline / Classroom', label: 'In-person / Offline', badge: 'Campus' },
  { value: 'Online / Digital', label: 'Online / Mobile phone', badge: 'Online' },
  { value: 'Hybrid', label: 'Hybrid (Both)', badge: 'Hybrid' },
  { value: 'Hands-on / Practical', label: 'Hands-on Workshop', badge: 'Practical' },
];

export default function OnboardingScreen() {
  const { draftForm, updateDraftForm, saveProfile } = useStudentProfile();

  const [step, setStep] = useState<number>(1);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [customStateInput, setCustomStateInput] = useState(
    draftForm.state && !POPULAR_STATES.includes(draftForm.state) ? draftForm.state : '',
  );

  // ─── Field update helper with error clearing ─────────────────────────────
  const handleChange = (field: keyof OnboardingFormData, value: any) => {
    updateDraftForm({ [field]: value });
    if (errors[field]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  const toggleInterest = (interest: string) => {
    const current = draftForm.interests || [];
    let updated: string[];
    if (current.includes(interest)) {
      updated = current.filter((item) => item !== interest);
    } else {
      updated = [...current, interest];
    }
    handleChange('interests', updated);
  };

  // ─── Step validation ─────────────────────────────────────────────────────
  const validateStep = (currentStep: number): boolean => {
    const newErrors: Record<string, string> = {};

    if (currentStep === 1) {
      if (!draftForm.displayName || draftForm.displayName.trim().length < 2) {
        newErrors.displayName = 'Please enter your preferred display name (at least 2 letters)';
      }
      if (!draftForm.preferredLanguage) {
        newErrors.preferredLanguage = 'Please select your preferred language';
      }
      const activeState = draftForm.state === 'Other' ? customStateInput.trim() : draftForm.state;
      if (!activeState || activeState.trim().length < 2) {
        newErrors.state = 'Please select or enter your state';
      }
    } else if (currentStep === 2) {
      if (!draftForm.educationLevel) {
        newErrors.educationLevel = 'Please select your current education level';
      }
      const needsStream = ['Class 11', 'Class 12', 'Diploma', 'Undergraduate'].includes(
        draftForm.educationLevel,
      );
      if (needsStream && (!draftForm.stream || draftForm.stream.trim().length === 0)) {
        newErrors.stream = 'Please select or enter your study stream / specialization';
      }
    } else if (currentStep === 3) {
      if (!draftForm.mainGoal) {
        newErrors.mainGoal = 'Please select your primary goal';
      }
      if (!draftForm.interests || draftForm.interests.length === 0) {
        newErrors.interests = 'Please select at least 1 field of interest';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // ─── Navigation handlers ─────────────────────────────────────────────────
  const handleContinue = () => {
    if (draftForm.state === 'Other' && customStateInput.trim()) {
      updateDraftForm({ state: customStateInput.trim() });
    }

    if (!validateStep(step)) {
      return;
    }

    if (step < 4) {
      setStep((prev) => prev + 1);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep((prev) => prev - 1);
      setErrors({});
    } else {
      router.back();
    }
  };

  const handleComplete = async () => {
    setIsSubmitting(true);
    try {
      const finalState =
        draftForm.state === 'Other' && customStateInput.trim()
          ? customStateInput.trim()
          : draftForm.state;

      await saveProfile({
        displayName: draftForm.displayName.trim(),
        preferredLanguage: draftForm.preferredLanguage,
        state: finalState,
        district: draftForm.district.trim() || undefined,
        educationLevel: draftForm.educationLevel,
        stream: draftForm.stream.trim() || undefined,
        institutionType: draftForm.institutionType || undefined,
        mainGoal: draftForm.mainGoal,
        interests: draftForm.interests,
        preferredLearningMode: draftForm.preferredLearningMode || undefined,
      });

      router.replace('/home');
    } catch (err) {
      console.error('Failed to complete onboarding', err);
      setErrors({ form: 'An error occurred while saving your profile. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  // ─── Progress percentage calculation ─────────────────────────────────────
  const progressPercent = useMemo(() => {
    switch (step) {
      case 1:
        return '25%';
      case 2:
        return '50%';
      case 3:
        return '75%';
      case 4:
        return '100%';
      default:
        return '25%';
    }
  }, [step]);

  const stepTitle = useMemo(() => {
    switch (step) {
      case 1:
        return 'Basic Details';
      case 2:
        return 'Education';
      case 3:
        return 'Goals & Interests';
      case 4:
        return 'Review & Confirm';
      default:
        return '';
    }
  }, [step]);

  return (
    <SafeAreaView style={styles.safeArea} edges={['top', 'left', 'right', 'bottom']}>
      <KeyboardAvoidingView
        style={styles.keyboardContainer}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        {/* ─── Top Header & Progress ─────────────────────────────── */}
        <View style={styles.header}>
          <View style={styles.headerRow}>
            <Pressable
              onPress={handleBack}
              style={styles.backButton}
              accessibilityRole="button"
              accessibilityLabel="Go back"
              hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
            >
              <View style={styles.backButtonInner}>
                <ArrowLeftIcon size={18} color={Palette.charcoal} />
                <Text style={styles.backButtonText}>Back</Text>
              </View>
            </Pressable>

            <View style={styles.stepBadge}>
              <Text style={styles.stepBadgeText}>
                Step {step} of 4
              </Text>
            </View>
          </View>

          {/* Progress Bar with Soft Sage */}
          <View style={styles.progressBarTrack}>
            <View style={[styles.progressBarFill, { width: progressPercent }]} />
          </View>

          <View style={styles.titleRow}>
            <Text style={styles.stepHeadline}>{stepTitle}</Text>
            <Text style={styles.stepSubhead}>
              {step === 1 && 'Tell us a bit about who you are and where you learn'}
              {step === 2 && 'Share your current educational background'}
              {step === 3 && 'Choose your targets and what subjects excite you'}
              {step === 4 && 'Double check your details before finding matches'}
            </Text>
          </View>
        </View>

        {/* ─── Scrollable Form Body ───────────────────────────────── */}
        <ScrollView
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          {/* STEP 1: BASIC DETAILS */}
          {step === 1 && (
            <View style={styles.stepContainer}>
              <YCard variant="elevated" style={styles.card}>
                {/* Display Name */}
                <YInput
                  label="Preferred Display Name *"
                  placeholder="e.g. Priya Sharma or Rahul"
                  value={draftForm.displayName}
                  onChangeText={(text) => handleChange('displayName', text)}
                  error={errors.displayName}
                  helperText="The name Yogya will address you with"
                  autoCapitalize="words"
                />

                {/* Preferred Language */}
                <View style={styles.fieldGroup}>
                  <Text style={styles.fieldLabel}>
                    Preferred Language *
                  </Text>
                  <Text style={styles.fieldHelper}>
                    Choose the language you prefer for explanations and voice
                  </Text>
                  <View style={styles.pillsWrap}>
                    {LANGUAGES.map((lang) => {
                      const isSelected = draftForm.preferredLanguage === lang.code;
                      return (
                        <Pressable
                          key={lang.code}
                          onPress={() => handleChange('preferredLanguage', lang.code)}
                          style={[
                            styles.languagePill,
                            isSelected && styles.languagePillSelected,
                          ]}
                          accessibilityRole="button"
                          accessibilityState={{ selected: isSelected }}
                        >
                          <View style={styles.languagePillContent}>
                            <Text
                              style={[
                                styles.languagePillText,
                                isSelected && styles.languagePillTextSelected,
                              ]}
                            >
                              {lang.native}
                            </Text>
                            {lang.code !== lang.native && (
                              <Text
                                style={[
                                  styles.languagePillSub,
                                  isSelected && styles.languagePillSubSelected,
                                ]}
                              >
                                {lang.label}
                              </Text>
                            )}
                          </View>
                          {isSelected && (
                            <View style={styles.pillCheckCircle}>
                              <CheckIcon size={12} color={Palette.softWhite} strokeWidth={3} />
                            </View>
                          )}
                        </Pressable>
                      );
                    })}
                  </View>
                  {errors.preferredLanguage ? (
                    <Text style={styles.inlineError}>{errors.preferredLanguage}</Text>
                  ) : null}
                </View>

                {/* Current State */}
                <View style={styles.fieldGroup}>
                  <Text style={styles.fieldLabel}>Current State / UT *</Text>
                  <Text style={styles.fieldHelper}>
                    Many government schemes and scholarships are state-specific
                  </Text>
                  <View style={styles.pillsWrap}>
                    {POPULAR_STATES.map((st) => {
                      const isSelected = draftForm.state === st;
                      return (
                        <Pressable
                          key={st}
                          onPress={() => handleChange('state', st)}
                          style={[
                            styles.chipPill,
                            isSelected && styles.chipPillSelected,
                          ]}
                          accessibilityRole="button"
                          accessibilityState={{ selected: isSelected }}
                        >
                          <Text
                            style={[
                              styles.chipPillText,
                              isSelected && styles.chipPillTextSelected,
                            ]}
                          >
                            {st}
                          </Text>
                          {isSelected && (
                            <View style={styles.chipCheckDot}>
                              <CheckIcon size={10} color={Palette.softWhite} strokeWidth={3} />
                            </View>
                          )}
                        </Pressable>
                      );
                    })}
                  </View>

                  {draftForm.state === 'Other' && (
                    <View style={styles.customStateWrapper}>
                      <YInput
                        label="Enter your State or Union Territory *"
                        placeholder="e.g. Uttarakhand, Goa, Ladakh..."
                        value={customStateInput}
                        onChangeText={(txt) => {
                          setCustomStateInput(txt);
                          handleChange('state', 'Other');
                        }}
                        error={errors.state}
                      />
                    </View>
                  )}

                  {errors.state && draftForm.state !== 'Other' ? (
                    <Text style={styles.inlineError}>{errors.state}</Text>
                  ) : null}
                </View>

                {/* District */}
                <YInput
                  label="District (Optional)"
                  placeholder="e.g. Varanasi, Mysuru, Madurai"
                  value={draftForm.district}
                  onChangeText={(text) => handleChange('district', text)}
                  helperText="Helps identify district-level skill centers and local opportunities"
                  autoCapitalize="words"
                />
              </YCard>
            </View>
          )}

          {/* STEP 2: EDUCATION */}
          {step === 2 && (
            <View style={styles.stepContainer}>
              <YCard variant="elevated" style={styles.card}>
                <View style={styles.fieldGroup}>
                  <Text style={styles.fieldLabel}>
                    Current Education Level *
                  </Text>
                  <Text style={styles.fieldHelper}>
                    Select your current or highest completed level of study
                  </Text>

                  <View style={styles.selectionList}>
                    {EDUCATION_LEVELS.map((edu) => {
                      const isSelected = draftForm.educationLevel === edu.value;
                      return (
                        <Pressable
                          key={edu.value}
                          onPress={() => handleChange('educationLevel', edu.value)}
                          style={[
                            styles.selectionOption,
                            isSelected && styles.selectionOptionSelected,
                          ]}
                          accessibilityRole="radio"
                          accessibilityState={{ selected: isSelected }}
                        >
                          <View
                            style={[
                              styles.optionBadgeContainer,
                              isSelected && styles.optionBadgeContainerSelected,
                            ]}
                          >
                            <Text
                              style={[
                                styles.optionBadgeText,
                                isSelected && styles.optionBadgeTextSelected,
                              ]}
                            >
                              {edu.badge}
                            </Text>
                          </View>
                          <View style={styles.optionContent}>
                            <Text
                              style={[
                                styles.optionTitle,
                                isSelected && styles.optionTitleSelected,
                              ]}
                            >
                              {edu.label}
                            </Text>
                          </View>
                          <View
                            style={[
                              styles.radioCircle,
                              isSelected && styles.radioCircleSelected,
                            ]}
                          >
                            {isSelected && <View style={styles.radioDot} />}
                          </View>
                        </Pressable>
                      );
                    })}
                  </View>
                  {errors.educationLevel ? (
                    <Text style={styles.inlineError}>{errors.educationLevel}</Text>
                  ) : null}
                </View>

                {/* Stream / Field of study */}
                <View style={styles.fieldGroup}>
                  <Text style={styles.fieldLabel}>
                    Stream or Field of Study {['Class 11', 'Class 12', 'Diploma', 'Undergraduate'].includes(draftForm.educationLevel) ? '*' : '(Optional)'}
                  </Text>
                  <Text style={styles.fieldHelper}>
                    Select or specify your subject branch
                  </Text>
                  <View style={styles.pillsWrap}>
                    {STREAMS.map((st) => {
                      const isSelected = draftForm.stream === st;
                      return (
                        <Pressable
                          key={st}
                          onPress={() => handleChange('stream', st)}
                          style={[
                            styles.chipPill,
                            isSelected && styles.chipPillSelected,
                          ]}
                          accessibilityRole="button"
                          accessibilityState={{ selected: isSelected }}
                        >
                          <Text
                            style={[
                              styles.chipPillText,
                              isSelected && styles.chipPillTextSelected,
                            ]}
                          >
                            {st}
                          </Text>
                          {isSelected && (
                            <View style={styles.chipCheckDot}>
                              <CheckIcon size={10} color={Palette.softWhite} strokeWidth={3} />
                            </View>
                          )}
                        </Pressable>
                      );
                    })}
                  </View>
                  {errors.stream ? (
                    <Text style={styles.inlineError}>{errors.stream}</Text>
                  ) : null}
                </View>

                {/* Institution Type */}
                <View style={styles.fieldGroup}>
                  <Text style={styles.fieldLabel}>
                    Institution Type (Optional)
                  </Text>
                  <Text style={styles.fieldHelper}>
                    Certain schemes prioritize government or aided school students
                  </Text>
                  <View style={styles.pillsWrap}>
                    {INSTITUTION_TYPES.map((inst) => {
                      const isSelected = draftForm.institutionType === inst.value;
                      return (
                        <Pressable
                          key={inst.value}
                          onPress={() => handleChange('institutionType', inst.value)}
                          style={[
                            styles.chipPill,
                            isSelected && styles.chipPillSelected,
                          ]}
                          accessibilityRole="button"
                          accessibilityState={{ selected: isSelected }}
                        >
                          <Text
                            style={[
                              styles.chipPillText,
                              isSelected && styles.chipPillTextSelected,
                            ]}
                          >
                            {inst.label}
                          </Text>
                          {isSelected && (
                            <View style={styles.chipCheckDot}>
                              <CheckIcon size={10} color={Palette.softWhite} strokeWidth={3} />
                            </View>
                          )}
                        </Pressable>
                      );
                    })}
                  </View>
                </View>
              </YCard>
            </View>
          )}

          {/* STEP 3: GOALS & INTERESTS */}
          {step === 3 && (
            <View style={styles.stepContainer}>
              <YCard variant="elevated" style={styles.card}>
                {/* Primary Goal */}
                <View style={styles.fieldGroup}>
                  <Text style={styles.fieldLabel}>Main Goal *</Text>
                  <Text style={styles.fieldHelper}>
                    What kind of opportunity is most urgent or important for you?
                  </Text>
                  <View style={styles.selectionList}>
                    {MAIN_GOALS.map((goal) => {
                      const isSelected = draftForm.mainGoal === goal.value;
                      return (
                        <Pressable
                          key={goal.value}
                          onPress={() => handleChange('mainGoal', goal.value)}
                          style={[
                            styles.goalOption,
                            isSelected && styles.selectionOptionSelected,
                          ]}
                          accessibilityRole="radio"
                          accessibilityState={{ selected: isSelected }}
                        >
                          <View style={styles.goalContent}>
                            <View
                              style={[
                                styles.goalTagBadge,
                                isSelected && styles.goalTagBadgeSelected,
                              ]}
                            >
                              <Text
                                style={[
                                  styles.goalTagText,
                                  isSelected && styles.goalTagTextSelected,
                                ]}
                              >
                                {goal.tag}
                              </Text>
                            </View>
                            <Text
                              style={[
                                styles.optionTitle,
                                isSelected && styles.optionTitleSelected,
                              ]}
                            >
                              {goal.label}
                            </Text>
                            <Text style={styles.goalDesc}>{goal.desc}</Text>
                          </View>
                          <View
                            style={[
                              styles.radioCircle,
                              isSelected && styles.radioCircleSelected,
                            ]}
                          >
                            {isSelected && <View style={styles.radioDot} />}
                          </View>
                        </Pressable>
                      );
                    })}
                  </View>
                  {errors.mainGoal ? (
                    <Text style={styles.inlineError}>{errors.mainGoal}</Text>
                  ) : null}
                </View>

                {/* Interests (Multi-select) */}
                <View style={styles.fieldGroup}>
                  <View style={styles.labelRow}>
                    <Text style={styles.fieldLabel}>Interests *</Text>
                    <View style={styles.selectedCountBadge}>
                      <Text style={styles.selectedCountText}>
                        {draftForm.interests?.length || 0} selected
                      </Text>
                    </View>
                  </View>
                  <Text style={styles.fieldHelper}>
                    Choose all fields that you enjoy or want to work in
                  </Text>
                  <View style={styles.pillsWrap}>
                    {INTEREST_OPTIONS.map((interest) => {
                      const isSelected = draftForm.interests?.includes(interest);
                      return (
                        <Pressable
                          key={interest}
                          onPress={() => toggleInterest(interest)}
                          style={[
                            styles.multiPill,
                            isSelected && styles.multiPillSelected,
                          ]}
                          accessibilityRole="checkbox"
                          accessibilityState={{ checked: isSelected }}
                        >
                          <Text
                            style={[
                              styles.multiPillText,
                              isSelected && styles.multiPillTextSelected,
                            ]}
                          >
                            {interest}
                          </Text>
                          {isSelected && (
                            <View style={styles.checkIconWrapper}>
                              <CheckIcon size={12} color={Palette.softWhite} strokeWidth={3} />
                            </View>
                          )}
                        </Pressable>
                      );
                    })}
                  </View>
                  {errors.interests ? (
                    <Text style={styles.inlineError}>{errors.interests}</Text>
                  ) : null}
                </View>

                {/* Preferred Learning Mode */}
                <View style={styles.fieldGroup}>
                  <Text style={styles.fieldLabel}>
                    Preferred Learning Mode (Optional)
                  </Text>
                  <View style={styles.pillsWrap}>
                    {LEARNING_MODES.map((mode) => {
                      const isSelected = draftForm.preferredLearningMode === mode.value;
                      return (
                        <Pressable
                          key={mode.value}
                          onPress={() =>
                            handleChange('preferredLearningMode', mode.value)
                          }
                          style={[
                            styles.chipPill,
                            isSelected && styles.chipPillSelected,
                          ]}
                          accessibilityRole="button"
                          accessibilityState={{ selected: isSelected }}
                        >
                          <Text
                            style={[
                              styles.chipPillText,
                              isSelected && styles.chipPillTextSelected,
                            ]}
                          >
                            {mode.label}
                          </Text>
                          {isSelected && (
                            <View style={styles.chipCheckDot}>
                              <CheckIcon size={10} color={Palette.softWhite} strokeWidth={3} />
                            </View>
                          )}
                        </Pressable>
                      );
                    })}
                  </View>
                </View>
              </YCard>
            </View>
          )}

          {/* STEP 4: FINAL PROFILE REVIEW */}
          {step === 4 && (
            <View style={styles.stepContainer}>
              {/* Privacy Reassurance Note */}
              <View style={styles.privacyCard}>
                <View style={styles.privacyHeader}>
                  <ShieldIcon size={18} color={Palette.sageDark} />
                  <Text style={styles.privacyTitle}>Privacy Protected</Text>
                </View>
                <Text style={styles.privacyText}>
                  Yogya uses your profile details solely to calculate eligibility matches. We never ask
                  for bank accounts, Aadhaar details, or sensitive income proofs during onboarding.
                </Text>
              </View>

              <YCard variant="elevated" style={styles.card}>
                <Text style={styles.reviewSectionHeading}>Profile Summary</Text>

                {/* Section 1: Basic */}
                <View style={styles.reviewGroup}>
                  <View style={styles.reviewGroupHeader}>
                    <Text style={styles.reviewGroupTitle}>1. Basic Details</Text>
                    <Pressable
                      onPress={() => setStep(1)}
                      hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
                    >
                      <Text style={styles.editAction}>Edit</Text>
                    </Pressable>
                  </View>
                  <View style={styles.reviewRow}>
                    <Text style={styles.reviewKey}>Display Name:</Text>
                    <Text style={styles.reviewVal}>{draftForm.displayName}</Text>
                  </View>
                  <View style={styles.reviewRow}>
                    <Text style={styles.reviewKey}>Language:</Text>
                    <Text style={styles.reviewVal}>{draftForm.preferredLanguage}</Text>
                  </View>
                  <View style={styles.reviewRow}>
                    <Text style={styles.reviewKey}>Location:</Text>
                    <Text style={styles.reviewVal}>
                      {draftForm.state === 'Other' && customStateInput
                        ? customStateInput
                        : draftForm.state}
                      {draftForm.district ? `, ${draftForm.district}` : ''}
                    </Text>
                  </View>
                </View>

                <View style={styles.divider} />

                {/* Section 2: Education */}
                <View style={styles.reviewGroup}>
                  <View style={styles.reviewGroupHeader}>
                    <Text style={styles.reviewGroupTitle}>2. Education</Text>
                    <Pressable
                      onPress={() => setStep(2)}
                      hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
                    >
                      <Text style={styles.editAction}>Edit</Text>
                    </Pressable>
                  </View>
                  <View style={styles.reviewRow}>
                    <Text style={styles.reviewKey}>Current Level:</Text>
                    <Text style={styles.reviewVal}>{draftForm.educationLevel}</Text>
                  </View>
                  {draftForm.stream ? (
                    <View style={styles.reviewRow}>
                      <Text style={styles.reviewKey}>Stream / Field:</Text>
                      <Text style={styles.reviewVal}>{draftForm.stream}</Text>
                    </View>
                  ) : null}
                  {draftForm.institutionType ? (
                    <View style={styles.reviewRow}>
                      <Text style={styles.reviewKey}>Institution:</Text>
                      <Text style={styles.reviewVal}>{draftForm.institutionType}</Text>
                    </View>
                  ) : null}
                </View>

                <View style={styles.divider} />

                {/* Section 3: Goals & Interests */}
                <View style={styles.reviewGroup}>
                  <View style={styles.reviewGroupHeader}>
                    <Text style={styles.reviewGroupTitle}>3. Goals & Interests</Text>
                    <Pressable
                      onPress={() => setStep(3)}
                      hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
                    >
                      <Text style={styles.editAction}>Edit</Text>
                    </Pressable>
                  </View>
                  <View style={styles.reviewRow}>
                    <Text style={styles.reviewKey}>Primary Goal:</Text>
                    <Text style={styles.reviewVal}>{draftForm.mainGoal}</Text>
                  </View>
                  <View style={styles.reviewInterestsBlock}>
                    <Text style={styles.reviewKey}>Selected Interests:</Text>
                    <View style={styles.reviewInterestsWrap}>
                      {draftForm.interests && draftForm.interests.length > 0 ? (
                        draftForm.interests.map((it) => (
                          <View key={it} style={styles.reviewInterestChip}>
                            <Text style={styles.reviewInterestText}>{it}</Text>
                          </View>
                        ))
                      ) : (
                        <Text style={styles.reviewVal}>None specified</Text>
                      )}
                    </View>
                  </View>
                  {draftForm.preferredLearningMode ? (
                    <View style={styles.reviewRow}>
                      <Text style={styles.reviewKey}>Learning Mode:</Text>
                      <Text style={styles.reviewVal}>
                        {draftForm.preferredLearningMode}
                      </Text>
                    </View>
                  ) : null}
                </View>

                {errors.form ? (
                  <Text style={[styles.inlineError, { marginTop: Spacing.two }]}>
                    {errors.form}
                  </Text>
                ) : null}
              </YCard>
            </View>
          )}

          <View style={styles.bottomSpacer} />
        </ScrollView>

        {/* ─── Persistent Bottom Action Bar ──────────────────────── */}
        <View style={styles.bottomBar}>
          <View style={styles.bottomBarButtons}>
            <View style={styles.buttonHalf}>
              <YButton
                title={step === 1 ? 'Cancel' : 'Back'}
                variant="outline"
                size="lg"
                onPress={handleBack}
                fullWidth
              />
            </View>
            <View style={styles.buttonHalf}>
              {step < 4 ? (
                <YButton
                  title="Continue"
                  variant="primary"
                  size="lg"
                  onPress={handleContinue}
                  fullWidth
                />
              ) : (
                <YButton
                  title="Complete Profile"
                  variant="primary"
                  size="lg"
                  onPress={handleComplete}
                  loading={isSubmitting}
                  fullWidth
                />
              )}
            </View>
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: Palette.ivory,
  },
  keyboardContainer: {
    flex: 1,
  },

  // Header & Step indicator
  header: {
    paddingHorizontal: Spacing.four,
    paddingTop: Spacing.two,
    paddingBottom: Spacing.twoHalf,
    backgroundColor: Palette.ivory,
    borderBottomWidth: 1,
    borderBottomColor: Palette.warmStone,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.two,
  },
  backButton: {
    paddingVertical: Spacing.one,
    paddingHorizontal: Spacing.one,
  },
  backButtonInner: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.one,
  },
  backButtonText: {
    fontSize: FontSize.sm,
    fontWeight: FontWeight.semibold,
    color: Palette.charcoal,
  },
  stepBadge: {
    backgroundColor: Palette.sageSurface,
    paddingHorizontal: Spacing.twoHalf,
    paddingVertical: Spacing.half,
    borderRadius: BorderRadius.full,
    borderWidth: 1,
    borderColor: Palette.sageLight,
  },
  stepBadgeText: {
    fontSize: FontSize.xs,
    fontWeight: FontWeight.bold,
    color: Palette.sageDark,
  },
  progressBarTrack: {
    height: 6,
    backgroundColor: Palette.warmStone,
    borderRadius: BorderRadius.full,
    overflow: 'hidden',
    marginBottom: Spacing.two,
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: Palette.sageDark,
    borderRadius: BorderRadius.full,
  },
  titleRow: {
    marginTop: Spacing.half,
  },
  stepHeadline: {
    fontSize: FontSize.xl,
    fontWeight: FontWeight.bold,
    color: Palette.charcoal,
  },
  stepSubhead: {
    fontSize: FontSize.sm,
    color: Palette.warmGray,
    marginTop: Spacing.half,
    lineHeight: FontSize.sm * 1.4,
  },

  // Scroll body
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: Spacing.four,
    paddingTop: Spacing.three,
  },
  stepContainer: {
    gap: Spacing.three,
  },
  card: {
    gap: Spacing.four,
    backgroundColor: Palette.softWhite,
  },

  // Field Groups & Typography
  fieldGroup: {
    gap: Spacing.one,
  },
  fieldLabel: {
    fontSize: FontSize.sm,
    fontWeight: FontWeight.bold,
    color: Palette.charcoal,
    letterSpacing: 0.1,
  },
  fieldHelper: {
    fontSize: FontSize.xs,
    color: Palette.warmGray,
    marginBottom: Spacing.one,
  },
  inlineError: {
    fontSize: FontSize.xs,
    color: Palette.brickRed,
    fontWeight: FontWeight.medium,
    marginTop: Spacing.one,
  },

  // Language selection pills
  pillsWrap: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.two,
  },
  languagePill: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: 46,
    paddingHorizontal: Spacing.three,
    paddingVertical: Spacing.one * 1.5,
    borderRadius: BorderRadius.md,
    borderWidth: 1.5,
    borderColor: Palette.warmStone,
    backgroundColor: Palette.softWhite,
    minWidth: 100,
    gap: Spacing.two,
  },
  languagePillSelected: {
    borderColor: Palette.sageDark,
    backgroundColor: Palette.sageSurface,
  },
  languagePillContent: {
    justifyContent: 'center',
  },
  languagePillText: {
    fontSize: FontSize.base,
    fontWeight: FontWeight.semibold,
    color: Palette.charcoal,
  },
  languagePillTextSelected: {
    color: Palette.charcoalDark,
    fontWeight: FontWeight.bold,
  },
  languagePillSub: {
    fontSize: FontSize.xs - 1,
    color: Palette.warmGray,
    marginTop: 1,
  },
  languagePillSubSelected: {
    color: Palette.sageDark,
  },
  pillCheckCircle: {
    width: 18,
    height: 18,
    borderRadius: 9,
    backgroundColor: Palette.sageDark,
    alignItems: 'center',
    justifyContent: 'center',
  },

  // Simple chip pills (States, Streams, Learning modes)
  chipPill: {
    flexDirection: 'row',
    alignItems: 'center',
    minHeight: 40,
    paddingHorizontal: Spacing.three,
    paddingVertical: Spacing.one * 1.5,
    borderRadius: BorderRadius.full,
    borderWidth: 1.5,
    borderColor: Palette.warmStone,
    backgroundColor: Palette.softWhite,
    gap: Spacing.one * 1.5,
  },
  chipPillSelected: {
    borderColor: Palette.sageDark,
    backgroundColor: Palette.sageSurface,
  },
  chipPillText: {
    fontSize: FontSize.sm,
    fontWeight: FontWeight.medium,
    color: Palette.charcoal,
  },
  chipPillTextSelected: {
    color: Palette.charcoalDark,
    fontWeight: FontWeight.bold,
  },
  chipCheckDot: {
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: Palette.sageDark,
    alignItems: 'center',
    justifyContent: 'center',
  },
  customStateWrapper: {
    marginTop: Spacing.two,
  },

  // Multi-select Interest pills
  labelRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  selectedCountBadge: {
    backgroundColor: Palette.terracottaSurface,
    paddingHorizontal: Spacing.two,
    paddingVertical: 2,
    borderRadius: BorderRadius.full,
  },
  selectedCountText: {
    fontSize: FontSize.xs,
    color: Palette.terracottaDark,
    fontWeight: FontWeight.bold,
  },
  multiPill: {
    flexDirection: 'row',
    alignItems: 'center',
    minHeight: 40,
    paddingHorizontal: Spacing.three,
    paddingVertical: Spacing.two,
    borderRadius: BorderRadius.md,
    borderWidth: 1.5,
    borderColor: Palette.warmStone,
    backgroundColor: Palette.softWhite,
    gap: Spacing.two,
  },
  multiPillSelected: {
    borderColor: Palette.sageDark,
    backgroundColor: Palette.sageSurface,
  },
  multiPillText: {
    fontSize: FontSize.sm,
    fontWeight: FontWeight.medium,
    color: Palette.charcoal,
  },
  multiPillTextSelected: {
    color: Palette.charcoalDark,
    fontWeight: FontWeight.bold,
  },
  checkIconWrapper: {
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: Palette.sageDark,
    alignItems: 'center',
    justifyContent: 'center',
  },

  // Selection list for Radio cards (Education)
  selectionList: {
    gap: Spacing.twoHalf,
    marginTop: Spacing.one,
  },
  selectionOption: {
    minHeight: 56,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: Spacing.threeHalf,
    paddingVertical: Spacing.twoHalf,
    borderRadius: BorderRadius.lg,
    borderWidth: 1.5,
    borderColor: Palette.warmStone,
    backgroundColor: Palette.softWhite,
    gap: Spacing.three,
  },
  selectionOptionSelected: {
    borderColor: Palette.sageDark,
    backgroundColor: Palette.sageSurface,
  },
  optionBadgeContainer: {
    minWidth: 42,
    height: 32,
    borderRadius: BorderRadius.sm,
    backgroundColor: Palette.warmStoneLight,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: Spacing.one,
  },
  optionBadgeContainerSelected: {
    backgroundColor: Palette.softWhite,
  },
  optionBadgeText: {
    fontSize: FontSize.xs,
    fontWeight: FontWeight.bold,
    color: Palette.warmGray,
  },
  optionBadgeTextSelected: {
    color: Palette.sageDark,
  },
  optionContent: {
    flex: 1,
  },
  optionTitle: {
    fontSize: FontSize.base,
    fontWeight: FontWeight.semibold,
    color: Palette.charcoal,
  },
  optionTitleSelected: {
    color: Palette.charcoalDark,
    fontWeight: FontWeight.bold,
  },
  radioCircle: {
    width: 22,
    height: 22,
    borderRadius: 11,
    borderWidth: 2,
    borderColor: Palette.warmStoneDark,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: Palette.softWhite,
  },
  radioCircleSelected: {
    borderColor: Palette.sageDark,
  },
  radioDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: Palette.sageDark,
  },

  // Goal option card
  goalOption: {
    minHeight: 76,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: Spacing.threeHalf,
    paddingVertical: Spacing.three,
    borderRadius: BorderRadius.lg,
    borderWidth: 1.5,
    borderColor: Palette.warmStone,
    backgroundColor: Palette.softWhite,
    gap: Spacing.three,
    overflow: 'hidden',
  },
  goalContent: {
    flex: 1,
    gap: Spacing.half,
  },
  goalTagBadge: {
    alignSelf: 'flex-start',
    backgroundColor: Palette.warmStoneLight,
    paddingHorizontal: Spacing.two,
    paddingVertical: 2,
    borderRadius: BorderRadius.sm,
    marginBottom: 2,
  },
  goalTagBadgeSelected: {
    backgroundColor: Palette.softWhite,
  },
  goalTagText: {
    fontSize: 10,
    fontWeight: FontWeight.bold,
    color: Palette.warmGray,
    textTransform: 'uppercase',
  },
  goalTagTextSelected: {
    color: Palette.sageDark,
  },
  goalDesc: {
    fontSize: FontSize.xs,
    color: Palette.warmGray,
    lineHeight: FontSize.xs * 1.45,
  },

  // Review step styles
  privacyCard: {
    backgroundColor: Palette.sageSurface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.threeHalf,
    borderWidth: 1,
    borderColor: Palette.sageLight,
    gap: Spacing.one,
  },
  privacyHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.two,
  },
  privacyTitle: {
    fontSize: FontSize.sm,
    fontWeight: FontWeight.bold,
    color: Palette.sageDark,
  },
  privacyText: {
    fontSize: FontSize.xs,
    color: Palette.charcoal,
    lineHeight: FontSize.xs * 1.55,
  },
  reviewSectionHeading: {
    fontSize: FontSize.lg,
    fontWeight: FontWeight.bold,
    color: Palette.charcoal,
  },
  reviewGroup: {
    gap: Spacing.two,
  },
  reviewGroupHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.half,
  },
  reviewGroupTitle: {
    fontSize: FontSize.base,
    fontWeight: FontWeight.bold,
    color: Palette.charcoal,
  },
  editAction: {
    fontSize: FontSize.sm,
    fontWeight: FontWeight.bold,
    color: Palette.sageDark,
  },
  reviewRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  reviewKey: {
    fontSize: FontSize.sm,
    color: Palette.warmGray,
    fontWeight: FontWeight.medium,
  },
  reviewVal: {
    fontSize: FontSize.sm,
    color: Palette.charcoal,
    fontWeight: FontWeight.semibold,
    textAlign: 'right',
    flex: 1,
    marginLeft: Spacing.two,
  },
  reviewInterestsBlock: {
    gap: Spacing.one,
    marginTop: Spacing.one,
  },
  reviewInterestsWrap: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.one,
    marginTop: Spacing.half,
  },
  reviewInterestChip: {
    backgroundColor: Palette.sageSurface,
    paddingHorizontal: Spacing.twoHalf,
    paddingVertical: Spacing.half,
    borderRadius: BorderRadius.sm,
    borderWidth: 1,
    borderColor: Palette.sageLight,
  },
  reviewInterestText: {
    fontSize: FontSize.xs,
    color: Palette.sageDark,
    fontWeight: FontWeight.medium,
  },
  divider: {
    height: 1,
    backgroundColor: Palette.warmStone,
    marginVertical: Spacing.one,
  },

  bottomSpacer: {
    height: Spacing.eight,
  },

  // Sticky bottom action bar
  bottomBar: {
    backgroundColor: Palette.softWhite,
    borderTopWidth: 1,
    borderTopColor: Palette.warmStone,
    paddingHorizontal: Spacing.four,
    paddingVertical: Spacing.three,
    ...Shadows.md,
  },
  bottomBarButtons: {
    flexDirection: 'row',
    gap: Spacing.three,
  },
  buttonHalf: {
    flex: 1,
  },
});
