# DNA Project Phase 3 — Walkthrough, `draw.io` Guide & Viva Preparation

**Course:** Data & Applications (DNA) — Monsoon 2026  
**Assigned Inputs:** Team 63's Phase 1 Requirements (`Initial_Exploration.pdf`) + Team 59's Phase 2 EER Diagram (`EER_diagram.pdf`)  
**Goal:** Convert Team 59's EER diagram for the **Towerrunning World Database (TWDB)** into a complete **Relational Database Schema** following **Elmasri & Navathe Chapter 9 (`ch9.pdf`)** and **Items 1–8 of `dna_phase3_instructions.pdf`**.

---

## 1. Plain-English Walkthrough of What We Did in Phase 3

In **Phase 2**, Team 59 modelled the **Towerrunning World Database (TWDB)** as an EER diagram with **13 Entity Types, 15 Relationships, and 110 Attributes**.  
In **Phase 3**, we translate that EER diagram into **relational tables, columns, underlined primary keys, and foreign-key arrows** using the textbook's 9-step mapping algorithm and the 8 rules in `dna_phase3_instructions.pdf`.

> **Important Constraint from Instructions:**  
> We do **not** perform database normalization (2NF/3NF/BCNF decomposition beyond standard EER-to-Relational mapping) in Phase 3, and we keep EER adjustments strictly minimal.

### Summary of the Conversion (13 Entities + 15 Relationships $\rightarrow$ 19 Relations)
| Instruction Rule / Textbook Step | EER Construct Count | Relations Created / Updated |
| :--- | :---: | :--- |
| **Rule 1 (Step 1): Strong Entities** | 9 | `NATION`, `NATIONAL_ASSOCIATION`, `PERSON`, `VENUE`, `SEASON`, `CHAMPIONSHIP`, `RACE`, `RANKING_EDITION`, `SCORING_RULE` |
| **Rule 2 (Step 2): Weak Entities** | 2 | `COURSE` (owner `RACE` via `HAS_COURSE`), `MEMBERSHIP` (owner `REGISTERED_ATHLETE` via `HOLDS`) |
| **Rule 3 (Steps 3–5): Binary 1:1, 1:N, M:N** | 11 (3 new tables) | **1:1** (`GOVERNS`, `FINAL_OF` $\rightarrow$ FKs), **1:N** (`CITIZEN_OF`, `LOCATED_IN`, `HELD_AT`, `PART_OF`, `DECIDED_AT`, `REPRESENTS` $\rightarrow$ FKs on N-side), **M:N** (`RANKED_IN`, `NATION_RANKED_IN`, `APPLIES_FOR` $\rightarrow$ 3 new tables) |
| **Rule 4 (Step 6): Multi-valued Attributes** | 3 (2 new tables + 1 inlined) | `Contact_Link_1..3` in `NATIONAL_ASSOCIATION` (**Option 4a**, `max = 3`), `VENUE_PHOTO_URLS` (**Option 4b**), `RACE_MEDIA_LINKS` (**Option 4b**) |
| **Rule 5 (Step 7): Degree $n > 2$** | 1 (1 new table) | `FINISHED` (ternary connecting `PERSON`, `COURSE`, `NATION`) |
| **Rule 6 (Step 8): Subclasses / Superclasses** | 2 subclasses | `OFFICIAL` and `REGISTERED_ATHLETE` under `PERSON` (**Option 8A**) |
| **Rule 7 (Step 3): Recursive Relationship** | 1 (0 new tables) | `PRECEDED_BY` (`Prev_Race_Code` self-FK inside `RACE`) |
| **Rule 8 (Step 9): Union Types (Categories)** | 0 | None present in EER diagram |
| **Total in Final Schema** | **19 Relations** | **24 Foreign Key constraints (25 arrows in the diagram)** |

---

## 2. Rule-by-Rule Cheat Sheet (Matching Instructions 1–8 Exactly)

