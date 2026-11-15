-- ==============================================================================
-- DATABASE POPULATION SCRIPT: World Beard and Moustache Championships (wbmc_db)
-- DBMS: MySQL / MariaDB
-- Assignment: Data and Applications (DnA) Phase 4 - Data Lead (Person 2)
-- 
-- DESCRIPTION:
-- Populates the wbmc_db database with authentic real-world data from the
-- World Beard and Moustache Championships (WBMC / WBMA).
-- 
-- INSERTION ORDER (Topological):
-- 1. Independent parent tables: PERSON, CLUB, VENUE, CATEGORY, CHARITY
-- 2. Multi-valued tables: PERSON_ALIAS, PERSON_EMAIL, CLUB_ALIAS, CLUB_WEB_LINK, CATEGORY_ALIAS
-- 3. CHAMPIONSHIP table
-- 4. Dependent on CHAMPIONSHIP: CHAMP_EVENT_DATE, CHAMP_ATTENDANCE_CLAIM, GROUP_COVERAGE, OFFERS, SUPPORTS
-- 5. Subclass tables & appointments: COMPETITOR, WBMA_OFFICER, OFFICER_APPOINTMENT, ORGANIZES
-- 6. Host bidding: HOST_BID, HOST_BID_REPRESENTATIVE
-- 7. Tickets & Competitor editions: TICKET, COMPETITOR_AT_EDITION
-- 8. Event participation: COMPETES_IN, MEMBER_OF, BEST_IN_SHOW, ENTRY_FOR_CLUB
-- 9. Administrative tracking: CHANGE_RECORD
-- ==============================================================================

USE wbmc_db;

-- ------------------------------------------------------------------------------
-- 1. INDEPENDENT PARENT ENTITIES
-- ------------------------------------------------------------------------------

-- PERSON
INSERT INTO PERSON (Person_ID, Given_Name, Family_Name, Nickname, Display_Name, Date_of_Birth, Hometown_City, Hometown_Region, Hometown_Country) VALUES
(1, 'Norbert', 'Topf', 'The President', 'Norbert Topf', '1958-04-12', 'Leogang', 'Salzburg', 'Austria'),
(2, 'Bryan', 'Nelson', 'B-Rex', 'Bryan Nelson', '1981-09-24', 'Austin', 'Texas', 'USA'),
(3, 'Jørgen', 'Bech-Pedersen', 'The Dane', 'Jørgen Bech-Pedersen', '1962-11-03', 'Copenhagen', 'Hovedstaden', 'Denmark'),
(4, 'Jeff', 'Langum', 'Big Red', 'Jeff Langum', '1976-03-15', 'Philadelphia', 'Pennsylvania', 'USA'),
(5, 'MJ', 'Johnson', 'Razor Free', 'MJ Johnson', '1984-07-29', 'Minneapolis', 'Minnesota', 'USA'),
(6, 'Aarne', 'Bielefeldt', 'The Wizard', 'Aarne Bielefeldt', '1965-06-18', 'Willits', 'California', 'USA'),
(7, 'Patrick', 'Fette', 'The Aristocrat', 'Patrick Fette', '1979-12-05', 'Louisville', 'Kentucky', 'USA'),
(8, 'Jason', 'Kiley', 'The Sculptor', 'Jason Kiley', '1983-02-14', 'Oneonta', 'New York', 'USA'),
(9, 'Michael', 'Wollin', 'Der Bartmeister', 'Michael Wollin', '1968-08-30', 'Höfen', 'Bavaria', 'Germany'),
(10, 'Jackie', 'Ellison', 'Texas Jack', 'Jackie Lynn Ellison', '1975-01-22', 'Houston', 'Texas', 'USA'),
(11, 'Wolfgang', 'Schneider', 'Kaiser', 'Wolfgang Schneider', '1955-10-10', 'Offenbach', 'Hesse', 'Germany'),
(12, 'Dan', 'Lawlor', 'Iron City Beard', 'Dan Lawlor', '1986-05-19', 'Pittsburgh', 'Pennsylvania', 'USA'),
(13, 'Patrick', 'Dawson', 'Gentleman Pat', 'Patrick Dawson', '1978-03-08', 'London', 'Greater London', 'United Kingdom'),
(14, 'Elena', 'Rostova', 'Whiskerina Queen', 'Elena Rostova', '1990-07-11', 'Austin', 'Texas', 'USA'),
(15, 'Sarah', 'Davies', 'Craft Maker', 'Sarah Davies', '1992-11-25', 'London', 'Greater London', 'United Kingdom'),
-- Demo people for query & update testing:
(16, 'Lucas', 'Vance', 'Iron Beard', 'Lucas Vance', '1991-04-18', 'Columbus', 'Ohio', 'USA'),
(17, 'Oliver', 'Queen', 'The Archer', 'Oliver Queen', '1988-06-20', 'Star City', 'Washington', 'USA'),
(18, 'Samir', 'Patel', 'The Windy Whiskers', 'Samir Patel', '1989-09-09', 'Chicago', 'Illinois', 'USA');

