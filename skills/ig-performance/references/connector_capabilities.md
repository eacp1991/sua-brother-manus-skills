# Mapeamento de Capacidades: Conector Instagram

**Documento de Referência Técnica**  
**Data:** 22 de julho de 2026  
**Escopo:** Somente-leitura — documentação de ferramentas reais, schemas e workflows automatizáveis  
**Autor:** Manus AI

---

## Sumário Executivo

O conector Instagram do Manus expõe **4 ferramentas MCP** (Model Context Protocol) que permitem automação de workflows de social media. Este documento consolida os achados de probes reais executadas contra a conta `@renatinhadiniz` (598.824 seguidores, 4.790 posts), documentando cada campo retornado, limites operacionais e 5 workflows de automação que podem ser implementados imediatamente usando agendamento via `manus-config schedule`.

**Achado crítico:** O conector **não oferece ferramentas nativas para stories, comentários, menções, DMs ou agendamento direto**. Agendamento é implementado através de `manus-config schedule` combinado com `create_instagram`, permitindo publicações em horários definidos por cron ou intervalo.

---

## 1. Ferramentas Disponíveis: Tabela de Referência

| Ferramenta | Tipo | Entrada | Saída | Leitura/Escrita | Status |
|---|---|---|---|---|---|
| `get_account_info` | Consulta | Nenhuma (objeto vazio) | 9 campos de perfil | Leitura | ✓ Testada |
| `get_post_list` | Consulta | `limit` (5-20), `page_cursor` | 14 campos por post | Leitura | ✓ Testada |
| `get_post_insights` | Consulta | `post_id` | 7 métricas lifetime | Leitura | ✓ Testada |
| `create_instagram` | Ação | 6 parâmetros | UI card para confirmação | Escrita | ✗ Não executada (por regra) |

**Ferramentas não encontradas:** Stories, comentários, menções, DMs, insights por período, agendamento nativo, análise de hashtags, análise de audiência, relatórios de crescimento.

---

## 2. Detalhamento de Ferramentas de Leitura

### 2.1 `get_account_info` — Informações de Perfil

**Descrição:** Retorna metadados da conta de negócios do Instagram autenticada.

**Entrada:**
```json
{}
```

**Saída (9 campos):**

| Campo | Tipo | Exemplo | Descrição |
|---|---|---|---|
| `id` | string | `27766670789611552` | ID único da conta no Instagram |
| `username` | string | `renatinhadiniz` | Nome de usuário (sem @) |
| `name` | string | `Renatinha Diniz \| Sua Brother` | Nome exibido no perfil |
| `biography` | string | `🎤 Apresentadora há 18 anos...` | Bio com suporte a emoji e quebras de linha |
| `followers_count` | integer | `598824` | Contagem de seguidores (snapshot atual) |
| `follows_count` | integer | `3213` | Contagem de contas seguidas |
| `media_count` | integer | `4790` | Total de posts publicados (histórico completo) |
| `website` | string | `https://suabrother.com/home/` | URL do site vinculado (se configurado) |
| `profile_picture_url` | string | `https://scontent-iad3-1.cdninstagram.com/...` | URL da foto de perfil em alta resolução |

**Observações:**
- Sem campos de demografia de audiência (idade, gênero, localização, horários de pico).
- Sem histórico de crescimento ou métricas de período.
- Sem dados de contas bloqueadas, seguidores falsos ou análise de audiência.

---

### 2.2 `get_post_list` — Histórico de Posts

**Descrição:** Retorna os posts mais recentes da conta com paginação por cursor.

**Entrada:**
```json
{
  "limit": 20,
  "page_cursor": "QVFIU2w1V3B6WC0yRkI4a3ZASdkdlSUROTTkzOHltc28zbjlDZA2tudTNzZAHcxZATdqWTBjcngwaU1ud0hYSlVfV2FnQzBLRDJBLWRrTnVlMnJTUUd1VWhBcGVR"
}
```

| Parâmetro | Tipo | Intervalo | Padrão | Obrigatório | Descrição |
|---|---|---|---|---|---|
| `limit` | integer | 5–20 | 5 | Não | Número de posts por página |
| `page_cursor` | string | N/A | N/A | Não | Cursor de paginação retornado pela resposta anterior |

