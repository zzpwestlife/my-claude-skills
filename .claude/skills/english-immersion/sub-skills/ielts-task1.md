# /ielts-task1

IELTS Academic — Task 1 Writing practice (Graph Description or Letter Writing).

## Usage

```
/ielts-task1 graph           # Bar chart, line graph, pie chart, or table
/ielts-task1 process         # Diagram (manufacturing/process)
//ielts-task1 map             # Map (location/change over time)
//ielts-task1 letter          # Formal or informal letter
/ielts-task1                 # Random selection
```

If no type is specified, Claude picks from the pool.

## Flow

1. **Present the prompt** in IELTS format:
   - For graphs: describe the visual data + "Write at least 150 words."
   - For letters: describe the scenario + bullet points + "Write at least 150 words."
   - Word count reminder
2. **Wait for the user's response**. Do not hint at key features.
3. **Grade** using `reference/ielts-rubrics.md#task-1`:
   - Task Achievement / 9
   - Coherence and Cohesion / 9
   - Lexical Resource / 9
   - Grammatical Range and Accuracy / 9
   - **Overall Band Score: {{avg}}/9**
4. **Report** in this format:

```
IELTS Task 1 Score: {{overall_band}} ({{TA}}/{{CC}}/{{LR}}/{{GRA}})

Task Achievement: {{n}}/9 — {{evidence}}
Coherence & Cohesion: {{n}}/9 — {{evidence}}
Lexical Resource: {{n}}/9 — {{evidence}}
Grammatical Range: {{n}}/9 — {{evidence}}

Word count: {{count}} words

Biggest single improvement: {{ONE dimension + specific fix}}

Errors tagged this task: {{list of error patterns}}
```

5. **Append to `ielts_progress.md`**:

```
## YYYY-MM-DD — Task 1 {{Graph/Letter}}
Type: {{type}}
Band Score: {{overall}}/9 (TA: {{n}}, CC: {{n}}, LR: {{n}}, GRA: {{n}})
Weakest dimension: {{dimension}}
Patterns: {{list}}
```

6. **Log errors** to `errors_tagged.md` as usual.

---

## Graph Types and Techniques

### Line Graph

**What to describe**:
- Overall trend (rising, falling, stable, fluctuating)
- Starting point vs ending point
- Highest/lowest points
- Key changes over time periods

**Template structure**:
1. **Overview sentence**: "The line graph illustrates the changes in X from [year] to [year]. Overall, there was a significant upward trend in X."
2. **Body paragraph 1**: Cover the first half of the time period
3. **Body paragraph 2**: Cover the second half of the time period
4. **Conclusion**: Summarize the main pattern (no new data)

**Trend vocabulary**:
| Trend | Verbs | Adjectives |
| :--- | :--- | :--- |
| Upward | increased, rose, grew, climbed | significant, dramatic, slight, gradual |
| Downward | decreased, fell, declined, dropped | sharp, steady, modest, slight |
| Stable | remained stable, stayed constant, plateaued | — |
| Fluctuation | fluctuated, varied, oscillated | considerably, significantly |

### Bar Chart

**What to describe**:
- Compare categories (countries, years, groups)
- Identify highest/lowest
- Note similarities/differences between bars

**Template structure**:
1. **Overview sentence**: "The bar chart compares X across [categories] in [year]."
2. **Body paragraph 1**: Describe the highest/lowest or most notable category
3. **Body paragraph 2**: Describe other significant comparisons
4. **Conclusion**: Summarize the main comparison

### Pie Chart

**What to describe**:
- Proportions (percentages)
- Largest/smallest segments
- How segments relate to each other

**Template structure**:
1. **Overview sentence**: "The pie chart shows the breakdown of X in [year]."
2. **Body paragraph 1**: Describe the largest segments
3. **Body paragraph 2**: Describe the remaining segments and any notable patterns
4. **Conclusion**: Summarize the main proportion

### Table

**What to describe**:
- Row vs row comparison
- Highest/lowest values
- Trends across rows (if time-based)

**Template structure**:
1. **Overview sentence**: "The table illustrates X across [categories/years]."
2. **Body paragraph 1**: Group related rows (e.g., developed vs developing countries)
3. **Body paragraph 2**: Cover remaining data
4. **Conclusion**: Summarize key findings

---

## Letter Writing

### Types

1. **Formal letter**: Complaint, application, request to authority
2. **Semi-formal letter**: To a colleague or neighbor you don't know well
3. **Informal letter**: To a friend or family member

### Key differences

| Element | Formal | Informal |
| :--- | :--- | :--- |
| Opening | "I am writing to..." | "Hi [name]," / "Hope you're well," |
| Closing | "Yours faithfully," | "Best regards," / "Love," |
| Vocabulary | "I wish to complain," | "I'm really annoyed about," |
| Tone | Objective, impersonal | Personal, subjective |

### Structure

1. **Opening**: State why you're writing
2. **Body**: Address each bullet point from the prompt
3. **Closing**: Summarize and state desired action

---

## Common Mistakes to Flag

- **Not selecting key features**: Only listing every number
- **Adding opinions**: "I think the graph shows..." — Task 1 is factual, not opinion
- **Using present tense for past data**: Check if the year is in the past
- **Forgetting to compare**: "France was 20%" means nothing without comparison
- **Writing under 150 words**: Minimum word count is a requirement

## Anti-patterns

- **Don't describe every single number**. Select the key figures and highlight trends.
- **Don't write a conclusion with new data**. The conclusion summarizes, it doesn't introduce new information.
- **Don't use the same opening for every essay**. Vary: "As is shown in the graph...", "The chart illustrates...", "It can be seen from the data that..."
- **Don't use informal language in formal letters**. Match the tone to the prompt type.
