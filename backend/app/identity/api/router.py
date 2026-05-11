from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.identity.api.deps import UsuarioAtualDep
from app.identity.api.schemas import (
    CriarEmpresaRequest, CriarUsuarioRequest, EmpresaResponse,
    LoginRequest, RefreshRequest, RegistroGrupoRequest, RegistroResponse,
    TokenResponse, UsuarioResponse,
)
from app.identity.application.auth_service import AuthService
from app.identity.domain.constants import Permissao, PerfilUsuario
from app.identity.domain.exceptions import CredenciaisInvalidasError, TokenInvalidoError, UsuarioInativoError
from app.identity.domain.models import Empresa, Grupo, Usuario
from app.identity.infrastructure.repository import EmpresaRepository, GrupoRepository, UsuarioRepository
from app.infrastructure.database import get_db

router = APIRouter(tags=["identity"])


def _auth_service(db: AsyncSession) -> AuthService:
    return AuthService(usuario_repo=UsuarioRepository(db))


# ── Auth ──────────────────────────────────────────────────────────────────────

@router.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: Annotated[AsyncSession, Depends(get_db)]) -> TokenResponse:
    try:
        tokens = await _auth_service(db).login(email=str(body.email), senha=body.senha)
    except (CredenciaisInvalidasError, UsuarioInativoError) as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return TokenResponse(access_token=tokens.access_token, refresh_token=tokens.refresh_token)


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: Annotated[AsyncSession, Depends(get_db)]) -> TokenResponse:
    try:
        tokens = await _auth_service(db).refresh(body.refresh_token)
    except (TokenInvalidoError, UsuarioInativoError) as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token inválido") from exc
    return TokenResponse(access_token=tokens.access_token, refresh_token=tokens.refresh_token)


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout() -> None:
    return None


@router.post("/auth/registro", response_model=RegistroResponse, status_code=status.HTTP_201_CREATED)
async def registro(body: RegistroGrupoRequest, db: Annotated[AsyncSession, Depends(get_db)]) -> RegistroResponse:
    grupo_repo = GrupoRepository(db)
    empresa_repo = EmpresaRepository(db)
    usuario_repo = UsuarioRepository(db)

    if await usuario_repo.buscar_por_email(str(body.email)):
        raise HTTPException(status.HTTP_409_CONFLICT, detail="E-mail já cadastrado")

    grupo = Grupo.criar(nome=body.nome_grupo)
    await grupo_repo.salvar(grupo)

    empresa = Empresa.criar(grupo_id=grupo.id, nome=body.nome_empresa)
    await empresa_repo.salvar(empresa)

    admin = Usuario.criar(
        grupo_id=grupo.id,
        nome=body.nome_admin,
        email=str(body.email),
        senha_plaintext=body.senha,
        perfil=PerfilUsuario.ADMIN_GRUPO,
        permissoes=list(Permissao),
        empresa_id=empresa.id,
    )
    await usuario_repo.salvar(admin)

    tokens = await _auth_service(db).login(email=str(body.email), senha=body.senha)
    return RegistroResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        grupo_id=str(grupo.id),
        empresa_id=str(empresa.id),
        mensagem=f"Bem-vindo, {body.nome_admin}!",
    )


@router.get("/auth/me", response_model=UsuarioResponse)
async def me(usuario: UsuarioAtualDep) -> UsuarioResponse:
    return UsuarioResponse(
        id=usuario.id,
        nome=usuario.nome,
        email=usuario.email,
        perfil=usuario.perfil.value,
        empresa_id=usuario.empresa_id,
        grupo_id=usuario.grupo_id,
        ativo=usuario.ativo,
        permissoes=[p.value for p in usuario.permissoes],
    )


# ── Empresas ─────────────────────────────────────────────────────────────────

