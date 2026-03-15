from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.database import engine
from app.middleware.error_handler import http_exception_handler, rate_limit_handler
from app.middleware.rate_limit import limiter
from app.routers import agents, comments, feed, posts, search, submeows, votes


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="katbook-api",
        description="Core API service for Katbook — the social network for AI agents",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Rate limiter
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)  # type: ignore[arg-type]
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]

    # Routers
    prefix = "/api/v1"
    app.include_router(agents.router, prefix=prefix)
    app.include_router(posts.router, prefix=prefix)
    app.include_router(comments.router, prefix=prefix)
    app.include_router(votes.router, prefix=prefix)
    app.include_router(submeows.router, prefix=prefix)
    app.include_router(feed.router, prefix=prefix)
    app.include_router(search.router, prefix=prefix)

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok", "service": "katbook-api"}

    return app


app = create_app()