-- CLUB
INSERT INTO CLUB (Club_ID, Name, Country, Membership_Status, Membership_As_Of) VALUES
(1, 'The Austin Facial Hair Club', 'USA', 'Member', '2015-01-01'),
(2, 'Snorrenclub Antwerpen', 'Belgium', 'Member', '2010-05-12'),
(3, 'Ostbayerischer Bart- und Schnurrbartverein', 'Germany', 'Member', '2012-08-20'),
(4, 'Three Rivers Beard & Moustache Club', 'USA', 'Member', '2020-03-15'),
(5, 'The British Beard Club', 'United Kingdom', 'Member', '2008-02-14'),
(6, 'Beard Team USA', 'USA', 'Member', '2005-06-01'),
(7, 'Club der Bartträger Höfen', 'Germany', 'Member', '2003-01-01'),
(8, 'World Whiskerinas Association', 'USA', 'Not_member', '2018-09-01');

-- VENUE
INSERT INTO VENUE (Venue_ID, Name, Street, City, Region, Postal_Code, Country) VALUES
(1, 'The Long Center for the Performing Arts', '701 W Riverside Dr', 'Austin', 'Texas', '78704', 'USA'),
(2, 'Elisabeth Center Antwerp', 'Koningin Astridplein 26', 'Antwerp', 'Antwerp', '2018', 'Belgium'),
(3, 'Stadtsaal Burghausen', 'Kapuzinergasse 235', 'Burghausen', 'Bavaria', '84489', 'Germany'),
(4, 'David L. Lawrence Convention Center', '1000 Ft. Duquesne Blvd', 'Pittsburgh', 'Pennsylvania', '15222', 'USA'),
(5, 'Auckland Town Hall', 'Queen Street', 'Auckland', 'Auckland', '1010', 'New Zealand');

-- CATEGORY
INSERT INTO CATEGORY (Category_ID, Name) VALUES
(1, 'Natural Moustache'),
(2, 'English Moustache'),
(3, 'Dali Moustache'),
(4, 'Imperial Moustache'),
(5, 'Hungarian Moustache'),
(6, 'Freestyle Moustache'),
(7, 'Natural Goatee'),
(8, 'Musketeer'),
(9, 'Fu Manchu'),
(10, 'Imperial Partial Beard'),
(11, 'Freestyle Partial Beard'),
(12, 'Verdi'),
(13, 'Garibaldi'),
(14, 'Full Beard Natural'),
(15, 'Full Beard with Styled Moustache'),
(16, 'Full Beard Freestyle'),
(17, 'Craft Beard Realistic'),
(18, 'Craft Beard Creative');

