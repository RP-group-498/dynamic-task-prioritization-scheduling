# Research Text Extraction & MCDM Task Priority System

A Decision Support System that uses Google Gemini AI and Multi-Criteria Decision Making (MCDM) to analyze academic assignments and calculate their priority based on urgency, impact, and difficulty.

## Workflow

This project follows the GitHub Flow workflow:

1.  **Create a branch:** For any new feature or bug fix, a new branch is created from the `main` branch.
2.  **Commit changes:** Make your changes and commit them to your branch.
3.  **Create a pull request:** When you're ready, create a pull request to merge your branch into `main`.
4.  **Code review:** At least one other person must review and approve the pull request.
5.  **Merge:** Once approved, the pull request is merged into `main`.

## Merge Records

A summary of all merges can be found in the Git log. Here are some of the most recent merges:

*   **2026-01-04:** Updated README.md with workflow, file structure, and setup instructions.
*   **2026-01-03:** Integrated frontend with backend API.
*   **2025-12-31:** Added Adaptive Time Estimation module.

*(For a complete history, please refer to the Git log.)*

## Project Structure

```
research-text-extraction/
├── main.py                        # Main application entry point
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── .env                          # API keys (create from .env.example)
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore file
│
├── models/                       # Trained ML models
│   ├── difficulty_predictor_v2.pkl
│   ├── difficulty_predictor_v3.pkl
│   └── sbert_model/
│
├── src/                         # Source code modules
│   ├── adaptive_time_estimator/   # Adaptive time estimation module
│   └── dynamic_task_prioritization/ # Core logic for task prioritization
│
├── frontend/                     # Frontend application
│   ├── main.js                   # Main frontend Javascript file
│   ├── package.json              # Frontend dependencies
│   └── src/
│       ├── assets/
│       └── pages/
│
└── data/                        # Input/output data
    ├── raw/                    # Original PDF files
    └── outputs/                # Generated JSON results
```

## Setup Instructions

### Backend Setup

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd research-text-extraction
    ```

2.  **Create virtual environment** (recommended):
    ```bash
    python -m venv venv

    # Windows
    venv\Scripts\activate

    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables**:
    ```bash
    # Copy the example file
    cp .env.example .env

    # Edit .env and add your Gemini API key
    # Get your key from: https://aistudio.google.com/apikey
    ```

### Frontend Setup

1.  **Navigate to the frontend directory**:
    ```bash
    cd frontend
    ```

2.  **Install dependencies**:
    ```bash
    npm install
    ```

## Usage

1.  **Place your PDF files** in the `data/raw/` directory.

2.  **Run the backend application**:
    ```bash
    python main.py
    ```

3.  **Run the frontend application**:
    ```bash
    cd frontend
    npm start
    ```

4.  **Follow the prompts** in the application to analyze your documents.

5.  **View results**:
    - Results are displayed in the application.
    - JSON output saved to `data/outputs/mcdm_output.json`.

## MCDM Methodology

### Scoring Criteria

1.  **Urgency Score (U)**:
    - Days ≤ 1: U = 100
    - Days ≤ 3: U = 80
    - Days ≤ 7: U = 60
    - Days ≤ 14: U = 40
    - Days > 14: U = 20

2.  **Impact Score (I)**:
    - Raw Impact = Credits × (Weight/100)
    - If Raw ≥ 2.0: I = 100
    - If Raw ≥ 1.5: I = 90
    - If Raw ≥ 1.0: I = 75
    - If Raw ≥ 0.5: I = 50
    - If Raw < 0.2: I = 10
    - Else: I = Raw × 50

3.  **Difficulty Score (D)**:
    - AI estimates 1-5 based on task complexity
    - Normalized: D = Difficulty × 20

### Final Score

```
Final Score = (U × 0.50) + (I × 0.30) + (D × 0.20)
```

### Priority Labels

- **High**: Final Score ≥ 70
- **Medium**: Final Score ≥ 40
- **Low**: Final Score < 40

## Configuration

Edit `src/dynamic_task_prioritization/config.py` to customize:
- MCDM weights
- Gemini model version
- File paths
- Prompt templates

## Requirements

- Python 3.8+
- Node.js
- Google Gemini API key
- Internet connection for API calls

## Troubleshooting

**Error: "Check your GEMINI_API_KEY"**
- Ensure `.env` file exists with valid `GEMINI_API_KEY`
- Verify API key at https://aistudio.google.com/apikey

**Error: "File not found"**
- Ensure PDF files are in `data/raw/` directory
- Check file path and permissions

**ImportError**
- Reinstall dependencies: `pip install -r requirements.txt`
- Ensure virtual environment is activated

## License



## Contributing



## Contact

