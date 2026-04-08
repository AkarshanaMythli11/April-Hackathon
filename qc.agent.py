# qc_agent.py
# QA/QC Agent: Generates QC procedures for new product lines

import os
import json
from dotenv import load_dotenv
import openai

# Load environment variables (API key)
load_dotenv()

# Configure OpenAI (or replace with your own LLM endpoint)
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_qc_procedure(
    product_specs: str,
    manufacturing_process: str,
    regulation: str
) -> dict:
    """
    Main agent function: generate QC procedure, checklist, tests, and compliance summary.
    Returns a dict (JSON‑style) or an error dict.
    """
    prompt = f"""
You are an expert QA/QC engineer for manufacturing.
Your task is to generate a **clear, structured quality control system** for a new product line,
based on the inputs below.

PRODUCT SPECS:
{product_specs}

MANUFACTURING PROCESS:
{manufacturing_process}

APPLICABLE REGULATION/STANDARD:
{regulation}

Return the result in strict JSON format with the following keys:

- product_name (string)
- regulation (string)
- qc_procedure (list of steps, each with step, control_point, method, frequency, acceptance_criteria)
- inspection_checklist (list of items, each with item, procedure, standard, pass_fail_criteria)
- testing_protocols (list of tests, each with test_name, method, sampling, spec_limits, acceptance_rule)
- compliance_summary (short string explaining how the procedure meets {regulation})

Example qc_procedure item:
{{
  "step": "Incoming inspection",
  "control_point": "Verify material lot traceability",
  "method": "Check COC and supplier certificate",
  "frequency": "Lot‑wise",
  "acceptance_criteria": "No deviation from spec and valid COC"
}}

Example inspection_checklist item:
{{
  "item": "Visual appearance",
  "procedure": "Check for burrs, scratches, discoloration",
  "standard": "Internal defect‑code XYZ or ISO 9001",
  "pass_fail_criteria": "No visible defects"
}}

Example testing_protocols item:
{{
  "test_name": "Dimensional inspection",
  "method": "Caliper and micrometer",
  "sampling": "n=5 per lot",
  "spec_limits": "LCL=..., UCL=...",
  "acceptance_rule": "All samples within limits"
}}

Now, based on the provided product, process, and regulation, generate the full JSON object.
Do not add any extra text outside the JSON.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # or "gpt-3.5-turbo" if you prefer
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500,
        )

        content = response.choices[0].message["content"].strip()

        # Clean possible Markdown code block wrapper
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()

        # Parse JSON
        result: dict = json.loads(content)

        # Basic structure check
        required_keys = [
            "product_name", "regulation",
            "qc_procedure", "inspection_checklist", "testing_protocols",
            "compliance_summary"
        ]
        for key in required_keys:
            if key not in result:
                raise ValueError(f"Missing key in JSON: {key}")

        return result

    except Exception as e:
        print("Error during LLM call or JSON parsing:", str(e))
        return {
            "error": str(e),
            "prompt": prompt,
        }


def save_output(qc_data: dict, output_path: str = "qc_procedure.json") -> None:
    """Save the generated QC procedure to a JSON file."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(qc_data, f, indent=2, ensure_ascii=False)
        print(f"✅ QC procedure saved to: {output_path}")
    except Exception as e:
        print(f"❌ Failed to save file {output_path}: {str(e)}")


def main():
    """Example inputs for your product line (simulate your real form/DB inputs)."""
    print("🤖 Quality Control Agent: Generating QC plan for new product line...")

    product_specs = """
    Product: Medical syringe, 10 mL single‑use.
    Material: Polypropylene barrel, silicone‑lubricated plunger.
    Dimensions: OD 14.5 mm ±0.2 mm, length 105 mm.
    Sterility: Sterile, single‑use, non‑pyrogenic.
    """

    manufacturing_process = """
    1. Raw material inspection (barrel, plunger, cap).
    2. Injection molding (barrel and plunger).
    3. Silicone lubrication of plunger.
    4. Assembly (barrel + plunger + cap).
    5. Leak test (pressure test).
    6. Visual inspection.
    7. Packaging and labeling.
    8. Autoclave sterilization (121°C, 15 min).
    """

    regulation = "FDA 21 CFR Part 820 (Quality System Regulation), ISO 13485"

    # Call the agent
    qc_data = generate_qc_procedure(product_specs, manufacturing_process, regulation)

    if "error" not in qc_data:
        print("\n📝 Generated QC Procedure (truncated preview):")
        print(json.dumps(qc_data, indent=2, ensure_ascii=False)[:2000] + " ...")
        save_output(qc_data, "qc_procedure.json")
        print("\n🎉 Agent finished successfully.")
    else:
        print("❌ Agent failed to generate QC procedure:")
        print(qc_data["error"])


if __name__ == "__main__":
    main()
