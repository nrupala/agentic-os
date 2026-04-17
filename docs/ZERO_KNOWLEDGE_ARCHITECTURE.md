# Zero-Knowledge Architecture (NUCLEAR GRADE SAFETY)

> **NUCLEAR PLANT THINKING**: Every variable, function, handoff must be verified. If data stays in RAM, it's exposed. If data is in file, it's encrypted.

---

## Problem: RAM is Vulnerable

| Threat | RAM Exposure | File Exposure |
|--------|-------------|----------------|
| Memory dump | YES - all data visible | N/A |
| Process crash | Data lost | File persists |
| Disk stolen | N/A | Unencrypted = readable |
| Malware | YES | YES if unencrypted |
| RAM exposure | User data visible | Encrypted = safe |

---

## Solution: Zero-Knowledge File-Based Architecture

```
BEFORE (RAM-based):
==================
Step 3 -> dict in RAM -> Step 4
If RAM fails -> ALL LOST

AFTER (Zero-Knowledge File-Based):
==================================
Step 3 -> encrypt to .enc file -> Step 4 reads from file
If RAM fails -> file persists, can resume
```

---

## New Modules

### 1. zero_knowledge_handoff.py
Encrypted file signaling between phases.

| Function | Purpose |
|----------|---------|
| `ZeroKnowledgeHandoff.write_phase()` | Encrypt phase data to .enc file |
| `ZeroKnowledgeHandoff.read_phase()` | Decrypt phase data from file |
| `write_phase_data()` | Convenience wrapper |
| `read_phase_data()` | Convenience wrapper |

**Files created:**
- `.omega/phases/{project}/phase3_planner.enc`
- `.omega/phases/{project}/phase3_planner.sig`

### 2. omega_phase_encryptor.py
Encrypt code, memory, config files.

| Function | Purpose |
|----------|---------|
| `OmegaPhaseEncryptor.encrypt_code()` | Encrypt generated code |
| `OmegaPhaseEncryptor.decrypt_code()` | Decrypt code |
| `OmegaPhaseEncryptor.encrypt_memory()` | Encrypt memory |
| `encrypt_for_transit()` | Encrypt for network transfer |
| `decrypt_from_transit()` | Decrypt from network |

### 3. omega_resume.py
Resume from encrypted files on crash.

| Function | Purpose |
|----------|---------|
| `ZeroKnowledgeResume.find_resume_points()` | Find all checkpoints |
| `ZeroKnowledgeResume.verify_resume_point()` | Verify checksum |
| `check_resume()` | Convenience wrapper |
| `can_resume()` | Check if can resume |

---

## Modified Files

### omega_codex.py
- Step 3 writes encrypted planner_context
- Step 4 reads encrypted planner_context if RAM empty
- Generated code encrypted
- Memory encrypted
- Startup checks for resume points

### omega_gan.py
- Generated code encrypted before return
- File: `.omega/encryptions/{project}/gen_*.code.enc`

### omega_feedback_loop.py
- Loop history encrypted after each iteration
- File: `.omega/encryptions/{project}/memory_iteration_*.mem.enc`

### bridge.py
- Plan encrypted before execution
- File: `.omega/phases/{project}/bridge_plan.enc`

---

## Encryption Details

| Layer | Algorithm | Key |
|-------|-----------|-----|
| Phase Handoff | AES-256-GCM | `.omega/handoff.key` |
| Code Files | AES-256-GCM | `.omega/encryptions/{project}/phase.key` |
| Memory | AES-256-GCM | `.omega/encryptions/{project}/phase.key` |

---

## File Structure

```
.omega/
├── handoff.key              # Master key for phase handoffs
├── phase_handover.log       # Audit log
├── phases/
│   └── {project}/
│       ├── phase3_planner.enc    # Encrypted planner context
│       ├── phase3_planner.sig    # Checksum
│       ├── phase4_omega.enc      # Encrypted omega state
│       └── bridge_plan.enc        # Encrypted bridge plan
└── encryptions/
    └── {project}/
        ├── phase.key              # Encryption key
        ├── index.json             # File inventory
        ├── gen_20260416_123456.code.enc  # Generated code
        └── memory_session_1.mem.enc       # Encrypted memory
```

---

## Resume Flow

```
Startup -> check_resume() -> 
  IF can_resume: Load encrypted files
  ELSE: Start fresh
```

---

## Security Properties

| Property | Protection |
|----------|------------|
| Confidentiality | AES-256-GCM encryption |
| Integrity | SHA-256 checksums |
| Availability | File persists if RAM fails |
| Audit | Handover log tracks all ops |
| Zero-Knowledge | Data encrypted at rest + in motion |

---

## Usage

```python
# Check for resume on startup
from omega_resume import check_resume, can_resume

status = check_resume("myproject")
if status['can_resume']:
    print("Can resume from:", status['resume_points'])

# Use in code
from zero_knowledge_handoff import write_phase_data, read_phase_data

# Write encrypted planner context
write_phase_data("myproject", "3_planner", {"goal": "...", "dag": [...]})

# Read encrypted planner context  
data = read_phase_data("myproject", "3_planner")
```

---

## Checksum Verification

Every encrypted file has a corresponding `.sig` file:

```json
{
  "phase_id": "3_planner",
  "timestamp": "2026-04-16T12:00:00",
  "checksum": "a1b2c3d4e5f6",
  "key_id": "handoff.key"
}
```

On read, checksum is verified. If mismatch -> reject and log.

---

## Future Enhancements

1. **HSM Integration** - Store keys in hardware security module
2. **Multi-party** - Require M-of-N keys for decryption  
3. **Hardware attestation** - Verify platform before decryption
4. **Network encryption** - Encrypt all inter-service communication

---

*Last Updated: 2026-04-16*
