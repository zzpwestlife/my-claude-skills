# Error Pattern Taxonomy

Growing dictionary of error pattern labels for tagging the user's English mistakes. Each entry has:

- **Label** (kebab-case, used in `errors_tagged.md`)
- **What it is** (one-line description)
- **Trigger** (the Chinese thinking pattern that produces it)
- **Fix** (the rule, stated as a usage principle not a grammar term)
- **Example**

When a new error shows up that doesn't fit any label here, coin a new one and append it.

---

## Seed patterns (initial session)

### preposition-about-vs-with

- **What**: Using "with" where "about" belongs, or vice versa
- **Trigger**: Chinese "跟" maps to both "with" and "about" depending on context
- **Fix**: "with" is the **person** you speak to. "about" is the **topic** you speak on. Different jobs.
- **Example**: "talk with that" → "talk about that". You talk **with me about English**.

### missing-be-verb

- **What**: Dropping "am/is/are" before a verb ending in -ing
- **Trigger**: Chinese doesn't have the "to be" auxiliary — "我学英语" doesn't need "am"
- **Fix**: Present continuous always needs an engine: **am / is / are + -ing**. No engine = no sentence.
- **Example**: "cause I learning English" → "cause I'm learning English"

### embedded-question-word-order

- **What**: Keeping question word order inside a subordinate clause
- **Trigger**: Chinese uses the same word order for questions and statements, so the flip feels unnatural
- **Fix**: When a question lives inside another sentence, drop it back to statement order. Questions: "What does that mean?" Embedded: "I need to know what **that means**."
- **Example**: "I need to know what's that mean" → "I need to know what that means"

---

## Common Chinese-English patterns (seeded, will grow)

### article-missing-a

- **What**: Dropping "a/an" before a singular countable noun
- **Trigger**: Chinese has no articles
- **Fix**: Countable singular nouns almost always need **a / an / the**. Default to "a/an" when introducing something new.
- **Example**: "I have cat" → "I have a cat"

### article-missing-the

- **What**: Dropping "the" before something already known
- **Trigger**: Chinese has no articles
- **Fix**: Use "the" when both speaker and listener already know which one. "Close the door" (the one we both see).
- **Example**: "I fixed bug in login page" → "I fixed the bug on the login page"

### plural-missing-s

- **What**: Forgetting to pluralize countable nouns
- **Trigger**: Chinese plurals are optional and usually implicit
- **Fix**: If there's more than one, the noun gets "-s". No exceptions in casual register.
- **Example**: "three customer" → "three customers"

### verb-tense-flat

- **What**: Using present tense where English demands past
- **Trigger**: Chinese relies on time words ("昨天") instead of verb inflection
- **Fix**: If it happened and finished before now, use past tense. The time word is not enough.
- **Example**: "yesterday I go to the meeting" → "yesterday I went to the meeting"

### to-plus-ing

- **What**: Writing "to + verb-ing" when the rule is "to + bare verb"
- **Trigger**: "help me to refactoring" sounds like "help me in refactoring"
- **Fix**: After "to" in an infinitive, use the bare verb. "to refactor", "to learn", "to go". Not "to refactoring".
- **Example**: "help me to refactoring this" → "help me refactor this" (or "help me with refactoring this")

### third-person-s

- **What**: Forgetting the "-s" on third-person singular present verbs
- **Trigger**: Chinese verbs never inflect for person
- **Fix**: He/she/it + verb → verb gets an -s. "He runs." "It works."
- **Example**: "he run fast" → "he runs fast"

### pronoun-it-missing

- **What**: Dropping "it" where English requires a placeholder subject
- **Trigger**: Chinese drops pronouns freely
- **Fix**: English sentences need a subject, even an empty one. "It's raining." "It seems fine."
- **Example**: "is raining" → "it's raining"

### word-order-adjective-after-noun

- **What**: Putting the adjective after the noun (Chinese default)
- **Trigger**: "一个红的苹果" — descriptor comes first in Chinese too, but modifier particles confuse the mapping
- **Fix**: English adjective goes **before** the noun. "red apple", not "apple red".
- **Example**: "a function recursive" → "a recursive function"

