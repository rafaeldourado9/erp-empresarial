# Plano de Roadmap — ERP Solar

> Documento vivo. Marcar `[x]` quando concluído. Cada fase tem critérios de aceitação e checklist de testes obrigatório.
>
> **Ordem de execução acordada:** Vendedores → Orçamentos → Caixa → Financeiro.
> Razão: orçamentos é o maior gargalo de produto; financeiro é o mais transversal e depende dos outros estarem prontos.

---

## Convenções

- **Migrations** ficam em `backend/alembic/versions/` e devem encadear `down_revision` corretamente.
- **Catálogos estáticos** ficam em `backend/app/quotes/data/` (volume `./backend/app:/app/app`).
- **PDFs** gerados no backend usam `weasyprint` ou `reportlab` — decidir antes de Caixa.
- **Permissões**: campos de configuração soberana → apenas perfil `ADMIN`.
- **Testes**: cada item da checklist de testes deve ter print, GIF curto, ou nota explícita "OK em http://localhost:5173/..." antes de marcar.

---

## Fase 1 — Vendedores (fechar pendências)

> Status: parte já entregue (migration `f3a1b2c4d5e6`, `Operadores.tsx` modificado). Aguardando lista do usuário sobre o que falta.

### Backend
- [ ] Aguardar lista de pendências apontadas pelo usuário
- [ ] Caso falte algo no schema/ORM, criar migration nova encadeada após `f3a1b2c4d5e6`
- [ ] Validar que `senha_inicial` (texto plano só na criação) é hashada antes de persistir
- [ ] Endpoint para alterar comissão sem precisar reabrir modal completo (PATCH parcial)

### Frontend (`Operadores.tsx`)
- [ ] Confirmar com usuário se botões pill cobrem todos os perfis necessários
- [ ] Confirmar se "Comissão" é input numérico direto em todos os lugares (sem slider/dropdown)
- [ ] Verificar exibição de telefone/endereço/email na listagem e modal
- [ ] Campo de senha inicial visível na criação; alteração de senha inline na edição

### Testes
- [ ] Criar vendedor novo com todos os campos preenchidos → salva e aparece na tabela
- [ ] Trocar perfil clicando no pill → muda cor do badge instantaneamente
- [ ] Digitar 12,5 no campo de comissão → salva como número
- [ ] Editar vendedor existente e trocar senha → login com nova senha funciona
- [ ] Tentar editar/excluir vendedor sendo perfil não-admin → backend bloqueia (403)

---

## Fase 2 — Orçamentos (wizard + calculadora + catálogo)

> Maior frente. Subdividir em 2.A → 2.E para conseguir testar incremental.

### 2.A — Catálogo: adicionar Solis e revisar lista

O usuário pediu: **Solis, ABB, Growatt, Deye, Sungrow, GoodWe**. Já presentes no catálogo: ABB/FIMER, Growatt, Deye, Sungrow, GoodWe. **Falta Solis.**

- [ ] Adicionar linha "Solis" em `backend/app/quotes/data/solar_catalog.py` cobrindo:
  - [ ] String mono 220V: 2kW, 3kW, 5kW (S5-GR1P/S6-GR1P)
  - [ ] String tri 220V: 5kW, 8kW, 10kW, 12kW, 15kW (S5-GR3P, S6-GR3P)
  - [ ] String tri 380V: 20kW, 25kW, 30kW, 50kW, 60kW, 80kW, 100kW (S5-GC, S6-GU)
  - [ ] Híbrido mono 220V: 3kW, 5kW, 6kW (S6-EH1P)
  - [ ] Híbrido tri: 5kW, 10kW, 15kW (S6-EH3P)
- [ ] Conferir que cada item tem `potencia_kw`, `fases`, `tensao_saida_v`, `num_mppt`, `tensao_mppt_min/max`, `corrente_cc_max`, `garantia_anos`, `eficiencia_max`, `comunicacao`, `certificacoes` com valores reais de datasheet
- [ ] Adicionar campo `componentes_opcionais` no catálogo (lista de transformadores, string boxes, otimizadores etc.) — nova estrutura `COMPONENTES_OPCIONAIS`
- [ ] Endpoint `GET /solar/componentes` retornando os opcionais filtráveis por categoria

**Critério de aceitação:** chamando `GET /solar/inversores?marca=Solis` retorna ≥ 15 modelos com dados completos.

### 2.B — Wizard de orçamento

Quebrar o `OrcamentoEditor.tsx` (1443 linhas) em etapas. Arquitetura proposta: manter uma única rota, mas controlar `step` no state e renderizar componente da etapa atual. Componentes em `frontend/src/pages/admin/orcamento/`:

