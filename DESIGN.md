---
version: alpha
name: "NoteNest"
description: "A trusted academic library with an expressive public welcome and focused student workspace."
colors:
  ink: "#172033"
  muted: "#5F6B85"
  canvas: "#F7F8FC"
  surface: "#FFFFFF"
  primary: "#5B4BE7"
  primary-deep: "#4034B6"
  blue: "#2477E8"
  lavender: "#F0EFFF"
  border: "#E3E6EF"
  success: "#16846A"
  danger: "#C33452"
typography:
  display:
    fontFamily: "Georgia, 'Times New Roman', serif"
  sans:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
  mono:
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace"
rounded:
  DEFAULT: "0.875rem"
  sm: "0.625rem"
  md: "0.875rem"
  lg: "1.25rem"
  pill: "999px"
spacing:
  page-max: "76rem"
  section-gap: "7rem"
components:
  button: { emphasis: "solid, outline, ghost", intent: "brand, neutral, danger" }
  card: { radius: "1.25rem", border: "1px solid var(--border)" }
  dialog: { radius: "1.25rem", focus: "app-owned" }
  toast: { placement: "bottom-right" }
---

# NoteNest Design System

## Overview

NoteNest is a hybrid experience for SR University students: the public side feels like a carefully indexed study journal, while the application is a calm, efficient library. The signature is a quiet indigo "knowledge current"—a fine radial grid and selective violet-blue glow behind discovery moments. It should never become a generic corporate dashboard, a loud gamer interface, or a glassmorphism collage.

Runtime CSS variables in `frontend/src/styles.css` are canonical. This document records their purpose and must change with them.

## Colors

`ink` carries reading hierarchy; `canvas` keeps long study sessions low glare; `primary` is reserved for meaningful progress and primary actions. Violet and blue appear together only in branded moments, not every card. Status colors are semantic and always paired with text.

## Typography

The editorial serif display face is limited to landing-page statements and compact page titles. All operational UI uses the sans stack for legibility. Labels are sentence case; metadata is concise and tabular where helpful.

## Layout

The public site uses a 76rem maximum reading frame. The app shell has a persistent navigation rail on desktop and a compact header plus horizontal navigation on smaller screens. Cards reflow from three columns to one; no interaction relies on hover.

## Elevation & Depth

Static surfaces use borders and tonal separation first. Soft shadows appear on floating headers, dialogs, and interactive cards only. Background decoration stays behind content and respects reduced motion.

## Shapes

Controls use 0.625–0.875rem corners; large panels use 1.25rem; filters and metadata use pills. No square Bootstrap controls or exaggerated pill cards.

## Components

Buttons preserve their footprint while busy. Native form fields own data entry, with inline error and help text. The shared dialog confirms deletion. Toasts provide short secondary feedback. Search has a visible clear control. Motion communicates navigation or state and disables under reduced motion.

## Do's and Don'ts

- **Do:** let titles, subjects, and file details do the visual work.
- **Do:** keep every destructive action behind the same confirmation dialog.
- **Don't:** invent student activity, statistics, notifications, or backend capabilities.
- **Don't:** use a gradient where typography or layout provides clearer hierarchy.
