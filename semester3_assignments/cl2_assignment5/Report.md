# Computational Linguistics 2 — Assignment 5 Report
## Discourse-Based Text Summarization using Rhetorical Structure Theory (RST)

- **Student Name:** Baani Solanki
- **Roll Number:** `2025114016`
- **Course:** Computational Linguistics 2 (Monsoon / Spring Semester)

---

## Problem 1: Discourse Parsing with Pretrained `isanlp_rst` (10 Points)

We parsed all 10 English paragraphs from `paragraph.txt` using the pretrained **`isanlp_rst`** discourse parser (`hf_model_name='tchewik/isanlp_rst_v3'`, `hf_model_version='rstdt'`, trained on the RST Discourse Treebank). The parser segments each paragraph into **Elementary Discourse Units (EDUs)** (clause-level leaves) and constructs a hierarchical binary constituent tree annotated with **Nuclearity** (`NS` = Left Nucleus / Right Satellite, `SN` = Left Satellite / Right Nucleus, `NN` = Multinuclear) and **Rhetorical Relations** (e.g., *Elaboration*, *Explanation*, *Contrast*, *Joint*, *Attribution*, *Background*, *Temporal*, *Condition*, *Manner-Means*, *Enablement*).

### Summary of Parsed RST Discourse Trees Across All 10 Paragraphs

| Para # | Topic (Mann & Thompson, 1988) | # Sentences | # EDUs | # Internal Splits | Root Split Relation & Nuclearity | Central Nucleus EDU(s) (Root Promoted) |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **1** | California Common Cause / Nuclear Freeze | 4 | 12 | 11 | `Explanation (NS)` | EDU 1 (S1): *"that endorsing the Nuclear Freeze Initiative is the right step..."* |
| **2** | Syncom Diskette (4-Way Protection) | 5 | 12 | 11 | `Elaboration (NS)` | EDU 1 (S1): *"a Syncom diskette is working four ways"* |
| **3** | Creating a "Victorian" Flower Bouquet | 4 | 11 | 10 | `Elaboration (NS)` | EDU 0 (S1): *"To create your own 'Victorian' bouquet of flowers,"* |
| **4** | Jobless Line Refuting "Moxie" Claims | 2 | 9 | 8 | `Elaboration (NS)` | EDU 0 & EDU 2 (S1): *"The people ... carried a message, a refutation, of claims"* |
| **5** | Scottsdale Model House ("Ostentatious") | 5 | 14 | 13 | `Elaboration (NS)` | EDU 1 (S1): *"my wife was amused by the real-estate agents,"* |
| **6** | Mother Teresa's Advice in Calcutta | 5 | 16 | 15 | `Elaboration (NS)` | EDU 0 & EDU 1 (S1): *"When a group of Americans... visited her... they asked her for some advice"* |
| **7** | ZPG 1985 Urban Stress Test | 3 | 7 | 6 | `Elaboration (NS)` | EDU 0 & EDU 2 (S1): *"ZPG's 1985 Urban Stress Test ... is the nation's first survey"* |
| **8** | Ancient Shipbuilding & Shipwrecks | 4 | 8 | 7 | `Joint (NN)` | EDU 0 (S1) & EDU 2 (S2): *"Our knowledge of ancient shipbuilding..."* & *"The contents of shipwrecks..."* |
| **9** | Susan Smart's Cessna 150 Spin | 3 | 9 | 8 | `Elaboration (NS)` | EDU 0 (S1): *"In an article for Campus Life magazine, Susan Smart describes her third and nearly last solo flight."* |
| **10** | Comparing RST & Systemic Linguistics | 5 | 14 | 13 | `Elaboration (NS)` | EDU 0 (S1): *"This paper is part of an effort"* |

### Extracted Relation Labels & Discourse Trees per Paragraph

#### Paragraph 1 (Nuclear Freeze Initiative)
- **Relation Labels (11 splits):** `Explanation (NS)`, `Attribution (SN)`, `Contrast (NN)`, `Explanation (NS)`, `Contrast (SN)`, `Elaboration (NS)`, `Background (SN)`, `Elaboration (NS)`, `Attribution (SN)`, `Condition (NS)`, `Elaboration (NS)`
```text
[Node 23] (ROOT | split_rel=Explanation, nuclearity=NS)
  [Node 13] (Nucleus | split_rel=Attribution, nuclearity=SN)
    [EDU 0] (Satellite | rel=Attribution): "I don't believe"
    [EDU 1] (Nucleus | rel=span): "that endorsing the Nuclear Freeze Initiative is the right step for California Common Cause."
  [Node 22] (Satellite | split_rel=Contrast, nuclearity=NN)
    [Node 18] (Nucleus | split_rel=Explanation, nuclearity=NS)
      [Node 15] (Nucleus | split_rel=Contrast, nuclearity=SN)
        [EDU 2] (Satellite | rel=Contrast): "Tempting as it may be,"
        [Node 14] (Nucleus | split_rel=Elaboration, nuclearity=NS)
          [EDU 3] (Nucleus | rel=span): "we shouldn't embrace every popular issue"
          [EDU 4] (Satellite | rel=Elaboration): "that comes along."
      [Node 17] (Satellite | split_rel=Background, nuclearity=SN)
        [EDU 5] (Satellite | rel=Background): "When we do so,"
        [Node 16] (Nucleus | split_rel=Elaboration, nuclearity=NS)
          [EDU 6] (Nucleus | rel=span): "we use precious, limited resources"
          [EDU 7] (Satellite | rel=Elaboration): "where other players with superior resources are already doing an adequate job."
    [Node 21] (Nucleus | split_rel=Attribution, nuclearity=SN)
      [EDU 8] (Satellite | rel=Attribution): "Rather, I think"
      [Node 20] (Nucleus | split_rel=Condition, nuclearity=NS)
        [EDU 9] (Nucleus | rel=span): "we will be stronger and more effective"
        [Node 19] (Satellite | split_rel=Elaboration, nuclearity=NS)
          [EDU 10] (Nucleus | rel=span): "if we stick to those issues of governmental structure and process, broadly defined,"
          [EDU 11] (Satellite | rel=Elaboration): "that have formed the core of our agenda for years."
```

