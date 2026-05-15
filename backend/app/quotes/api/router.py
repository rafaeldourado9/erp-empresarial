from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.identity.api.deps import UsuarioAtualDep
from app.identity.domain.constants import PerfilUsuario
from app.infrastructure.database import get_db
from app.quotes.api.schemas import (
    CalcularOrcamentoRequest, CalcularOrcamentoResponse,
    FecharOrcamentoRequest, ItemOrcamentoRequest, ItemOrcamentoResponse,
    OrcamentoRequest, OrcamentoResponse,
    PremissaOrcamentoRequest, PremissaOrcamentoResponse,
    PremissaRequest, PremissaResponse,
)
from app.quotes.application.calculator import ItemCalculo, PremissaCalculo, calcular
from app.quotes.infrastructure.repository import OrcamentoRepository, PremissaRepository
from app.quotes.infrastructure.orm_models import VariavelOrcamentoORM

router = APIRouter(tags=["orcamentos"])

# ── Variáveis de sistema (não armazenadas em BD, apenas referência) ────────────
VARIAVEIS_SISTEMA = [
    # Identificação
    {"chave": "NUMERO", "label": "Número do Orçamento", "grupo": "Identificação"},
    {"chave": "TITULO", "label": "Título", "grupo": "Identificação"},
    {"chave": "DATA", "label": "Data de Criação", "grupo": "Identificação"},
    {"chave": "VALIDADE", "label": "Validade (dias)", "grupo": "Identificação"},
    {"chave": "STATUS", "label": "Status", "grupo": "Identificação"},
    # Empresa
    {"chave": "EMPRESA", "label": "Nome da Empresa", "grupo": "Empresa"},
    {"chave": "EMPRESA_CNPJ", "label": "CNPJ da Empresa", "grupo": "Empresa"},
    # Cliente
    {"chave": "CLIENTE", "label": "Nome do Cliente", "grupo": "Cliente"},
    {"chave": "CLIENTE_CNPJ", "label": "CPF/CNPJ do Cliente", "grupo": "Cliente"},
    {"chave": "CLIENTE_EMAIL", "label": "E-mail do Cliente", "grupo": "Cliente"},
    {"chave": "CLIENTE_TELEFONE", "label": "Telefone do Cliente", "grupo": "Cliente"},
    {"chave": "CLIENTE_ENDERECO", "label": "Endereço do Cliente", "grupo": "Cliente"},
    {"chave": "CLIENTE_BAIRRO", "label": "Bairro do Cliente", "grupo": "Cliente"},
    {"chave": "CLIENTE_CIDADE", "label": "Cidade do Cliente", "grupo": "Cliente"},
    {"chave": "CLIENTE_ESTADO", "label": "Estado do Cliente", "grupo": "Cliente"},
    {"chave": "CLIENTE_COMPLEMENTO", "label": "Complemento do Endereço", "grupo": "Cliente"},
    # Vendedor
    {"chave": "VENDEDOR", "label": "Vendedor Responsável", "grupo": "Vendedor"},
    {"chave": "VENDEDOR_CELULAR", "label": "Celular do Vendedor", "grupo": "Vendedor"},
    # Financeiro
    {"chave": "VALOR_VENDA", "label": "Valor de Venda", "grupo": "Financeiro"},
    {"chave": "CUSTO_BASE", "label": "Custo Base", "grupo": "Financeiro"},
    {"chave": "SUBTOTAL", "label": "Subtotal", "grupo": "Financeiro"},
    {"chave": "OBSERVACOES", "label": "Observações", "grupo": "Financeiro"},
    # Dimensionamento Solar
    {"chave": "POTENCIA_SISTEMA", "label": "Potência Instalada (kWp)", "grupo": "Dimensionamento Solar"},
    {"chave": "GERACAO_MENSAL", "label": "Geração Mensal (kWh/mês)", "grupo": "Dimensionamento Solar"},
    {"chave": "CONSUMO_MENSAL", "label": "Consumo Médio Mensal (kWh)", "grupo": "Dimensionamento Solar"},
    {"chave": "AREA_UTIL", "label": "Área Necessária (m²)", "grupo": "Dimensionamento Solar"},
    # Módulo Solar
    {"chave": "MODULO_FABRICANTE", "label": "Fabricante do Módulo", "grupo": "Módulo Solar"},
    {"chave": "MODULO_MODELO", "label": "Modelo do Módulo", "grupo": "Módulo Solar"},
    {"chave": "MODULO_POTENCIA", "label": "Potência do Módulo (W)", "grupo": "Módulo Solar"},
    {"chave": "MODULO_QUANTIDADE", "label": "Quantidade de Módulos", "grupo": "Módulo Solar"},
    {"chave": "VC_MODULO_EFICIENCIA", "label": "Eficiência do Módulo (%)", "grupo": "Módulo Solar"},
    # Inversor
    {"chave": "INVERSOR_FABRICANTE", "label": "Fabricante do Inversor", "grupo": "Inversor"},
    {"chave": "INVERSOR_POTENCIA", "label": "Potência do Inversor (kW)", "grupo": "Inversor"},
    {"chave": "INVERSOR_POTENCIA_NOMINAL", "label": "Potência Nominal do Inversor", "grupo": "Inversor"},
    {"chave": "INVERSORES_UTILIZADOS", "label": "Quantidade de Inversores", "grupo": "Inversor"},
    # Análise Financeira
    {"chave": "ECONOMIA_MENSAL", "label": "Economia Mensal Esperada (R$)", "grupo": "Análise Financeira"},
    {"chave": "ECONOMIA_PERCENTUAL", "label": "Economia Esperada (%)", "grupo": "Análise Financeira"},
    {"chave": "VC_ANUAL_ATUAL", "label": "Conta de Luz Anual Atual (R$)", "grupo": "Análise Financeira"},
    {"chave": "VC_ANUAL_NOVO", "label": "Conta de Luz Anual com Solar (R$)", "grupo": "Análise Financeira"},
    {"chave": "VC_ECONOMIA_ANUAL", "label": "Economia Anual (R$)", "grupo": "Análise Financeira"},
    {"chave": "VC_SERVICO", "label": "Valor dos Serviços (R$)", "grupo": "Análise Financeira"},
    {"chave": "INFLACAO_ENERGETICA", "label": "Taxa de Inflação Energética (% a.a.)", "grupo": "Análise Financeira"},
    {"chave": "PERDA_EFICIENCIA_ANUAL", "label": "Perda de Eficiência Anual (%)", "grupo": "Análise Financeira"},
    {"chave": "GASTO_TOTAL_MENSAL_ATUAL", "label": "Gasto Total Mensal Atual (R$)", "grupo": "Análise Financeira"},
    {"chave": "GASTO_TOTAL_MENSAL_NOVO", "label": "Gasto Total Mensal Novo (R$)", "grupo": "Análise Financeira"},
    {"chave": "CAPO_BANCARIO", "label": "Campo Bancário / Conta", "grupo": "Financeiro"},
]


