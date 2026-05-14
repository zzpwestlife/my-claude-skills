# /ielts-read-aloud

IELTS Speaking — Read Aloud practice task (warm-up for pronunciation and fluency).

## Usage

```
/ielts-read-aloud             # Claude picks a difficulty-calibrated passage
/ielts-read-aloud easy        # Week 1-2 difficulty
/ielts-read-aloud medium      # Week 3-4 difficulty
/ielts-read-aloud hard        # Week 5+ difficulty
```

## Flow

1. **Generate a 50-70 word passage** calibrated to the current week (see progression in `reference/ielts-rubrics.md#read-aloud`):
   - **Week 1-2 (easy)**: concrete topics, common vocabulary, short sentences
   - **Week 3-4 (medium)**: abstract topics, mixed vocabulary, compound sentences
   - **Week 5+ (hard)**: academic register, Latinate vocabulary, complex sentence structures
2. **Present the passage** with this frame:
   - "You have 30 seconds to prepare, then read this passage aloud. Ideally record yourself — we'll score from your self-report."
3. **Flag high-risk words** before the user starts: long syllable counts, unusual stress patterns, Latinate roots. Example: "Watch these: `infrastructure` (4 syllables, stress on in-), `predominantly` (stress on -dom-), `archaeological` (stress on ar-)."
4. **Wait for the user's self-report**:
   - Any word he tripped on?
   - Any sentence he restarted?
   - Self-rated fluency 1-9?
   - Self-rated pronunciation 1-9?
5. **Grade**:

```
IELTS Read Aloud Score: {{fluency}}/9 + {{pronunciation}}/9

Fluency (self-reported): {{n}}/9
  Words tripped on: {{list}}
  Sentences restarted: {{count}}
  Duration: {{seconds}} seconds

Pronunciation (self-rated): {{n}}/9

Flagged words — drill individually:
- {{word 1}}: {{phonetic breakdown + stress pattern}}
- {{word 2}}: {{phonetic breakdown + stress pattern}}
```

6. **Log to `ielts_progress.md`**.

---

## Difficulty Examples

### Easy (W1-2)

> Australia has many national parks that protect unique wildlife. Many visitors come each year to see kangaroos, koalas, and native birds. Rangers work hard to keep these animals safe from threats like bushfires. Visitors are asked to stay on marked paths and not feed the animals.

Common words, short sentences, no Latinate clusters.

### Medium (W3-4)

> The rise of remote work has changed how companies organize their offices. Many firms now offer flexible arrangements, allowing employees to work from home several days each week. This shift has reduced commuting costs and improved work-life balance for many workers. However, it has also raised concerns about collaboration and team spirit.

Abstract topic, compound sentences, some multisyllabic vocabulary.

### Hard (W5+)

> Recent archaeological evidence suggests that the decline of certain ancient civilizations was caused by prolonged droughts rather than by external invasion. Paleoclimatic reconstructions, derived from stalagmite isotope ratios in regional caves, indicate sustained rainfall anomalies spanning several decades. These environmental pressures likely exacerbated existing sociopolitical tensions throughout the classical period.

Academic register, Latinate density, complex noun phrases — close to real IELTS Reading difficulty.

---

## High-Risk Word Patterns

### Words with unusual stress

| Word | Stress pattern | Trap |
| :--- | :--- | :--- |
| development | de-VEL-op-ment | Stress on second syllable |
| economic | ee-ko-NOM-ic | Stress on third syllable |
| opportunity | op-por-TU-ni-ty | Stress on third syllable |
| environmental | en-vi-ron-MEN-tal | Stress on fourth syllable |
| comfortable | COM-for-ta-ble | Stress on first syllable |
| photograph | PHO-to-graph | vs pho-TO-graph (verb) |

### Long words to break down

| Word | Syllables | Breakdown |
| :--- | :--- | :--- |
| infrastructure | 5 | in-fra-struc-ture |
| telecommunications | 7 | tele-com-mu-ni-ca-tions |
| characteristic | 6 | char-ac-ter-is-tic |
| responsibility | 6 | re-spon-si-bil-i-ty |
| automatically | 6 | au-to-mat-i-cal-ly |

### Homophones to watch

| Word | Confusion |
| :--- | :--- |
| affect / effect | Verb vs noun |
| weather / whether | Climate vs conditional |
| advice / advise | Noun vs verb |
| practice / practise | Noun vs verb (British) |

---

## Self-Rating Guide

| Band | Fluency descriptor |
| :---: | :--- |
| 9 | Native-like pace and rhythm |
| 8 | Smooth with occasional minor hesitation |
| 7 | Generally smooth, some hesitation |
| 6 | Acceptable pace, some hesitation and self-correction |
| 5 | Noticeably hesitant, frequent pauses |

| Band | Pronunciation descriptor |
| :---: | :--- |
| 9 | All sounds clear, native-like intonation |
| 8 | Mostly clear, minor pronunciation issues |
| 7 | Generally clear, some first-language influence |
| 6 | Understandable, some persistent errors |
| 5 | Frequently unclear, significant pronunciation issues |

---

## Anti-patterns

- **Don't read the passage for the user**. If he asks "how do you pronounce X?", give the stress pattern in words ("like in-FRA-struc-ture") — do not audio-read.
- **Don't over-inflate self-ratings**. If the user says "I think 7/9 on fluency but I paused five times", that's a 6. Be the honest coach.
- **Don't skip the high-risk word flag**. Flagging them *before* reading gives the user a chance to mentally rehearse — that's real practice.
- **Don't focus only on single words**. The goal is continuous speech at natural pace, not perfect pronunciation of isolated words.
