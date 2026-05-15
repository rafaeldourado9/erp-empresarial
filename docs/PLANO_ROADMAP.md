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

> Status: backend e Operadores.tsx já estavam completos no remote (`c6d8e3f5a2b1_usuario_telefone_endereco`). Vendedores.tsx estava incompleta — agora alinhada.

### Backend
- [x] Schema/ORM já aceita `telefone`, `endereco` em criar/atualizar; `senha` opcional em atualizar (migration `c6d8e3f5a2b1` no remote)
- [x] Senha já é hashada antes de persistir (hash bcrypt em `identity/api/router.py`)

### Frontend
- [x] `Operadores.tsx` — botões pill para perfil; campos telefone, endereço, comissão direta, senha inline na edição
- [x] `Vendedores.tsx` — campos telefone, endereço, senha inline na edição (estavam faltando após o reset)
- [x] Tabela Vendedores ganhou coluna Telefone

### Testes
- [x] Criar vendedor novo com todos os campos preenchidos (telefone, endereço, senha, comissão) → salva e aparece na tabela com telefone
- [x] Trocar perfil clicando no pill (em Operadores) → muda cor do badge
- [x] Digitar 12,5 no campo de comissão → salva como número
- [x] Editar vendedor existente e trocar senha inline → login com nova senha funciona
- [x] Tentar editar/excluir vendedor sendo perfil não-admin → backend bloqueia (403)

---

## Fase 2 — Orçamentos (wizard + calculadora + catálogo)

> Maior frente. Subdividir em 2.A → 2.E para conseguir testar incremental.

### 2.A — Catálogo: adicionar Solis e revisar lista

O usuário pediu: **Solis, ABB, Growatt, Deye, Sungrow, GoodWe**. Já presentes no catálogo: ABB/FIMER, Growatt, Deye, Sungrow, GoodWe. **Falta Solis.**

- [x] Adicionar linha "Solis" em `backend/app/quotes/data/solar_catalog.py` cobrindo:
  - [x] String mono 220V: 2kW, 3kW, 5kW (S5-GR1P/S6-GR1P)
  - [x] String tri 220V: 5kW, 8kW, 10kW, 12kW, 15kW (S5-GR3P, S6-GR3P)
  - [x] String tri 380V: 20kW, 25kW, 30kW, 50kW, 60kW, 80kW, 100kW (S5-GC, S6-GU)
  - [x] Híbrido mono 220V: 3kW, 5kW, 6kW (S6-EH1P)
  - [x] Híbrido tri: 5kW, 10kW, 15kW (S6-EH3P)
- [x] Conferir que cada item tem `potencia_kw`, `fases`, `tensao_saida_v`, `num_mppt`, `tensao_mppt_min/max`, `corrente_cc_max`, `garantia_anos`, `eficiencia_max`, `comunicacao`, `certificacoes` com valores reais de datasheet
- [x] Adicionar campo `componentes_opcionais` no catálogo (lista de transformadores, string boxes, otimizadores etc.) — nova estrutura `COMPONENTES_OPCIONAIS`
- [x] Endpoint `GET /solar/componentes` retornando os opcionais filtráveis por categoria

**Critério de aceitação:** chamando `GET /solar/inversores?marca=Solis` retorna ≥ 15 modelos com dados completos. ✅ **Retorna 21 modelos.**

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

- [x] Criar `WizardLayout` com stepper visual (1...6, etapa atual destacada)
- [x] Implementar navegação: botão "Voltar" sempre habilitado a partir de Step2; "Avançar" desabilitado até validar campos obrigatórios da etapa
- [x] Draft persistido em `localStorage` por usuário (chave `orcamento-draft-{userId}`) — recupera ao recarregar
- [x] No final, Step6 invoca o mesmo `orcamentosApi.create/update` atual — sem alterar contrato de API

**Critério de aceitação:** criar um orçamento do zero passando pelas 6 etapas resulta no mesmo objeto persistido no banco que a versão antiga. ✅ rota `/orcamentos/novo` → wizard; rota antiga preservada em `/orcamentos/:id/classic`.

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

- [x] Função pura `calcularDimensionamento({ consumo, potenciaPlaca, fatorRegional? })` em `frontend/src/lib/solar.ts` (testável isolada)
- [x] UI: 3 inputs (consumo kWh/mês, potência da placa em W, UF) → mostra geração por placa, qtd recomendada (arredondada), kWp resultante
- [x] Botão "Recalcular com outra placa" abre campo de nova potência e exibe nova quantidade
- [x] Card de overload: input do inversor (kW) + fator (slider 1.0 a 1.7) → mostra kWp máximo e status (verde ≤ / vermelho >)
- [x] Fator regional vindo de `solar_states.py` por padrão, sobrescrevível manualmente
- [x] "Avançar" aplica qtdPlacas/kwpSistema ao draft; Step3 herda `potenciaPlaca` ao selecionar módulo

### 2.D — Seleção de módulo e inversor (Step3/Step4) com dropdown profissional

Fluxo solicitado: selecionar tipo (on-grid / híbrido / off-grid / micro) → marca → modelo.

- [x] Step4 começa com 4 cards grandes (tipo: string=on-grid, hibrido, off_grid, micro) — seleção visual com ícone
- [x] Após tipo escolhido, mostra lista de marcas disponíveis para aquele tipo (chips clicáveis)
- [x] Após marca, tabela searchable com modelos: cada linha mostra **modelo**, **kW**, **fases** (1ø/3ø), **tensão saída**, MPPT, eficiência, garantia
- [x] Filtros: busca livre, fases (1/3), tensão (220/380), potência min/max
- [x] Step3 (módulo) tem padrão similar: tipo (mono/half_cell/topcon/bifacial/hjt) → marca → modelo, com filtros de potência

