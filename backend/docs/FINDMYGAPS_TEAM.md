# Find My Gaps - Multi-Agent Team Architecture

## Overview

Find My Gaps uses a coordinated team of specialized AI agents to analyze customer feedback and identify product gaps.

## Team Structure

### 1. **Triage Agent** (Coordinator)
- Routes requests to appropriate agents
- Determines best approach for each question
- Decides output format

### 2. **Data Agent**
- Retrieves review data
- Filters by rating, source, keyword
- Manages data access

**Tools:**
- `retrieve_reviews` - Get reviews for a company
- `filter_reviews_by_rating` - Filter by rating range
- `filter_reviews_by_source` - Filter by platform
- `search_reviews_by_keyword` - Search by keyword

### 3. **ML Agent**
- TF-IDF analysis
- Sentiment distribution
- Feature request identification
- Topic clustering

**Tools:**
- `compute_tfidf` - Find important terms
- `analyze_sentiment_distribution` - Rating analysis
- `identify_feature_requests` - Extract requests
- `cluster_similar_reviews` - Group by topic

### 4. **Visualization Agent**
- Determines optimal output format
- Creates visualization specs
- Formats: Markdown, Chart, Table, DataFrame, JSON

**Tools:**
- `determine_best_output_format` - Choose format
- `generate_visualization_spec` - Create spec

### 5. **Verification Agent**
- Validates answer accuracy
- Checks data references
- Ensures quality

**Tools:**
- `verify_answer_accuracy` - Quality check

## Mock Data

Mock reviews available for:
- **Spotify**: 15 reviews (mobile, features, audio quality)
- **Notion**: 10 reviews (performance, offline, export)
- **Slack**: 5 reviews (AI, search, video quality)

## Usage

### Python API

```python
from app.agents.teams import create_findmygaps_team

team = create_findmygaps_team(
    api_key="your-openai-key",
    db_file="memory.db",
    user_id="user123"
)

# Stream analysis
async for event in team.arun(
    "What are the top product gaps for Spotify?",
    stream=True,
    stream_intermediate_steps=True,
    stream_member_events=True
):
    if event.event == RunEvent.run_content:
        print(event.content, end="")
```

### REST API

```bash
# Start server
cd backend
uvicorn app.api.main:app --reload

# Query
curl -X POST http://localhost:8000/api/v1/analysis/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are customers saying about Spotify mobile app?",
    "session_id": "session123"
  }'
```

### Demo Script

```bash
cd backend
export OPENAI_API_KEY="your-key"
python scripts/agno_example/findmygaps_demo.py
```

## Example Queries

### Data Retrieval
- "Show me all reviews for Spotify"
- "Get negative reviews for Notion"
- "Search Slack reviews for 'AI'"

### Analysis
- "What are the top 10 terms in Spotify reviews using TF-IDF?"
- "Analyze sentiment distribution for Notion"
- "What features are customers requesting?"

### Clustering
- "Group Spotify reviews by topic"
- "What are the main themes in negative reviews?"

### Visualization
- "Show rating distribution as a chart"
- "Display feature requests as a table"

### Gaps
- "What are the top 3 product gaps for Notion?"
- "Compare Spotify vs Notion customer satisfaction"

## Workflow

1. **User asks question** → Triage Agent
2. **Triage routes** → Determines which agents needed
3. **Data Agent** → Fetches relevant reviews
4. **ML Agent** → Performs analysis (TF-IDF, sentiment, clustering)
5. **Visualization Agent** → Chooses output format
6. **Verification Agent** → Validates answer
7. **Response** → Streams back to user

## Output Formats

- **Markdown**: Explanations, summaries
- **Bar Chart**: Comparisons, distributions
- **Pie Chart**: Proportions, percentages
- **Line Chart**: Trends over time
- **Table**: Detailed listings
- **DataFrame**: Structured data
- **JSON**: Raw data

## ML Capabilities

### TF-IDF
Identifies most important terms in reviews
```python
# Returns top terms with scores
{"term": "offline", "tfidf_score": 2.34}
```

### Sentiment Analysis
Rating distribution and sentiment breakdown
```python
{
  "positive": 45,
  "neutral": 20,
  "negative": 35,
  "average_rating": 3.2
}
```

### Clustering
Groups reviews by topic (performance, features, UI/UX, etc.)

### Feature Requests
Extracts explicit customer requests using keyword analysis

## Adding More Data

Edit `app/agents/mock_data.py`:

```python
MOCK_REVIEWS = {
    "your_company": [
        {
            "id": 1,
            "rating": 3,
            "text": "Review text here",
            "source": "app_store",
            "date": "2025-10-20",
            "author": "username"
        }
    ]
}
```

## Architecture Benefits

✅ **Modular**: Each agent has specific responsibility
✅ **Scalable**: Add new agents easily
✅ **Flexible**: Triage routes optimally
✅ **Accurate**: Verification validates answers
✅ **Smart**: Auto-detects best output format
✅ **Memory**: Persistent conversation history

## Next Steps

1. Add real data sources (API integrations)
2. Improve ML models (better clustering, NLP)
3. Add more visualizations
4. Implement caching
5. Add export functionality