```
orcamento/
├── WizardLayout.tsx        — header com stepper + navegação prev/next
├── Step1_Cliente.tsx       — cliente, vendedor, localização (UF/cidade)
├── Step2_Dimensionamento.tsx — calculadora rápida (consumo → placas)
├── Step3_Modulo.tsx        — seleção do módulo fotovoltaico
├── Step4_Inversor.tsx      — seleção do inversor (tipo → marca → modelo)
├── Step5_Componentes.tsx   — transformadores e opcionais
├── Step6_Resumo.tsx        — resumo com itens discriminados + %, validação overload, ações (salvar/aprovar/exportar)
└── hooks/useOrcamentoDraft.ts — draft em React Context + localStorage
```

- [ ] Criar `WizardLayout` com stepper visual (1...6, etapa atual destacada)
- [ ] Implementar navegação: botão "Voltar" sempre habilitado a partir de Step2; "Avançar" desabilitado até validar campos obrigatórios da etapa
- [ ] Draft persistido em `localStorage` por usuário (chave `orcamento-draft-{userId}`) — recupera ao recarregar
- [ ] No final, Step6 invoca o mesmo `orcamentosApi.create/update` atual — sem alterar contrato de API

**Critério de aceitação:** criar um orçamento do zero passando pelas 6 etapas resulta no mesmo objeto persistido no banco que a versão antiga.

### 2.C — Calculadora de dimensionamento rápido (dentro de Step2)

Fórmulas conforme manual interno Nacional Energy:

```
Geração mensal por placa  = potência_placa_kW × 126
Quantidade de placas      = teto(consumo_kWh_mês / geração_por_placa)
kWp do sistema            = qtd_placas × potência_placa_kW
Recalculo p/ outra placa  = teto(kWp_sistema / nova_potência_kW)
Overload máximo           = potência_inversor_W × fator_overload  (1.30 a 1.50)
Verificação               = kWp_sistema ≤ overload_máximo
```

- [ ] Função pura `calcularDimensionamento({ consumo, potenciaPlaca, fatorRegional? })` em `frontend/src/lib/solar.ts` (testável isolada)
- [ ] UI: 3 inputs (consumo kWh/mês, potência da placa em W, UF) → mostra geração por placa, qtd recomendada (arredondada), kWp resultante
- [ ] Botão "Recalcular com outra placa" abre campo de nova potência e exibe nova quantidade
- [ ] Card de overload: input do inversor (kW) + fator (slider 1.0 a 1.7) → mostra kWp máximo e status (verde ≤ / vermelho >)
- [ ] Fator regional vindo de `solar_states.py` por padrão, sobrescrevível manualmente
- [ ] Botão "Aplicar ao orçamento" copia placas escolhidas para o Step3 (seleciona o módulo no dropdown automaticamente se modelo da potência indicada existe)

### 2.D — Seleção de módulo e inversor (Step3/Step4) com dropdown profissional

Fluxo solicitado: selecionar tipo (on-grid / híbrido / off-grid / micro) → marca → modelo.

- [ ] Step4 começa com 4 cards grandes (tipo: string=on-grid, hibrido, off_grid, micro) — seleção visual com ícone
- [ ] Após tipo escolhido, mostra lista de marcas disponíveis para aquele tipo (chips clicáveis)
- [ ] Após marca, dropdown searchable com modelos: cada linha mostra **modelo**, **kW**, **fases** (1ø/3ø), **tensão saída** (220/380), badge de overload sugerido
- [ ] Filtros laterais: faixa de potência (slider 2-200 kW), fases (1/3), tensão (220/380), garantia mínima
- [ ] Step3 (módulo) tem padrão similar: tipo (mono/half_cell/topcon/bifacial) → marca → modelo, com filtros de potência e eficiência

**Critério de aceitação:** carregar Step4, filtrar por tipo=hibrido + fase=1 + tensao=220 → lista enxuta sem inversores incompatíveis.

### 2.E — Premissas automáticas (soberania admin) e resumo

- [ ] Backend: `PremissaORM` ganha flag `obrigatoria` (boolean, default false). Migration nova.
- [ ] Configurações: apenas perfil `ADMIN` pode marcar/desmarcar `obrigatoria` e editar `valor_padrao`. Backend retorna 403 para outros perfis.
- [ ] Orçamento: ao criar, **toda** premissa com `obrigatoria=true` da empresa é aplicada automaticamente, sem opção de remover. Operador só remove/edita premissas não-obrigatórias.
- [ ] Frontend: na tela de resumo (Step6), premissas obrigatórias aparecem na seção PREMISSAS com cadeado e tooltip "definida pelo administrador"
- [ ] Componente `TabelaComposicao` já existente exibe % automaticamente — garantir que itens + premissas obrigatórias entram no cálculo do total e na coluna `% DO TOTAL`

