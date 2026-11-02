# Project Phase 3: Relational Database Schema — Towerrunning World Database (TWDB)

- **Domain & Phase 1 Requirements:** Team 63 (Carromboard) — *Project Phase 1: Data Requirements — Tower Running* (`https://www.towerrunning.com`)
- **Assigned Phase 2 EER Model:** Team 59 (Aggregays) — *Phase 2: EER Model of Team 63's Tower Running Requirements* (13 Entity Types, 15 Relationship Types, 110 Attributes)
- **Relational Schema Diagram (`draw.io` file):** `TWDB_Relational_Schema.drawio` (interactive `draw.io` link included in the PDF report; full vector diagram also in `TWDB_Relational_Schema_Diagram.pdf`)

---

## 1. Overview of the EER-to-Relational Mapping

We convert Team 59's Enhanced Entity-Relationship (EER) diagram into a relational database schema following **Elmasri & Navathe Chapter 9 (Steps 1–9)** and **Items 1–8 of the Phase 3 instructions**. As instructed, **no normalization** is performed beyond the direct EER-to-relational mapping rules, and all 16 derived attributes are omitted from stored base relations and explicitly noted below.

The resulting relational schema contains **19 relations** and **24 foreign key constraints** (25 attribute-level arrows, as the composite foreign key to `COURSE` spans 2 columns):
- **9 strong entity relations:** `NATION`, `NATIONAL_ASSOCIATION`, `PERSON`, `VENUE`, `SEASON`, `CHAMPIONSHIP`, `RACE`, `RANKING_EDITION`, `SCORING_RULE`
- **2 weak entity relations:** `COURSE`, `MEMBERSHIP`
- **2 subclass relations:** `OFFICIAL`, `REGISTERED_ATHLETE`
- **2 multi-valued attribute relations:** `VENUE_PHOTO_URLS`, `RACE_MEDIA_LINKS`
- **3 binary $M:N$ relationship relations:** `RANKED_IN`, `NATION_RANKED_IN`, `APPLIES_FOR`
- **1 ternary ($n = 3$) relationship relation:** `FINISHED`

---

## 2. Step-by-Step Mapping Explanation (Following Instructions 1–8)

### 2.1 Strong Entity Types, Composite Attributes, and Derived Attributes (Rule 1 / Step 1)

Each of the 9 strong entity types is mapped to a relation containing its simple attributes and the simple components of any composite attributes:

1. **`NATION`**: Mapped with attributes `Nation_Code`, `Nation_Name`, and `Continent`. Both `Nation_Code` and `Nation_Name` are underlined as candidate keys in the EER diagram; we choose **`Nation_Code`** as the primary key and keep `Nation_Name` as a `UNIQUE` alternate key.
2. **`NATIONAL_ASSOCIATION`**: Mapped with primary key **`Assoc_ID`** and simple attributes `Assoc_Name` and `Founded_Year` (plus `Contact_Link_1..3` from Rule 4(a) and foreign key `Nation_Code` from `GOVERNS`).
3. **`PERSON`**: Mapped with primary key **`Person_ID`** and simple attributes `Gender` and `Date_of_Birth` (plus foreign key `Nation_Code` from `CITIZEN_OF`).
   - *Composite attribute flattened:* `Name` becomes simple columns **`First_Name`** and **`Last_Name`**.
   - *Derived attribute not stored:* **`Age`** is omitted because it is computed dynamically from `Date_of_Birth` and the current date.
4. **`VENUE`**: Mapped with primary key **`Venue_ID`** and simple attributes `Venue_Name`, `Venue_Type`, and `Building_Height_m` (plus foreign key `Nation_Code` from `LOCATED_IN`).
   - *Composite attribute flattened:* `Address` becomes simple columns **`Street`**, **`City`**, and **`Postal_Code`**.
   - *Derived attributes not stored:* **`Course_Record_Male`** and **`Course_Record_Female`** are omitted because they are computed as the fastest evaluated `FIN` time per gender across courses at that venue.
