# Domain-Aligned IT Support Assistant Using Nugen Intelligence

An end-to-end domain alignment project developed as part of a technical assignment provided by **Nugen Intelligence**. **[Access the Live Application Here](https://northsas.streamlit.app/)**
 
The project demonstrates how a base language model can be adapted for a specific business domain using company-specific documentation, deployed through the Nugen platform, and integrated into a Streamlit application for interactive inference.

> **Important clarification:** Nugen Intelligence is the actual company that provided this technical assignment and its platform for completing the task. Northsas Example Company is a fictional company created exclusively for this demonstration. It does not represent a real organization or an actual Nugen customer.

## 1. Problem Statement

As part of the technical assignment provided by Nugen Intelligence, the objective was to explore its domain alignment capabilities and build a working application using an aligned language model.

For this demonstration, I selected the IT support domain and created a fictional organization named **Northsas Example Company**.

In a typical organization, employees may require assistance with:


- VPN connectivity problems.
- Device troubleshooting.
- Software installation requests.
- IT support tickets and escalation procedures.

The objective was to build an AI-powered IT Support Assistant that can respond to questions related to these scenarios using the domain-specific information provided in the fictional company's IT support documents.

This project demonstrates the complete workflow:

1. Preparing domain-specific documents.
2. Uploading documents to Nugen Intelligence.
3. Performing domain alignment using a selected base model.
4. Deploying the aligned model.
5. Connecting to the deployed model through the Nugen inference API.
6. Building a Streamlit application for user interaction.
7. Testing and evaluating model responses.

## 2. Dataset and Documentation

Since this is a demonstration project, I created two fictional IT support documents for Northsas Example Company.

These documents were used as the domain-specific inputs for the alignment workflow on the Nugen platform.


### Document 1: VPN, Device, Software, and IT Ticket Guide

This document covers:

- VPN connectivity troubleshooting.
- Device-related support procedures.
- Software installation requests.
- Common technical issues.
- IT ticket submission and escalation procedures.

**Dataset clarification:**

- Company name: Northsas Example Company (fictional).
- Documents: self-created fictional IT support documents.
- Purpose: Demonstrating domain alignment using Nugen Intelligence.
- These documents do not contain actual company policies or confidential organizational information.

## 3. Base Model Selection

The base model selected for this project was:

**Qwen/Qwen2.5-1.5B-Instruct**

This model was used as the foundation for the domain alignment process.

The objective was to adapt the base model toward the IT support use case using the fictional documentation prepared for this assignment.

## 4. Domain Alignment Using Nugen Intelligence

The domain alignment workflow was performed using the Nugen Intelligence platform.

The following steps were completed:

1. Created an alignment project on the Nugen platform.
2. Prepared  fictional IT support documents for the Northsas Example Company use case.
3. Uploaded the documents to the platform.
4. Verified that the uploaded documents were successfully processed and marked as ready.
5. Selected `Qwen/Qwen2.5-1.5B-Instruct` as the base model.
6. Configured and executed the domain alignment process.
7. Waited for the alignment process to complete.
8. Generated the aligned model for the IT support use case.

This workflow was used to explore how Nugen's domain alignment capabilities can adapt a language model to a specific business domain.

## 5. Model Deployment

After completing the domain alignment process, the resulting aligned model was deployed through Nugen Intelligence.

Deployment workflow:

1. Selected the completed aligned model.
2. Initiated the model deployment process.
3. Waited for the deployment status to become `DEPLOYED`.
4. Retrieved the deployed model information.
5. Used the deployed model ID for subsequent inference requests.

**Deployment details:**

| Component | Details |
|---|---|
| Platform | Nugen Intelligence |
| Base model | Qwen2.5-1.5B-Instruct |
| Use case | Fictional IT Support Assistant |
| Deployment status | DEPLOYED |

## 6. Inference – Python Integration with Nugen

After deployment, I integrated the aligned model into a Python application using the Nugen chat completions API.

**API endpoint:**

`https://api.nugen.in/api/v3/inference/chat/completions`

The Python application communicates with the deployed model by sending:

- API authentication credentials.
- The deployed aligned model ID.
- System instructions.
- User messages.

The model processes the request and returns a generated response, which is displayed in the Streamlit application.

### Example Python API Integration

```python
import requests

API_URL = "https://api.nugen.in/api/v3/inference/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": ALIGNED_MODEL_ID,
    "messages": [
        {
            "role": "system",
            "content": (
                "You are an IT Support Assistant for the fictional "
                "Northsas Example Company. Answer IT support "
                "questions clearly and professionally."
            )
        },
        {
            "role": "user",
            "content": "How can I troubleshoot a VPN connection issue?"
        }
    ],
    "temperature": 0.2
}

response = requests.post(
    API_URL,
    headers=headers,
    json=payload,
    timeout=60
)

response.raise_for_status()

result = response.json()

print(result)
```

The application uses environment variables to manage the API key and deployed model ID securely instead of hardcoding credentials in the source code.

## 7. Model Evaluation and Testing

After deployment, I tested the aligned model with questions related to the  uploaded IT support documents.

The objective was to observe whether the model could generate relevant and useful responses for the selected IT support use case.

### Sample Evaluation Questions

| Category | Test Question |
|---|---|
| Account Access | How can I reset my password? |
| Account Security | What should I do if my account is locked? |
| VPN Support | How can I troubleshoot a VPN connection issue? |
| Device Support | How do I report a device-related issue? |
| Software Support | How can I request software installation? |
| Ticket Management | How do I submit an IT support ticket? |

### Evaluation Criteria

The responses were reviewed based on:

- Relevance to the user's question.
- Clarity and usefulness of generated answers.
- Consistency with the intended IT support use case.
- Ability to handle different IT support scenarios.
- Handling of questions outside the supported domain.


### Limitations

- The project uses only the  fictional IT support documents.
- The evaluation dataset is relatively small.
- Generated responses may contain inaccurate or unsupported information.
- Model alignment does not guarantee that every answer will exactly follow the uploaded documents.
- The assistant should not replace a human IT support team.
- A larger dataset and a more comprehensive evaluation framework would be required for production use.

## 8. Streamlit Application

To make the deployed aligned model accessible through a simple interface, I developed a Streamlit web application.

### Application Features

- Interactive chat interface.
- User-friendly question input.
- Integration with the deployed Nugen aligned model.
- Real-time response generation through API requests.
- Environment-based configuration for API credentials and model information.

### Application Screenshots

Add screenshots of the actual working application to the repository.

**Streamlit application interface:**

1. Streamlit home page.
2. User submitting an IT support question.
3. Model-generated response.
4. Example questions covering different IT support categories.

### Run the Application Locally

**Step 1: Clone the repository**

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Northsas-it-assistant
```

**Step 2: Create a virtual environment**

For Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

For Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

**Step 3: Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 4: Configure environment variables**

Create a `.env` file in the project root:

```env
NUGEN_API_KEY=your_nugen_api_key
NUGEN_API_URL=https://api.nugen.in/api/v3/inference/chat/completions
NUGEN_MODEL_ID=your_deployed_aligned_model_id
```

Replace the placeholder values with your actual Nugen API credentials and deployed aligned model ID.

**Important:** Never commit your `.env` file or expose your API key in a public repository.

**Step 5: Run the Streamlit application**

```bash
streamlit run app.py
```

## 9. Project Structure

```text
Northsas-it-assistant/
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── services/
│   ├── __init__.py
│   └── nugen_client.py
│
├── scripts/
│   ├── list_models.py
│   ├── test_inference.py
│   └── run_evaluation.py
│
├── evaluation/
│   └── test_questions.json
│
└── screenshots/
    └── streamlit_app.png
```

## 10. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application development |
| Nugen Intelligence | Domain alignment, deployment, and inference platform |
| Qwen2.5-1.5B-Instruct | Base language model |
| Streamlit | User interface |
| Requests | API communication |
| JSON | API payloads and evaluation questions |

## 11. Future Improvements

Some potential improvements for this project include:

- Expanding the fictional IT support dataset with more detailed documentation.
- Implementing automated evaluation against expected answers.
- Adding conversation history.
- Improving unsupported-question detection.
- Adding document retrieval and source references for verifiable answers.
- Evaluating model performance across a larger set of test questions.

## 12. Conclusion

This project was developed as part of the technical assignment provided by **Nugen Intelligence**.

It demonstrates an end-to-end workflow for exploring domain alignment and building an application around a deployed language model.

Using fictional IT support documents created for Northsas Example Company, I performed domain alignment with `Qwen/Qwen2.5-1.5B-Instruct`, deployed the aligned model through Nugen Intelligence, integrated it into a Python application using the Nugen inference API, and developed a Streamlit interface for interactive testing.

Through this assignment, I gained practical experience with:

- Domain-specific dataset preparation.
- Language model domain alignment.
- Model deployment.
- API-based inference integration.
- Streamlit application development.
- Model response evaluation.

---

**Assignment Platform:** Nugen Intelligence  
**Project:** Northsas IT Support Assistant  
**Company represented in the demo:** Northsas Example Company (Fictional)  
**Base Model:** Qwen2.5-1.5B-Instruct  
**Application Framework:** Streamlit  
**Programming Language:** Python
