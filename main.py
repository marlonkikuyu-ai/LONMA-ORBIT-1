@app.get("/")
@app.head("/")
def root():
    return {"status":"ok","auth_loaded":True}

@app.get("/health")
@app.head("/health")
def health():
    return {"status":"ok"}
