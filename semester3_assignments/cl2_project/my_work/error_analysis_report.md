# Phase 4: Qualitative Error Analysis & Learned Feature Weight Inspection

## 1. Learned Linguistic Feature Weights (Logistic Regression M4)

| Feature Name | Learned Weight | Linguistic Interpretation |
| :--- | :---: | :--- |
| `rst_weighted_polarity_density` | `+0.6803` | Pushes toward Positive (+1) |
| `rst_weighted_neg_density` | `-0.4992` | Pushes toward Negative (0) |
| `rst_weighted_neg_excess_density` | `-0.4094` | Pushes toward Negative (0) |
| `ana_salient_neg_density` | `-0.3201` | Pushes toward Negative (0) |
| `ana_salient_net_density` | `+0.3072` | Pushes toward Positive (+1) |
| `rst_weighted_pos_excess_density` | `+0.2709` | Pushes toward Positive (+1) |
| `ana_salient_neg_excess_density` | `-0.1875` | Pushes toward Negative (0) |
| `rst_weighted_pos_density` | `+0.1812` | Pushes toward Positive (+1) |
| `ana_salient_pos_excess_density` | `+0.1197` | Pushes toward Positive (+1) |
| `ana_resolved_pronoun_density` | `-0.0958` | Pushes toward Negative (0) |
| `rst_nucleus_pos_density` | `+0.0723` | Pushes toward Positive (+1) |
| `rst_nucleus_pos_excess_density` | `+0.0595` | Pushes toward Positive (+1) |
| `rst_satellite_pos_density` | `-0.0497` | Pushes toward Negative (0) |
| `rst_nucleus_neg_excess_density` | `-0.0373` | Pushes toward Negative (0) |
| `lex_polarity_density` | `+0.0255` | Pushes toward Positive (+1) |
| `rst_satellite_neg_density` | `+0.0248` | Pushes toward Positive (+1) |
| `rst_nucleus_neg_density` | `-0.0246` | Pushes toward Negative (0) |
| `shift_density` | `+0.0203` | Pushes toward Positive (+1) |
| `lex_neg_count_density` | `-0.0198` | Pushes toward Negative (0) |
| `lex_neg_density` | `-0.0198` | Pushes toward Negative (0) |
| `lex_neg_excess_density` | `-0.0162` | Pushes toward Negative (0) |
| `shift_neg_density` | `-0.0157` | Pushes toward Negative (0) |
| `lex_total_density` | `-0.0142` | Pushes toward Negative (0) |
| `ana_salient_pos_density` | `-0.0129` | Pushes toward Negative (0) |
| `shift_neg_excess_density` | `-0.0129` | Pushes toward Negative (0) |
| `shift_abs_density` | `-0.0110` | Pushes toward Negative (0) |
| `lex_pos_excess_density` | `+0.0093` | Pushes toward Positive (+1) |
| `shift_pos_excess_density` | `+0.0074` | Pushes toward Positive (+1) |
| `lex_pos_count_density` | `+0.0057` | Pushes toward Positive (+1) |
| `lex_pos_density` | `+0.0057` | Pushes toward Positive (+1) |
| `shift_pos_density` | `+0.0047` | Pushes toward Positive (+1) |

## 2. Examples Corrected by Anaphora (M3) & RST Discourse Weighting (M4)

Total test reviews where M4 corrected an error made by M0/M2 baseline: **17**

- **Test Review #15** (Gold Label: **Positive (1)**):
  - `LR_M0`: 0, `LR_M4`: 1 | `NB_M0`: 0, `NB_M4`: 0 | `SO-CAL M2`: 1, `SO-CAL M4`: 1
  - *Excerpt:* "warning ! : may contain some mild spoilers and offensive material . rated : r ( ! ) for sexual content , crude and sexual humor , and some nudity . . ( a mild r rating ) starring : rob schneider , oded fehr , eddie griffin , arija bareikis , amy poehler , norm mcdonald . running time : 88 minutes " deuce bigalow : male gigolo " is simply a hilarious good-natured comedy that may offend some , but underneath all it's crude humor and sexual content ..."

- **Test Review #23** (Gold Label: **Positive (1)**):
  - `LR_M0`: 0, `LR_M4`: 1 | `NB_M0`: 0, `NB_M4`: 1 | `SO-CAL M2`: 1, `SO-CAL M4`: 1
  - *Excerpt:* "let's face it : since waterworld floated by , the summer movie season has grown * very * stale . with no new eye-candy for four weeks straight , we've had to sustain ourselves on the quasi-nutritional value of cheatin' husbands , traveling chocolate salesmen , and computer- generated serial killers . sigh . thank god for desperado . the freewheeling sequel to el mariachi--director robert rodriguez's notorious $7000 debut--stars a cool antonio banderas as the returning guitarist with no name . he's a man in black with revenge on ..."

