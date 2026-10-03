@app.head("/")
async def head_root():
    return Response(status_code=200)
