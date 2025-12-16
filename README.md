# Research Text Extraction & MCDM Task Priority System

A Decision Support System that uses Google Gemini AI and Multi-Criteria Decision Making (MCDM) to analyze academic assignments and calculate their priority based on urgency, impact, and difficulty.

## Features

- **PDF Text Extraction**: Uses Google Gemini 2.5 Pro API to extract text from assignment PDFs
- **MCDM Priority Scoring**: Calculates task priority using three weighted criteria:
  - **Urgency (50%)**: Based on days until deadline
  - **Impact (30%)**: Based on module credits and assignment weight
  - **Difficulty (20%)**: AI-estimated from PDF content complexity
- **Structured Output**: Generates JSON output with task breakdown and metrics
- **Modular Architecture**: Clean, maintainable codebase with separation of concerns

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
│   ├── difficulty_model.pkl
│   ├── vectorizer.pkl
│   ├── all_topics.pkl
│   └── cleaned_training_data.csv
│
├── src/                         # Source code modules
│   ├── __init__.py
│   ├── pdf_extractor.py        # PDF processing with Gemini
│   ├── mcdm_calculator.py      # MCDM calculation utilities
│   └── config.py               # Configuration & prompts
│
└── data/                        # Input/output data
    ├── raw/                    # Original PDF files
    └── outputs/                # Generated JSON results
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd research-text-extraction
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and add your Gemini API key
   # Get your key from: https://aistudio.google.com/apikey
   ```

## Usage

1. **Place your PDF files** in the `data/raw/` directory

2. **Run the application**:
   ```bash
   python main.py
   ```

3. **Follow the prompts**:
   - Enter assignment deadline (YYYY-MM-DD)
   - Enter module credits (1-4)
   - Enter assignment weight percentage
   - Select PDF file to analyze

4. **View results**:
   - Results are displayed in the console
   - JSON output saved to `data/outputs/mcdm_output.json`

## Example Output

```json
{
  "tasks": [
    {
      "task_name": "Implement Binary Search Tree",
      "sub_tasks": [
        "Design BST class structure",
        "Implement insert operation",
        "Implement search operation",
        "Write unit tests"
      ],
      "metrics": {
        "deadline": "2025-12-20",
        "days_left": 4,
        "credits": 4,
        "percentage": 30,
        "difficulty_rating": 4
      },
      "mcdm_calculation": {
        "urgency_score": 60,
        "impact_score_calculated": 100,
        "difficulty_score": 80,
        "final_weighted_score": 76.0
      },
      "priority": "High"
    }
  ]
}
```

## MCDM Methodology

### Scoring Criteria

1. **Urgency Score (U)**:
   - Days ≤ 1: U = 100
   - Days ≤ 3: U = 80
   - Days ≤ 7: U = 60
   - Days ≤ 14: U = 40
   - Days > 14: U = 20

2. **Impact Score (I)**:
   - Raw Impact = Credits × (Weight/100)
   - If Raw ≥ 2.0: I = 100
   - If Raw ≥ 1.5: I = 90
   - If Raw ≥ 1.0: I = 75
   - If Raw ≥ 0.5: I = 50
   - If Raw < 0.2: I = 10
   - Else: I = Raw × 50

3. **Difficulty Score (D)**:
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

Edit `src/config.py` to customize:
- MCDM weights
- Gemini model version
- File paths
- Prompt templates

## Requirements

- Python 3.8+
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

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Contact

[Add contact information here]