5. **`SEASON`**: Mapped with primary key **`Season_Year`** and simple attributes `Start_Date`, `End_Date`, `Invites_Per_Gender`, `Wildcards_Per_Gender`, and `Invitation_Cutoff` (plus foreign key `Final_Race_Code` from `FINAL_OF`).
6. **`CHAMPIONSHIP`**: Mapped with primary key **`Championship_ID`** and simple attributes `Title`, `Level`, `Region`, and `Year`.
7. **`RACE`**: Mapped with primary key **`Race_Code`** and simple attributes `Race_Name`, `Race_Date`, `Duration_Days`, `Edition_No`, `Factor`, `Status`, `Evaluation_Status`, `Results_Received_On`, and `Additional_Info` (plus foreign keys/attributes from `HELD_AT`, `PART_OF`, `DECIDED_AT`, and `PRECEDED_BY`).
   - *Composite attribute flattened:* `Contact` becomes simple columns **`Contact_Person`** and **`Contact_Email`**.
   - *Derived attributes not stored:* **`Category`** (derived from whether `Factor >= 60`), **`Male_Winner`**, and **`Female_Winner`** (derived from `FINISHED` where `Gender_Place = 1` on the evaluated course) are omitted.
8. **`RANKING_EDITION`**: Mapped with primary key **`Ranking_ID`** and simple attributes `Edition_Label`, `Period_Start`, `Period_End`, `Revision_No`, `Is_Season_Final`, and `Published_On`.
9. **`SCORING_RULE`**: Mapped with simple attribute `Points`.
   - *Composite primary key flattened:* The composite key `Factor_Place` becomes its simple component attributes **`(Factor, Place)`**, which together form the composite primary key of `SCORING_RULE`.

---

### 2.2 Weak Entity Types and Identifying Relationships (Rule 2 / Step 2)

1. **`COURSE` (Owner: `RACE` via identifying relationship `R4 HAS_COURSE`)**:
   - Includes owner primary key **`Race_Code`** as a foreign key referencing `RACE(Race_Code)`, combined with partial key **`Course_Name`** to form composite primary key **`(Race_Code, Course_Name)`** (absorbing `R4 HAS_COURSE`).
   - Simple attributes included: `Race_Mode`, `Upward_Stairs`, `Downward_Stairs`, `Floors`, `Vertical_Metres`, `Flat_Section_m`, `Special_Info`, and `Stair_Time_Share_Pct`.
   - *Derived attribute not stored:* **`Is_Evaluated`** is omitted (derived as `true` for the course with maximum `Upward_Stairs` in its race).
2. **`MEMBERSHIP` (Owner: `REGISTERED_ATHLETE` via identifying relationship `R5 HOLDS`)**:
   - Includes owner primary key **`Athlete_ID`** as a foreign key referencing `REGISTERED_ATHLETE(Athlete_ID)`, combined with partial key **`Member_Year`** to form composite primary key **`(Athlete_ID, Member_Year)`** (absorbing `R5 HOLDS`).
   - *Composite attribute flattened:* `Payment` becomes simple columns **`Payment_Method`** and **`Payment_Reference`**, alongside simple attributes `Paid_On` and `Status`.
   - *Derived attribute not stored:* **`Fee_EUR`** is omitted (derived from `Member_Year` and birth year: `18` if age $\le 20$ or $\ge 50$, else `24`).

---

### 2.3 Binary 1:1, 1:N, and M:N Relationships (Rule 3 / Steps 3, 4, 5)

#### (a) Binary 1:1 Relationships (Step 3 — Foreign Key Approach)
- **`R9 GOVERNS` (`NATIONAL_ASSOCIATION (1,1)` — `NATION (0,1)`)**: Foreign key **`Nation_Code`** (`UNIQUE NOT NULL`, referencing `NATION(Nation_Code)`) is placed in **`NATIONAL_ASSOCIATION`** because `NATIONAL_ASSOCIATION` has total participation `(1,1)`.
- **`R7 FINAL_OF` (`SEASON (0,1)` — `RACE (0,1)`)**: Both sides are partial; foreign key **`Final_Race_Code`** (`UNIQUE`, nullable, referencing `RACE(Race_Code)`) is placed in **`SEASON`** (1 row per year, avoiding `NULL`s across hundreds of non-final `RACE` rows).

