---
name: Madrasah Vibrant
colors:
  surface: '#e2ffff'
  surface-dim: '#aae5e5'
  surface-bright: '#e2ffff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#c4feff'
  surface-container: '#bef9f9'
  surface-container-high: '#b8f3f4'
  surface-container-highest: '#b3edee'
  on-surface: '#002020'
  on-surface-variant: '#3a4a47'
  inverse-surface: '#003738'
  inverse-on-surface: '#c1fcfc'
  outline: '#6a7a78'
  outline-variant: '#b9cac7'
  surface-tint: '#006a63'
  primary: '#006a63'
  on-primary: '#ffffff'
  primary-container: '#00fdec'
  on-primary-container: '#007169'
  inverse-primary: '#00decf'
  secondary: '#00696b'
  on-secondary: '#ffffff'
  secondary-container: '#2ff7fa'
  on-secondary-container: '#006e70'
  tertiary: '#00658e'
  on-tertiary: '#ffffff'
  tertiary-container: '#c7e7ff'
  on-tertiary-container: '#006c96'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#00fdec'
  primary-fixed-dim: '#00decf'
  on-primary-fixed: '#00201d'
  on-primary-fixed-variant: '#00504a'
  secondary-fixed: '#35fafd'
  secondary-fixed-dim: '#00dcdf'
  on-secondary-fixed: '#002020'
  on-secondary-fixed-variant: '#004f51'
  tertiary-fixed: '#c7e7ff'
  tertiary-fixed-dim: '#83cfff'
  on-tertiary-fixed: '#001e2e'
  on-tertiary-fixed-variant: '#004c6c'
  background: '#e2ffff'
  on-background: '#002020'
  surface-variant: '#b3edee'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '800'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  title-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-caps:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 14px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px
  xxl: 32px
  gutter: 16px
  touch-target: 48px
---

## Brand & Style

The design system is built on a philosophy of **Vibrant Energy**, modernizing Islamic academic assessment through an interface that feels like a high-performance digital laboratory. It targets educators who require high-visibility productivity tools that maintain a sense of urgency and clarity.

The aesthetic is a blend of **Vibrant Minimalism** and **Glassmorphism**, characterized by:
- **Luminous Energy:** A move from muted tones to high-saturation accents that keep the user engaged during repetitive data entry.
- **Atmospheric Depth:** Multi-layered, low-opacity shadows and frosted glass surfaces that create a sense of weightless hierarchy.
- **Tactile Responsiveness:** Subtle scale-down transforms and shadow shifts on interaction to provide physical feedback during high-frequency tasks.
- **Academic Precision:** A spacious layout that uses airy separations to reduce cognitive load while highlighting critical student data.

## Colors

The palette is anchored by **Electric Cyan**, signifying modern digital scholarship and clarity. It is supported by a range of vibrant aquas and blues that provide maximum visibility and a high-tech academic feel.

- **Primary (Electric Cyan):** Used for critical actions, navigation focal points, and active states.
- **Secondary (Vibrant Aqua):** Used for supportive UI elements and professional contrast.
- **Tertiary (Sky Brilliance):** Reserved for high-achievement markers and specialized functional indicators.
- **Neutral (Slate Teal):** A deep, saturated teal-grey that provides a sturdy anchor for the vibrant foreground elements.

**Functional States:**
- **Success (Tuntas):** Background `#00FDEC` (20% opacity) with Text `#008077`.
- **Error/Alert (Belum Tuntas):** Background `#FFDAD6` with Text `#BA1A1A`.
- **Warning:** Background `#FFF3CD` with Text `#8A5A00`.

## Typography

This design system utilizes **Inter** exclusively to ensure maximum legibility for numerical data and academic records.

- **Numerical Clarity:** When displaying scores or student IDs, use `Semi-Bold` or `Bold` weights to ensure they are the primary focal point of the container.
- **Vertical Rhythm:** Maintain generous line-heights (minimum 1.4x) to prevent text crowding in multi-line student notes.
- **Hierarchy:** Use `label-caps` for metadata like "NIS" or "KELAS" to differentiate labels from dynamic student data.

## Layout & Spacing

The layout follows a **Fluid Mobile-First** model, optimized for one-handed "thumb-zone" operation. 

- **Outer Margins:** A consistent `16px` (`gutter`) padding is applied to the left and right of the viewport.
- **Card Spacing:** Use `12px` (`md`) vertical spacing between list items to prevent accidental taps while maintaining high data density.
- **Touch Targets:** All interactive elements (buttons, toggles, steppers) must maintain a minimum hit area of `48px`.
- **Safe Areas:** Layouts must dynamically account for device notches and home indicators, particularly for the floating action bars.

## Elevation & Depth

Visual hierarchy is established through **Ambient Shadows** and **Glassmorphism**, creating a layered environment that feels light and accessible.

- **Surface Layer (Cards):** Use a soft, multi-layered shadow `0px 6px 20px rgba(71, 128, 129, 0.08)` to lift primary assessment cards off the neutral background.
- **Interaction Depth:** On-press, card elevation should decrease to `0px 2px 8px rgba(71, 128, 129, 0.12)` combined with a `scale(0.98)` transform.
- **Floating Layer (Action Bars):** Use `backdrop-filter: blur(12px)` with a semi-transparent background `rgba(255, 255, 255, 0.90)` and a more aggressive elevation: `0 14px 32px rgba(71, 128, 129, 0.18)`.
- **Outlines:** Use low-contrast hairline borders (`1px solid rgba(71, 128, 129, 0.2)`) on all cards to maintain structural integrity.

## Shapes

The shape language is defined by **Rounded (Level 2)** containers, providing a friendly and modern character.

- **Primary Containers:** Cards and input fields use `16px` (`rounded-lg`) corners.
- **High-Interaction Elements:** Buttons and pill-shaped status badges use `32px` (`rounded-xl`) or full `999px` curves to signal touchability.
- **Drawers & Modals:** Top-aligned sheet modals use a super-large `32px` (`rounded-xl`) radius on top-left and top-right corners only.

## Components

### Buttons
- **Primary:** 52px height, Electric Cyan (`#00FDEC`) background, Dark Slate text. Shadow: `0 4px 14px rgba(0, 253, 236, 0.3)`.
- **Secondary:** Sky Brilliance (`#0CB1F4`) background with White text. Flat profile.
- **Steppers:** Circle or heavily rounded square `-` and `+` buttons sized at `40px` for incrementing counts.

### Input Fields
- **Base:** 48px height with 16px corner radius. 
- **Focus State:** Electric Cyan border with a soft-glow focus ring: `0 0 0 4px rgba(0, 253, 236, 0.2)`.

### Assessment Cards
- **Structure:** White surface with 16px padding.
- **Features:** Must include a clear student name in `Headline Medium`, a dedicated zone for error steppers, and a high-visibility score output in the far right using the primary color.

### Sticky Save Bar
- **Position:** Anchored to bottom, floating above navigation.
- **Style:** Glassmorphic with a 24px top radius. Uses the Tertiary color as a vibrant accent for the "Save" action.

### Status Badges
- Pill-shaped tags with `label-caps` typography. The background should be a 15% opacity version of the status color for a "glowing" effect.