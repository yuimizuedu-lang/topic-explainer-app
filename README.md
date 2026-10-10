# topic-explainer-app

A small Python Flask app that accepts a topic and returns:
- a short explanation
- 3 key takeaways

It works without an API key using a built-in fallback generator, and it can also use OpenAI if `OPENAI_API_KEY` is provided.

## Features
- Simple web interface
- Beginner-friendly explanations
- Key takeaways for quick learning
- Ready for local run or deployment to cloud hosting

## Local setup

1. Clone the repository
2. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
python app.py
```

Open `http://localhost:5000` in your browser.

## Optional: OpenAI integration

Create a `.env` file using the example:

```bash
cp .env.example .env
```

Then add your OpenAI key:

```env
OPENAI_API_KEY=your_api_key_here
```

The app will use OpenAI automatically when the key is available.

## Deployment options

### Render
1. Push this repo to GitHub
2. Create a new Web Service on Render
3. Connect the repo
4. Set the build command to `pip install -r requirements.txt`
5. Set the start command to `gunicorn app:app`

### Railway / Heroku / similar
- Use the included `Procfile` or set `gunicorn app:app` as the startup command.

### Docker

```bash
docker build -t topic-explainer-app .
docker run -p 8000:8000 topic-explainer-app
```

## Project structure

- `app.py` — Flask app and logic
- `templates/index.html` — user interface
- `static/style.css` — styling
- `requirements.txt` — dependencies
- `Dockerfile` — container deployment
- `.env.example` — environment variables

## Example usage

Input topic:

```text
Artificial Intelligence
```

Output:

- Short explanation about AI
- 3 key takeaways
