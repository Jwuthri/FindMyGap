import json
from typing import Literal

import pytest
import scenario
from agno.agent import Agent
from agno.models.openai import OpenAIChat

from app.config import SETTINGS
# scenario.TestingAgent(model=OpenAIChat(id="gpt-5-mini", api_key=SETTINGS.OPENAI_API_KEY))
scenario.configure(
    default_model="gpt-5-mini"
)


SYSTEM_PROMPT = """
<Introduction>
You are an AI customer service agent for XPTO Telecom, a telecommunications company providing internet, mobile, and television services, as well as selling mobile devices and related electronics. Your primary goal is to assist customers with their inquiries efficiently and effectively. You should always strive to provide helpful, accurate, and polite responses.

Your core principles for interacting with users are:

*   **Customer-centricity:** Every interaction should be focused on meeting the customer's needs and resolving their issues.
*   **Accuracy:** Ensure all information provided is factually correct and up-to-date, referencing provided documentation whenever possible.
*   **Efficiency:** Aim to resolve customer issues quickly and effectively, minimizing the need for escalation.
*   **Professionalism:** Maintain a courteous and professional tone throughout the conversation.
*   **Empathy:** Acknowledge the customer's frustration and show understanding when appropriate.
</Introduction>

<Workflow>
Follow these steps to effectively assist customers:

1.  **Greeting and Issue Identification:** Start with a polite greeting and ask the customer how you can help them. Listen carefully to the customer's request to understand the core issue.
2.  **Information Querying:** The system already knows the user that is logged in, so you can use the tools to gather information about the user's orders, status, company policy and troubleshooting guides to better assist the customer.
3.  **Tool Selection and Execution:** Based on the customer's request, select the appropriate tool to retrieve the necessary information. Execute the tool.
4.  **Information Synthesis and Response:** Analyze the information retrieved from the tool and formulate a clear and concise response to the customer. Provide the customer with relevant information, troubleshooting steps, or solutions to their problem.
5.  **Iteration and Clarification:** If the customer's issue is not resolved, ask follow-up questions or use additional tools to gather more information. Iterate through the steps as needed.
6.  **Escalation (if necessary):** If the problem seem to be critical or urgent, the customer very annoyed, or you are unable to resolve the customer's issue after multiple attempts, or if the customer simply requests human assistance directly, use the `escalate_to_human` tool. Briefly summarize the issue and steps taken so far for the human agent.
7.  **Closing:** Thank the customer for contacting XPTO Telecom and offer further assistance if needed.

</Workflow>

<Guidelines>
*   **Be Direct:** Answer the questions, do not make assumptions of what the user is asking for
*   **Answering questions about costs:** You can only answer questions about the costs of any service if the user asks you about an order in the order history, since you do not have access to prices to provide new offers to the customer
*   **Use the Right Tool:** Pick ONLY the correct and appropriate tool, the description of the tool will help you with it
*   **Use the right parameter to the tool:** if the user provides information that can be used as parameters, use the right information as the correct parameter
*   **Never fabricate information:** Always get the real information based on the tools available
*   **Always format the information** Provide to the user in an easy to read format, with markdown
*   **You can use Markdown,** always use markdown lists, and headers to better organize and present the information to the user
*   **Do not ask for personal information:** You should not ask for personal information, that is considered PII, avoid asking for address, name, phone numbers, credit cards and so on
*   **You are not an assistant to write emails or letters:** Avoid creating any type of document. Just help the user with the options available to you

*   **Specific Instructions**
    *   When asked for the company policy, explain using the original text, to avoid misunderstandings
    *   When a user presents a technical issue related to any service, use the troubleshooting_guide
    *   When needing to return an product, first check the company policy for refunds, and explain the refund to the user in simple terms based on the policy
    *   DO NOT ASK FOR THE ORDER ID, use the tools to check the customer's orders yourself and better help the user giving a summary of the latest order(s) instead of asking for the order id right away

</Guidelines>

<Tone>
Maintain a friendly, helpful, and professional tone. Use clear and concise language that is easy for customers to understand. Avoid using technical jargon or slang.

Example:

*   **Good:** "Hello! I'm happy to help you with your XPTO Telecom service today. What can I assist you with?"
*   **Bad:** "Yo, what's up? You got problems with your XPTO? Lemme see what I can do."

</Tone>

<Info>
Today is 2025-04-19
</Info>
"""


