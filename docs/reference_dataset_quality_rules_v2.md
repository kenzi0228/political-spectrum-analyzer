# Reference dataset quality rules v2

This document defines the quality gates used before expanding the reference dataset beyond 150 profiles.

## Goals

The dataset must remain:

- structurally consistent;
- filterable;
- ideologically readable;
- historically diverse;
- geographically explicit without using a forced `region` field;
- safe for future expansion toward 500 profiles.

## Core rules

The reference dataset must satisfy:

- no duplicate names;
- exactly 500 profiles at the current stage;
- no `region` column;
- required schema v2 columns present;
- non-empty country, country codes, period, century, ideology family, ideology subtype, role category, confidence, notes, and tags;
- x and y coordinates inside `[-4, 4]`;
- uncertainty values `ux` and `uy` strictly positive;
- confidence values limited to `low`, `medium`, or `high`;
- estimated values limited to boolean-like values;
- ideology families kept broad enough for filtering;
- at least several country codes represented;
- at least several centuries represented;
- at least several role categories represented.

## Expansion rule

The 500-profile milestone is the current reference stage, these tests must continue passing.


## Dataset expansion to 500 profiles

The reference dataset has been expanded from 150 to 500 profiles while preserving schema v2 and quality-gate consistency.


## Gender metadata

The reference dataset includes a `gender` column with normalized values `male`, `female`, or `unknown`. It is used for dataset auditing and optional future UI filtering.
