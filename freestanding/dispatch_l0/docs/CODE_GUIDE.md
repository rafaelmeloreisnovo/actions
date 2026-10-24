# Explicação do código, do byte ao recibo

**Autoridade técnica:** [`dispatch.h`](../dispatch.h) + [`dispatch.c`](../dispatch.c), sem inferir um driver. `rd_plan` é a única função pública do núcleo freestanding L0.

## 1. Contrato de memória e ABI

O chamador aloca `rd_request` com **10 palavras de 32 bits** (40 bytes esperados) e `rd_receipt` com **6 palavras de 32 bits** (24 bytes esperados). `_Static_assert(sizeof(rd_u32)==4)` verifica apenas a largura de palavra; alinhamento, offsets e ABI completa exigem teste por alvo.

| Campo | O que o código exige |
|---|---|
| `tag` | `RD_TAG=0x52444c30` |
| `sequence` / `previous_sequence` | incremento de 1 sem overflow/replay |
| `present_mask` | exatamente `RD_ALL_PRESENT=31` |
| `observed_caps` / `permitted_caps` | máscaras declaradas: escalar=1, NEON=2, SIMD=4, GPU=8 |
| `preferred` | 0 automático ou um único bit válido |
| `watchdog_a` / `watchdog_b` / `watchdog_limit` | sinais positivos e dentro do limite |

**Não atribua verdade a uma declaração.** O bit `RD_PRESENT_SOURCE` afirma *presença declarada*, **não verifica SHA, assinatura, identidade, licença ou frescor**. Nenhum campo atesta se o processador realmente suporta NEON. `TOKEN_VAZIO` é ausência de campo, não um zero avaliado como evidência.

## 2. Ordem exata da implementação

```text
receipt nulo? → retorna antes de ler entrada
snapshot das 10 palavras da entrada → inicialização DENY do recibo
request nulo? → UNKNOWN
tag/máscaras/preferred inválidos? → BAD_INPUT (1)
faltou um campo? → UNKNOWN (0)
sequência repetida/overflow? → STALE (2)
watchdog_a ou watchdog_b 0/acima do limite? → WATCHDOG (3)
preferência GPU? → GPU_BOUNDARY (5)
eligible = (observed_caps & permitted_caps) & RD_CPU_CAPS
preferência CPU elegível → seleciona preferência
sem preferência → NEON > SIMD > escalar
preferência ausente → escalar apenas se elegível
não existe rota? → NO_ROUTE (4)
rota escolhida? → PLAN_ONLY (6)
```

Independentemente do caminho, `hardware_activated=0` e `merge_authorized=0`. `rollback_required` é **sinal**, não uma reversão executada. As verificações usam ramificações `if` por segurança; removê-las apenas por estética não preserva necessariamente o comportamento.

## 3. Exemplo fonte-fiel

```c
#include "dispatch.h"
rd_request req = {RD_TAG, 9u, 8u, RD_ALL_PRESENT,
  RD_SCALAR|RD_NEON, RD_SCALAR|RD_NEON, RD_NEON, 4u, 3u, 4u};
rd_receipt out;
rd_plan(&req, &out);
/* status=6; route=2; fallback=0; rollback_required=0;
 * hardware_activated=0; merge_authorized=0. */
```

## 4. Demonstração executável **somente no host**

Na raiz do checkout, **sem instalar no Android**:

```sh
cc -std=c11 -O2 -Wall -Wextra -Werror \
  freestanding/dispatch_l0/dispatch.c \
  freestanding/dispatch_l0/examples/demo.c -o /tmp/dispatch-l0-demo
/tmp/dispatch-l0-demo
python3 freestanding/dispatch_l0/docs/check_navigation.py
sh freestanding/dispatch_l0/tests/verify.sh
```

O exemplo usa `stdio.h` **apenas** na camada hospedada de demonstração, nunca no núcleo C. Há quatro cenários: NEON permitido, fallback escalar, GPU negada, sinal watchdog ausente. Confira [matriz e aceitação](GATES_AND_RELATIONS.md). Os testes de host e objetos cross-target não provam execução ARM, GitHub CI, watchdog real, GPU, NUMA, DEX ou ART.