#### Paragraph 2 (Syncom Diskette)
- **Relation Labels (11 splits):** `Elaboration (NS)`, `Background (SN)`, `Elaboration (NS)`, `Joint (NN)`, `Temporal (NS)`, `Joint (NN)`, `Temporal (NS)`, `Joint (NN)`, `same-unit (NN)`, `Background (NS)`, `Elaboration (NS)`
```text
[Node 23] (ROOT | split_rel=Elaboration, nuclearity=NS)
  [Node 14] (Nucleus | split_rel=Background, nuclearity=SN)
    [EDU 0] (Satellite | rel=Background): "As your floppy drive writes or reads,"
    [Node 13] (Nucleus | split_rel=Elaboration, nuclearity=NS)
      [EDU 1] (Nucleus | rel=span): "a Syncom diskette is working four ways"
      [EDU 2] (Satellite | rel=Elaboration): "to keep loose particles and dust from causing soft errors, dropouts."
  [Node 22] (Satellite | split_rel=Joint, nuclearity=NN)
    [Node 15] (Nucleus | split_rel=Temporal, nuclearity=NS)
      [EDU 3] (Nucleus | rel=span): "Cleaning agents on the burnished surface of the Ectype coating actually remove build-up from the head,"
      [EDU 4] (Satellite | rel=Temporal): "while lubricating it at the same time."
    [Node 21] (Nucleus | split_rel=Joint, nuclearity=NN)
      [Node 16] (Nucleus | split_rel=Temporal, nuclearity=NS)
        [EDU 5] (Nucleus | rel=span): "A carbon additive drains away static electricity"
        [EDU 6] (Satellite | rel=Temporal): "before it can attract dust or lint."
      [Node 20] (Nucleus | split_rel=Joint, nuclearity=NN)
        [EDU 7] (Nucleus | rel=Joint): "Strong binders hold the signal-carrying oxides tightly within the coating."
        [Node 19] (Nucleus | split_rel=same-unit, nuclearity=NN)
          [Node 17] (Nucleus | split_rel=Background, nuclearity=NS)
            [EDU 8] (Nucleus | rel=span): "And the non-woven jacket liner,"
            [EDU 9] (Satellite | rel=Background): "more than just wiping the surface,"
          [Node 18] (Nucleus | split_rel=Elaboration, nuclearity=NS)
            [EDU 10] (Nucleus | rel=span): "provides thousands of tiny pockets"
            [EDU 11] (Satellite | rel=Elaboration): "to keep what it collects."
```

#### Paragraph 3 (Victorian Bouquet)
- **Relation Labels (10 splits):** `Elaboration (NS)`, `Manner-Means (NS)`, `Joint (NN)`, `same-unit (NN)`, `Elaboration (NS)`, `Joint (NN)`, `Elaboration (NS)`, `Elaboration (NS)`, `same-unit (NN)`, `Elaboration (NS)`
```text
[Node 21] (ROOT | split_rel=Elaboration, nuclearity=NS)
  [Node 12] (Nucleus | split_rel=Manner-Means, nuclearity=NS)
    [EDU 0] (Nucleus | rel=span): "To create your own "Victorian" bouquet of flowers,"
    [EDU 1] (Satellite | rel=Manner-Means): "choose varying shapes, sizes and forms, besides a variety of complementary colors."
  [Node 20] (Satellite | split_rel=Joint, nuclearity=NN)
    [Node 16] (Nucleus | split_rel=same-unit, nuclearity=NN)
      [Node 13] (Nucleus | split_rel=Elaboration, nuclearity=NS)
        [EDU 2] (Nucleus | rel=span): "Plants"
        [EDU 3] (Satellite | rel=Elaboration): "that grow tall"
      [Node 15] (Nucleus | split_rel=Joint, nuclearity=NN)
        [EDU 4] (Nucleus | rel=Joint): "should be surrounded by smaller ones"
        [Node 14] (Nucleus | split_rel=Elaboration, nuclearity=NS)
          [EDU 5] (Nucleus | rel=span): "and filled with others"
          [EDU 6] (Satellite | rel=Elaboration): "that tumble over the side of a hanging basket."
    [Node 19] (Nucleus | split_rel=Elaboration, nuclearity=NS)
      [EDU 7] (Nucleus | rel=span): "Leaf textures and colors will also be important."
      [Node 18] (Satellite | split_rel=same-unit, nuclearity=NN)
        [Node 17] (Nucleus | split_rel=Elaboration, nuclearity=NS)
          [EDU 8] (Nucleus | rel=span): "There is the silver-white foliage of dusty miller, the feathery threads of lotus vine"
          [EDU 9] (Satellite | rel=Elaboration): "floating down from above,"
        [EDU 10] (Nucleus | rel=same-unit): "the deep greens, or chartreuse, even the widely varied foliage colors of the coleus."
```

#### Paragraph 4 (Jobless Line)
- **Relation Labels (8 splits):** `Elaboration (NS)`, `same-unit (NN)`, `Elaboration (NS)`, `Elaboration (NS)`, `Condition (NS)`, `Contrast (SN)`, `same-unit (NN)`, `Elaboration (NS)`
```text
[Node 17] (ROOT | split_rel=Elaboration, nuclearity=NS)
  [Node 13] (Nucleus | split_rel=same-unit, nuclearity=NN)
    [Node 10] (Nucleus | split_rel=Elaboration, nuclearity=NS)
      [EDU 0] (Nucleus | rel=span): "The people"
      [EDU 1] (Satellite | rel=Elaboration): "waiting in line"
    [Node 12] (Nucleus | split_rel=Elaboration, nuclearity=NS)
      [EDU 2] (Nucleus | rel=span): "carried a message, a refutation, of claims"
      [Node 11] (Satellite | split_rel=Condition, nuclearity=NS)
        [EDU 3] (Nucleus | rel=span): "that the jobless could be employed"
        [EDU 4] (Satellite | rel=Condition): "if only they showed enough moxie."
  [Node 16] (Satellite | split_rel=Contrast, nuclearity=SN)
    [EDU 5] (Satellite | rel=Contrast): "Every rule has exceptions,"
    [Node 15] (Nucleus | split_rel=same-unit, nuclearity=NN)
      [Node 14] (Nucleus | split_rel=Elaboration, nuclearity=NS)
        [EDU 6] (Nucleus | rel=span): "but the tragic and too-common tableaux of hundreds or even thousands of people"
        [EDU 7] (Satellite | rel=Elaboration): "snake-lining up for any task with a paycheck"
      [EDU 8] (Nucleus | rel=same-unit): "illustrates a lack of jobs, not laziness."
```