**Saída (14 campos por post):**

| Campo | Tipo | Exemplo | Descrição |
|---|---|---|---|
| `id` | string | `17942655069055722` | ID único do post |
| `media_type` | string | `IMAGE`, `VIDEO`, `CAROUSEL_ALBUM` | Tipo de conteúdo |
| `media_product_type` | string | `FEED`, `REELS` | Categoria de produto (feed ou reels) |
| `caption` | string | `Você prometeu pra si mesmo...` | Legenda do post (suporta emoji e quebras) |
| `like_count` | integer | `201` | Contagem de likes (snapshot) |
| `comments_count` | integer | `2` | Contagem de comentários (snapshot) |
| `is_comment_enabled` | boolean | `true` | Se comentários estão habilitados |
| `is_shared_to_feed` | boolean | `true` | Se o reel foi compartilhado também no feed |
| `media_url` | string | `https://scontent-iad6-1.cdninstagram.com/...` | URL da imagem ou vídeo (CDN do Instagram) |
| `thumbnail_url` | string | `https://scontent-iad3-1.cdninstagram.com/...` | Thumbnail para vídeos (presente apenas em VIDEO e CAROUSEL_ALBUM) |
| `permalink` | string | `https://www.instagram.com/p/DbBeG2BS6Zk/` | URL pública do post |
| `shortcode` | string | `DbBeG2BS6Zk` | Código curto do post (usado em URLs) |
| `timestamp` | string (ISO 8601) | `2026-07-20T21:30:04+0000` | Data e hora de publicação (UTC) |
| `owner` | object | `{"id": "27766670789611552"}` | ID do proprietário (sempre a conta autenticada) |

**Paginação:**
- A resposta inclui um campo `next_page_cursor` quando há mais posts disponíveis.
- Ordenação: **mais recentes primeiro** (descendente por timestamp).
- Limite máximo: 20 posts por página.
- Sem filtros por período, hashtag, tipo de conteúdo ou performance.

**Dados obtidos na probe:**
- 20 posts retornados na primeira página.
- Tipos encontrados: `IMAGE` (1), `VIDEO` (6), `CAROUSEL_ALBUM` (13).
- Produtos: `FEED` (14), `REELS` (6).
- Intervalo de datas: 20 de julho a 1º de julho de 2026 (19 dias).

---

### 2.3 `get_post_insights` — Métricas de Performance

**Descrição:** Retorna 7 métricas de performance acumuladas (lifetime) para um post específico.

**Entrada:**
```json
{
  "post_id": "17942655069055722"
}
```

| Parâmetro | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `post_id` | string | Sim | ID do post (obtido via `get_post_list`) |

**Saída (7 métricas, estrutura uniforme para todos os tipos):**

Cada métrica é retornada como um objeto com os seguintes campos:

| Campo | Tipo | Descrição |
|---|---|---|
| `name` | string | Identificador da métrica (`shares`, `comments`, `likes`, `saved`, `total_interactions`, `reach`, `views`) |
| `title` | string | Rótulo legível (`Shares`, `Comments`, `Likes`, `Saved`, `Reels interactions` ou `Post interactions`, `Accounts reached`, `Views`) |
| `description` | string | Definição técnica da métrica |
| `period` | string | Período de agregação (`lifetime` — sempre) |
| `values` | array | Array com um objeto contendo `value` (número inteiro) |
| `id` | string | ID único da métrica (`{post_id}/insights/{name}/lifetime`) |

**Métricas Detalhadas:**

| Métrica | Definição | Unidade | Aplicável a |
|---|---|---|---|
| `shares` | Número de compartilhamentos | Contagem | Todos (IMAGE, VIDEO, CAROUSEL_ALBUM) |
| `comments` | Número de comentários | Contagem | Todos |
| `likes` | Número de likes | Contagem | Todos |
| `saved` | Número de salvamentos | Contagem | Todos |
| `total_interactions` | Soma de likes + saves + comments + shares (menos unlikes, unsaves, comentários deletados) | Contagem | Todos |
| `reach` | Contas únicas que viram o post (métrica estimada) | Contagem | Todos |
| `views` | Número de vezes que o post foi reproduzido ou exibido | Contagem | Todos |