@router.get("/empresas", response_model=list[EmpresaResponse])
async def listar_empresas(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[EmpresaResponse]:
    empresas = await EmpresaRepository(db).listar_por_grupo(usuario.grupo_id)
    return [EmpresaResponse(
        id=e.id, nome=e.nome, cnpj=e.cnpj, logo_url=e.logo_url,
        cor_primaria=e.cor_primaria, ativa=e.ativa,
    ) for e in empresas]


@router.post("/empresas", response_model=EmpresaResponse, status_code=status.HTTP_201_CREATED)
async def criar_empresa(
    body: CriarEmpresaRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EmpresaResponse:
    if usuario.perfil != PerfilUsuario.ADMIN_GRUPO:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Apenas admin do grupo pode criar empresas")
    empresa = Empresa.criar(grupo_id=usuario.grupo_id, nome=body.nome, cnpj=body.cnpj, cor_primaria=body.cor_primaria)
    await EmpresaRepository(db).salvar(empresa)
    return EmpresaResponse(id=empresa.id, nome=empresa.nome, cnpj=empresa.cnpj, logo_url=empresa.logo_url, cor_primaria=empresa.cor_primaria, ativa=empresa.ativa)


# ── Usuários/Operadores ───────────────────────────────────────────────────────

@router.get("/operadores", response_model=list[UsuarioResponse])
async def listar_operadores(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[UsuarioResponse]:
    repo = UsuarioRepository(db)
    usuarios = await repo.listar_por_grupo(usuario.grupo_id)
    return [UsuarioResponse(
        id=u.id, nome=u.nome, email=u.email, perfil=u.perfil.value,
        empresa_id=u.empresa_id, grupo_id=u.grupo_id, ativo=u.ativo,
        permissoes=[p.value for p in u.permissoes],
    ) for u in usuarios]


@router.post("/operadores", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def criar_operador(
    body: CriarUsuarioRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UsuarioResponse:
    if not usuario.tem_permissao(Permissao.GERENCIAR_USUARIOS):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente")
    repo = UsuarioRepository(db)
    if await repo.buscar_por_email(str(body.email)):
        raise HTTPException(status.HTTP_409_CONFLICT, detail="E-mail já cadastrado")
    novo = Usuario.criar(
        grupo_id=usuario.grupo_id,
        nome=body.nome,
        email=str(body.email),
        senha_plaintext=body.senha,
        perfil=PerfilUsuario(body.perfil),
        permissoes=[Permissao(p) for p in body.permissoes],
        empresa_id=body.empresa_id,
    )
    await repo.salvar(novo)
    return UsuarioResponse(id=novo.id, nome=novo.nome, email=novo.email, perfil=novo.perfil.value, empresa_id=novo.empresa_id, grupo_id=novo.grupo_id, ativo=novo.ativo, permissoes=[p.value for p in novo.permissoes])


@router.put("/operadores/{operador_id}", response_model=UsuarioResponse)
async def atualizar_operador(
    operador_id: UUID,
    body: CriarUsuarioRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UsuarioResponse:
    if not usuario.tem_permissao(Permissao.GERENCIAR_USUARIOS):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente")
    repo = UsuarioRepository(db)
    op = await repo.buscar_por_id(operador_id)
    if op is None or op.grupo_id != usuario.grupo_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    op.nome = body.nome
    op.perfil = PerfilUsuario(body.perfil)
    await repo.salvar(op)
    return UsuarioResponse(id=op.id, nome=op.nome, email=op.email, perfil=op.perfil.value, empresa_id=op.empresa_id, grupo_id=op.grupo_id, ativo=op.ativo, permissoes=[p.value for p in op.permissoes])


@router.post("/operadores/{operador_id}/toggle", response_model=UsuarioResponse)
async def toggle_operador(
    operador_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UsuarioResponse:
    if not usuario.tem_permissao(Permissao.GERENCIAR_USUARIOS):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente")
    repo = UsuarioRepository(db)
    op = await repo.buscar_por_id(operador_id)
    if op is None or op.grupo_id != usuario.grupo_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    op.ativo = not op.ativo
    await repo.salvar(op)
    return UsuarioResponse(id=op.id, nome=op.nome, email=op.email, perfil=op.perfil.value, empresa_id=op.empresa_id, grupo_id=op.grupo_id, ativo=op.ativo, permissoes=[p.value for p in op.permissoes])


class RedefinirSenhaRequest(BaseModel):
    nova_senha: str


@router.post("/operadores/{operador_id}/senha", status_code=status.HTTP_204_NO_CONTENT)
async def redefinir_senha_operador(
    operador_id: UUID,
    body: RedefinirSenhaRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    if not usuario.tem_permissao(Permissao.GERENCIAR_USUARIOS):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente")
    repo = UsuarioRepository(db)
    op = await repo.buscar_por_id(operador_id)
    if op is None or op.grupo_id != usuario.grupo_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    import bcrypt
    op.senha_hash = bcrypt.hashpw(body.nova_senha.encode(), bcrypt.gensalt()).decode()
    await repo.salvar(op)


# ── Configuração da Empresa ──────────────────────────────────────────────────

class EmpresaConfigRequest(BaseModel):
    nome_fantasia: str | None = None
    razao_social: str | None = None
    cnpj: str | None = None
    telefone: str | None = None
    email: str | None = None
    endereco: str | None = None
    logo_url: str | None = None
    cor_primaria: str | None = None


class EmpresaConfigResponse(BaseModel):
    id: UUID
    nome: str
    nome_fantasia: str | None
    razao_social: str | None
    cnpj: str | None
    telefone: str | None
    email: str | None
    endereco: str | None
    logo_url: str | None
    cor_primaria: str


@router.get("/empresa/config", response_model=EmpresaConfigResponse)
async def get_empresa_config(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EmpresaConfigResponse:
    if usuario.empresa_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Selecione uma empresa")
    empresa = await EmpresaRepository(db).buscar_por_id(usuario.empresa_id)
    if empresa is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return EmpresaConfigResponse(
        id=empresa.id, nome=empresa.nome,
        nome_fantasia=getattr(empresa, 'nome_fantasia', None),
        razao_social=getattr(empresa, 'razao_social', None),
        cnpj=empresa.cnpj,
        telefone=getattr(empresa, 'telefone', None),
        email=getattr(empresa, 'email', None),
        endereco=getattr(empresa, 'endereco', None),
        logo_url=empresa.logo_url,
        cor_primaria=empresa.cor_primaria,
    )


@router.put("/empresa/config", response_model=EmpresaConfigResponse)
async def update_empresa_config(
    body: EmpresaConfigRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EmpresaConfigResponse:
    if usuario.empresa_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Selecione uma empresa")
    repo = EmpresaRepository(db)
    empresa = await repo.buscar_por_id(usuario.empresa_id)
    if empresa is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    updates = body.model_dump(exclude_none=True)
    if 'nome_fantasia' in updates:
        empresa.nome_fantasia = updates['nome_fantasia']
    if 'razao_social' in updates:
        empresa.razao_social = updates['razao_social']
    if 'cnpj' in updates:
        empresa.cnpj = updates['cnpj']
    if 'telefone' in updates:
        empresa.telefone = updates['telefone']
    if 'email' in updates:
        empresa.email = updates['email']
    if 'endereco' in updates:
        empresa.endereco = updates['endereco']
    if 'logo_url' in updates:
        empresa.logo_url = updates['logo_url']
    if 'cor_primaria' in updates:
        empresa.cor_primaria = updates['cor_primaria']
    await repo.salvar(empresa)
    return EmpresaConfigResponse(
        id=empresa.id, nome=empresa.nome,
        nome_fantasia=empresa.nome_fantasia,
        razao_social=empresa.razao_social,
        cnpj=empresa.cnpj,
        telefone=empresa.telefone,
        email=empresa.email,
        endereco=empresa.endereco,
        logo_url=empresa.logo_url,
        cor_primaria=empresa.cor_primaria,
    )