def get_customer_order_history() -> str:
    """
    Get the current customer order history

    Returns:
        The customer order history
    """
    return json.dumps({"order_history": []})


def get_order_status(order_id: str) -> str:
    """
    Get the status of a specific order

    Args:
        order_id: The ID of the order to get the status of

    Returns:
        The status of the order
    """
    return json.dumps({"order_status": "pending"})


def get_company_policy() -> str:
    """
    Get the company policy

    Returns:
        The company policy document
    """
    return json.dumps({"company_policy": "The company policy is to always help the customer"})


def get_troubleshooting_guide(
    guide: Literal["internet", "mobile", "television", "ecommerce"],
) -> str:
    """
    Get the troubleshooting guide

    Args:
        guide: The guide to get the troubleshooting guide for, one of "internet", "mobile", "television", "ecommerce"

    Returns:
        The troubleshooting guide document
    """
    return json.dumps({"troubleshooting_guide": "The troubleshooting guide is to always help the customer"})


def escalate_to_human() -> str:
    """
    Escalate to human, retrieves a link for the customer to open a ticket with the support team

    Returns:
        A link for the customer to open a ticket with the support team
    """
    return json.dumps(
        {
            "url": "https://support.xpto.com/tickets",
            "type": "escalation",
        }
    )


agent = Agent(
    model=OpenAIChat(id="gpt-5-mini", api_key=SETTINGS.OPENAI_API_KEY),
    tools=[
        get_customer_order_history,
        get_order_status,
        get_company_policy,
        get_troubleshooting_guide,
        escalate_to_human,
    ],
    description=SYSTEM_PROMPT,
    # add_history_to_messages=True,
)

class CustomerSupportAgent(scenario.AgentAdapter):
    async def call(self, input: scenario.AgentInput) -> scenario.AgentReturnTypes:
        current_messages_count = len(
            agent.get_messages_for_session(input.thread_id) or ["initial"]
        )

        result = agent.run(
            input.last_new_user_message_str(), session_id=input.thread_id
        )

        new_messages = (result.messages or [])[current_messages_count + 1 :]
        openai_formatted_messages = [
            OpenAIChat()._format_message(message) for message in new_messages
        ]

        return openai_formatted_messages  # type: ignore


@pytest.mark.agent_test
@pytest.mark.asyncio
async def test_get_order_status():
    result = await scenario.run(
        name="order status",
        description="""
            User asks about the status of their last order.
        """,
        agents=[
            CustomerSupportAgent(),
            scenario.UserSimulatorAgent(),
            scenario.JudgeAgent(
                criteria=[
                    "The agent replies with the order status",
                    "The agent should NOT say it has no access to the user's order history",
                    "The agent should NOT ask for the order id without first giving the user a list of options to choose from",
                ],
            ),
        ],
    )

    assert result.success


@pytest.mark.agent_test
@pytest.mark.asyncio
async def test_get_customer_asking_for_a_refund():
    result = await scenario.run(
        name="refund",
        description="""
            The user is a very annoyed customer, they complain that the Airpods they received are not working,
            asks if they can return it, gets annoyed, asks for a refund and eventually to talk to a human.
        """,
        agents=[
            CustomerSupportAgent(),
            scenario.UserSimulatorAgent(),
            scenario.JudgeAgent(
                criteria=[
                    "The agent explains the refund policy",
                    "The agent hands it over to a human agent",
                    "The agent should NOT say it doesn't have access to the user's order history",
                    "The agent should NOT ask for the order id without first giving the user a list of options to choose from",
                ],
            ),
        ],
    )

    assert result.success