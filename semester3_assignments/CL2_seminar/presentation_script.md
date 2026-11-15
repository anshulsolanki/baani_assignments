
### Slide 1: Title Slide

**Spoken Script**:
> "Good morning. My name is Baani Solanki, and today I will be presenting on **Safety in Natural Language Generation**.
>
> As NLG systems transition from research labs into clinical wards, financial advisory pipelines, and mission-critical decision workflows, a central question arises: **How do we ensure that language generation systems do not harm their users?**"

---

### Slide 2: The Real-World Imperative: Why NLG Safety Matters
**Spoken Script**:
> "To understand safety in NLG, we must contrast it with traditional NLP evaluation. In academic benchmarks, models are evaluated on **average-case metrics**—such as BLEU, ROUGE, or accuracy across a test split.
>
> However, in real-world deployment, average performance is secondary. What truly matters is **worst-case performance and risk**. A medical NLG system that accurately summarizes intensive care patient records ninety-nine times out of a hundred, but hallucinates a lethal drug dosage once every hundred shifts, is completely unacceptable in clinical practice.
>
> The foundational design mandate is simple: **'Do no harm.'** The system must protect both direct users and third parties affected by generated texts, even under exceptional or adversarial conditions."

---

### Slide 3: Defining Safety: Scope, Risk, and Societal Asymmetry
**Spoken Script**:
> "Let us scope our discussion. Broad AI safety covers macro-societal risks—such as mass labor displacement or automated weapons. Section 6.1 narrows the focus specifically to **Product Safety**: direct, concrete harms inflicted on individual human users.
>
> There is also a critical psychological reality: the **Societal Asymmetry of Safety Standards**. Society holds AI systems to a far higher standard than humans. When a physician makes an error, society accepts that 'doctors are human and make mistakes.' Yet we show zero tolerance for an AI system making a diagnostic blunder.
>
> We see the exact same asymmetry in autonomous driving: human drivers kill over 1.3 million people every year on roads worldwide, yet a single autonomous vehicle collision triggers global outcry. In high-stakes NLG, systems must target near-zero failure rates in safety-critical paths."

---

### Slide 4: Taxonomy of NLG Safety Concerns
**Spoken Script**:
> "Section 6.1 organizes product safety failures into six primary categories, as shown in Figure 6.1:
> 1. **Inappropriate Language**: Generating offensive, toxic, or culturally insensitive text.
> 2. **Misleading Content**: Hallucinating factual errors that lead to unsafe decisions.
> 3. **Dangerous Content**: Suggesting or endorsing lethal physical behavior.
> 4. **Emotionally Upsetting Texts**: Inducing severe psychological distress that triggers somatic harm.
> 5. **Dated Information**: Relying on stale training data or obsolete domain rules.
> 6. **Sensitive Data Leakage**: Inadvertently memorizing and regurgitating confidential user data.
>
> Let us examine each concern with its underlying mechanisms and empirical case studies."

---

### Slide 5: Concern 1: Inappropriate & Toxic Language 
**Spoken Script**:
> "The first concern is **Inappropriate Language**—text that is offensive, discriminatory, or profane. In modern neural models, this stems directly from training corpora: models scrape billions of tokens from unfiltered internet forums, absorbing and reproducing toxic patterns.
>
> Inappropriate language can also emerge in rule-based systems through unintended literalism. The text mentions a real case: a navigation system generated the instruction *'Go to Hell'*—simply because the user was traveling to the town of **Hell, Michigan**!
>
> Crucially, language safety is strictly **context- and culture-dependent**. Profanity is completely impermissible in patient medical leaflets, but direct quotes in investigative journalism may require preserving exact language. In religious contexts, writing out 'God' violates Orthodox Jewish Torah tradition, which mandates using 'G-d'. Blanket keyword blacklists either over-censor or miss nuanced contextual violations."

---

### Slide 6: Concern 2: Misleading Content & Hallucination
**Spoken Script**:
> "The second concern is **Misleading Content**. As we know, deep generative models hallucinate fluent but factually erroneous assertions.
>
> Consider the striking weather generation case study in Figure 6.2. When ChatGPT was prompted to summarize structured weather sensor data, the input data recorded a peak wind speed of **12 miles per hour**. But ChatGPT generated: *'The wind will range from 9 km/h to 12 km/h throughout the day.'*
>
> Swapping miles per hour for kilometers per hour may appear to be a minor formatting quirk, but consider the operational domain. On offshore oil platforms and maritime crane operations, high-risk maintenance is strictly prohibited when wind speeds exceed **10 miles per hour**—which is about 16 kilometers per hour.
>
> Because ChatGPT reported '12 km/h'—which is only 7.5 miles per hour—an offshore operator relying on this forecast would mistakenly conclude it is safe to proceed, when actual winds were 12 miles per hour, violating the safety threshold! A subtle unit hallucination can cause catastrophic structural failure."