- **Test Review #24** (Gold Label: **Positive (1)**):
  - `LR_M0`: 1, `LR_M4`: 1 | `NB_M0`: 1, `NB_M4`: 1 | `SO-CAL M2`: 0, `SO-CAL M4`: 1
  - *Excerpt:* "just look back two years ago at the coen brothers' comedic gem the big lebowski , change the actors , take away the bowling alley , add a record store , and you've got high fidelity ( or maybe the other way around since nick hornby's novel high fidelity came first ) . either way , it's been done before , a trio of losers cracking jokes and complaining about their failed romances , yet it remains consistently funny . why is this ? maybe because you know your life ..."

- **Test Review #26** (Gold Label: **Negative (0)**):
  - `LR_M0`: 0, `LR_M4`: 0 | `NB_M0`: 0, `NB_M4`: 0 | `SO-CAL M2`: 1, `SO-CAL M4`: 0
  - *Excerpt:* "one of the most blatantly obvious signs that often-acclaimed director sidney lumet's " gloria , " a remake of the 1980 john cassavetes film , had absolutely no effect on me occurred when i was driving home from the theatre . suddenly , i realized that since i had stood up from my theatre seat five minutes before , i had not thought once about the film i had just invested nearly two hours of my life in . when a movie is over , aren't we supposed to think ..."

- **Test Review #31** (Gold Label: **Negative (0)**):
  - `LR_M0`: 1, `LR_M4`: 1 | `NB_M0`: 1, `NB_M4`: 0 | `SO-CAL M2`: 0, `SO-CAL M4`: 0
  - *Excerpt:* "silly performances and some huge gaps in logic mar an otherwise interesting tale of an eclectic group of people stranded at " the last stop cafe and motel " due to heavy snowfall . one of the stranded is a colorado state highway patrolman ( adam beach ) who discovers a murder scene and a bag full of cash from a recent bank robbery . someone amongst the group of strangers is a bank robber and a murderer , but is it the same person or are there multiple criminals ..."

## 3. Remaining Error Cases in M4 (False Positives & False Negatives)

- **Remaining False Positives (Actual Negative predicted as Positive):** 10
  - *Test Review #10:* "steve martin is one of the funniest men alive . if you can take that as a true statement , then your disappointment at this film will equal mine . martin can be hilarious , creating some of the best laugh-out-loud experiences that have ever taken place in movie theaters . you won't find any of them here . the old television series that this is based on has its moments of humor and wit ..."
  - *Test Review #16:* "phew , what a mess ! for his fifth collaboration with director rich- ard donner ( lethal weapon i-iii , maverick ) , mel gibson plays a motormouth , maybe mentally ill new york city cabbie , jerry , whose wild conspiracy theories are all but ignored by alice ( julia roberts , acting all serious ) , the justice department employee that he has a crush on . she not interested , but another ..."
  - *Test Review #31:* "silly performances and some huge gaps in logic mar an otherwise interesting tale of an eclectic group of people stranded at " the last stop cafe and motel " due to heavy snowfall . one of the stranded is a colorado state highway patrolman ( adam beach ) who discovers a murder scene and a bag full of cash from a recent bank robbery . someone amongst the group of strangers is a bank robber ..."

- **Remaining False Negatives (Actual Positive predicted as Negative):** 13
  - *Test Review #54:* "susan granger's review of " osmosis jones " ( warner bros . ) if the farrelly brothers taught anatomy & physiology in school , no one would cut ever class . this hip , live action/animation story begins as a monkey snatches a hard-boiled egg from frank , a zookeeper ( bill murray ) , who grabs it back , drops it , then gobbles up the contaminated morsel , explaining , " if it ..."
  - *Test Review #58:* "synopsis : in phantom menace the galaxy is divided into power groups whose interests will inevitably collide in later sequels . there is an overarching galactic united nations-type organization called the senate presided by a weak chancellor . within the senate two camps are at odds : a bickering , isolationist alliance called the republic and their aggressive rival the trade federation . preserving law and order are a council of jedi knights who are ..."
  - *Test Review #59:* "this movie was one of the first american films done by director paul verhoeven . he has done films since then such as basic instict and starship troopers . all of his movies have one main thing in common- they don't skimp on the violence . in a verhoeven movie a guy doesn't get shot once in the chest- he gets shot many times all over the body . robocop takes place in detroit in ..."
