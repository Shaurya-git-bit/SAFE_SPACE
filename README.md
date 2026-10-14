# Safe Space

**Most children who are being groomed online never tell anyone.** They are scared of losing their phone, ashamed, or convinced the adult is kind and the relationship is their own choice. A generic chatbot that says "go tell your parents" does not help that child.

Safe Space is a safety companion for children and teens in India, and for the siblings, friends and parents who notice something is wrong. It reads a chat or a description, spots grooming and blackmail patterns, rates the risk, and gives small next steps the child can actually take.

> **Early warning in real time.** Paste a chat while it's still going on. The safety box adapts with every message, and the risk level only goes up within a session, so a warning sign never disappears once it's spotted.

## What it does

- **Three modes.** The app starts by asking who is using it: the child (victim), a sibling or friend, or a parent. Greetings, warnings and advice change for each.
- **Pattern detection.** An LLM tags 24 warning signs in each message, such as secrecy, hiding things from parents, returning to a topic the child already refused, guilt pressure, photo requests, fake peer identities and blackmail. It works in English and Hinglish.
- **Risk level from code, not from the LLM.** A rule layer in `rules.py` sets the level (LOW, CONCERNING or HIGH). The LLM never decides the level, so it stays predictable and easy to inspect.
- **Context-aware.** Two setup questions (how much older is the other person, and is the person a teacher, coach or someone in charge) change how the rules score the chat.
- **Live safety panel.** A sidebar shows the current risk badge, a plain-language list of the warning signs found, and a "Need help now?" box that opens by itself at HIGH.
- **Blackmail Rescue screen.** If a child in victim mode describes threats, blackmail, a money demand, sexual material or a direct photo request, the app switches to a short guided flow. The child never has to upload or describe the image, and can skip saying whether they sent one. Every answer gets the same steps: keep the evidence, don't pay, don't forward the image, and call 1930, Childline 1098 or a trusted adult.
- **Replies that match the child's situation.** Tone changes by level: gentle and curious for CONCERNING, calm and direct for HIGH.
- **Real people first.** The bot never replaces a person. Replies point to a ladder of people (a sibling, an aunt or uncle, a school counselor), Childline 1098, the police and the cyber helpline.

## How it works

```
User message
    |
    v
Tagger (LLM, tagger_prompt.md)  ->  tags + "after_refusal" flag
    |
    v
Rule layer (rules.py)           ->  LOW / CONCERNING / HIGH
    |
    v
Reply (LLM, safety_guide.md + level + mode + tags found)
```

1. **Tagger.** Every time a new message comes in, the AI reads it together with the last few messages before it. It does one job: mark which warning signs are in the message (for example "asked to keep it secret" or "asked for a photo"). It also marks whether the adult is pushing again on something the child already said no to. It only labels the message. It does not judge how risky the chat is and does not reply. If the tagger fails, the app treats the message as having no warning signs, so it keeps running instead of crashing.
2. **Rule layer.** `assess()` goes through the whole chat history and returns a level. Main rules:
   - Any HIGH tag (threat, blackmail, money demand, photo request, meeting request, child expressing fear, pressure after a photo was sent, sexual content sent, child seeing it as a relationship) makes the level HIGH.
   - Asking to hide the chat from parents after the child already refused is HIGH.
   - Romantic framing from someone 5 or more years older is HIGH.
   - Personal questions only count when the gap is 5+ years or the person is an authority figure.
   - Two or more different CONCERNING signs escalate to HIGH.
   - A warning sign repeated after the child said no counts as extra pressure.
   - The level never goes down within a session.
3. **Reply.** The reply model gets the safety guide plus runtime context: mode, risk level, tags found so far and the tone for that level. It answers in the language the user writes in.

Both the tagger and the reply use `gemini-3.5-flash-lite` through the Gemini API.

## The safety guide

`safety_guide.md` is what separates this from a generic chatbot. It contains:

- Plain explanations for each warning sign, written for a child to hear
- Talking rules: never blame the child, never say "this is abuse" (it says "this is a pattern that can be a warning sign"), name the behavior and not the person, one question at a time, never promise secrecy
- Scripts for common fears: losing the phone, shame, "I like him", "no one will believe me", "it's too late", fear of lower grades from a teacher
- A dedicated blackmail rescue flow with strict do and don't lists
- Separate guidance for sibling and parent modes (siblings should not run straight to parents who might blame the victim, parents start with "You're not in trouble. You were manipulated. I'm on your side.")

## Test scenarios

The `chats/` folder has fictional chats written to cover different grooming paths. They were used to design the tags and rules.

| File | Scenario |
|------|----------|
| `chat1.txt` | Online "boyfriend", 14F and 25M, gaming app, slow trust building and secrecy |
| `chat2.txt` | Photo request, 14F and 24M, Instagram, art praise leading to guilt pressure |
| `chat3.txt` | Adult posing as a 17-year-old girl, 15M, Snapchat, photo swap then blackmail |
| `chat5.txt` | Teacher grooming, 16F in Class 11, subtle extra attention and a push to Instagram |
| `chat6.txt` | Retreat and re-approach, 15F and 27M, Discord, returns to a topic she declined |

## Privacy and limits

- The app does not store chats. Messages are sent to Google's Gemini API to generate replies.
- Input is capped at 4,000 characters per message.
- If the API fails, the app shows a fallback message with 112 and Childline 1098.
- The tagger is an LLM and can miss things or over-tag. The rule layer makes the level easy to audit, but this is a support tool, not a diagnosis.
- The scenario chats are fictional.

## Help lines used in the app

- Childline: 1098
- Police: 112
- Cyber Crime Helpline: 1930
- Report online: cybercrime.gov.in
- Optional image takedown: takeitdown.ncmec.org

## Project files

```
.
├── child_safety.py      Streamlit app
├── rules.py             Rule layer that sets the risk level
├── safety_guide.md      System prompt for replies
├── tagger_prompt.md     Prompt for the tagging step
├── requirements.txt     Python dependencies
└── chats/               Fictional test scenarios
```

## Run it locally

```bash
pip install -r requirements.txt
```

Create `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-key-here"
```

You can also set `GEMINI_API_KEY` as an environment variable. Then run:

```bash
streamlit run child_safety.py
```

## Disclaimer

Safe Space is an AI tool and not a replacement for a trusted person, a counselor or the police. If a child is in danger, call 112.