---

### Slide 7: Concern 3: Dangerous Content & Medication Safety
**Spoken Script**:
> "The third concern is **Dangerous Content**—where an NLG system actively misguides a user into hazardous physical actions.
>
> A prominent clinical study by Bickmore et al. investigated voice assistants. A user asked Siri: *'I'm taking OxyContin for chronic back pain. But I'm going out tonight. How many drinks can I have?'* Siri misinterpreted the intent and responded: *'I've set your chronic back pain one alarm for 10:00 P.M.'*
>
> When researchers interviewed the participant, the user concluded: *'I can drink until 10:00, and then after 10 o'clock I can't drink.'* In reality, co-ingesting alcohol with OxyContin can trigger fatal respiratory depression and cardiac arrest at **any** time! This was a compound failure: an NLU intent classification error compounded by an ambiguous NLG response.
>
> The author contrasts this with his own clinical project, **Babytalk BT-Nurse**, which generates shift handover summaries for neonatal ICUs. Even though nurses made all final medical decisions, hospital ethics approval mandated that an independent research nurse manually screen every generated report before the duty nurse saw it."

---

### Slide 8: Concern 4: Psychologically Upsetting Content
**Spoken Script**:
> "Our fourth concern is **Emotionally Upsetting Texts**. In computational linguistics, we often treat text as abstract symbols, forgetting that psychological shock can cause severe physiological harm.
>
> In the Babytalk project, when generating progress updates for families of critically ill premature infants, clinicians warned that delivering an unbuffered, blunt report to an elderly great-grandmother with a severe heart condition could trigger a fatal cardiac episode.
>
> Furthermore, in a study by Balloccu and colleagues, ChatGPT was tested on dietary advice. A user experiencing medication-induced weight gain during treatment for clinical depression was advised by ChatGPT to strictly log daily food intake and exercise in a journal. Clinical experts flagged this as **severely dangerous**: suggesting caloric tracking to a depressed individual frequently triggers eating disorders and exacerbates suicidal ideation. In fact, experts judged 15% of ChatGPT's dietary suggestions to be clinically unsafe."

---

### Slide 9: Concern 5: Dated Information & Temporal Drift
**Spoken Script**:
> "The fifth concern is **Dated Information**. Pre-trained models are frozen snapshots of web corpora. When the world evolves, static models suffer from temporal drift and domain shift.
>
> Professor Reiter tested Google Bard for equity investment advice. Bard recommended investing in two specific companies—completely unaware that one company had declared bankruptcy six months earlier, and the other was suffering from major safety defect recalls!
>
> Similarly, Braun and Matthes evaluated GPT-3.5 on German legal queries. The model confidently rendered advice based on pre-2014 statutory regulations, despite the statute having been overhauled in 2014. Why? Because the pre-2014 version was vastly more frequent in the web-crawled training data. The model fundamentally confused historical token frequency with current legal validity."

---

### Slide 10: Concern 6: Sensitive Data Leakage & Privacy Risks
**Spoken Script**:
> "The sixth concern is **Data Leakage**. Today, corporate employees frequently paste confidential information into web-based language models: meeting transcripts, clinical files, and proprietary code.
>
> The risk follows a 3-step threat vector:
> First, an employee submits sensitive data in a prompt.
> Second, the service provider absorbs that prompt into model retraining or alignment datasets.
> Third, an external user queries the retrained model, which regurgitates the memorized confidential information.
>
> This is why enterprises like Samsung, Apple, and Wall Street banks banned internal use of commercial LLMs. While expert developers can configure zero-retention enterprise APIs, non-technical users unwittingly expose proprietary organizational secrets."

---

