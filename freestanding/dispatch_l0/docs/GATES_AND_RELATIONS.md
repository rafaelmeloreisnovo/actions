# Relações, falsificadores, recibos e critérios R3

## Onde o módulo se encaixa

```text
L3: revisão humana, direitos, segurança e proteção do provedor (NÃO IMPLEMENTADO NO L0)
L2: GitHub Actions, Android, ART/DEX, drivers/ELF e consumidores (HOSTS SEPARADOS)
L1: fonte confiável para capacidades, watchdog e identidade (ADAPTADOR AUSENTE)
L0: dispatch.h + dispatch.c → rd_plan(request) → receipt (IMPLEMENTADO)
```

O L0 **não chama** `kernel4`, `omega_os`, `provenance_core`, `apk_bridge`, `rafcode/l0`, Gradle nem GitHub. Relações são de arquitetura, não integração executável.

## Fonte → requisito → falsificador

| ID | Invariante do código | Teste ou prova | Estado |
|---|---|---|---|
| R01 | tag e flags inválidas negadas | `tests/test_dispatch.c`: máscaras/tag/preferência | PASS_SCOPED local |
| R02 | campo desconhecido ≠ zero válido | sem `RD_PRESENT_WATCHDOG_B` → UNKNOWN | PASS_SCOPED local |
| R03 | replay e overflow barrados | `RD_STALE` | PASS_SCOPED local |
| R04 | 2 entradas watchdog dentro do limite | zero/limite inválido → `RD_WATCHDOG` | Só entradas, não timers reais |
| R05 | GPU fora das rotas CPU | `RD_CPU_CAPS=7` e `GPU_BOUNDARY` | PASS_SCOPED local |
| R06 | fallback escalar limitado à política | preferência NEON sem permissão → SCALAR | PASS_SCOPED local |
| R07 | nenhum merge ou acionamento físico | saída `activated=merge=0` | PASS_SCOPED local |
| R08 | ausência de símbolos externos | `nm -u` em 3 objetos cross-ISA | PASS_SCOPED local |
| R09 | navegação apontando para fontes reais | `docs/check_navigation.py` | Gate HOST apenas |
| R10 | CI exata no HEAD da PR + proteção `main` | provider run/jobs/logs e teste de bloqueio | NOT_OBSERVED / P0 |
| R11 | ABI, NEON, GPU, NUMA, Android/ART reais | mesmo binário e recibo do dispositivo | NOT_RUN |
| R12 | titularidade, licenças e revisão | `LICENSES/README.md` + decisão humana | TOKEN_VAZIO |

## Demonstração de comportamento — não execução física

| Cenário | Mudança na entrada | status | route | fallback | rollback |
|---|---|---:|---:|---:|---:|
| N1 | NEON preferido, observado, permitido | 6 | 2 | 0 | 0 |
| N2 | NEON preferido, somente escalar permitido | 6 | 1 | 1 | 0 |
| N3 | GPU preferida | 5 | 0 | 0 | 1 |
| N4 | bit de presença watchdog B ausente | 0 | 0 | 0 | 1 |

Sempre `hardware_activated=0` e `merge_authorized=0`. `examples/demo.c` testa esses quatro resultados.

## Modos de falha e aceitação

- **Capacidade falseada:** o host precisa verificar ISA/ABI; bit fornecido por chamador não é prova.
- **Watchdogs fraudulentos:** dois valores positivos não demonstram dois relógios independentes nem supervisão ativa.
- **Rollback fictício:** `rollback_required` não modifica memória de produção nem o dispositivo.
- **GPU/NUMA:** driver, segurança, escalonamento, comparabilidade bit a bit, medições de tempo/energia são trabalhos específicos futuros.
- **Segurança e privacidade:** o índice JSON é leitura, não um gateway de acesso; não armazena segredos ou dados pessoais.
- **Autoria:** repositório é fork de Gradle; licença herdada permanece, outorga do delta autoral requer revisão humana.

**Critério real de promoção:** prova de direitos e licenças; revisão humana independente; CI com HEAD, passos, logs e recibos; branch protection obrigatória, teste de rejeição de merge inválido; hardware/ART apenas com prova física separada. **Nenhum resultado local herda essas provas.**

**R3:** F_ok = fonte e teste local; F_gap = CI remota, proteção, licença, dispositivos; F_next = resolver provider P0 e revisão, depois adaptadores separados. Reversão: fechar PR DRAFT sem merge **e sem apagar branch/commits**.