**Comparação de Métricas por Tipo de Post:**

| Tipo | Post ID | Likes | Comments | Shares | Saved | Total Interactions | Reach | Views |
|---|---|---|---|---|---|---|---|---|
| **IMAGE** | 17942655069055722 | 201 | 2 | 14 | 31 | 263 | 6.934 | 13.012 |
| **VIDEO (Reel)** | 17897668449516451 | 580 | 10 | 202 | 63 | 888 | 15.486 | 21.159 |
| **CAROUSEL** | 18347273560223438 | 350 | 14 | 7 | 7 | 382 | 16.251 | 40.432 |

**Achados:**
- **Reels** geram 2,9× mais likes e 14,4× mais shares que imagens simples.
- **Carrosséis** têm o maior alcance (reach) e visualizações, mas menor taxa de compartilhamento.
- Métricas são **lifetime** (acumuladas desde publicação); sem suporte para períodos (últimos 7 dias, últimos 30 dias, etc.).
- Sem dados de impressões, cliques em links, salvamentos por tipo de audiência, ou análise de horário de pico.

---

## 3. Schema Completo de `create_instagram` (Documentado, Não Executado)

**Descrição:** Cria um post, story ou reel no Instagram. Gera um container de mídia e exibe um card UI para confirmação do usuário antes de publicar. Não suporta agendamento nativo; use `manus-config schedule` para publicações futuras.

**Entrada (6 parâmetros):**

```json
{
  "type": "post",
  "caption": "Sua legenda aqui",
  "media": [
    {
      "type": "image",
      "media_url": "https://example.com/image.jpg",
      "alt_text": "Descrição da imagem para acessibilidade"
    }
  ],
  "cover_url": "https://example.com/cover.jpg",
  "share_to_feed": true,
  "thumb_offset": 5000
}
```

### Parâmetros Detalhados:

| Parâmetro | Tipo | Obrigatório | Enum/Intervalo | Padrão | Descrição |
|---|---|---|---|---|---|
| `type` | string | Sim | `post`, `story`, `reels` | N/A | Tipo de conteúdo. Use `reels` para vídeos no feed (não `video`). |
| `caption` | string | Não | N/A | N/A | Legenda do post ou reel. Ignorada para stories. Suporta emoji, quebras de linha, hashtags, menções. |
| `media` | array | Sim | 1–10 itens | N/A | Array de objetos de mídia. Estrutura abaixo. |
| `cover_url` | string | Não (apenas reels) | N/A | N/A | URL da imagem de capa para reels. Limite: 8 MB. Se omitido, usa frame do vídeo em `thumb_offset`. |
| `share_to_feed` | boolean | Não (apenas reels) | N/A | `true` | Se `true`, o reel é compartilhado também no feed principal. |
| `thumb_offset` | integer | Não (apenas reels) | N/A | N/A | Offset em milissegundos para seleção de thumbnail do vídeo. Ignorado se `cover_url` fornecido. |

### Estrutura de `media` (Array de Objetos):

Cada item do array `media` é um objeto com os seguintes campos:

| Campo | Tipo | Obrigatório | Descrição | Limite |
|---|---|---|---|---|
| `type` | string | Sim | `image` ou `video` | N/A |
| `media_url` | string | Sim | URL pública da imagem ou vídeo | N/A |
| `alt_text` | string | Não | Descrição para acessibilidade (alt text) | 1.000 caracteres |
| `thumbnail_url` | string | Não (apenas video) | URL da thumbnail para preview de vídeo | 8 MB |

### Limites de Mídia:

| Aspecto | Post | Story | Reels |
|---|---|---|---|
| **Itens por conteúdo** | 1–10 (carrossel) | 1–10 (sequencial) | 1 |
| **Tamanho de imagem** | 8 MB | 8 MB | 8 MB |
| **Tamanho de vídeo** | N/A | 100 MB | 300 MB |
| **Duração de vídeo** | N/A | 60 segundos | 15 minutos |
| **Formatos suportados** | JPEG, PNG, GIF, WebP | JPEG, PNG, GIF, WebP, MP4, MOV | MP4, MOV, WebM |