#### Paragraph 5 (Scottsdale Model House)
- **Relation Labels (13 splits):** `Elaboration (NS)`, `Elaboration (NS)`, `Background (SN)`, `Elaboration (NS)`, `Elaboration (NS)`, `Contrast (NN)`, `Attribution (SN)`, `same-unit (NN)`, `Background (SN)`, `Temporal (NN)`, `Elaboration (NS)`, `Attribution (SN)`, `Attribution (NS)`
```text
[Node 27] (ROOT | split_rel=Elaboration, nuclearity=NS)
  [Node 20] (Nucleus | split_rel=Elaboration, nuclearity=NS)
    [Node 19] (Nucleus | split_rel=Background, nuclearity=SN)
      [EDU 0] (Satellite | rel=Background): "While looking over a Scottsdale, Ariz., model house one day,"
      [Node 18] (Nucleus | split_rel=Elaboration, nuclearity=NS)
        [EDU 1] (Nucleus | rel=span): "my wife was amused by the real-estate agents,"
        [Node 17] (Satellite | split_rel=Elaboration, nuclearity=NS)
          [EDU 2] (Nucleus | rel=span): "who engaged her in the "you talk kinda funny" conversation."
          [Node 16] (Satellite | split_rel=Contrast, nuclearity=NN)
            [Node 15] (Nucleus | split_rel=Attribution, nuclearity=SN)
              [EDU 3] (Satellite | rel=Attribution): "We say"
              [EDU 4] (Nucleus | rel=span): ""to-mah-to""
            [EDU 5] (Nucleus | rel=Contrast): "and Arizonans say "to-may-to.""
    [EDU 6] (Satellite | rel=Elaboration): "We call the hood of a car a "bonnet" and the trunk a boot."
  [Node 26] (Satellite | split_rel=same-unit, nuclearity=NN)
    [EDU 7] (Nucleus | rel=same-unit): "Then,"
    [Node 25] (Nucleus | split_rel=Background, nuclearity=SN)
      [EDU 8] (Satellite | rel=Background): "as my wife entered the dining room,"
      [Node 24] (Nucleus | split_rel=Temporal, nuclearity=NN)
        [EDU 9] (Nucleus | rel=Temporal): "one agent pointed to a massive chandelier"
        [Node 23] (Nucleus | split_rel=Elaboration, nuclearity=NS)
          [Node 21] (Nucleus | split_rel=Attribution, nuclearity=SN)
            [EDU 10] (Satellite | rel=Attribution): "and asked,"
            [EDU 11] (Nucleus | rel=span): ""What would you call that in England?""
          [Node 22] (Satellite | split_rel=Attribution, nuclearity=NS)
            [EDU 12] (Nucleus | rel=span): ""Ostentatious,""
            [EDU 13] (Satellite | rel=Attribution): "my wife replied."
```

#### Paragraph 6 (Mother Teresa in Calcutta)
- **Relation Labels (15 splits):** `Elaboration (NS)`, `Elaboration (NS)`, `Temporal (NN)`, `Elaboration (NS)`, `Contrast (NN)`, `Attribution (NS)`, `Elaboration (NS)`, `Background (SN)`, `Attribution (SN)`, `Explanation (NS)`, `Attribution (SN)`, `Temporal (NN)`, `Attribution (NS)`, `Temporal (NS)`, `Explanation (NS)`
```text
[Node 31] (ROOT | split_rel=Elaboration, nuclearity=NS)
  [Node 21] (Nucleus | split_rel=Elaboration, nuclearity=NS)
    [Node 18] (Nucleus | split_rel=Temporal, nuclearity=NN)
      [EDU 0] (Nucleus | rel=Temporal): "When a group of Americans, many in the teaching profession, visited her in Calcutta,"
      [Node 17] (Nucleus | split_rel=Elaboration, nuclearity=NS)
        [EDU 1] (Nucleus | rel=span): "they asked her for some advice"
        [EDU 2] (Satellite | rel=Elaboration): "to take home to their families."
    [Node 20] (Satellite | split_rel=Contrast, nuclearity=NN)
      [Node 19] (Nucleus | split_rel=Attribution, nuclearity=NS)
        [EDU 3] (Nucleus | rel=span): ""Smile at your wives,""
        [EDU 4] (Satellite | rel=Attribution): "she told them."
      [EDU 5] (Nucleus | rel=Contrast): ""Smile at your husbands.""
  [Node 30] (Satellite | split_rel=Elaboration, nuclearity=NS)
    [Node 25] (Nucleus | split_rel=Background, nuclearity=SN)
      [Node 23] (Satellite | split_rel=Attribution, nuclearity=SN)
        [EDU 6] (Satellite | rel=Attribution): "Thinking"
        [Node 22] (Nucleus | split_rel=Explanation, nuclearity=NS)
          [EDU 7] (Nucleus | rel=span): "that perhaps the counsel was simplistic,"
          [EDU 8] (Satellite | rel=Explanation): "coming from an unmarried person,"
      [Node 24] (Nucleus | split_rel=Attribution, nuclearity=SN)
        [EDU 9] (Satellite | rel=Attribution): "one of them asked,"
        [EDU 10] (Nucleus | rel=span): ""Are you married?""
    [Node 29] (Satellite | split_rel=Temporal, nuclearity=NN)
      [Node 26] (Nucleus | split_rel=Attribution, nuclearity=NS)
        [EDU 11] (Nucleus | rel=span): ""Yes,""
        [EDU 12] (Satellite | rel=Attribution): "she replied, to their surprise,"
      [Node 28] (Nucleus | split_rel=Temporal, nuclearity=NS)
        [EDU 13] (Nucleus | rel=span): """
        [Node 27] (Satellite | split_rel=Explanation, nuclearity=NS)
          [EDU 14] (Nucleus | rel=span): "and I find it hard sometimes to smile at Jesus."
          [EDU 15] (Satellite | rel=Explanation): "He can be very demanding.""
```

