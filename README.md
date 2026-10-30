# Northstar IT Support Assistant (Nugen + Streamlit)

A small Streamlit application that calls a **deployed Nugen domain-aligned model** for IT support questions.

## What this project does

- Lists aligned models using `GET /api/v3/models/aligned`.
- Shows only models whose deployment status is `DEPLOYED`.
- Sends chat requests to `POST /api/v3/inference/chat/completions` using the aligned `model_id` in the JSON body.
- Keeps chat history in the current Streamlit session.
- Displays the most recent response's returned confidence score and token usage, when available.
- Exports the current conversation as JSON.
- Includes a five-question manual-review evaluation set.

## Important limitation

This app calls the domain-aligned model directly. It does **not** perform document retrieval at question time and does not show citations from the uploaded documents. Domain alignment does not guarantee every answer is factually grounded. Compare outputs against the original source documents before treating the app as reliable.

## 1. Requirements

- Windows 10/11 or another OS with Python 3.10+.
- A Nugen API key.
- At least one aligned model in your Nugen account with deployment status `DEPLOYED`.

## 2. Setup in VS Code (Windows PowerShell)

Open this folder in VS Code. Open **Terminal > New Terminal** and run:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and replace the placeholder with your real API key:

```dotenv
NUGEN_API_KEY=your_real_api_key
NUGEN_MODEL_ID=
NUGEN_API_BASE_URL=https://api.nugen.in/api/v3
```

Do not add quotes unless your key itself includes them. Do not commit `.env` to GitHub.

## 3. Verify your deployed model from VS Code

```powershell
python scripts/list_models.py
```

Find the model whose base is `Qwen/Qwen2.5-1.5B-Instruct` and whose status is `DEPLOYED`. Copy its **exact** `Model ID` value.

Optionally paste that ID into `.env`:

```dotenv
NUGEN_MODEL_ID=model_your_exact_id_here
```

If `NUGEN_MODEL_ID` is blank, the Streamlit app and smoke test try to select the Qwen2.5-1.5B deployed model first, then another deployed model if that one is not present.

## 4. Test one inference request before opening Streamlit

```powershell
python scripts/test_inference.py
```

Expected outcome: `INFERENCE SUCCEEDED`, followed by a generated answer, optional confidence score, and usage information.

If the error says model cannot be resolved:

1. Run `python scripts/list_models.py` again.
2. Confirm the model status is exactly `DEPLOYED`.
3. Copy the matching `model_id`, not the model name or base Hugging Face ID.
4. Put that exact value in `NUGEN_MODEL_ID` in `.env`.
5. Re-run the smoke test.

If the list endpoint returns 401/403, check that your API key belongs to the same Nugen account that owns the deployed model.

## 5. Run the Streamlit application

```powershell
streamlit run app.py
```

Open the local URL shown in the terminal (normally `http://localhost:8501`). The sidebar should load deployed aligned models. Select your Qwen2.5-1.5B model and ask an IT support question.

## 6. Evaluate the model

Run the five-question evaluation set:

```powershell
python scripts/run_evaluation.py
```

This sends five inference requests and saves answers to `evaluation/results.csv`. It does not automatically determine factual correctness. Open the CSV and review each answer against the original uploaded Northstar documents. Fill the manual review columns:

- `policy_supported (fill manually)`
- `relevant (fill manually)`
- `unsupported_claims (fill manually)`
- `review_notes`

Do not interpret Nugen's confidence score as a factual accuracy percentage unless Nugen explicitly documents that interpretation.

## 7. Suggested manual test cases

1. Forgotten password: does the answer match the password guide?
2. Lost MFA device: does it follow the source's security/recovery steps without inventing a bypass?
3. Invalid VPN certificate: are troubleshooting actions supported by the VPN guide?
4. IT ticket details: are the required fields accurate?
5. Unknown helpdesk phone number: does the model abstain if the documents do not specify it?

## 8. GitHub preparation

Before pushing:

```powershell
git status
```

Check that `.env` is not listed. Then:

```powershell
git init
git add .
git commit -m "Build Nugen aligned IT support assistant"
```

Create a new empty GitHub repository and follow GitHub's instructions to add the remote and push. Never commit API keys, personal OTP login URLs, or private company documents.

## Project tree

```text
nugen_it_support_assistant/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── services/
│   ├── __init__.py
│   └── nugen_client.py
├── scripts/
│   ├── list_models.py
│   ├── test_inference.py
│   └── run_evaluation.py
└── evaluation/
    └── test_questions.json
```
