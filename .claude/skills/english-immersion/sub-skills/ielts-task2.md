# /ielts-task2

IELTS Academic — Task 2 Essay Writing practice.

## Usage

```
/ielts-task2 [topic]
```

If `[topic]` is omitted, Claude picks one from the IELTS topic pool (see below).

## Flow

1. **Present the prompt** in IELTS format:
   - Topic statement (agree/disagree, discuss both views, advantages/disadvantages, etc.)
   - "You have 40 minutes. Write at least 250 words. Argue your position with reasons and examples."
   - Word count reminder
2. **Wait for the user's essay**. Do not interrupt, do not give mid-writing feedback.
3. **Grade** using `reference/ielts-rubrics.md#task-2`:
   - Task Achievement / 9
   - Coherence and Cohesion / 9
   - Lexical Resource / 9
   - Grammatical Range and Accuracy / 9
   - **Overall Band Score: {{avg}}/9**
4. **Report** in this format:

```
IELTS Task 2 Score: {{overall_band}} ({{TA}}/{{CC}}/{{LR}}/{{GRA}})

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
## YYYY-MM-DD — Task 2 Essay
Topic: {{topic}}
Band Score: {{overall}}/9 (TA: {{n}}, CC: {{n}}, LR: {{n}}, GRA: {{n}})
Weakest dimension: {{dimension}}
Patterns: {{list}}
```

6. **Log errors** to `errors_tagged.md` as usual.

## Essay Types (IELTS Task 2)

IELTS Task 2 questions fall into these types:

### 1. Opinion (Agree/Disagree)
> "Some people believe that X. To what extent do you agree or disagree?"
> "Do you agree or disagree with this statement?"

**Structure**:
- Introduction: Paraphrase the topic + state your position
- Body 1: First reason/support
- Body 2: Second reason/support
- Conclusion: Restate position

### 2. Discussion (Discuss Both Views)
> "Discuss both views and give your own opinion."

**Structure**:
- Introduction: Introduce the debate + state your view
- Body 1: One side's argument
- Body 2: Other side's argument
- Conclusion: Your balanced opinion

### 3. Advantages and Disadvantages
> "What are the advantages and disadvantages of X?"
> "Do the advantages outweigh the disadvantages?"

**Structure**:
- Introduction: Introduce the topic
- Body 1: Advantages
- Body 2: Disadvantages
- Conclusion: Overall judgment (if required)

### 4. Problem-Solution
> "What are the causes of X? How can this problem be solved?"

**Structure**:
- Introduction: State the problem
- Body 1: Causes / contributing factors
- Body 2: Solutions
- Conclusion: Summary

### 5. Two-Part Question
> "What are the reasons for X? What solutions can you suggest?"

**Structure**:
- Introduction: Address both parts
- Body 1: Answer to first question
- Body 2: Answer to second question
- Conclusion: Summary

## Topic pool (seed, will grow)

These are representative IELTS essay topic shapes. Pick one at random if the user doesn't specify.

1. "Some people believe that university students should be required to attend classes. Others believe that going to classes should be optional. To what extent do you agree or disagree?"
2. "In many countries, traditional foods are being replaced by international fast food. Do you think this is a positive or negative development?"
3. "Some people think that governments should spend money on railways rather than roads. To what extent do you agree or disagree?"
4. "The rise of remote work has changed how companies hire. Do the benefits of remote work outweigh the drawbacks?"
5. "Some people believe that the arts (music, painting, literature) should be taught to all children. Others think schools should focus on practical subjects. Discuss both views and give your opinion."
6. "Environmental problems are too big to be solved by individual action. To what extent do you agree or disagree?"
7. "Some people say that the main environmental problem of our time is the loss of particular species of plants and animals. Others say that there are more important environmental problems. Discuss both these views and give your own opinion."
8. "Some people think that parents should teach children how to be good members of society. Others, however, believe that school is the place to learn this. Discuss both these views and give your own opinion."
9. "Some people say that advertising has positive economic effects. Others think it has negative social effects. Discuss both views and give your opinion."
10. "In the future, nobody will buy printed newspapers or books because they will be able to read everything they want online without paying. To what extent do you agree or disagree?"

## Anti-patterns

- **Don't give writing tips during the essay**. The real exam gives no hints.
- **Don't round up scores**. If Lexical Resource is a weak 5, score 5 — the honesty is the point.
- **Don't grade content on whether you agree with the user's position**. Agree or disagree — a clear, supported position scores full content marks regardless of which side.
- **Don't accept essays under 250 words**. If the user writes fewer than 250 words, note it in the report — it's a structural weakness that affects Task Achievement.
- **Don't let the user ignore part of the question**. If the question has multiple parts (e.g., "What are the causes AND what solutions can you suggest?"), make sure both parts are addressed.

## Paragraphing checklist (for grading CC)

- [ ] Introduction (1 paragraph, 2-3 sentences)
- [ ] Body paragraph 1 (1 paragraph, main idea + support)
- [ ] Body paragraph 2 (1 paragraph, main idea + support)
- [ ] Conclusion (1 paragraph, restate position)

If paragraphs are missing or merged, deduct CC points.
