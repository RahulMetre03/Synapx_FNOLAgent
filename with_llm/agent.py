import json
import re
from google import genai


class FNOLLLMAgent:
    def __init__(self, api_key):
        self.client = genai.Client(api_key)
        self.mandatory_fields = [
            "Policy Number",
            "Date",
            "Description",
            "Claim Type",
            "Estimated Damage"
        ]
        self.fraud_keywords = ["fraud", "inconsistent", "staged"]

    def _prompt(self):
        return """
You are an insurance document information extraction agent.

You will be given raw text from a FNOL (First Notice of Loss) document.
Your task is ONLY to extract structured information from the text.

Extract the following fields if present.

Policy Information:
- Policy Number
- Policyholder Name
- Effective Dates

Incident Information:
- Date
- Time
- Location
- Description

Involved Parties:
- Claimant
- Third Parties
- Contact Details

Asset Details:
- Asset Type
- Asset ID
- Estimated Damage

Other Fields:
- Claim Type
- Attachments
- Initial Estimate

Rules:
- If a field is not present, return its value as null.
- Do NOT infer or guess missing values.
- Do NOT apply business rules or routing logic.

Output format (STRICT JSON):
{
  "extractedFields": {
    "Policy Number": null,
    "Policyholder Name": null,
    "Effective Dates": null,
    "Date": null,
    "Time": null,
    "Location": null,
    "Description": null,
    "Claimant": null,
    "Third Parties": null,
    "Contact Details": null,
    "Asset Type": null,
    "Asset ID": null,
    "Estimated Damage": null,
    "Claim Type": null,
    "Attachments": null,
    "Initial Estimate": null
  }
}
"""

    def _extract_fields_llm(self, text):
        response = self.client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=f"{self._prompt()}\n\nFNOL DOCUMENT:\n{text}"
        )

        raw_text = response.text
        match = re.search(r"\{[\s\S]*\}", raw_text)

        if not match:
            raise ValueError("No JSON found in LLM response")

        parsed = json.loads(match.group())
        return parsed["extractedFields"]

    def _check_missing_fields(self, fields):
        return [
            f for f in self.mandatory_fields
            if not fields.get(f)
        ]

    def _route(self, fields, missing_fields):
        description = (fields.get("Description") or "").lower()
        claim_type = (fields.get("Claim Type") or "").lower()

        try:
            damage = float(fields.get("Estimated Damage"))
        except (TypeError, ValueError):
            damage = None

        if missing_fields:
            return "Manual Review"

        if any(word in description for word in self.fraud_keywords):
            return "Investigation Flag"

        if claim_type == "injury":
            return "Specialist Queue"

        if damage is not None and damage < 25000:
            return "Fast-track"

        return "Manual Review"

    def _reasoning(self, route, missing_fields):
        if route == "Manual Review" and missing_fields:
            return "Claim routed to Manual Review because mandatory fields are missing."
        if route == "Investigation Flag":
            return "Claim routed to Investigation Flag due to suspicious keywords in the description."
        if route == "Specialist Queue":
            return "Claim routed to Specialist Queue because claim type is injury."
        if route == "Fast-track":
            return "Claim routed to Fast-track because estimated damage is below ₹25,000."
        return "Claim routed to Manual Review due to unmet routing conditions."

    def process(self, text):
        fields = self._extract_fields_llm(text)
        missing_fields = self._check_missing_fields(fields)
        route = self._route(fields, missing_fields)
        reasoning = self._reasoning(route, missing_fields)

        return {
            "extractedFields": fields,
            "missingFields": missing_fields,
            "recommendedRoute": route,
            "reasoning": reasoning
        }
