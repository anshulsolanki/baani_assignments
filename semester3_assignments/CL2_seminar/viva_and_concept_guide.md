# Viva, Concept & Seminar Preparation Guide: Safety in NLG
**Topic**: Section 6.1 (*Safety*), Chapter 6 (*Safety, testing, and maintenance*)  
**Source**: Ehud Reiter, *Natural Language Generation: An Engineering Approach*  
**Student**: Baani Solanki (2nd-Year B.Tech CSE / Dual Degree CLD, IIIT Hyderabad)  
**Target Purpose**: Seminar Voiceover Preparation, Defense, and Faculty/TA Viva Defense

---

## 1. High-Level Concept & Reading Walkthrough

### 1.1 The Theoretical Core: What is "Product Safety" in NLG?
In academic computational linguistics and NLP benchmarks, evaluation is overwhelmingly dominated by **average-case metrics** (BLEU, ROUGE, METEOR, BERTScore, Perplexity). A system with an average accuracy of $95\%$ is considered state-of-the-art.

However, Section 6.1 argues that in real-world engineering deployments, this paradigm fails. Deployed systems must be evaluated on **worst-case performance and tail risk**:
- **Core Directive**: *"Do no harm."* NLG systems must not lead to actions that harm users or third parties.
- **Product Safety Scope**: Focuses strictly on direct, tangible harms to individual humans interacting with or affected by the system (patients, financial consumers, factory operators, vulnerable individuals). It explicitly sets aside macro-societal risks (mass unemployment, state cyberwarfare, existential threat).
- **The Societal Asymmetry**: Society tolerates human fallibility (doctors make mistakes, drivers cause 1.3M+ traffic fatalities globally per year), but imposes a near-zero tolerance standard on autonomous software systems.

### 1.2 The Taxonomy of NLG Safety Concerns (Section 6.1.1)
The reading breaks down safety risks into six concrete vectors:

| Concern | Underlying Mechanism | Textbook Case Study |
| :--- | :--- | :--- |
| **1. Inappropriate Language** (6.1.1.1) | Scraping uncurated web data; lack of pragmatic filter; literal generation. | • Rule-based navigation generating *"Go to Hell"* (Hell, Michigan).<br>• Cultural/contextual: *"God"* vs. *"G-d"* in Torah tradition; profanity allowed in news quotes but forbidden in health apps. |
| **2. Misleading Content** (6.1.1.2) | Neural hallucination of factual units, numbers, and logical constraints. | • **ChatGPT Weather Generation**: Input data showed wind speed at $12\text{ mph}$. ChatGPT generated $12\text{ km/h}$. Offshore oil rig safety cutoff is $< 10\text{ mph}$ ($16\text{ km/h}$); false forecast falsely signals safety for deadly operations. |
| **3. Dangerous Content** (6.1.1.3) | NLU intent failure + ambiguous NLG feedback; software bugs. | • **Siri \& OxyContin (Bickmore et al., 2018)**: User asks how many drinks they can have; Siri sets an alarm for 10:00 PM; user infers they can drink freely until 10:00 PM (potentially lethal drug-alcohol interaction).<br>• **Babytalk BT-Nurse**: Mandatory independent research nurse screening required by hospital ethics board. |
| **4. Upsetting Texts** (6.1.1.4) | Lack of emotional moderation and clinical empathy; malicious URL redirection. | • **Babytalk Relatives**: Blunt clinical updates about a critically ill baby could trigger a cardiac event in a frail great-grandmother.<br>• **Balloccu et al. (ChatGPT)**: Advised a depressed user to count calories/journal food intake (15% unsafe; triggers eating disorders).<br>• **Author's GPT-4 test**: Mental health query linked to a spam/predatory website. |
| **5. Dated Information** (6.1.1.5) | Static model weights; temporal corpus bias; outdated rule sets. | • **Google Bard**: Recommended buying stock in a company bankrupt for 6 months.<br>• **Braun \& Matthes**: GPT-3.5 gave superseded German legal advice because pre-2014 statutory documents dominated the training web crawl. |
| **6. Sensitive Data Leakage** (6.1.1.6) | Memorization in pre-training/fine-tuning; absence of enterprise zero-retention. | • 3-step leak: Meeting transcription $\rightarrow$ provider ingests into training set $\rightarrow$ third-party extracts proprietary facts via probing prompts. Prompted enterprise bans at Apple, Samsung, Wall Street banks. |

