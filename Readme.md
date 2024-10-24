## Bowling Game API

This project is a Bowling Game API built with FastAPI. It supports players, games, scores, and rolls, with full support. The API also integrates with OpenAI GPT-4 for generating summaries. A CI/CD pipeline is implemented using GitHub Actions for seamless deployment to Heroku.

### Features
- Manage Players and Games.
- Record Rolls and Calculate Scores.
- Generate Game Summaries using OpenAI GPT-4.
- CI/CD pipeline using GitHub Actions.
- Deployed on Heroku without Docker.

### Prerequisites
- **Heroku Account**: Create one at https://www.heroku.com.
- **Heroku CLI**: Install Heroku CLI.
- **Python 3.12+**: Ensure Python is installed.
- **GitHub Account**: Required for version control and CI/CD setup.

### Project Setup

1. Clone the Repository
```bash
git clone https://github.com/Sajjad-Amjad/bowling-llm-api.git
```

2. Install Dependencies
```bash
python -m venv env
source env/bin/activate  # For Linux/macOS
env\Scripts\activate      # For Windows
pip install -r requirements.txt
```

3. Set Up Environment Variables

Create a .env file in the root of your project with the following content:

```env
OPENAI_API_KEY=<your-openai-api-key>
```

4. Run the Application Locally
```bash
uvicorn app.main:app --reload
```

Access the API at: http://localhost:8000/docs

### Heroku Deployment

1. Login to Heroku via CLI

```bash
heroku login
```

2. Create a New Heroku App

```bash
heroku create your-app-name
```

Replace `your-app-name with` a unique app name.

3. Set Up Git for Deployment

```bash
git remote add heroku https://git.heroku.com/your-app-name.git
```

4. Add Heroku API Key as GitHub Secret

- Generate your API key:
```bash
heroku auth:token
```

- Add the key to GitHub Secrets in your repository:

HEROKU_API_KEY: (Your API key)
HEROKU_APP_NAME: (Your Heroku app name)
HEROKU_EMAIL: (Your Heroku email)


### CI/CD Setup with GitHub Actions

The CI/CD pipeline is set up to deploy the project automatically to Heroku when changes are pushed to the main branch.

1. It's already created `.github/workflows/deploy.yml`. You can modify it according to your needs.

2. Push Changes to Trigger Deployment:

```bash
git add .
git commit -m "Set up CI/CD"
git push origin main
```

### Testing

1. Run Unit Tests Locally

Make sure to run the tests before pushing changes:

```bash
pytest tests/
```

2. API Testing

You can use `Postman` or `Swagger UI` to test endpoints.

To access `Swagger UI` please visit this link : http://localhost:8000/docs

### Porject Structure

```bash
├── app/
│   ├── main.py          # FastAPI app logic
│   ├── game.py          # Game logic and rules
│   ├── player.py        # Player management logic
│   ├── storage.py       # JSON storage handling
│   └── __init__.py
├── tests/
│   ├── test_game.py     # Unit tests for game logic
│   ├── test_main.py     # API tests for main endpoints
│   ├── test_player.py   # Tests for player logic
├── requirements.txt     # Python dependencies
├── Procfile             # Heroku process file
├── runtime.txt          # Python version for Heroku
├── .env                 # Environment variables (ignored in Git)
├── .github/
│   └── workflows/
│       └── deploy.yml   # CI/CD workflow
└── README.md            # Project documentation

```