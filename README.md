# Synapx_FNOLAgent

# FNOL Claims Processing Agent

## Overview
This project implements a lightweight agent to process First Notice of Loss (FNOL) documents.  
It extracts key claim information, identifies missing mandatory fields, routes claims based on predefined rules, and provides an explanation for the routing decision.

## Approaches Implemented

### 1. LLM-Based Extraction
- Uses a large language model to extract structured fields from unstructured FNOL text.
- Suitable for noisy OCR output and varying document layouts.
- Business rules, validation, and routing logic are implemented deterministically in code.

### 2. Rule-Based Extraction (No LLM)
- Uses regex-based parsing for standardized FNOL or ACORD-style forms.
- Fully deterministic and does not require external APIs.
- Best suited for fixed-format documents.

## Design Rationale
LLMs are used only where semantic understanding is required.  
All business-critical decisions such as validation and routing are implemented using explicit rules to ensure reliability, auditability, and explainability.

## Running the Project
- Configure the API key using environment variables for LLM-based execution.
- Install all the requirements before running using - pip install -r requirements.txt
- Toggle between LLM and non-LLM modes in `main.py`.
- Run the application using `python main.py`.

## Notes
Sample FNOL documents contain dummy data and are used only for testing and demonstration.
