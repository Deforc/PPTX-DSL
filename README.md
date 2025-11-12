# PPTX-DSL
## How to launch backend part?
1. Create and activate it Virtual Environment
```shell
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```
2. Install libraries from `requirements.txt`
```shell
pip install -r requirements.txt
```
3. Copy and edit .env.example from `backend/`. Launch it from the directory of initial project repository
```shell
cp .env.example .env
```
4. From the directory of project (not from the backend/ directory) launch FastAPI server
```shell
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```
5. Project Documentation can be opened:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc