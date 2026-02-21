"""Main application for MCDM-based task priority analysis."""

import argparse
import datetime
import json
from pathlib import Path

from src.dynamic_task_prioritization.pdf_extractor import GeminiPDFExtractor
from src.dynamic_task_prioritization.difficulty_predictor import DifficultyPredictor
from src.dynamic_task_prioritization.database import MongoDBHandler
from src.dynamic_task_prioritization.mcdm_calculator import (
    calculate_urgency_score,
    calculate_impact_score,
    calculate_difficulty_score,
    calculate_final_score,
    get_priority_label
)
from src.dynamic_task_prioritization.config import get_extraction_prompt, RAW_DATA_DIR, OUTPUTS_DIR, MONGODB_URI


def format_time(minutes):
    """
    Format time in minutes to human-readable format.

    Args:
        minutes: Time in minutes (integer)

    Returns:
        Formatted time string (e.g., "2 hours 30 minutes", "45 minutes", "1 hour")
    """
    if minutes == 0:
        return "0 minutes"

    hours = minutes // 60
    mins = minutes % 60

    if hours > 0 and mins > 0:
        hour_str = "hour" if hours == 1 else "hours"
        min_str = "minute" if mins == 1 else "minutes"
        return f"{hours} {hour_str} {mins} {min_str}"
    elif hours > 0:
        hour_str = "hour" if hours == 1 else "hours"
        return f"{hours} {hour_str}"
    else:
        min_str = "minute" if mins == 1 else "minutes"
        return f"{mins} {min_str}"


def get_user_inputs():
    """
    Collect user inputs for MCDM analysis.

    Returns:
        Tuple of (deadline_date, credits, weight, days_left, deadline_input)
    """
    print("\n--- MANUAL INPUT REQUIRED ---")

    # Get deadline
    while True:
        try:
            deadline_input = input("Enter Deadline (Format YYYY-MM-DD, e.g., 2025-12-01): ").strip()
            deadline_date = datetime.datetime.strptime(deadline_input, "%Y-%m-%d").date()
            break
        except ValueError as e:
            print(f"Error: Invalid date format. Please use YYYY-MM-DD (e.g., 2025-10-25)")

    # Get credits (max 4)
    while True:
        credits_str = input("Enter Module Credits (Integer, Max 4): ").replace('%', '').strip()
        try:
            user_credits = int(credits_str)
            if user_credits > 4:
                print("Error: Maximum credit allowed is 4. Please try again.")
            elif user_credits < 1:
                print("Error: Credits must be at least 1. Please try again.")
            else:
                break
        except ValueError:
            print("Error: Please enter a valid whole number (e.g., 3 or 4).")

    # Get weight percentage
    while True:
        weight_str = input("Enter Assignment Weight % (Integer, e.g., 30): ").replace('%', '').strip()
        try:
            user_weight = int(weight_str)
            if user_weight < 0 or user_weight > 100:
                print("Error: Weight must be between 0 and 100.")
            else:
                break
        except ValueError:
            print("Error: Please enter a valid whole number.")

    # Calculate days left
    today = datetime.date.today()
    user_days_left = (deadline_date - today).days

    print(f"\n-> Calculated Days Left: {user_days_left} days")

    return deadline_date, user_credits, user_weight, user_days_left, deadline_input


def get_pdf_file():
    """
    Prompt user to select a PDF file from data/raw directory.

    Returns:
        Path to the selected PDF file
    """
    pdf_files = list(RAW_DATA_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"\nNo PDF files found in {RAW_DATA_DIR}")
        pdf_name = input("Enter the full path to your PDF file: ").strip()
        return Path(pdf_name)

    print("\n--- Available PDF Files ---")
    for idx, pdf_file in enumerate(pdf_files, 1):
        print(f"{idx}. {pdf_file.name}")

    while True:
        choice = input(f"\nSelect PDF file (1-{len(pdf_files)}) or enter custom path: ").strip()
        try:
            idx = int(choice)
            if 1 <= idx <= len(pdf_files):
                return pdf_files[idx - 1]
            else:
                print(f"Error: Please enter a number between 1 and {len(pdf_files)}")
        except ValueError:
            # User entered custom path
            custom_path = Path(choice)
            if custom_path.exists():
                return custom_path
            else:
                print(f"Error: File not found: {choice}")