### 1.3 The Mitigation Landscape (Section 6.1.2)

```
                       ┌──────────────────────────────────────────────┐
                       │          The 100% Guarantee Dilemma          │
                       │ Stochastic black-box neural models CANNOT be │
                       │    mathematically guaranteed 100% safe.      │
                       └──────────────────────┬───────────────────────┘
                                              │
         ┌───────────────────┬────────────────┴──────────────────┬───────────────────┐
         ▼                   ▼                                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐                 ┌─────────────────┐ ┌─────────────────┐
│ 1. Safer Models │ │ 2. Human-in-Loop│                 │ 3. Guardrails & │ │ 4. Red Teaming  │
│ • RLHF / DPO    │ │ • Expert vetting│                 │    Detectors    │ │ • Spot-checks   │
│ • Downsized &   │ │ • Orthogonal    │                 │ • Pre/post toxic│ │   lack bounds   │
│   constrained   │ │   error profiles│                 │   classifiers   │ │ • Tester        │
│   scope         │ │ • Liability risk│                 │ • Context-blind │ │   intuition gap │
└─────────────────┘ └─────────────────┘                 └─────────────────┘ └─────────────────┘
                                              │
                         ┌────────────────────┴────────────────────┐
                         ▼                                         ▼
              ┌─────────────────────┐                   ┌─────────────────────┐
              │  5. User Training   │                   │ 6. Safety Cases &   │
              │  • Cyber-hygiene    │                   │    Regulation       │
              │  • Scepticism of AI │                   │  • FDA/FAA model    │
              │  • Enterprise only  │                   │  • Closed vs Open   │
              └─────────────────────┘                   └─────────────────────┘
```

---

## 2. Key Viva Pointers ("What to Highlight to the TA / Faculty")

When giving your seminar or answering follow-up questions from your Computational Linguistics instructor or TA, make sure to emphasize these specific conceptual distinctions:

1. **Worst-Case vs. Average-Case Evaluation**:
   - Point out that standard NLP benchmarks focus on the mean ($\mu$), whereas safety engineering focuses on the extreme tails of the distribution ($3\sigma, 6\sigma$). A model with $98\%$ accuracy is useless in healthcare if the $2\%$ error mode is lethal.
2. **The "Unit Hallucination" in the Weather Example (Slide 6)**:
   - Mention why ChatGPT's swap of $12\text{ mph}$ to $12\text{ km/h}$ is an ideal teaching example: it demonstrates that hallucination isn't just making up fake names—it includes unit conversions that invert safety thresholds in industrial protocols ($< 10\text{ mph}$ cutoff).
3. **The Multi-Agent Interaction Failure in Siri/OxyContin (Slide 7)**:
   - Clarify that safety failures are often **compound failures**: an NLU intent classification mistake paired with an ambiguous NLG template created a life-threatening mental model in the patient.
4. **Why Rule-Based Systems Are Not Completely Safe, But More Manageable (Slide 5 & 11)**:
   - Rule-based systems can fail due to literalism (*"Go to Hell, Michigan"*) or software bugs. But crucially: rule-based systems are deterministic and auditable. When a bug is discovered, you can trace the exact rule and deploy a regression test. With neural models, fixing one edge case via fine-tuning often causes catastrophic forgetting or introduces regressions elsewhere.
5. **The Open-Weights Regulatory Paradox (Slide 15)**:
   - Highlight the contrast between closed APIs and open-weight models: regulators can audit closed providers (OpenAI, Google) via centralized server telemetry, but once an open-weight model (e.g., Llama) is downloaded and modified locally, incident reporting and regulatory compliance become practically unenforceable.

---

## 3. 15 Realistic Viva Questions & Ready-to-Speak Model Answers

