import json
import re
from typing import Dict, List, Union
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


class BraFittingRAG:
    def __init__(self):
        self.knowledge_base: List[Dict] = []
        self.similarity_threshold = 0.1  # Lowered to allow more flexible matching
        self.vectorizer = TfidfVectorizer()
        self.load_knowledge_base()

    def load_knowledge_base(self):
        try:
            with open('app/data/bra_fitting_data.json', 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
        except FileNotFoundError:
            print("[Warning] Knowledge base file not found. Initializing empty base.")
            self.knowledge_base = []

    def extract_measurements(self, text: str) -> List[str]:
        """
        Using regex to extracts measurements from text like '34B', '75cm', '80 kg', etc.
        """
        return re.findall(r'\b\d{2,3}[A-Za-z]*\b', text)

    def calculate_fit_similarity(self, query: str, context: Dict) -> float:
        """
        Combines TF-IDF cosine similarity and measurement matching to compute fit similarity.
        """
        query_text = query.lower()
        context_text = context.get('description', '').lower()

        # Calculate TF-IDF cosine similarity
        try:
            # convert to vector
            vectors = self.vectorizer.fit_transform([query_text, context_text])
            cosine_sim = (vectors[0] @ vectors[1].T).A[0][0]
        except Exception:
            # Fallback if TF-IDF fails
            cosine_sim = SequenceMatcher(None, query_text, context_text).ratio()

        # Calculate measurement overlap ratio
        query_meas = set(self.extract_measurements(query_text))
        context_meas = set(self.extract_measurements(context_text))
        if query_meas and context_meas:
            # Jaccard similarity formula
            match_ratio = len(query_meas & context_meas) / len(query_meas | context_meas)
            # 70% for semantic comparison and 30% for accuracy of measurements.
            return 0.7 * cosine_sim + 0.3 * match_ratio

        return cosine_sim

    def identify_fit_issues(self, query: str) -> List[str]:
        """
        Identifies bra fit issues based on keyword matching.
        Returns standardized issue codes that align with the knowledge base.
        """
        issues = []
        synonyms = {
            "band_riding_up": ["riding up", "band too loose", "back lifting", "band climbs"],
            "straps_falling": ["straps falling", "slipping straps", "loose straps"],
            "straps_digging": ["digging straps", "straps hurting", "shoulder pain", "straps tight"],
            "cup_wrinkling": ["wrinkling", "wrinkled cups", "loose cups", "extra space in cups"],
            "quadraboob": ["overflow", "spilling", "bulging", "quadraboob"],
            "gore_floating": ["gore not flat", "gore lifting", "center not touching", "floating gore"]
        }

        lowered = query.lower()
        for issue_code, keywords in synonyms.items():
            if any(keyword in lowered for keyword in keywords):
                issues.append(issue_code)

        return issues

    def get_recommendation(self, query: str) -> Union[Dict, str]:
        """
        Returns the best matching bra fit recommendation based on user input.
        """
        if not query.strip():
            return {
                "error": "Query is empty. Please describe your measurements and issues."
            }

        identified_issues = self.identify_fit_issues(query)
        relevant_matches = []

        for context in self.knowledge_base:
            similarity = self.calculate_fit_similarity(query, context)
            if similarity >= self.similarity_threshold:
                relevant_matches.append({
                    "context": context,
                    "similarity": similarity
                })

        if not relevant_matches:
            return {
                "recommendation": None,
                "confidence": 0.0,
                "reasoning": "No suitable match found in the knowledge base.",
                "fit_tips": "Consider checking our sizing guide or consulting a bra fitter.",
                "identified_issues": identified_issues
            }

        best_match = max(relevant_matches, key=lambda x: x["similarity"])
        return {
            "recommendation": best_match["context"].get("recommendation", "Unknown"),
            "confidence": round(best_match["similarity"], 2),
            "reasoning": best_match["context"].get("reasoning", "Matched based on description and measurements."),
            "fit_tips": best_match["context"].get("fit_tips", "Refer to our fitting tips for guidance."),
            "identified_issues": identified_issues
        }