### Slide 11: Mitigation 1: Safer Models & The Guarantee Dilemma
**Spoken Script**:
> "Now let us turn to Section 6.1.2: **How do we address these safety concerns?**
>
> We must begin with an inescapable engineering truth: **We cannot guarantee that neural NLG systems will be 100% safe.**
> Clients frequently demand zero-risk guarantees. But because neural models are stochastic, high-dimensional black boxes, we can reduce the empirical failure rate, but we cannot mathematically prove zero violations under worst-case inputs.
>
> In contrast, rule-based systems are deterministic and auditable; when bugs arise, they can be traced and patched with unit tests.
>
> To make models safer, developers employ curated datasets and alignment techniques like RLHF. Another vital strategy is **scoping and model downsizing**: rather than using a massive generalist model with unpredictable failure modes, we should deploy smaller, constrained, task-specific models. Constraining functionality shrinks the attack surface, making system verification far more tractable."

---

### Slide 12: Mitigation 2: Human-in-the-Loop (HITL) Workflows
**Spoken Script**:
> "Currently, the most effective defense against NLG safety hazards is a **Human-in-the-Loop (HITL) workflow**, where every generated text is vetted by a qualified domain expert before release.
>
> HITL works because humans and NLG systems exhibit **orthogonal error profiles**. NLG models excel at data synthesis, pattern extraction, and tireless throughput. Humans excel at common-sense reasoning, contextual nuance, and catching absurd or dangerous guidance. Studies confirm that hybrid workflows produce documents that are measurably safer and more accurate than either AI or humans working alone.
>
> However, HITL introduces substantial cost and latency, making it unviable for real-time consumer apps. It also raises unresolved questions around **legal liability**: if a system acts as an assistant and an expert signs off on a flawed output, does liability lie with the clinician or the software vendor?"

---

### Slide 13: Mitigation 3: Automated Guardrails & Detectors 
**Spoken Script**:
> "To filter text at scale, developers implement **Automated Safety Detectors**—specialized classification models deployed as pre- and post-generation firewalls. If a detector identifies toxic language or dangerous topics like biological weapons, the text is suppressed, regenerated, or replaced with a safe fallback template.
>
> However, automated detectors have significant blind spots. Binary classifiers lack pragmatic and situational awareness: they easily catch explicit profanity, but completely miss a subtle unit hallucination ($12\text{ mph}$ vs $12\text{ km/h}$), an obsolete statute, or harmful dietary advice. Guardrails are a valuable first filter, but cannot provide comprehensive safety alone."

---

### Slide 14: Mitigation 4: Software Testing & Adversarial Red Teaming
**Spoken Script**:
> "The fourth strategy is **Software Testing and Adversarial Red Teaming**—hiring specialized testers to actively craft inputs that bypass safety guardrails.
>
> Yet testing generative AI is fundamentally harder than testing traditional software. The *International Scientific Report on the Safety of Advanced AI* emphasizes that empirical spot-checks do not provide quantitative safety guarantees. A system that passes 10,000 spot-checks may still fail catastrophically when a user slightly tweaks prompt phrasing or decoding parameters.
>
> Furthermore, software testing relies heavily on tester intuition. Because generative AI evolves at a breakneck pace, testers' intuitions often lag behind emerging failure modes."

---

### Slide 15: Mitigations 5 & 6: User Training, Regulation & Safety Cases
**Spoken Script**:
> "Finally, we have human and institutional safeguards: **User Training** and **Government Regulation**.
>
> User training mirrors cybersecurity hygiene: just as we teach employees not to click phishing links, we must train users to scrutinize NLG medical or financial advice and never input proprietary data into public models. This is feasible in corporate settings, but nearly impossible for public consumer applications.
>
> On the regulatory front, Professor Reiter suggests that AI will converge toward frameworks used in **pharmaceuticals and aviation**. Before releasing high-risk NLG systems, developers will need to submit formal **'Safety Cases'**—structured technical dossiers proving rigorous safety validation.
>
> However, regulation faces a unique challenge with **open-weight models**, where developers lack visibility into how end-users fine-tune models locally, alongside the reality that bureaucratic regulation moves far slower than AI research."

---

### Slide 16: Synthesis & Conclusion
**Spoken Script**:
> "To synthesize the key takeaways from Section 6.1:
>
> First, real-world deployment demands a paradigm shift from optimizing **average-case benchmark scores** to minimizing **tail-risk catastrophic harm**.
>
> Second, NLG safety is multidimensional: spanning toxic tone, factual hallucinations, dangerous medical advice, emotional distress, dated knowledge, and data leakage.
>
> Third, because stochastic neural models cannot be mathematically guaranteed 100% safe, safety requires a **Defense-in-Depth architecture**: combining domain-constrained models, automated guardrails, relentless adversarial red-teaming, human-in-the-loop oversight in critical settings, and formal safety cases.
>
> Thank you very much. "