def _empresa_id(usuario: UsuarioAtualDep) -> UUID:
    if usuario.empresa_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Selecione uma empresa")
    return usuario.empresa_id


def _exigir_admin(usuario: UsuarioAtualDep) -> None:
    if usuario.perfil not in (PerfilUsuario.ADMIN_GRUPO, PerfilUsuario.ADMIN_EMPRESA):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem gerenciar premissas",
        )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _premissa_to_response(p: object) -> PremissaOrcamentoResponse:
    return PremissaOrcamentoResponse(
        id=UUID(p.id),
        premissa_id=UUID(p.premissa_id) if p.premissa_id else None,
        nome=p.nome, descricao=p.descricao, tipo=p.tipo,
        valor=float(p.valor), valor_calculado=float(p.valor_calculado),
        ordem=p.ordem,
        obrigatoria=bool(getattr(p, "obrigatoria", False)),
    )


def _item_to_response(i: object) -> ItemOrcamentoResponse:
    return ItemOrcamentoResponse(
        id=UUID(i.id), tipo=i.tipo, descricao=i.descricao,
        item_estoque_id=UUID(i.item_estoque_id) if i.item_estoque_id else None,
        quantidade=float(i.quantidade) if i.quantidade else None,
        valor_unitario=float(i.valor_unitario) if i.valor_unitario else None,
        valor_calculado=float(i.valor_calculado),
        ordem=i.ordem,
    )


async def _orc_to_response(orc: object, repo: OrcamentoRepository) -> OrcamentoResponse:
    premissas = await repo.listar_premissas(UUID(orc.id))
    itens = await repo.listar_itens(UUID(orc.id))
    return OrcamentoResponse(
        id=UUID(orc.id), empresa_id=UUID(orc.empresa_id), numero=orc.numero,
        titulo=orc.titulo, custo_base=float(orc.custo_base),
        subtotal=float(orc.subtotal), valor_venda=float(orc.valor_venda),
        status=orc.status,
        cliente_id=UUID(orc.cliente_id) if orc.cliente_id else None,
        vendedor_id=UUID(orc.vendedor_id) if orc.vendedor_id else None,
        criado_por=UUID(orc.criado_por), criado_em=orc.criado_em,
        atualizado_em=orc.atualizado_em,
        aprovado_em=orc.aprovado_em,
        enviado_em=orc.enviado_em,
        fechado_em=orc.fechado_em,
        observacoes=orc.observacoes, validade_dias=orc.validade_dias,
        endereco=orc.endereco, email=orc.email,
        telefone=orc.telefone, cpf=orc.cpf,
        campos_extras=orc.campos_extras or {},
        premissas=[_premissa_to_response(p) for p in premissas],
        itens=[_item_to_response(i) for i in itens],
    )


async def _resolver_premissa(
    req: PremissaOrcamentoRequest,
    premissa_repo: PremissaRepository,
    empresa_id: UUID,
) -> tuple[UUID | None, str, str | None, str, float, bool]:
    if req.premissa_id:
        template = await premissa_repo.buscar_por_id(req.premissa_id, empresa_id)
        if template is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Premissa {req.premissa_id} não encontrada")
        return (
            req.premissa_id, template.nome, template.descricao,
            template.tipo, float(template.valor), bool(template.obrigatoria),
        )
    if not req.nome or not req.tipo or req.valor is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Informe premissa_id ou (nome, tipo, valor)")
    return None, req.nome, req.descricao, req.tipo, req.valor, False


