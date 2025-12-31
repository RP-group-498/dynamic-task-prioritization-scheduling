"""Configuration and prompt templates for the MCDM system."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
OUTPUTS_DIR = DATA_DIR / "outputs"

# Gemini API configuration
GEMINI_MODEL = "gemini-2.5-flash"

# MongoDB configuration
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = "research_task_db"
MONGODB_COLLECTION = "tasks"

# MCDM weights
URGENCY_WEIGHT = 0.50
IMPACT_WEIGHT = 0.30
DIFFICULTY_WEIGHT = 0.20


def get_extraction_prompt(deadline_input: str, user_days_left: int, user_credits: int, user_weight: int, today_date_str: str) -> str:
    """
    Generate the extraction prompt for Gemini API to extract task information from PDF.

    Args:
        deadline_input: Deadline date string (YYYY-MM-DD)
        user_days_left: Days remaining until deadline
        user_credits: Module credits (1-4)
        user_weight: Assignment weight percentage
        today_date_str: Today's date string (YYYY-MM-DD)

    Returns:
        Formatted prompt string for Gemini API
    """
    return f"""
    You are an intelligent PDF task extraction system. Read this assignment/task PDF carefully and extract the following information:

    **Your Goal:**
    1. Extract the main task/assignment name or title
    2. Extract the task description as a SIMPLE ONE-LINE QUESTION (e.g., "What algorithm should be implemented?", "How to design a database schema?")
    3. Extract all subtasks or requirements listed in the document
    4. Extract any additional context or notes

    **Instructions:**
    - Extract the EXACT text from the PDF wherever possible
    - For task_name: Use the main assignment title or question
    - For task_description: Write a clear, simple ONE-LINE QUESTION that summarizes what needs to be done (this will be used for difficulty analysis)
    - For sub_tasks: List ALL subtasks, requirements, or deliverables mentioned in the PDF
    - For context: Include any important notes, constraints, or additional information

    **Output Format (Strict JSON):**
    {{
      "task_name": "The main assignment title or question from the PDF",
      "task_description": "A simple one-line question that describes what needs to be done (e.g., 'What is the implementation of Binary Search Tree?')",
      "sub_tasks": [
        "First subtask or requirement",
        "Second subtask or requirement",
        "Third subtask or requirement"
      ],
      "context": "Any additional notes, constraints, or important information from the PDF"
    }}

    **Important:**
    - Return ONLY valid JSON (no markdown, no code blocks, no extra text)
    - Ensure all strings are properly escaped
    - If a field is not found in the PDF, use an empty string "" or empty array []

    Return ONLY the raw JSON.
    """
