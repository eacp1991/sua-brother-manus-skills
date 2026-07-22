# MANUS_RUNBOOK — COMMENTARIUM v0.3 Serious First

## Objetivo

Rodar uma análise séria de comentários a partir de um post público.

## Variáveis

```bash
export APIFY_TOKEN="..."
export APIFY_ACTOR_ID="username~actor-name"
export POST_URL="https://www.instagram.com/reel/.../"
```

## 1. Coletar

```bash
python3 scripts/fetch_apify_comments.py \
  --post-url "$POST_URL" \
  --actor-id "$APIFY_ACTOR_ID" \
  --limit 1000 \
  --out raw_comments.json
```

## 2. Normalizar

```bash
python3 scripts/normalize_comments.py raw_comments.json normalized_comments.json
```

## 3. Gerar shortlist séria

```bash
python3 scripts/shortlist_comments.py normalized_comments.json shortlist.json --mode SERIO_SOCIALDEV --top 120
```

## 4. Fazer análise LLM

Cole no Manus:

```text
Use COMMENTARIUM_MANUS_PROMPT.md.
Modo: SERIO_SOCIALDEV.
Leia shortlist.json e normalized_comments.json.
Gere relatório estratégico sério, com evidência/inferência/hipótese.
Mantenha análise estratégica, séria e anonimizada. Não exponha @ reais no output público.
```

## 5. Criar conteúdo derivado, se solicitado

Depois do relatório sério, rode:

```text
Agora use CREATOR_INTELLIGENCE sobre o mesmo relatório.
Gere respostas em vídeo, carrosséis, hooks e plano de 7 dias.
Preserve as categorias e evidências da análise séria.
```

## 6. Segurança

Antes de output público:

```bash
cat runbooks/ETHICS_CHECKLIST.md
```

## Observação

Se o run síncrono do Apify passar do limite, use task pré-configurada ou rode assíncrono pela própria UI/API do Apify e exporte dataset como JSON/CSV.
