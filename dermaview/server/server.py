from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Literal
from uuid import uuid4

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field, HttpUrl

DB_PATH = Path(
    os.getenv(
        "DERMAVIEW_DATABASE_PATH",
        "dermaview.db",
    )
)

ADMIN_KEY = os.getenv(
    "DERMAVIEW_ADMIN_API_KEY",
    "change-me",
)

app = FastAPI(
    title="DermaView Product API",
    version="0.1.0",
)

REGIONS = {
    "face",
    "neck",
    "chest",
    "abdomen",
    "upper_back",
    "lower_back",
    "left_upper_arm",
    "right_upper_arm",
    "left_forearm",
    "right_forearm",
    "left_elbow",
    "right_elbow",
    "left_hand",
    "right_hand",
    "left_thigh",
    "right_thigh",
    "left_knee",
    "right_knee",
    "left_shin",
    "right_shin",
    "left_foot",
    "right_foot",
    "left_heel",
    "right_heel",
}


@contextmanager
def db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db():
    with db() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                catalog_url TEXT,
                catalog_api_key TEXT
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sku TEXT NOT NULL,
                name_ar TEXT NOT NULL,
                name_en TEXT NOT NULL,
                product_url TEXT NOT NULL,
                image_url TEXT,
                price_sar REAL,
                ingredients TEXT NOT NULL DEFAULT '[]',
                regions TEXT NOT NULL DEFAULT '[]',
                concerns TEXT NOT NULL DEFAULT '[]',
                skin_types TEXT NOT NULL DEFAULT '["all"]',
                contraindications TEXT NOT NULL DEFAULT '[]',
                active INTEGER NOT NULL DEFAULT 1,
                UNIQUE(company_id, sku)
            );
            """
        )

        connection.execute(
            """
            INSERT OR IGNORE INTO companies(name)
            VALUES (?)
            """,
            ("DermaView Demo Partner",),
        )

        company_id = connection.execute(
            """
            SELECT id
            FROM companies
            WHERE name = ?
            """,
            ("DermaView Demo Partner",),
        ).fetchone()["id"]

        seed_products = [
            (
                "CER-01",
                "مرطب سيراميد للوجه والجسم",
                "Ceramide Moisturizer",
                "https://example.com/ceramide",
                49,
                ["ceramides", "glycerin"],
                sorted(REGIONS),
                [
                    "visible_dryness",
                    "texture",
                    "maintenance",
                ],
                ["all"],
                [],
            ),
            (
                "NIA-02",
                "سيروم نياسيناميد لطيف",
                "Gentle Niacinamide Serum",
                "https://example.com/niacinamide",
                69,
                ["niacinamide", "panthenol"],
                [
                    "face",
                    "neck",
                    "chest",
                    "upper_back",
                ],
                [
                    "oiliness",
                    "redness",
                    "tone_uniformity",
                ],
                ["all"],
                [],
            ),
            (
                "UREA-03",
                "كريم يوريا للكوع والركبة والكعب",
                "Urea Cream",
                "https://example.com/urea",
                39,
                ["urea", "glycerin"],
                [
                    "left_elbow",
                    "right_elbow",
                    "left_knee",
                    "right_knee",
                    "left_heel",
                    "right_heel",
                    "left_foot",
                    "right_foot",
                ],
                [
                    "visible_dryness",
                    "texture",
                    "tone_uniformity",
                ],
                ["all"],
                [],
            ),
        ]

        for product in seed_products:
            connection.execute(
                """
                INSERT OR IGNORE INTO products(
                    company_id,
                    sku,
                    name_ar,
                    name_en,
                    product_url,
                    price_sar,
                    ingredients,
                    regions,
                    concerns,
                    skin_types,
                    contraindications
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    company_id,
                    product[0],
                    product[1],
                    product[2],
                    product[3],
                    product[4],
                    json.dumps(product[5]),
                    json.dumps(product[6]),
                    json.dumps(product[7]),
                    json.dumps(product[8]),
                    json.dumps(product[9]),
                ),
            )


class Metrics(BaseModel):
    visible_dryness: float = Field(ge=0, le=100)
    redness: float = Field(ge=0, le=100)
    tone_uniformity: float = Field(ge=0, le=100)
    texture: float = Field(ge=0, le=100)
    fine_lines: float = Field(ge=0, le=100)
    oiliness: float = Field(ge=0, le=100)
    quality: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=100)
    model_version: str


