import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

import main as main_script
from schemas import Quiz, Question, Video


# --- State Definition ---
class AgentState(TypedDict):
    video_url: str
    transcript: List[dict]
    quiz: Quiz
    error: str

# --- Nodes ---

def fetch_transcript_node(state: AgentState):
    """Fetches the transcript from the YouTube URL."""
    url = state["video_url"]
    print(f"--- Fetching transcript for: {url} ---")
    try:
        # Reusing the existing function from main.py
        transcript_data = main_script.get_transcript(url)
        return {"transcript": transcript_data}
    except Exception as e:
        return {"error": str(e)}

def extract_questions_node(state: AgentState):
    """Generates questions from the transcript using Gemini."""
    if state.get("error"):
        return state # Propagate error, could handle gracefully

    transcript = state["transcript"]
    # Provide a capped amount of text to avoid huge context windows if video is long
    # Usually transcripts are list of dicts with 'text', 'start', 'duration'.
    full_text = " ".join([item["text"] for item in transcript[:500]]) # Limit to first 500 lines for demo speed/cost

    print("--- Extracting questions using Gemini ---")
    
    # Initialize LLM
    if not os.environ.get("GOOGLE_API_KEY"):
        # Fallback or error if not set, but assuming it is per user instructions
        pass

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    structured_llm = llm.with_structured_output(Quiz)

    system_prompt = """You are an expert educational content creator. 
    Your task is to analyze the provided cartoon transcript and identifying 'interactive questions' asked by the characters to the audience.
    Commonly in shows like Dora the Explorer or Mickey Mouse Clubhouse, characters ask the viewer to help them.
    
    Extract these questions. If there are no obvious direct questions, generate valid educational questions based on the context.
    Return the result as a strictly formatted Quiz object."""

    user_message = f"Transcript:\n{full_text}"

    try:
        response = structured_llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_message)])
        
        # Determine video metadata if missing (simple fallback)
        if not response.video.url:
             response.video.url = state["video_url"]
        
        return {"quiz": response}
    except Exception as e:
        return {"error": f"LLM Extraction failed: {str(e)}"}

# --- Graph Construction ---

workflow = StateGraph(AgentState)

workflow.add_node("fetch_transcript", fetch_transcript_node)
workflow.add_node("extract_questions", extract_questions_node)

workflow.set_entry_point("fetch_transcript")
workflow.add_edge("fetch_transcript", "extract_questions")
workflow.add_edge("extract_questions", END)

app = workflow.compile()

# --- Entry Point for Testing ---
if __name__ == "__main__":
    # Example usage
    test_url = input("Enter Video URL: ") # Dora The Explorer
    print(f"Starting agent with URL: {test_url}")
    inputs = {"video_url": test_url}
    result = app.invoke(inputs)
    
    if result.get("error"):
        print(f"Error: {result['error']}")
    elif result.get("quiz"):
        print("\n=== GENERATED QUIZ ===")
        print(f"Title: {result['quiz'].video.title}")
        for q in result['quiz'].questions:
            print(f"Q: {q.prompt}")
            print(f"   Answers: {q.choices}")
            print(f"   Correct: {q.choices[q.answer_index]}")
            print("-" * 20)
