DROP DATABASE IF EXISTS wbmc_db;

CREATE DATABASE wbmc_db;

USE wbmc_db;

-- INDEPENDENT ENTITY TABLES:

CREATE TABLE PERSON (
    Person_ID INT AUTO_INCREMENT PRIMARY KEY,
    Given_Name VARCHAR(100),
    Family_Name VARCHAR(100),
    Nickname VARCHAR(100),
    Display_Name VARCHAR(200) NOT NULL,
    Date_of_Birth DATE,

    Hometown_City VARCHAR(100),
    Hometown_Region VARCHAR(100),
    Hometown_Country VARCHAR(100)
  
);

CREATE TABLE CLUB (
    Club_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(200) NOT NULL,
    Country VARCHAR(100),

    Membership_Status ENUM(
        'Member',
        'Not_member',
        'Unknown'
    ) DEFAULT 'Unknown',

    Membership_As_Of DATE
);

CREATE TABLE VENUE (
    Venue_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(200) NOT NULL,
    Street VARCHAR(200),
    City VARCHAR(100),
    Region VARCHAR(100),
    Postal_Code VARCHAR(30),
    Country VARCHAR(100)
);

CREATE TABLE CATEGORY (
    Category_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(200) NOT NULL
);


CREATE TABLE CHARITY (
    Charity_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(200) NOT NULL,
    Website VARCHAR(500)
);

-- CHAMPIONSHIP