### Q1: Why can't we just give a mathematical guarantee that an LLM will never output an unsafe response?
> **Answer**: "Because modern neural language models are stochastic, high-dimensional black boxes parameterized by billions of weights. Decoding is fundamentally probabilistic ($P(w_t \mid w_{<t})$). Even with temperature set to zero or strict top-$k$ decoding, the sheer size of the input prompt space is combinatorial and infinite. We cannot formally prove reachability or bound outputs across all possible inputs, unlike formal verification in finite-state automata or deterministic software."

### Q2: How does safety in Section 6.1 differ from the standard AI alignment or existential risk debates?
> **Answer**: "Section 6.1 focuses strictly on **product safety**—the direct, tangible harm that an NLG software artifact inflicts on an individual user or downstream third party (such as a patient or client). Existential risk and broader AI safety address societal macro-risks, such as large-scale labor market displacement, autonomous weapons, or cyber-terrorism. Professor Reiter deliberately scopes this chapter to the day-to-day software engineering and liability issues of shipping NLG systems."

### Q3: Explain why society has an asymmetry in safety expectations between human professionals and AI.
> **Answer**: "Societal psychology treats human errors as an unavoidable consequence of human imperfection—we accept that doctors or drivers experience fatigue or cognitive lapses. However, autonomous software is treated as an engineered tool. Society expects engineered artifacts (like bridges, airplane autopilots, and medical devices) to be deterministic and zero-defect. When an AI causes a death, it is viewed as an engineering design negligence, resulting in intense regulatory and legal scrutiny."

### Q4: In the weather forecast case study, why was a simple conversion from mph to km/h considered a major safety risk?
> **Answer**: "In high-stakes industrial operations like offshore oil platforms and maritime crane operations, safety standards prohibit outdoor work when wind speeds exceed $10\text{ mph}$ (around $16\text{ km/h}$). The ground truth sensor data recorded $12\text{ mph}$, meaning conditions were unsafe. However, ChatGPT hallucinated the units and generated '$12\text{ km/h}$' ($7.5\text{ mph}$). An offshore supervisor relying on the text would conclude operations are safe, exposing crew members to gale-force winds and fatal structural hazards."

### Q5: In the Siri and OxyContin study by Bickmore et al., what was the root cause of the dangerous advice?
> **Answer**: "It was a compound failure of both NLU and NLG. The user asked how many drinks they could have while on OxyContin. The NLU module failed to understand the intent and instead parsed the query as a reminder or alarm request, setting an alarm for 10:00 PM. The NLG module then confirmed: *'I've set your alarm for 10:00 P.M.'* The user pragmatically interpreted this confirmation as medical permission to drink alcohol until 10:00 PM. Combining alcohol with opioids can cause fatal respiratory depression at any time."

### Q6: What was the Babytalk BT-Nurse project, and what ethical safety protocol did the researchers have to implement?
> **Answer**: "Babytalk BT-Nurse was a clinical NLG system developed by Professor Reiter's research group to automatically generate shift-handover summaries from sensor streams and medical records in a Neonatal Intensive Care Unit. Even though the system was purely advisory and human duty nurses made all medical decisions, the clinical research ethics board mandated that every generated summary had to be manually screened by an independent research nurse before the duty nurse was permitted to read it."

### Q7: Why did clinical experts rate ChatGPT's dietary advice to a depressed user as dangerous in the Balloccu et al. study?
> **Answer**: "The user stated they were in treatment for depression and anxiety, and that their medication caused unavoidable weight gain. ChatGPT suggested food logging, calorie journaling, and habit adjustments. Clinical experts rated this as severely dangerous because prescribing dietary restriction and obsessive caloric tracking to an individual struggling with depression can trigger eating disorders, exacerbate guilt, and accelerate self-harm or suicidal ideation. Standard LLMs lack clinical psychiatric context."

### Q8: What causes language models to output dated or superseded legal information, as demonstrated by Braun and Matthes?
> **Answer**: "This is driven by corpus frequency bias. Pre-trained models are trained on unweighted web scrapes. In the German legal study, statutory law had changed in 2014, but pre-2014 legal documents were far more prevalent across the web than post-2014 documents. Consequently, GPT-3.5 gave higher probability to the obsolete legal framework. The model cannot naturally distinguish between the historical frequency of a document and its current legal validity."

