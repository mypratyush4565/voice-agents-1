import os
import json
import asyncio
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import murf, deepgram, google

# -------------------
# Load environment variables
# -------------------
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.local")
load_dotenv(dotenv_path)

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "wellness_log.json")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Ensure file exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

# -------------------
# Wellness Check State
# -------------------
@dataclass
class WellnessCheck:
    date: str
    mood: str = ""
    energy: str = ""
    stress: str = ""
    objectives: List[str] = field(default_factory=list)
    summary: str = ""

    def save_step(self):
        """Save the current state to JSON immediately after each step."""
        # Make partial summary for this step
        self.summary = f"Mood: {self.mood}, Energy: {self.energy}, Stress: {self.stress}, Objectives: {', '.join(self.objectives)}"

        logs = []
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

        logs.append(vars(self))
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)
        print(f"[DEBUG] Step saved: {self.summary}")

# -------------------
# Wellness Agent (Interactive & Step-by-Step)
# -------------------
class WellnessAgent(Agent):
    def __init__(self):
        super().__init__(instructions="You are a supportive health & wellness companion. Ask the following questions step by step: mood, energy, stress, objectives.")
        self.current_check = WellnessCheck(date=datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.step = 0
        self.previous_summary: Optional[str] = None

        # Load last summary if exists
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    logs = json.load(f)
                    if logs:
                        self.previous_summary = logs[-1].get("summary", None)
            except json.JSONDecodeError:
                self.previous_summary = None

    async def handle_message(self, message: str):
        msg = message.strip()
        print(f"[DEBUG] Received: '{msg}' at step {self.step}")  # debug

        # Step 0: start command
        if self.step == 0:
            self.step += 1
            greeting = "Let's start your daily wellness check-in!"
            if self.previous_summary:
                greeting += f" Last time you mentioned: {self.previous_summary}"
            return greeting + "\nHow are you feeling today (mood)?"

        # Step 1: Mood
        elif self.step == 1:
            self.current_check.mood = msg
            self.current_check.save_step()
            self.step += 1
            return "What is your energy level today?"

        # Step 2: Energy
        elif self.step == 2:
            self.current_check.energy = msg
            self.current_check.save_step()
            self.step += 1
            return "Anything stressing you out right now?"

        # Step 3: Stress
        elif self.step == 3:
            self.current_check.stress = msg
            self.current_check.save_step()
            self.step += 1
            return "What are 1–3 objectives for today (comma-separated)?"

        # Step 4: Objectives
        elif self.step == 4:
            self.current_check.objectives = [obj.strip() for obj in msg.split(",")]
            self.current_check.save_step()
            self.previous_summary = self.current_check.summary
            # Reset for next session
            self.current_check = WellnessCheck(date=datetime.now().strftime("%Y-%m-%d %H:%M"))
            self.step = 1  # next session starts from mood
            return f"Check-in complete! Summary saved.\nSummary:\n{self.previous_summary}"

# -------------------
# LiveKit Entrypoint
# -------------------
async def entrypoint(ctx: JobContext):
    session = AgentSession(
        userdata={},

        # Deepgram STT
        stt=deepgram.STT(model="nova-3", api_key=os.getenv("DEEPGRAM_API_KEY")),

        # Google LLM
        llm=google.LLM(model="gemini-2.5-flash", temperature=0.5, api_key=os.getenv("GOOGLE_API_KEY")),

        # Murf TTS
        tts=murf.TTS(voice="en-US-matthew", style="Conversation", api_key=os.getenv("MURF_API_KEY"))
    )

    await ctx.connect()
    await session.start(agent=WellnessAgent(), room=ctx.room)

# -------------------
# Run CLI Worker
# -------------------
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