### Testes — Fase 2

- [ ] Wizard: criar orçamento passando por todas as 6 etapas até salvar; recarregar página no meio → draft preservado
- [ ] Calculadora: consumo 600 kWh/mês + placa 540W deve retornar 9 placas, 4,86 kWp (caso do manual)
- [ ] Calculadora: recalculo com placa 620W deve retornar 8 placas
- [ ] Overload: inversor 5kW × fator 1.5 → 7,5 kWp máximo; sistema de 4,86 kWp → status verde
- [ ] Overload: sistema de 8 kWp com mesmo inversor → status vermelho com mensagem
- [ ] Catálogo: filtrar inversor por tipo=micro retorna apenas Enphase/Hoymiles/APSystems
- [ ] Catálogo: filtrar por marca=Solis retorna ≥ 15 modelos
- [ ] Premissas: operador não-admin não consegue editar premissa marcada como obrigatória (UI desabilitada + backend retorna 403)
- [ ] Premissas: criar orçamento → premissa obrigatória aparece automaticamente no resumo
- [ ] Resumo: tabela de composição soma 100% nas porcentagens
- [ ] PDF/exportar: caso já exista exportação, validar que o novo fluxo wizard não quebrou

---

## Fase 3 — Caixa (produtos em OS + PDFs)

### Backend
- [ ] `OrdemServicoORM` já tem itens? Verificar se vínculo com `produtos` está correto. Se não, migration adicionando FK opcional `produto_id` em `ItemOrdemServicoORM`
- [ ] Endpoint `GET /pos/produtos` retornando catálogo de produtos ativos da empresa para popular o select da OS
- [ ] Endpoint `POST /pos/ordens/{id}/pdf` → retorna PDF binário da OS individual
- [ ] Endpoint `GET /pos/ordens/relatorio?inicio=&fim=&status=` → retorna PDF com resumo de todas as OS no período
- [ ] Decidir biblioteca: **weasyprint** (HTML→PDF, mais fácil para layouts ricos) vs **reportlab** (mais controle, mais código)
  - Recomendação: weasyprint. Template Jinja2 em `backend/app/pos/templates/`

### Frontend (`Caixa.tsx`)
- [ ] `ProdutoSelect` já existe (linha 29). Garantir que `produtos` está sendo carregado de `/pos/produtos` e não está vazio na hora de criar OS
- [ ] Botão "Criar novo produto" abre modal inline; ao salvar, novo produto entra no select e é selecionado automaticamente
- [ ] Vincular produto é opcional (manter campo livre `descricao` se nenhum produto selecionado)
- [ ] Botão "Exportar PDF" em cada linha da listagem de OS → download
- [ ] Botão "Relatório do período" no topo → modal com filtros (data início/fim, status) → gera PDF resumo

### Testes
- [ ] Criar OS sem produto vinculado (só descrição) → salva ok
- [ ] Criar OS com produto do catálogo selecionado → salva com `produto_id` correto no banco
- [ ] Criar produto novo inline → aparece imediatamente no select
- [ ] Baixar PDF de uma OS → abre, tem dados corretos (cliente, itens, total, assinatura)
- [ ] Baixar PDF do relatório com filtro de período → tabela com todas as OS do período + totais

---

## Fase 4 — Financeiro (integração total + abatimento + relatórios + auditoria)

> Mais sensível. Tocar com cuidado pra não quebrar histórico existente.

### 4.A — Integração total com outros módulos

Objetivo: financeiro deve refletir **todas** entradas e saídas dos módulos.

- [ ] Mapear origens: `caixa` (vendas + OS), `orcamento` (aprovados), `comissao`, `manual`. Verificar se algum módulo ainda não está enviando ao financeiro.
- [ ] Migration `d3e4f5a6b7c8` já existe — revisar e completar caso falte algo
- [ ] Hook nos services: ao aprovar orçamento → criar `Conta` a receber; ao pagar comissão → criar `Conta` a pagar; ao fechar OS → criar lançamento
- [ ] Garantir que badges de `origem` cobrem todos os casos (já existe `ORIGEM_CONFIG` em `Financeiro.tsx`)
- [ ] View consolidada `GET /finance/visao-geral?periodo=` retornando entradas/saídas agregadas por origem