def main():
    """Main application entry point."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='MCDM Task Priority Analysis System')
    parser.add_argument('--input', type=str, help='Path to input JSON file (for Electron frontend)')
    args = parser.parse_args()

    input_mode = "pdf"  # Default mode
    pdf_file = None
    text_content = None

    # Check if running in automated mode (from Electron) or manual mode
    if args.input:
        # AUTOMATED MODE: Read from JSON input file (from frontend)
        print("\n" + "=" * 80)
        print("AUTOMATED MODE - Processing request from Frontend")
        print("=" * 80)
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                input_data = json.load(f)

            # Determine input mode from automated request
            if 'text_content' in input_data and input_data['text_content']:
                input_mode = "text"
                text_content = input_data['text_content']
            else:
                input_mode = "pdf"
                pdf_file = Path(input_data['pdf_path'])

            deadline_input = input_data['deadline']
            credits = int(input_data['credits'])
            weight = int(input_data['weight'])

            # Calculate deadline and days left
            deadline_date = datetime.datetime.strptime(deadline_input, "%Y-%m-%d").date()
            today = datetime.date.today()
            days_left = (deadline_date - today).days

            print(f"\nRequest Parameters:")
            if input_mode == "pdf":
                print(f"  Input Mode: PDF File")
                print(f"  File: {pdf_file.name}")
            else:
                print(f"  Input Mode: Direct Text")
                print(f"  Text Length: {len(text_content)} characters")
            
            print(f"  Deadline: {deadline_input} ({days_left} days left)")
            print(f"  Credits: {credits}")
            print(f"  Weight: {weight}%")
            print("=" * 80)

        except Exception as e:
            print(f"Error reading input file: {e}")
            import traceback
            traceback.print_exc()
            return
    else:
        # MANUAL MODE: Interactive prompts
        print("=" * 60)
        print("MCDM Task Priority Analysis System")
        print("=" * 60)

        # Get user inputs for MCDM
        deadline_date, credits, weight, days_left, deadline_input = get_user_inputs()

        # Select input method
        print("\n--- INPUT METHOD ---")
        print("1. Analyze PDF File")
        print("2. Paste Direct Text Content")
        
        while True:
            mode_choice = input("\nSelect input method (1-2): ").strip()
            if mode_choice == "1":
                input_mode = "pdf"
                pdf_file = get_pdf_file()
                break
            elif mode_choice == "2":
                input_mode = "text"
                print("\nPaste your task description/content below (Press Enter then Ctrl+Z and Enter on Windows, or Ctrl+D on Linux to finish):")
                lines = []
                try:
                    while True:
                        line = input()
                        lines.append(line)
                except EOFError:
                    text_content = "\n".join(lines)
                
                if not text_content.strip():
                    print("Error: Text content cannot be empty.")
                    continue
                break
            else:
                print("Error: Please enter 1 or 2.")

    # Initialize Gemini extractor
    try:
        extractor = GeminiPDFExtractor()
    except Exception as e:
        print(f"\nFailed to initialize Gemini client. Exiting.")
        return

    # Initialize ML difficulty predictor
    predictor = DifficultyPredictor()

    # Generate extraction prompt
    today_date_str = datetime.date.today().strftime("%Y-%m-%d")
    prompt = get_extraction_prompt(
        deadline_input=deadline_input,
        user_days_left=days_left,
        user_credits=credits,
        user_weight=weight,
        today_date_str=today_date_str
    )

    # Step 1: Extract content using Gemini
    try:
        print("\n" + "=" * 60)
        if input_mode == "pdf":
            print(f"Step 1: Extracting content from PDF ({pdf_file.name}) using Gemini API...")
            extracted_json = extractor.extract_text_from_pdf(str(pdf_file), prompt)
        else:
            print(f"Step 1: Analyzing direct text content using Gemini API...")
            extracted_json = extractor.analyze_text_content(text_content, prompt)

        # Parse JSON response
        try:
            # Clean the response (remove markdown code blocks if present)
            cleaned_json = extracted_json.strip()
            if cleaned_json.startswith("```json"):
                cleaned_json = cleaned_json.split("```json")[1].split("```")[0].strip()
            elif cleaned_json.startswith("```"):
                cleaned_json = cleaned_json.split("```")[1].split("```")[0].strip()

            extracted_data = json.loads(cleaned_json)
            print("[OK] Successfully parsed extraction data")

            # Display extracted information
            print(f"\n{'='*80}")
            print(f"EXTRACTED TASK INFORMATION")
            print(f"{'='*80}")
            print(f"Task Name: {extracted_data.get('task_name', 'N/A')}")
            print(f"Task Description: {extracted_data.get('task_description', 'N/A')[:100]}...")
            print(f"Number of Subtasks: {len(extracted_data.get('sub_tasks', []))}")

            # Display subtasks with AI estimated time
            subtasks = extracted_data.get('sub_tasks', [])
            if subtasks:
                print(f"\n{'='*80}")
                print(f"SUBTASKS WITH AI TIME ESTIMATES")
                print(f"{'='*80}")
                total_subtask_minutes = 0
                for idx, subtask in enumerate(subtasks, 1):
                    if isinstance(subtask, dict):
                        subtask_name = subtask.get('name', 'Unnamed subtask')
                        # Support both new (estimated_minutes) and old (estimated_hours) formats
                        subtask_minutes = subtask.get('estimated_minutes')
                        if subtask_minutes is None:
                            # Fallback to old format (hours) and convert to minutes
                            subtask_hours = subtask.get('estimated_hours', 0)
                            subtask_minutes = subtask_hours * 60
                        total_subtask_minutes += subtask_minutes
                        print(f"  {idx}. {subtask_name}")
                        print(f"     Estimated Time: {format_time(subtask_minutes)}")
                    else:
                        # Handle old format (plain strings) for backward compatibility
                        print(f"  {idx}. {subtask}")
                        print(f"     Estimated Time: Not available")
                if total_subtask_minutes > 0:
                    print(f"\n{'='*80}")
                    print(f"TOTAL ESTIMATED TIME: {format_time(total_subtask_minutes)}")
                    print(f"{'='*80}")

            print(f"\nAI Suggestions:")
            print(f"  Suggested Difficulty: {extracted_data.get('ai_suggested_difficulty', 'N/A')}")
            print(f"  Suggested Time (Hours): {extracted_data.get('ai_suggested_time', 'N/A')}")

        except json.JSONDecodeError as e:
            print(f"\nError: Failed to parse JSON from Gemini: {e}")
            print(f"Raw response:\n{extracted_json}")
            return

        # Step 2: Predict difficulty using ML model
        print(f"\n{'='*80}")
        print("STEP 2: ML-BASED DIFFICULTY PREDICTION")
        print(f"{'='*80}")
        task_description = extracted_data.get("task_description", "")
        ml_difficulty, ml_confidence = predictor.predict_difficulty(task_description)

        # Hybrid Decision: Use AI difficulty if ML confidence < 50%
        ai_suggested_difficulty = int(extracted_data.get("ai_suggested_difficulty", 3))
        
        if ml_confidence < 50:
            print(f"  [HYBRID DECISION] ML Confidence ({ml_confidence:.1f}%) is low.")
            print(f"  Falling back to AI Suggested Difficulty: {ai_suggested_difficulty}/5")
            difficulty_rating = ai_suggested_difficulty
            difficulty_method = f"AI Suggested (ML Confidence: {ml_confidence:.1f}%)"
        else:
            print(f"  [HYBRID DECISION] Using ML Prediction (Confidence: {ml_confidence:.1f}%)")
            difficulty_rating = ml_difficulty
            difficulty_method = "ML Prediction (High Confidence)"

        # Step 3: Calculate MCDM scores
        print(f"\n{'='*80}")
        print("STEP 3: MCDM PRIORITY CALCULATION")
        print(f"{'='*80}")
        urgency_score = calculate_urgency_score(days_left)
        impact_score = calculate_impact_score(credits, weight)
        difficulty_score = calculate_difficulty_score(difficulty_rating)
        final_score = calculate_final_score(urgency_score, impact_score, difficulty_score)
        priority_label = get_priority_label(final_score)

        print(f"\nScores:")
        print(f"  Urgency Score:    {urgency_score}/100  ({days_left} days left)")
        print(f"  Impact Score:     {impact_score}/100  ({credits} credits × {weight}%)")
        print(f"  Difficulty Score: {difficulty_score}/100  (Method: {difficulty_method})")
        print(f"  Final Difficulty: {difficulty_rating}/5")
        print(f"\n  Final MCDM Score: {final_score:.1f}/100")
        print(f"  Priority Level:   {priority_label}")
        print(f"{'='*80}")

        # Step 4: Build final output JSON
        # Convert numpy types to Python native types for JSON serialization
        import numpy as np

        def convert_to_native(obj):
            """Convert numpy types to Python native types"""
            if isinstance(obj, (np.integer, np.floating)):
                return obj.item()
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_to_native(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_native(item) for item in obj]
            return obj

        task_data = {
            "task_name": extracted_data.get("task_name", "Unknown Task"),
            "task_description": extracted_data.get("task_description", ""),
            "sub_tasks": extracted_data.get("sub_tasks", []),
            "context": extracted_data.get("context", ""),
            "ai_suggestions": {
                "ai_suggested_difficulty": int(extracted_data.get("ai_suggested_difficulty")) if extracted_data.get("ai_suggested_difficulty") is not None else None,
                "ai_suggested_time": float(extracted_data.get("ai_suggested_time")) if extracted_data.get("ai_suggested_time") is not None else None
            },
            "metrics": {
                "deadline": deadline_input,
                "days_left": int(days_left),
                "credits": int(credits),
                "percentage": int(weight),
                "difficulty_rating": int(difficulty_rating)
            },
            "mcdm_calculation": {
                "urgency_score": float(urgency_score),
                "impact_score": float(impact_score),
                "difficulty_score": float(difficulty_score),
                "final_weighted_score": float(round(final_score, 2))
            },
            "priority": priority_label
        }

        final_output = {
            "tasks": [convert_to_native(task_data)]
        }

        # Step 5: Save results
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        output_file = OUTPUTS_DIR / "mcdm_output.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)

        print(f"\n{'='*80}")
        print(f"RESULTS SAVED")
        print(f"{'='*80}")
        print(f"  Output File: {output_file}")
        print(f"  Task Name: {task_data['task_name']}")
        print(f"  Priority: {priority_label}")
        print(f"  Final Score: {final_score:.1f}/100")
        print(f"{'='*80}")

        # Step 6: Save to MongoDB
        try:
            print(f"\n{'='*80}")
            print("SAVING TO MONGODB")
            print(f"{'='*80}")

            db_handler = MongoDBHandler(MONGODB_URI)
            task_id = db_handler.save_task(task_data)

            print(f"  Status: SUCCESS")
            print(f"  Database: {db_handler.db.name}")
            print(f"  Collection: {db_handler.tasks_collection.name}")
            print(f"  Document ID: {task_id}")

            # Display statistics
            stats = db_handler.get_task_statistics()
            print(f"\n  Database Statistics:")
            print(f"    Total Tasks: {stats.get('total_tasks', 0)}")
            print(f"    High Priority: {stats.get('high_priority', 0)}")
            print(f"    Medium Priority: {stats.get('medium_priority', 0)}")
            print(f"    Low Priority: {stats.get('low_priority', 0)}")
            print(f"{'='*80}")

            db_handler.close()

        except Exception as e:
            print(f"\n{'='*80}")
            print(f"MONGODB WARNING")
            print(f"{'='*80}")
            print(f"  Failed to save to MongoDB: {e}")
            print(f"  Data has been saved to JSON file only.")
            print(f"{'='*80}")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