### Rule 1 (Step 1): Strong Entity Types, Composite Attributes & Derived Attributes
- **Candidate keys (`NATION`):** Both `Nation_Code` (3-letter IOC code like `'AUT'`) and `Nation_Name` (`'Austria'`) are underlined in the EER diagram. We chose **`Nation_Code`** as the **Primary Key** (compact, fixed-length code referenced by 5 other relations) and kept `Nation_Name` as a `UNIQUE` alternate key.
- **All 5 Composite Attributes Flattened into Simple Columns:**
  1. `PERSON.Name` $\rightarrow$ `First_Name`, `Last_Name`
  2. `VENUE.Address` $\rightarrow$ `Street`, `City`, `Postal_Code`
  3. `RACE.Contact` $\rightarrow$ `Contact_Person`, `Contact_Email`
  4. `MEMBERSHIP.Payment` $\rightarrow$ `Payment_Method`, `Payment_Reference` (alongside simple attributes `Paid_On` and `Status`)
  5. `SCORING_RULE.Factor_Place` (composite key) $\rightarrow$ **`(Factor, Place)`**
- **All 16 Derived Attributes Omitted from Base Relations (and Explicitly Stated in Report):**
  - `PERSON.Age`, `REGISTERED_ATHLETE.Current_Score`, `MEMBERSHIP.Fee_EUR`, `VENUE.{Course_Record_Male, Course_Record_Female}`, `RACE.{Category, Male_Winner, Female_Winner}`, `COURSE.Is_Evaluated`, `FINISHED.{Gender_Place, Points}`, `RANKED_IN.{Total_Races, Rank_Change, Score_Change}`, `NATION_RANKED_IN.{Total_Races, Rank_Change, Score_Change}`.

### Rule 2 (Step 2): Weak Entity Types (PK = Owner PK + Partial Key)
- **`COURSE`** (owner `RACE` via `R4 HAS_COURSE`):
  - Partial key: `Course_Name`. Full PK: **`(Race_Code, Course_Name)`**, with FK `Race_Code` $\rightarrow$ `RACE(Race_Code)`.
- **`MEMBERSHIP`** (owner `REGISTERED_ATHLETE` via `R5 HOLDS`):
  - Partial key: `Member_Year`. Full PK: **`(Athlete_ID, Member_Year)`**, with FK `Athlete_ID` $\rightarrow$ `REGISTERED_ATHLETE(Athlete_ID)`.

### Rule 3 (Steps 3, 4, 5): Binary 1:1, 1:N, and M:N Relationships
- **Binary 1:1 (Foreign Key Approach):**
  - `R9 GOVERNS` (`NATIONAL_ASSOCIATION (1,1)` — `NATION (0,1)`): Place FK `Nation_Code` (`UNIQUE NOT NULL`) in **`NATIONAL_ASSOCIATION`** because it has **total participation** `(1,1)`.
  - `R7 FINAL_OF` (`SEASON (0,1)` — `RACE (0,1)`): Both partial; place FK `Final_Race_Code` (`UNIQUE`, nullable) in **`SEASON`** (only 1 row per year, avoiding ~99.6% `NULL`s across `RACE`).
- **Binary 1:N (Foreign Key on the N-Side):**
  - `R1 CITIZEN_OF`: `Nation_Code` in `PERSON`
  - `R2 LOCATED_IN`: `Nation_Code` in `VENUE`
  - `R3 HELD_AT`: `Venue_ID` in `RACE`
  - `R6 PART_OF`: `Season_Year` + relationship attribute **`Season_Race_No`** in `RACE`
  - `R8 DECIDED_AT`: `Championship_ID` (nullable) in `RACE`
  - `R10 REPRESENTS`: `Assoc_ID` (nullable) in `OFFICIAL`
- **Binary M:N (Separate Relationship Relations):**
  - **`RANKED_IN(Athlete_ID [PK, FK], Ranking_ID [PK, FK], Rank_Position, Score_Points, Regular_Races, Tour_Races)`**
  - **`NATION_RANKED_IN(Nation_Code [PK, FK], Ranking_ID [PK, FK], Rank_Position, Score_Points, Regular_Races, Tour_Races)`**
  - **`APPLIES_FOR(Athlete_ID [PK, FK], Race_Code [PK, FK], Applied_On, Application_Status, Travel_Reimbursement_EUR)`**

### Rule 4 (Step 6): Multi-Valued Attributes — Both Option 4(a) and Option 4(b) Used
1. **`NATIONAL_ASSOCIATION.Contact_Links` $\rightarrow$ Option 4(a) (`max = 3`: `Contact_Link_1`, `Contact_Link_2`, `Contact_Link_3`)**:
   - *One-line reason:* Sections 1.1 and 2.1 of `Initial_Exploration.pdf` specify a fixed maximum of 3 contact channels per national association (website, Facebook, and e-mail).
