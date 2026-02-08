import re


class FNOLAgent:
    def __init__(self):
        self.mandatory_fields = [
            "Policy Number",
            "Date",
            "Description",
            "Claim Type",
            "Estimated Damage"
        ]

        self.fraud_keywords = ["fraud", "inconsistent", "staged"]

    def _extract(self, pattern, text):
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def extract_fields(self, text):
        return {
            "Policy Number": self._extract(r"Policy Number:\s*([A-Z0-9\-]+)", text),
            "Policyholder Name": self._extract(r"Name of Insured:\s*([A-Za-z ]+)", text),
            "Effective Dates": self._extract(r"Effective Dates:\s*([\d/–\- ]+)", text),

            "Date": self._extract(r"Date of Loss:\s*([\d/]+)", text),
            "Time": self._extract(r"Time of Loss:\s*([\d: ]+(AM|PM))", text),
            "Location": self._extract(r"Location of Loss:\s*(.+)", text),
            "Description": self._extract(r"Description of Accident:\s*([\s\S]+?)\n", text),

            "Claimant": self._extract(r"Claimant Name:\s*([A-Za-z ]+)", text),
            "Third Parties": self._extract(r"Third Party Involved:\s*(Yes|No)", text),
            "Contact Details": self._extract(r"Primary Phone.*?:\s*([\+\d\-]+)", text),

            "Asset Type": self._extract(r"Asset Type:\s*(\w+)", text),
            "Asset ID": self._extract(r"Asset ID:\s*([A-Z0-9\-]+)", text),
            "Estimated Damage": self._extract(r"Estimated Damage Amount:\s*(\d+)", text),

            "Claim Type": self._extract(r"Claim Type:\s*(.+)", text),
            "Attachments": self._extract(r"Attachments Provided:\s*(.+)", text),
            "Initial Estimate": self._extract(r"Initial Estimate:\s*(\d+)", text)
        }

    def check_missing_fields(self, fields):
        return [
            f for f in self.mandatory_fields
            if not fields.get(f)
        ]

    def route_claim(self, fields, missing_fields):
        description = (fields.get("Description") or "").lower()
        claim_type = (fields.get("Claim Type") or "").lower()

        try:
            damage = int(fields.get("Estimated Damage"))
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

    def get_reasoning(self, route, missing_fields):
        if route == "Manual Review" and missing_fields:
            return "Claim routed to Manual Review due to missing mandatory fields."
        if route == "Investigation Flag":
            return "Claim routed to Investigation Flag due to suspicious keywords in description."
        if route == "Specialist Queue":
            return "Claim routed to Specialist Queue because claim type is injury."
        if route == "Fast-track":
            return "Claim routed to Fast-track because estimated damage is below ₹25,000."
        return "Claim routed to Manual Review based on routing rules."

    def process(self, text):
        fields = self.extract_fields(text)
        missing_fields = self.check_missing_fields(fields)
        route = self.route_claim(fields, missing_fields)
        reasoning = self.get_reasoning(route, missing_fields)

        return {
            "extractedFields": fields,
            "missingFields": missing_fields,
            "recommendedRoute": route,
            "reasoning": reasoning
        }