#### Paragraph 7 (ZPG 1985 Urban Stress Test)
- **Relation Labels (6 splits):** `Elaboration (NS)`, `Elaboration (NS)`, `same-unit (NN)`, `Elaboration (NS)`, `Elaboration (NS)`, `Elaboration (NS)`
```text
[Node 13] (ROOT | split_rel=Elaboration, nuclearity=NS)
  [Node 12] (Nucleus | split_rel=Elaboration, nuclearity=NS)
    [Node 10] (Nucleus | split_rel=same-unit, nuclearity=NN)
      [Node 8] (Nucleus | split_rel=Elaboration, nuclearity=NS)
        [EDU 0] (Nucleus | rel=span): "ZPG's 1985 Urban Stress Test,"
        [EDU 1] (Satellite | rel=Elaboration): "created after months of persistent and exhaustive research,"
      [Node 9] (Nucleus | split_rel=Elaboration, nuclearity=NS)
        [EDU 2] (Nucleus | rel=span): "is the nation's first survey"
        [EDU 3] (Satellite | rel=Elaboration): "of how population-linked pressures affect U.S. cities."
    [Node 11] (Satellite | split_rel=Elaboration, nuclearity=NS)
      [EDU 4] (Nucleus | rel=span): "It ranks 184 urban areas on 11 different criteria"
      [EDU 5] (Satellite | rel=Elaboration): "ranging from crowding and birth rates to air quality and toxic wastes."
  [EDU 6] (Satellite | rel=Elaboration): "The Urban Stress Test translates complex, technical data into an easy-to-use action tool for concerned citizens, elected officials and opinion leaders."
```

#### Paragraph 8 (Ancient Shipbuilding & Shipwrecks)
- **Relation Labels (7 splits):** `Joint (NN)`, `Elaboration (NS)`, `Explanation (NS)`, `Elaboration (NS)`, `Explanation (SN)`, `same-unit (NN)`, `Elaboration (NS)`
```text
[Node 15] (ROOT | split_rel=Joint, nuclearity=NN)
  [Node 9] (Nucleus | split_rel=Elaboration, nuclearity=NS)
    [EDU 0] (Nucleus | rel=span): "Our knowledge of ancient shipbuilding techniques, for example, is dependent on the work of archaeologists"
    [EDU 1] (Satellite | rel=Elaboration): "who have painstakingly excavated remains of ships themselves."
  [Node 14] (Nucleus | split_rel=Explanation, nuclearity=NS)
    [EDU 2] (Nucleus | rel=span): "The contents of shipwrecks are an equally valuable archaeological resource."
    [Node 13] (Satellite | split_rel=Elaboration, nuclearity=NS)
      [Node 10] (Nucleus | split_rel=Explanation, nuclearity=SN)
        [EDU 3] (Satellite | rel=Explanation): "Since the objects in a wreck represent a single moment in time,"
        [EDU 4] (Nucleus | rel=span): "they provide better chronological information than even the most carefully excavated terrestrial site."
      [Node 12] (Satellite | split_rel=same-unit, nuclearity=NN)
        [Node 11] (Nucleus | split_rel=Elaboration, nuclearity=NS)
          [EDU 5] (Nucleus | rel=span): "Moreover, perishable items such as foodstuffs,"
          [EDU 6] (Satellite | rel=Elaboration): "which do not survive well on land,"
        [EDU 7] (Nucleus | rel=same-unit): "are often preserved underwater."
```

#### Paragraph 9 (Susan Smart Cessna 150 Spin)
- **Relation Labels (8 splits):** `Elaboration (NS)`, `Elaboration (NS)`, `Temporal (NN)`, `Temporal (NN)`, `Elaboration (NS)`, `Elaboration (NS)`, `Condition (SN)`, `Enablement (NS)`
```text
[Node 17] (ROOT | split_rel=Elaboration, nuclearity=NS)
  [EDU 0] (Nucleus | rel=span): "In an article for Campus Life magazine, Susan Smart describes her third and nearly last solo flight."
  [Node 16] (Satellite | split_rel=Elaboration, nuclearity=NS)
    [Node 11] (Nucleus | split_rel=Temporal, nuclearity=NN)
      [EDU 1] (Nucleus | rel=Temporal): "She had been practicing a maneuver at 5,000 feet"
      [Node 10] (Nucleus | split_rel=Temporal, nuclearity=NN)
        [EDU 2] (Nucleus | rel=Temporal): "when she lost control"
        [EDU 3] (Nucleus | rel=Temporal): "and her Cessna 150 began spinning wildly toward earth."
    [Node 15] (Satellite | split_rel=Elaboration, nuclearity=NS)
      [Node 13] (Nucleus | split_rel=Elaboration, nuclearity=NS)
        [EDU 4] (Nucleus | rel=span): "After several seconds of panic, she recalled her instructor's words:"
        [Node 12] (Satellite | split_rel=Condition, nuclearity=SN)
          [EDU 5] (Satellite | rel=Condition): ""If you ever go into a spin in a Cessna 150,"
          [EDU 6] (Nucleus | rel=span): "just let go of the controls."
      [Node 14] (Satellite | split_rel=Enablement, nuclearity=NS)
        [EDU 7] (Nucleus | rel=span): "It's built"
        [EDU 8] (Satellite | rel=Enablement): "to fly on its own.""
```

#### Paragraph 10 (RST vs. Systemic Linguistics)
- **Relation Labels (13 splits):** `Elaboration (NS)` (×6), `Contrast (NN)`, `same-unit (NN)`, `Elaboration (NS)` (×3), `Contrast (SN)`, `Elaboration (NS)`
```text
[Node 27] (ROOT | split_rel=Elaboration, nuclearity=NS)
  [Node 15] (Nucleus | split_rel=Elaboration, nuclearity=NS)
    [EDU 0] (Nucleus | rel=span): "This paper is part of an effort"
    [EDU 1] (Satellite | rel=Elaboration): "to relate various accounts."
  [Node 26] (Satellite | split_rel=Elaboration, nuclearity=NS)
    [Node 17] (Nucleus | split_rel=Elaboration, nuclearity=NS)
      [Node 16] (Nucleus | split_rel=Elaboration, nuclearity=NS)
        [EDU 2] (Nucleus | rel=span): "It is the first in a pair of papers"
        [EDU 3] (Satellite | rel=Elaboration): "that compare two particular accounts:"
      [EDU 4] (Satellite | rel=Elaboration): "Rhetorical Structure Theory and Systemic Linguistics."
    [Node 25] (Satellite | split_rel=Elaboration, nuclearity=NS)
      [Node 22] (Nucleus | split_rel=Contrast, nuclearity=NN)
        [Node 20] (Nucleus | split_rel=same-unit, nuclearity=NN)
          [Node 18] (Nucleus | split_rel=Elaboration, nuclearity=NS)
            [EDU 5] (Nucleus | rel=span): "Rhetorical Structure Theory,"
            [EDU 6] (Satellite | rel=Elaboration): "initially formulated in 1983,"
          [Node 19] (Nucleus | split_rel=Elaboration, nuclearity=NS)
            [EDU 7] (Nucleus | rel=span): "describes texts in terms of functionally-defined relations"
            [EDU 8] (Satellite | rel=Elaboration): "that hold between their parts."
        [Node 21] (Nucleus | split_rel=Elaboration, nuclearity=NS)
          [EDU 9] (Nucleus | rel=span): "Systemic Linguistics is a much more comprehensive view of language"
          [EDU 10] (Satellite | rel=Elaboration): "initiated in the early 1960s."
      [Node 24] (Satellite | split_rel=Contrast, nuclearity=SN)
        [EDU 11] (Satellite | rel=Contrast): "Where the two approaches are comparable,"
        [Node 23] (Nucleus | split_rel=Elaboration, nuclearity=NS)
          [EDU 12] (Nucleus | rel=span): "Systemic Linguistics describes texts in terms of categories of processes"
          [EDU 13] (Satellite | rel=Elaboration): "which the texts perform."
```

