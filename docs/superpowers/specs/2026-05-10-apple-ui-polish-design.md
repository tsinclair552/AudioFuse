# Apple Design System — Surface Polish for AudioFuse

**Date:** 2026-05-10
**Status:** Approved for implementation
**Scope:** Surface polish — colors, typography, buttons, spacing, waveform styling. Existing layout and component structure preserved.

## Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Scope | Surface polish | Quickest path to Apple design language; lowest risk for a frozen Qt app |
| Color base | Light (canvas + parchment) | Clean utility feel, matches Apple's dominant surface mode |
| Button grammar | Blue pills (primary) + ghost outline (secondary) | Matches Apple's button-primary and button-secondary-pill |
| Waveform treatment | Action Blue bars on parchment + product shadow | Brand accent + Apple's single-shadow product grammar |
| Panel surface | Parchment (#f5f5f7) on white canvas | Creates Apple's signature alternating-surface rhythm |

## Color Palette

| Token | Hex | Qt Usage |
|---|---|---|
| canvas | `#ffffff` | Window background, central widget |
| parchment | `#f5f5f7` | Audio panel backgrounds |
| ink | `#1d1d1f` | All text, labels |
| primary | `#0066cc` | Button fills, waveform bars, interactive elements |
| ink-muted-48 | `#7a7a7a` | Placeholder text, secondary labels |
| hairline | `#e0e0e0` | Panel borders |

All implemented via Qt stylesheets on `main_window.py` and `audio_panel.py`. No runtime color computation.

## Typography

| Element | Font | Size | Weight | Color |
|---|---|---|---|---|
| Panel title ("Clip 1", "Clip 2") | `system-ui` | 28px | 300 | ink (#1d1d1f) |
| Duration label ("01:30") | `system-ui` | 17px | 400 | ink (#1d1d1f) |
| Button labels | `system-ui` | 14px | 400 | on-primary / primary |
| Placeholder / error | `system-ui` | 14px | 400 | ink-muted-48 (#7a7a7a) |

Uses `system-ui` which resolves to SF Pro on macOS — no custom font loading needed.

## Buttons

### Primary (Preview, Download)
- Background: Action Blue `#0066cc`
- Text: White `#ffffff`
- Shape: Pill (`border-radius: 9999px`)
- Padding: 8px 22px
- Active: `transform: scale(0.95)`

### Secondary (Gap toggle)
- Background: Transparent
- Border: 1px solid Action Blue `#0066cc`
- Text: Action Blue `#0066cc`
- Shape: Pill (`border-radius: 9999px`)
- Padding: 8px 22px
- Text toggles: "Gap: OFF" ↔ "Gap: ON"

## Audio Panel

- Background: Parchment `#f5f5f7`
- Border: 1px hairline `#e0e0e0`, rounded 18px
- Drop shadow: `rgba(0,0,0,0.22) 3px 5px 30px` (Apple's single product shadow)
- Internal padding: 24px
- Clickable whole area (click to load, drag-and-drop)
- Empty state: "Click to load" placeholder text
- Loaded state: title + waveform bars + duration label

## Waveform

- Bar color: Action Blue `#0066cc`
- Background: Transparent (parchment shows through)
- Drawn via QPainter (unchanged rendering logic, only color changes)
- Empty state shows placeholder text instead of waveform

## Layout

- Two panels side by side, 24px gap between them
- Panels sit on white canvas window background
- Controls row centered below panels, generous vertical spacing
- Window minimum size: 600x300 (unchanged)

## Files to Modify

| File | Changes |
|---|---|
| `main_window.py` | Apply global stylesheet (colors, typography), restyle buttons as pills, restyle panels |
| `audio_panel.py` | Set parchment background, hairline border, 18px radius, product shadow, placeholder text styling; change waveform paint color to Action Blue |

## What Stays the Same

- Application logic (audio engine, loading, preview, export)
- Layout structure (two side-by-side panels, bottom controls row)
- Drag-and-drop behavior
- Waveform rendering algorithm (only color changes)
- Window title, minimum size
- All audio processing code

## Non-Goals

- No layout restructuring (panels remain side-by-side, not stacked)
- No new components (no custom nav bar, no sticky bar, no frosted glass)
- No dark mode
- No runtime theme switching
- No custom font loading (relies on system fonts)
