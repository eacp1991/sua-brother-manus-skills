# Sua Brother — Manus Skills

Skills de Manus da marca **Sua Brother / Renatinha Diniz**, feitas e **testadas** pra rodar no projeto `Renatinha.IA` (Manus da Rê, conta Pro). Cada skill declara quais conectores usa — cada conector é um superpoder com papel fixo.

| Skill | Papel | Conectores |
|---|---|---|
| **brother-ultra-v7** | Persona + orquestrador: voz canônica, ideação ancorada em dado, roteamento dos superpoderes | Instagram · Apify · Firecrawl · Canva · Higgsfield · Trello · Agent Opus · Browser/Playwright |
| **commentarium** (v0.5) | Social listening de comentários → inteligência cultural (EVIDÊNCIA/INFERÊNCIA/HIPÓTESE) | Apify (coleta) · Instagram (âncora de contagem) |
| **ig-performance** (v1.0) | Relatórios/ranking/outliers com métricas privilegiadas | Instagram |
| **oraculo-sua-brother** (v1.0) | O Oráculo: consulta estratégica da criadora com grounding total num super KB embarcado (5,5k+ átomos master + 347 social) | nenhum (KB local + Python) |

## Instalar no Manus

**Rota A — Importar do GitHub (recomendada):** no projeto → Habilidades → Adicionar → *Importar do GitHub* → colar a URL deste repositório.
**Rota B — Upload:** Habilidades → Adicionar → *Fazer upload de habilidade* → subir o `.skill` da pasta `dist/` (um por skill).

> ⚠️ **oraculo-sua-brother instala SÓ pela Rota B** (upload do `.skill` entregue em canal privado): os bancos de conhecimento (`kb/*.db`, conteúdo pago) **não são versionados neste repositório público** — o pacote completo é gerado localmente fora do repo.

Depois de instalar, habilite os conectores recomendados do projeto (Instagram, Apify, Firecrawl, Playwright, Canva, Higgsfield, Trello, Agent Opus, Meu Navegador).

## Testar (protocolo)

1. **ig-performance:** "Snapshot verificado da conta" → deve retornar ~600k seguidores com `pulled_at` e fonte. Divergência grosseira = investigar.
2. **commentarium:** "Use a skill commentarium no modo SERIO_SOCIALDEV no post <permalink>" → o relatório DEVE abrir com a cobertura da coleta (N/esperado). Sem cobertura = suspeitar.
3. **brother-ultra-v7:** "5 ideias de roteiro a partir do último commentarium" → toda ideia com fonte + gancho em frase completa + CTA pela régua.
4. Via API: `task.create` com `message.force_skills` + `message.connectors` (IDs via `skill.list` / `connector.list`).

## Regras herdadas por todas as skills

- **Anti-fabricação absoluta** (incidente 2026-07-21: agente sem ferramenta inventou dataset com "sucesso" — nunca mais).
- **Nunca publicar/responder/enviar sem ordem explícita.**
- **Anonimização por padrão** em material publicável; travas éticas do commentarium valem pra todos.
- **Protocolo de crise** (CVV 188) sobrepõe qualquer persona ou funil.

## Estrutura

```
skills/
  brother-ultra-v7/   SKILL.md + references/ (voz canon, guardrails, fewshots, linguagem nativa 2026-07)
  commentarium/       SKILL.md + references/ + scripts/ (CLI testada com 868 comentários reais) + templates/ + runbooks/
  ig-performance/     SKILL.md + references/ (capacidades reais do conector, probe 2026-07-21)
dist/                 pacotes .skill prontos pra upload
```

## Changelog

- **2026-07-22 (noite)** — oraculo-sua-brother v1.0: skill de consulta com super KB embarcado (rótulos EVIDÊNCIA/INFERÊNCIA/HIPÓTESE, tripwire de exaustão, barreira anti-injeção via conteúdo recuperado, escada FTS5 dual-KB com fonte rastreável). Código no repo; KBs (.db) e pacote .skill ficam FORA (IP pago — instalar via upload). 14 achados da revisão adversarial Codex aplicados.
- **2026-07-22** — v7 inicial: brother-ultra-v7 + commentarium v0.5 (CLI real nos scripts, anti-fabricação, conector Apify, case 868) + ig-performance v1.0. Pipeline de scripts testado ponta-a-ponta com dados reais do reel Bora Viver.
