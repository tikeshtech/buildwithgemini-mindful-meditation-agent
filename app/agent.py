# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from pathlib import Path

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory import VertexAiMemoryBankService
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.tools import (
    list_meditation_techniques,
    get_meditation_technique,
    add_meditation_technique,
    log_meditation_session,
    get_daily_mindfulness_quote,
    get_wellness_advice_slip,
)

PROJECT_ID = "qwiklabs-gcp-01-17eadfbc5e99"
LOCATION = "us-east1"

# Load Reasoning Engine resource name from deployment_metadata.json if available
deployment_metadata_path = Path(__file__).parent.parent / "deployment_metadata.json"
agent_engine_resource_name = None
memory_bank_id = "6505860879085469696"

if deployment_metadata_path.exists():
    try:
        with open(deployment_metadata_path) as f:
            metadata = json.load(f)
            agent_engine_resource_name = metadata.get("remote_agent_runtime_id")
            if agent_engine_resource_name:
                memory_bank_id = agent_engine_resource_name.split("/")[-1]
    except Exception:
        pass

code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=agent_engine_resource_name
)


# Memory generation callback to extract and store durable facts in Memory Bank after each turn
async def generate_memories_callback(callback_context: CallbackContext):
    try:
        await callback_context.add_session_to_memory()
    except Exception:
        pass
    return None


def memory_bank_service_builder():
    """Build Memory Bank service for deployed container on Agent Runtime."""
    return VertexAiMemoryBankService(
        project=PROJECT_ID,
        location=LOCATION,
        agent_engine_id=memory_bank_id,
    )


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are Mindful Meditation & Support Assistant, a compassionate conversational wellness guide. "
        "Your mission is to guide users—especially customer support agents, engineers, and busy professionals—through peaceful meditation techniques tailored to their role and stress level. "
        "You remember user preferences, health details, and allergies across sessions using Memory Bank."
    ),
    workflow_description=(
        "Analyze the request and return structured UI when appropriate.\n"
        "Capabilities & Guidelines:\n"
        "1. Use `list_meditation_techniques` to discover available meditation routines in Firestore, filtering by category or role if relevant.\n"
        "2. Use `get_meditation_technique` to retrieve step-by-step instructions for a technique.\n"
        "3. Use `add_meditation_technique` if the user wants to save or customize a new meditation routine.\n"
        "4. Use `log_meditation_session` when a user completes a meditation session to record their practice in Firestore.\n"
        "5. Use `get_daily_mindfulness_quote` to fetch inspirational daily quotes for stress relief and peace.\n"
        "6. Use `get_wellness_advice_slip` to fetch supportive advice for managing work stress.\n"
        "7. You can safely write and execute Python code using your code_executor sandbox to solve math, process data, or perform calculations.\n"
        "8. Pay special attention to remembering and honoring all stated user allergies, health preferences, and dietary/environmental restrictions across sessions.\n"
        "9. Present meditation routines with clarity, warmth, and step-by-step encouragement."
    ),
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=code_executor,
    instruction=instruction,
    tools=[
        PreloadMemoryTool(),
        list_meditation_techniques,
        get_meditation_technique,
        add_meditation_technique,
        log_meditation_session,
        get_daily_mindfulness_quote,
        get_wellness_advice_slip,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)