### Comportamento de Publicação:

- **Posts:** Publica 1–10 imagens/vídeos como carrossel no feed.
- **Stories:** Publica 1–10 itens sequencialmente (cada item desaparece em 24 horas).
- **Reels:** Publica 1 vídeo no feed de reels. Se `share_to_feed=true`, também aparece no feed principal.

### Saída (Não Testada):

A ferramenta retorna um status de sucesso e exibe um **UI card** para confirmação do usuário. Após confirmação, o conteúdo é publicado e retorna:
- ID do post criado
- URL pública do post
- Timestamp de publicação

---

## 4. Limites Operacionais e Restrições

| Limite | Valor | Origem |
|---|---|---|
| Posts por página (get_post_list) | 5–20 | Schema MCP |
| Itens por post (carousel) | 1–10 | Schema MCP |
| Itens por story | 1–10 | Schema MCP |
| Tamanho de imagem | 8 MB | Schema MCP |
| Tamanho de vídeo (story) | 100 MB | Schema MCP |
| Tamanho de vídeo (reel) | 300 MB | Schema MCP |
| Duração de vídeo (story) | 60 segundos | Schema MCP |
| Duração de vídeo (reel) | 15 minutos | Schema MCP |
| Alt text | 1.000 caracteres | Schema MCP |
| Métricas de insights | Lifetime (acumuladas) | Probe real |
| Períodos de insights | Nenhum (sem filtro por data) | Probe real |
| Ferramentas de analytics | Nenhuma (sem relatórios, sem crescimento) | Probe real |
| Agendamento nativo | Não suportado | Documentação MCP |

---

## 5. Workflows de Automação Implementáveis

Os 5 workflows abaixo podem ser implementados **hoje** combinando as ferramentas de leitura com `manus-config schedule` e scripts Python/Shell.

### Workflow 1: Relatório Semanal de Performance

**Objetivo:** Gerar um relatório de performance dos últimos 7 dias de posts e enviá-lo por email ou salvar em arquivo.

**Componentes:**
- `get_post_list` (limit=20) para obter posts da semana.
- `get_post_insights` para cada post (7 métricas).
- Script Python para agregar dados e gerar tabela.
- `manus-config schedule` com cron `0 0 9 * * 1` (segunda-feira, 09:00 UTC).

**Saída esperada:**
```
RELATÓRIO SEMANAL: @renatinhadiniz
Período: 15-21 de julho de 2026

Posts publicados: 8
Engagement médio: 645 interações
Melhor post: Reel "Aceitar não é gostar" (1.213 likes, 43 comentários)
Pior post: Imagem "Você prometeu..." (201 likes, 2 comentários)
Crescimento de seguidores: +1.200 (estimado)
```

**Implementação:**
```bash
manus-config schedule create \
  --title "Relatório Semanal de Performance" \
  --detail "Coletar posts da última semana, calcular métricas agregadas e gerar relatório de performance." \
  --cron "0 0 9 * * 1" \
  --repeated
```

---

### Workflow 2: Ranking de Posts (Top 10 All-Time)

**Objetivo:** Identificar os 10 posts com melhor performance (por likes, shares, reach) e listar em ordem de impacto.

**Componentes:**
- `get_post_list` com múltiplas chamadas (paginação via cursor) para percorrer todo o histórico (4.790 posts).
- `get_post_insights` para cada post (paralelizável em batches de 10).
- Script Python para ordenar por métrica e gerar ranking.

**Saída esperada:**
```
TOP 10 POSTS (@renatinhadiniz)

1. Reel "Você sente falta dela ou da versão de você..." (6.048 likes, 235 comentários, 4.514 views)
2. Reel "E se isso não for o fim?" (6.048 likes, 205 comentários, 4.514 views)
3. Carousel "33 anos de Farben" (350 likes, 14 comentários, 16.251 reach)
...
```

**Implementação:**
```bash
# Executar uma vez (ou agendado mensalmente)
manus-config schedule create \
  --title "Ranking Mensal de Top 10 Posts" \
  --detail "Percorrer histórico de posts, calcular métricas e gerar ranking de top 10 por engagement." \
  --cron "0 0 10 1 * *" \
  --repeated
```

