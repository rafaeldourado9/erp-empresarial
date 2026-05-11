from __future__ import annotations


class CredenciaisInvalidasError(Exception):
    pass


class UsuarioInativoError(Exception):
    pass


class TokenInvalidoError(Exception):
    pass


class UsuarioNaoEncontradoError(Exception):
    pass


class EmpresaNaoEncontradaError(Exception):
    pass


class EmailJaCadastradoError(Exception):
    pass
