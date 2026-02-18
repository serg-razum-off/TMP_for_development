# Project Run
`uv run uvicorn fin_app.main:app --reload ` <br>
`uv run uvicorn fin_app.main:app --reload > server.log 2>&1 &`

## killing
`pkill -f uvicorn`
`kill $(lsof -ti:8000)` if [Errno 98] Already in use || other Err on Server side
`fuser -k 8000/tcp` alternative
