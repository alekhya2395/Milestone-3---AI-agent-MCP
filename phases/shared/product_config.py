"""Product configuration — read from .env (default: Groww)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

PRODUCT_NAME = os.getenv("PRODUCT_NAME", "Groww").strip()
APP_STORE_ID = os.getenv("APP_STORE_ID", "1404871703").strip()
PLAY_PACKAGE = os.getenv("PLAY_PACKAGE", "com.nextbillion.groww").strip()
PLAY_COUNTRY = os.getenv("PLAY_COUNTRY", "in").strip()
APP_STORE_COUNTRIES = tuple(
    c.strip() for c in os.getenv("APP_STORE_COUNTRIES", "in,us").split(",") if c.strip()
)

THEME_VOCABULARY = [
    "Trading & orders",
    "KYC & onboarding",
    "Deposits & withdrawals",
    "App UX & bugs",
    "Customer support",
]

THEME_KEYWORDS: dict[str, list[str]] = {
    "Trading & orders": [
        "trade", "trading", "order", "buy", "sell", "stock", "fno", "option",
        "chart", "execute", "position", "broker", "nifty", "mutual fund", "ipo",
    ],
    "KYC & onboarding": [
        "kyc", "verify", "verification", "pan", "aadhaar", "onboard", "account open",
        "document", "signup", "register",
    ],
    "Deposits & withdrawals": [
        "deposit", "withdraw", "withdrawal", "money", "transfer", "upi", "bank",
        "settlement", "credit", "debit", "balance", "payment",
    ],
    "App UX & bugs": [
        "crash", "bug", "slow", "freeze", "glitch", "hang", "loading", "ui",
        "update", "app", "screen",
    ],
    "Customer support": [
        "support", "customer care", "help", "complaint", "refund", "response",
        "chatbot", "executive", "service", "unhelpful",
    ],
}


def pulse_title(date: str) -> str:
    return f"# {PRODUCT_NAME} — Weekly Review Pulse ({date})"