### 4.B — Abatimento parcial preservando valor cheio

Requisito chave: pagamento parcial deve mostrar **valor cheio**, **valor abatido** e **restante**, mas o valor de referência da conta **não muda**.

- [ ] `ContaORM` já tem `valor`. Confirmar que `valor_pago` é soma agregada de `PagamentoParcial` e que `valor_restante` é derivado (não persistido) → evita drift
- [ ] Backend: ao registrar abatimento via `POST /finance/contas/{id}/abater`, validar que `valor_abatido <= valor_restante`
- [ ] Frontend: `ModalPagamentoParcial` já existe (linha 39). Garantir que mostra:
  - Valor original da conta (sempre o cheio)
  - Total já abatido (somatório dos pagamentos)
  - Restante calculado
  - Histórico de abatimentos (lista de pagamentos com data e observação)
- [ ] Status da conta:
  - `aberto` → nenhum pagamento
  - `parcial` → 0 < valor_pago < valor
  - `quitado` → valor_pago = valor
  - Nunca alterar `valor` original

### 4.C — Relatórios e extratos complexos

- [ ] Relatório DRE mensal/anual em PDF
- [ ] Extrato por categoria, por origem, por conta corrente
- [ ] Fluxo de caixa previsto vs realizado
- [ ] Aging de recebíveis (já existe parcialmente — completar formato impresso)
- [ ] Aging de pagáveis
- [ ] Todos os relatórios com botão "Gerar PDF" (mesma lib decidida na Fase 3)

### 4.D — Filtros avançados de auditoria

- [ ] Página dedicada `Auditoria.tsx` (já existe, expandir) com filtros:
  - Período (de–até)
  - Origem (multiselect)
  - Categoria
  - Conta corrente
  - Status (aberto/parcial/quitado/cancelado)
  - Operador que criou/alterou
  - Faixa de valor (min/max)
  - Texto livre (busca em descrição e observações)
- [ ] Cada lançamento mostra trilha de auditoria: criação, alterações, abatimentos, com timestamp e operador responsável
- [ ] Exportação CSV + PDF da query filtrada

### Testes — Fase 4

- [ ] Aprovar orçamento → conta a receber aparece no financeiro com `origem=orcamento`
- [ ] Pagar comissão → conta a pagar aparece com `origem=comissao`
- [ ] Fechar OS → lançamento aparece com `origem=caixa`
- [ ] Conta de R$ 1.000,00: abater R$ 300 → valor original continua R$ 1.000,00; restante = R$ 700; status = `parcial`
- [ ] Mesma conta: abater + R$ 700 → status muda para `quitado`; histórico mostra 2 abatimentos
- [ ] Tentar abater R$ 1.500 numa conta de R$ 1.000 → backend rejeita (422)
- [ ] DRE em PDF: valores batem com soma dos lançamentos no período
- [ ] Filtro de auditoria com múltiplos critérios → backend responde correto e PDF reflete o filtro
- [ ] Exportar CSV → abre no Excel sem encoding quebrado (UTF-8 com BOM)

---

## Critérios transversais (todas as fases)

- [ ] Nenhuma fase entra em main com migration sem `downgrade()` testado em dev
- [ ] Nenhuma rota nova sem proteção de auth + perfil
- [ ] Nenhum endpoint que mexe em dinheiro sem testes manuais documentados
- [ ] Após cada fase, rodar `docker compose up -d --build` limpo e validar smoke test (login → dashboard → criar registro de exemplo no módulo afetado)
- [ ] Commit por fase concluída (não acumular as 4 num único commit)

---

## Estratégia de testes manuais

Cada fase tem sua subseção "Testes" acima. Padrão para marcar como `[x]`:

1. Backend: chamar via curl/httpie ou Swagger (`http://localhost:8000/docs`) e anotar resposta.
2. Frontend: usar Chrome em `http://localhost:5173/`, percorrer fluxo descrito.
3. Migrations: rodar `alembic upgrade head` e `alembic downgrade -1` em base de dev limpa.
4. Bugs: abrir issue interna ou anotar em `docs/BUGS_TRACKING.md` (criar se necessário).

---

## Próximos passos imediatos

1. Usuário lista pendências de **Vendedores** → fecho Fase 1.
2. Começamos **Fase 2.A** (adicionar Solis ao catálogo) — entrega rápida e isolada.
3. Avançamos para 2.B (wizard) — entrega visível mas grande; pode ser dividida em PRs/commits separados por etapa do wizard.

> Atualizar este documento ao concluir cada item ou descobrir nova pendência.