2. **`VENUE.Photo_URLs` $\rightarrow$ Option 4(b) (`VENUE_PHOTO_URLS(Venue_ID [PK, FK], Photo_URL [PK])`)**:
   - *One-line reason:* A venue hosts many race editions across years and can accumulate an unbounded number of building photographs.
3. **`RACE.Media_Links` $\rightarrow$ Option 4(b) (`RACE_MEDIA_LINKS(Race_Code [PK, FK], Media_Link [PK])`)**:
   - *One-line reason:* A race can have an unbounded number of external media URLs (race page, results, announcements, and multiple videos/galleries).

### Rule 5 (Step 7): Relationship of Degree $n > 2$ (`R15 FINISHED`)
- **`FINISHED(Person_ID [PK, FK], Race_Code [PK, FK], Course_Name [PK, FK], Nation_Code [FK], Finish_Time, Result_Status)`**
- Contains foreign keys to all 3 participating relations (`PERSON`, `COURSE`, `NATION`).
- **Why `Nation_Code` is NOT in the PK:** Per Chapter 9 Step 7 and Finding C2, a given `(PERSON, COURSE)` pair has at most **1** `NATION` (the country that athlete represented in that race). Hence `(Person_ID, Race_Code, Course_Name)` uniquely identifies the row, and `Nation_Code` is a non-key FK.

### Rule 6 (Step 8): Subclasses and Superclasses (`PERSON` $\rightarrow$ `OFFICIAL`, `REGISTERED_ATHLETE`)
- Overlapping (`o`) and partial specialization $\rightarrow$ **Textbook Option 8A (Multiple relations — superclass and subclasses)**:
  - `OFFICIAL(Person_ID [PK, FK -> PERSON], Official_Role, Since_Year, Assoc_ID [FK])`
  - `REGISTERED_ATHLETE(Athlete_ID [PK], Person_ID [FK -> PERSON, UNIQUE NOT NULL], Username, Email, Registered_On)` — preserves `Athlete_ID` as PK (Finding M3) so `MEMBERSHIP`, `RANKED_IN`, and `APPLIES_FOR` reference `Athlete_ID` directly.

### Rule 7 (Step 3): Recursive Relationship (`R14 PRECEDED_BY`)
- Self-referencing 1:1 relationship on `RACE` (`next (0,1)` to `previous (0,1)`) $\rightarrow$ FK **`Prev_Race_Code`** inside `RACE` referencing `RACE(Race_Code)`.

### Rule 8 (Step 9): Union Types (Categories)
- None exist in Team 59's EER diagram.

---

## 3. Key Viva Pointers ("What to Show the TA") & `draw.io` Guide

### Files to Keep Handy During Evaluation / Submission
1. **`DNA_Phase3_Relational_Model_Report.pdf`** — Your complete formal PDF report:
   - **Pages 1–3:** Concise rule-by-rule explanation (Sections 2.1–2.8 matching Rules 1–8) + minimal EER gap notes (Section 3).
   - **Pages 4–5:** Complete 19-relation summary table with underlined PKs, all attributes, and all `FK -> Target(PK)` mappings + clickable `draw.io` link.
   - **Page 6 (A4 Landscape):** Full-width embedded vector Relational Schema Diagram in Elmasri & Navathe Figure 9.2 notation.
2. **`TWDB_Relational_Schema.drawio`** — Native editable `draw.io` (`app.diagrams.net`) XML file.
3. **`TWDB_Relational_Schema_Diagram.pdf`** — Standalone single-sheet high-resolution vector PDF of the diagram.

