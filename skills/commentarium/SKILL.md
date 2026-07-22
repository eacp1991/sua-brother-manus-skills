---
name: commentarium
version: 0.5
summary: Social listening de comentários públicos → inteligência cultural, conteúdo e leitura de mercado. Manus-native, budget-safe, com coleta via conector Apify e anti-fabricação absoluta.
description: Recebe link de post público, coleta comentários via conector Apify (actor instagram-comment-scraper) ou script determinístico, peneira via scripts, e usa o LLM só na camada de insight (EVIDÊNCIA/INFERÊNCIA/HIPÓTESE). Modos SERIO_SOCIALDEV (padrão), CREATOR_INTELLIGENCE e QUINTA_SERIE_LAB. Caso #1 Renatinha/Sua Brother (benchmarks: 3.724 e 868 comentários).
---

# COMMENTARIUM v0.5 — Manus-native, budget-safe, anti-fabricação

> O post é o palco. O comentário é o povo escrevendo o roteiro — sem saber.

**Changelog v0.5 (2026-07-22):** coleta migra pro **conector Apify do Manus** (agora conectado no projeto) com fallback no script; regra ANTI-FABRICAÇÃO dura (incidente real de 21/07: agente sem ferramenta inventou dataset inteiro com "sucesso"); fato provado: **conector Instagram NÃO extrai comentários** (só métricas agregadas) — comentário é SEMPRE Apify; benchmark de cobertura 868/872 (99,5%); budget atualizado pra conta Pro.

---

## ⛔ ANTI-FABRICAÇÃO (regra nova, INEGOCIÁVEL)

Todo comentário e todo número vem de coleta REAL. Se o conector/actor falhar, **PARE e reporte o erro exato** — diagnóstico honesto É entrega válida. É PROIBIDO inventar, estimar, simular ou "preencher com estrutura esperada". Tells de dado fabricado (auto-cheque): IDs sequenciais, urls example.com, números redondos, legendas genéricas fora da voz do perfil. **Sempre reporte a taxa de cobertura**: N extraído vs contagem oficial do post (meta ≥95%; benchmark real: 868/872).

## 💰 BUDGET GUARD (atualizado)

Conta Pro (Renatinha: 8.000 cr/mês + refresh diário): o teto relaxou, a disciplina NÃO. Princípio de sempre: **dado bruto é barato, interpretação é cara** — scripts peneiram, LLM julga só a shortlist.
1. **NUNCA Deep Research / Agent Mode autônomo pra coletar** (500-900cr num job).
2. Coleta = conector Apify ou script determinístico. Análise = camada barata (`agent_profile: manus-1.6-lite` quando disparado via API).
3. Job em massa (>3.000 comentários ou N posts): estimar créditos e confirmar antes.

## 📥 COLETA (ordem de preferência)

1. **Conector Apify do Manus** (habilitado no projeto): actor **`apify/instagram-comment-scraper`** (cobra por comentário gravado — centavos). Input: `{"directUrls": ["<permalink>"], "resultsLimit": <3× a contagem esperada>, "includeNestedComments": true}`. Atenção: replies aninhadas podem não vir (benchmark 21/07: 102 replies ficaram fora) — reportar.
2. **Fallback script:** `python3 scripts/fetch_apify_comments.py --post-url "$POST_URL" --actor-id "$APIFY_ACTOR_ID" --limit 1000 --out raw_comments.json` (token do cliente).
3. Se o usuário já tem JSON/CSV exportado, pule a coleta.

⚠️ **O conector Instagram do Manus NÃO serve pra isso** (provado 2026-07-21: get_post_insights devolve só a CONTAGEM de comentários, nunca o texto). Use o Instagram só pra âncora de sanidade: a contagem oficial que define a meta de cobertura.
⚠️ Actors de IG quebram (DOM muda). Run síncrono estourou (408) → rodar async e exportar o dataset; não insistir em re-run.

## 🔬 PIPELINE (barato → caro)

1. Ler `references/budget_guard.md` + `references/travas_eticas.md`.
2. Coleta (acima) → `raw_comments.json`.
3. Normalizar: `python3 scripts/normalize_comments.py raw_comments.json normalized_comments.json`.
4. Peneira: `python3 scripts/classify_comments.py normalized_comments.json shortlist.json --mode SERIO_SOCIALDEV --top 120` (a peneira não é veredito — o LLM julga a shortlist).
5. Análise LLM em 3 camadas: **EVIDÊNCIA** (literal) / **INFERÊNCIA** (interpretação provável) / **HIPÓTESE** (aposta validável). Benchmarks metodológicos: `references/case_renatinha_3724.md` e `references/case_boraviver_868.md`.
6. Output: `templates/relatorio_template.md` (+ `plano_creator_7dias_template.md` se o objetivo for conteúdo).

## 🎭 MODOS (serious-first)

1. **`SERIO_SOCIALDEV`** (padrão) — dores, desejos, objeções, medos, linguagem nativa, oportunidades. Ref: `references/modo_serio_socialdev.md`.
2. **`CREATOR_INTELLIGENCE`** — pautas, respostas em vídeo, quadros, plano 7 dias. Ref: `references/modo_creator_intelligence.md`.
3. **`QUINTA_SERIE_LAB`** — braço viral/humor, só quando pedido. Ref: `references/modo_quinta_serie_lab.md`.

## 🧭 MÉTODO (dado → estratégia)

```
DADO BRUTO → PADRÃO CULTURAL → TENSÃO CENTRAL → LINGUAGEM NATIVA → OPORTUNIDADE → FORMATO
```
Nunca entregue só "sentimento positivo/negativo" — isso é raso. A boa análise **revela a frase que o público ainda não conseguiu formular sozinho**. Bom: "o público está juridificando o afeto: troca linguagem de desejo por linguagem de risco." Ruim: "sentimento majoritariamente neutro."

## 🔒 TRAVAS ÉTICAS (INEGOCIÁVEIS — `references/travas_eticas.md`)

Ranking é de **comentários, não de pessoas**. Anonimizar por padrão (`Comentarista 01`); @ real só em ANEXO INTERNO — NÃO PUBLICAR. Não inferir atributos sensíveis. Não amplificar agressão. Comentário = artefato cultural. LGPD. Dor aguda/crise detectada no material → sinalizar pra resposta HUMANA (nunca automação, nunca funil).

## 📤 OUTPUT MÍNIMO

```
# COMMENTARIUM REPORT
0. Cobertura da coleta (N/esperado + método) · 1. Resumo brutal · 2. Números · 3. Leitura cultural
4. Clusters · 5. Top comentários anonimizados · 6. Linguagem nativa · 7. Ouro estratégico
8. Conteúdos prontos · 9. Recomendação · 10. Hipóteses a validar · 11. Anexo interno (só se pedido)
```
