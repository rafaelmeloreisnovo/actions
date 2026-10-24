# Evidence Registry — AI Releases & Public Claims

Collector documental para lançamentos, patches, revisões, previews, disponibilidade, deprecações e correções públicas de OpenAI, Anthropic/Claude, Google/Gemini e GitHub Copilot, com testemunhas secundárias de Bing/Yahoo.

## Invariantes

`SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`

- Bash + GitHub Actions; sem Python no coletor.
- Preserva URL original, URL efetiva, timestamp UTC de coleta, headers HTTP e corpo bruto.
- Calcula SHA-256 de cada corpo e do conjunto da execução.
- `response_date` é horário da resposta HTTP, não data de publicação.
- `last_modified` e `etag` são metadados de transporte/cache, não prova isolada de lançamento.
- A data histórica declarada pela fonte fica em tabela separada; quando ausente = `TOKEN_VAZIO`.
- Contradições e correções editoriais são preservadas, nunca apagadas.
- `claim_allowed=false` por padrão: coleta documental não é conclusão jurídica.

## Estrutura

- `sources.tsv`: fontes públicas primárias, comunidades oficiais e testemunhas secundárias.
- `collect.sh`: coleta HTTP, headers, corpos, SHA-256 e ledger JSONL.
- `seed_events.tsv`: cronologia inicial verificada manualmente em fontes primárias.
- `.github/workflows/evidence-registry.yml`: execução manual + diária, artifact e commit do ledger/manifests.

## Execução local

```bash
bash evidence-registry/collect.sh evidence-registry/sources.tsv evidence-artifact
```

Os corpos brutos ficam no artifact do GitHub Actions. O Git registra ledger e manifests para manter trilha documental sem transformar o repositório em depósito de centenas de GB.

## Zero-trust collection successor (2026-10-24; proposed)

Source hosts are explicitly allowlisted in `allowed_hosts.v1.txt`. Only HTTPS
URLs are accepted; implicit redirects are **not followed**. A 301/302 or other
non-200 response is retained as a typed observation, **not** a fetched source
claim. Bodies are bounded at 10 MiB. URL policy is independently falsified
without external network calls in `tests/test_sources.py`.

The workflow separates a network-facing read-only `collect` job from an
optional main-only `publish-ledger` job with `contents: write`. This enforces
least privilege on the HTTP collector; publish checks the same-run artifact's
SHA256SUMS and exact source SHA before append-only commit. A hash verifies
artifact integrity relative to the uploader; it is not a vendor signature or
independent attestation. Provider protections, independent review, and actual
Actions execution still require their own receipts.

These are HOST/L1 controls. Curl, TLS, Git, jq and GitHub Actions are not
freestanding components, and this workflow is not training any AI model.

## 2026-10-24 — Custody / human-merge successor (draft, non-promoting)

The collector may preserve raw transport responses, including non-200 status
and unsuccessful partial downloads. Only `curl exit=0 && HTTP 200` is permitted
to populate the **source-body** SHA-256 field. Retained error bodies are
diagnostic artefacts, never authenticated primary-source evidence.

The scheduled publisher no longer performs `git push` on `main`. It commits
new ledger records to a unique `evidence/review-<run_key>` branch and asks
GitHub to open a **Draft PR** for explicit human review. A provider policy may
disallow PR creation by GitHub Actions; that is a typed `PROVIDER_BLOCKED`
condition, not authorization to bypass protections. Every branch is retained
for rollback/reconstruction, including a branch whose PR could not be opened.
No automatic merge, branch cleanup, license promotion, or historical deletion.

The policy is tested offline in
`evidence-registry/tests/test_custody_gate.py`; an Actions CI run on an exact
commit is still required before deployment. The publisher and HTTP/TLS client
are HOST infrastructure, not freestanding/bare-metal runtime code.
