# from typing import Optional

# from agno.agent import Agent
# from agno.eval.accuracy import AccuracyEval, AccuracyResult
# from agno.models.openai import OpenAIChat
# from agno.tools.calculator import CalculatorTools
# from app.config import SETTINGS
# evaluation = AccuracyEval(
#     name="Calculator Evaluation",
#     model=OpenAIChat(id="gpt-5-mini", api_key=SETTINGS.OPENAI_API_KEY),
#     agent=Agent(
#         model=OpenAIChat(id="gpt-5-mini", api_key=SETTINGS.OPENAI_API_KEY),
#         tools=[CalculatorTools()],
#     ),
#     input="What is 10*5 then to the power of 2? do it step by step",
#     expected_output="2500",
#     additional_guidelines="Agent output should include the steps and the final answer.",
#     num_iterations=3,
# )

# result: Optional[AccuracyResult] = evaluation.run(print_results=True)
# assert result is not None and result.avg_score >= 8
# """Run `pip install openai agno memory_profiler` to install dependencies."""

# from agno.agent import Agent
# from agno.eval.performance import PerformanceEval
# from agno.models.openai import OpenAIChat
# from app.config import SETTINGS

# def run_agent():
#     agent = Agent(
#         model=OpenAIChat(id="gpt-5-mini", api_key=SETTINGS.OPENAI_API_KEY),
#         system_message="Be concise, reply with one sentence.",
#     )

#     response = agent.run("What is the capital of France?")
#     print(f"Agent response: {response.content}")

#     return response


# simple_response_perf = PerformanceEval(
#     name="Simple Performance Evaluation",
#     func=run_agent,
#     num_iterations=1,
#     warmup_runs=0,
# )

# if __name__ == "__main__":
#     simple_response_perf.run(print_results=True, print_summary=True)


from typing import Optional

from agno.agent import Agent
from agno.eval.reliability import ReliabilityEval, ReliabilityResult
from agno.models.openai import OpenAIChat
from agno.run.agent import RunOutput
from agno.tools.calculator import CalculatorTools
from app.config import SETTINGS

def factorial():
    agent = Agent(
        model=OpenAIChat(id="gpt-5-mini", api_key=SETTINGS.OPENAI_API_KEY),
        tools=[CalculatorTools()],
    )
    response: RunOutput = agent.run("What is 10!?")
    evaluation = ReliabilityEval(
        name="Tool Call Reliability",
        agent_response=response,
        expected_tool_calls=["factorial"],
    )
    result: Optional[ReliabilityResult] = evaluation.run(print_results=True)
    # result.assert_passed()


if __name__ == "__main__":
    factorial()