---

### Workflow 3: Fila de Publicação Agendada

**Objetivo:** Agendar posts para serem publicados em horários específicos (ex.: segunda-feira 09:00, quarta-feira 14:00, sexta-feira 18:00).

**Componentes:**
- `manus-config schedule` com múltiplos crons para cada horário.
- Playbook com `create_instagram` (sem execução, apenas preparação de conteúdo).
- Fila de posts em arquivo JSON ou banco de dados.

**Implementação:**
```bash
# Publicar segunda-feira às 09:00
manus-config schedule create \
  --title "Publicação: Segunda-feira 09:00" \
  --detail "Publicar post pré-preparado no Instagram." \
  --cron "0 0 9 * * 1" \
  --repeated \
  --playbook "Chamar create_instagram com conteúdo da fila"

# Publicar quarta-feira às 14:00
manus-config schedule create \
  --title "Publicação: Quarta-feira 14:00" \
  --detail "Publicar post pré-preparado no Instagram." \
  --cron "0 0 14 * * 3" \
  --repeated

# Publicar sexta-feira às 18:00
manus-config schedule create \
  --title "Publicação: Sexta-feira 18:00" \
  --detail "Publicar post pré-preparado no Instagram." \
  --cron "0 0 18 * * 5" \
  --repeated
```

**Nota:** Cada schedule dispara uma tarefa separada. Para gerenciar fila, use um arquivo JSON com posts pendentes.

---

### Workflow 4: Monitoramento de Engagement em Tempo Real

**Objetivo:** Verificar a cada 2 horas se algum post atingiu milestones (1.000 likes, 100 comentários, 10.000 views) e alertar.

**Componentes:**
- `get_post_list` (limit=5) para obter posts mais recentes.
- `get_post_insights` para cada post.
- Script Python para comparar com snapshot anterior e detectar milestones.
- `manus-config schedule` com intervalo de 7.200 segundos (2 horas).

**Saída esperada:**
```
🎯 MILESTONE ATINGIDO!
Post: "E se isso não for o fim?"
Métrica: 6.048 LIKES (ultrapassou 5.000)
Timestamp: 2026-07-21 14:30 UTC
```

**Implementação:**
```bash
manus-config schedule create \
  --title "Monitoramento de Milestones" \
  --detail "Verificar posts recentes e alertar quando atingem milestones de engagement." \
  --interval 7200 \
  --repeated
```

---

### Workflow 5: Análise de Tendência de Conteúdo

**Objetivo:** Identificar padrões nos posts com melhor performance (tipo de conteúdo, comprimento de legenda, horário de publicação, uso de hashtags).

**Componentes:**
- `get_post_list` (múltiplas páginas) para obter histórico.
- `get_post_insights` para cada post.
- Script Python para análise de texto (NLP) e correlação.
- Gerar gráficos de tendência.

**Saída esperada:**
```
ANÁLISE DE TENDÊNCIA (@renatinhadiniz)

Tipo de conteúdo com melhor performance:
- Reels: 2,9× mais likes que imagens
- Carrosséis: 2,4× mais reach que imagens

Horário de publicação mais efetivo:
- 21:00 UTC: 1.200 likes médios
- 14:00 UTC: 850 likes médios
- 09:00 UTC: 600 likes médios

Comprimento de legenda ideal:
- 100-200 caracteres: 1.100 likes médios
- 200-500 caracteres: 950 likes médios
- >500 caracteres: 800 likes médios

Hashtags mais correlacionadas com alto engagement:
- #suabrother: +45% engagement
- #conscienciamasculina: +38% engagement
- #autoconhecimento: +32% engagement
```

**Implementação:**
```bash
manus-config schedule create \
  --title "Análise Mensal de Tendência" \
  --detail "Analisar padrões de conteúdo, horários e hashtags correlacionados com alta performance." \
  --cron "0 0 10 1 * *" \
  --repeated
```

---

## 6. Estrutura de Dados Retornada: Referência Completa

### 6.1 Resposta de `get_account_info`

