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

    # Check if running in automated mode (from Electron) or manual mode
    if args.input:
        # AUTOMATED MODE: Read from JSON input file
        print("Running in automated mode (Electron frontend)...")
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                input_data = json.load(f)

            pdf_file = Path(input_data['pdf_path'])
            deadline_input = input_data['deadline']
            credits = int(input_data['credits'])
            weight = int(input_data['weight'])

            # Calculate deadline and days left
            deadline_date = datetime.datetime.strptime(deadline_input, "%Y-%m-%d").date()
            today = datetime.date.today()
            days_left = (deadline_date - today).days

            print(f"PDF: {pdf_file}")
            print(f"Deadline: {deadline_input} ({days_left} days left)")
            print(f"Credits: {credits}, Weight: {weight}%")

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

        # Get user inputs
        deadline_date, credits, weight, days_left, deadline_input = get_user_inputs()

        # Get PDF file
        pdf_file = get_pdf_file()

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

    # Step 1: Extract content from PDF using Gemini
    try:
        print("\n" + "=" * 60)
        print("Step 1: Extracting content from PDF using Gemini API...")
        extracted_json = extractor.extract_text_from_pdf(str(pdf_file), prompt)

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
            print(f"\n--- Extracted Task Information ---")
            print(f"Task Name: {extracted_data.get('task_name', 'N/A')}")
            print(f"Task Description: {extracted_data.get('task_description', 'N/A')}")
            print(f"Number of Subtasks: {len(extracted_data.get('sub_tasks', []))}")
            print(f"Context Available: {'Yes' if extracted_data.get('context') else 'No'}")
            print(f"AI Suggested Difficulty: {extracted_data.get('ai_suggested_difficulty', 'N/A')}")
            print(f"AI Suggested Time (Hours): {extracted_data.get('ai_suggested_time', 'N/A')}")

        except json.JSONDecodeError as e:
            print(f"\nError: Failed to parse JSON from Gemini: {e}")
            print(f"Raw response:\n{extracted_json}")
            return

        # Step 2: Predict difficulty using ML model
        print("\nStep 2: Predicting difficulty using ML model...")
        task_description = extracted_data.get("task_description", "")
        difficulty_rating = predictor.predict_difficulty(task_description)

        # Step 3: Calculate MCDM scores
        print("\nStep 3: Calculating MCDM scores...")
        urgency_score = calculate_urgency_score(days_left)
        impact_score = calculate_impact_score(credits, weight)
        difficulty_score = calculate_difficulty_score(difficulty_rating)
        final_score = calculate_final_score(urgency_score, impact_score, difficulty_score)
        priority_label = get_priority_label(final_score)

        print(f"  -> Urgency Score: {urgency_score}/100 ({days_left} days left)")
        print(f"  -> Impact Score: {impact_score}/100 ({credits} credits x {weight}%)")
        print(f"  -> Difficulty Score: {difficulty_score}/100 (ML rating: {difficulty_rating}/5)")
        print(f"  -> Final MCDM Score: {final_score:.1f}/100")
        print(f"  -> Priority: {priority_label}")

        # Step 4: Build final output JSON
        task_data = {
            "task_name": extracted_data.get("task_name", "Unknown Task"),
            "task_description": extracted_data.get("task_description", ""),
            "sub_tasks": extracted_data.get("sub_tasks", []),
            "context": extracted_data.get("context", ""),
            "ai_suggestions": {
                "ai_suggested_difficulty": extracted_data.get("ai_suggested_difficulty"),
                "ai_suggested_time": extracted_data.get("ai_suggested_time")
            },
            "metrics": {
                "deadline": deadline_input,
                "days_left": days_left,
                "credits": credits,
                "percentage": weight,
                "difficulty_rating": difficulty_rating
            },
            "mcdm_calculation": {
                "urgency_score": urgency_score,
                "impact_score": impact_score,
                "difficulty_score": difficulty_score,
                "final_weighted_score": round(final_score, 2)
            },
            "priority": priority_label
        }

        final_output = {
            "tasks": [task_data]
        }

        # Step 5: Display and save results
        print("\n" + "=" * 60)
        print("FINAL MCDM ANALYSIS RESULT")
        print("=" * 60)
        print(json.dumps(final_output, indent=2, ensure_ascii=False))

        # Save to JSON file
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        output_file = OUTPUTS_DIR / "mcdm_output.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)

        print(f"\n[SUCCESS] MCDM Data saved to JSON: {output_file}")

        # Step 6: Save to MongoDB
        try:
            print("\n" + "=" * 60)
            print("Saving to MongoDB...")
            print("=" * 60)

            db_handler = MongoDBHandler(MONGODB_URI)
            task_id = db_handler.save_task(task_data)

            print(f"[SUCCESS] Task successfully saved to MongoDB!")
            print(f"   Database: {db_handler.db.name}")
            print(f"   Collection: {db_handler.tasks_collection.name}")
            print(f"   Document ID: {task_id}")

            # Display statistics
            stats = db_handler.get_task_statistics()
            print(f"\n[STATS] Database Statistics:")
            print(f"   Total Tasks: {stats.get('total_tasks', 0)}")
            print(f"   High Priority: {stats.get('high_priority', 0)}")
            print(f"   Medium Priority: {stats.get('medium_priority', 0)}")
            print(f"   Low Priority: {stats.get('low_priority', 0)}")

            db_handler.close()

        except Exception as e:
            print(f"\n[WARNING] Failed to save to MongoDB: {e}")
            print("   Data has been saved to JSON file only.")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