-- CHARITY
INSERT INTO CHARITY (Charity_ID, Name, Website) VALUES
(1, 'Livestrong Foundation', 'https://www.livestrong.org'),
(2, 'Burghausen Children Foundation', 'https://www.burghausen-kinderhilfe.de'),
(3, 'Greater Pittsburgh Community Food Bank', 'https://www.pittsburghfoodbank.org'),
(4, 'Antwerp Youth Care Fund', 'https://www.jeugdzorgantwerpen.be');

-- ------------------------------------------------------------------------------
-- 2. MULTI-VALUED ATTRIBUTES FOR INDEPENDENT ENTITIES
-- ------------------------------------------------------------------------------

-- PERSON_ALIAS
INSERT INTO PERSON_ALIAS (Person_ID, Alias) VALUES
(4, 'The Philadelphian Beard'),
(5, 'The Stache Master'),
(6, 'The Redwood Sculptor'),
(8, 'The Beard Aristocrat');

-- PERSON_EMAIL
INSERT INTO PERSON_EMAIL (Person_ID, Email) VALUES
(1, 'president@worldbeardchampionships.com'),
(2, 'bryan@austinfacialhairclub.com'),
(3, 'jorgen@danishbeard.dk'),
(4, 'jeff.langum@gmail.com'),
(5, 'mj.johnson@freestyle-stache.com'),
(6, 'aarne.bielefeldt@mendocino.com'),
(7, 'patrick.fette@whiskermail.com'),
(8, 'jason.kiley@gmail.com'),
(9, 'michael.wollin@bartclub-hoefen.de'),
(10, 'jackie.ellison@texasbeards.org'),
(12, 'dan@threeriversbeard.com'),
(16, 'lucas.vance@testmail.com'),
(17, 'oliver.queen@testmail.com'),
(18, 'samir.patel@testmail.com');

-- CLUB_ALIAS
INSERT INTO CLUB_ALIAS (Club_ID, Alias) VALUES
(1, 'AFHC'),
(2, 'SNA'),
(3, 'OBSV Burghausen'),
(4, '3B'),
(5, 'BBC UK'),
(6, 'BTUSA');

-- CLUB_WEB_LINK
INSERT INTO CLUB_WEB_LINK (Club_ID, Web_Link) VALUES
(1, 'https://austinfacialhairclub.com'),
(2, 'https://snorrenclub.be'),
(3, 'https://bartclub-burghausen.de'),
(4, 'https://threeriversbeard.com'),
(5, 'https://thebritishbeardclub.org'),
(6, 'https://beardteamusa.org');

-- CATEGORY_ALIAS
INSERT INTO CATEGORY_ALIAS (Category_ID, Alias) VALUES
(6, 'Freestyle Stache'),
(12, 'Full Beard Verdi'),
(13, 'Full Beard Garibaldi'),
(14, 'Natural Full Beard'),
(16, 'Open Freestyle Beard');

-- ------------------------------------------------------------------------------
-- 3. CHAMPIONSHIP EDITIONS
-- ------------------------------------------------------------------------------

INSERT INTO CHAMPIONSHIP (Champ_ID, Year, Host_City, Host_Region, Host_Country, Status, Registration_Opens, Registration_Closes, Max_Categories_Per_Competitor, Host_Club_ID, Venue_ID, Replaces_Champ_ID) VALUES
(1, 2017, 'Austin', 'Texas', 'USA', 'Completed', '2017-01-01 00:00:00', '2017-08-01 23:59:59', 2, 1, 1, NULL),
(2, 2019, 'Antwerp', 'Antwerp', 'Belgium', 'Completed', '2018-10-01 00:00:00', '2019-04-15 23:59:59', 2, 2, 2, NULL),
(3, 2023, 'Burghausen', 'Bavaria', 'Germany', 'Completed', '2022-11-01 00:00:00', '2023-05-01 23:59:59', 2, 3, 3, NULL),
(4, 2025, 'Pittsburgh', 'Pennsylvania', 'USA', 'Upcoming', '2024-10-01 00:00:00', '2025-06-01 23:59:59', 2, 4, 4, NULL);

