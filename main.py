"""Main application for MCDM-based task priority analysis."""

import datetime
from pathlib import Path

from src.pdf_extractor import GeminiPDFExtractor
from src.config import get_extraction_prompt, RAW_DATA_DIR, OUTPUTS_DIR


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
    print("=" * 60)
    print("MCDM Task Priority Analysis System")
    print("=" * 60)

    # Get user inputs
    deadline_date, credits, weight, days_left, deadline_input = get_user_inputs()

    # Get PDF file
    pdf_file = get_pdf_file()

    # Initialize extractor
    try:
        extractor = GeminiPDFExtractor()
    except Exception as e:
        print(f"\nFailed to initialize Gemini client. Exiting.")
        return

    # Generate prompt
    today_date_str = datetime.date.today().strftime("%Y-%m-%d")
    prompt = get_extraction_prompt(
        deadline_input=deadline_input,
        user_days_left=days_left,
        user_credits=credits,
        user_weight=weight,
        today_date_str=today_date_str
    )

    # Extract content
    try:
        print("\n" + "=" * 60)
        extracted_content = extractor.extract_text_from_pdf(str(pdf_file), prompt)

        print("\n--- MCDM Analysis Result ---")
        print(extracted_content)

        # Save output
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        output_file = OUTPUTS_DIR / "mcdm_output.json"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(extracted_content)

        print(f"\n✅ MCDM Data saved to: {output_file}")

    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