---

## Problem 2: Structured Extraction of Nucleus/Satellite & Relation Features (10 Points)

To bridge clause-level RST trees and sentence-level extractive summarization, `problem_2()` traverses each binary tree from the root (`depth=0`) to every leaf EDU (`extract_edu_records()`) and then aggregates EDU descriptors onto sentences via character-offset alignment (`align_edus_to_sentences()`). For each sentence $S_i$, we extract:
1. **`dominant_role`**: `Nucleus` if the sentence contains the Central Nucleus, has at least as many Nucleus EDUs as Satellite EDUs, is a direct child of the Root (`min_depth == 1`), or opens with a top-level promoted Nucleus clause (`promoted_depth <= 1`); otherwise `Satellite`.
2. **`has_central_nucleus`**: `True` if any EDU in $S_i$ follows an all-Nucleus path from the root (`satellite_steps == 0`).
3. **`min_promoted_depth`** (*Marcu's 2000 Promotion Depth*): The shallowest tree depth to which an EDU in $S_i$ is promoted along Nucleus links (`0` = promoted to Root; `1` = promoted to a child of Root).
4. **`min_depth`** & **`max_nucleus_ratio`**: Minimum leaf depth and maximum path nuclearity purity $1 / (1 + \text{satellite\_steps})$ along the root-to-leaf path.
5. **`nucleus_relations`** & **`satellite_relations`**: Lists of promoted rhetorical relations in which the sentence's EDUs participate as a Nucleus vs. as a Satellite (excluding syntactic continuation pseudo-relations like `same-unit`).

---

## Problem 3: Rule-Based RST Summarization Design & Generated Summaries (10 Points)

### Five Explicit RST Sentence-Scoring Rules (`score_sentence_with_rst_rules`)
1. **Rule 1 — Central Tree Nucleus Promotion (`+3.00`):** Rewards any sentence containing the paragraph's Root-promoted Central Nucleus EDU (`promoted_depth == 0`).
2. **Rule 2 — Marcu Promotion Level & Tree Hierarchy Depth (`+3.0 / (1 + min_promoted_depth) + 1.5 / min_depth`):** Gives high weight to sentences promoted to the top levels of the RST hierarchy (`promoted_depth` 0 or 1) and penalizes deeply nested nodes.
3. **Rule 3 — Path Nuclearity Ratio (`+3.0 * max_nucleus_ratio`):** Rewards sentences whose constituent EDUs remain on the Nucleus side across ancestors ($1 / (1 + \text{satellite\_steps})$).
4. **Rule 4 — Core Rhetorical Relation Bonus (`+RelationWeight / sqrt(num_edus)`):** Rewards sentences whose promoted Nucleus EDUs participate in high-value informative relations (*Result* `+2.0`, *Summary* `+2.0`, *Explanation* `+1.6`, *Contrast* `+1.5`, *Joint* `+1.3`, *Manner-Means* `+1.1`, *Condition/Temporal* `+1.0`, *Elaboration* `+0.8`).
5. **Rule 5 — Subordinate Satellite Pruning & Fragment Filter:** Penalizes sentences whose dominant role is `Satellite` (*Background* `-1.2`, *Attribution* `-0.8`, *Elaboration* `-0.6`) and short dialogue fragments (`< 6 words`, `-2.0`) that cannot stand alone coherently.

### Original Paragraphs vs. Generated Rule-Based Summaries (1–2 Sentences)

| Para # | Original Paragraph | Selected Sentences & Rule Scores | Generated Rule-Based Summary |
| :---: | :--- | :--- | :--- |
| **1** | I don't believe that endorsing the Nuclear Freeze Initiative is the right step for California Common Cause. Tempting as it may be, we shouldn't embrace every popular issue that comes along. When we do so, we use precious, limited resources where other players with superior resources are already doing an adequate job. Rather, I think we will be stronger and more effective if we stick to those issues of governmental structure and process, broadly defined, that have formed the core of our agenda for years. | **S1** (`11.02`), **S4** (`5.25`) *(vs. S2 `5.06`, S3 `1.89`)* | I don't believe that endorsing the Nuclear Freeze Initiative is the right step for California Common Cause. Rather, I think we will be stronger and more effective if we stick to those issues of governmental structure and process, broadly defined, that have formed the core of our agenda for years. |
| **2** | As your floppy drive writes or reads, a Syncom diskette is working four ways to keep loose particles and dust from causing soft errors, dropouts. Cleaning agents on the burnished surface of the Ectype coating actually remove build-up from the head, while lubricating it at the same time. A carbon additive drains away static electricity before it can attract dust or lint. Strong binders hold the signal-carrying oxides tightly within the coating. And the non-woven jacket liner, more than just wiping the surface, provides thousands of tiny pockets to keep what it collects. | **S1** (`10.39`), **S2** (`5.13`) *(vs. S3 `5.00`, S4 `4.67`, S5 `4.45`)* | As your floppy drive writes or reads, a Syncom diskette is working four ways to keep loose particles and dust from causing soft errors, dropouts. Cleaning agents on the burnished surface of the Ectype coating actually remove build-up from the head, while lubricating it at the same time. |
| **3** | To create your own "Victorian" bouquet of flowers, choose varying shapes, sizes and forms, besides a variety of complementary colors. Plants that grow tall should be surrounded by smaller ones and filled with others that tumble over the side of a hanging basket. Leaf textures and colors will also be important. There is the silver-white foliage of dusty miller, the feathery threads of lotus vine floating down from above, the deep greens, or chartreuse, even the widely varied foliage colors of the coleus. | **S1** (`11.09`), **S3** (`5.60`) *(vs. S2 `4.31`, S4 `2.59`)* | To create your own "Victorian" bouquet of flowers, choose varying shapes, sizes and forms, besides a variety of complementary colors. Leaf textures and colors will also be important. |
| **4** | The people waiting in line carried a message, a refutation, of claims that the jobless could be employed if only they showed enough moxie. Every rule has exceptions, but the tragic and too-common tableaux of hundreds or even thousands of people snake-lining up for any task with a paycheck illustrates a lack of jobs, not laziness. | **S1** (`10.30`) *(vs. S2 `4.90`)* | The people waiting in line carried a message, a refutation, of claims that the jobless could be employed if only they showed enough moxie. |
| **5** | While looking over a Scottsdale, Ariz., model house one day, my wife was amused by the real-estate agents, who engaged her in the "you talk kinda funny" conversation. We say "to-mah-to" and Arizonans say "to-may-to." We call the hood of a car a "bonnet" and the trunk a boot. Then, as my wife entered the dining room, one agent pointed to a massive chandelier and asked, "What would you call that in England?" "Ostentatious," my wife replied. | **S1** (`10.14`), **S4** (`4.78`) *(vs. S2 `2.73`, S3 `1.85`, S5 `-0.11`)* | While looking over a Scottsdale, Ariz., model house one day, my wife was amused by the real-estate agents, who engaged her in the "you talk kinda funny" conversation. Then, as my wife entered the dining room, one agent pointed to a massive chandelier and asked, "What would you call that in England?" |
| **6** | When a group of Americans, many in the teaching profession, visited her in Calcutta, they asked her for some advice to take home to their families. "Smile at your wives," she told them. "Smile at your husbands." Thinking that perhaps the counsel was simplistic, coming from an unmarried person, one of them asked, "Are you married?" "Yes," she replied, to their surprise, "and I find it hard sometimes to smile at Jesus. He can be very demanding." | **S1** (`10.54`), **S4** (`4.11`) *(vs. S2 `4.08`, S5 `3.77`, S3 `2.50`)* | When a group of Americans, many in the teaching profession, visited her in Calcutta, they asked her for some advice to take home to their families. Thinking that perhaps the counsel was simplistic, coming from an unmarried person, one of them asked, "Are you married?" |
| **7** | ZPG's 1985 Urban Stress Test, created after months of persistent and exhaustive research, is the nation's first survey of how population-linked pressures affect U.S. cities. It ranks 184 urban areas on 11 different criteria ranging from crowding and birth rates to air quality and toxic wastes. The Urban Stress Test translates complex, technical data into an easy-to-use action tool for concerned citizens, elected officials and opinion leaders. | **S1** (`9.78`), **S3** (`4.50`) *(vs. S2 `3.57`)* | ZPG's 1985 Urban Stress Test, created after months of persistent and exhaustive research, is the nation's first survey of how population-linked pressures affect U.S. cities. The Urban Stress Test translates complex, technical data into an easy-to-use action tool for concerned citizens, elected officials and opinion leaders. |
| **8** | Our knowledge of ancient shipbuilding techniques, for example, is dependent on the work of archaeologists who have painstakingly excavated remains of ships themselves. The contents of shipwrecks are an equally valuable archaeological resource. Since the objects in a wreck represent a single moment in time, they provide better chronological information than even the most carefully excavated terrestrial site. Moreover, perishable items such as foodstuffs, which do not survive well on land, are often preserved underwater. | **S1** (`11.23`), **S2** (`12.65`) *(vs. S3 `4.57`, S4 `2.59`)* | Our knowledge of ancient shipbuilding techniques, for example, is dependent on the work of archaeologists who have painstakingly excavated remains of ships themselves. The contents of shipwrecks are an equally valuable archaeological resource. |
| **9** | In an article for Campus Life magazine, Susan Smart describes her third and nearly last solo flight. She had been practicing a maneuver at 5,000 feet when she lost control and her Cessna 150 began spinning wildly toward earth. After several seconds of panic, she recalled her instructor's words: "If you ever go into a spin in a Cessna 150, just let go of the controls. It's built to fly on its own." | **S1** (`11.30`), **S2** (`4.54`) *(vs. S3 `3.40`)* | In an article for Campus Life magazine, Susan Smart describes her third and nearly last solo flight. She had been practicing a maneuver at 5,000 feet when she lost control and her Cessna 150 began spinning wildly toward earth. |
| **10** | This paper is part of an effort to relate various accounts. It is the first in a pair of papers that compare two particular accounts: Rhetorical Structure Theory and Systemic Linguistics. Rhetorical Structure Theory, initially formulated in 1983, describes texts in terms of functionally-defined relations that hold between their parts. Systemic Linguistics is a much more comprehensive view of language initiated in the early 1960s. Where the two approaches are comparable, Systemic Linguistics describes texts in terms of categories of processes which the texts perform. | **S1** (`10.32`), **S2** (`3.96`) *(vs. S4 `3.93`, S3 `3.40`, S5 `2.64`)* | This paper is part of an effort to relate various accounts. It is the first in a pair of papers that compare two particular accounts: Rhetorical Structure Theory and Systemic Linguistics. |

---

## Problem 4: Comparison with ChatGPT Baseline & Accuracy / F1 Evaluation (10 Points)

We compared our 1-to-2 sentence rule-based RST summaries against a 2-to-3 sentence ChatGPT baseline across all 10 paragraphs (`40` total sentences) with respect to manually identified gold key sentences (grounded in Mann & Thompson's 1988 canonical nuclearity analysis) and content-word unigram overlap (ROUGE-1 style Token F1).

### Per-Paragraph Comparison Table

| Para # | Gold Key Sentences | RST Selected | ChatGPT Summary (2–3 Sentences) | Sent Acc (%) | Sent F1 (%) | Token F1 (RST vs Gold) | Token F1 (RST vs ChatGPT) |
| :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: |
| **1** | `S[1, 4]` | `S[1, 4]` | Endorsing the Nuclear Freeze Initiative is not the right step for California Common Cause because embracing every popular issue drains limited resources where other organizations are already effective. Instead, the organization will remain stronger by focusing on its core agenda of governmental structure and process. | **100.0%** | **100.0%** | **100.0%** | 50.7% |
| **2** | `S[1, 2]` | `S[1, 2]` | As a floppy drive reads or writes, a Syncom diskette works in four ways to prevent dust and loose particles from causing soft errors and dropouts. Its Ectype coating cleans and lubricates the drive head, a carbon additive drains static electricity, strong binders secure the oxides, and a non-woven liner traps collected debris. | **100.0%** | **100.0%** | **100.0%** | 51.4% |
| **3** | `S[1, 3]` | `S[1, 3]` | Creating a Victorian flower bouquet requires selecting varied shapes, sizes, forms, and complementary colors. Tall plants should be surrounded by smaller and trailing varieties, while incorporating diverse leaf textures and foliage colors such as dusty miller, lotus vine, and coleus. | **100.0%** | **100.0%** | **100.0%** | 38.5% |
| **4** | `S[2]` | `S[1]` | The long lines of unemployed people waiting for work refute the claim that joblessness is simply due to a lack of effort or moxie. Seeing hundreds or thousands of applicants lining up for any paid task demonstrates a genuine shortage of jobs rather than laziness. | 0.0% | 0.0% | 5.3% | 13.3% |
| **5** | `S[1, 4]` | `S[1, 4]` | While touring a model house in Scottsdale, Arizona, the narrator's British wife was amused by real-estate agents comparing American and British vocabulary. When an agent pointed to a massive dining room chandelier and asked what she would call it in England, she wittily replied, 'Ostentatious.' | **100.0%** | **100.0%** | **100.0%** | 55.6% |
| **6** | `S[1, 5]` | `S[1, 4]` | When a group of visiting American teachers in Calcutta asked Mother Teresa for family advice, she told husbands and wives to smile at one another. When questioned on whether she was married, she surprised them by replying that she was married to Jesus and found him very demanding at times. | 60.0% | 50.0% | 53.8% | 28.1% |
| **7** | `S[1, 3]` | `S[1, 3]` | ZPG's 1985 Urban Stress Test is the first national survey examining how population-related pressures impact U.S. cities. It ranks 184 urban areas across 11 environmental and demographic criteria, translating complex technical data into an accessible action tool for citizens and leaders. | **100.0%** | **100.0%** | **100.0%** | 58.2% |
| **8** | `S[1, 2]` | `S[1, 2]` | Archaeological excavations of both ship remains and shipwreck contents are vital to our understanding of ancient shipbuilding. Because shipwrecks capture a single moment in time and preserve perishable items like food underwater, they offer superior chronological evidence compared to land sites. | **100.0%** | **100.0%** | **100.0%** | 23.5% |
| **9** | `S[1, 2]` | `S[1, 2]` | In Campus Life magazine, Susan Smart recounts losing control of her Cessna 150 at 5,000 feet during her third solo flight as the plane spun toward earth. Overcoming her panic, she remembered her instructor's advice to simply let go of the controls because the aircraft is designed to stabilize itself. | **100.0%** | **100.0%** | **100.0%** | 50.0% |
| **10** | `S[2, 3]` | `S[1, 2]` | This paper is the first of two studies comparing Rhetorical Structure Theory (RST) and Systemic Linguistics. While RST characterizes texts through functionally defined relations between text parts, Systemic Linguistics offers a broader framework that describes texts through the categories of processes they perform. | 60.0% | 50.0% | 53.3% | 31.4% |

### Overall Micro-Averaged Evaluation Metrics (Across All 40 Sentences)

| Summarization System | Sentence Accuracy | Precision | Recall | Sentence F1-Score | Content-Word Overlap F1 (vs. Gold) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Rule-Based RST Summarizer (1–2 sentences)** | **85.00%** (`34/40`) | **84.21%** (`TP=16, FP=3`) | **84.21%** (`TP=16, FN=3`) | **84.21%** | **81.24%** |
| **ChatGPT Baseline (2–3 sentences)** | 75.00% (`30/40`) | 65.52% (`TP=19, FP=10`) | **100.00%** (`TP=19, FN=0`) | 79.17% | 44.39% *(abstractive paraphrase)* |

---

## Problem 5: Discussion of Results, Rule Analysis & System Improvements (5 Points)

1. **Summarization Quality:** Purely structural RST rules (without any lexical TF-IDF or neural embeddings) achieved **85.00% sentence selection accuracy** and **84.21% F1-score** (**81.24% content-word F1**), achieving a **perfect 100% sentence match on 7 out of 10 paragraphs** (Paragraphs 1, 2, 3, 5, 7, 8, and 9) and partial match (`60%` Accuracy / `50%` F1) on Paragraphs 6 and 10.
2. **Rule Patterns That Worked Well:**
   - **Central Nucleus Promotion (Rule 1) & Marcu Promotion Depth (Rule 2):** In expository and argumentative paragraphs (Paragraphs 1, 2, 3, 7, 8, 9), the central claim is placed in Sentence 1 and promoted all the way to the Root (`promoted_depth = 0`). Following the all-Nucleus path identified the primary topic sentence in 9 out of 10 paragraphs.
   - **Promoted Multinuclear & Explanatory Relations (Rules 2 & 4):** Crediting promoted Nucleus relations (`promoted_nucleus_relations`) to the sentence containing the promoted Nucleus head allowed high-level splits—such as `Contrast (NN)` in Paragraph 1 (`S4`), `Joint (NN)` in Paragraph 2 (`S2`) and Paragraph 3 (`S3`), and `Joint (NN)` at the root of Paragraph 8 (`S1` and `S2`)—to select both halves of the core argument.
   - **Satellite Pruning (Rule 5):** Penalizing subordinate `Background` and deep `Elaboration` satellites effectively filtered out secondary example lists (such as the plant species list in Paragraph 3 S4 and the British/American vocabulary examples in Paragraph 5 S2–S3).
3. **Failure Modes & Where Rules Struggled:**
   - **Parser Nuclearity Errors on Concession/Refutation (Paragraph 4):** In Paragraph 4, Mann & Thompson's human analysis treats S2 (*"Every rule has exceptions, but the tragic and too-common tableaux... illustrates a lack of jobs, not laziness"*) as the stronger thesis, whereas `isanlp_rst` attached S2 as an `Elaboration (NS)` satellite of S1. Because the extractive budget for a 2-sentence paragraph is 1 sentence, the rule-based selector picked S1 over S2.
   - **Deep Narrative / Dialogue Punchlines (Paragraph 6):** In Paragraph 6, Mother Teresa's final answer (`S5`: *'"Yes," she replied, to their surprise, "and I find it hard sometimes to smile at Jesus. He can be very demanding."'* ) is attached as a `Temporal` satellite under `S4` (*'"Are you married?"'* at `PromDepth = 1`), and `isanlp_rst` also segmented an isolated quote mark `"` as `[EDU 13]`, demoting the clause `"and I find it hard sometimes to smile at Jesus"` to `PromDepth = 4`. Consequently, top-down tree scoring selected `S[1, 4]` (`3.77` vs `4.11`) rather than `S[1, 5]`.
   - **Meta-Discourse Openers (Paragraph 10):** In Paragraph 10, S1 (*"This paper is part of an effort to relate various accounts"*) is the syntactic root Nucleus (`promoted_depth = 0`), so tree-top rules select `S[1, 2]` instead of `S[2, 3]`, even though S1 is meta-discourse with lower standalone informativeness than S3.
4. **Ways to Improve the System:**
   - **Sub-Sentence EDU Compression:** Prune `Attribution` (*"I don't believe"*, *"Rather, I think"*) and `Background` satellite EDUs within selected sentences to produce tighter, abstractive-like summaries.
   - **Discourse + Lexical Hybrid Scoring:** Combine learned Logistic Regression RST weights (Extra Credit) with entity/noun-phrase salience so meta-discourse sentences like Paragraph 10 S1 are downweighted relative to entity-rich sentences like S2 and S3.
   - **Anaphora Post-Processing:** Resolve leading pronouns (*"It"*, *"She"*) when a non-initial sentence is extracted without its antecedent.

---

## Extra Credit: Learning Nucleus & Satellite Weights via Logistic Regression (10 Points)

We implemented a custom L2-regularized binary **Logistic Regression** classifier (`SimpleLogisticRegression`, learned intercept $b = -1.6209$) trained via batch gradient descent on 16 discourse features extracted from each sentence ($N=40$ sentences).

### Learned Logistic Regression Weights & RST Theoretical Interpretation

| Rank | Feature / Relation Name | Learned Weight ($w_j$) | Interpretation in Rhetorical Structure Theory (Mann & Thompson, 1988) |
| :---: | :--- | :---: | :--- |
| **1** | `inv_min_depth` | **`+1.0888`** | **Strongest positive predictor:** Confirms hierarchical tree dominance—clauses near the top of the discourse tree subsume lower subtrees. |
| **2** | `inv_promoted_depth` | **`+1.0334`** | Confirms Marcu's (2000) Nuclearity Promotion Principle—sentences promoted close to the Root (`promoted_depth` 0 or 1) carry the central writer intention. |
| **3** | `N_Temporal` | **`+0.6741`** | High positive weight for Nucleus clauses in `Temporal` sequences (e.g., narrative spine events in Paragraphs 2, 5, 6, and 9). |
| **4** | `is_central_nucleus` | **`+0.6345`** | Directly validates Mann & Thompson's nuclearity hypothesis: the unique all-Nucleus root path almost always belongs in the summary. |
| **5** | `max_nucleus_ratio` | **`+0.4980`** | Sentences with high path nuclearity purity ($1 / (1 + \text{satellite\_steps})$) are structurally central. |
| **6** | `N_Elaboration` | **`+0.3180`** | Sentences acting as the **Nucleus** of an `Elaboration` split state the general thesis that subsequent satellites elaborate upon. |
| **7** | `N_Joint` | **`+0.2525`** | Positive weight for multinuclear `Joint` Nuclei (e.g., Paragraph 2 S1–S2, Paragraph 3 S3, and Paragraph 8 S1–S2). |
| **8** | `N_Manner_Means` | **`+0.1320`** | Nucleus of `Manner-Means` (e.g., Paragraph 3 S1 goal statement) expresses the primary objective. |
| **9** | `N_Explanation` | **`+0.1210`** | Sentences acting as the **Nucleus** of an `Explanation` relation represent the core claim being justified by evidence. |
| **10–11** | `S_Background` / `S_Attribution` | `+0.0881` / `+0.0545` | Near-zero weights: occur as minor framing clauses attached inside longer topic sentences (e.g., EDU 0 in Paragraphs 1, 2, 5). |
| **12** | `N_Condition` | **`-0.0527`** | Slight negative weight: reflects conditional clauses inside longer argumentative or instructional sentences. |
| **13** | `S_Elaboration` | **`-0.0575`** | Negative weight: confirms that **Satellites** of `Elaboration` provide optional detail that can be omitted in a brief summary. |
| **14** | `S_Explanation` | **`-0.1131`** | Negative weight: directly mirrors RST theory—while the **Nucleus** of `Explanation` (`+0.1210`) is the essential claim, the **Satellite** of `Explanation` (`-0.1131`) is supporting justification that should be pruned in a compact summary. |
| **15** | `S_Condition_Enablement` | **`-0.3203`** | Strongly negative: `Condition` and `Enablement` satellites express hypothetical or procedural qualifiers rather than the core proposition. |
| **16** | `N_Contrast` | **`-0.4158`** | Negative weight: reflects that many `Contrast` splits in this corpus occur in secondary examples or concessions (e.g., Paragraph 1 S2, Paragraph 5 `"to-mah-to"`, Paragraph 6 S2–S3). |

### Quantitative Performance of Learned Logistic Regression Model
- **Full-Dataset Fit (Top-$K$ Selection):** **Accuracy = 85.00% (`34/40`)**, **F1-Score = 84.21%**, matching the refined rule-based system's high accuracy while learning all weights automatically from data.
- **Leave-One-Paragraph-Out Cross-Validation (LOPO-CV on Unseen Paragraphs):** **Accuracy = 75.00% (`30/40`)**, **F1-Score = 73.68%**, demonstrating strong generalization across unseen rhetorical structures despite training on only 9 paragraphs per fold.

