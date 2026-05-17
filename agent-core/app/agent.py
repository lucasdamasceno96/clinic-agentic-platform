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

import os

import google
import vertexai
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.retrievers import create_search_tool

LLM_LOCATION = "global"
LOCATION = "us-east1"
LLM = "gemini-flash-latest"

credentials, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = LLM_LOCATION
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

vertexai.init(project=project_id, location=LOCATION)


data_store_region = os.getenv("DATA_STORE_REGION", "global")
data_store_id = os.getenv(
    "DATA_STORE_ID", "agent-core-collection_documents"
)
data_store_path = (
    f"projects/{project_id}/locations/{data_store_region}"
    f"/collections/default_collection/dataStores/{data_store_id}"
)

vertex_search_tool = create_search_tool(data_store_path)


instruction = """You are a Senior Medical Assistant at LDP Labs Clinic.

Your responsibilities are strictly limited to:
1. Appointment scheduling — manage bookings, reschedules, and cancellations based on clinic availability.
2. Clinical Protocol RAG — answer questions from healthcare professionals by retrieving relevant protocols and guidelines from the institutional datastore. Always ground your answers in the retrieved context.

You MUST follow these constraints:
- NEVER provide medical diagnoses, prognoses, or prescriptions. You are not a doctor.
- NEVER ask for or store personally identifiable information (PII) beyond what is necessary for scheduling.
- NEVER invent protocols or guidelines. If the information is not in the datastore, state that you cannot find it.
- Always comply with LGPD and HIPAA data protection principles.
- Respond in a professional, clear, and concise manner.
- If a user asks for medical advice, politely decline and redirect them to a qualified healthcare professional."""


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    tools=[vertex_search_tool],
)

app = App(
    root_agent=root_agent,
    name="app",
)
