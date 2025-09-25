# Prompts

## Concise
id: 4a86b61f-4f65-44ed-917b-93d2cda236c5

Task: Based on the provided image, create:
	•	Description: 2–3 precise sentences, factual, objective, no interpretation.
	•	Caption: One short sentence (max. 10 words).
	•	Keywords: 5–10 comma-separated keywords describing visible elements.
Output format:

Description: …
Caption: …
Keywords: …

Rules:
	•	Do not speculate about symbolism, meaning, or context.
	•	Mention only what is visibly present.
	•	Use technical/domain terms when possible.
	•	Keep Description under ~60 words.


## Detailed
id: d0c95806-91aa-49e4-b70d-fb96779737bc

Task: Based on the provided image, create:
	•	Description: A longer, detailed account (1 paragraph, 80–120 words). Start with the main subject, then foreground/middle/background details. Include shapes, colors, materials, spatial relationships, and interactions.
	•	Caption: One short sentence (max. 12 words).
	•	Keywords: 8–15 comma-separated keywords.

Output format:

Description: …
Caption: …
Keywords: …

Rules:
	•	Factual only; omit unverifiable details.
	•	Include technical terminology if identifiable (e.g., engraving, woodcut, manuscript illumination).
	•	Useful for accessibility and detailed indexing.


## Named Entities / Contextual
id: 0e4f8917-d62e-4aef-b4c4-91a255b4d61e

Task: Based on the provided image (and surrounding context if given), create:
	•	Description: A detailed description (100–150 words). Identify known places, persons, or objects if visible and recognizable. Start with an overall summary, then describe parts (foreground, background, significant details).
	•	Caption: One concise sentence identifying the main subject.
	•	Keywords: 10–15 comma-separated terms, including proper names if visible.

Output format:

Description: …
Caption: …
Keywords: …

Rules:

	•	If identification is uncertain, describe neutrally instead of guessing.
	•	Use geographic, architectural, or biographical terms if correct.
	•	Suitable for curated collections where recognition is possible.
