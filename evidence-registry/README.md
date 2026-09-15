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
