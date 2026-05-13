from __future__ import annotations

from uuid import UUID

from app.identity.domain.constants import Permissao, PerfilUsuario
from app.identity.domain.models import Empresa, Grupo, Usuario
from app.identity.infrastructure.orm_models import EmpresaORM, GrupoORM, UsuarioORM


def grupo_to_domain(o: GrupoORM) -> Grupo:
    return Grupo(
        id=UUID(o.id),
        nome=o.nome,
        logo_url=o.logo_url,
        ativo=o.ativo,
        criado_em=o.criado_em,
    )


def grupo_to_orm(g: Grupo) -> GrupoORM:
    return GrupoORM(
        id=str(g.id),
        nome=g.nome,
        logo_url=g.logo_url,
        ativo=g.ativo,
        criado_em=g.criado_em,
    )


def empresa_to_domain(o: EmpresaORM) -> Empresa:
    return Empresa(
        id=UUID(o.id),
        grupo_id=UUID(o.grupo_id),
        nome=o.nome,
        cnpj=o.cnpj,
        logo_url=o.logo_url,
        cor_primaria=o.cor_primaria,
        ativa=o.ativa,
        criado_em=o.criado_em,
        nome_fantasia=getattr(o, 'nome_fantasia', None),
        razao_social=getattr(o, 'razao_social', None),
        telefone=getattr(o, 'telefone', None),
        email=getattr(o, 'email', None),
        endereco=getattr(o, 'endereco', None),
    )


def empresa_to_orm(e: Empresa) -> EmpresaORM:
    return EmpresaORM(
        id=str(e.id),
        grupo_id=str(e.grupo_id),
        nome=e.nome,
        cnpj=e.cnpj,
        logo_url=e.logo_url,
        cor_primaria=e.cor_primaria,
        ativa=e.ativa,
        criado_em=e.criado_em,
        nome_fantasia=e.nome_fantasia,
        razao_social=e.razao_social,
        telefone=e.telefone,
        email=e.email,
        endereco=e.endereco,
    )


def usuario_to_domain(o: UsuarioORM) -> Usuario:
    return Usuario(
        id=UUID(o.id),
        grupo_id=UUID(o.grupo_id),
        empresa_id=UUID(o.empresa_id) if o.empresa_id else None,
        nome=o.nome,
        email=o.email,
        senha_hash=o.senha_hash,
        perfil=PerfilUsuario(o.perfil),
        permissoes=[Permissao(p) for p in o.permissoes],
        ativo=o.ativo,
        criado_em=o.criado_em,
        comissao_percentual=float(o.comissao_percentual or 0),
        telefone=getattr(o, 'telefone', None),
        endereco=getattr(o, 'endereco', None),
    )


def usuario_to_orm(u: Usuario) -> UsuarioORM:
    return UsuarioORM(
        id=str(u.id),
        grupo_id=str(u.grupo_id),
        empresa_id=str(u.empresa_id) if u.empresa_id else None,
        nome=u.nome,
        email=u.email,
        senha_hash=u.senha_hash,
        perfil=u.perfil.value,
        permissoes=[p.value for p in u.permissoes],
        ativo=u.ativo,
        criado_em=u.criado_em,
        comissao_percentual=float(u.comissao_percentual),
        telefone=u.telefone,
        endereco=u.endereco,
    )
