---
name: Madrasah Excellence System
colors:
  surface: '#f9f9ff'
  surface-dim: '#cfdaf2'
  surface-bright: '#f9f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f0f3ff'
  surface-container: '#e7eeff'
  surface-container-high: '#dee8ff'
  surface-container-highest: '#d8e3fb'
  on-surface: '#111c2d'
  on-surface-variant: '#3d4947'
  inverse-surface: '#263143'
  inverse-on-surface: '#ecf1ff'
  outline: '#6d7a77'
  outline-variant: '#bcc9c6'
  surface-tint: '#006a61'
  primary: '#00685f'
  on-primary: '#ffffff'
  primary-container: '#008378'
  on-primary-container: '#f4fffc'
  inverse-primary: '#6bd8cb'
  secondary: '#505f76'
  on-secondary: '#ffffff'
  secondary-container: '#d0e1fb'
  on-secondary-container: '#54647a'
  tertiary: '#595c5e'
  on-tertiary: '#ffffff'
  tertiary-container: '#727577'
  on-tertiary-container: '#fbfdff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#89f5e7'
  primary-fixed-dim: '#6bd8cb'
  on-primary-fixed: '#00201d'
  on-primary-fixed-variant: '#005049'
  secondary-fixed: '#d3e4fe'
  secondary-fixed-dim: '#b7c8e1'
  on-secondary-fixed: '#0b1c30'
  on-secondary-fixed-variant: '#38485d'
  tertiary-fixed: '#e0e3e5'
  tertiary-fixed-dim: '#c4c7c9'
  on-tertiary-fixed: '#191c1e'
  on-tertiary-fixed-variant: '#444749'
  background: '#f9f9ff'
  on-background: '#111c2d'
  surface-variant: '#d8e3fb'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  title-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
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
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  container-max: 1440px
  sidebar-width: 260px
  sidebar-collapsed: 80px
  gutter: 1.5rem
  margin-mobile: 1rem
  margin-desktop: 2rem
  component-gap: 1rem
  table-row-height: 2.75rem
---

## Brand & Style

The design system is engineered for the Madrasah Tsanawiyah (MTs) environment, prioritizing academic integrity, organizational clarity, and administrative efficiency. The aesthetic leans into **Corporate Modernism** with a focus on high-density information display and systematic reliability.

The target audience consists of educators and administrators who require a tool that feels authoritative yet accessible. The UI evokes a sense of "digital calm" to reduce cognitive load during complex data entry and assessment tasks. We utilize a structured grid, generous whitespace in headers, and precise functional elements to ensure the software stays out of the user's way while facilitating accurate reporting.

## Colors

The color strategy uses a "Madrasah Teal" (#0D9488) as the primary anchor, symbolizing both growth and the traditional color associations of Islamic educational institutions in Indonesia. 

- **Primary:** Used for key actions, active navigation states, and primary brand moments.
- **Secondary:** A professional slate gray used for icons, sub-labels, and secondary buttons.
- **Surface & Backgrounds:** We use a hierarchy of whites and extremely light grays (#F8FAFC) to create distinct regions without relying on heavy borders.
- **Semantic Colors:** Success, Warning, and Error colors are used strictly for assessment scores, progress indicators, and validation states to ensure immediate legibility of teacher performance metrics.

## Typography

This design system utilizes **Inter** exclusively to ensure maximum legibility in data-heavy contexts. The typeface was chosen for its tall x-height and exceptional clarity in small font sizes, which is critical for the "spreadsheet-like" assessment views.

- **Headlines:** Use Bold or SemiBold weights with tighter letter spacing for a grounded, authoritative feel.
- **Data Tables:** Use `body-sm` (13px) for table cells to maximize information density while maintaining a professional appearance.
- **Labels:** Uppercase labels with slight tracking are reserved for section headers and table column headers to provide clear visual categorization.

## Layout & Spacing

The layout is built on a **Fluid Grid** system that maximizes horizontal space for assessment tables. 

1. **Sidebar:** A collapsible left-hand navigation is the primary anchor. It transitions from 260px to 80px to give more room for data entry.
2. **Main Content:** Occupies the remaining width with a maximum container cap of 1440px to prevent excessive line lengths on ultra-wide monitors.
3. **Rhythm:** An 8px (0.5rem) base unit governs all padding and margins. 
4. **Data Density:** In assessment modules, padding is tightened (8px vertical) to allow teachers to see more rows of students or criteria at once without excessive scrolling.

## Elevation & Depth

This design system utilizes **Tonal Layers** and **Low-Contrast Outlines** rather than aggressive shadows. This keeps the interface feeling "flat" and efficient, like a modern productivity tool.

- **Level 0 (Background):** #F8FAFC (Slate 50) for the main application canvas.
- **Level 1 (Cards/Sidebar):** Pure White (#FFFFFF) with a thin 1px border (#E2E8F0). No shadow.
- **Level 2 (Dropdowns/Modals):** Pure White with a soft, diffused shadow (0px 10px 15px -3px rgba(0,0,0,0.1)) to indicate temporary interaction.
- **State Changes:** Hovering over table rows or list items should trigger a subtle background change to #F1F5F9 rather than a lift effect.

## Shapes

The design system uses **Soft (0.25rem)** roundedness for standard components. This provides a professional, "stable" look that feels more modern than sharp corners but more serious than highly rounded "pill" shapes.

- **Buttons & Inputs:** 4px (0.25rem) radius.
- **Cards & Modals:** 8px (0.5rem) radius for a slightly softer container feel.
- **Status Badges:** Fully rounded (pill) to distinguish them from interactive buttons.

## Components

### Buttons
- **Primary:** Solid Teal (#0D9488) with white text. Used for "Simpan" (Save) or "Kirim" (Submit).
- **Secondary:** Ghost style with Slate #64748B border and text. Used for "Batal" (Cancel) or "Ekspor".
- **Density:** Provide a "Compact" variant for use within table rows.

### Data Tables (The Core Component)
- **Header:** Light gray background (#F1F5F9) with `label-md` typography.
- **Cells:** `body-sm` text. Input fields within tables should have no borders by default, gaining a teal outline only on focus (spreadsheet-style).
- **Zebra Striping:** Use very subtle off-white striping for rows with more than 15 entries.

### Sidebar
- Icons should be line-art style (e.g., Lucide or Heroicons) for a clean look.
- Active state: Background #F0FDFA (Teal 50) with a 4px left-border of Primary Teal.

### Form Inputs
- Standard labels appear above the field in `body-sm` Bold.
- Focus state: 2px Teal ring with 0.1 opacity blur.

### Cards (Dashboard Metrics)
- Simple white containers with a 1px border.
- Include a small trend indicator (Success or Error color) next to the main metric.