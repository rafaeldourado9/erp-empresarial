"""
email_service.py — Envio de e-mails via SMTP assíncrono (aiosmtplib).

Uso:
    service = EmailService(get_settings())
    await service.send_welcome_email(
        to_email="chef@restaurante.com",
        nome="Rafael",
        nome_restaurante="Burguer Palace",
        slug="burguer-palace",
    )

Se SMTP_ENABLED=false (padrão em dev), os e-mails são apenas logados.
"""
from __future__ import annotations

import asyncio
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from app.config import Settings
from app.shared.email_templates import render_welcome_email

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self, settings: Settings) -> None:
        self._cfg = settings

    async def _send(self, to: str, subject: str, html: str) -> None:
        if not self._cfg.smtp_enabled:
            logger.info("[EMAIL SIMULADO] Para: %s | Assunto: %s", to, subject)
            return

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self._cfg.smtp_from_name} <{self._cfg.smtp_from_email}>"
        msg["To"] = to
        msg.attach(MIMEText(html, "html", "utf-8"))

        try:
            await aiosmtplib.send(
                msg,
                hostname=self._cfg.smtp_host,
                port=self._cfg.smtp_port,
                username=self._cfg.smtp_user,
                password=self._cfg.smtp_password,
                start_tls=self._cfg.smtp_port == 587,
                use_tls=self._cfg.smtp_port == 465,
            )
            logger.info("[EMAIL ENVIADO] Para: %s | Assunto: %s", to, subject)
        except Exception as exc:
            logger.error("[EMAIL FALHOU] Para: %s | Erro: %s", to, exc)

    def send_background(self, to: str, subject: str, html: str) -> None:
        """Dispara o envio em background — não bloqueia o request."""
        asyncio.create_task(self._send(to, subject, html))

    async def send_welcome_email(
        self,
        to_email: str,
        nome: str,
        nome_restaurante: str,
        slug: str,
    ) -> None:
        subject, html = render_welcome_email(
            nome=nome,
            nome_restaurante=nome_restaurante,
            slug=slug,
            app_url=self._cfg.app_url,
        )
        self.send_background(to_email, subject, html)