#### (b) Binary 1:N Relationships (Step 4 — Foreign Key Approach on the $N$-Side)
- **`R1 CITIZEN_OF` (`PERSON (1,1)` — `NATION (0,N)`)**: Foreign key **`Nation_Code`** placed in $N$-side relation **`PERSON`** referencing `NATION(Nation_Code)`.
- **`R2 LOCATED_IN` (`VENUE (1,1)` — `NATION (0,N)`)**: Foreign key **`Nation_Code`** placed in $N$-side relation **`VENUE`** referencing `NATION(Nation_Code)`.
- **`R3 HELD_AT` (`RACE (1,1)` — `VENUE (0,N)`)**: Foreign key **`Venue_ID`** placed in $N$-side relation **`RACE`** referencing `VENUE(Venue_ID)`.
- **`R6 PART_OF` (`RACE (1,1)` — `SEASON (0,N)`)**: Foreign key **`Season_Year`** (referencing `SEASON(Season_Year)`) and relationship attribute **`Season_Race_No`** placed in $N$-side relation **`RACE`**.
- **`R8 DECIDED_AT` (`CHAMPIONSHIP (1,N)` — `RACE (0,1)`)**: Foreign key **`Championship_ID`** (nullable, referencing `CHAMPIONSHIP(Championship_ID)`) placed in $N$-side relation **`RACE`**.
- **`R10 REPRESENTS` (`OFFICIAL (0,1)` — `NATIONAL_ASSOCIATION (1,N)`)**: Foreign key **`Assoc_ID`** (nullable, referencing `NATIONAL_ASSOCIATION(Assoc_ID)`) placed in $N$-side relation **`OFFICIAL`**.

#### (c) Binary M:N Relationships (Step 5 — Separate Relationship Relations)
1. **`RANKED_IN` (`R11`: `REGISTERED_ATHLETE (0,N)` — `RANKING_EDITION (1,N)`)**:
   - Relation **`RANKED_IN`** with composite primary key **`(Athlete_ID, Ranking_ID)`** referencing `REGISTERED_ATHLETE(Athlete_ID)` and `RANKING_EDITION(Ranking_ID)`, plus stored attributes `Rank_Position`, `Score_Points`, `Regular_Races`, and `Tour_Races`.
   - *Derived attributes not stored:* **`Total_Races`** (`Regular_Races + Tour_Races`), **`Rank_Change`**, and **`Score_Change`** are omitted.
2. **`NATION_RANKED_IN` (`R12`: `NATION (0,N)` — `RANKING_EDITION (1,N)`)**:
   - Relation **`NATION_RANKED_IN`** with composite primary key **`(Nation_Code, Ranking_ID)`** referencing `NATION(Nation_Code)` and `RANKING_EDITION(Ranking_ID)`, plus stored attributes `Rank_Position`, `Score_Points`, `Regular_Races`, and `Tour_Races`.
   - *Derived attributes not stored:* **`Total_Races`**, **`Rank_Change`**, and **`Score_Change`** are omitted.
3. **`APPLIES_FOR` (`R13`: `REGISTERED_ATHLETE (0,N)` — `RACE (0,N)`)**:
   - Relation **`APPLIES_FOR`** with composite primary key **`(Athlete_ID, Race_Code)`** referencing `REGISTERED_ATHLETE(Athlete_ID)` and `RACE(Race_Code)`, plus stored attributes `Applied_On`, `Application_Status`, and `Travel_Reimbursement_EUR`.

---

### 2.4 Multi-Valued Attributes (Rule 4 / Step 6)

