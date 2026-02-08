
import sys
import os
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

# Add shared path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
from cag_engine.ollama_client import OllamaClient

logger = logging.getLogger(__name__)

class AgentState(Enum):
    PLANNING = "planning"
    RETRIEVING = "retrieving"
    GENERATING = "generating"
    REFLECTING = "reflecting"
    COMPLETED = "completed"

@dataclass
class ReasoningStep:
    step_id: int
    name: str
    description: str
    thought_process: str
    result: str
    status: str = "pending"

class AgenticCAG:
    def __init__(self, ollama_client: OllamaClient):
        self.client = ollama_client
        self.steps: List[ReasoningStep] = []
        self.current_state = AgentState.PLANNING

    async def run(self, query: str) -> Dict[str, Any]:
        """Run the full agentic loop."""
        self.steps = []
        
        # 1. Planning Step
        plan = await self._plan(query)
        
        # 2. Execution (Retrieval + Reasoning)
        context = []
        for step in plan['steps']:
            step_result = await self._execute_step(step, query, context)
            context.append(step_result)
            
        # 3. Final Answer Generation
        answer = await self._generate_answer(query, context)
        
        # 4. Reflection / Self-Critique
        critique = await self._reflect(query, answer)
        
        # 5. Refinement (if needed, simplified to 1 pass here)
        final_answer = answer
        if critique['needs_improvement']:
            final_answer = await self._refine_answer(query, answer, critique)

        return {
            "query": query,
            "answer": final_answer,
            "original_answer": answer,
            "critique": critique,
            "steps": [s.__dict__ for s in self.steps],
            "context_used": context
        }

    async def _plan(self, query: str) -> Dict[str, Any]:
        """Decompose query into actionable steps."""
        prompt = f"""You are a research planner. Break down this query into 3-4 distinct research steps.
Query: {query}
Return ONLY JSON format: {{ "steps": [ "step 1", "step 2", ... ] }}"""
        
        response, _ = await self.client.generate(prompt)
        
        # Simple parsing (robustness would use strict JSON mode or repair)
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            plan = json.loads(response[start:end])
        except:
            plan = {"steps": ["Analyze query keywords", "Retrieve general context", "Synthesize specific answer"]}
            
        self.steps.append(ReasoningStep(
            step_id=1, name="Planning", description="Decompose query",
            thought_process=f"Breaking down '{query}' into sub-tasks.",
            result=str(plan['steps']), status="completed"
        ))
        return plan

    async def _execute_step(self, step_name: str, query: str, context: List[str]) -> str:
        """Execute a single planned step."""
        context_str = "\n".join(context)
        prompt = f"""Perform this research step: {step_name}
Context so far: {context_str}
Goal for this step: Retrieve or derive information relevant to the main query: {query}."""
        
        response, _ = await self.client.generate(prompt)
        
        self.steps.append(ReasoningStep(
            step_id=len(self.steps) + 1, name="Execution", description=step_name,
            thought_process=f"Executing sub-task: {step_name}",
            result=response[:200] + "...", status="completed"
        ))
        return response

    async def _generate_answer(self, query: str, context: List[str]) -> str:
        """Synthesize final answer."""
        context_str = "\n\n".join(context)
        prompt = f"""Synthesize a comprehensive answer for: "{query}"
Based on these findings:
{context_str}"""
        
        response, _ = await self.client.generate(prompt)
        return response

    async def _reflect(self, query: str, answer: str) -> Dict[str, Any]:
        """Critique the answer."""
        prompt = f"""Critique this answer for accuracy, completeness, and clarity.
Query: {query}
Answer: {answer}
Return ONLY JSON: {{ "score": <0-10>, "critique": "...", "needs_improvement": <bool> }}"""
        
        response, _ = await self.client.generate(prompt)
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            critique = json.loads(response[start:end])
        except:
            critique = {"score": 5, "critique": "Could not parse critique.", "needs_improvement": False}
            
        self.steps.append(ReasoningStep(
            step_id=len(self.steps) + 1, name="Reflection", description="Self-Critique",
            thought_process="Evaluating answer quality.",
            result=f"Score: {critique['score']}, Issues: {critique.get('critique', 'None')}", status="completed"
        ))
        return critique

    async def _refine_answer(self, query: str, answer: str, critique: Dict[str, Any]) -> str:
        prompt = f"""Refine this answer based on the critique.
Query: {query}
Original Answer: {answer}
Critique: {critique.get('critique')}
Improved Answer:"""
        
        response, _ = await self.client.generate(prompt)
        return response
