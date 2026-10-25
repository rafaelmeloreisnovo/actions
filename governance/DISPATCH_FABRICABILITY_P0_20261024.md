# P0 — Fabricabilidade, revisão e prova de origem: RAFAELIA Actions / Dispatch L0

Data: 2026-10-24 (Brasil). Escopo: `rafaelmeloreisnovo/actions`, fork público de `gradle/actions`. Status: **SOURCE_HOTFIX_CANDIDATE / LOCAL_PASS_SCOPED / NO_PROMOTION**.

## Baseline, execução e contraditório
- Analisado `main@47e0ad95703009bfaaa902f605fd3bf69aae4b48`, `protected=false`. Histórico: PR#16 com **[NÃO PROMOVER]** e zero avaliações/reviews observadas mesclada 2026-10-24T22:40:09Z; PR#17 e #18 igualmente mescladas, sem atribuir motivação ou identidade. GitHub REST `issues` retornou **HTTP 410, Issues desativadas** quando tentado registrar P0.
- `GET check-runs` no HEAD da #16 e em `main@47e0...` retornou zero; listagem de workflows retornou runs históricos até 2026-10-08. **Não concluir causa**, nem confundir ausência de run com resultado positivo.
- O ZIP anterior `RAFAELIA_ACTIONS_DISPATCH_L0_PR16_20261024.zip` foi extraído localmente; SHA256 `7e11920cad23f4aeff8626e3124ea8ea426dccaff35a32343852b2882ef08434`. Blobs de `dispatch.c` e `dispatch.h` igualam os SHAs do GitHub `8f65489dfed597cd437a43cde14fb755eeaabef8` e `dd355383185e4f9c9dda22de089cdcaa28eedea6`.
- Reexecutado `sh freestanding/dispatch_l0/tests/verify.sh`: testes hosted `-O0/-O2` com Clang/ASan/UBSan, mais 3 objetos x86-64 / ARMv7 / AArch64; símbolos indefinidos vazios e 2 compiladores byte-idênticos por alvo: **PASS_SCOPED**. Clang+LLD vinculou **3 ELF estáticos ET_EXEC** (nenhum NEEDED/INTERP/undefined; sem segmentos LOAD W+X); `rd_plan` usado como entry **apenas para testar link**: NÃO é ponto de boot seguro, não há inicialização de stack/ABI ou execução ARM.
- Script de origem real `rafcode/verify-source/verify.sh` blob `f2145923473ae02a0fb4f3803c7ffb475dd3a312` reproduzido localmente com o mesmo `git hash-object`. O gate antigo **PASS** em checkout com `rogue.c/rogue.h` não rastreados e **BLOCK** em arquivo rastreado modificado. É uma lacuna de abrangência, não comprova execução efetiva do rogue pelo pipeline.
- Hotfix único: negar arquivos **não rastreados e não ignorados** antes de emitir `SOURCE_GATE=PASS_SCOPED`; ajustar harness `GITHUB_OUTPUT` para `.git/gate-output` para evitar falso bloqueio do próprio teste; acrescentar dois casos negativos (arquivos normais e com newline no nome). Local após o ajuste: **10/10 testes PASS**. Permanece não demonstrado GitHub Actions exato do HEAD do candidato.