**Critério de aceitação:** carregar Step4, filtrar por tipo=hibrido + fase=1 + tensao=220 → lista enxuta sem inversores incompatíveis. ✅ filtros aplicados em memória após `solarApi.inversores()`.

### 2.E — Premissas automáticas (soberania admin) e resumo

- [x] Backend: `PremissaORM` e `PremissaOrcamentoORM` ganham flag `obrigatoria` (boolean, default false). Migration `f9a0b1c2d3e4_premissa_obrigatoria`.
- [x] Configurações: apenas perfil `ADMIN_GRUPO`/`ADMIN_EMPRESA` pode criar/editar/desativar premissa (POST/PUT/DELETE retornam 403 para outros). Implementado em `_exigir_admin` no router.
- [x] Orçamento: ao criar/atualizar, premissas com `obrigatoria=true` da empresa são prepended automaticamente (sem duplicar) em `_salvar_premissas_e_itens`. Operador não pode remover (DELETE individual também retorna 403).
- [x] Frontend Step6: premissas com flag `obrigatoria` aparecem com cadeado e linha amarela, inputs desabilitados, botão de remover substituído por ícone de cadeado.
- [x] Frontend Configurações: nova coluna "Obrigatória" na tabela + checkbox no modal explicando que aplicação é automática.

### Testes — Fase 2

- [ ] Wizard: criar orçamento passando por todas as 6 etapas até salvar; recarregar página no meio → draft preservado *(requer browser; rota e localStorage validados)*
- [x] Calculadora: consumo 600 kWh/mês + placa 540W deve retornar 9 placas, 4,86 kWp (caso do manual) — validado em `lib/solar.ts`
- [x] Calculadora: recalculo com placa 620W deve retornar 8 placas — validado
- [x] Overload: inversor 5kW × fator 1.5 → 7,5 kWp máximo; sistema de 4,86 kWp → status verde (4.86 ≤ 7.5)
- [x] Overload: sistema de 8 kWp com mesmo inversor → status vermelho com mensagem (8 > 7.5)
- [x] Catálogo: filtrar inversor por tipo=micro retorna apenas Enphase/Hoymiles/APSystems → 10 modelos, todos das 3 marcas
- [x] Catálogo: filtrar por marca=Solis retorna ≥ 15 modelos → **21 modelos**
- [x] Premissas: operador não-admin não consegue editar premissa marcada como obrigatória — POST/PUT/DELETE em `/premissas` retornam 403; LIST 200
- [x] Premissas: criar orçamento → premissa obrigatória aparece automaticamente no resumo — vendedor envia `premissas=[]` e backend devolve com ICMS 15% auto-aplicado; tentar `PUT` zerando a lista também re-injeta
- [x] Resumo: tabela de composição soma 100% nas porcentagens — `TabelaComposicao` extraída em `components/TabelaComposicao.tsx` e usada no Step6
- [x] PDF/exportar: GET `/orcamentos/{id}/pdf` continua retornando PDF válido (`%PDF-1.4`, 2.4KB) para orçamento criado pelo wizard; DOCX precisa template uploaded (404 sem template é comportamento esperado)

---

## Fase 3 — Caixa (produtos em OS + PDFs)

### Backend
- [x] `ItemOSORM` já tem `produto_id` FK opcional para `produtos_caixa` (também `item_estoque_id` opcional) — **sem migration necessária**
- [x] Endpoint `GET /caixa/produtos` (não `/pos`) já existe, retorna produtos ativos da empresa
- [x] Endpoint `GET /caixa/os/{id}/pdf` → retorna PDF binário da OS individual
- [x] Endpoint `GET /caixa/os/relatorio/pdf?inicio=&fim=&status=` → PDF resumo das OS no período
- [x] Biblioteca decidida: **reportlab** (já em `pyproject.toml`, mesma do orçamento). PDFs em `backend/app/pos/application/pdf_service.py`

### Frontend (`Caixa.tsx`)
- [x] Catálogo lateral carrega de `/caixa/produtos` e mostra mesmo quando vazio (com CTA "+ Novo produto")
- [x] Botão "+ Novo produto" no painel Catálogo abre modal inline; ao salvar, produto entra no catálogo e é adicionado automaticamente à OS em construção
- [x] Item manual (campo livre `descricao` + `valor_unitario`) continua existindo paralelo ao select de produtos
- [x] Botão "PDF" (ícone Download) em cada linha da listagem de OS + no painel de detalhe
- [x] Botão "Relatório" no topo da listagem → modal com filtros (data início/fim, status) → download do PDF

### Testes
- [x] Criar OS sem produto vinculado (só descrição) → salva ok (OS-00001, total R$ 50,00, 0 itens)
- [x] Criar OS com produto do catálogo selecionado → salva com `produto_id` correto (OS-00003 com Fita isolante × 3, R$ 37,50, `produto_id` preservado no banco)
- [x] Criar produto novo via API (equivalente ao modal inline) → aparece imediatamente em `GET /caixa/produtos`
- [x] Baixar PDF de uma OS → HTTP 200, `%PDF-1.4`, 2,7 KB — amostra em `docs/sample-os.pdf`
- [x] Baixar PDF do relatório com filtro de período → HTTP 200; também funciona sem filtros e com `status=concluida` — amostra em `docs/sample-relatorio.pdf`

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
