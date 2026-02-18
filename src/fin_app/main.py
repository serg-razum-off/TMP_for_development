import uvicorn
from fin_app import create_app
from fin_app.settings.config import HOST, PORT


app = create_app()

if __name__ == "__main__":
    server_port = int(PORT)  # SR: for docker
    uvicorn.run("fin_app.main:app", host=HOST, port=server_port, reload=True)
