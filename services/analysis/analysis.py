from crewai import Agent, Task, Crew
from pydantic import BaseModel
import os

class LanguageFeedback(BaseModel):
    grammar: str
    vocabulary: str
    overall: str

def analyze_text(text: str) -> dict:
    agent = Agent(
        role="English Language Evaluator",
        goal="Evaluate grammar and vocabulary usage in learner text",
        backstory="You are an experienced English instructor.",
        llm=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        verbose=False
    )

    task = Task(
        description=f"Analyze this text:\n{text}",
        expected_output="Structured feedback on grammar and vocabulary.",
        output_json=LanguageFeedback,
        agent=agent
    )

    crew = Crew(agents=[agent], tasks=[task])
    result = crew.kickoff()
    print("Analysis result:", result.json)
    return result.json