### collocation-wrong-partner

- **What**: Pairing a correct word with the wrong collocational partner — technically grammatical but sounds unnatural
- **Trigger**: Translating Chinese verb+noun combinations word-by-word ("做研究" → "do research" when native English uses "conduct research")
- **Fix**: Look up the headword in `ielts_vocab.md` (the Academic Collocation List). The ACL tells you which specific partner English natives reach for. Collocations are fixed — "heavy rain" not "strong rain", "make a decision" not "do a decision", "reach a peak" not "arrive at a peak".
- **IELTS impact**: High — collocations are directly rewarded in Writing (vocabulary range, linguistic range) and in Reading/Listening Fill-in-the-Blanks tasks
- **Example**: "do research" → "conduct research"; "big growth" → "significant growth"; "make a crime" → "commit a crime"

### countable-uncountable-confusion

- **What**: Treating an uncountable noun as countable, or vice versa
- **Trigger**: Chinese doesn't distinguish countable/uncountable — "信息" can take a number, "information" cannot
- **Fix**: Some nouns resist counting: information, advice, equipment, research, knowledge, homework, luggage. Use "a piece of" / "some" instead of "an" or plural "-s".
- **Example**: "many informations" → "a lot of information"; "an advice" → "a piece of advice"

### subject-verb-agreement

- **What**: Singular subject with plural verb, or vice versa
- **Trigger**: Chinese verbs never inflect for number — "他/他们 去" is the same verb form
- **Fix**: After writing the subject, check: is it singular or plural? The verb must match. "The system **runs**" (one system) vs "The systems **run**" (many).
- **Example**: "the data show" → "the data shows" (data is treated as singular in most academic writing); "he don't" → "he doesn't"

### preposition-after-adjective

- **What**: Using the wrong preposition after an adjective, or dropping it entirely
- **Trigger**: Chinese adjectives connect directly to objects without prepositions — "对...感兴趣" → "interested about" instead of "interested in"
- **Fix**: Adjective + preposition pairs are fixed in English. Memorize the common ones: interested **in**, good **at**, responsible **for**, dependent **on**, different **from** (not "than" or "with").
- **Example**: "good in programming" → "good at programming"; "responsible of" → "responsible for"

### redundant-pronoun

- **What**: Including a pronoun that duplicates the relative clause's subject or object
- **Trigger**: Chinese relative clauses repeat the noun naturally — "我认识的那个人他很聪明"
- **Fix**: In English, the relative pronoun (who/that/which) replaces the noun — don't add it again. "The person **who** I met" (not "who I met him").
- **Example**: "the book that I read it" → "the book that I read"; "the man who he called" → "the man who called"

### double-negative

- **What**: Using two negatives where one is enough, or mixing Chinese double-negative logic into English
- **Trigger**: Chinese uses double negatives for emphasis ("不得不" = must, "不是不" = is), but English treats double negatives as logical cancellation
- **Fix**: In standard English, two negatives cancel out. "I don't have nothing" logically means "I have something". Use one negative + positive verb: "I don't have anything" or "I have nothing".
- **Example**: "I can't not go" → "I have to go"; "it's not impossible" → clarify: "it's difficult but possible"

### run-on-sentence

- **What**: Joining two independent clauses with a comma or nothing
- **Trigger**: Chinese uses commas to string related clauses together without conjunctions — "天气很好我们出去了"
- **Fix**: Two complete sentences need a conjunction (and/but/so/because), a semicolon (;), or a full stop (.) between them. A comma alone is not enough.
- **Example**: "I was tired, I went to bed" → "I was tired, so I went to bed"; "it's late we should go" → "It's late. We should go."

---

## How to add a new pattern

When an error doesn't match any label above:

1. Coin a label in kebab-case (short, memorable)
2. Append a new section to this file with the 5 fields (what/trigger/fix/example)
3. Reference the label in `errors_tagged.md` for that error entry

The taxonomy growing is a feature — it maps the territory of the user's specific mistakes.
