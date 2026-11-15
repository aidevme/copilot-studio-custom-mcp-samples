# Rewrite patterns

<!-- cspell:ignore aidevme Dataverse -->

Patterns for the Yoast readability checks, with examples from aidevme topics. Rewrite only flagged
sentences, and keep every fact, number and product name.

## Passive → active

Name the actor and put it first. The verb changes form; the rest of the sentence usually stays.

| Passive | Active | How |
| --- | --- | --- |
| The record is created by the plugin. | The plugin creates the record. | Actor from the *by* phrase moves to the front |
| The solution was imported into the test environment. | We imported the solution into the test environment. | Name the person (I, we, the admin) |
| Connection references must be configured before deployment. | Configure connection references before deployment. | Instruction → imperative |
| The agent is activated when it's published. | The agent runs once you publish and activate it. | Address the reader as "you" |
| Customer data isn't sent to or processed by GitHub Copilot. | These agents don't send customer data to GitHub Copilot, and GitHub Copilot doesn't process it. | Split a double passive into two actives |
| Each user's usage is totalled and billed through the environment. | Microsoft totals each user's usage and bills it through the environment. | Name the vendor as the actor |
| Not all Graph operations are supported yet. | Agent accounts don't support all Graph operations yet. | Make the feature the subject |

**Keep the passive** when the actor is unknown or irrelevant and no active version reads naturally
("The flow runs when a row is added"). Keep verbatim quotes as they are.

## Long sentence → short sentences

| Technique | Before | After |
| --- | --- | --- |
| One idea per sentence | The harness reasons over the goal, breaks it into steps and adjusts when a step fails, which is why Microsoft positions it for long, multi-step processes. | The harness reasons over the goal, breaks it into steps and adjusts when a step fails. That's why Microsoft positions it for long, multi-step processes. |
| Split at "and", "but", "so", "which" | It means the pilot lives in a dedicated environment, not in production, and your ALM path has to account for that. | The pilot lives in a dedicated environment, not in production. Your ALM path has to account for that. |
| Hidden list → bullets | It excludes personal details such as ID numbers; passwords and tokens; health information; … | It excludes: followed by one bullet per item |
| Move a parenthetical out | The harness replaces topics with Skills and Hooks (workflows that run at points in the agent's lifecycle, such as session start). | The harness replaces topics with Skills and Hooks. Hooks are workflows that run at points in the agent's lifecycle, such as session start. |
| Overview sentence → several | This post looks at what shipped, what you need, how identity is governed, the memory behavior, the gaps and billing. | This post covers what shipped and what you need. It then looks at identity and memory. It ends with the gaps and billing. |

- Link the new sentences with transition words (then, also, so, because, but, that's why) so the logic stays
  visible.
- Avoid two sentences over 20 words in a row. An occasional long analytical sentence is fine.
- Don't overcorrect into fragments: each sentence needs a subject and a verb.
- Click paths and UI labels count as words; move a long path into its own sentence ("The setting is under
  **Copilot** > **Settings** > **Agent accounts**.").

## Subheading distribution (sections under 300 words)

- Split at a natural break: a new sub-topic, a step, a table or a list. Don't cut a paragraph in half.
- Use an H3 under the H2. It should be descriptive and searchable, and its first sentence answers it.
- Bold lead-in paragraphs ("**Triggers start the cycle.**") don't count as subheadings for Yoast. When a section
  built from them runs past 300 words, turn two or three of the lead-ins into H3s.

| Section (words) | Split into |
| --- | --- |
| "The agent's identity: Entra account, Agent ID and Agent 365" (416) | H3 "Publishing fixes the identity" · H3 "Connector permissions and Conditional Access" · H3 "Tool authentication" |
| "What you need before the Agent account button appears" (323) | H3 "Enablement steps" (the numbered list) · H3 "Where the pilot runs" (the early-release paragraph) |

## Paragraph length (150 words at most)

- Split where the idea changes, usually at "but", "however" or a new example.
- A paragraph that lists items becomes a short lead-in sentence plus bullets.

## Transition words (at least 30% of sentences)

Transition words show how one sentence relates to the next. Splitting long sentences removes them, so put them
back when you split.

| Relation | Words |
| --- | --- |
| Addition | also, in addition, furthermore, besides |
| Cause and effect | because, so, therefore, as a result, that's why |
| Contrast | but, however, instead, on the other hand, although |
| Example | for example, for instance, such as, in particular |
| Sequence | first, then, next, after, finally, once |
| Conclusion | in short, overall, ultimately |

| Without | With |
| --- | --- |
| The pilot lives in a dedicated environment. Your ALM path has to account for that. | The pilot lives in a dedicated environment, so your ALM path has to account for that. |
| You can't move agents between harnesses. Choosing the harness is an architectural decision. | You can't move agents between harnesses. That's why choosing the harness is an architectural decision. |

"And" doesn't count as a transition word.

## Consecutive sentences (no 3 in a row with the same first word)

- Vary the opening: move a time or condition to the front ("In this preview, …", "When you publish, …"), or
  join two sentences with a transition word.
- Bullets count. Three bullets that start with "The agent…" or "No…" trigger the check. Lead with the specific
  noun or a bold label instead.
