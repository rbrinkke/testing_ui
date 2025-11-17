"""
FastAPI router for serving the authentication testing UI.

This router serves a standalone HTML page for testing all authentication flows:
- Registration with email code
- Login with code and organization selection
- Password reset with email code
- Token management (refresh, logout)
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Setup templates directory
TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter(
    prefix="/test",
    tags=["testing-ui"],
    include_in_schema=True,
)


@router.get("/auth", response_class=HTMLResponse, summary="Authentication Testing Page")
async def auth_testing_page(request: Request):
    """
    Serves the authentication testing interface.

    This page allows testing all authentication flows:
    - Registration (with email verification code)
    - Login (with login code and optional org selection)
    - Password reset (with reset code)
    - Token refresh and logout
    """
    return templates.TemplateResponse(
        "auth_test.html",
        {
            "request": request,
            "title": "Auth API Testing Interface",
        }
    )


@router.get("/login", response_class=HTMLResponse, summary="Authentication Login Page")
async def auth_login_page(request: Request):
    """
    Serves the authentication login/register page.

    This page provides a clean, single-box interface for:
    - Login with code verification
    - Registration with email verification
    - Password reset with code
    """
    return templates.TemplateResponse(
        "auth_login.html",
        {
            "request": request,
            "title": "Login - Authentication",
        }
    )


@router.get("/notifications", response_class=HTMLResponse, summary="Notifications API Testing Page")
async def notifications_testing_page(request: Request):
    """
    Serves the notifications API testing interface.

    This page allows testing all notification flows:
    - Create notifications (service-to-service)
    - List notifications (with filtering and pagination)
    - Get unread count
    - Mark notifications as read (single and bulk)
    - Delete/archive notifications
    - Manage notification settings
    """
    return templates.TemplateResponse(
        "notifications_test.html",
        {
            "request": request,
            "title": "Notifications API Testing Interface",
        }
    )


@router.get("/notifications/live", response_class=HTMLResponse, summary="Notifications Live Feed Page")
async def notifications_live_page(request: Request):
    """
    Serves the live notifications feed interface.

    This page provides a production-ready notification interface with:
    - Professional notification cards with type-based styling
    - Actor avatars and relative timestamps
    - Smart filtering (status and type filters)
    - Mark as read and delete actions
    - Auto-refresh polling (30s interval)
    - Unread count badges
    """
    return templates.TemplateResponse(
        "notifications_live.html",
        {
            "request": request,
            "title": "Notifications - Live Feed",
        }
    )
