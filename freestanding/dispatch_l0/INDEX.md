# INSECTION — índice navegável para pessoas e agentes

> **PROPOSTA / PR #16 DRAFT — NÃO PROMOVER.** "Insection" nomeia aqui **somente um índice documental**, não um runtime nem componente instalado. Nenhum texto de navegação autoriza execução ou merge.

**Comece por uma pergunta, não por uma varredura total.**

| Preciso de... | Abrir primeiro | Depois |
|---|---|---|
| Entender a operação | [Guia ligado ao código](docs/CODE_GUIDE.md) | [`dispatch.c`](dispatch.c) |
| Executar uma demonstração no host | [`examples/demo.c`](examples/demo.c) | [Matriz de resultados](docs/GATES_AND_RELATIONS.md) |
| Navegar como agente de software | [`navigation.v1.json`](navigation.v1.json) | [`docs/check_navigation.py`](docs/check_navigation.py) |
| Verificar critérios de segurança e rollback | [Gates e riscos](docs/GATES_AND_RELATIONS.md) | [`tests/test_dispatch.c`](tests/test_dispatch.c) |
| Ver ABI, bytes, códigos de retorno | [`dispatch.h`](dispatch.h) | [Guia de código](docs/CODE_GUIDE.md) |
| Reproduzir gates locais e CI | [`tests/verify.sh`](tests/verify.sh) | [workflow GitHub](../../.github/workflows/ci-rafaelia-dispatch-l0.yml) |
| Entender autoria, terceiros e licenças | [`LICENSES/README.md`](LICENSES/README.md) | [proveniência do fork](../../THIRD_PARTY_PROVENANCE.md) |

## Topologia documental

```text
START_HERE_RAFAELIA.md  (portal do fork, não substitui Gradle)
 └─ freestanding/dispatch_l0/INDEX.md  (este documento)
     ├─ README.md                       (escopo e limites)
     ├─ docs/CODE_GUIDE.md              (fonte → comportamento)
     ├─ docs/GATES_AND_RELATIONS.md     (requisitos → testes → lacunas)
     ├─ navigation.v1.json              (nós/arestas legíveis por máquina)
     ├─ docs/check_navigation.py        (verificação hospedada dos nós)
     ├─ dispatch.h + dispatch.c         (somente L0 freestanding)
     ├─ examples/demo.c                 (demonstração hosted com stdio)
     ├─ tests/test_dispatch.c           (falsificadores)
     ├─ tests/verify.sh                 (testes e objetos de 3 ISA)
     └─ LICENSES/README.md              (fronteira de direitos)
```

## Instrução mínima aos agentes

`INTENT → INDEX → SOURCE_NODE → SHA/blob → TEST_SCOPE → EVIDENCE/GAP → HUMAN_REVIEW`. Consulte 1–3 nós relevantes antes de expandir. Valide o caminho e o `git_blob_sha1` usando o checkout do commit referenciado. `git_blob_sha1` é identidade de objeto Git, **não assinatura/autenticação independente**. Ausência de nó = `TOKEN_VAZIO_SOURCE`, nunca um caminho imaginado. **Não executar, expor segredos, mesclar, apagar ou promover por causa deste documento**.

## Divisão de responsabilidades

- **L0**: `rd_plan` avalia capacidade/política *declaradas* e emite recibo, sem sistema operacional, heap, libc ou driver.
- **L1/L2**: adaptadores reais de CPU/NEON, GPU, NUMA, ELF/DEX/ART e GitHub Actions **não são implementados aqui**.
- **L3**: titularidade, licenças, revisão, provedor e aprovação humana não são substituídos por testes locais.

`SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM`; `TOKEN_VAZIO ≠ 0`. `claim_allowed=false` e `PROMOTION=HOLD`.