## Matriz cirúrgica de modos de falha (P0/P1/P2)
| Risco | Falsificador e impacto | Correção mínima / limite | Estado |
|---|---|---|---|
| P0-R01 provider merge | PR#16 [NÃO PROMOVER] mesclada sem revisão/checks observados; main sem proteção | Habilitar rule + required review/checks; provar recusa em PR teste | `TOKEN_VAZIO_PROVIDER_ENFORCEMENT` |
| P0-R02 no Actions run | check_runs=0 em HEAD real | Administrador examinar Settings/Actions/uso/plano/políticas e obter job, steps e logs | `TOKEN_VAZIO_RUNNER_CAUSE` |
| P0-R03 untracked source | `rogue.c/h` com gate anterior PASS | Novo fail-closed + 2 negativos e teste limpo | `LOCAL_PASS_SCOPED`; provider NOT_RUN |
| P1-R04 ignored inputs | .gitignore e arquivos gerados podem fugir da checagem | Controlar entradas por allowlist/ambiente, rastrear compilador e diretórios | `TOKEN_VAZIO_IGNORED_INPUTS` |
| P1-R05 POST-GATE TOCTOU | arquivos modificáveis após checar a árvore | Bind hash do artefato, snapshot/recheck imediato à compilação | `TOKEN_VAZIO_BUILD_INPUT_BINDING` |
| P1-R06 compiler, PATH, LLVM | versão/fornecimento da toolchain não autenticados | Receipts de toolchain hash e compilação reproduzível independente | `TOKEN_VAZIO_TOOLCHAIN_AUTHORITY` |
| P1-R07 signature and third-party | SHA Git/checkout não certifica origem jurídica ou pacote Gradle dist | Auditoria per-file/licença e assinatura/reviewer | `TOKEN_VAZIO_RIGHTS` |
| P1-R08 caller-supplied caps/rights | `RD_PRESENT_SOURCE`, `observed_caps` são afirmações | HWCAP/ISA e principals confiáveis via adaptador separado | `TOKEN_VAZIO_CAPABILITY_ATTESTATION` |
| P1-R09 watchdog | dois inteiros não são relógios independentes | Fault injection/timeout real por supervisor autorizado | `TOKEN_VAZIO_DOUBLE_WATCHDOG` |
| P1-R10 fallback/rollback | seleção e flag não executam failover ou restauração | Integrador físico com teste de falha, idempotência e rollback | `TOKEN_VAZIO_EXECUTION` |
| P1-R11 cross-platform | ELF ET_EXEC linkável com entry argument-taking não prova boot; objetos ARM não rodados | ABI/stack/loader, dispositivo real, DEX/ART produtor separado | `TOKEN_VAZIO_PHYSICAL_RUN` |
| P2-R12 GPU/NEON/NUMA | bitmask não liga ISA, driver, afinidade ou memória NUMA | Adapter/provider atestado, benchmarks funcionais e equivalência | `TOKEN_VAZIO_HETEROGENEOUS` |
| P2-R13 observability | teste host sob ASan não é zero-overhead target | medição real de custo, tempo, ciclos, watchdog/race e regressões | `TOKEN_VAZIO_PERF` |
| P2-R14 privacy and minors | ambiente host/coleta pode manipular dados sensíveis fora do L0 | minimização, Zero Trust, salvaguardas de crianças, logs sem payloads | `TOKEN_VAZIO_DATA_USE_CONTEXT` |

Normas NIST/ISO citadas apenas como **referências de boas práticas**, jamais certificação, auditoria independente, patente ou conformidade integral. Informações de cultura local e respeito ao livre arbítrio não devem ser substituídas por inferência de agente.

## R3 e autoridade
`SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`. `TOKEN_VAZIO != 0`; `PASS_SCOPED != GLOBAL_PASS`.
- **F_ok**: defeito identificado e falsificado, correção de três linhas + ajuste do teste, 10/10 testes locais, regressões rastreadas, 3 ELF vinculados estaticamente sem requisitos dinâmicos.
- **F_gap**: regras obrigatórias no GitHub, runner atual, toolchain/SBOM/licenças, boot real, Android, hardware, revisões humanas, inputs ignorados e posteriores ao gate.
- **F_next**: revisão humana e aprovação somente com CI no HEAD exato e promoção bloqueada no servidor; ampliar o escopo **em PR separada** se for autorizado.
- **Rollback**: `git revert` do commit candidato, ou simplesmente não adotar esta branch; preservar predecessor e commits, nunca apagar ou forçar `main`.

**PROMOTION=HOLD / claim_allowed=false**. A branch HOLD é proposta sem abertura de PR para evitar nova integração sem controle.
