# Streamlit UI review fixes

This commit addresses UI issues observed in the deployed app screenshot.

## Changes

- Adds a user-controlled `Interface theme` selector with Dark and Light modes.
- Fixes the overly bright sidebar by applying mode-aware sidebar CSS.
- Adds a reusable `Gender filter` selector and filtering helpers for reference profiles.
- Adds a sentence deduplication helper for profile-reading text.
- Adds an explicit `Score input mode` label and help text for the slider/numeric input selector.

## Design rule

Gender is metadata only. It can be used to filter the reference dataset but must never affect scoring, positioning, interpretation, or comparison logic.

## Follow-up

The next UI integration step can wire the gender filtering helper directly into every reference-table and reference-map rendering path if any legacy path still bypasses the shared filter.