### How to Open or Share `TWDB_Relational_Schema.drawio` in `draw.io`
- **Option 1 (Instant Clickable Link Already in Report PDF):** Clicking the blue link at the top of Page 1 (or bottom of Page 5) of `DNA_Phase3_Relational_Model_Report.pdf` opens the full interactive diagram directly in `viewer.diagrams.net` with an **Edit** button—no login or Google Drive permissions required.
- **Option 2 (Upload to Your Google Drive on `app.diagrams.net` if TA Wants a Drive Link):**
  1. Open [https://app.diagrams.net/](https://app.diagrams.net/).
  2. Click **File $\rightarrow$ Open from $\rightarrow$ Device** and select `TWDB_Relational_Schema.drawio`.
  3. Click **File $\rightarrow$ Save as $\rightarrow$ Google Drive**, then click **Share** (top-right) $\rightarrow$ *Anyone with the link can view* if you ever want a short Google Drive URL.

### Quick Pointers When the TA Inspects Your Diagram
- **Color Legend (top-right of diagram):**
  - **Soft Blue (`Primary_Key`, bold + underlined):** Pure primary key column (e.g., `NATION.Nation_Code`, `RACE.Race_Code`).
  - **Soft Green (`PK & FK (Both)`, bold + underlined + arrow out):** Column that is both part of the table's PK and a FK to another table (e.g., `COURSE.Race_Code`, `MEMBERSHIP.Athlete_ID`, `FINISHED.Person_ID`).
  - **Soft Yellow (`Foreign_Key`, arrow out):** Non-key foreign key column (e.g., `PERSON.Nation_Code`, `SEASON.Final_Race_Code`, `FINISHED.Nation_Code`).
- **Arrow Direction:** Every arrow starts with a dot at the **Foreign Key** cell and ends with a filled arrowhead pointing **into the Primary Key** cell it references (matching Elmasri & Navathe Figure 9.2, p. 291).

---

## 4. Likely Viva Questions & Model Answers (12 Questions)

### Q1: Why do you have 19 relations when the EER diagram had 13 entity types?
**Answer:**
- **13 relations** come from the 13 entity types (9 strong + 2 weak `COURSE`, `MEMBERSHIP` + 2 subclasses `OFFICIAL`, `REGISTERED_ATHLETE` under Option 8A).
- **3 relations** come from the 3 binary M:N relationships (`RANKED_IN`, `NATION_RANKED_IN`, `APPLIES_FOR`).
- **1 relation** comes from the ternary relationship (`FINISHED`).
- **2 relations** come from the 2 unbounded multivalued attributes mapped via Option 4(b) (`VENUE_PHOTO_URLS`, `RACE_MEDIA_LINKS`).
- $13 + 3 + 1 + 2 = 19$ relations.

### Q2: Why did you use Option 4(a) for `Contact_Links` on `NATIONAL_ASSOCIATION`, but Option 4(b) for `Photo_URLs` and `Media_Links`?
**Answer:**
- Rule 4 says to use **4(a)** when a small, fixed maximum number of values is known from the requirements, and **4(b)** when the count is not fixed or can grow large.
- Sections 1.1 and 2.1 of `Initial_Exploration.pdf` explicitly specify at most **3** contact links per national association (website, Facebook, e-mail), so `Contact_Link_1..3` in `NATIONAL_ASSOCIATION` avoids an extra join table.
- By contrast, venues accumulate photos across years of races (`Photo_URLs`) and races can have arbitrarily many result/video/gallery links (`Media_Links`), so separate tables (`VENUE_PHOTO_URLS`, `RACE_MEDIA_LINKS`) avoid `NULL` padding or artificial caps.

### Q3: In `R9 GOVERNS` (`NATIONAL_ASSOCIATION` 1:1 `NATION`), why is `Nation_Code` placed in `NATIONAL_ASSOCIATION` rather than putting `Assoc_ID` in `NATION`?
**Answer:**
- By Chapter 9 Step 3, for a 1:1 relationship with total participation on one side, we place the foreign key in the relation with **total participation**.
- Every `NATIONAL_ASSOCIATION` governs a nation `(1,1)`, whereas most countries in `NATION` do not have a national towerrunning association `(0,1)`. Putting `Nation_Code` in `NATIONAL_ASSOCIATION` guarantees zero `NULL`s on that FK.

### Q4: Why couldn't you merge `NATIONAL_ASSOCIATION` and `NATION` into a single relation (Step 3, Merged Relation Approach)?
**Answer:**
- Step 3 states that merging two 1:1 entities into a single relation is only valid when **both** participations are total `(1,1)`. Since `NATION` has partial participation `(0,1)` in `GOVERNS`, merging would force `NULL` values for `Assoc_ID`, `Assoc_Name`, and `Founded_Year` on every country without an association.

### Q5: In `R7 FINAL_OF` (`SEASON` 1:1 `RACE`), both sides have partial participation `(0,1)`. Why put `Final_Race_Code` in `SEASON` instead of `RACE`?
**Answer:**
- There is only 1 `SEASON` row per year (and once the Tour Final is announced, `Final_Race_Code` is non-null), whereas there are 200+ `RACE` rows per year of which only 1 is the Final. Putting the FK in `SEASON` avoids 99.5% `NULL` values in `RACE`.

### Q6: Where did the relationship attribute `Season_Race_No` on `R6 PART_OF` go, and why?
**Answer:**
- `R6 PART_OF` is a 1:N relationship (`SEASON` is the 1-side, `RACE` is the N-side, since each race belongs to one season). By Step 4, both the 1-side PK (`Season_Year`) and any relationship attributes (`Season_Race_No`) migrate into the **N-side** relation (`RACE`).

### Q7: Why does `FINISHED` have two foreign key arrows pointing to `COURSE`?
**Answer:**
- `COURSE` is a weak entity identified by `RACE`, so its primary key is composite: `(Race_Code, Course_Name)`. Any foreign key referencing `COURSE` must include **both** columns `(Race_Code, Course_Name)` referencing `COURSE(Race_Code, Course_Name)`.

### Q8: Why is `Nation_Code` a Foreign Key in `FINISHED`, but NOT underlined as part of `FINISHED`'s Primary Key?
**Answer:**
- By Chapter 9 Step 7, if a participant in an $n$-ary relationship has a cardinality constraint of **1** for a given combination of the other participants, its FK is omitted from the relationship relation's PK.
- In `FINISHED`, each `(PERSON, COURSE)` pair has at most **one** race-day `NATION` (an athlete cannot finish the same course twice for two different countries). Thus `(Person_ID, Race_Code, Course_Name)` already uniquely identifies each row.

### Q9: Why do both `PERSON` and `FINISHED` have a `Nation_Code` foreign key? Isn't that redundant?
**Answer:**
- No—as noted in Phase 2 Finding C2, `PERSON.Nation_Code` stores the person's *current* citizenship (`CITIZEN_OF`), while `FINISHED.Nation_Code` stores the *historical nationality they raced under on race day*. If an athlete changes citizenship later, historical Nation Rankings must still credit the country they represented on the day of that race.

### Q10: Why did you choose Option 8A over Options 8B, 8C, and 8D for `PERSON` $\rightarrow$ `{OFFICIAL, REGISTERED_ATHLETE}`?
**Answer:**
- The specialization is **partial** (unregistered race finishers belong to neither subclass) and **overlapping** (officials like Wai Ching Soh also compete as registered athletes).
- **Option 8B** (subclasses only) loses unregistered finishers (violating partial) and duplicates people who are both officials and athletes (violating overlapping).
- **Option 8C** (single table + 1 type column) only works for **disjoint** subclasses.
- **Option 8D** (single table + 2 boolean flags) would put 6 nullable columns on thousands of unregistered finishers and cannot cleanly enforce foreign keys from `MEMBERSHIP`, `RANKED_IN`, and `APPLIES_FOR` to *only* registered athletes.
- **Option 8A** handles partial + overlapping cleanly with zero duplication and clean subclass-level foreign keys.

### Q11: In `REGISTERED_ATHLETE`, textbook Option 8A normally uses `Person_ID` as the PK. Why did you make `Athlete_ID` the PK and `Person_ID` a `UNIQUE NOT NULL` FK?
**Answer:**
- In Team 63's requirements and Team 59's EER diagram (Finding M3), `REGISTERED_ATHLETE` defines `Athlete_ID` as its domain identifier, and weak entity `MEMBERSHIP` explicitly forms its key as `(Athlete_ID, Member_Year)`. Making `Athlete_ID` the PK while keeping `Person_ID` `UNIQUE NOT NULL REFERENCES PERSON(Person_ID)` preserves strict 1-to-1 subclass inheritance under Option 8A while keeping `MEMBERSHIP`, `RANKED_IN`, and `APPLIES_FOR` foreign keys consistent with the EER diagram.

### Q12: Why is `SCORING_RULE` not connected by any foreign key arrow in the schema diagram?
**Answer:**
- As documented in Team 59's Finding C1, `SCORING_RULE(Factor, Place, Points)` is a standalone scoring lookup matrix. In `FINISHED`, `Points` is a **derived** attribute computed at query time by matching `RACE.Factor` and the derived `Gender_Place` against `SCORING_RULE(Factor, Place)`. Since `Gender_Place` and `Points` are derived (not stored), there is no stored foreign key to `SCORING_RULE`.
