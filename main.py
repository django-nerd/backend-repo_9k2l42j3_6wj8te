import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Any

from database import db, create_document, get_documents
from schemas import Product, Order, Subscriber

app = FastAPI(title="Beast Hustle API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def seed_product_if_needed():
    """
    Ensure the Beast Hustle Strength Stick product exists for presale.
    Uses SKU to prevent duplicates.
    """
    try:
        if db is None:
            return
        products = db["product"]
        sku = "BH-SS-001"
        existing = products.find_one({"sku": sku})
        if not existing:
            data = Product(
                title="Beast Hustle Strength Stick",
                subtitle="Tear. Pour. Perform.",
                description=(
                    "30 precision-dosed sticks presented in a matte black wooden case with a magnetic "
                    "closure. Formulated for those who demand performance without compromise."
                ),
                price=44.0,
                currency="EUR",
                images=[
                    # Placeholder: replace with direct image URLs when available
                ],
                in_stock=True,
                sku=sku,
                limited_drop=True,
                units_per_case=30,
            )
            create_document("product", data)
    except Exception:
        # Silent fail to avoid crashing startup if seeding cannot run
        pass

@app.get("/")
def read_root():
    return {"message": "Beast Hustle API is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# Public catalog endpoints
@app.get("/api/products")
def list_products() -> List[Any]:
    docs = get_documents("product")
    # Convert Mongo docs to dicts including id
    products: List[Any] = []
    for d in docs:
        prod = dict(d)
        _id = str(prod.pop("_id", ""))
        prod["id"] = _id
        products.append(prod)
    return products

@app.post("/api/products", status_code=201)
def create_product(product: Product):
    inserted_id = create_document("product", product)
    return {"id": inserted_id}

# Subscribe for drops
class SubscribeIn(BaseModel):
    email: EmailStr

@app.post("/api/subscribe", status_code=201)
def subscribe(data: SubscribeIn):
    sub = Subscriber(email=data.email, source="landing")
    create_document("subscriber", sub)
    return {"ok": True}

# Create simple order capture (no payments)
@app.post("/api/orders", status_code=201)
def create_order(order: Order):
    order_id = create_document("order", order)
    return {"id": order_id, "ok": True}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
