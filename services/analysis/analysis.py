import os
import asyncio
from crewai import Agent, Task, Crew, Process
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()
import json


# ==================== Output Models ====================

class GrammarFeedback(BaseModel):
    grammar: str

class VocabularyFeedback(BaseModel):
    vocabulary: str

class ClarityFeedback(BaseModel):
    clarity: str

class ToneFeedback(BaseModel):
    tone: str

class CompleteFeedback(BaseModel):
    grammar: str
    vocabulary: str
    clarity: str
    tone: str

# ==================== Analysis Function ====================

def analyze_text(text: str) -> dict:
    """
    Analyze text using 4 parallel agents (grammar, vocabulary, clarity, tone)
    Then gather all feedback using a synthesis agent
    """

    # Define analysis agents with strong role prompts
    grammar_agent = Agent(
        role="Grammar Specialist",
        goal="Evaluate grammar and sentence structure",
        backstory=(
            "You are a seasoned English professor who has spent decades teaching grammar, sentence structure, "
            "and proper punctuation. You are passionate about clear writing and always provide specific, helpful feedback. "
            "You never criticize without offering a better alternative."
        ),
        verbose=False,
        memory=True
    )

    vocabulary_agent = Agent(
        role="Vocabulary Expert",
        goal="Evaluate word choice and vocabulary richness",
        backstory=(
            "You are a linguist who specializes in advanced vocabulary and technical language. You always assess the "
            "richness and precision of word choice, identifying both strong and weak usage. "
            "You never overlook vague or repetitive wording."
        ),
        verbose=False,
        memory=True
    )

    clarity_agent = Agent(
        role="Clarity Analyst",
        goal="Evaluate how clearly the message is communicated",
        backstory=(
            "You are a professional editor focused on making complex writing clear and easy to follow. "
            "You are known for identifying unclear phrases, confusing structures, and logical gaps. "
            "You always look at how the flow and organization impact understanding, and never miss a lack of cohesion."
        ),
        verbose=False,
        memory=True
    )

    tone_agent = Agent(
        role="Tone Evaluator",
        goal="Evaluate tone and emotional undertones",
        backstory=(
            "You are a tone and style specialist trained in communication psychology. "
            "You detect whether a message sounds formal, casual, professional, emotional, hesitant, or confident. "
            "You always describe the tone and emotional feel accurately and never make vague guesses."
        ),
        verbose=False,
        memory=True
    )

    gather_agent = Agent(
        role="Analysis Synthesizer",
        goal="Combine all feedback into one complete analysis",
        backstory=(
            "You are an expert writing evaluator who combines feedback from multiple specialists to produce one clear, "
            "structured review. You always make sure every category (grammar, vocabulary, clarity, tone) is represented in the final output. "
            "You never ignore or omit any contributor’s feedback."
        ),
        verbose=False,
        memory=True
    )

    # Define tasks
    grammar_task = Task(
        description=f"Analyze the grammar and sentence structure in this text:\n\n{text}\n\nProvide detailed feedback on grammatical correctness, sentence structure, punctuation, and any errors found.",
        expected_output="Detailed grammar feedback",
        output_json=GrammarFeedback,
        agent=grammar_agent,
        async_execution=True
    )

    vocabulary_task = Task(
        description=f"Analyze the vocabulary and word choice in this text:\n\n{text}\n\nProvide feedback on word sophistication, vocabulary richness, technical terminology, and word choice quality.",
        expected_output="Detailed vocabulary feedback",
        output_json=VocabularyFeedback,
        agent=vocabulary_agent,
        async_execution=True
    )

    clarity_task = Task(
        description=f"Analyze the clarity and coherence in this text:\n\n{text}\n\nProvide feedback on how clearly the message is communicated, logical flow, organization, and readability.",
        expected_output="Detailed clarity feedback",
        output_json=ClarityFeedback,
        agent=clarity_agent,
        async_execution=True
    )

    tone_task = Task(
        description=f"Analyze the tone and emotional undertones in this text:\n\n{text}\n\nProvide feedback on whether the tone is formal/casual, confident/hesitant, and identify any emotional undertones.",
        expected_output="Detailed tone feedback",
        output_json=ToneFeedback,
        agent=tone_agent,
        async_execution=True
    )

    gather_task = Task(
        description="Combine all feedback from the 4 evaluators (grammar, vocabulary, clarity, tone) into one complete, comprehensive analysis. Ensure all 4 aspects are included in the final output.",
        expected_output="Complete structured feedback covering all 4 aspects (grammar, vocabulary, clarity, tone)",
        output_json=CompleteFeedback,
        agent=gather_agent,
        context=[grammar_task, vocabulary_task, clarity_task, tone_task],
        async_execution=False,
        output_file="analysis_report.json"
    )

    # Create and run the crew
    crew = Crew(
        agents=[grammar_agent, vocabulary_agent, clarity_agent, tone_agent, gather_agent],
        tasks=[grammar_task, vocabulary_task, clarity_task, tone_task, gather_task],
    )

    print("Starting async text analysis...")
    result = crew.kickoff()

    print("Analysis complete!")
    return json.loads(gather_task.output.raw)