1. **`Contact_Links` on `NATIONAL_ASSOCIATION`** — **Option 4(a) (Same relation, Maximum = 3 values: `Contact_Link_1`, `Contact_Link_2`, `Contact_Link_3`)**:
   - *One-line reason:* Sections 1.1 and 2.1 of the requirements specify a small, fixed maximum of three contact links per national association (website, Facebook, and e-mail).
2. **`Photo_URLs` on `VENUE`** — **Option 4(b) (Separate relation `VENUE_PHOTO_URLS` with PK `(Venue_ID, Photo_URL)` and FK `Venue_ID` $\rightarrow$ `VENUE(Venue_ID)`)**:
   - *One-line reason:* A venue hosts many race editions across years and can accumulate an unbounded number of building photographs over time.
3. **`Media_Links` on `RACE`** — **Option 4(b) (Separate relation `RACE_MEDIA_LINKS` with PK `(Race_Code, Media_Link)` and FK `Race_Code` $\rightarrow$ `RACE(Race_Code)`)**:
   - *One-line reason:* A race can have an unbounded number of external media URLs (race page, results, TWA announcement, and multiple videos and photo galleries).

---

### 2.5 Relationships of Degree $n > 2$ (Rule 5 / Step 7)

- **`FINISHED` (`R15` — Ternary relationship among `PERSON`, `COURSE`, and `NATION`)**:
  - Mapped to relation **`FINISHED`** containing foreign keys to all three participating relations: `Person_ID` $\rightarrow$ `PERSON(Person_ID)`, `(Race_Code, Course_Name)` $\rightarrow$ `COURSE(Race_Code, Course_Name)`, and `Nation_Code` $\rightarrow$ `NATION(Nation_Code)`, plus simple attributes `Finish_Time` and `Result_Status`.
  - **Primary Key:** **`(Person_ID, Race_Code, Course_Name)`** (per Chapter 9 Step 7, `Nation_Code` is excluded from the primary key because each person finishes a given course at most once for a single race-day nation).
  - *Derived attributes not stored:* **`Gender_Place`** and **`Points`** are omitted.

---

### 2.6 Subclasses and Superclasses — Specialization Mapping (Rule 6 / Step 8)

