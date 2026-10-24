# RAFAELIA — Governança de código, riscos e falsificabilidade (v1)

Scope: rafaelmeloreisnovo/actions, candidate of 2026-10-24.
Source boundary: Gradle Actions upstream remains third-party and is NOT rewritten
or claimed as an original freestanding implementation. These are recommended
engineering controls, not conformity declarations or copyrighted standards text.

## Versioned framework of references

| Reference | Operational application | Evidence / falsifier | Not claimed |
|---|---|---|---|
| ISO/IEC/IEEE 12207:2026 | Separate software life cycle processes, host from freestanding L0, change/operation/recovery | exact SHA, architecture trace and human review before merge | full process compliance |
| ISO 9001:2026 | quality objectives, measured deviations, continual improvement | baseline/negative test/corrective receipt | certification or Sigma capability |
| ISO/IEC 27001:2022 + ISO/IEC 27005:2022 | information security risk inventory, least privilege, treatment | role/permission readback and blocked paths | certified ISMS |
| NIST SP 800-218 v1.1 SSDF | protect software, secure development, respond to vulnerabilities | source-bound CI, threat model, vulnerability triage | NIST approval |
| ISO 8000 family | typed data quality/provenance and completeness | preserve unknowns; distinguish HTTP time from original publication | conformity to an unspecified part |
| ISO/IEC/IEEE 29148:2018 | trace requirement → behavior → verification → change | test ID → source SHA → receipt | full requirement coverage |

Official high-level sources:
- https://www.iso.org/standard/90219.html
- https://committee.iso.org/standard/9001
- https://www.iso.org/standard/80585.html
- https://csrc.nist.gov/pubs/sp/800/218/final
- https://www.iso.org/standard/72089.html

## Typing observable and latent gaps

SOURCE_GAP: actual upstream fork-point and transitive source package unknown.
PROVIDER_GAP: no exact HEAD runner evidence or provider protection write/readback.
LICENSE_GAP: distribution bundles have unresolved upstream component rights.
PHYSICAL_GAP: ARM32/ARM64 same-artifact device execution not observed.
TRUST_GAP: caller-supplied identities, DNS rebinding/private routing, and
HTTP response data are not fully authenticated by this collector.
PROCEDURE_GAP: an Actions-created PR may be forbidden by provider settings.
TOKEN_VAZIO is distinct from a known zero, a pass and a rejected observation.

## Audit and rollback contract

A release or legal originality claim is blocked without independently
verifiable evidence. Human approval is required for a merge. Existing
branches/commits and upstream attribution must never be deleted by
automation. Safe rollback = close Draft PR or selectively revert; do not
rewrite Git history. Host collection is not freestanding; no blind assembly
optimization of its TLS and parsing dependencies is claimed.

Controls evolve with `INTENT → CURRENT_STATE → SOURCE → AUTHORITY →
CHANGE → TEST → RECEIPT → R3`. DMAIC can organize problem solving;
PDCA can supervise recurring operation. Neither establishes a statistical
Six Sigma level without measured process performance.

## Correção de precisão — normativo ≠ certificação (2026-10-24)

As referências acima servem **exclusivamente como fontes de boas práticas, critérios de projeto e testes proporcionais**, e não constituem certificação, acreditação, homologação, aprovação ISO/NIST, implementação integral ou conclusão de conformidade. Sem avaliação de requisitos específicos, a terminologia correta é "boas práticas inspiradas em"; para alegações mais fortes, seguir o gate de evidências e escopo de [NORMATIVE_CLAIM_POLICY_V1.md](NORMATIVE_CLAIM_POLICY_V1.md). No estado registrado, `certification_claim_allowed=false`, `full_conformity_claim_allowed=false` e prova de certificação = `TOKEN_VAZIO_NOT_OBSERVED`. A ISO não emite certificados e o NIST SSDF é orientação de desenvolvimento seguro, não certificação. Esta correção prevalece sobre qualquer ambiguidade de linguagem precedente sem apagar os registros.
