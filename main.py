# ADD THIS - BULK ADD PRODUCTS ENDPOINT
@app.post("/api/{branch_id}/products/bulk")
async def bulk_add(branch_id: str, products: List[Product]):
    added = []
    for p in products:
        new_p = {"id": str(uuid.uuid4())[:6], "name": p.name, "price": p.price, "stock": p.stock, "cat": p.cat.upper()}
        SUPERMARKETS[branch_id]["products"].append(new_p)
        added.append(new_p)
    return {"added": len(added), "products": added}

# SINGLE ADD (Already in your app)
@app.post("/api/{branch_id}/products")
async def add_prod(branch_id: str, p: Product):
    new_p = {"id": str(uuid.uuid4())[:6], "name": p.name, "price": p.price, "stock": p.stock, "cat": p.cat.upper()}
    SUPERMARKETS[branch_id]["products"].append(new_p)
    return new_p