- The specialization of **`PERSON`** into **`OFFICIAL`** and **`REGISTERED_ATHLETE`** is **overlapping (`o`) and partial**.
- **Textbook Option Used:** **Option 8A (Multiple relations — superclass and subclasses)** from Elmasri & Navathe Section 9.2.1. Option 8B is inapplicable because the specialization is partial and overlapping; Options 8C/8D would create `NULL`-heavy rows on `PERSON` and cannot cleanly host subclass-specific relationships (`REPRESENTS`, `HOLDS`, `RANKED_IN`, `APPLIES_FOR`) and unique athlete keys.
  1. **`OFFICIAL`**: Primary key **`Person_ID`** (foreign key referencing `PERSON(Person_ID)`), local attributes `Official_Role` and `Since_Year`, and foreign key `Assoc_ID` (from `REPRESENTS`).
  2. **`REGISTERED_ATHLETE`**: Primary key **`Athlete_ID`** (see Section 3.1), foreign key `Person_ID` (`UNIQUE NOT NULL`, referencing `PERSON(Person_ID)`), `UNIQUE` alternate keys `Username` and `Email`, and local attribute `Registered_On`.
     - *Derived attribute not stored:* **`Current_Score`** is omitted (computed as the sum of the athlete's best 8 race points in the last 12 months).

---

### 2.7 Recursive Relationships (Rule 7 / Step 3)

- **`R14 PRECEDED_BY` (`RACE` as `next` `(0,1)` — `RACE` as `previous` `(0,1)`, recursive 1:1)**:
  - Mapped using a self-referencing foreign key **`Prev_Race_Code`** (`UNIQUE`, nullable) inside **`RACE`** referencing **`RACE(Race_Code)`**, pointing from a race edition to its immediately preceding edition (`NULL` for a first edition).

---

### 2.8 Union Types / Categories (Rule 8 / Step 9)

- No union types (categories) or shared subclasses exist in the EER diagram, so Step 9 is not required.

---

## 3. Minimal Corrections / Gaps Noted in the EER Diagram

1. **Subclass Key of `REGISTERED_ATHLETE` (Phase 2 Finding M3):** In Team 59's EER diagram, `REGISTERED_ATHLETE` underlines `Athlete_ID`, `Username`, and `Email` besides inheriting `Person_ID`, and weak entity `MEMBERSHIP` uses `Athlete_ID` in its full key `(Athlete_ID, Member_Year)`. Under Option 8A, we keep `Person_ID` as a `UNIQUE NOT NULL` foreign key referencing `PERSON(Person_ID)` and choose `Athlete_ID` as the primary key of `REGISTERED_ATHLETE` (with `Username` and `Email` as `UNIQUE` alternate keys) so `MEMBERSHIP`, `RANKED_IN`, and `APPLIES_FOR` reference `Athlete_ID` directly.
2. **Ternary `FINISHED` Functional Dependency (Phase 2 Finding C2 & M2):** Because `(min, max)` notation on a ternary cannot draw `(PERSON, COURSE)` $\rightarrow$ `NATION`, the EER diagram labels all three edges `(0,N)`. Following Chapter 9 Step 7, we make `(Person_ID, Race_Code, Course_Name)` the primary key of `FINISHED` and keep `Nation_Code` as a non-key foreign key referencing `NATION(Nation_Code)`.

---

## 4. Complete Relational Schema Summary (All 19 Relations)

Primary key attributes are **<u>underlined</u>**, and foreign keys are shown with arrows ($\rightarrow$) to the referenced primary key:

| # | Relation Name | Attributes (Primary Key <u>Underlined</u>) | Foreign Keys ($\text{FK} \rightarrow \text{Target Relation(PK)}$) |
| :-: | :--- | :--- | :--- |
| 1 | **`NATION`** | <u>`Nation_Code`</u>, `Nation_Name`, `Continent` | *None* (`Nation_Name` is `UNIQUE`) |
| 2 | **`NATIONAL_ASSOCIATION`** | <u>`Assoc_ID`</u>, `Assoc_Name`, `Founded_Year`, `Contact_Link_1`, `Contact_Link_2`, `Contact_Link_3`, `Nation_Code` | `Nation_Code` $\rightarrow$ `NATION(Nation_Code)` |
| 3 | **`PERSON`** | <u>`Person_ID`</u>, `First_Name`, `Last_Name`, `Gender`, `Date_of_Birth`, `Nation_Code` | `Nation_Code` $\rightarrow$ `NATION(Nation_Code)` |
| 4 | **`OFFICIAL`** | <u>`Person_ID`</u>, `Official_Role`, `Since_Year`, `Assoc_ID` | `Person_ID` $\rightarrow$ `PERSON(Person_ID)`<br>`Assoc_ID` $\rightarrow$ `NATIONAL_ASSOCIATION(Assoc_ID)` |
| 5 | **`REGISTERED_ATHLETE`** | <u>`Athlete_ID`</u>, `Person_ID`, `Username`, `Email`, `Registered_On` | `Person_ID` $\rightarrow$ `PERSON(Person_ID)` (`Person_ID`, `Username`, `Email` `UNIQUE`) |
| 6 | **`MEMBERSHIP`** | <u>`Athlete_ID`</u>, <u>`Member_Year`</u>, `Payment_Method`, `Payment_Reference`, `Paid_On`, `Status` | `Athlete_ID` $\rightarrow$ `REGISTERED_ATHLETE(Athlete_ID)` |
| 7 | **`VENUE`** | <u>`Venue_ID`</u>, `Venue_Name`, `Venue_Type`, `Street`, `City`, `Postal_Code`, `Building_Height_m`, `Nation_Code` | `Nation_Code` $\rightarrow$ `NATION(Nation_Code)` |
| 8 | **`VENUE_PHOTO_URLS`** | <u>`Venue_ID`</u>, <u>`Photo_URL`</u> | `Venue_ID` $\rightarrow$ `VENUE(Venue_ID)` |
| 9 | **`SEASON`** | <u>`Season_Year`</u>, `Start_Date`, `End_Date`, `Invites_Per_Gender`, `Wildcards_Per_Gender`, `Invitation_Cutoff`, `Final_Race_Code` | `Final_Race_Code` $\rightarrow$ `RACE(Race_Code)` |
| 10 | **`CHAMPIONSHIP`** | <u>`Championship_ID`</u>, `Title`, `Level`, `Region`, `Year` | *None* |
| 11 | **`RACE`** | <u>`Race_Code`</u>, `Race_Name`, `Race_Date`, `Duration_Days`, `Edition_No`, `Factor`, `Status`, `Evaluation_Status`, `Results_Received_On`, `Additional_Info`, `Contact_Person`, `Contact_Email`, `Venue_ID`, `Season_Year`, `Season_Race_No`, `Championship_ID`, `Prev_Race_Code` | `Venue_ID` $\rightarrow$ `VENUE(Venue_ID)`<br>`Season_Year` $\rightarrow$ `SEASON(Season_Year)`<br>`Championship_ID` $\rightarrow$ `CHAMPIONSHIP(Championship_ID)`<br>`Prev_Race_Code` $\rightarrow$ `RACE(Race_Code)` |
| 12 | **`RACE_MEDIA_LINKS`** | <u>`Race_Code`</u>, <u>`Media_Link`</u> | `Race_Code` $\rightarrow$ `RACE(Race_Code)` |
| 13 | **`COURSE`** | <u>`Race_Code`</u>, <u>`Course_Name`</u>, `Race_Mode`, `Upward_Stairs`, `Downward_Stairs`, `Floors`, `Vertical_Metres`, `Flat_Section_m`, `Special_Info`, `Stair_Time_Share_Pct` | `Race_Code` $\rightarrow$ `RACE(Race_Code)` |
| 14 | **`FINISHED`** | <u>`Person_ID`</u>, <u>`Race_Code`</u>, <u>`Course_Name`</u>, `Nation_Code`, `Finish_Time`, `Result_Status` | `Person_ID` $\rightarrow$ `PERSON(Person_ID)`<br>`(Race_Code, Course_Name)` $\rightarrow$ `COURSE(Race_Code, Course_Name)`<br>`Nation_Code` $\rightarrow$ `NATION(Nation_Code)` |
| 15 | **`APPLIES_FOR`** | <u>`Athlete_ID`</u>, <u>`Race_Code`</u>, `Applied_On`, `Application_Status`, `Travel_Reimbursement_EUR` | `Athlete_ID` $\rightarrow$ `REGISTERED_ATHLETE(Athlete_ID)`<br>`Race_Code` $\rightarrow$ `RACE(Race_Code)` |
| 16 | **`RANKING_EDITION`** | <u>`Ranking_ID`</u>, `Edition_Label`, `Period_Start`, `Period_End`, `Revision_No`, `Is_Season_Final`, `Published_On` | *None* |
| 17 | **`RANKED_IN`** | <u>`Athlete_ID`</u>, <u>`Ranking_ID`</u>, `Rank_Position`, `Score_Points`, `Regular_Races`, `Tour_Races` | `Athlete_ID` $\rightarrow$ `REGISTERED_ATHLETE(Athlete_ID)`<br>`Ranking_ID` $\rightarrow$ `RANKING_EDITION(Ranking_ID)` |
| 18 | **`NATION_RANKED_IN`** | <u>`Nation_Code`</u>, <u>`Ranking_ID`</u>, `Rank_Position`, `Score_Points`, `Regular_Races`, `Tour_Races` | `Nation_Code` $\rightarrow$ `NATION(Nation_Code)`<br>`Ranking_ID` $\rightarrow$ `RANKING_EDITION(Ranking_ID)` |
| 19 | **`SCORING_RULE`** | <u>`Factor`</u>, <u>`Place`</u>, `Points` | *None* |
