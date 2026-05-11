from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class RegistroAuditoriaORM(Base):
    __tablename__ = "registros_auditoria"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    grupo_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("grupos.id"), nullable=True, index=True)
    empresa_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("empresas.id"), nullable=True, index=True)
    usuario_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("usuarios.id"), nullable=True, index=True)
    usuario_nome: Mapped[str | None] = mapped_column(String(200), nullable=True)
    acao: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    recurso: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    recurso_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    detalhes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
