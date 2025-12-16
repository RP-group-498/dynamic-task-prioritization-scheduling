"""Configuration and prompt templates for the MCDM system."""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
OUTPUTS_DIR = DATA_DIR / "outputs"

# Gemini API configuration
GEMINI_MODEL = "gemini-2.5-pro"

# MCDM weights
URGENCY_WEIGHT = 0.50
IMPACT_WEIGHT = 0.30
DIFFICULTY_WEIGHT = 0.20


def get_extraction_prompt(deadline_input: str, user_days_left: int, user_credits: int, user_weight: int, today_date_str: str) -> str:
    """
    Generate the MCDM extraction prompt for Gemini API.

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
    Read this PDF. You are a Decision Support System using Multi-Criteria Decision Making (MCDM).

    Current Date: {today_date_str}

    **CONTEXT (Provided by User - USE THESE EXACT NUMBERS):**
    - Deadline: {deadline_input}
    - Calculated Days_Left: {user_days_left}
    - Module_Credits: {user_credits}
    - Assignment_Percentage: {user_weight}

    **Goal:** Extract the Task Name/Subtasks from the PDF, determine Difficulty based on the text, and calculate the Priority Score using the provided numbers.

    **Step 1: Normalize Criteria (Using User Data)**
    1. **Urgency (U):** Use calculated 'Days_Left' ({user_days_left}).
       - If {user_days_left} <= 1: U=100
       - If {user_days_left} <= 3: U=80
       - If {user_days_left} <= 7: U=60
       - If {user_days_left} <= 14: U=40
       - Else: U=20

    2. **Impact (I) - ADVANCED HYBRID LOGIC:**
       - Calculate Raw_Impact = {user_credits} * ({user_weight}/100).
       - **Conditional Conditions:**
         - IF Raw_Impact >= 2.0: Set I = 100 (Maximum Critical)
         - IF Raw_Impact >= 1.5: Set I = 90  (Very High)
         - IF Raw_Impact >= 1.0: Set I = 75  (High)
         - IF Raw_Impact >= 0.5: Set I = 50  (Moderate)
         - IF Raw_Impact < 0.2:  Set I = 10  (Negligible)
         - **ELSE (For in-between values):** Use Formula: I = Raw_Impact * 50

    3. **Difficulty (D):** READ THE PDF TEXT. Estimate 1-5 based on complexity.
       - Look for verbs like 'Analyze', 'Prove', 'Implement' -> Higher Difficulty.
       - Look for 'List', 'Describe' -> Lower Difficulty.
       - Normalize D: (Difficulty * 20).

    **Step 2: Calculate MCDM Score**
    Formula: Final_Score = (U * 0.50) + (I * 0.30) + (D * 0.20)

    **Step 3: Assign Label**
    - If Final_Score >= 70 -> Priority: "High"
    - If Final_Score >= 40 -> Priority: "Medium"
    - Else -> Priority: "Low"

    **Output Format (Strict JSON):**
    {{
      "tasks": [
        {{
          "task_name": "Understand the assigment and  Use the main Question Text exactly as written in the PDF as example Given an array of integers numsÂ and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice. You can return the answer in any order. ",
          "sub_tasks": ["Extract all subtasks exactly as listed in the PDF"],
          "metrics": {{
            "deadline": "{deadline_input}",
            "days_left": {user_days_left},
            "credits": {user_credits},
            "percentage": {user_weight},
            "difficulty_rating": "AI Estimated (1-5)"
          }},
          "mcdm_calculation": {{
            "urgency_score": Int,
            "impact_score_calculated": Int,
            "difficulty_score": Int,
            "final_weighted_score": Float
          }},
          "priority": "High/Medium/Low"
        }}
      ]
    }}

    Return ONLY the raw JSON.
    """
