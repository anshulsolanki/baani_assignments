# World Beard and Moustache Championships (WBMC) — Phase 4 Data & Application Guide
**Course**: Data and Applications (DnA)  
**Deliverable**: Phase 4 — Database Implementation, Population & Web Application  
**Role**: Person 2 (Data Lead — `populate.sql`)  
**Student**: Baani (2nd Year B.Tech CSE / CLD)

---

## 1. Domain & Project Overview

### What is the Mini-World?
The project models the **World Beard and Moustache Championships (WBMC)**, sanctioned by the **World Beard and Moustache Association (WBMA)**. It tracks:
- **Championship Editions**: Held biennially in host cities around the world (e.g., Austin 2017, Antwerp 2019, Burghausen 2023, Pittsburgh 2025).
- **Categories**: Highly specific facial hair categories across 4 main category groups: *Moustache* (English, Dali, Freestyle, Imperial), *Partial Beard* (Goatee, Musketeer), *Full Beard* (Natural, Garibaldi, Verdi, Freestyle), and *Craft* (realistic/creative craft beards).
- **Competitors & Clubs**: Athletes representing their nations and facial hair clubs (e.g., Austin Facial Hair Club, Beard Team USA, Snorrenclub Antwerpen).
- **Competition Lifecycle**: Bidding for host status, ticketing, registration, category check-in, scoring/placement, Best in Show honours, and formal change requests.

---

## 2. Person 2 (Data Lead) Implementation Strategy

### A. Topological Insertion Order
Because all foreign keys in `schema.sql` are enforced with `ON DELETE RESTRICT ON UPDATE CASCADE`, records must be inserted strictly from parent to child to avoid foreign key violations:
1. **Independent Reference Entities**: `PERSON`, `CLUB`, `VENUE`, `CATEGORY`, `CHARITY`
2. **Multivalued Attributes**: `PERSON_ALIAS`, `PERSON_EMAIL`, `CLUB_ALIAS`, `CLUB_WEB_LINK`, `CATEGORY_ALIAS`
3. **Core Event Parent**: `CHAMPIONSHIP`
4. **Championship Dependents**: `CHAMP_EVENT_DATE`, `CHAMP_ATTENDANCE_CLAIM`, `GROUP_COVERAGE`, `OFFERS`, `SUPPORTS`
5. **Subclasses & Appointments**: `COMPETITOR`, `WBMA_OFFICER`, `OFFICER_APPOINTMENT`, `ORGANIZES`
6. **Host Bidding**: `HOST_BID`, `HOST_BID_REPRESENTATIVE`
7. **Tickets & Editions**: `TICKET`, `COMPETITOR_AT_EDITION`
8. **Event Participation**: `COMPETES_IN`, `MEMBER_OF`, `BEST_IN_SHOW`, `ENTRY_FOR_CLUB`
9. **Administrative Tracking**: `CHANGE_RECORD`

### B. Pre-Configured Test Fixtures for UI & Video Demo
To satisfy the assignment rubric (Section 4.3 & 5), Person 2 must supply demo-ready rows for Person 3 (Backend) and Person 4 (Frontend):
- **Query 1 (Search by Name / Text)**: Search competitors (`PERSON.Display_Name`) or clubs.
- **Query 2 (Filter by Status / Category)**: Filter championships by `Status` ('Completed' vs 'Upcoming') or categories by `Styling_Aids`.
- **Query 3 (Join Detail Page)**: View Championship 2017 details, joining `CHAMPIONSHIP`, `VENUE`, `CLUB`, and `CHAMP_EVENT_DATE`.
- **Query 4 (Aggregation / Leaderboard)**: Count competitors per country, or calculate average scores by category.
- **Query 5 (Multi-table Join)**: Competitor profile showing their club membership, entered categories, scores, and Best-in-Show awards.
- **Update 1 (CREATE / INSERT Demo)**: Form to register a new competitor or purchase a spectator ticket.
- **Update 2 (UPDATE Demo)**: Competitor check-in for 2025 Pittsburgh: `Lucas Vance` (Person_ID 16, Competitor_No 401) is seeded with `Checked_In = FALSE`, `Check_In_At = NULL`, `Entry_Status = 'Registered'`, ready to be updated via the UI to `Checked_In = TRUE`, `Check_In_At = NOW()`, `Entry_Status = 'Checked_in'`.
- **Update 3 (DELETE Demo)**: Ticket `(Champ_ID = 4, Ticket_No = 999)` is a valid day ticket held by spectator Oliver Queen with NO dependent records. It can be safely deleted/cancelled in the UI without triggering foreign key `RESTRICT` violations.

---

## 3. Key Viva Pointers ("What to Show the TA")

1. **Topological Order**:
   - Highlight lines 1–105 (`PERSON`, `CLUB`, `VENUE`, `CATEGORY`) and explain how parent tables are populated before any junction or weak entity.
