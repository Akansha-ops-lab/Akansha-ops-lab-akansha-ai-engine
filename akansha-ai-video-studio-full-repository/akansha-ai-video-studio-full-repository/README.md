# Akansha AI Video Studio — Full Repository

A Python + Streamlit starter application for:
- Generating an editable script from a video topic and audience settings
- Finalising the script
- Rendering a branded slideshow-style MP4
- Optionally adding online text-to-speech narration
- Previewing and downloading the MP4

## Repository structure

```text
akansha-ai-video-studio/
├── app.py
├── api.py
├── requirements.txt
├── Dockerfile
├── README.md
├── .gitignore
├── .streamlit/
│   └── config.toml
└── engine/
    ├── __init__.py
    └── core.py
```

## Deploy on Streamlit Community Cloud

1. Create/open your GitHub repository.
2. Upload the entire contents of this folder, including the `.streamlit` and `engine` folders.
3. In Streamlit Community Cloud, choose the repository and set **Main file path** to `app.py`.
4. Deploy. When replacing an existing repository, make sure old files are removed only if they are no longer needed.
5. After a commit, wait for deployment to finish. If it fails, open **Manage app → Logs**.

## Run locally (optional)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Optional JSON API

The Streamlit app does not need the API. To run the optional FastAPI service:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

Endpoints:
- `GET /health`
- `POST /generate-script`

## Honest capability notes

- Built-in script generation is template-based Python logic; it is not a true LLM and does not independently research facts.
- Optional narration uses gTTS and needs an internet connection. Availability is not guaranteed.
- Video rendering creates branded text scene cards in MP4 format. It does not generate realistic animated humans or lip-sync.
- Streamlit Community Cloud is a free hosting option with resource limits; rendering long videos can hit limits or take time.
- No Groq key is required.
