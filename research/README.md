# Research

This directory is the repository's long-term research workspace. It exists so the protocol design can stay grounded in evidence while biometric cryptography, trust establishment, and recovery patterns are still being evaluated.

## Why This Research Exists

Silent Key is intentionally protocol-first. The research area captures the technical questions that must be answered before biometrics, hardware attestation, or post-quantum choices are promoted into the core implementation.

## Long-Term Research Goals

- Understand how to model identity without relying on a single device
- Evaluate biometric cryptosystems without treating biometrics as the secret itself
- Compare pairing and verification options such as WebAuthn, challenge-response signatures, and threshold schemes
- Track performance, usability, and security trade-offs before any production redesign

## Directory Guide

- [architecture/](architecture/) - Architecture notes and design decisions
- [papers/](papers/) - Papers, articles, RFCs, and standards references
- [benchmarks/](benchmarks/) - Benchmark results and methodology
- [experiments/](experiments/) - Experiment logs and reproducible results
- [notes/](notes/) - Open questions, assumptions, and working notes

## How to Add New Research

- Create a short markdown file in the most relevant subdirectory
- Start with the problem statement and the question being investigated
- Record the sources consulted and the decision or hypothesis being tested
- Capture the result, even if the result is that the idea should be deferred
- Link related notes instead of duplicating the same argument in multiple places

## Expected Format

Use this structure when adding a new research note:

1. Title
2. Problem statement
3. Context and current approaches
4. Sources and references
5. Decision, conclusion, or hypothesis
6. Follow-up questions
