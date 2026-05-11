from __future__ import annotations

from enum import StrEnum


class PerfilUsuario(StrEnum):
    ADMIN_GRUPO = "admin_grupo"
    ADMIN_EMPRESA = "admin_empresa"
    VENDEDOR = "vendedor"
    OPERADOR = "operador"
    CAIXA = "caixa"
    FINANCEIRO = "financeiro"


class Permissao(StrEnum):
    VER_DASHBOARD = "ver_dashboard"
    VER_ESTOQUE = "ver_estoque"
    EDITAR_ESTOQUE = "editar_estoque"
    VER_ORCAMENTOS = "ver_orcamentos"
    CRIAR_ORCAMENTOS = "criar_orcamentos"
    APROVAR_ORCAMENTOS = "aprovar_orcamentos"
    VER_CLIENTES = "ver_clientes"
    EDITAR_CLIENTES = "editar_clientes"
    VER_FINANCEIRO = "ver_financeiro"
    LANCAR_FINANCEIRO = "lancar_financeiro"
    VER_COMISSOES = "ver_comissoes"
    VER_AUDITORIA = "ver_auditoria"
    USAR_CAIXA = "usar_caixa"
    GERENCIAR_USUARIOS = "gerenciar_usuarios"
    GERENCIAR_PREMISSAS = "gerenciar_premissas"
    CONFIGURAR_SISTEMA = "configurar_sistema"