```json
{
  "success": true,
  "result": {
    "id": "27766670789611552",
    "username": "renatinhadiniz",
    "name": "Renatinha Diniz | Sua Brother",
    "biography": "🎤 Apresentadora há 18 anos e mentora de homens desde 2017\n🙋🏼‍♀️ Autoconhecimento | Relacionamentos | Automobilismo\n👇🏻Conheça meus cursos aqui",
    "followers_count": 598824,
    "follows_count": 3213,
    "media_count": 4790,
    "website": "https://suabrother.com/home/",
    "profile_picture_url": "https://scontent-iad3-1.cdninstagram.com/v/t51.75761-19/..."
  }
}
```

### 6.2 Resposta de `get_post_list` (Exemplo de 1 Post)

```json
{
  "success": true,
  "result": {
    "data": [
      {
        "id": "17942655069055722",
        "caption": "Você prometeu pra si mesmo que não ia mais aceitar isso.\nLembra? Promessa pra você mesmo também é palavra empenhada.\n\nVocê tem cumprido a sua?",
        "comments_count": 2,
        "is_comment_enabled": true,
        "like_count": 201,
        "media_product_type": "FEED",
        "media_type": "IMAGE",
        "media_url": "https://scontent-iad6-1.cdninstagram.com/v/t51.82787-15/...",
        "owner": {
          "id": "27766670789611552"
        },
        "permalink": "https://www.instagram.com/p/DbBeG2BS6Zk/",
        "shortcode": "DbBeG2BS6Zk",
        "timestamp": "2026-07-20T21:30:04+0000"
      }
    ],
    "paging": {
      "cursors": {
        "before": "...",
        "after": "QVFIU2w1V3B6WC0yRkI4a3ZASdkdlSUROTTkzOHltc28zbjlDZA2tudTNzZAHcxZATdqWTBjcngwaU1ud0hYSlVfV2FnQzBLRDJBLWRrTnVlMnJTUUd1VWhBcGVR"
      }
    }
  }
}
```

### 6.3 Resposta de `get_post_insights` (Exemplo Completo)

```json
{
  "success": true,
  "result": {
    "data": [
      {
        "name": "shares",
        "period": "lifetime",
        "values": [{"value": 202}],
        "title": "Shares",
        "description": "The number of shares of your reel.",
        "id": "17897668449516451/insights/shares/lifetime"
      },
      {
        "name": "comments",
        "period": "lifetime",
        "values": [{"value": 10}],
        "title": "Comments",
        "description": "The number of comments on your reel.",
        "id": "17897668449516451/insights/comments/lifetime"
      },
      {
        "name": "likes",
        "period": "lifetime",
        "values": [{"value": 580}],
        "title": "Likes",
        "description": "The number of likes on your reel.",
        "id": "17897668449516451/insights/likes/lifetime"
      },
      {
        "name": "saved",
        "period": "lifetime",
        "values": [{"value": 63}],
        "title": "Saved",
        "description": "The number of saves of your reel.",
        "id": "17897668449516451/insights/saved/lifetime"
      },
      {
        "name": "total_interactions",
        "period": "lifetime",
        "values": [{"value": 888}],
        "title": "Reels interactions",
        "description": "The number of likes, saves, comments and shares on your reels minus the number of unlikes, unsaves and deleted comments.",
        "id": "17897668449516451/insights/total_interactions/lifetime"
      },
      {
        "name": "reach",
        "period": "lifetime",
        "values": [{"value": 15486}],
        "title": "Accounts reached",
        "description": "The number of unique accounts that have seen this reel, at least once. Reach is different from impressions, which may include multiple views of your reel by the same accounts. This metric is estimated.",
        "id": "17897668449516451/insights/reach/lifetime"
      },
      {
        "name": "views",
        "period": "lifetime",
        "values": [{"value": 21159}],
        "title": "Views",
        "description": "The number of times your reels was played or displayed.",
        "id": "17897668449516451/insights/views/lifetime"
      }
    ]
  }
}
```

---

## 7. Padrões de Uso Recomendados

### 7.1 Paginação em `get_post_list`

Para percorrer todo o histórico de posts (4.790 posts):

