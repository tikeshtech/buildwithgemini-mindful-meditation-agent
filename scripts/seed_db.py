#!/usr/bin/env python3
"""Seed script for Mindful Meditation & Support Assistant Firestore database.

IMPORTANT: The GCP Project ID is explicitly hardcoded as a string
('qwiklabs-gcp-01-17eadfbc5e99') to prevent project number resolution issues on Vertex AI Agent Runtime.
"""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-01-17eadfbc5e99"
COLLECTION_NAME = "meditation_techniques"

SEED_DATA = [
    {
        "id": "box_breathing",
        "title": "Box Breathing for Instant Calm",
        "category": "Breathing",
        "target_role": "General",
        "duration_minutes": 4,
        "recommended_stress_level": "High",
        "description": "A simple 4-count breathing technique used to lower stress and quickly regain focus.",
        "steps": [
            "Inhale through your nose for 4 seconds.",
            "Hold your breath for 4 seconds.",
            "Exhale slowly through your mouth for 4 seconds.",
            "Hold your lungs empty for 4 seconds.",
            "Repeat for 4 cycles."
        ]
    },
    {
        "id": "body_scan",
        "title": "Deep Muscle Release Body Scan",
        "category": "Mindfulness",
        "target_role": "Support Rep",
        "duration_minutes": 10,
        "recommended_stress_level": "Moderate",
        "description": "Systematically release physical tension from head to toe after long support shifts.",
        "steps": [
            "Sit or lie down comfortably and close your eyes.",
            "Bring attention to your feet and toes, releasing any tension.",
            "Move your awareness up through your legs, hips, and lower back.",
            "Soften your shoulders, neck, and jaw.",
            "Breathe deeply into your entire body and notice a wave of relaxation."
        ]
    },
    {
        "id": "mindful_code_break",
        "title": "5-Minute Micro Reset for Developers",
        "category": "Focus",
        "target_role": "Developer",
        "duration_minutes": 5,
        "recommended_stress_level": "Moderate",
        "description": "A quick mental clarity reset between complex coding or debugging sessions.",
        "steps": [
            "Step away from screen and close your eyes.",
            "Rest your palms comfortably on your thighs.",
            "Take 3 deep diaphragmatic breaths.",
            "Focus on the physical sensation of breathing without thinking about code.",
            "Open your eyes slowly feeling refreshed."
        ]
    },
    {
        "id": "loving_kindness",
        "title": "Compassion & Patience Meditation",
        "category": "Stress Relief",
        "target_role": "Support Rep",
        "duration_minutes": 8,
        "recommended_stress_level": "High",
        "description": "Cultivate emotional balance and patience when handling challenging customer support interactions.",
        "steps": [
            "Sit quietly and place a hand over your heart.",
            "Silently repeat: 'May I be calm, may I be patient, may I be at peace.'",
            "Direct the same well wishes toward your colleagues and callers.",
            "Notice the easing of tension in your chest."
        ]
    },
    {
        "id": "nighttime_wind_down",
        "title": "Evening Wind Down & Unplug",
        "category": "Sleep",
        "target_role": "General",
        "duration_minutes": 12,
        "recommended_stress_level": "Low",
        "description": "Transition out of work mode and prepare your mind for restful sleep.",
        "steps": [
            "Dim lights and turn off all screens.",
            "Practice 4-7-8 breathing: inhale for 4s, hold for 7s, exhale for 8s.",
            "Reflect on 3 small things that went well today.",
            "Allow thoughts to drift away as you relax into bed."
        ]
    }
]

def seed_firestore():
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection(COLLECTION_NAME)

    print(f"Seeding '{COLLECTION_NAME}' collection...")
    for item in SEED_DATA:
        doc_id = item["id"]
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(item)
        print(f"  ✓ Seeded document: {doc_id} ('{item['title']}')")

    print(f"\nSuccessfully seeded {len(SEED_DATA)} meditation techniques into Firestore!")

if __name__ == "__main__":
    seed_firestore()
