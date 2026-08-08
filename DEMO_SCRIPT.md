# 🎥 Demo Video Script (6 Questions Guide for Loom)

Use this script to record your 2 to 3 minute Loom video. Read the bold spoken lines clearly!

---

### Question 1: Problem & Audience (~30 sec)
**What problem does your project solve, who is it for, and why does it matter?**

> 🗣️ **Script to speak:**
> *"Navigating UAE visa rules, Emirates ID procedures, and overstay fine calculations is confusing and fragmented across government websites—especially for tourists, expats, and non-English speakers. Our project, the UAE Visa Intelligence AI Voice Agent, provides an instant, multilingual voice assistant that speaks directly with users in their native language (English, Arabic, Hindi, Urdu) to give clear, 2-to-3 sentence spoken answers sourced directly from official UAE government portals."*

---

### Question 2: Live Working Demo (~2 min)
**Give a live, working demo showing a real voice conversation and live web-data fetch through context.dev.**

> 🗣️ **Script to speak & action:**
> 1. *"Now, let's look at a live demo of our voice agent."*
> 2. **Ask the Agent out loud or trigger the webhook with a question**:
>    - *Question:* *"What are the requirements for the UAE Golden Visa for real estate investors?"*
> 3. **Show the Terminal / Server Logs**: Point to `server.py` and show `context.dev` fetching from `https://u.ae/en/information-and-services/visa-and-emirates-id/Types-of-visas/golden-visa`.
> 4. **Show the Spoken Voice Output**: Show the agent responding aloud:
>    - *"To qualify for the Golden Visa as a real estate investor, you must own property in the UAE worth at least 2 million AED. You can apply directly through the ICP Smart Services portal or GDRFA Dubai."*
> 5. **Ask a second question in another language (e.g. Hindi or Arabic)**:
>    - *Question:* *"UAE mein tourist visa par overstay fine kitna hai?"*
> 6. **Show Groq detecting Hindi and replying in Hindi voice**:
>    - *"UAE mein tourist visa overstay ke liye 10 din ka grace period milta hai, uske baad 50 AED daily fine lagta hai."*

---

### Question 3: Essential Web Data (~30 sec)
**Why is live web data essential to your project?**

> 🗣️ **Script to speak:**
> *"Our project would fundamentally break without live web data because UAE visa regulations, fee structures, and grace period rules change frequently by government decree. If visa rules change tomorrow on the ICP or GDRFA portals, our agent dynamically extracts the newest verified rules via `context.dev` in real-time mid-conversation, ensuring zero outdated or hallucinated legal advice."*

---

### Question 4: Autonomy & Agent Logic (~45 sec)
**Beyond text-to-speech, what does your agent actually do on its own?**

> 🗣️ **Script to speak:**
> *"Beyond TTS, our agent runs an autonomous processing pipeline: First, it analyzes the user's spoken intent and dynamically selects the official UAE government URL and JSON extraction schema. Second, it executes a live `context.dev` web extraction. Third, it passes the raw structured data through Groq Llama 3.3 70B to detect the user's native language and synthesize a warm 2-sentence conversational script. Finally, it triggers ElevenLabs Multilingual TTS with custom voice personality tuning optimized for official government advisory."*

---

### Question 5: Novelty (~30 sec)
**What makes your approach novel?**

> 🗣️ **Script to speak:**
> *"What makes our approach novel is combining schema-bound live web extraction from authoritative government portals (`context.dev`) with multilingual real-time LLM voice summarization. Instead of returning raw search links or unverified blogs, it turns complex official government legal portals into a conversational, human-like voice advisor accessible to anyone in any language."*

---

### Question 6: Hardest Problem (~30 sec)
**What was the hardest problem you solved?**

> 🗣️ **Script to speak:**
> *"The hardest technical challenge was maintaining low voice latency (under 1.5 seconds) while performing live web extraction and LLM summarization. We solved this by building a smart dynamic routing system paired with a persistent disk fallback cache covering 21+ major UAE legal topics, ensuring instant responses even under network latency or API rate limits."*