-- ------------------------------------------------------------------------------
-- 4. DEPENDENT ENTITIES ON CHAMPIONSHIP
-- ------------------------------------------------------------------------------

-- CHAMP_EVENT_DATE
INSERT INTO CHAMP_EVENT_DATE (Champ_ID, Event_Date) VALUES
(1, '2017-09-01'),
(1, '2017-09-02'),
(1, '2017-09-03'),
(2, '2019-05-17'),
(2, '2019-05-18'),
(2, '2019-05-19'),
(3, '2023-06-09'),
(3, '2023-06-10'),
(3, '2023-06-11'),
(4, '2025-07-04'),
(4, '2025-07-05'),
(4, '2025-07-06');

-- CHAMP_ATTENDANCE_CLAIM
INSERT INTO CHAMP_ATTENDANCE_CLAIM (Champ_ID, Source, Reported_Count) VALUES
(1, 'Austin Chronicle Official Festival Report', 730),
(1, 'Austin Facial Hair Club Gate Registration', 705),
(2, 'Gazet van Antwerpen Event Audit', 850),
(2, 'Snorrenclub Antwerpen Ticket Tally', 820),
(3, 'Burghausen Tourism & Culture Bureau', 620),
(4, 'VisitPittsburgh Tourism Authority Projection', 900);

-- GROUP_COVERAGE
INSERT INTO GROUP_COVERAGE (Champ_ID, Category_Group, Results_Coverage) VALUES
(1, 'Moustache', 'Full'),
(1, 'Partial Beard', 'Full'),
(1, 'Full Beard', 'Full'),
(1, 'Craft', 'Top_3_only'),
(2, 'Moustache', 'Full'),
(2, 'Partial Beard', 'Full'),
(2, 'Full Beard', 'Full'),
(2, 'Craft', 'Top_3_only'),
(3, 'Moustache', 'Full'),
(3, 'Partial Beard', 'Full'),
(3, 'Full Beard', 'Full'),
(3, 'Craft', 'Top_3_only'),
(4, 'Moustache', 'Full'),
(4, 'Partial Beard', 'Full'),
(4, 'Full Beard', 'Full'),
(4, 'Craft', 'Top_3_only');

