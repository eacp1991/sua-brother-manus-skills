# Benchmark Metodológico #2 — Caso Bora Viver / 868 comentários (2026-07-21)

Referência de método e de COBERTURA. Complementa o `case_renatinha_3724.md`.

## Contexto
Reel do evento "Bora Viver" (@renatinhadiniz, 11/07/2026): 603.006 alcance · 766.694 views · 52.154 likes · 22.504 shares · 872 comentários (contagem oficial via conector Instagram).
Coleta: Apify `apify/instagram-comment-scraper` → **868/872 = 99,5% de cobertura** (3-4 faltantes = deletados/restritos; 102 replies aninhadas ficaram fora — limitação do actor na run). Verificação anti-fabricação: post-âncora com baseline de 7 dias antes cresceu monotonicamente em 6 métricas ✓.

## Achados-base
- **Anatomia:** ~55% aplauso de tese (👏 ×1.299 — comentário-aplauso = conteúdo de TESE) · ~15% debate/threads · ~12% relatos e dores · ~5% fé · ~4% objeções (nenhuma passou de 1 like) · ~2% pedidos diretos.
- **UGC de ouro ("Teoria do Feijão"):** comentarista descartou pretendente por não gostar de feijão → debate mais quente do post (160 likes, 48 replies, 34 menções). Síntese dela: "não é só sobre feijão — a longo prazo tudo incomoda". Lição: a metáfora abstrata do post (defeitos toleráveis) foi MATERIALIZADA pela audiência num caso concreto — nomear e colher.
- **Desejo nº 1** (top comment, 176 likes): relacionamento maduro como aspiração RARA ("sonho achar um relacionamento assim").
- **Linguagem devolvida:** "parceiro de jornada de evolução" quotada 3× · "autoconhecimento não é gostosinho" · "é sobre isso" / "cirúrgico" / "aula".
- **Tensão cultural detectada:** atrito espiritual DENTRO da base (Eclesiastes com 32 likes E "meteu um Kardec" no mesmo post) → linguagem de evolução/jornada une, doutrina divide.
- **Prova de posicionamento:** homens vulneráveis comentando abertamente (términos, solidão) — o caminho do meio entrega o espaço que promete.

## Lições metodológicas novas (vs. caso 3.724)
1. **Cobertura é métrica de primeira classe:** sempre reportar N/esperado e o que ficou fora (replies).
2. **Verificação por âncora:** cruzar contra baseline conhecido pega dado fabricado que schema perfeito esconde.
3. **Threads > comentários isolados:** o valor do feijão está na CONVERSA (48 replies), não no comentário original.
4. **Comentário-aplauso em massa (👏) = assinatura de conteúdo de TESE** — o post que gera fórum vale mais que o que gera elogio.
