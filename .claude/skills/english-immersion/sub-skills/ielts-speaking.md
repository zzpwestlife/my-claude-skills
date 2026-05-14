# /ielts-speaking

IELTS Academic — Speaking Part 2 (Long Turn) and Part 3 (Discussion) practice.

## Usage

```
/ielts-speaking            # Part 2 by default
/ielts-speaking part2      # Cue card topic
/ielts-speaking part3      # Discussion questions
```

## Speaking Test Structure

| Part | Duration | What happens |
| :--- | :--- | :--- |
| Part 1 | 4-5 min | Introduction + familiar topics (hometown, work, hobbies) |
| Part 2 | 3-4 min | Long turn on a cue card topic (1 min prep + 2 min talk) |
| Part 3 | 4-5 min | Discussion on abstract ideas related to Part 2 topic |

This skill focuses on **Part 2** (Long Turn) and **Part 3** (Discussion).

---

## Part 2: Long Turn Practice

### Usage

```
/ielts-speaking part2 [topic-category]
```

If no category is specified, Claude picks from the pool.

### Flow

1. **Present the cue card**:

```
CUE CARD

Describe [topic].

You should say:
- [bullet point 1]
- [bullet point 2]
- [bullet point 3]
- [bullet point 4]

Explain why this is important to you / what you think about it.
```

2. **Tell the user**: "You have 1 minute to prepare. You can make notes if you like. Then speak for 1-2 minutes."
3. **Wait for the user's response**. He can either:
   - Type what he would say
   - Record himself, transcribe, paste transcript
   - Paste his speaking notes
4. **Grade** using `reference/ielts-rubrics.md#speaking-part-2`:
   - Fluency and Coherence / 9
   - Lexical Resource / 9
   - Grammatical Range and Accuracy / 9
   - Pronunciation / 9 (self-rated)
5. **Report** in this format:

```
IELTS Speaking Part 2 Score: {{overall_band}} ({{FC}}/{{LR}}/{{GRA}}/{{P}})

Fluency & Coherence: {{n}}/9 — {{evidence}}
  ✓ spoke for 1-2 minutes: {{yes/no, duration}}
  ✓ used cohesive devices: {{list}}
  ✓ covered all bullet points: {{list}}
Lexical Resource: {{n}}/9 — {{evidence}}
Grammatical Range: {{n}}/9 — {{evidence}}
Pronunciation (self-rated): {{n}}/9

Biggest single improvement: {{ONE dimension + specific fix}}
```

6. **Append to `ielts_progress.md`**:

```
## YYYY-MM-DD — Speaking Part 2
Topic: {{topic}}
Band Score: {{overall}}/9 (FC: {{n}}, LR: {{n}}, GRA: {{n}}, P: {{n}})
Weakest dimension: {{dimension}}
```

---

## Part 3: Discussion Practice

### Usage

```
/ielts-speaking part3 [topic]
```

If no topic is specified, Claude generates discussion questions based on a Part 2 topic.

### Flow

1. **Present the topic context**: "In Part 2, you talked about [topic]. Now let's discuss some more abstract ideas related to this."
2. **Ask 3-4 discussion questions**:
   - "Do you think [broader question]?"
   - "In what ways might [comparative question]?"
   - "How do you think [future/hypothetical question]?"
3. **Wait for the user's responses** to each question.
4. **Grade** using the same four criteria, but with higher expectations for vocabulary and ideas.

**Report** in this format:

```
IELTS Speaking Part 3 Score: {{overall_band}} ({{FC}}/{{LR}}/{{GRA}}/{{P}})

Fluency & Coherence: {{n}}/9 — {{evidence}}
Lexical Resource: {{n}}/9 — {{evidence}}
Grammatical Range: {{n}}/9 — {{evidence}}
Pronunciation (self-rated): {{n}}/9

Biggest single improvement: {{ONE dimension + specific fix}}
```

---

## Part 2 Cue Card Topics (Seed Pool)

### People

1. "Describe a person you know who has an interesting job.
   You should say who this person is, what their job is, how you know them, and explain why you think their job is interesting."

