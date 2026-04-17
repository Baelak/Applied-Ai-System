# 🐾 Model Card — # PawPal+ ~ AI-Enhanced Pet Care Scheduler

---

## What it does

Uses the Gemini 2.5 Flash-Lite API to suggest pet names based on species and an optional theme provided by the user. It returns exactly 3 male and 3 female names with a one-line explanation of the theme or inspiration.

---

## Limitations and Biases

Without a theme, the model defaults to popular Western names almost every time. It has no awareness of the user's culture, language, or personal taste unless told. It also has no memory between sessions so every suggestion starts from scratch. The output format is inconsistent enough that the parser can silently return nothing if the model deviates from the expected structure.

---

## Misuse

The risk is pretty low since it only suggests pet names but someone could technically use the theme field to push the model toward inappropriate output. Gemini's built-in safety filters catch most of that and since the user has to manually type the final name nothing gets applied automatically. For a production version I'd add validation on the theme input field.

---

## Reliability

I expected the model to follow format instructions consistently and it didn't. Sometimes it returned `Male:` with a capital M, sometimes `male` in lowercase, sometimes a dash instead of a colon. The parser would break silently on those variations which was harder to catch than an actual error. That pushed me toward parsing more loosely rather than expecting exact formatting.

---

## Collaboration with AI

Working with Claude Code throughout this project was genuinely useful. The most helpful moment was when it caught that I was about to commit my API key directly to the repo and suggested moving it to a secrets file before it became a problem. The one time it got things wrong was recommending `gemini-1.5-flash` as the model name which threw a 404 because that model ID was no longer valid. A good reminder that AI tools can sound confident and still be wrong.

---

## Intended Use

This allows pet owners manage their responsibilities with their pets. It's a simple app with simple ai feature to be used for Personal or educational projects only. Not validated for production use.

## Personal Reflection

The hardest part of building this wasn't making the AI work, it was figuring out where humans should stay in control. Keeping the AI as a suggestion tool rather than full automation was the best decision I made. The system works well for what it does, but I learned that the real challenge in AI apps isn't the AI itself, it's everything around it like state management, error handling, and making sure things don't break silently. If I kept building this, I'd explore something more interesting than name suggestions, like an AI scheduling assistant.