async def _salvar_premissas_e_itens(
    orc_id: UUID, custo_base: float, valor_venda: float | None,
    premissas_req: list[PremissaOrcamentoRequest],
    itens_req: list[ItemOrcamentoRequest],
    repo: OrcamentoRepository,
    premissa_repo: PremissaRepository,
    empresa_id: UUID,
) -> tuple[float, float]:
    # Bloquear premissas duplicadas pelo premissa_id
    ids_usados: set[str] = set()
    for p_req in premissas_req:
        if p_req.premissa_id:
            pid_str = str(p_req.premissa_id)
            if pid_str in ids_usados:
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    detail=f"Premissa duplicada: cada premissa só pode ser usada uma vez no orçamento",
                )
            ids_usados.add(pid_str)

    # Forçar inclusão das premissas obrigatórias da empresa.
    # Operador não pode remover — se faltar, prepende automaticamente.
    obrigatorias = await premissa_repo.listar_obrigatorias(empresa_id)
    obrigatorias_a_adicionar = [
        o for o in obrigatorias if str(o.id) not in ids_usados
    ]
    if obrigatorias_a_adicionar:
        premissas_req = [
            PremissaOrcamentoRequest(premissa_id=UUID(o.id), ordem=i)
            for i, o in enumerate(obrigatorias_a_adicionar)
        ] + list(premissas_req)

    premissas_calc: list[PremissaCalculo] = []
    premissas_resolvidas: list[tuple[UUID | None, str, str | None, str, float, int, bool]] = []
    for idx, p_req in enumerate(premissas_req):
        pid, nome, desc, tipo, valor, obrig = await _resolver_premissa(p_req, premissa_repo, empresa_id)
        premissas_calc.append(PremissaCalculo(
            id=str(idx), nome=nome, descricao=desc, tipo=tipo, valor=valor,
            ordem=p_req.ordem or idx,
        ))
        premissas_resolvidas.append((pid, nome, desc, tipo, valor, p_req.ordem or idx, obrig))

    itens_calc: list[ItemCalculo] = []
    for idx, i_req in enumerate(itens_req):
        itens_calc.append(ItemCalculo(
            id=str(idx), tipo=i_req.tipo, descricao=i_req.descricao,
            quantidade=i_req.quantidade, valor_unitario=i_req.valor_unitario,
            ordem=i_req.ordem or idx,
        ))

    calc = calcular(custo_base, premissas_calc, itens_calc, valor_venda)

    for idx, (pid, nome, desc, tipo, valor, ordem, obrig) in enumerate(premissas_resolvidas):
        vc = calc.premissas[idx]["valor_calculado"]
        await repo.criar_premissa(orc_id, pid, nome, desc, tipo, valor, vc, ordem, obrigatoria=obrig)

    for idx, (i_req, i_calc) in enumerate(zip(itens_req, calc.itens)):
        await repo.criar_item(
            orcamento_id=orc_id, tipo=i_req.tipo, descricao=i_req.descricao,
            item_estoque_id=i_req.item_estoque_id,
            quantidade=i_req.quantidade, valor_unitario=i_req.valor_unitario,
            valor_calculado=i_calc["valor_calculado"], ordem=i_req.ordem or idx,
        )

    return float(calc.subtotal), float(calc.valor_venda)


# ── Premissas (templates) ─────────────────────────────────────────────────────