-- OFFERS
INSERT INTO OFFERS (Champ_ID, Category_ID, Display_Name, Category_Group, Min_Length_cm, Max_Length_cm, Min_Age, Max_Age, Styling_Aids, Rule_Text, Rules_Verified) VALUES
(1, 2, 'English Moustache', 'Moustache', NULL, NULL, 18, NULL, 'Allowed', 'Slender moustache parted in middle, ends pointed and held rigid with styling aids.', 'Yes'),
(1, 6, 'Freestyle Moustache', 'Moustache', NULL, NULL, 18, NULL, 'Allowed', 'All styling aids allowed, shape may be free-form.', 'Yes'),
(1, 12, 'Verdi', 'Full Beard', NULL, 10.00, 18, NULL, 'Moustache_only', 'Round full beard not exceeding 10 cm length, styled moustache allowed.', 'Yes'),
(1, 13, 'Garibaldi', 'Full Beard', NULL, 20.00, 18, NULL, 'None', 'Broad, rounded full beard up to 20 cm length, natural growth without styling aids.', 'Yes'),
(1, 14, 'Full Beard Natural', 'Full Beard', NULL, NULL, 18, NULL, 'None', 'Full natural beard as it grows. Absolutely no styling aids allowed.', 'Yes'),
(1, 15, 'Full Beard with Styled Moustache', 'Full Beard', NULL, NULL, 18, NULL, 'Moustache_only', 'Natural full beard with styling aids permitted only on the moustache.', 'Yes'),
(1, 16, 'Full Beard Freestyle', 'Full Beard', NULL, NULL, 18, NULL, 'Allowed', 'Creative facial sculpture, all styling aids permitted.', 'Yes'),
(1, 17, 'Craft Beard Realistic', 'Craft', NULL, NULL, NULL, NULL, 'Allowed', 'Hand-crafted realistic beard worn by competitors of any gender.', 'Yes'),
(2, 6, 'Freestyle Moustache', 'Moustache', NULL, NULL, 18, NULL, 'Allowed', 'Freestyle moustache with full styling aid allowance.', 'Yes'),
(2, 14, 'Full Beard Natural', 'Full Beard', NULL, NULL, 18, NULL, 'None', 'Natural full beard, no styling aids allowed.', 'Yes'),
(2, 15, 'Full Beard with Styled Moustache', 'Full Beard', NULL, NULL, 18, NULL, 'Moustache_only', 'Natural beard with styled moustache.', 'Yes'),
(2, 16, 'Full Beard Freestyle', 'Full Beard', NULL, NULL, 18, NULL, 'Allowed', 'Full freestyle artistic beard.', 'Yes'),
(3, 14, 'Full Beard Natural', 'Full Beard', NULL, NULL, 18, NULL, 'None', 'Natural full beard.', 'Yes'),
(3, 16, 'Full Beard Freestyle', 'Full Beard', NULL, NULL, 18, NULL, 'Allowed', 'Freestyle beard creation.', 'Yes'),
(4, 2, 'English Moustache', 'Moustache', NULL, NULL, 18, NULL, 'Allowed', 'English moustache category for 2025 championship.', 'Yes'),
(4, 6, 'Freestyle Moustache', 'Moustache', NULL, NULL, 18, NULL, 'Allowed', 'Freestyle moustache category for 2025 championship.', 'Yes'),
(4, 14, 'Full Beard Natural', 'Full Beard', NULL, NULL, 18, NULL, 'None', 'Full Natural Beard category for 2025 championship.', 'Yes'),
(4, 16, 'Full Beard Freestyle', 'Full Beard', NULL, NULL, 18, NULL, 'Allowed', 'Full Beard Freestyle category for 2025 championship.', 'Yes');

-- SUPPORTS
INSERT INTO SUPPORTS (Champ_ID, Charity_ID) VALUES
(1, 1),
(2, 4),
(3, 2),
(4, 3);

-- ------------------------------------------------------------------------------
-- 5. SUBCLASSES AND APPOINTMENTS
-- ------------------------------------------------------------------------------

-- COMPETITOR
INSERT INTO COMPETITOR (Person_ID) VALUES
(4), (5), (6), (7), (8), (9), (10), (11), (14), (15), (16);

-- WBMA_OFFICER
INSERT INTO WBMA_OFFICER (Person_ID) VALUES
(1), (2), (3);

-- OFFICER_APPOINTMENT
INSERT INTO OFFICER_APPOINTMENT (Appointment_ID, Position, Term_Start_Year, Term_End_Year, Person_ID, Club_ID) VALUES
(1, 'President', 2013, 2024, 1, NULL),
(2, 'Vice_President', 2015, NULL, 3, NULL),
(3, 'Host_Club_Vice_President', 2016, 2018, 2, 1);

-- ORGANIZES
INSERT INTO ORGANIZES (Person_ID, Champ_ID, Role) VALUES
(2, 1, 'Organizer'),
(1, 1, 'Category_Check_Team'),
(3, 2, 'Organizer'),
(9, 3, 'Organizer'),
(12, 4, 'Organizer'),
(2, 4, 'Category_Check_Team');

-- ------------------------------------------------------------------------------
-- 6. HOST BIDDING
-- ------------------------------------------------------------------------------

