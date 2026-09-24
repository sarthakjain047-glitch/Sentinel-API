from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import time

app = FastAPI(title="SentinelAPI Vulnerable Orders API", version="1.0.0", description="Local demo target with seeded security defects")

USERS = {
    "token-a": {"id": 1, "name": "Alice", "email": "alice@example.test", "password_hash": "argon2$alice", "ssn": "111-22-3333", "internal_notes": "VIP customer"},
    "token-b": {"id": 2, "name": "Bob", "email": "bob@example.test", "password_hash": "argon2$bob", "ssn": "222-33-4444", "internal_notes": "Refund pending"},
}
ORDERS = {101: {"id": 101, "owner_id": 1, "total": 129.50, "status": "paid", "internal_notes": "Gift order"}, 202: {"id": 202, "owner_id": 2, "total": 899.00, "status": "processing", "internal_notes": "Wholesale account"}}
LOGIN_ATTEMPTS = {}

class LoginBody(BaseModel):
    username: str
    password: str

@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}

@app.get("/profile/me", tags=["users"], openapi_extra={"security": [{"bearerAuth": []}]})
def profile_me(authorization: Optional[str] = Header(default=None)):
    user = USERS.get((authorization or "").replace("Bearer ", ""))
    if not user:
        raise HTTPException(401, "authentication required")
    return {"id": user["id"], "name": user["name"], "email": user["email"]}

@app.get("/orders/{order_id}", tags=["orders"], openapi_extra={"security": [{"bearerAuth": []}]})
def get_order(order_id: int, authorization: Optional[str] = Header(default=None)):
    # Deliberate BOLA: authentication is checked but ownership is not.
    if (authorization or "").replace("Bearer ", "") not in USERS:
        raise HTTPException(401, "authentication required")
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(404, "order not found")
    return order

@app.get("/users/{user_id}", tags=["users"], openapi_extra={"security": [{"bearerAuth": []}]})
def get_user(user_id: int, authorization: Optional[str] = Header(default=None)):
    # Deliberate excessive data exposure: returns secret and internal fields.
    if (authorization or "").replace("Bearer ", "") not in USERS:
        raise HTTPException(401, "authentication required")
    for user in USERS.values():
        if user["id"] == user_id:
            return user
    raise HTTPException(404, "user not found")

@app.get("/admin/export", tags=["admin"])
def admin_export():
    # Deliberate missing authentication on a sensitive endpoint.
    return {"exported_at": time.time(), "users": list(USERS.values()), "orders": list(ORDERS.values())}

@app.post("/login", tags=["auth"])
def login(body: LoginBody, request: Request):
    # Deliberate absence of rate limiting.
    client = request.client.host if request.client else "unknown"
    LOGIN_ATTEMPTS[client] = LOGIN_ATTEMPTS.get(client, 0) + 1
    return {"ok": body.username in {"alice", "bob"}, "token": "token-a" if body.username == "alice" else None}
