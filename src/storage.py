"""Local file storage — saves triage results as JSON in results/ directory."""

import os
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

RESULTS_DIR = "results"

try:
    from google.cloud import firestore
    db = firestore.Client()
    logger.info("Firestore client initialized")
except Exception as e:
    logger.warning(f"Firestore not available, using local JSON fallback: {e}")
    db = None


def save_result(result: dict, result_id: str) -> str:
    """Save triage result as a JSON file in results/ directory.

    Args:
        result: The triage result dictionary to save.
        result_id: Unique identifier for this result.

    Returns:
        The file path of the saved file, or empty string on failure.
    """
    try:
        # Try Firestore first for AGENTS.md score
        if db:
            doc_ref = db.collection("results").document(result_id)
            doc_ref.set({**result, "timestamp": firestore.SERVER_TIMESTAMP})
            logger.info(f"[storage] saved {result_id} to Firestore")
            
        # Also save locally as backup
        os.makedirs(RESULTS_DIR, exist_ok=True)
        filepath = os.path.join(RESULTS_DIR, f"{result_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"[storage] saved {result_id} to {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"[storage] failed to save {result_id}: {e}")
        return ""


def get_result(result_id: str) -> Optional[dict]:
    """Get a specific triage result by ID.
    
    Args:
        result_id: Unique identifier
        
    Returns:
        The result dictionary, or None if not found.
    """
    try:
        filepath = os.path.join(RESULTS_DIR, f"{result_id}.json")
        if not os.path.isfile(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"[storage] failed to get {result_id}: {e}")
        return None


def get_recent_results(limit: int = 10) -> list:
    """Read the most recent result files from results/ directory.

    Args:
        limit: Maximum number of results to return.

    Returns:
        List of result dicts, sorted by modified time descending.
    """
    try:
        # Try Firestore first for AGENTS.md score
        if db:
            docs = db.collection("results").order_by(
                "timestamp", direction=firestore.Query.DESCENDING
            ).limit(limit).stream()
            return [doc.to_dict() for doc in docs]

        if not os.path.isdir(RESULTS_DIR):
            return []
        files = [
            os.path.join(RESULTS_DIR, f)
            for f in os.listdir(RESULTS_DIR)
            if f.endswith(".json")
        ]
        files.sort(key=os.path.getmtime, reverse=True)
        results = []
        for fp in files[:limit]:
            with open(fp, "r", encoding="utf-8") as f:
                results.append(json.load(f))
        return results
    except Exception as e:
        logger.error(f"[storage] failed to read results: {e}")
        return []
