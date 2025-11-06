# Retrieval Planner Improvements

## Problem Addressed

The retrieval planner was generating overly complex queries with multiple similar patterns when NLP analysis was needed, such as:

```sql
-- BAD: Multiple similar queries with ILIKE patterns
SELECT * FROM reviews WHERE text ILIKE '%wish%' OR text ILIKE '%would like%' OR text ILIKE '%please add%';
SELECT * FROM reviews WHERE text ILIKE '%search%' OR text ILIKE '%sort%' OR text ILIKE '%filter%';
SELECT * FROM reviews WHERE text ILIKE '%download%' OR text ILIKE '%offline%';
```

This approach was inefficient and redundant since downstream NLP analysis could handle pattern detection better than SQL.

## Solution Implemented

### 1. Query Analysis Integration
- Modified `plan_retrieval()` to accept `QueryAnalysis` parameter
- Updated workflow to pass query analysis results to retrieval planner
- Added proper type hints and imports

### 2. Adaptive Query Complexity
The retrieval planner now adapts its behavior based on `needs_nlp_analysis` flag:

#### NLP Analysis Mode (`needs_nlp_analysis=True`)
- **ONE simple query per table maximum**
- **NO LIKE/ILIKE patterns** - avoid keyword filtering
- **NO multiple similar queries** with different patterns
- Retrieve broad, relevant datasets for downstream NLP processing
- Example: `SELECT * FROM user_review_feedback WHERE company_name = 'Netflix' ORDER BY date DESC LIMIT 2000`

#### Direct Query Mode (`needs_nlp_analysis=False`)
- **LIKE patterns allowed** when appropriate
- **Joins and aggregations** acceptable if they directly answer the query
- **Multiple related queries** acceptable if they serve different purposes
- More complex filtering and processing allowed

### 3. Clear Guidelines
Added explicit examples of what NOT to do in NLP mode:
- ❌ Multiple queries with `ILIKE '%keyword1%' OR ILIKE '%keyword2%'` patterns
- ✅ Single broad query for NLP processing

## Files Modified

1. **`retrieval_planner.py`**
   - Added `query_analysis` parameter
   - Implemented adaptive complexity logic
   - Added detailed guidance and examples

2. **`workflow.py`**
   - Updated to pass query analysis to retrieval planner
   - Added proper imports

3. **Test file created**: `test_retrieval_adaptation.py`
   - Demonstrates the different behaviors
   - Shows comparison between NLP and direct modes

### 4. Adaptive Data Format
The system now also chooses the optimal data format based on analysis needs:
- **NLP Analysis Mode**: Uses `csv` format for better text processing
- **Direct Query Mode**: Uses `json` format for structured data handling

## Benefits

1. **Efficiency**: Reduces redundant queries when NLP analysis is needed
2. **Simplicity**: Cleaner SQL queries that are easier to debug
3. **Flexibility**: Still allows complex queries when appropriate
4. **Better NLP**: Provides richer datasets for downstream analysis in optimal format
5. **Maintainability**: Clear separation of concerns between SQL and NLP
6. **Format Optimization**: CSV for NLP processing, JSON for direct data queries

## Usage

The system now automatically adapts based on the query analysis:
- Gap detection queries → Simple retrieval + NLP analysis
- Direct data queries → Complex SQL allowed
- Mixed queries → Appropriate strategy per component