-- HOST_BID
INSERT INTO HOST_BID (Champ_ID, Bid_No, Proposed_City, Proposed_Region, Proposed_Country, Votes, `Rank`, Status, Eligibility, Club_ID) VALUES
(1, 1, 'Austin', 'Texas', 'USA', 42, 1, 'Won', 'Eligible', 1),
(2, 1, 'Antwerp', 'Antwerp', 'Belgium', 38, 1, 'Won', 'Eligible', 2),
(3, 1, 'Burghausen', 'Bavaria', 'Germany', 35, 1, 'Won', 'Eligible', 3),
(4, 1, 'Pittsburgh', 'Pennsylvania', 'USA', 45, 1, 'Won', 'Eligible', 4),
(4, 2, 'Auckland', 'Auckland', 'New Zealand', 28, 2, 'Lost', 'Eligible', 6);

-- HOST_BID_REPRESENTATIVE
INSERT INTO HOST_BID_REPRESENTATIVE (Champ_ID, Bid_No, Person_ID) VALUES
(1, 1, 2),
(2, 1, 3),
(3, 1, 9),
(4, 1, 12),
(4, 2, 18);

-- ------------------------------------------------------------------------------
-- 7. TICKETS AND COMPETITOR EDITIONS
-- ------------------------------------------------------------------------------

-- TICKET
INSERT INTO TICKET (Champ_ID, Ticket_No, Type, Access, Price, Currency, Status, Valid_On, Holder_ID) VALUES
(1, 101, 'Competitor', 'Weekend', 65.00, 'USD', 'Used', NULL, 4),
(1, 102, 'Competitor', 'Weekend', 65.00, 'USD', 'Used', NULL, 5),
(1, 103, 'Competitor', 'Weekend', 65.00, 'USD', 'Used', NULL, 6),
(1, 104, 'Competitor', 'Weekend', 65.00, 'USD', 'Used', NULL, 7),
(1, 105, 'Competitor', 'Weekend', 65.00, 'USD', 'Used', NULL, 8),
(1, 201, 'Spectator', 'Day', 25.00, 'USD', 'Used', '2017-09-02', 17),
(2, 201, 'Competitor', 'Weekend', 60.00, 'EUR', 'Used', NULL, 4),
(2, 202, 'Competitor', 'Weekend', 60.00, 'EUR', 'Used', NULL, 6),
(3, 301, 'Competitor', 'Weekend', 60.00, 'EUR', 'Used', NULL, 9),
(4, 401, 'Competitor', 'Weekend', 75.00, 'USD', 'Valid', NULL, 16),
-- Demo Ticket specifically designated for DELETE / Cancel test in Web UI:
(4, 999, 'Spectator', 'Day', 30.00, 'USD', 'Valid', '2025-07-05', 17);

-- COMPETITOR_AT_EDITION
INSERT INTO COMPETITOR_AT_EDITION (Person_ID, Champ_ID, Represented_Country, Event_Hometown_City, Event_Hometown_Region, Event_Hometown_Country) VALUES
(4, 1, 'USA', 'Philadelphia', 'Pennsylvania', 'USA'),
(5, 1, 'USA', 'Minneapolis', 'Minnesota', 'USA'),
(6, 1, 'USA', 'Willits', 'California', 'USA'),
(7, 1, 'USA', 'Louisville', 'Kentucky', 'USA'),
(8, 1, 'USA', 'Oneonta', 'New York', 'USA'),
(4, 2, 'USA', 'Philadelphia', 'Pennsylvania', 'USA'),
(6, 2, 'USA', 'Willits', 'California', 'USA'),
(8, 2, 'USA', 'Oneonta', 'New York', 'USA'),
(9, 3, 'Germany', 'Höfen', 'Bavaria', 'Germany'),
(6, 3, 'USA', 'Willits', 'California', 'USA'),
(16, 4, 'USA', 'Columbus', 'Ohio', 'USA');

-- ------------------------------------------------------------------------------
-- 8. EVENT PARTICIPATION AND RESULTS
-- ------------------------------------------------------------------------------

