from fastapi import APIRouter
from fastapi.responses import HTMLResponse

base_router = APIRouter()


@base_router.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Financial Tracker API</title>
            <style>
                body { font-family: sans-serif; margin: 40px; line-height: 1.6; }
                .container { max-width: 600px; margin: 0 auto; text-align: center; }
                a { color: #007bff; text-decoration: none; font-weight: bold; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>💸 Financial Tracker API</h1>
                <p>Welcome! The server is up and running.</p>
                <p>To explore the API endpoints and test the CRUD operations, please visit the:</p>
                <a href="/docs">Interactive API Documentation (Swagger UI)</a>
            </div>
        </body>
    </html>
    """
