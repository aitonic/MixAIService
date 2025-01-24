import json

from .base import BasePrompt


class ClarificationQuestionPrompt(BasePrompt):
    """Prompt to generate Python code with SQL from a dataframe."""

    template_path = "clarification_questions_prompt.tmpl"

    def validate(self, output) -> bool:
        try:
            output = output.replace("```json", "").replace("```", "")
            json_data = json.loads(output)
            return isinstance(json_data, list)
        except json.JSONDecodeError:
            return False