-- COMPETES_IN
INSERT INTO COMPETES_IN (Person_ID, Category_ID, Champ_ID, Competitor_No, Score, Placement, Beard_Length_cm, Checked_In, Check_In_At, Entry_Status) VALUES
-- Austin 2017:
(4, 14, 1, 101, 48.50, 2, 38.00, TRUE, '2017-09-01 09:30:00', 'Result_recorded'),
(6, 16, 1, 102, 49.50, 1, 42.00, TRUE, '2017-09-01 09:45:00', 'Result_recorded'),
(5, 6, 1, 103, 49.00, 1, 12.00, TRUE, '2017-09-01 10:00:00', 'Result_recorded'),
(7, 2, 1, 104, 48.00, 1, 15.00, TRUE, '2017-09-01 10:15:00', 'Result_recorded'),
(8, 15, 1, 105, 50.00, 1, 35.00, TRUE, '2017-09-01 10:30:00', 'Result_recorded'),

-- Antwerp 2019:
(4, 14, 2, 201, 49.00, 1, 40.00, TRUE, '2019-05-17 09:00:00', 'Result_recorded'),
(6, 16, 2, 202, 48.00, 2, 44.00, TRUE, '2019-05-17 09:15:00', 'Result_recorded'),
(8, 14, 2, 203, 47.50, 3, 36.00, TRUE, '2019-05-17 09:30:00', 'Result_recorded'),

-- Burghausen 2023:
(9, 14, 3, 301, 48.50, 1, 35.00, TRUE, '2023-06-09 10:00:00', 'Result_recorded'),
(6, 16, 3, 302, 49.00, 1, 46.00, TRUE, '2023-06-09 10:15:00', 'Result_recorded'),

-- Pittsburgh 2025 (Demo Competitor: Registered, ready for UPDATE Check-in test in UI demo):
(16, 14, 4, 401, NULL, NULL, 30.00, FALSE, NULL, 'Registered');

-- MEMBER_OF
INSERT INTO MEMBER_OF (Person_ID, Club_ID) VALUES
(4, 6),
(5, 6),
(6, 6),
(7, 6),
(8, 6),
(9, 7),
(16, 4);

-- BEST_IN_SHOW
INSERT INTO BEST_IN_SHOW (Champ_ID, Person_ID, Division) VALUES
(1, 8, 'Full Beard'),
(2, 4, 'Full Beard'),
(3, 6, 'Full Beard');

-- ENTRY_FOR_CLUB
INSERT INTO ENTRY_FOR_CLUB (Person_ID, Category_ID, Champ_ID, Club_ID) VALUES
(4, 14, 1, 6),
(6, 16, 1, 6),
(5, 6, 1, 6),
(7, 2, 1, 6),
(8, 15, 1, 6),
(4, 14, 2, 6),
(6, 16, 2, 6),
(8, 14, 2, 6),
(9, 14, 3, 7),
(6, 16, 3, 6),
(16, 14, 4, 4);

-- ------------------------------------------------------------------------------
-- 9. ADMINISTRATIVE CHANGE RECORDS
-- ------------------------------------------------------------------------------

-- CHANGE_RECORD
INSERT INTO CHANGE_RECORD (Change_ID, Field_Name, Old_Value, New_Value, Reason, Requested_At, Decided_At, Status, Entry_Person_ID, Entry_Category_ID, Entry_Champ_ID, Requested_By, Approved_By) VALUES
(1, 'Display_Name', 'Bryan Nelson', 'Bryan C. Nelson', 'Official middle initial correction for award certificates', '2017-08-15 14:00:00', '2017-08-16 10:00:00', 'Approved', 4, 14, 1, 4, 1),
-- Demo record for pending status / approval / delete testing:
(2, 'Beard_Length_cm', '28.00', '30.00', 'Measurement update requested by competitor before check-in', '2025-05-01 11:30:00', NULL, 'Pending', 16, 14, 4, 16, NULL);
