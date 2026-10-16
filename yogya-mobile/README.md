# Yogya Mobile (योग्य)

An AI-powered opportunity navigator for students across rural and urban India. Yogya connects students to verified government scholarships, skill development training programs, youth welfare schemes, and industrial apprenticeships.

---

## 🎨 Visual Identity & Design System

Yogya is designed with a **warm, student-friendly, handcrafted editorial identity** that feels trustworthy, approachable, and accessible across low-end mobile devices and diverse regional scripts.

* **Warm Canvas & Surfaces**:
  * Canvas Background: Warm Ivory (`#F7F4ED`)
  * Card Surface: Soft White (`#FFFDF8`)
  * Soft Sage Surface: `#E4E5D8`
  * Soft Terracotta Surface: `#EADBCB`
  * Borders & Dividers: Warm Stone (`#E3DED4`)
* **Readable Typography**:
  * Primary Text: Charcoal (`#383A36`)
  * Secondary Text: Warm Gray (`#77766E`)
  * Scale: Fluid 12px captions to 36px hero titles
* **Earthy Accents**:
  * Primary Accent: Muted Sage (`#747D68` / `#565E4C`)
  * Secondary Accent: Muted Terracotta (`#B77C5C` / `#965C3E`)
* **Accessible Semantic Signals**:
  * Success: Muted Forest Green (`#3D683A` / `#E4EDE2`)
  * Warning / Live Notice: Muted Ochre (`#8C5F1E` / `#F5ECDB`)
  * Error: Restrained Brick Red (`#9E433C` / `#F6E4E2`)
* **Hand-Drawn Vector Illustrations**: 9 lightweight, local SVG vector illustrations in [HandDrawnIllustrations.tsx](file:///d:/yogya-mobile/src/components/illustrations/HandDrawnIllustrations.tsx) (no runtime image fetches, zero network latency).
* **Handcrafted Icon System**: Outline vector SVGs in [NavIcons.tsx](file:///d:/yogya-mobile/src/components/icons/NavIcons.tsx) with rounded terminals, consistent line weights, and zero third-party font icon dependencies.

---

## 📱 App Architecture & Screens

```
src/
├── app/
│   ├── _layout.tsx              # Root Stack navigation, splash hydration & providers
│   ├── index.tsx                # Welcome screen (editorial hero & smart returning student flow)
│   ├── onboarding.tsx           # 4-step mobile onboarding (profile, education, goals, review)
│   ├── (tabs)/
│   │   ├── _layout.tsx          # Bottom tab bar (Home, Explore, Saved, Profile)
│   │   ├── home.tsx             # Central dashboard (search, filters, category cards, listings)
│   │   ├── explore.tsx          # Pathway discovery (scholarships, training, schemes, jobs)
│   │   ├── saved.tsx            # Local bookmarks with live count & removal actions
│   │   └── profile.tsx          # Student details, privacy protection, and editing flow
│   └── opportunity/
│       └── [id].tsx             # Detailed opportunity view with "Check My Fit" self-check
├── components/
│   ├── icons/NavIcons.tsx       # Handcrafted outline SVG icons
│   ├── illustrations/           # Hand-drawn local SVG illustrations
│   └── ui/                      # Reusable components (YButton, YCard, YInput)
├── constants/theme.ts           # Centralized color palette, fonts, spacing, shadows
├── context/                     # ProfileContext & SavedContext
├── data/mock.ts                 # 4 verified demonstration opportunity records
└── services/
    ├── api.ts                   # Fetch wrapper with network error handling
    ├── opportunities.ts         # Normalizes FastAPI schema with mock fallback
    └── storage.ts               # AsyncStorage persistence layer
```

---

## 🚀 How to Run and View the App on Expo Go

You can run and test the Yogya app on your physical mobile phone using the free **Expo Go** app.

### 1. Prerequisites
1. Install **Node.js** (v18 or higher) on your computer.
2. Install **Expo Go** on your physical phone:
   * **Android**: Download [Expo Go on Google Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)
   * **iOS**: Download [Expo Go on Apple App Store](https://apps.apple.com/app/expo-go/id982107779)
3. Ensure your computer and phone are connected to the **same Wi-Fi network**.

---

### 2. Starting the Development Server

From the `yogya-mobile` directory, run:

```bash
# Start the Metro bundler
npx expo start
```

This will display an interactive terminal dashboard and a large **QR Code**.

> **Tip for different networks or cellular data:**
> If your phone and PC are on different Wi-Fi networks (or mobile hotspot), use Expo's tunnel mode:
> ```bash
> npx expo start --tunnel
> ```

---

### 3. Opening the App on Your Phone

#### On Android:
1. Open the **Expo Go** app on your phone.
2. Tap the blue **"Scan QR code"** button.
3. Point your camera at the QR code displayed in your terminal.
4. The JavaScript bundle will download and the app will open immediately.

#### On iPhone / iPad (iOS):
1. Open your phone's native **Camera app**.
2. Point your camera at the QR code in your terminal.
3. Tap the yellow **"Open in Expo Go"** banner that appears at the top.

#### In Web Browser (Alternative):
Press <kbd>w</kbd> in the terminal or run:
```bash
npm run web
```

---

### 4. Expo Go Developer Menu & Floating Button Tip

* **To open the developer menu**: Shake your device or long-press the screen with **3 fingers**.
* **Floating Settings Button**: The floating blue/gray gear icon that sometimes appears in Expo Go is Expo's development menu shortcut. It is disabled programmatically in [_layout.tsx](file:///d:/yogya-mobile/src/app/_layout.tsx). If you still see it on your device, shake your device, tap **Settings**, and toggle off **"Show floating action button"**.

---

## 🔌 Connecting to Backend API (Optional)

The mobile app runs out-of-the-box with local verified mock data. To connect to a live FastAPI backend:

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Configure your computer's local LAN IP:
   ```env
   # On mobile, use your computer's local Wi-Fi IP (not localhost):
   EXPO_PUBLIC_API_URL=http://192.168.1.15:8000
   ```
3. Restart the dev server with cache cleared:
   ```bash
   npx expo start -c
   ```

---

## 🧪 Verification & Health Check

* **TypeScript Compilation**:
  ```bash
  npx tsc --noEmit
  ```
* **Web Bundle Export Test**:
  ```bash
  npx expo export -p web
  ```