### Q9: Describe the 3-step threat model of sensitive data leakage through NLG prompts.
> **Answer**: "First, an employee inputs confidential data (e.g., patient records, financial audits, or unreleased source code) into a prompt for summarization. Second, the service provider logs these prompts and ingests them into future model retraining or alignment corpora. Third, external users query the retrained model, which regurgitates the memorized confidential data through targeted prompt extraction or memorization attacks."

### Q10: Why does Professor Reiter argue that smaller, specialized models are safer than giant monolithic foundation models?
> **Answer**: "Large monolithic LLMs have billions of parameters and vast multi-domain capabilities, which creates an enormous, unpredictable attack surface with myriad failure modes. In contrast, smaller, task-specific models (or domain-constrained architectures) have limited capabilities and fewer parameters. Just like specialized relational databases, they are easier to bound, test, monitor, and formally audit for a specific business process."

### Q11: Why are human-in-the-loop (HITL) workflows so effective, and what is their error complementarity?
> **Answer**: "HITL is the most effective safety intervention because humans and NLG systems make fundamentally orthogonal errors. NLG systems excel at high-throughput data processing, synthesizing complex multi-sensor streams, and never experiencing physical fatigue. Humans excel at common-sense reasoning, contextual pragmatics, and emotional empathy. When an NLG system drafts a text and an expert verifies it, the combined workflow achieves higher accuracy and safety than either could achieve alone."

### Q12: What is the primary operational trade-off of human-in-the-loop workflows?
> **Answer**: "Cost, latency, and legal liability. Expert human review (such as a doctor or lawyer vetting drafts) is extremely expensive, introduces major delays, and makes real-time applications impossible. Furthermore, it creates legal ambiguity: if the system is legally classified as a writing assistant, does medical malpractice liability fall on the physician who approved the summary, or does product liability fall on the software developer who built the NLG pipeline?"

### Q13: What are the main limitations of automatic toxicity and safety detectors?
> **Answer**: "Automated detectors are typically binary classifiers that lack pragmatic, cultural, and domain context. While they easily catch explicit obscenities, they completely miss subtle, context-dependent hazards—such as an offshore wind unit mismatch, an obsolete legal precedent, or psychologically damaging dietary advice. Additionally, they often produce false positives on reclaimed language or legitimate medical discussions."

### Q14: What did the 2024 International Scientific Report on the Safety of Advanced AI state about software testing for LLMs?
> **Answer**: "It stated that empirical spot checks on test inputs are helpful for identifying general strengths and weaknesses, but cannot provide quantitative safety guarantees. General-purpose AI systems behave unpredictably across subtle changes in prompts, user backgrounds, or decoding parameters. Furthermore, software testing relies on tester intuition, but because AI evolves so rapidly, testers lack mature intuitions regarding where edge-case failures will occur."

### Q15: What is a 'Safety Case', and how might it be used to regulate high-risk NLG systems?
> **Answer**: "Borrowed from safety engineering in nuclear energy, pharmaceuticals, and aviation, a Safety Case is a formal, structured argument supported by a body of evidence demonstrating that a system is acceptably safe for a specific operational context. Before deploying high-risk NLG systems in healthcare or public infrastructure, developers would have to present a formal safety case containing empirical test suites, failure mode analyses, human-in-the-loop protocols, and risk mitigation proofs to regulatory authorities."

---

## 4. Overleaf Setup Instructions for Baani

To compile your Beamer presentation in Overleaf:
1. Open [Overleaf](https://www.overleaf.com) and create a **New Project** $\rightarrow$ **Blank Project** (name it `CL2_NLG_Safety_Seminar`).
2. Delete the default contents in `main.tex` and paste the entire code from `baani_assignments/semester3/CL2_seminar/presentation.tex`.
3. Set your compiler to **pdfLaTeX** (which is the default on Overleaf).
4. Click **Recompile**.
5. All packages used (`tcolorbox`, `tikz`, `amsmath`, `booktabs`, `hyperref`) are standard packages included in the default TeX Live distribution on Overleaf, so it will compile with zero errors!
