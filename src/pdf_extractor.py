"""PDF extraction using Google Gemini API."""

import os
from pathlib import Path
from google import genai
from google.genai.types import Part

from .config import GEMINI_MODEL


class GeminiPDFExtractor:
    """Handle PDF extraction using Gemini API."""

    def __init__(self):
        """Initialize Gemini client."""
        try:
            # --- START OF FIX ---
            # 1. Retrieve the specific API key from your environment variables
            api_key = os.environ.get("GEMINI_API_KEY")

            # 2. Check if the key exists before trying to use it
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found. Please check your System Environment Variables.")

            # 3. Pass the key directly to the Client
            self.client = genai.Client(api_key=api_key)
            # --- END OF FIX ---

            print("Gemini client initialized successfully.")
        except Exception as e:
            print(f"Error initializing client: {e}. Check your GEMINI_API_KEY.")
            raise

    def extract_text_from_pdf(self, pdf_path: str, extraction_prompt: str) -> str:
        """
        Read a PDF file and extract text using Gemini API.

        Args:
            pdf_path: Path to the PDF file
            extraction_prompt: Prompt for text extraction

        Returns:
            Extracted text from Gemini API

        Raises:
            FileNotFoundError: If PDF file doesn't exist
        """
        pdf_file = Path(pdf_path)

        if not pdf_file.exists():
            raise FileNotFoundError(f"File not found: {pdf_path}")

        print(f"Loading PDF file: {pdf_path}")

        # Read PDF file as binary
        with open(pdf_file, "rb") as f:
            pdf_data = f.read()

        # Create PDF part for Gemini
        pdf_part = Part.from_bytes(
            data=pdf_data,
            mime_type='application/pdf'
        )

        # Combine PDF + Prompt
        contents = [pdf_part, extraction_prompt]

        print(f"Sending request to {GEMINI_MODEL}...")

        # Call Gemini API
        response = self.client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents
        )

        return response.text