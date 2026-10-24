# RAFAELIA — Política de alegações sobre normas e certificações / v1

**Situação de referência:** 2026-10-24. Esta é uma política de comunicação e evidências, **não** um certificado, auditoria, declaração de conformidade ou opinião legal.

## Regra de fronteira (obrigatória)

A RAFAELIA pode **consultar e adotar boas práticas inspiradas em normas e referências técnicas**, com contexto, versão e evidência local de cada controle realmente aplicado. A simples referência a ISO, IEC, IEEE, NIST ou a um framework não significa adoção integral de requisitos, aprovação, auditoria, homologação, certificação, acreditação ou conformidade demonstrada.

Uma declaração como "certificado ISO 9001", "certificado ISO/IEC 27001", "homologado pelo NIST" ou "100% conforme à ISO" deve ser **bloqueada** até existir evidência externa adequada ao escopo e ao tipo de alegação. A ISO publica normas, mas não emite certificados; a certificação, quando cabível, é realizada por organismos independentes. As recomendações NIST SSDF não constituem por si um esquema de certificação NIST.

**Não confundir:** 
- `REFERENCE_ONLY`: norma apenas consultada, sem implementação demonstrada;
- `CONTROL_DESIGNED`: processo ou controle proposto, ainda não testado;
- `IMPLEMENTED_UNTESTED`: fonte implantada sem execução vinculada;
- `TESTED_SCOPED`: teste com HEAD e recibo, somente no escopo medido;
- `CONFORMITY_ASSESSED_SCOPED`: avaliação documentada contra requisitos específicos, com limites e avaliador identificados;
- `CERTIFICATION_VERIFIED_SCOPED`: certificado válido verificado, exclusivamente para titular, norma/edição, local e escopo do certificado.

**Não há promoção automática entre estados.** `TOKEN_VAZIO_NOT_OBSERVED` não significa `0`, `FAIL` ou "não existe certificação"; significa apenas que a prova não foi apresentada/verificada nesta auditoria. `claim_allowed=false` para alegações de certificação e conformidade plena enquanto faltarem provas.

## Linguagem aprovada e reprovada

| Estado e prova | Exemplo aceitável | Exemplo indevido |
| --- | --- | --- |
| Referência documental | "Consultamos recomendações do NIST SP 800-218 para estruturar verificações." | "Aprovado pelo NIST." |
| Controle implementado e testado | "O controle de checkout por SHA foi testado no commit X no ambiente Y." | "Todo o sistema é conforme ISO/IEC 27001." |
| Programa de qualidade em evolução | "Aplicamos práticas de gestão de riscos e melhoria contínua inspiradas na ISO 9001." | "Possuímos ISO 9001." |
| Sem certidão comprovada | "Certificação externa: evidência ainda não verificada." | "Somos certificados." |

O verbo **"seguimos"** deve ser limitado ao controle específico efetivamente comprovado; prefira "adotamos boas práticas inspiradas em..." quando não houver análise de todos os requisitos.

## Gate mínimo para declarar certificação

Somente após evidência independente, adequada à norma e ao escopo: `holder`, identificador/número do certificado, edição da norma, organismo certificador, escopo e unidades cobertas, validade, estado vigente, fonte autenticável e verificação de autenticidade. Se a alegação incluir acreditação, comprovar também a acreditação e seu escopo. Registros em páginas internas, aprovação de PR, testes C/ARM ou checks do CI não são certificados.

Para avaliação de conformidade **sem certificação**, identificar os requisitos avaliados, evidências, competências do avaliador, exclusões, período e limites. Não usar "conforme integralmente" se o escopo é parcial.

## Rastreabilidade

`CLAIM → STANDARD_REFERENCE → APPLICABLE_CONTROL → SOURCE_REF → HEAD_SHA → TEST_RECEIPT → REVIEW → SCOPE → ALLOWED_WORDING`.

A política acima é executada por revisão humana; `normative_claim_state.v1.json` descreve seu estado automatizável e o teste hospedado apenas rejeita promoções documentais indevidas. **Ele não detecta certificações reais nem emite certificados**. Código e upstream herdado continuam com autoria/licenças separadas. Retroalimentação: corrigir alegação gera registro sucessor, não apagar predecessores.

## Fontes oficiais para a distinção

- ISO Certification: https://www.iso.org/certification.html
- ISO Management System Standards — Certification: https://www.iso.org/management-system-standards.html
- ISO 9001 (uso sem certificação): https://committee.iso.org/quality-management/iso-9001-2026
- NIST SP 800-218: https://csrc.nist.gov/pubs/sp/800/218/final