@router.get("/premissas", response_model=list[PremissaResponse])
async def listar_premissas(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[PremissaResponse]:
    premissas = await PremissaRepository(db).listar(_empresa_id(usuario))
    return [PremissaResponse(
        id=UUID(p.id), nome=p.nome, descricao=p.descricao,
        tipo=p.tipo, valor=float(p.valor), ordem=p.ordem, ativo=p.ativo,
        obrigatoria=bool(p.obrigatoria),
    ) for p in premissas]


@router.post("/premissas", response_model=PremissaResponse, status_code=status.HTTP_201_CREATED)
async def criar_premissa(
    body: PremissaRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PremissaResponse:
    _exigir_admin(usuario)
    p = await PremissaRepository(db).criar(
        _empresa_id(usuario), body.nome, body.tipo, body.valor, body.ordem, body.descricao,
        obrigatoria=body.obrigatoria,
    )
    return PremissaResponse(id=UUID(p.id), nome=p.nome, descricao=p.descricao,
                            tipo=p.tipo, valor=float(p.valor), ordem=p.ordem, ativo=p.ativo,
                            obrigatoria=bool(p.obrigatoria))


@router.put("/premissas/{premissa_id}", response_model=PremissaResponse)
async def atualizar_premissa(
    premissa_id: UUID,
    body: PremissaRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PremissaResponse:
    _exigir_admin(usuario)
    repo = PremissaRepository(db)
    p = await repo.buscar_por_id(premissa_id, _empresa_id(usuario))
    if p is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Premissa não encontrada")
    p.nome = body.nome
    p.descricao = body.descricao
    p.tipo = body.tipo
    p.valor = body.valor
    p.ordem = body.ordem
    p.obrigatoria = body.obrigatoria
    await repo.salvar(p)
    return PremissaResponse(id=UUID(p.id), nome=p.nome, descricao=p.descricao,
                            tipo=p.tipo, valor=float(p.valor), ordem=p.ordem, ativo=p.ativo,
                            obrigatoria=bool(p.obrigatoria))


@router.delete("/premissas/{premissa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_premissa(
    premissa_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    _exigir_admin(usuario)
    repo = PremissaRepository(db)
    p = await repo.buscar_por_id(premissa_id, _empresa_id(usuario))
    if p is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Premissa não encontrada")
    p.ativo = False
    await repo.salvar(p)


# ── Cálculo em tempo real ─────────────────────────────────────────────────────

@router.post("/orcamentos/calcular", response_model=CalcularOrcamentoResponse)
async def calcular_orcamento(
    body: CalcularOrcamentoRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CalcularOrcamentoResponse:
    premissa_repo = PremissaRepository(db)
    empresa_id = _empresa_id(usuario)

    premissas_calc: list[PremissaCalculo] = []
    for idx, p_req in enumerate(body.premissas):
        pid, nome, desc, tipo, valor, _obrig = await _resolver_premissa(p_req, premissa_repo, empresa_id)
        premissas_calc.append(PremissaCalculo(
            id=str(idx), nome=nome, descricao=desc, tipo=tipo, valor=valor,
            ordem=p_req.ordem or idx,
        ))

    itens_calc = [ItemCalculo(
        id=str(idx), tipo=i.tipo, descricao=i.descricao,
        quantidade=i.quantidade, valor_unitario=i.valor_unitario,
        ordem=i.ordem or idx,
    ) for idx, i in enumerate(body.itens)]

    result = calcular(body.custo_base, premissas_calc, itens_calc, body.valor_venda)

    return CalcularOrcamentoResponse(
        custo_base=float(result.custo_base),
        subtotal_premissas=float(result.subtotal_premissas),
        subtotal_itens=float(result.subtotal_itens),
        subtotal=float(result.subtotal),
        valor_venda=float(result.valor_venda),
        premissas=result.premissas,
        itens=result.itens,
    )


# ── Orçamentos CRUD ───────────────────────────────────────────────────────────

@router.get("/orcamentos", response_model=list[OrcamentoResponse])
async def listar_orcamentos(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    status_filtro: str | None = Query(None, alias="status"),
) -> list[OrcamentoResponse]:
    repo = OrcamentoRepository(db)
    orcs = await repo.listar(_empresa_id(usuario), status_filtro)
    return [await _orc_to_response(o, repo) for o in orcs]


@router.post("/orcamentos", response_model=OrcamentoResponse, status_code=status.HTTP_201_CREATED)
async def criar_orcamento(
    body: OrcamentoRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrcamentoResponse:
    empresa_id = _empresa_id(usuario)
    repo = OrcamentoRepository(db)
    premissa_repo = PremissaRepository(db)

    orc = await repo.criar(
        empresa_id=empresa_id, criado_por=usuario.id, titulo=body.titulo,
        custo_base=body.custo_base, subtotal=0, valor_venda=0,
        cliente_id=body.cliente_id, vendedor_id=body.vendedor_id,
        observacoes=body.observacoes, validade_dias=body.validade_dias,
        endereco=body.endereco, email=body.email,
        telefone=body.telefone, cpf=body.cpf,
    )
    orc.campos_extras = body.campos_extras or {}

    subtotal, valor_venda = await _salvar_premissas_e_itens(
        UUID(orc.id), body.custo_base, body.valor_venda,
        body.premissas, body.itens, repo, premissa_repo, empresa_id,
    )
    orc.subtotal = subtotal
    orc.valor_venda = valor_venda
    await repo.salvar(orc)

    return await _orc_to_response(orc, repo)


@router.get("/orcamentos/{orc_id}", response_model=OrcamentoResponse)
async def obter_orcamento(
    orc_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrcamentoResponse:
    repo = OrcamentoRepository(db)
    orc = await repo.buscar_por_id(orc_id, _empresa_id(usuario))
    if orc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Orçamento não encontrado")
    return await _orc_to_response(orc, repo)


@router.put("/orcamentos/{orc_id}", response_model=OrcamentoResponse)
async def atualizar_orcamento(
    orc_id: UUID,
    body: OrcamentoRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrcamentoResponse:
    empresa_id = _empresa_id(usuario)
    repo = OrcamentoRepository(db)
    orc = await repo.buscar_por_id(orc_id, empresa_id)
    if orc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Orçamento não encontrado")

    orc.titulo = body.titulo
    orc.custo_base = body.custo_base
    orc.cliente_id = str(body.cliente_id) if body.cliente_id else None
    orc.vendedor_id = str(body.vendedor_id) if body.vendedor_id else None
    orc.observacoes = body.observacoes
    orc.validade_dias = body.validade_dias
    orc.endereco = body.endereco
    orc.email = body.email
    orc.telefone = body.telefone
    orc.cpf = body.cpf
    orc.campos_extras = body.campos_extras or {}

    await repo.deletar_premissas(orc_id)
    await repo.deletar_itens(orc_id)

    subtotal, valor_venda = await _salvar_premissas_e_itens(
        orc_id, body.custo_base, body.valor_venda,
        body.premissas, body.itens, repo, PremissaRepository(db), empresa_id,
    )
    orc.subtotal = subtotal
    orc.valor_venda = valor_venda
    await repo.salvar(orc)

    return await _orc_to_response(orc, repo)


@router.delete("/orcamentos/{orc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_orcamento(
    orc_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    repo = OrcamentoRepository(db)
    orc = await repo.buscar_por_id(orc_id, _empresa_id(usuario))
    if orc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Orçamento não encontrado")
    await repo.deletar(orc_id)


# ── Status ────────────────────────────────────────────────────────────────────

@router.patch("/orcamentos/{orc_id}/enviar", response_model=OrcamentoResponse)
async def enviar_orcamento(
    orc_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrcamentoResponse:
    repo = OrcamentoRepository(db)
    orc = await repo.buscar_por_id(orc_id, _empresa_id(usuario))
    if orc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Orçamento não encontrado")
    if orc.status not in ("rascunho",):
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Somente rascunhos podem ser enviados")
    orc.status = "enviado"
    orc.enviado_em = datetime.now(UTC)
    await repo.salvar(orc)
    return await _orc_to_response(orc, repo)


@router.patch("/orcamentos/{orc_id}/fechar", response_model=OrcamentoResponse)
async def fechar_orcamento(
    orc_id: UUID,
    body: FecharOrcamentoRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrcamentoResponse:
    repo = OrcamentoRepository(db)
    orc = await repo.buscar_por_id(orc_id, _empresa_id(usuario))
    if orc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Orçamento não encontrado")
    orc.endereco = body.endereco
    orc.email = body.email
    orc.telefone = body.telefone
    orc.cpf = body.cpf
    orc.status = "fechado"
    orc.fechado_em = datetime.now(UTC)
    await repo.salvar(orc)
    return await _orc_to_response(orc, repo)


@router.patch("/orcamentos/{orc_id}/aprovar", response_model=OrcamentoResponse)
async def aprovar_orcamento(
    orc_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrcamentoResponse:
    repo = OrcamentoRepository(db)
    orc = await repo.buscar_por_id(orc_id, _empresa_id(usuario))
    if orc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Orçamento não encontrado")
    orc.status = "aprovado"
    orc.aprovado_em = datetime.now(UTC)
    await repo.salvar(orc)

    from sqlalchemy import select
    from uuid import uuid4
    from datetime import date as _date

    # Auto-criar comissão se houver vendedor atribuído
    if orc.vendedor_id:
        from app.identity.infrastructure.orm_models import UsuarioORM
        from app.commissions.infrastructure.orm_models import ComissaoORM
        vendedor = (await db.execute(
            select(UsuarioORM).where(UsuarioORM.id == orc.vendedor_id)
        )).scalar_one_or_none()
        if vendedor and float(getattr(vendedor, 'comissao_percentual', 0) or 0) > 0:
            percentual = float(vendedor.comissao_percentual)
            valor_comissao = float(orc.valor_venda) * percentual / 100
            comissao = ComissaoORM(
                id=str(uuid4()),
                empresa_id=orc.empresa_id,
                orcamento_id=orc.id,
                orcamento_numero=orc.numero,
                vendedor_id=orc.vendedor_id,
                vendedor_nome=vendedor.nome,
                valor_venda=float(orc.valor_venda),
                percentual=percentual,
                valor_comissao=valor_comissao,
                status="pendente",
                criado_em=datetime.now(UTC),
            )
            db.add(comissao)
            await db.flush()

    # Auto-criar conta a receber com origem=orcamento (Fase 4.A)
    from app.finance.infrastructure.orm_models import ContaORM
    from app.clients.infrastructure.orm_models import ClienteORM
    cliente_nome = None
    if orc.cliente_id:
        cli = (await db.execute(
            select(ClienteORM).where(ClienteORM.id == orc.cliente_id)
        )).scalar_one_or_none()
        cliente_nome = cli.nome if cli else None
    venc = _date.fromordinal(_date.today().toordinal() + (orc.validade_dias or 30))
    conta = ContaORM(
        id=str(uuid4()), empresa_id=orc.empresa_id, tipo="receber",
        descricao=f"Orçamento {orc.numero} — {orc.titulo}",
        parceiro=cliente_nome,
        valor=float(orc.valor_venda),
        data_vencimento=venc,
        status="pendente",
        orcamento_id=orc.id,
        cliente_id=orc.cliente_id,
        observacoes=f"Auto-criada pela aprovação do orçamento {orc.numero}",
        origem="orcamento",
        criado_por=str(usuario.id), criado_em=datetime.now(UTC),
    )
    db.add(conta)
    await db.flush()

    return await _orc_to_response(orc, repo)


@router.patch("/orcamentos/{orc_id}/reprovar", response_model=OrcamentoResponse)
async def reprovar_orcamento(
    orc_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrcamentoResponse:
    repo = OrcamentoRepository(db)
    orc = await repo.buscar_por_id(orc_id, _empresa_id(usuario))
    if orc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Orçamento não encontrado")
    orc.status = "reprovado"
    await repo.salvar(orc)
    return await _orc_to_response(orc, repo)


# ── PDF ───────────────────────────────────────────────────────────────────────

@router.get("/orcamentos/{orc_id}/pdf")
async def gerar_pdf(
    orc_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    from sqlalchemy import select
    from app.identity.infrastructure.orm_models import UsuarioORM
    from app.clients.infrastructure.orm_models import ClienteORM
    from app.quotes.application.pdf_service import gerar_pdf_orcamento
    from app.identity.infrastructure.orm_models import EmpresaORM

    empresa_id = _empresa_id(usuario)
    repo = OrcamentoRepository(db)
    orc = await repo.buscar_por_id(orc_id, empresa_id)
    if orc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Orçamento não encontrado")

    premissas = await repo.listar_premissas(orc_id)
    itens = await repo.listar_itens(orc_id)

    empresa = (await db.execute(select(EmpresaORM).where(EmpresaORM.id == str(empresa_id)))).scalar_one_or_none()
    cliente_nome = ""
    if orc.cliente_id:
        cliente = (await db.execute(select(ClienteORM).where(ClienteORM.id == orc.cliente_id))).scalar_one_or_none()
        if cliente:
            cliente_nome = cliente.nome
    vendedor_nome = ""
    if orc.vendedor_id:
        vendedor = (await db.execute(select(UsuarioORM).where(UsuarioORM.id == orc.vendedor_id))).scalar_one_or_none()
        if vendedor:
            vendedor_nome = vendedor.nome

    pdf_bytes = gerar_pdf_orcamento(
        orc=orc, premissas=premissas, itens=itens,
        empresa_nome=empresa.nome if empresa else "",
        cliente_nome=cliente_nome,
        vendedor_nome=vendedor_nome,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="orcamento-{orc.numero}.pdf"'},
    )


# ── Variáveis personalizadas de orçamento ─────────────────────────────────────

class VariavelRequest(BaseModel):
    chave: str
    label: str
    grupo: str = "Personalizado"


class VariavelResponse(BaseModel):
    id: str
    chave: str
    label: str
    grupo: str
    sistema: bool = False


@router.get("/orcamentos/variaveis")
async def listar_variaveis(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    from sqlalchemy import select
    eid = str(_empresa_id(usuario))
    result = await db.execute(
        select(VariavelOrcamentoORM).where(VariavelOrcamentoORM.empresa_id == eid)
    )
    custom = result.scalars().all()
    return {
        "sistema": VARIAVEIS_SISTEMA,
        "personalizadas": [
            {"id": v.id, "chave": v.chave, "label": v.label, "grupo": v.grupo}
            for v in custom
        ],
    }


@router.post("/orcamentos/variaveis", status_code=status.HTTP_201_CREATED)
async def criar_variavel(
    body: VariavelRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VariavelResponse:
    import re
    from datetime import UTC, datetime
    from sqlalchemy.exc import IntegrityError
    chave = re.sub(r'[^a-z0-9_]', '_', body.chave.lower().strip())
    if not chave:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Chave inválida")
    eid = str(_empresa_id(usuario))
    nova = VariavelOrcamentoORM(
        id=str(__import__('uuid').uuid4()),
        empresa_id=eid,
        chave=chave,
        label=body.label.strip(),
        grupo=body.grupo.strip() or "Personalizado",
        criado_em=datetime.now(UTC),
    )
    db.add(nova)
    try:
        await db.flush()
    except IntegrityError:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Já existe uma variável com essa chave")
    return VariavelResponse(id=nova.id, chave=nova.chave, label=nova.label, grupo=nova.grupo)


@router.put("/orcamentos/variaveis/{var_id}", response_model=VariavelResponse)
async def atualizar_variavel(
    var_id: str,
    body: VariavelRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VariavelResponse:
    from sqlalchemy import select
    eid = str(_empresa_id(usuario))
    result = await db.execute(
        select(VariavelOrcamentoORM).where(
            VariavelOrcamentoORM.id == var_id,
            VariavelOrcamentoORM.empresa_id == eid,
        )
    )
    v = result.scalar_one_or_none()
    if v is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    v.label = body.label.strip()
    v.grupo = body.grupo.strip() or "Personalizado"
    await db.flush()
    return VariavelResponse(id=v.id, chave=v.chave, label=v.label, grupo=v.grupo)


@router.delete("/orcamentos/variaveis/{var_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_variavel(
    var_id: str,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    from sqlalchemy import select
    eid = str(_empresa_id(usuario))
    result = await db.execute(
        select(VariavelOrcamentoORM).where(
            VariavelOrcamentoORM.id == var_id,
            VariavelOrcamentoORM.empresa_id == eid,
        )
    )
    v = result.scalar_one_or_none()
    if v is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    await db.delete(v)


# ── DOCX Template ─────────────────────────────────────────────────────────────

@router.get("/orcamentos/template/exemplo")
async def baixar_template_exemplo(usuario: UsuarioAtualDep) -> Response:
    """Baixa um template .docx de proposta comercial com todas as variáveis pré-inseridas."""
    from app.quotes.application.template_docx_service import gerar_template_docx
    docx_bytes = gerar_template_docx()
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": 'attachment; filename="modelo-proposta-comercial.docx"'},
    )


@router.post("/orcamentos/template", status_code=status.HTTP_204_NO_CONTENT)
async def upload_template(
    usuario: UsuarioAtualDep,
    file: UploadFile = File(...),
) -> None:
    """Salva um template .docx para a empresa. Variáveis: {{NUMERO}}, {{TITULO}}, {{CLIENTE}},
    {{VENDEDOR}}, {{DATA}}, {{VALIDADE}}, {{CUSTO_BASE}}, {{VALOR_VENDA}}, {{OBSERVACOES}},
    {{PREMISSAS_TABELA}} (lista de premissas), {{ITENS_TABELA}} (lista de itens)."""
    from pathlib import Path
    empresa_id = _empresa_id(usuario)
    templates_dir = Path("/app/templates")
    templates_dir.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    (templates_dir / f"{empresa_id}.docx").write_bytes(content)


@router.get("/orcamentos/{orc_id}/docx")
async def gerar_docx(
    orc_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    from pathlib import Path
    from sqlalchemy import select
    from app.identity.infrastructure.orm_models import UsuarioORM, EmpresaORM
    from app.clients.infrastructure.orm_models import ClienteORM
    from docxtpl import DocxTemplate
    import io, zipfile

    empresa_id = _empresa_id(usuario)
    template_path = Path(f"/app/templates/{empresa_id}.docx")
    if not template_path.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Nenhum template encontrado. Faça upload de um arquivo .docx primeiro.")

    repo = OrcamentoRepository(db)
    orc = await repo.buscar_por_id(orc_id, empresa_id)
    if orc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Orçamento não encontrado")

    premissas = await repo.listar_premissas(orc_id)
    itens = await repo.listar_itens(orc_id)

    # Dados da empresa
    empresa = (await db.execute(select(EmpresaORM).where(EmpresaORM.id == str(empresa_id)))).scalar_one_or_none()
    empresa_nome = empresa.nome if empresa else ""
    empresa_cnpj = getattr(empresa, 'cnpj', '') or ""

    # Dados do cliente
    cliente_nome = cliente_cnpj = cliente_email = cliente_tel = ""
    cliente_endereco = cliente_bairro = cliente_cidade = cliente_estado = ""
    if orc.cliente_id:
        cli = (await db.execute(select(ClienteORM).where(ClienteORM.id == orc.cliente_id))).scalar_one_or_none()
        if cli:
            cliente_nome = cli.nome or ""
            cliente_cnpj = cli.cpf_cnpj or ""
            cliente_email = cli.email or ""
            cliente_tel = cli.telefone or ""
            cliente_endereco = cli.endereco or ""
            cliente_bairro = getattr(cli, 'bairro', '') or ""
            cliente_cidade = getattr(cli, 'cidade', '') or ""
            cliente_estado = getattr(cli, 'estado', '') or ""

    # Dados do vendedor
    vendedor_nome = vendedor_celular = ""
    if orc.vendedor_id:
        vend = (await db.execute(select(UsuarioORM).where(UsuarioORM.id == orc.vendedor_id))).scalar_one_or_none()
        if vend:
            vendedor_nome = vend.nome or ""

    # Campos extras (solar e customizados)
    extras: dict = orc.campos_extras or {}

    def _fmt(v: float) -> str:
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _s(key: str, default: str = "") -> str:
        return str(extras.get(key, default)) if extras.get(key) is not None else default

    # Contexto completo para {{ }} (docxtpl)
    context = {
        # Identificação
        "NUMERO": orc.numero,
        "TITULO": orc.titulo,
        "STATUS": orc.status.capitalize(),
        "DATA": orc.criado_em.strftime("%d/%m/%Y") if orc.criado_em else "",
        "VALIDADE": str(orc.validade_dias),
        # Empresa
        "EMPRESA": empresa_nome,
        "EMPRESA_CNPJ": empresa_cnpj,
        # Cliente
        "CLIENTE": cliente_nome or orc.email or "",
        "CLIENTE_CNPJ": cliente_cnpj or orc.cpf or "",
        "CLIENTE_EMAIL": cliente_email or orc.email or "",
        "CLIENTE_TELEFONE": cliente_tel or orc.telefone or "",
        "CLIENTE_ENDERECO": cliente_endereco or orc.endereco or "",
        "CLIENTE_BAIRRO": cliente_bairro,
        "CLIENTE_CIDADE": cliente_cidade,
        "CLIENTE_ESTADO": cliente_estado,
        # Vendedor
        "VENDEDOR": vendedor_nome,
        "VENDEDOR_CELULAR": vendedor_celular,
        # Compat legado (campos do orçamento)
        "EMAIL": orc.email or cliente_email,
        "TELEFONE": orc.telefone or cliente_tel,
        "ENDERECO": orc.endereco or cliente_endereco,
        "CPF": orc.cpf or cliente_cnpj,
        # Financeiro padrão
        "CUSTO_BASE": _fmt(float(orc.custo_base)),
        "SUBTOTAL": _fmt(float(orc.subtotal)),
        "VALOR_VENDA": _fmt(float(orc.valor_venda)),
        "PRECO": _fmt(float(orc.valor_venda)),
        "OBSERVACOES": orc.observacoes or "",
        # Listas
        "PREMISSAS": [
            {"NOME": p.nome, "TIPO": p.tipo,
             "VALOR": f"{float(p.valor):.2f}", "CALCULADO": _fmt(float(p.valor_calculado))}
            for p in premissas
        ],
        "ITENS": [
            {"DESCRICAO": i.descricao,
             "QUANTIDADE": f"{float(i.quantidade):.3f}" if i.quantidade else "",
             "VALOR": _fmt(float(i.valor_calculado))}
            for i in itens
        ],
        # Dimensionamento Solar
        "POTENCIA_SISTEMA": _s("potencia_sistema"),
        "GERACAO_MENSAL": _s("geracao_mensal"),
        "CONSUMO_MENSAL": _s("consumo_mensal"),
        "AREA_UTIL": _s("area_util"),
        # Módulo
        "MODULO_FABRICANTE": _s("modulo_fabricante"),
        "MODULO_MODELO": _s("modulo_modelo"),
        "MODULO_POTENCIA": _s("modulo_potencia"),
        "MODULO_QUANTIDADE": _s("modulo_quantidade"),
        "VC_MODULO_EFICIENCIA": _s("vc_modulo_eficiencia"),
        # Inversor
        "INVERSOR_FABRICANTE": _s("inversor_fabricante"),
        "INVERSOR_POTENCIA": _s("inversor_potencia"),
        "INVERSOR_POTENCIA_NOMINAL": _s("inversor_potencia_nominal"),
        "INVERSORES_UTILIZADOS": _s("inversores_utilizados"),
        # Análise financeira
        "ECONOMIA_MENSAL": _s("economia_mensal"),
        "ECONOMIA_PERCENTUAL": _s("economia_mensal_p"),
        "VC_ANUAL_ATUAL": _s("vc_anual_atual"),
        "VC_ANUAL_NOVO": _s("vc_anual_novo"),
        "VC_ECONOMIA_ANUAL": _s("vc_economia_anual"),
        "VC_SERVICO": _s("vc_servico"),
        "INFLACAO_ENERGETICA": _s("inflacao_energetica"),
        "PERDA_EFICIENCIA_ANUAL": _s("perda_eficiencia_anual"),
        "GASTO_TOTAL_MENSAL_ATUAL": _s("gasto_total_mensal_atual"),
        "GASTO_TOTAL_MENSAL_NOVO": _s("gasto_total_mensal_novo"),
        # Financeiro extra
        "CAPO_BANCARIO": _s("capo_bancario"),
        # Complemento de endereço
        "CLIENTE_COMPLEMENTO": _s("cliente_complemento"),
    }

    # Injetar variáveis personalizadas da empresa no contexto
    _vars_result = await db.execute(
        select(VariavelOrcamentoORM).where(VariavelOrcamentoORM.empresa_id == str(empresa_id))
    )
    for _var in _vars_result.scalars():
        _key = _var.chave.upper()
        if _key not in context:
            context[_key] = _s(_var.chave)

    # Mapeamento [bracket] → valor (compatível com template legado)
    bracket_map: dict[str, str] = {
        "[proposta_identificador]": context["NUMERO"],
        "[cliente_nome]": context["CLIENTE"],
        "[cliente_cnpj_cpf]": context["CLIENTE_CNPJ"],
        "[cliente_endereco]": context["CLIENTE_ENDERECO"],
        "[cliente_bairro]": context["CLIENTE_BAIRRO"],
        "[cliente_cidade]": context["CLIENTE_CIDADE"],
        "[cliente_estado]": context["CLIENTE_ESTADO"],
        "[cliente_complemento]": context["CLIENTE_COMPLEMENTO"],
        "[consumo_mensal]": context["CONSUMO_MENSAL"],
        "[economia_mensal]": context["ECONOMIA_MENSAL"],
        "[economia_mensal_p]": context["ECONOMIA_PERCENTUAL"],
        "[geracao_mensal]": context["GERACAO_MENSAL"],
        "[potencia_sistema]": context["POTENCIA_SISTEMA"],
        "[modulo_potencia]": context["MODULO_POTENCIA"],
        "[modulo_quantidade]": context["MODULO_QUANTIDADE"],
        "[modulo_modelo]": context["MODULO_MODELO"],
        "[modulo_fabricante]": context["MODULO_FABRICANTE"],
        "[area_util]": context["AREA_UTIL"],
        "[cap_vendedorresp]": context["VENDEDOR"],
        "[representante_celular]": context["VENDEDOR_CELULAR"],
        "[inversor_fabricante]": context["INVERSOR_FABRICANTE"],
        "[inversor_potencia]": context["INVERSOR_POTENCIA"],
        "[inversor_potencia_nominal]": context["INVERSOR_POTENCIA_NOMINAL"],
        "[inversores_utilizados]": context["INVERSORES_UTILIZADOS"],
        "[vc_servico]": context["VC_SERVICO"],
        "[preco]": context["PRECO"],
        "[vc_anual_atual]": context["VC_ANUAL_ATUAL"],
        "[vc_anual_novo]": context["VC_ANUAL_NOVO"],
        "[vc_economia_anual]": context["VC_ECONOMIA_ANUAL"],
        "[vc_modulo_eficiencia]": context["VC_MODULO_EFICIENCIA"],
        "[inflacao_energetica]": context["INFLACAO_ENERGETICA"],
        "[perda_eficiencia_anual]": context["PERDA_EFICIENCIA_ANUAL"],
        "[gasto_total_mensal_atual]": context["GASTO_TOTAL_MENSAL_ATUAL"],
        "[gasto_total_mensal_novo]": context["GASTO_TOTAL_MENSAL_NOVO"],
        "[capo_bancario]": context["CAPO_BANCARIO"],
    }

    # Adicionar variáveis personalizadas ao bracket_map
    for _key_upper, _val in context.items():
        _bracket_key = f"[{_key_upper.lower()}]"
        if _bracket_key not in bracket_map and isinstance(_val, str):
            bracket_map[_bracket_key] = _val

    # Render com docxtpl ({{ }})
    doc = DocxTemplate(str(template_path))
    doc.render(context)
    buf = io.BytesIO()
    doc.save(buf)

    # Substituição dos [bracket] no XML do DOCX gerado
    def _replace_brackets(docx_bytes: bytes, replacements: dict[str, str]) -> bytes:
        inp = io.BytesIO(docx_bytes)
        out = io.BytesIO()
        with zipfile.ZipFile(inp) as zin, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename.endswith(".xml"):
                    text = data.decode("utf-8", errors="replace")
                    for k, v in replacements.items():
                        text = text.replace(k, v)
                    data = text.encode("utf-8")
                zout.writestr(item, data)
        return out.getvalue()

    final_bytes = _replace_brackets(buf.getvalue(), bracket_map)

    return Response(
        content=final_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="orcamento-{orc.numero}.docx"'},
    )


# ── Gerenciar premissas/itens individualmente ─────────────────────────────────

@router.post("/orcamentos/{orc_id}/premissas", response_model=PremissaOrcamentoResponse, status_code=status.HTTP_201_CREATED)
async def adicionar_premissa(
    orc_id: UUID,
    body: PremissaOrcamentoRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PremissaOrcamentoResponse:
    empresa_id = _empresa_id(usuario)
    repo = OrcamentoRepository(db)
    orc = await repo.buscar_por_id(orc_id, empresa_id)
    if orc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Orçamento não encontrado")

    # Bloquear premissa duplicada
    if body.premissa_id:
        existentes = await repo.listar_premissas(orc_id)
        ids_existentes = {p.premissa_id for p in existentes if p.premissa_id}
        if str(body.premissa_id) in ids_existentes:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail="Esta premissa já foi adicionada ao orçamento",
            )

    pid, nome, desc, tipo, valor, obrig = await _resolver_premissa(body, PremissaRepository(db), empresa_id)
    from app.quotes.application.calculator import PremissaCalculo, calcular
    p_calc = PremissaCalculo(id="0", nome=nome, descricao=desc, tipo=tipo, valor=valor, ordem=0)
    result = calcular(float(orc.custo_base), [p_calc], [], None)
    vc = result.premissas[0]["valor_calculado"]

    existentes = await repo.listar_premissas(orc_id)
    orm = await repo.criar_premissa(
        orc_id, pid, nome, desc, tipo, valor, vc,
        body.ordem or len(existentes), obrigatoria=obrig,
    )
    return _premissa_to_response(orm)


@router.delete("/orcamentos/{orc_id}/premissas/{premissa_orc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_premissa(
    orc_id: UUID,
    premissa_orc_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    repo = OrcamentoRepository(db)
    orc = await repo.buscar_por_id(orc_id, _empresa_id(usuario))
    if orc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Orçamento não encontrado")
    aplicadas = await repo.listar_premissas(orc_id)
    alvo = next((p for p in aplicadas if p.id == str(premissa_orc_id)), None)
    if alvo is not None and bool(getattr(alvo, "obrigatoria", False)):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Premissa obrigatória não pode ser removida",
        )
    await repo.deletar_premissa(premissa_orc_id)


@router.post("/orcamentos/{orc_id}/itens", response_model=ItemOrcamentoResponse, status_code=status.HTTP_201_CREATED)
async def adicionar_item(
    orc_id: UUID,
    body: ItemOrcamentoRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ItemOrcamentoResponse:
    repo = OrcamentoRepository(db)
    orc = await repo.buscar_por_id(orc_id, _empresa_id(usuario))
    if orc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Orçamento não encontrado")
    existentes = await repo.listar_itens(orc_id)
    from app.quotes.application.calculator import ItemCalculo, calcular
    i_calc = ItemCalculo(id="0", tipo=body.tipo, descricao=body.descricao,
                         quantidade=body.quantidade, valor_unitario=body.valor_unitario, ordem=0)
    result = calcular(float(orc.custo_base), [], [i_calc], None)
    vc = result.itens[0]["valor_calculado"]
    orm = await repo.criar_item(
        orcamento_id=orc_id, tipo=body.tipo, descricao=body.descricao,
        item_estoque_id=body.item_estoque_id,
        quantidade=body.quantidade, valor_unitario=body.valor_unitario,
        valor_calculado=vc, ordem=body.ordem or len(existentes),
    )
    return _item_to_response(orm)


@router.delete("/orcamentos/{orc_id}/itens/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_item(
    orc_id: UUID,
    item_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    repo = OrcamentoRepository(db)
    orc = await repo.buscar_por_id(orc_id, _empresa_id(usuario))
    if orc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Orçamento não encontrado")
    item = await repo.buscar_item(item_id, _empresa_id(usuario))
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Item não encontrado")
    await repo.deletar_item(item_id)
