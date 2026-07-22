# Apify-as-Gateway — padrão Goldbach (referência de coleta)

Fonte: KB Goldbach — Pesquisa Apify Universal Scraper Pattern (2026-04-29, Manus+Firecrawl).

## O padrão
- **Um token Apify = gateway universal** pra N actors (Instagram, TikTok, X…). Um `APIFY_TOKEN`, muitos scrapers.
- **CLI-as-Skill, não MCP pesado:** empacotar a API/CLI do Apify num script + SKILL.md (o que o `fetch_apify_comments.py` faz) reduz consumo de token **10-32×** vs servidor MCP. É o coração do budget-safe.
- Apify oficializou o padrão: **Apify Agent Skills** (`github.com/apify/agent-skills`) e **Apify MCP Server** (`github.com/apify/apify-mcp-server`, ~1.2k★) — uma chave, 3.000+ actors.

## Como usar aqui
```bash
python3 scripts/fetch_apify_comments.py --post-url "$POST_URL" --actor-id "$APIFY_ACTOR_ID" --limit 1000 --out raw_comments.json
```
- `--actor-id` = o actor de IG comments (schemas variam; passar `--input-json` se o actor exigir campos próprios).
- Run síncrono estourou (408) → rodar async pela UI/API do Apify e exportar o dataset como JSON. **Não re-rodar em loop.**

## Armadilhas (do KB — leia antes de prometer ao cliente)
1. **Fragilidade:** scrapers de IG/TikTok quebram com mudança de DOM (postmortem real: 12× em 6 semanas, 48h de manutenção). A coleta é o ponto que mais quebra.
2. **Custo por Compute Unit** (~$0.20/CU = 1GB RAM/hora): actors pesados de JS queimam CU rápido; 100→1M requests vira centenas de dólares.
3. **Rate limits / bloqueio de IP:** IG/TikTok agressivos; precisa backoff + proxy residencial (pago, não free).
4. **Só dado público** e às vezes divergente do nativo (contagens diferentes).
5. **Free tier Apify = $5 crédito** + proxy interno só; social media exige proxy residencial = plano pago.

## Tendência (pra onde migrar quando o Apify custar caro)
MCPs nativos de plataforma (X já tem oficial) · browser-use vision-first (Stagehand, Skyvern) · agentic scrapers (Reworkd) · APIs oficiais (TikTok Research API, Threads API). Migrar quando a manutenção dos actors virar fardo.
