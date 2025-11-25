# ======================================================
# 🌐 DAY 4: TEACH-THE-TUTOR (WEB DEVELOPMENT EDITION)  # 🌐 CHANGED FOR WEB DEVELOPMENT
# ======================================================

import logging
import json
import os
import asyncio
from typing import Annotated, Literal, Optional
from dataclasses import dataclass

print("\n" + "💻" * 50)  # 🌐 CHANGED FOR WEB DEVELOPMENT
print("🚀 WEB DEVELOPMENT TUTOR - DAY 4 TUTORIAL")  # 🌐 CHANGED FOR WEB DEVELOPMENT
print("💡 agent.py LOADED SUCCESSFULLY!")
print("💻" * 50 + "\n")  # 🌐 CHANGED FOR WEB DEVELOPMENT

from dotenv import load_dotenv
from pydantic import Field
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    WorkerOptions,
    cli,
    function_tool,
    RunContext,
)

# 🔌 PLUGINS
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")
load_dotenv(".env.local")

# ======================================================
# 📚 KNOWLEDGE BASE (WEB DEV DATA)  # 🌐 CHANGED FOR WEB DEVELOPMENT
# ======================================================

CONTENT_FILE = "webdev_content.json"  # 🌐 CHANGED FOR WEB DEVELOPMENT

# 🌐 NEW WEB DEVELOPMENT TOPICS  # 🌐 CHANGED FOR WEB DEVELOPMENT
DEFAULT_CONTENT = [
  {
    "id": "html",
    "title": "HTML Basics",
    "summary": "HTML (HyperText Markup Language) is used to structure content on the web using tags like <h1>, <p>, <div>, etc.",
    "sample_question": "What does HTML stand for and what is its purpose?"
  },
  {
    "id": "css",
    "title": "CSS Styling",
    "summary": "CSS (Cascading Style Sheets) is used to style and design websites including layout, colors, and responsiveness.",
    "sample_question": "What is the role of CSS in web development?"
  },
  {
    "id": "js",
    "title": "JavaScript",
    "summary": "JavaScript is a programming language that makes websites interactive. It can modify HTML/CSS dynamically.",
    "sample_question": "Why is JavaScript important in web development?"
  },
  {
    "id": "frontend",
    "title": "Frontend Development",
    "summary": "Frontend development focuses on the client-side of websites — what users see and interact with.",
    "sample_question": "Name any two frontend frameworks."
  }
]

def load_content():
    """
    📖 Checks if web dev JSON exists. 
    If NO: Generates it from DEFAULT_CONTENT.
    """  # 🌐 CHANGED FOR WEB DEVELOPMENT
    try:
        path = os.path.join(os.path.dirname(__file__), CONTENT_FILE)
        
        if not os.path.exists(path):
            print(f"⚠️ {CONTENT_FILE} not found. Generating web dev data...")  # 🌐 CHANGED FOR WEB DEVELOPMENT
            with open(path, "w", encoding='utf-8') as f:
                json.dump(DEFAULT_CONTENT, f, indent=4)
            print("✅ Web Dev content file created successfully.")  # 🌐 CHANGED FOR WEB DEVELOPMENT
            
        with open(path, "r", encoding='utf-8') as f:
            data = json.load(f)
            return data
            
    except Exception as e:
        print(f"⚠️ Error managing content file: {e}")
        return []

COURSE_CONTENT = load_content()

# ======================================================
# 🧠 STATE MANAGEMENT
# ======================================================

@dataclass
class TutorState:
    current_topic_id: str | None = None
    current_topic_data: dict | None = None
    mode: Literal["learn", "quiz", "teach_back"] = "learn"
    
    def set_topic(self, topic_id: str):
        topic = next((item for item in COURSE_CONTENT if item["id"] == topic_id), None)
        if topic:
            self.current_topic_id = topic_id
            self.current_topic_data = topic
            return True
        return False

@dataclass
class Userdata:
    tutor_state: TutorState
    agent_session: Optional[AgentSession] = None 

# ======================================================
# 🛠️ TUTOR TOOLS
# ======================================================

@function_tool
async def select_topic(
    ctx: RunContext[Userdata], 
    topic_id: Annotated[str, Field(description="The ID of the topic to study (HTML, CSS, JS, frontend)")]  # 🌐 CHANGED FOR WEB DEVELOPMENT
) -> str:
    state = ctx.userdata.tutor_state
    success = state.set_topic(topic_id.lower())
    
    if success:
        return f"Topic set to {state.current_topic_data['title']}! Do you want to Learn, take a Quiz, or Teach it back?"
    else:
        available = ", ".join([t["id"] for t in COURSE_CONTENT])
        return f"Topic not found. Available topics: {available}"

@function_tool
async def set_learning_mode(
    ctx: RunContext[Userdata], 
    mode: Annotated[str, Field(description="Mode to switch to: learn, quiz, teach_back")]
) -> str:
    
    state = ctx.userdata.tutor_state
    state.mode = mode.lower()
    
    agent_session = ctx.userdata.agent_session 
    
    if agent_session:
        if state.mode == "learn":
            agent_session.tts.update_options(voice="en-US-matthew", style="Promo")
            instruction = f"Explain: {state.current_topic_data['summary']}"
            
        elif state.mode == "quiz":
            agent_session.tts.update_options(voice="en-US-alicia", style="Conversational")
            instruction = f"Ask: {state.current_topic_data['sample_question']}"
            
        elif state.mode == "teach_back":
            agent_session.tts.update_options(voice="en-US-ken", style="Promo")
            instruction = "Ask the user to explain the topic in simple words."

        else:
            return "Invalid mode."
    else:
        instruction = "No session found."

    print(f"🔄 SWITCHING MODE -> {state.mode.upper()}")
    return f"Switched to {state.mode}. {instruction}"

@function_tool
async def evaluate_teaching(
    ctx: RunContext[Userdata],
    user_explanation: Annotated[str, Field(description="User explanation")]
) -> str:
    print(f"📝 EVALUATING: {user_explanation}")
    return "Evaluate the explanation, score out of 10, and correct mistakes."

# ======================================================
# 🧠 AGENT DEFINITION
# ======================================================

class TutorAgent(Agent):
    def __init__(self):
        topic_list = ", ".join([f"{t['id']} ({t['title']})" for t in COURSE_CONTENT])
        
        super().__init__(
            instructions=f"""
            You are a Web Development Tutor.  # 🌐 CHANGED FOR WEB DEVELOPMENT
            
            📚 TOPICS: {topic_list}
            
            Modes:
            - Learn → Explain the topic
            - Quiz → Ask a question
            - Teach_back → Ask the user to teach you
            
            Always ask which topic the user wants first.
            """,
            tools=[select_topic, set_learning_mode, evaluate_teaching],
        )

# ======================================================
# 🎬 ENTRYPOINT
# ======================================================

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    print("\n" + "💻" * 25)  # 🌐 CHANGED FOR WEB DEVELOPMENT
    print("🚀 STARTING WEB DEV TUTOR SESSION")  # 🌐 CHANGED FOR WEB DEVELOPMENT
    print(f"📚 Loaded {len(COURSE_CONTENT)} topics!")

    userdata = Userdata(tutor_state=TutorState())

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew", 
            style="Promo",
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        userdata=userdata,
    )
    
    userdata.agent_session = session
    
    await session.start(
        agent=TutorAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )

    await ctx.connect()

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