class Profile(BaseModel):
    sensitive_skin: bool = False
    pregnant: bool = False
    breastfeeding: bool = False
    under_dermatology_treatment: bool = False
    known_allergies: list[str] = []


class RecommendationRequest(BaseModel):
    consent: bool
    body_region: str
    metrics: Metrics
    profile: Profile = Profile()
    language: Literal["ar", "en"] = "ar"


class CompanyIn(BaseModel):
    name: str
    catalog_url: HttpUrl | None = None
    catalog_api_key: str | None = None


class ProductIn(BaseModel):
    company_id: int
    sku: str
    name_ar: str
    name_en: str
    product_url: HttpUrl
    image_url: HttpUrl | None = None
    price_sar: float | None = None
    ingredients: list[str] = []
    body_regions: list[str] = []
    concerns: list[str] = []
    skin_types: list[str] = ["all"]
    contraindications: list[str] = []
    active: bool = True


def require_admin(
    x_admin_key: str = Header(
        default="",
        alias="X-Admin-Key",
    )
):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid admin key",
        )


def concerns_from(metrics: Metrics):
    concerns = {}

    if metrics.visible_dryness >= 42:
        concerns["visible_dryness"] = (
            metrics.visible_dryness
        )

    if metrics.redness >= 38:
        concerns["redness"] = metrics.redness

    if metrics.tone_uniformity <= 65:
        concerns["tone_uniformity"] = (
            100 - metrics.tone_uniformity
        )

    if metrics.texture >= 40:
        concerns["texture"] = metrics.texture

    if metrics.fine_lines >= 38:
        concerns["fine_lines"] = (
            metrics.fine_lines
        )

    if metrics.oiliness >= 55:
        concerns["oiliness"] = metrics.oiliness

    return concerns or {"maintenance": 35}


def is_blocked(product, profile: Profile):
    flags = set(
        json.loads(
            product["contraindications"]
        )
    )

    if profile.pregnant and "pregnancy" in flags:
        return True

    if (
        profile.breastfeeding
        and "breastfeeding" in flags
    ):
        return True

    if (
        profile.sensitive_skin
        and "sensitive_skin" in flags
    ):
        return True

    if (
        profile.under_dermatology_treatment
        and "dermatology_treatment" in flags
    ):
        return True

    ingredients = {
        item.lower()
        for item in json.loads(
            product["ingredients"]
        )
    }

    allergies = {
        item.lower()
        for item in profile.known_allergies
    }

    return bool(
        ingredients.intersection(allergies)
    )


@app.on_event("startup")
def startup():
    init_db()


@app.middleware("http")
async def reject_media(
    request: Request,
    call_next,
):
    content_type = request.headers.get(
        "content-type",
        "",
    ).lower()

    if (
        request.url.path == "/v1/recommendations"
        and (
            "image/" in content_type
            or "video/" in content_type
            or "multipart/form-data" in content_type
        )
    ):
        raise HTTPException(
            status_code=415,
            detail="JSON numeric indicators only",
        )

    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"

    return response


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/recommendations")
def recommend(request: RecommendationRequest):
    if not request.consent:
        raise HTTPException(
            status_code=400,
            detail="Explicit consent required",
        )

    if request.body_region not in REGIONS:
        raise HTTPException(
            status_code=422,
            detail="Unsupported body region",
        )

    if (
        request.metrics.quality < 42
        or request.metrics.confidence < 35
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "Scan quality or confidence "
                "is too low"
            ),
        )

    wanted = concerns_from(request.metrics)

    with db() as connection:
        rows = connection.execute(
            """
            SELECT
                p.*,
                c.name AS company_name,
                c.active AS company_active
            FROM products p
            JOIN companies c
                ON c.id = p.company_id
            WHERE
                p.active = 1
                AND c.active = 1
            """
        ).fetchall()

    items = []

    for product in rows:
        regions = json.loads(product["regions"])
        product_concerns = set(
            json.loads(product["concerns"])
        )

        if request.body_region not in regions:
            continue

        if is_blocked(product, request.profile):
            continue

        matched = product_concerns.intersection(
            wanted
        )

        if (
            not matched
            and "maintenance"
            not in product_concerns
        ):
            continue

        score = 25.0

        for concern in matched:
            score += (
                48
                * wanted[concern]
                / 100
                / max(1, len(matched))
            )

        if "all" in json.loads(
            product["skin_types"]
        ):
            score += 8

        if request.metrics.confidence >= 70:
            score += 5

        if product["price_sar"] is not None:
            score += 2

        items.append({
            "id": product["id"],
            "company_name": (
                product["company_name"]
            ),
            "name_ar": product["name_ar"],
            "name_en": product["name_en"],
            "product_url": (
                product["product_url"]
            ),
            "image_url": product["image_url"],
            "price_sar": product["price_sar"],
            "score": min(
                round(score, 2),
                100,
            ),
            "reasons": (
                sorted(matched)
                or ["maintenance"]
            ),
        })

    items.sort(
        key=lambda item: (
            -item["score"],
            item["price_sar"] or 10**9,
        )
    )

    return {
        "request_id": str(uuid4()),
        "data_received": [
            "body_region",
            "numeric_metrics",
            "general_safety_profile",
        ],
        "items": items[:12],
        "disclaimer": (
            "Cosmetic matching only. "
            "No diagnosis and no images stored."
        ),
    }