CREATE TABLE CHAMPIONSHIP (
    Champ_ID INT AUTO_INCREMENT PRIMARY KEY,

    Year INT NOT NULL UNIQUE,

    Host_City VARCHAR(100),
    Host_Region VARCHAR(100),
    Host_Country VARCHAR(100),

    Status ENUM(
        'Upcoming',
        'In_progress',
        'Completed',
        'Cancelled'
    ) NOT NULL,

    Registration_Opens DATETIME,
    Registration_Closes DATETIME,

    Max_Categories_Per_Competitor INT,

    Host_Club_ID INT,
    Venue_ID INT,

    Replaces_Champ_ID INT UNIQUE,

    FOREIGN KEY (Host_Club_ID)
        REFERENCES CLUB(Club_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (Venue_ID)
        REFERENCES VENUE(Venue_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (Replaces_Champ_ID)
        REFERENCES CHAMPIONSHIP(Champ_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CHECK (Year >= 1990),

    CHECK (
        Registration_Closes IS NULL
        OR Registration_Opens IS NULL
        OR Registration_Closes >= Registration_Opens
    ),

    CHECK (
        Max_Categories_Per_Competitor IS NULL
        OR Max_Categories_Per_Competitor > 0
    )
);

-- MULTIVALUED ATTRIBUTES

CREATE TABLE PERSON_ALIAS (
    Person_ID INT NOT NULL,
    Alias VARCHAR(200) NOT NULL,

    PRIMARY KEY (Person_ID, Alias),

    FOREIGN KEY (Person_ID)
        REFERENCES PERSON(Person_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE PERSON_EMAIL (
    Person_ID INT NOT NULL,
    Email VARCHAR(255) NOT NULL,

    PRIMARY KEY (Person_ID, Email),

    FOREIGN KEY (Person_ID)
        REFERENCES PERSON(Person_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE CLUB_ALIAS (
    Club_ID INT NOT NULL,
    Alias VARCHAR(200) NOT NULL,

    PRIMARY KEY (Club_ID, Alias),

    FOREIGN KEY (Club_ID)
        REFERENCES CLUB(Club_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE CLUB_WEB_LINK (
    Club_ID INT NOT NULL,
    Web_Link VARCHAR(500) NOT NULL,

    PRIMARY KEY (Club_ID, Web_Link),

    FOREIGN KEY (Club_ID)
        REFERENCES CLUB(Club_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE CATEGORY_ALIAS (
    Category_ID INT NOT NULL,
    Alias VARCHAR(200) NOT NULL,

    PRIMARY KEY (Category_ID, Alias),

    FOREIGN KEY (Category_ID)
        REFERENCES CATEGORY(Category_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE CHAMP_EVENT_DATE (
    Champ_ID INT NOT NULL,
    Event_Date DATE NOT NULL,

    PRIMARY KEY (Champ_ID, Event_Date),

    FOREIGN KEY (Champ_ID)
        REFERENCES CHAMPIONSHIP(Champ_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);


CREATE TABLE CHAMP_ATTENDANCE_CLAIM (
    Champ_ID INT NOT NULL,
    Source VARCHAR(200) NOT NULL,
    Reported_Count INT NOT NULL,

    PRIMARY KEY (Champ_ID, Source, Reported_Count),

    FOREIGN KEY (Champ_ID)
        REFERENCES CHAMPIONSHIP(Champ_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CHECK (Reported_Count >= 0)
);

-- SUBCLASSES

CREATE TABLE COMPETITOR (
    Person_ID INT PRIMARY KEY,

    FOREIGN KEY (Person_ID)
        REFERENCES PERSON(Person_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE WBMA_OFFICER (
    Person_ID INT PRIMARY KEY,

    FOREIGN KEY (Person_ID)
        REFERENCES PERSON(Person_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE OFFICER_APPOINTMENT (
    Appointment_ID INT AUTO_INCREMENT PRIMARY KEY,

    Position ENUM(
        'President',
        'Vice_President',
        'Host_Club_Vice_President'
    ) NOT NULL,

    Term_Start_Year INT NOT NULL,
    Term_End_Year INT,

    Person_ID INT NOT NULL,
    Club_ID INT,

    FOREIGN KEY (Person_ID)
        REFERENCES WBMA_OFFICER(Person_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (Club_ID)
        REFERENCES CLUB(Club_ID)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT,

    CHECK (Term_Start_Year >= 2004),

    CHECK (
        Term_End_Year IS NULL
        OR Term_End_Year >= Term_Start_Year
    ),

    CHECK (
        Position <> 'Host_Club_Vice_President'
        OR Club_ID IS NOT NULL
    )
);


CREATE TABLE TICKET (
    Champ_ID INT NOT NULL,
    Ticket_No INT NOT NULL,

    Type ENUM(
        'Competitor',
        'Spectator',
        'Kids_competitor',
        'Kids_spectator'
    ) NOT NULL,

    Access ENUM(
        'Day',
        'Weekend'
    ) NOT NULL,

    Price DECIMAL(10,2) NOT NULL,
    Currency CHAR(3) NOT NULL,

    Status ENUM(
        'Valid',
        'Used',
        'Void',
        'Refund_pending',
        'Refunded'
    ) NOT NULL,

    Valid_On DATE,
    Holder_ID INT NOT NULL,

    PRIMARY KEY (Champ_ID, Ticket_No),

    FOREIGN KEY (Champ_ID)
        REFERENCES CHAMPIONSHIP(Champ_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (Holder_ID)
        REFERENCES PERSON(Person_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (Champ_ID, Valid_On)
        REFERENCES CHAMP_EVENT_DATE(Champ_ID, Event_Date)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT,

    CHECK (Ticket_No > 0),
    CHECK (Price >= 0),

    CHECK (
        (Access = 'Day' AND Valid_On IS NOT NULL)
        OR
        (Access = 'Weekend' AND Valid_On IS NULL)
    )
);

CREATE TABLE HOST_BID (
    Champ_ID INT NOT NULL,
    Bid_No INT NOT NULL,

    Proposed_City VARCHAR(100) NOT NULL,
    Proposed_Region VARCHAR(100),
    Proposed_Country VARCHAR(100) NOT NULL,

    Votes INT,
    `Rank` INT,

    Status ENUM(
        'Submitted',
        'Won',
        'Lost',
        'Withdrawn',
        'Awarded_as_runner_up'
    ) NOT NULL,

    Eligibility ENUM(
        'Pending',
        'Eligible',
        'Ineligible'
    ) NOT NULL DEFAULT 'Pending',

    Club_ID INT NOT NULL,

    PRIMARY KEY (Champ_ID, Bid_No),

    FOREIGN KEY (Champ_ID)
        REFERENCES CHAMPIONSHIP(Champ_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (Club_ID)
        REFERENCES CLUB(Club_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CHECK (Bid_No > 0),
    CHECK (Votes IS NULL OR Votes >= 0),
    CHECK (`Rank` IS NULL OR `Rank` > 0)
);

CREATE TABLE HOST_BID_REPRESENTATIVE (
    Champ_ID INT NOT NULL,
    Bid_No INT NOT NULL,
    Person_ID INT NOT NULL,

    PRIMARY KEY (Champ_ID, Bid_No, Person_ID),

    FOREIGN KEY (Champ_ID, Bid_No)
        REFERENCES HOST_BID(Champ_ID, Bid_No)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (Person_ID)
        REFERENCES PERSON(Person_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE GROUP_COVERAGE (
    Champ_ID INT NOT NULL,
    Category_Group VARCHAR(150) NOT NULL,

    Results_Coverage ENUM(
        'None',
        'Top_3_only',
        'Full'
    ) NOT NULL,

    PRIMARY KEY (Champ_ID, Category_Group),

    FOREIGN KEY (Champ_ID)
        REFERENCES CHAMPIONSHIP(Champ_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE OFFERS (
    Champ_ID INT NOT NULL,
    Category_ID INT NOT NULL,

    Display_Name VARCHAR(200) NOT NULL,
    Category_Group VARCHAR(150) NOT NULL,

    Min_Length_cm DECIMAL(7,2),
    Max_Length_cm DECIMAL(7,2),

    Min_Age INT,
    Max_Age INT,

    Styling_Aids ENUM(
        'None',
        'Moustache_only',
        'Allowed'
    ),

    Rule_Text TEXT,

    Rules_Verified ENUM(
        'Yes',
        'No'
    ) NOT NULL DEFAULT 'No',

    PRIMARY KEY (Champ_ID, Category_ID),

    FOREIGN KEY (Champ_ID)
        REFERENCES CHAMPIONSHIP(Champ_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (Category_ID)
        REFERENCES CATEGORY(Category_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (Champ_ID, Category_Group)
        REFERENCES GROUP_COVERAGE(Champ_ID, Category_Group)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CHECK (
        Min_Length_cm IS NULL
        OR Min_Length_cm >= 0
    ),

    CHECK (
        Max_Length_cm IS NULL
        OR Max_Length_cm >= 0
    ),

    CHECK (
        Min_Length_cm IS NULL
        OR Max_Length_cm IS NULL
        OR Min_Length_cm <= Max_Length_cm
    ),

    CHECK (Min_Age IS NULL OR Min_Age >= 0),
    CHECK (Max_Age IS NULL OR Max_Age >= 0),

    CHECK (
        Min_Age IS NULL
        OR Max_Age IS NULL
        OR Min_Age <= Max_Age
    )
);

CREATE TABLE COMPETITOR_AT_EDITION (
    Person_ID INT NOT NULL,
    Champ_ID INT NOT NULL,

    Represented_Country VARCHAR(100),

    Event_Hometown_City VARCHAR(100),
    Event_Hometown_Region VARCHAR(100),
    Event_Hometown_Country VARCHAR(100),

    PRIMARY KEY (Person_ID, Champ_ID),

    FOREIGN KEY (Person_ID)
        REFERENCES COMPETITOR(Person_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (Champ_ID)
        REFERENCES CHAMPIONSHIP(Champ_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE COMPETES_IN (
    Person_ID INT NOT NULL,
    Category_ID INT NOT NULL,
    Champ_ID INT NOT NULL,

    Competitor_No INT,

    Score DECIMAL(7,2),
    Placement INT,

    Beard_Length_cm DECIMAL(7,2),

    Checked_In BOOLEAN NOT NULL DEFAULT FALSE,
    Check_In_At DATETIME,

    Entry_Status ENUM(
        'Registered',
        'Checked_in',
        'Withdrawn',
        'Disqualified',
        'Result_recorded',
        'Event_cancelled'
    ) NOT NULL DEFAULT 'Registered',

    PRIMARY KEY (
        Person_ID,
        Category_ID,
        Champ_ID
    ),

    FOREIGN KEY (Person_ID)
        REFERENCES COMPETITOR(Person_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (Category_ID)
        REFERENCES CATEGORY(Category_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (Champ_ID)
        REFERENCES CHAMPIONSHIP(Champ_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (Champ_ID, Category_ID)
        REFERENCES OFFERS(Champ_ID, Category_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (Person_ID, Champ_ID)
        REFERENCES COMPETITOR_AT_EDITION(Person_ID, Champ_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    UNIQUE (Champ_ID, Competitor_No),

    CHECK (Competitor_No IS NULL OR Competitor_No > 0),
    CHECK (Score IS NULL OR Score >= 0),
    CHECK (Placement IS NULL OR Placement >= 1),
    CHECK (Beard_Length_cm IS NULL OR Beard_Length_cm >= 0),

    CHECK (
        (Checked_In = FALSE AND Check_In_At IS NULL)
        OR
        (Checked_In = TRUE AND Check_In_At IS NOT NULL)
    )
);

CREATE TABLE MEMBER_OF (
    Person_ID INT NOT NULL,
    Club_ID INT NOT NULL,

    PRIMARY KEY (Person_ID, Club_ID),

    FOREIGN KEY (Person_ID)
        REFERENCES COMPETITOR(Person_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (Club_ID)
        REFERENCES CLUB(Club_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);


CREATE TABLE BEST_IN_SHOW (
    Champ_ID INT NOT NULL,
    Person_ID INT NOT NULL,
    Division VARCHAR(100) NOT NULL,

    PRIMARY KEY (Champ_ID, Person_ID),

    FOREIGN KEY (Champ_ID)
        REFERENCES CHAMPIONSHIP(Champ_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (Person_ID)
        REFERENCES COMPETITOR(Person_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);


CREATE TABLE SUPPORTS (
    Champ_ID INT NOT NULL,
    Charity_ID INT NOT NULL,

    PRIMARY KEY (Champ_ID, Charity_ID),

    FOREIGN KEY (Champ_ID)
        REFERENCES CHAMPIONSHIP(Champ_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (Charity_ID)
        REFERENCES CHARITY(Charity_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE ORGANIZES (
    Person_ID INT NOT NULL,
    Champ_ID INT NOT NULL,

    Role ENUM(
        'Organizer',
        'Category_Check_Team'
    ) NOT NULL,

    PRIMARY KEY (Person_ID, Champ_ID, Role),

    FOREIGN KEY (Person_ID)
        REFERENCES PERSON(Person_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (Champ_ID)
        REFERENCES CHAMPIONSHIP(Champ_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);


CREATE TABLE ENTRY_FOR_CLUB (
    Person_ID INT NOT NULL,
    Category_ID INT NOT NULL,
    Champ_ID INT NOT NULL,
    Club_ID INT NOT NULL,

    PRIMARY KEY (
        Person_ID,
        Category_ID,
        Champ_ID,
        Club_ID
    ),

    FOREIGN KEY (
        Person_ID,
        Category_ID,
        Champ_ID
    )
        REFERENCES COMPETES_IN(
            Person_ID,
            Category_ID,
            Champ_ID
        )
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (Club_ID)
        REFERENCES CLUB(Club_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE CHANGE_RECORD (
    Change_ID INT AUTO_INCREMENT PRIMARY KEY,

    Field_Name VARCHAR(100) NOT NULL,

    Old_Value TEXT,
    New_Value TEXT,

    Reason TEXT NOT NULL,

    Requested_At DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Decided_At DATETIME,

    Status ENUM(
        'Pending',
        'Approved',
        'Rejected'
    ) NOT NULL DEFAULT 'Pending',

    Entry_Person_ID INT NOT NULL,
    Entry_Category_ID INT NOT NULL,
    Entry_Champ_ID INT NOT NULL,

    Requested_By INT NOT NULL,
    Approved_By INT,

    FOREIGN KEY (
        Entry_Person_ID,
        Entry_Category_ID,
        Entry_Champ_ID
    )
        REFERENCES COMPETES_IN(
            Person_ID,
            Category_ID,
            Champ_ID
        )
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (Requested_By)
        REFERENCES PERSON(Person_ID)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (Approved_By)
        REFERENCES WBMA_OFFICER(Person_ID)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT,

    CHECK (
        (Status = 'Pending' AND Decided_At IS NULL)
        OR
        (Status IN ('Approved', 'Rejected') AND Decided_At IS NOT NULL)
    ),

    CHECK (
        Status <> 'Approved'
        OR Approved_By IS NOT NULL
    )
);

CREATE INDEX idx_championship_status
ON CHAMPIONSHIP(Status);

CREATE INDEX idx_championship_year
ON CHAMPIONSHIP(Year);

CREATE INDEX idx_person_display_name
ON PERSON(Display_Name);

CREATE INDEX idx_club_name
ON CLUB(Name);

CREATE INDEX idx_category_name
ON CATEGORY(Name);

CREATE INDEX idx_host_bid_status
ON HOST_BID(Status);

CREATE INDEX idx_competes_in_placement
ON COMPETES_IN(Champ_ID, Placement);

CREATE INDEX idx_competes_in_score
ON COMPETES_IN(Champ_ID, Category_ID, Score);

CREATE INDEX idx_offers_group
ON OFFERS(Champ_ID, Category_Group);

CREATE INDEX idx_ticket_status
ON TICKET(Champ_ID, Status);
