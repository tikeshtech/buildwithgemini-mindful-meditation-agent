"""Firestore function tools for Mindful Meditation & Support Assistant."""

from typing import Any, List, Optional
from google.cloud import firestore

# CRITICAL: Hardcode GCP Project ID as a string so Firestore client works both locally and deployed on Agent Platform
# (On Agent Platform, google.auth.default() / GOOGLE_CLOUD_PROJECT returns project number, which breaks Firestore).
PROJECT_ID = "qwiklabs-gcp-01-17eadfbc5e99"

_db_client = None


def get_db_client() -> firestore.Client:
    """Lazy initialize Firestore client with hardcoded project ID."""
    global _db_client
    if _db_client is None:
        _db_client = firestore.Client(project=PROJECT_ID)
    return _db_client


def list_meditation_techniques(
    category: Optional[str] = None, target_role: Optional[str] = None
) -> List[dict]:
    """Retrieve meditation techniques from Firestore database.

    Args:
        category: Optional filter by category (e.g. 'Breathing', 'Body Scan', 'Micro Reset', 'Compassion', 'Evening').
        target_role: Optional filter by target role (e.g. 'General', 'Customer Support', 'Software Engineer', 'Shift Worker').

    Returns:
        A list of meditation technique dictionaries containing id, title, category, target_role, duration_minutes, description, and steps.
    """
    db = get_db_client()
    collection_ref = db.collection("meditation_techniques")
    docs = collection_ref.stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id

        # Apply category filter if provided
        if category and category.lower() not in data.get("category", "").lower():
            continue
        # Apply target_role filter if provided (matching General or specific role)
        if target_role and target_role.lower() != "all":
            doc_role = data.get("target_role", "").lower()
            if doc_role != "general" and target_role.lower() not in doc_role:
                continue

        results.append(data)

    return results


def get_meditation_technique(technique_id: str) -> dict:
    """Retrieve detailed information for a specific meditation technique by ID.

    Args:
        technique_id: Unique ID of the technique (e.g. 'box_breathing', 'body_scan', 'mindful_code_break').

    Returns:
        Dictionary with full details of the technique, or error message if not found.
    """
    db = get_db_client()
    doc_ref = db.collection("meditation_techniques").document(technique_id)
    doc = doc_ref.get()

    if not doc.exists:
        return {"error": f"Meditation technique '{technique_id}' not found."}

    data = doc.to_dict()
    data["id"] = doc.id
    return data


def add_meditation_technique(
    technique_id: str,
    title: str,
    category: str,
    description: str,
    steps: List[str],
    target_role: str = "General",
    duration_minutes: int = 5,
) -> str:
    """Create or update a meditation technique in Firestore database.

    Args:
        technique_id: Unique string identifier for the technique (e.g. 'desk_stretch').
        title: Title of the technique.
        category: Category (e.g. 'Breathing', 'Focus', 'Movement').
        description: Brief overview of benefits and purpose.
        steps: List of step-by-step instructions.
        target_role: Intended role or user type (e.g. 'General', 'Support Agent').
        duration_minutes: Estimated duration in minutes.

    Returns:
        Status message confirming the record was saved.
    """
    db = get_db_client()
    data = {
        "title": title,
        "category": category,
        "description": description,
        "steps": steps,
        "target_role": target_role,
        "duration_minutes": duration_minutes,
    }
    db.collection("meditation_techniques").document(technique_id).set(data)
    return f"Successfully saved meditation technique '{title}' (ID: {technique_id}) to Firestore!"


def log_meditation_session(
    user_id: str, technique_id: str, minutes_spent: int, notes: str = ""
) -> str:
    """Log a user's completed meditation session into Firestore database.

    Args:
        user_id: Unique ID or name of the user.
        technique_id: ID of the technique practiced.
        minutes_spent: Number of minutes spent meditating.
        notes: Optional user notes or feelings after session.

    Returns:
        Status message confirming session log creation.
    """
    db = get_db_client()
    log_data = {
        "user_id": user_id,
        "technique_id": technique_id,
        "minutes_spent": minutes_spent,
        "notes": notes,
        "timestamp": firestore.SERVER_TIMESTAMP,
    }
    doc_ref = db.collection("user_meditation_logs").add(log_data)
    return f"Successfully logged {minutes_spent}-minute meditation session for '{user_id}' (Log ID: {doc_ref[1].id})."


def get_daily_mindfulness_quote() -> str:
    """Fetch a daily inspirational mindfulness and stress relief quote from a live external API.

    Returns:
        A string containing a motivational quote and author for stress relief and focus.
    """
    import json
    import urllib.request

    try:
        req = urllib.request.Request(
            "https://zenquotes.io/api/random",
            headers={"User-Agent": "MindfulMeditationAgent/1.0"},
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if isinstance(data, list) and len(data) > 0:
                quote = data[0].get("q", "")
                author = data[0].get("a", "Unknown")
                return f'"{quote}" — {author}'
    except Exception:
        pass
    return '"Peace comes from within. Do not seek it without." — Buddha'


def get_wellness_advice_slip() -> str:
    """Fetch a random piece of supportive advice or wisdom slip from a live public API to help user navigate daily work stress.

    Returns:
        A string containing a supportive advice message.
    """
    import json
    import os
    import urllib.request

    # Read optional API key from environment variable if configured
    api_key = os.getenv("ADVICE_API_KEY", "")
    url = "https://api.adviceslip.com/advice"
    if api_key:
        url += f"?key={api_key}"

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "MindfulMeditationAgent/1.0"},
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            slip = data.get("slip", {})
            advice = slip.get("advice")
            if advice:
                return f"Wellness Advice: {advice}"
    except Exception:
        pass
    return "Wellness Advice: Take a deep breath and give yourself permission to rest when needed."


