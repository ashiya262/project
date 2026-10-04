# Smart Battery Backend

FastAPI backend for the Smart Battery Lifecycle System.

## Run locally

Install dependencies and start the development server from this directory:

```powershell
pip install -r requirements.txt
uvicorn main:app --reload
```

The API root is available at `http://127.0.0.1:8000/`. Create a battery with
`POST http://127.0.0.1:8000/batteries`; interactive API documentation is
available at `http://127.0.0.1:8000/docs`.

Add local configuration to `.env`. Keep secrets out of version control.
The `app/` subpackages and `tests/` files are scaffolding for implementation.
