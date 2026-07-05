# Project Overview

## Mission

Build an open-source RV trip binder system that helps travelers keep a live binder during the trip and produce a final binder after the trip from the same structured trip data.

## What this is

RV Expedition Logbook is a reusable binder-oriented framework for RV trips:

- a Hermes skill for conversational trip capture and follow-up questions
- schemas for consistent trip data
- templates for binder generation
- documentation for the domain model and workflows
- examples and validation tools

## What this is not

This is not a private cloud trip database.

The repository should not contain real user travel history, private journals, expenses, photos, or location records. Those belong in Hermes/Hindsight or another private user-owned store.

## Primary users

- RV travelers who want a practical binder during and after a trip
- Hermes agents that need structured instructions for RV trip capture
- developers improving importers, renderers, and binder workflows

## Primary outputs

The main outputs are:

1. current binder snapshots during the trip
2. final binders after the trip
3. reusable sample artifacts and tools that support those workflows
