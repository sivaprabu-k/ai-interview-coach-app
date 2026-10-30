
import json

from google import genai

from app.core.config import settings
from app.schemas.ai_questions import (
    InterviewQuestion,
    QuestionGenerationRequest,
    QuestionGenerationResponse,
)


class AIQuestionService:
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not configured")

        self.client = genai.Client(api_key=settings.gemini_api_key)

    def generate_questions(
        self,
        request: QuestionGenerationRequest,
    ) -> QuestionGenerationResponse:
        prompt = f"""
Generate {request.number_of_questions} interview questions for this candidate.

Role: {request.role}
Experience: {request.experience_years} years
Skills: {", ".join(request.skills)}
Difficulty: {request.difficulty}

Return only a JSON object with this structure:
{{
  "role": "{request.role}",
  "questions": [
    {{
      "question": "Question text",
      "expected_answer_points": [
        "Important point 1",
        "Important point 2"
      ]
    }}
  ]
}}

Ensure questions are relevant, technically accurate, and appropriate
for the candidate's experience and requested difficulty.
"""

        response = self.client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
            },
        )
        response_text = (response.text or "").strip()

        if response_text.startswith("```"):
            lines = response_text.splitlines()
            lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            response_text = "\n".join(lines).strip()

        if not response_text:
            raise RuntimeError("Gemini returned an empty response")

        try:
            data = json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Gemini returned invalid JSON. "
                f"Response preview: {response_text[:300]!r}"
            ) from exc

        result = QuestionGenerationResponse.model_validate(data)

        if len(result.questions) != request.number_of_questions:
            raise ValueError("Gemini returned an unexpected number of questions")

        return result
