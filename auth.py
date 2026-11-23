# --- FORCE LOGOUT ALL - Run on every deploy ---
def logout_all_users():
    db = get_db()
    db.execute("DELETE FROM sessions")
    db.commit(); db.close()
    print("ALL USERS LOGGED OUT - Must sign in again")

logout_all_users()

# --- Check if token still valid ---
@router.get("/api/auth/me")
async def check_me(request: Request):
    email = get_current_user(request)
    return {"ok": True, "email": email}
