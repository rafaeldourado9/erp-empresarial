from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.audit.api.router import router as auditoria_router
from app.clients.api.router import router as clientes_router
from app.commissions.api.router import router as comissoes_router
from app.finance.api.router import router as financeiro_router
from app.identity.api.router import router as identity_router
from app.inventory.api.router import router as estoque_router
from app.pos.api.router import router as caixa_router
from app.prospecting.api.router import router as prospeccao_router
from app.quotes.api.router import router as orcamentos_router
from app.quotes.api.solar_router import router as solar_router

app = FastAPI(
    title="ERP Empresarial",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(identity_router, prefix="/api/v1")
app.include_router(clientes_router, prefix="/api/v1")
app.include_router(estoque_router, prefix="/api/v1")
app.include_router(orcamentos_router, prefix="/api/v1")
app.include_router(solar_router, prefix="/api/v1")
app.include_router(financeiro_router, prefix="/api/v1")
app.include_router(comissoes_router, prefix="/api/v1")
app.include_router(prospeccao_router, prefix="/api/v1")
app.include_router(caixa_router, prefix="/api/v1")
app.include_router(auditoria_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "erp-empresarial"}