2. "Describe a leader or politician you admire.
   You should say who this person is, what their position is, what they have done, and explain why you admire them."

3. "Describe a friend from your childhood.
   You should say who this person is, how you met, what you used to do together, and explain what made this friendship memorable."

### Places

4. "Describe a city you have visited that you would like to live in.
   You should say which city it is, when you visited it, what impressed you about it, and explain why you would like to live there."

5. "Describe a café or restaurant you enjoy going to.
   You should say where it is, what kind of food it serves, how often you go there, and explain why you enjoy it."

6. "Describe a beautiful natural place you have visited.
   You should say where it is, what you did there, what the scenery was like, and explain how you felt about this place."

### Activities

7. "Describe a hobby or activity you enjoy doing in your free time.
   You should say what the hobby is, when you first started it, how often you do it, and explain why you enjoy it."

8. "Describe a type of music that is popular in your country.
   You should say what type of music it is, when it became popular, who enjoys this music, and explain why it is popular."

9. "Describe a film or TV programme that you watched recently.
   You should say what it was, when you watched it, what it was about, and explain whether you would recommend it."

### Objects

10. "Describe something valuable that you own.
    You should say what it is, how you got it, how long you have had it, and explain why it is valuable to you."

11. "Describe a gift you have given or received recently.
    You should say what it was, who gave/received it, when it happened, and explain how you felt about it."

12. "Describe a book you have recently read.
    You should say what it was about, who wrote it, why you decided to read it, and explain whether you would recommend it."

### Events

13. "Describe a celebration or event you recently attended.
    You should say what it was, where it took place, who was there, and explain how you felt about it."

14. "Describe a news story that interested you.
    You should say what it was about, how you heard about it, why it interested you, and explain whether it changed your opinion about something."

15. "Describe a memorable event in your life.
    You should say when and where it happened, what occurred, who was involved, and explain why it was memorable."

---

## Speaking Techniques to Drill

### Part 2 Techniques

1. **Use the 1 minute prep time wisely**:
   - Write down 3-4 keywords for each bullet point
   - Plan your structure: Introduction → Bullet 1 → Bullet 2 → Bullet 3 → Bullet 4 → Why it matters

2. **Cover all bullet points** — each one is a separate speaking point

3. **Extend beyond the bullet points** — add an extra sentence about why it matters or how you feel

4. **Use discourse markers**:
   - "Well, the first thing I'd like to talk about is..."
   - "Moving on to my second point..."
   - "As for the third aspect..."
   - "Finally, I'd like to mention..."
   - "To sum up, I'd say this is important because..."

5. **Don't read from notes** — glance, then speak

### Part 3 Techniques

1. **Give longer, more detailed answers** than Part 1
2. **Use complex structures**: conditionals, passive voice, cleft sentences
3. **Speculate**: "If more people did X, then Y might happen..."
4. **Give examples**: "For instance, in Japan, people tend to..."
5. **Compare and contrast**: "On one hand... On the other hand..."
6. **Use abstract vocabulary**: society, culture, environment, economy

---

## Self-Rating Guide for Pronunciation

| Band | Description |
| :---: | :--- |
| 9 | Native-like — all sounds clear, natural intonation |
| 8 | Few minor issues — mostly clear, occasional non-native stress |
| 7 | Generally clear — some errors in word/sentence stress |
| 6 | Understandable — occasional mispronunciation but doesn't impede |
| 5 | Usually understandable — some persistent errors |

Ask the user to self-rate honestly:
- Did you stumble on any words?
- Did your intonation sound natural?
- Were you able to speak without long pauses?

---

## Anti-patterns

- **Don't rush Part 2**. The target is 1-2 minutes of continuous speech.
- **Don't ignore bullet points**. Each one is a required part of the answer.
- **Don't use informal language in Part 3**. It's a formal discussion, not casual chat.
- **Don't self-rate too generously**. Be honest — a 5/9 on Fluency when you paused 10 times is more useful than a false 7.
