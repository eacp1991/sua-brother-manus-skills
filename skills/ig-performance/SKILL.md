---
name: ig-performance
version: 1.0
summary: Relatórios de performance do Instagram via conector nativo — snapshot verificado, ranking, outliers e relatório semanal, com métricas privilegiadas (reach/views/saves/shares) e custo disciplinado.
description: Usa exclusivamente o conector Instagram do Manus (get_account_info, get_post_list, get_post_insights) para produzir relatórios de performance da conta conectada. Anti-fabricação absoluta, âncoras de sanidade, regra de custo por chamada de insights. Não publica nada; não coleta comentários (isso é a skill commentarium via Apify).
---

# IG-PERFORMANCE v1.0 — métricas reais, disciplina de custo

Você produz inteligência de performance da conta Instagram conectada (caso #1: @renatinhadiniz / Sua Brother). SOMENTE LEITURA — publicação exige ordem explícita e não é papel desta skill.

## ⛔ Regras duras
1. **ANTI-FABRICAÇÃO:** só números que as ferramentas retornarem. Falhou → pare e reporte o erro. Âncora de sanidade da conta: ~600 mil seguidores, ~4.800 posts (jul/2026) — divergência grosseira = investigar antes de reportar.
2. **Fronteira de ferramenta (provada 2026-07-21):** o conector entrega conta, lista de posts e métricas agregadas por post. Ele NÃO entrega comentários individuais (texto), demografia de audiência nem stories analytics. Comentários = skill `commentarium` (Apify).
3. **Custo:** ~6-7 créditos por post COM insights. `get_post_list` pagina em 5-20 posts/página (cursor). Antes de rodar mais de 20 posts com insights, estime o custo e confirme.

## 🛠️ Ferramentas (detalhe completo: `references/connector_capabilities.md`)
- `get_account_info` — snapshot do perfil (9 campos: id, username, bio, followers, follows, media_count, website...).
- `get_post_list` — histórico paginado (14 campos/post: id, tipo, data, caption, permalink, likes, comments...).
- `get_post_insights` — 7 métricas lifetime por post: likes, comments, shares, **saved, reach, views**, total_interactions.

## 🔁 Workflows

### 1. Snapshot verificado (barato, ~5cr)
`get_account_info` + 1 página de `get_post_list`. Entrega: números da conta + últimos posts com métricas básicas, com data/hora da coleta.

### 2. Relatório semanal (padrão, ~60-150cr conforme volume)
1. `get_post_list` até cobrir os posts da semana.
2. `get_post_insights` em cada post novo.
3. Compare com a mediana dos últimos 20 posts (alcance, views, engajamento = interações/alcance).
4. Entregue: tabela por post + destaques (melhor/pior + por quê aparente: formato, tema, gancho) + **outliers** (>3× a mediana de alcance → recomendar commentarium completo no outlier).
5. Formato: markdown + JSON anexo `{account, posts[], pulled_at, source: "instagram_connector"}`.

### 3. Ranking top N (mensal, ~130cr p/ 20 posts)
Top N por alcance/views no período + padrões (tipo de conteúdo, tema, dia/hora, duração) + 3 recomendações acionáveis ancoradas nos padrões.

### 4. Alerta de outlier (agendável)
Se algum post das últimas 48h passar 3× a mediana de alcance dos últimos 20 → reportar imediatamente com métricas completas + recomendar dobrar a aposta (cortes, série, commentarium). Agendamento: `manus-config schedule` (cron) — o conector não tem agendamento nativo.

## 📤 Saída padrão
Sempre: data/hora da coleta (`pulled_at`), fonte (`instagram_connector`), custo estimado da rodada, e — em relatórios comparativos — a mediana usada como régua. Insights de negócio no padrão da marca: direto, acionável, sem dashboard-speak ("views subiu" não é insight; "reels de tese com gancho normalizado dobram o alcance dos de lifestyle" é).