2. **Referential Integrity & Constraints**:
   - Point out `TICKET`: Show how Weekend tickets have `Valid_On = NULL`, while Day tickets have `Valid_On` referencing `CHAMP_EVENT_DATE(Champ_ID, Event_Date)` to enforce valid single-day passes.
   - Point out `COMPETES_IN`: Show that `Checked_In = FALSE` strictly mandates `Check_In_At IS NULL` in compliance with the CHECK constraint.
3. **Data Authenticity**:
   - Emphasize to the TA that the dataset reflects real historical WBMC editions (Austin 2017, Antwerp 2019, Burghausen 2023) and actual real-world facial hair champions (Bryan Nelson, Jeff Langum, Aarne Bielefeldt, Jason Kiley).

---

## 4. Likely Viva Questions & Ready-to-Speak Answers

### Q1: Why did you choose MySQL / Relational for this project instead of MongoDB or Neo4j?
**Answer**: "Our Phase 3 conceptual design was relational. Choosing MySQL allowed us to map the relational tables, compound primary keys, and foreign key integrity rules directly without impedance mismatch. Additionally, MySQL natively enforces strict constraints (`CHECK`, `FOREIGN KEY ... ON DELETE RESTRICT`) that MongoDB would require us to manually manage in application logic."

### Q2: What was the primary challenge in designing `populate.sql`?
**Answer**: "Foreign key ordering and constraint satisfaction. Because foreign keys use `ON DELETE RESTRICT` and composite keys (like `(Champ_ID, Category_ID)` or `(Champ_ID, Valid_On)`), the population script must strictly follow topological dependencies. For instance, `OFFERS` must exist before `COMPETES_IN`, and `CHAMP_EVENT_DATE` must exist before any day `TICKET` is created."

### Q3: How did you ensure your data supports the video demonstration for updates and deletes?
**Answer**: "In our schema, child tables restrict deletions from parent tables. For our video demo, we seeded specific leaf rows—such as Ticket `(4, 999)` and Change Record `(2)`—which have valid foreign keys pointing to parents, but no dependent child rows. This allows the web UI to execute a clean `DELETE` query and prove it in the MySQL shell without causing constraint errors."

### Q4: Why are multivalued attributes like emails and aliases in separate tables?
**Answer**: "To satisfy First Normal Form (1NF). In 1NF, every attribute must contain only atomic (indivisible) values. A person or club can have multiple email addresses or nicknames, so storing them in normalized tables (`PERSON_EMAIL`, `PERSON_ALIAS`, `CLUB_ALIAS`) avoids comma-separated strings and enables indexing."

### Q5: How do your check constraints handle ticket validity?
**Answer**: "The `TICKET` table enforces:
`((Access = 'Day' AND Valid_On IS NOT NULL) OR (Access = 'Weekend' AND Valid_On IS NULL))`.
A day ticket must specify the exact championship date it is valid for, and that date is foreign-key verified against `CHAMP_EVENT_DATE`. A weekend pass grants access across all dates, so `Valid_On` remains NULL."

### Q6: How does the schema handle competitor check-in consistency?
**Answer**: "In `COMPETES_IN`, a CHECK constraint ensures:
`((Checked_In = FALSE AND Check_In_At IS NULL) OR (Checked_In = TRUE AND Check_In_At IS NOT NULL))`.
This guarantees that a competitor cannot have a timestamp without being checked in, nor be marked checked in without an official timestamp."

### Q7: If a competitor is deleted, what happens to their competition records?
**Answer**: "Because foreign keys are configured with `ON DELETE RESTRICT`, MySQL forbids deleting a competitor if they have associated records in `COMPETES_IN`, `MEMBER_OF`, or `TICKET`. This preserves the historical record of the championship."

### Q8: What is the difference between `COMPETITOR` and `COMPETITOR_AT_EDITION`?
**Answer**: "`COMPETITOR` represents the enduring person subclass who competes in WBMC events. `COMPETITOR_AT_EDITION` captures edition-specific details, such as the country or club they represented in a given championship year, as competitors may relocate or represent different national affiliates over time."

### Q9: Why did you avoid ORMs like SQLAlchemy or Django ORM?
**Answer**: "The assignment rubric strictly mandates 'Query Purity'—requiring raw, parameterized SQL queries with `%s` placeholders. Using an ORM or query builder is forbidden to ensure we demonstrate mastery of raw SQL execution, parameter passing, and query optimization."

### Q10: How do you prevent SQL injection when executing backend queries?
**Answer**: "We use parameterized queries provided by the Python driver (`PyMySQL`). User input is passed as a separate tuple to `cur.execute(query, params)`. The database driver safely escapes and treats input strictly as data values, preventing SQL injection."
