import os
import json
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv
import asyncio

from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import murf, deepgram, google

# -------------------
# Load environment variables
# -------------------
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.local")
load_dotenv(dotenv_path)

# -------------------
# Order state
# -------------------
@dataclass
class OrderState:
    drinkType: str = None
    size: str = None
    milk: str = None
    extras: List[str] = field(default_factory=list)
    name: str = None

    def to_json(self):
        # Save file under backend/src/order_summary.json
        backend_src = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
        os.makedirs(backend_src, exist_ok=True)
        filepath = os.path.join(backend_src, "order_summary.json")

        orders = []
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    orders = json.load(f)
            except json.JSONDecodeError:
                orders = []

        orders.append(vars(self))
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(orders, f, indent=2)

        print(f"Order saved to {filepath}")  # Debug output
        return filepath

# -------------------
# Coffee Barista Agent
# -------------------
class CoffeeBarista(Agent):
    def __init__(self):
        super().__init__(
            instructions="You are a friendly barista. Ask questions to collect drinkType, size, milk, extras, and name."
        )
        self.order_state = OrderState()
        self.current_field = "drinkType"

    async def handle_message(self, message):
        value = message.strip()

        # Update the current field with exact user input
        if self.current_field:
            if self.current_field == "extras":
                # Convert "none" to empty list
                if value.lower() != "none":
                    self.order_state.extras.append(value)
            else:
                setattr(self.order_state, self.current_field, value)

        # Determine next missing field
        missing_fields = []
        for k, v in vars(self.order_state).items():
            if k == "extras" and len(v) == 0:
                missing_fields.append(k)
            elif k != "extras" and not v:
                missing_fields.append(k)

        if missing_fields:
            self.current_field = missing_fields[0]
            return f"Please provide: {self.current_field}"
        else:
            # Order complete → save JSON
            filename = self.order_state.to_json()
            summary = json.dumps(vars(self.order_state), indent=2)

            # Reset for next order
            self.order_state = OrderState()
            self.current_field = "drinkType"

            return f"Order complete! Saved to {filename}\nSummary:\n{summary}"

# -------------------
# LiveKit session entrypoint
# -------------------
async def entrypoint(ctx: JobContext):
    session = AgentSession(
        userdata={},  # simple user data
        stt=deepgram.STT(model="nova-3", api_key=os.getenv("DEEPGRAM_API_KEY")),
        llm=google.LLM(model="gemini-2.5-flash", temperature=0.5, api_key=os.getenv("GOOGLE_API_KEY")),
        tts=murf.TTS(
            voice="en-US-matthew",
            style="Conversation",
            api_key=os.getenv("MURF_API_KEY"),
        ),
    )
    await ctx.connect()
    await session.start(agent=CoffeeBarista(), room=ctx.room)

# -------------------
# Run CLI Worker
# -------------------
if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint
        )
    )
