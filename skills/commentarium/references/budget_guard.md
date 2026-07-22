# BUDGET GUARD — teto 300 créditos/dia (Manus free)

O Manus free = **Manus 1.6 Lite**, **300cr/dia que NÃO acumulam**, **1 task concorrente**, 2 scheduled tasks. Cap mensal real ~1.500/mês (o "refresh diário" engana). Regras duras:

## As 5 regras
1. **NUNCA Deep Research / Agent Mode autônomo pra coletar.** 1 Deep Research = **500-900cr** → estoura o dia inteiro num job.
2. **Manus cobra MESMO quando a task falha.** Re-run por output incompleto paga de novo. Prefira tasks determinísticas (script/query), não agente aberto.
3. **Coleta = script barato; LLM só na interpretação.** Rode `normalize` + `shortlist` ANTES; o LLM julga a shortlist (~120 comentários), nunca os 3 mil crus.
4. **1 task concorrente:** vários clientes = fila serial. Não prometa "analytics realtime de N clientes em paralelo" no free.
5. **Se for estourar o teto, PARE e avise** — não rode.

## Tabela de custo (aprox, Manus)
| Ação | Créditos |
|---|---|
| Chat simples | 5-15 |
| Web search | 10-30 |
| Geração de imagem | 30-50 |
| Code gen grande | 200-500 |
| **Deep Research** | **500-900** ⚠️ |
| Agente autônomo multi-hora | 5.000-20.000+ ☠️ |

## Estratégia budget-safe do Commentarium
Coleta (Apify) roda como **script fora do Manus** (ou script Manus determinístico, não Agent Mode). O Manus só entra pra **gerar o relatório/insight** sob demanda (chat 5-15cr). Assim o consumo diário fica previsível dentro dos 300cr. Dado bruto barato + interpretação sob demanda = MVP sustentável no free (1-2 clientes). Escalar = plano pago.
