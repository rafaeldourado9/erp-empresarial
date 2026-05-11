from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.identity.api.deps import UsuarioAtualDep
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

router = APIRouter(tags=["orcamentos"])


def _empresa_id(usuario: UsuarioAtualDep) -> UUID:
    if usuario.empresa_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Selecione uma empresa")
    return usuario.empresa_id


# ── Helpers ───────────────────────────────────────────────────────────────────

def _premissa_to_response(p: object) -> PremissaOrcamentoResponse:
    return PremissaOrcamentoResponse(
        id=UUID(p.id),
        premissa_id=UUID(p.premissa_id) if p.premissa_id else None,
        nome=p.nome, descricao=p.descricao, tipo=p.tipo,
        valor=float(p.valor), valor_calculado=float(p.valor_calculado),
        ordem=p.ordem,
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
        premissas=[_premissa_to_response(p) for p in premissas],
        itens=[_item_to_response(i) for i in itens],
    )


async def _resolver_premissa(
    req: PremissaOrcamentoRequest,
    premissa_repo: PremissaRepository,
    empresa_id: UUID,
) -> tuple[UUID | None, str, str | None, str, float]:
    if req.premissa_id:
        template = await premissa_repo.buscar_por_id(req.premissa_id, empresa_id)
        if template is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Premissa {req.premissa_id} não encontrada")
        return req.premissa_id, template.nome, template.descricao, template.tipo, float(template.valor)
    if not req.nome or not req.tipo or req.valor is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Informe premissa_id ou (nome, tipo, valor)")
    return None, req.nome, req.descricao, req.tipo, req.valor


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

    premissas_calc: list[PremissaCalculo] = []
    premissas_resolvidas = []
    for idx, p_req in enumerate(premissas_req):
        pid, nome, desc, tipo, valor = await _resolver_premissa(p_req, premissa_repo, empresa_id)
        premissas_calc.append(PremissaCalculo(
            id=str(idx), nome=nome, descricao=desc, tipo=tipo, valor=valor,
            ordem=p_req.ordem or idx,
        ))
        premissas_resolvidas.append((pid, nome, desc, tipo, valor, p_req.ordem or idx))

    itens_calc: list[ItemCalculo] = []
    for idx, i_req in enumerate(itens_req):
        itens_calc.append(ItemCalculo(
            id=str(idx), tipo=i_req.tipo, descricao=i_req.descricao,
            quantidade=i_req.quantidade, valor_unitario=i_req.valor_unitario,
            ordem=i_req.ordem or idx,
        ))

    calc = calcular(custo_base, premissas_calc, itens_calc, valor_venda)

    for idx, (pid, nome, desc, tipo, valor, ordem) in enumerate(premissas_resolvidas):
        vc = calc.premissas[idx]["valor_calculado"]
        await repo.criar_premissa(orc_id, pid, nome, desc, tipo, valor, vc, ordem)

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
    ) for p in premissas]


@router.post("/premissas", response_model=PremissaResponse, status_code=status.HTTP_201_CREATED)
async def criar_premissa(
    body: PremissaRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PremissaResponse:
    p = await PremissaRepository(db).criar(
        _empresa_id(usuario), body.nome, body.tipo, body.valor, body.ordem, body.descricao,
    )
    return PremissaResponse(id=UUID(p.id), nome=p.nome, descricao=p.descricao,
                            tipo=p.tipo, valor=float(p.valor), ordem=p.ordem, ativo=p.ativo)


@router.put("/premissas/{premissa_id}", response_model=PremissaResponse)
async def atualizar_premissa(
    premissa_id: UUID,
    body: PremissaRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PremissaResponse:
    repo = PremissaRepository(db)
    p = await repo.buscar_por_id(premissa_id, _empresa_id(usuario))
    if p is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Premissa não encontrada")
    p.nome = body.nome
    p.descricao = body.descricao
    p.tipo = body.tipo
    p.valor = body.valor
    p.ordem = body.ordem
    await repo.salvar(p)
    return PremissaResponse(id=UUID(p.id), nome=p.nome, descricao=p.descricao,
                            tipo=p.tipo, valor=float(p.valor), ordem=p.ordem, ativo=p.ativo)


@router.delete("/premissas/{premissa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_premissa(
    premissa_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
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
        pid, nome, desc, tipo, valor = await _resolver_premissa(p_req, premissa_repo, empresa_id)
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

    # Auto-criar comissão se houver vendedor atribuído
    if orc.vendedor_id:
        from sqlalchemy import select
        from app.identity.infrastructure.orm_models import UsuarioORM
        from app.commissions.infrastructure.orm_models import ComissaoORM
        from uuid import uuid4
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


# ── DOCX Template ─────────────────────────────────────────────────────────────

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
    from app.identity.infrastructure.orm_models import UsuarioORM
    from app.clients.infrastructure.orm_models import ClienteORM

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

    from docxtpl import DocxTemplate
    import io

    def _fmt(v: float) -> str:
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    doc = DocxTemplate(str(template_path))
    context = {
        "NUMERO": orc.numero,
        "TITULO": orc.titulo,
        "CLIENTE": cliente_nome,
        "VENDEDOR": vendedor_nome,
        "DATA": orc.criado_em.strftime("%d/%m/%Y") if orc.criado_em else "",
        "VALIDADE": f"{orc.validade_dias} dias",
        "CUSTO_BASE": _fmt(float(orc.custo_base)),
        "SUBTOTAL": _fmt(float(orc.subtotal)),
        "VALOR_VENDA": _fmt(float(orc.valor_venda)),
        "OBSERVACOES": orc.observacoes or "",
        "EMAIL": orc.email or "",
        "TELEFONE": orc.telefone or "",
        "ENDERECO": orc.endereco or "",
        "STATUS": orc.status.capitalize(),
        "PREMISSAS": [
            {"NOME": p.nome, "TIPO": p.tipo, "VALOR": f"{float(p.valor):.2f}", "CALCULADO": _fmt(float(p.valor_calculado))}
            for p in premissas
        ],
        "ITENS": [
            {"DESCRICAO": i.descricao, "QUANTIDADE": f"{float(i.quantidade):.3f}" if i.quantidade else "", "VALOR": _fmt(float(i.valor_calculado))}
            for i in itens
        ],
    }
    doc.render(context)
    buf = io.BytesIO()
    doc.save(buf)

    return Response(
        content=buf.getvalue(),
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

    pid, nome, desc, tipo, valor = await _resolver_premissa(body, PremissaRepository(db), empresa_id)
    from app.quotes.application.calculator import PremissaCalculo, calcular
    p_calc = PremissaCalculo(id="0", nome=nome, descricao=desc, tipo=tipo, valor=valor, ordem=0)
    result = calcular(float(orc.custo_base), [p_calc], [], None)
    vc = result.premissas[0]["valor_calculado"]

    existentes = await repo.listar_premissas(orc_id)
    orm = await repo.criar_premissa(orc_id, pid, nome, desc, tipo, valor, vc, body.ordem or len(existentes))
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
