from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse

app = FastAPI()

# This fixes Render health check
@app.head("/")
async def head_root():
    return Response(status_code=200)

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head><title>LONMA ORBIT</title></head>
        <body style="background:black;color:gold;text-align:center;padding:50px">
            <h1>LONMA ORBIT App Studio 🚀</h1>
            <p>Elite Systems by Marlone</p>
            <p>Service is LIVE!</p>
        </body>
    </html>
    """
# keep your other routes below...
