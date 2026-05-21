---
name: demo-router
description: Use when routing a short support question to either account, billing, or access documentation.
---

# Demo Router

## Usage

Read the user question and return the most relevant documentation path.

## Safety Rules

- Do not invent documentation paths.
- If no route is supported, return `unknown`.

## Routes

- Account profile questions route to `docs/account.md`.
- Payment, invoice, and plan questions route to `docs/billing.md`.
- Login and permission questions route to `docs/access.md`.
