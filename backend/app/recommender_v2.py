import json
import os
from typing import Dict, Union
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

load_dotenv()

class BraFittingRAG:
    def __init__(self):
        self.knowledge_base = self.load_knowledge_base()
        self.llm = ChatOpenAI(
            temperature=0.0,
            model="gpt-3.5-turbo",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.issue_labels = [
            "band_riding_up",
            "straps_falling",
            "straps_digging",
            "cup_wrinkling",
            "quadraboob",
            "gore_floating"
        ]
        self.parser = JsonOutputParser()
        self.prompt = PromptTemplate.from_template(
            """
            You are a bra fitting expert. You will receive a customer description and a set of known fitting cases (recommendation contexts).

            Step 1: Compare the description against the known fitting cases.
            Step 2: If you find any context that seems to fit well (e.g., similar measurements and issues), reuse its recommendation, reasoning, and fit_tips.
            Step 3: If none of the known cases fit the description, create a new recommendation, reasoning, and fit_tips based on your expertise.

            Here are the known fitting cases (in JSON array format):
            {contexts}

            Your response must be a valid JSON with this structure:
            {{
              "recommendation": "...",
              "reasoning": "...",
              "fit_tips": "...",
              "identified_issues": [ ... ]
            }}

            Description: "{query}"
            """
        )
        self.chain = self.prompt | self.llm | self.parser

    def load_knowledge_base(self):
        try:
            with open('app/data/bra_fitting_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("[Warning] Knowledge base file not found.")
            return []

    def get_recommendation(self, query: str) -> Union[Dict, str]:
        if not query.strip():
            return {"error": "Query is empty. Please describe your measurements and issues."}

        try:
            result = self.chain.invoke({
                "query": query,
                "contexts": json.dumps(self.knowledge_base)
            })
            result["confidence"] = 1.0
            return result
        except Exception as e:
            print(f"[LLM error] {e}")
            return {
                "recommendation": None,
                "confidence": 0.0,
                "reasoning": "LLM failed to process the input.",
                "fit_tips": "Check our sizing guide or try again later.",
                "identified_issues": []
            }
