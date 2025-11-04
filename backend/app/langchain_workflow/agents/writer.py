"""Writer agents using LangChain."""
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


def create_markdown_writer_agent(model: ChatOpenAI):
    """Writer specialized in markdown reports."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Markdown Writer that creates well-formatted markdown reports.

Guidelines:
- Format output as clean, readable markdown
- Use headers, lists, and emphasis appropriately
- Include data references and numbers
- Be comprehensive but concise"""),
        ("user", "{input}")
    ])
    
    return prompt | model


def create_table_writer_agent(model: ChatOpenAI):
    """Writer specialized in tables and structured data."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Table Writer that creates structured tables and dataframes.

Guidelines:
- Format output as markdown tables
- Include clear column headers
- Align data properly
- Add totals/summaries if relevant"""),
        ("user", "{input}")
    ])
    
    return prompt | model


def create_chart_writer_agent(model: ChatOpenAI):
    """Writer specialized in visualization specifications."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Chart Writer that generates visualization specifications.

Guidelines:
- Provide clear chart specifications
- Include chart type, data, labels
- Suggest appropriate visualization
- Explain what the chart shows"""),
        ("user", "{input}")
    ])
    
    return prompt | model


def create_json_writer_agent(model: ChatOpenAI):
    """Writer specialized in JSON output."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a JSON Writer that creates structured JSON responses.

Guidelines:
- Format output as valid JSON
- Include all relevant data
- Use clear key names
- Add metadata if helpful"""),
        ("user", "{input}")
    ])
    
    return prompt | model

