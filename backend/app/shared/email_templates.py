"""
email_templates.py — Templates HTML para e-mails transacionais.
"""
from __future__ import annotations


_BASE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{subject}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background-color: #F4F4F5;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      font-size: 15px;
      line-height: 1.6;
      color: #18181B;
    }}
    .wrapper {{
      max-width: 600px;
      margin: 32px auto;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 4px 24px rgba(0,0,0,0.08);
    }}
    .header {{
      background: #18181B;
      padding: 28px 40px;
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .logo-box {{
      background: #E83B4C;
      border-radius: 10px;
      padding: 8px 14px;
    }}
    .logo-text {{
      color: #FFFFFF;
      font-size: 17px;
      font-weight: 700;
      letter-spacing: -0.3px;
    }}
    .tagline {{
      color: #71717A;
      font-size: 12px;
      margin-top: 4px;
    }}
    .content {{
      background: #FFFFFF;
      padding: 40px;
    }}
    h1 {{
      font-size: 22px;
      font-weight: 700;
      color: #09090B;
      margin-bottom: 12px;
    }}
    p {{
      color: #3F3F46;
      margin-bottom: 16px;
    }}
    .highlight {{
      color: #E83B4C;
      font-weight: 600;
    }}
    .divider {{
      border: none;
      border-top: 1px solid #F4F4F5;
      margin: 28px 0;
    }}
    .steps-title {{
      font-size: 13px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: #71717A;
      margin-bottom: 16px;
    }}
    .step {{
      display: flex;
      gap: 14px;
      margin-bottom: 14px;
      align-items: flex-start;
    }}
    .step-num {{
      background: #FEE2E4;
      color: #E83B4C;
      border-radius: 50%;
      width: 28px;
      height: 28px;
      font-size: 13px;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      text-align: center;
      line-height: 28px;
    }}
    .step-text {{
      padding-top: 4px;
      color: #3F3F46;
      font-size: 14px;
    }}
    .step-text strong {{
      color: #09090B;
    }}
    .btn-wrapper {{
      text-align: center;
      margin: 32px 0 24px;
    }}
    .btn {{
      display: inline-block;
      background: #E83B4C;
      color: #FFFFFF !important;
      text-decoration: none;
      font-weight: 700;
      font-size: 15px;
      padding: 14px 36px;
      border-radius: 10px;
      letter-spacing: -0.1px;
    }}
    .info-box {{
      background: #F9FAFB;
      border: 1px solid #F4F4F5;
      border-radius: 10px;
      padding: 16px 20px;
      margin: 20px 0;
    }}
    .info-row {{
      display: flex;
      justify-content: space-between;
      font-size: 13px;
      margin-bottom: 6px;
    }}
    .info-row:last-child {{ margin-bottom: 0; }}
    .info-label {{ color: #71717A; }}
    .info-value {{ color: #09090B; font-weight: 600; font-family: monospace; }}
    .footer {{
      background: #FAFAFA;
      border-top: 1px solid #F4F4F5;
      padding: 24px 40px;
      text-align: center;
    }}
    .footer p {{
      font-size: 12px;
      color: #A1A1AA;
      margin-bottom: 4px;
    }}
    .footer a {{
      color: #E83B4C;
      text-decoration: none;
    }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <div class="logo-box">
        <span class="logo-text">Pediu Chegou</span>
      </div>
    </div>
    {body}
    <div class="footer">
      <p>Pediu Chegou &mdash; Sistema de gestao de pedidos para restaurantes</p>
      <p>Duvidas? <a href="mailto:suporte@pediu-chegou.com.br">suporte@pediu-chegou.com.br</a></p>
      <p style="margin-top: 12px;">Se voce nao criou esta conta, ignore este e-mail.</p>
    </div>
  </div>
</body>
</html>"""


def render_welcome_email(
    nome: str,
    nome_restaurante: str,
    slug: str,
    app_url: str = "http://localhost",
) -> tuple[str, str]:
    """Returns (subject, html_body)."""
    subject = f"Bem-vindo ao Pediu Chegou, {nome_restaurante}!"

    body = f"""
    <div class="content">
      <h1>Ola, {nome}!</h1>
      <p>
        O restaurante <span class="highlight">{nome_restaurante}</span> foi cadastrado
        com sucesso. Sua conta de administrador esta pronta para uso.
      </p>

      <div class="info-box">
        <div class="info-row">
          <span class="info-label">Restaurante</span>
          <span class="info-value">{nome_restaurante}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Slug</span>
          <span class="info-value">{slug}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Plano</span>
          <span class="info-value">Trial (14 dias)</span>
        </div>
      </div>

      <hr class="divider" />

      <p class="steps-title">Proximos passos</p>

      <div class="step">
        <div class="step-num">1</div>
        <div class="step-text">
          Monte seu <strong>cardapio</strong> com categorias e produtos
          diretamente no painel admin.
        </div>
      </div>
      <div class="step">
        <div class="step-num">2</div>
        <div class="step-text">
          Conecte seu <strong>WhatsApp</strong> para ativar o agente de IA
          que recebe e confirma pedidos automaticamente.
        </div>
      </div>
      <div class="step">
        <div class="step-num">3</div>
        <div class="step-text">
          Configure o <strong>KDS de cozinha</strong> e cadastre seus
          entregadores para comecar a operar.
        </div>
      </div>

      <div class="btn-wrapper">
        <a href="{app_url}/admin" class="btn">Acessar o painel agora</a>
      </div>

      <hr class="divider" />

      <p style="font-size: 13px; color: #71717A;">
        Seu cardapio publico estara disponivel em
        <strong>{app_url}/cardapio?slug={slug}</strong> assim que voce
        cadastrar os produtos.
      </p>
    </div>
    """

    return subject, _BASE.format(subject=subject, body=body)