```python
import json
from manus_mcp_cli import tool_call

posts_all = []
page_cursor = None

while True:
    params = {"limit": 20}
    if page_cursor:
        params["page_cursor"] = page_cursor
    
    result = tool_call("get_post_list", params, server="instagram")
    posts_all.extend(result["result"]["data"])
    
    # Verificar se há próxima página
    if "paging" in result["result"] and "cursors" in result["result"]["paging"]:
        page_cursor = result["result"]["paging"]["cursors"].get("after")
        if not page_cursor:
            break
    else:
        break

print(f"Total de posts coletados: {len(posts_all)}")
```

### 7.2 Insights em Batch

Para coletar insights de múltiplos posts (paralelizável):

```python
from concurrent.futures import ThreadPoolExecutor
from manus_mcp_cli import tool_call

post_ids = ["17942655069055722", "17897668449516451", "18347273560223438"]

def get_insights(post_id):
    return tool_call("get_post_insights", {"post_id": post_id}, server="instagram")

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(get_insights, post_ids))

for result in results:
    print(f"Post {result['result']['data'][0]['id']}: {result['result']['data'][0]['values'][0]['value']} likes")
```

### 7.3 Agendamento com Playbook

Para agendar uma tarefa que chama `create_instagram`:

```bash
manus-config schedule create \
  --title "Publicar Reel Semanal" \
  --detail "Publicar reel pré-preparado no Instagram todas as segundas-feiras." \
  --cron "0 0 9 * * 1" \
  --repeated \
  --playbook "Chamar create_instagram com type=reels, media=[{type: video, media_url: https://example.com/video.mp4}], caption='Nova semana, novo mindset 💪'"
```

---

## 8. Limitações Conhecidas e Gaps

| Gap | Impacto | Workaround |
|---|---|---|
| Sem insights por período (últimos 7 dias, 30 dias) | Impossível análise de tendência temporal | Armazenar snapshots diários em banco de dados |
| Sem dados de impressões | Métrica de reach é estimada | Usar reach como proxy (métrica mais confiável) |
| Sem análise de audiência (idade, gênero, localização) | Impossível segmentação de conteúdo | Usar dados do Instagram Insights (manual) |
| Sem ferramentas para stories | Impossível automação de stories | Usar `create_instagram` com `type=story` (manual) |
| Sem ferramentas para comentários/menções | Impossível responder automaticamente | Integrar com ferramentas de CRM/social listening |
| Sem agendamento nativo | Requer `manus-config schedule` | Usar cron + schedule para automação |
| Sem análise de hashtags | Impossível pesquisa de hashtags | Usar ferramentas externas (Hashtagify, TagsForLikes) |
| Sem dados de crescimento | Impossível rastrear crescimento de seguidores | Armazenar snapshots de `followers_count` |
| Sem filtros em `get_post_list` | Impossível filtrar por tipo, período ou performance | Filtrar em Python após coleta |

---

## 9. Conclusão

O conector Instagram do Manus oferece um **conjunto mínimo mas funcional** de ferramentas para automação de workflows de social media. As 3 ferramentas de leitura (`get_account_info`, `get_post_list`, `get_post_insights`) permitem análise de performance e geração de relatórios. A ferramenta de escrita (`create_instagram`) permite publicação de posts, stories e reels, com agendamento via `manus-config schedule`.

**Recomendação:** Para workflows de social media mais complexos (análise de audiência, resposta a comentários, campanhas multi-canal), considere integrar ferramentas externas como Hootsuite, Buffer ou Meta Business Suite.

---

## Apêndice: Comandos MCP de Referência Rápida

```bash
# Obter informações da conta
manus-mcp-cli tool call get_account_info --server instagram --input '{}'

# Listar 20 posts mais recentes
manus-mcp-cli tool call get_post_list --server instagram --input '{"limit": 20}'

# Obter insights de um post específico
manus-mcp-cli tool call get_post_insights --server instagram --input '{"post_id": "17942655069055722"}'

# Agendar publicação semanal
manus-config schedule create --title "Publicação Semanal" --cron "0 0 9 * * 1" --repeated

# Verificar status de schedules
manus-config schedule status --limit 1000
```

---

**Documento finalizado:** 22 de julho de 2026  
**Versão:** 1.0  
**Status:** Pronto para produção