@app.post(
    "/v1/admin/companies",
    dependencies=[Depends(require_admin)],
)
def add_company(data: CompanyIn):
    with db() as connection:
        cursor = connection.execute(
            """
            INSERT INTO companies(
                name,
                catalog_url,
                catalog_api_key
            )
            VALUES (?, ?, ?)
            """,
            (
                data.name,
                str(data.catalog_url)
                if data.catalog_url
                else None,
                data.catalog_api_key,
            ),
        )

    return {
        "id": cursor.lastrowid,
        "name": data.name,
    }


@app.put(
    "/v1/admin/products",
    dependencies=[Depends(require_admin)],
)
def upsert_product(product: ProductIn):
    invalid_regions = (
        set(product.body_regions) - REGIONS
    )

    if invalid_regions:
        raise HTTPException(
            status_code=422,
            detail="Unsupported body region",
        )

    with db() as connection:
        connection.execute(
            """
            INSERT INTO products(
                company_id,
                sku,
                name_ar,
                name_en,
                product_url,
                image_url,
                price_sar,
                ingredients,
                regions,
                concerns,
                skin_types,
                contraindications,
                active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(company_id, sku)
            DO UPDATE SET
                name_ar = excluded.name_ar,
                name_en = excluded.name_en,
                product_url = excluded.product_url,
                image_url = excluded.image_url,
                price_sar = excluded.price_sar,
                ingredients = excluded.ingredients,
                regions = excluded.regions,
                concerns = excluded.concerns,
                skin_types = excluded.skin_types,
                contraindications =
                    excluded.contraindications,
                active = excluded.active
            """,
            (
                product.company_id,
                product.sku,
                product.name_ar,
                product.name_en,
                str(product.product_url),
                str(product.image_url)
                if product.image_url
                else None,
                product.price_sar,
                json.dumps(product.ingredients),
                json.dumps(product.body_regions),
                json.dumps(product.concerns),
                json.dumps(product.skin_types),
                json.dumps(
                    product.contraindications
                ),
                int(product.active),
            ),
        )

        row = connection.execute(
            """
            SELECT id
            FROM products
            WHERE company_id = ?
              AND sku = ?
            """,
            (
                product.company_id,
                product.sku,
            ),
        ).fetchone()

    return {
        "id": row["id"],
        "action": "upserted",
    }


@app.post(
    "/v1/admin/sync/{company_id}",
    dependencies=[Depends(require_admin)],
)
async def sync_company(company_id: int):
    with db() as connection:
        company = connection.execute(
            """
            SELECT *
            FROM companies
            WHERE id = ?
            """,
            (company_id,),
        ).fetchone()

    if (
        not company
        or not company["catalog_url"]
    ):
        raise HTTPException(
            status_code=404,
            detail="Company or catalog not found",
        )

    headers = {
        "Accept": "application/json",
    }

    if company["catalog_api_key"]:
        headers["Authorization"] = (
            f"Bearer "
            f"{company['catalog_api_key']}"
        )

    async with httpx.AsyncClient(
        timeout=15,
        follow_redirects=False,
    ) as client:
        response = await client.get(
            company["catalog_url"],
            headers=headers,
        )

        response.raise_for_status()

        products = response.json().get(
            "products",
            [],
        )

    count = 0

    for raw_product in products:
        product = ProductIn(
            company_id=company_id,
            **raw_product,
        )

        upsert_product(product)
        count += 1

    return {"synced": count}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
