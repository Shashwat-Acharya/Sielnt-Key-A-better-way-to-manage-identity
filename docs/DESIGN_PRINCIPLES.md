# Silent Key Design Principles

A comprehensive Q&A document covering the foundational design principles, threat model, and architectural concepts of Silent Key.

---

## Layer 1: System Boundary
*(What are we building — and what are we NOT building?)*

### Q1. What problem are we solving?
**A:**
We are solving the problem of loss of access due to forgotten passwords or unavailable primary devices, by enabling users to prove their identity without remembering secrets and without depending on one specific device.

### Q2. What does Silent Key do?
**A:**
Silent Key provides passwordless identity verification that allows a user to authenticate across devices using their physical presence, not stored knowledge.

### Q3. What does Silent Key explicitly NOT do?
**A:**

- We do not manage user accounts for third‑party services
- We do not store user behavior or activity
- We do not authorize actions (only authenticate identity)
- We do not act as a password manager or vault
- We do not monetize user data

### Q4. How is this different from "Sign in with Google"?
**A:**
Google is an identity provider that centralizes trust and data.
Silent Key is an identity verifier that minimizes trust and avoids centralized user profiling.

---

## Layer 2: Threat Model
*(What can go wrong, and how bad is it?)*

### Q5. What happens if the database is stolen?
**A:**
The system must be designed so that a stolen database cannot reconstruct identities or biometrics.
No raw biometric data should be stored centrally.

### Q6. What if someone spoofs a fingerprint?
**A:**
Biometrics are treated as local authorization signals, not as cryptographic secrets.
Spoofing a biometric alone should not be sufficient to impersonate a user.

### Q7. What if the QR flow is intercepted?
**A:**
QR codes must represent short‑lived, single‑use challenges, not identity data.
Interception should result only in a failed or expired authentication.

### Q8. What if the desktop app is compromised?
**A:**
The desktop app is treated as untrusted by default.
No long‑term secrets should be accessible to it without user‑present authorization.

### Q9. What if law enforcement or a third party requests user data?
**A:**
The system should be architected so that Silent Key cannot meaningfully comply, because it does not possess usable biometric or identity secrets.

---

## Layer 3: Biometric & Identity Model
*(Where does identity actually live?)*

### Q10. Is the user's identity stored on Silent Key servers?
**A:**
No. Silent Key should not store raw biometrics or stable identity secrets centrally.

### Q11. Then what role do biometrics play?
**A:**
Biometrics are used only to authorize access to a cryptographic key — they are not the key itself.

### Q12. Why can't biometrics encrypt the private key directly?
**A:**
Because biometrics are probabilistic (they change slightly every scan), while cryptography requires exact reproducibility.
Using biometrics as encryption keys would cause random lockouts.

### Q13. What is the corrected mental model?
**A:**
```
Biometrics unlock → secure environment → releases a stable private key
```

**Not:**
```
Biometrics → become the private key
```

### Q14. Where is the private key generated and stored?
**A:**
It must be generated deterministically and stored in a way that:

- Is stable
- Is protected from extraction
- Requires user presence to access

*(The exact mechanism is a later architectural decision.)*

---

## Layer 4: Core User Flow (Happy Path)
*(What does the user actually experience?)*

### Q15. Describe the simplest successful use case.
**A:**
A user logs into a system on a device without a fingerprint scanner by proving their identity using their physical presence and a secondary device.

### Q16. What does the user see?
**A:**

1. A login screen
2. A QR code labeled clearly as a one‑time identity request

### Q17. What does the user do?
**A:**

1. Scans the QR code using any available phone
2. Authenticates locally using biometrics
3. Confirms the login request

### Q18. What reassures the user?
**A:**

- Clear messaging that no biometric data is shared
- Visible confirmation of what device is requesting access
- Explicit user consent before authentication completes

### Q19. What should the user never feel?
**A:**

- Confused about where their data is
- Afraid they are "giving" their fingerprint to Silent Key
- Locked in or unable to recover access

---

## Layer 5: Conceptual Modules
*(How the system is broken down — without tech details)*

### Q20. What are the core modules?
**A:**

1. Identity Initialization Module
2. Local Authorization (Biometric Gate) Module
3. Cross‑Device Challenge Module
4. Verification & Response Module
5. Recovery & Continuity Module

### Q21. What defines a good module?
**A:**
Each module must clearly state:

- Purpose
- Inputs
- Outputs
- Failure modes

If a module cannot fail safely, it should not exist.
