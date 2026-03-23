import requests
import json
def get_llm_annotation(prompt_text):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "gemma2:2b", 
        "prompt": prompt_text,
        "stream": False
    }
    response = requests.post(url, json=payload)
    return response.json()['response']

prompt_text_1 = """

Annotate the following English sentences in CoNLL format. The POS column must be tagged using 
the Universal Dependencies tagset. The CHUNK and NER columns must be tagged using 
the IOB tagging scheme.


Columns: TOKEN POS CHUNK NER

Sentences:

# sentence 1
Marshall sat in one of the several leather chairs.

# sentence 2
Outside the office windows, twenty-four stories above Wall Street, a light rain was falling.

# sentence 3
`` Mr. Gross, your report says that ' our function is investigative and advisory and does not in any way derogate from or prejudice Mr. Bang-Jensen's rights as a staff member.

# sentence 4
You know, Bang-Jensen characterized your Committee as having prejudged his case ''.

# sentence 5
Gross swung his swivel chair.

# sentence 6
`` Well, how could that have been??

# sentence 7
I don't consider that he was prejudged.

# sentence 8
We were given a job and we carried it out, and later, his case was taken up by the Disciplinary Committee.

# sentence 9
`` We have nothing to hide under a bushel.

# sentence 10
We did our job, Mr. Stavropoulos and Mr. De Seynes and myself, taking evidence from a number of people ''.

# sentence 11
`` What did you think about his mental state ''??

# sentence 12
`` I think our report sums up our finding '', Gross answered.

# sentence 13
`` Don't forget, here was a man who had been accusing his colleagues for almost a year of willfully attempting to present an incorrect report.

# sentence 14
`` This was not merely alleging errors, but was carried out by day-after-day allegations in memos, written charges of serious consequence.

# sentence 15
`` This is a distressing thing.

# sentence 16
Supposing you or I were being accused in this manner, and yet we were doing our level best to carry on our work.

# sentence 17
No organization can carry on like that.

# sentence 18
`` I've been in government and I can tell some pretty hairy stories about personnel difficulties, so I know what a problem he was ''.

# sentence 19
`` What I'd like you to comment on is the criticism leveled at your Committee ''.

# sentence 20
`` What do you mean ''??

# sentence 21
`` For instance, regarding the fact that the Gross Committee issued two interim announcements to the press during its investigation.

# sentence 22
You know Bang-Jensen was told the Committee was ' to convey its views, suggestions and recommendations to the Secretary General.

# sentence 23
In his own words, Bang-Jensen ' took it for granted that the Group would report to the Secretary General privately and not in public.

# sentence 24
He claimed that the release of the preliminary findings was ' prejudicial to his position ' ''.

# sentence 25
Gross bristled.

# sentence 26
For an instant he glared speechless at Marshall.

# sentence 27
`` Listen '', he said.

# sentence 28
`` I thought the entire report was going to be confidential from beginning to end.

# sentence 29
But you know Bang-Jensen launched an active campaign against us in the press.

# sentence 30
It was getting so that we, the Committee, were being tried.

# sentence 31
You can find it in the papers ''.

# sentence 32
`` Well, as a matter of fact, I've looked through back-issue files of New York papers for December, 1957, and haven't found a great deal '' -- Gross shot another look at Marshall.

# sentence 33
`` It wasn't necessarily all here in New York.

# sentence 34
Don't forget the foreign press ''.

# sentence 35
`` Then what about the second interim public announcement??

# sentence 36
This cited Bang-Jensen's ' aberrant conduct ' ''.

# sentence 37
`` The reason for that report was to settle the matter of the list.

# sentence 38
As far as I'm concerned, it was a separate matter from the general Committee study of Bang-Jensen's conduct.

# sentence 39
The January fifteen report recommended that Bang-Jensen be instructed to burn the list -- the papers -- in the presence of a U.N. Security Officer ''.

# sentence 40
`` How about your press conference three days later -- what was the reason for that??

# sentence 41
Bang-Jensen said you told correspondents that you had checked in advance to make sure the term ' aberrant conduct ' was not libelous.

# sentence 42
He claimed you made other slanderous allegations ''.

# sentence 43
Gross paused and repeated himself.

# sentence 44
`` The entire object of the press conference was to clarify the problem of the list, since many in the press were querying the U.N. about it.

# sentence 45
What was the list??

# sentence 46
I don't know.

# sentence 47
Bang-Jensen never explained what the documents or papers were that he had in his possession.

# sentence 48
`` It was foolish of him to keep them, whatever they were.

# sentence 49
He could have been blackmailed, or his family might have been threatened.

# sentence 50
Of course the matter caught the public's attention.

# sentence 51
We attempted to conclude this, and did so by having the papers burned.

# sentence 52
Hammarskjold didn't like the way it was carried out.

# sentence 53
It was a sort of Gotterdammerung affair.

# sentence 54
Hammarskjold believes the U.N. is an organization that settles matters in a procedural way. ''

# sentence 55
Peter Marshall reflected.

# sentence 56
If Hammarskjold had not wanted the list disposed of in this manner, and if Bang-Jensen had not wanted it -- who had ordered it??

# sentence 57
`` Mr. Gross, concerning the formation of your Committee, there's the fact that you have been a legal adviser to the U.N. in the past ; ; as I understand it, Mr. Hammarskjold wanted outside advice.

# sentence 58
Could you comment on that ''??

# sentence 59
`` I've served as a counsel for the U.N. for some years, specializing particularly in real estate matters or other problems that the regular U.N. legal staff might not be equipped to handle.

# sentence 60
Mr. Stavropoulos is the U.N. legal chief and a very good man, but he is not fully versed on some technical points of American law ''.

# sentence 61
`` What did you think about Bang-Jensen's contention of errors and omissions in the Hungarian report ''??

# sentence 62
Marshall asked.

# sentence 63
`` Those ''!!

# sentence 64
Gross answered.

# sentence 65
`` Why, Mick Shann went over and over the report with Alsing Andersen, trying to check them out.

# sentence 66
Even after the incident between Bang-Jensen and Shann in the Delegates' Lounge and this was not the way the Chicago Tribune presented it ''.

# sentence 67
Gross reached in his desk and pulled out two newspaper clippings.

# sentence 68
One was an article on the U.N. by Alice Widener from the Cincinnati Enquirer.

# sentence 69
The other was by Chesly Manley in the Chicago Daily Tribune.

# sentence 70
Gross pointed to the Manley story.

# sentence 71
`` I know Ches, he's a friend of mine.

# sentence 72
He probably didn't mean to write it this way, or maybe he did.

# sentence 73
There wasn't any ' violent argument ' between Bang-Jensen and Shann, as the Tribune puts it.

# sentence 74
That implies that Shann was on the enemy side.

# sentence 75
You see what I mean??

# sentence 76
How it's phrased there -- the word violent.

# sentence 77
`` The case was that Bang-Jensen came up to Shann claiming he had found further errors in the report. '

# sentence 78
I've found errors and I want you to look them over.

# sentence 79
So once again Shann had to argue with him about this.

# sentence 80
But it wasn't a violent discussion.

# sentence 81
And after all this, Shann went over all that Bang-Jensen had brought up ''.

# sentence 82
( Shann's own report, Peter Marshall reflected, describes the encounter as `` immoderate ''.

# sentence 83
Bang-Jensen was in `` hysterical condition ''. )

# sentence 84
Gross stopped briefly, then went on.

# sentence 85
`` Shann was responsible for the report.

# sentence 86
He has felt terrible about all this.

# sentence 87
It was a good report, he did all he could to make it a good report.

# sentence 88
When I speak of how Shann felt, I know well.

# sentence 89
Don't forget, I am an old member of the club, a former delegate.

# sentence 90
I think you are being unfair to take these things up now.

# sentence 91
`` You know, this hits in many areas.

# sentence 92
It appeals to those who were frustrated in the outcome of the Hungarian situation.

# sentence 93
Don't forget, the U.N. did no more than the United States did.

# sentence 94
It takes a great deal of sophisticated thought to get the impact of this fact ''.

# sentence 95
Chapter 22 from the home of his friend, Henrik Kauffmann, in Washington, D.C., Paul Bang-Jensen sent a telegram dated December 9, 1957, to Ernest Gross.

# sentence 96
It said in part : `` the matters to be considered are obviously of a grave character, and I therefore respectfully request that the hearing be postponed for two weeks in order that I might make adequate preparation ''.

# sentence 97
Ernest Gross replied the next day, putting the suspended diplomat's fears to rest.

# sentence 98
`` This reveals some misunderstanding on your part.

# sentence 99
The group conducting the review is not holding formal hearings.

# sentence 100
It wished to pursue, in the course of this review, questions arising from the body of material already in its possession. ''

"""

prompt_text_2 = """

Annotate the following English sentences in CoNLL format. The POS column must be tagged using 
the Universal Dependencies tagset. The CHUNK and NER columns must be tagged using 
the IOB tagging scheme.

Columns: TOKEN POS CHUNK NER

Take help from these examples:

# sentence 1
The	DET	B-NP	O
group	NOUN	I-NP	O
,	PUNCT	O	O
upon	ADP	B-PP	O
the	DET	B-NP	O
issuance	NOUN	I-NP	O
of	ADP	B-PP	O
its	PRON	B-NP	O
first	ADJ	I-NP	O
press	NOUN	I-NP	O
release	NOUN	I-NP	O
on	ADP	B-PP	O
December	PROPN	B-NP	B-DATE
21	NUM	I-NP	I-DATE
,	PUNCT	O	I-DATE
1957	NUM	B-NP	I-DATE
,	PUNCT	O	O
designated	VERB	B-VP	O
itself	PRON	B-NP	O
a	DET	B-NP	O
``	PUNCT	I-NP	O
Committee	PROPN	I-NP	B-ORG
of	ADP	I-NP	I-ORG
Investigation	PROPN	I-NP	I-ORG
``	PUNCT	O	O
.	PUNCT	O	O

# sentence 2
In	ADP	B-PP	O
the	DET	B-NP	O
course	NOUN	I-NP	O
of	ADP	B-PP	O
its	PRON	B-NP	O
inquiry	NOUN	I-NP	O
,	PUNCT	O	O
it	PRON	B-NP	O
took	VERB	B-VP	O
testimony	NOUN	B-NP	O
from	ADP	B-PP	O
only	ADV	B-NP	O
seven	NUM	I-NP	O
witnesses	NOUN	I-NP	O
.	PUNCT	O	O

# sentence 3
It	PRON	B-NP	O
heard	VERB	B-VP	O
Bang-Jensen	PROPN	B-NP	B-PER
twice	ADV	B-ADVP	O
and	CCONJ	O	O
his	PRON	B-NP	O
lawyer	NOUN	I-NP	O
,	PUNCT	O	O
Adolf	PROPN	B-NP	B-PER
A.	PROPN	I-NP	I-PER
Berle	PROPN	I-NP	I-PER
,	PUNCT	O	I-PER
Jr.	PROPN	B-NP	I-PER
,	PUNCT	O	O
once	ADV	O	O
.	PUNCT	O	O

# sentence 4
Its	PRON	B-NP	O
second	ADJ	I-NP	O
press	NOUN	I-NP	O
release	NOUN	I-NP	O
was	AUX	B-VP	O
on	ADP	B-PP	O
January	PROPN	B-NP	B-DATE
15	NUM	I-NP	I-DATE
,	PUNCT	O	I-DATE
1958	NUM	B-NP	I-DATE
,	PUNCT	O	O
and	CCONJ	O	O
it	PRON	B-NP	O
recommended	VERB	B-VP	O
that	SCONJ	B-SCONJ	O
the	DET	B-NP	O
secret	ADJ	I-NP	O
papers	NOUN	I-NP	O
be	AUX	B-VP	O
destroyed	VERB	I-VP	O
.	PUNCT	O	O

# sentence 5
It	PRON	B-NP	O
also	ADV	B-ADVP	O
implied	VERB	B-VP	O
that	SCONJ	B-SCONJ	O
Paul	PROPN	B-NP	O
Bang-Jensen	PROPN	I-NP	B-PER
had	AUX	B-VP	O
been	AUX	I-VP	O
irresponsible	ADJ	B-ADJP	O
.	PUNCT	O	O

# sentence 6
On	ADP	B-PP	O
January	PROPN	B-NP	B-DATE
18	NUM	I-NP	I-DATE
,	PUNCT	O	O
Ernest	PROPN	B-NP	B-PER
Gross	PROPN	I-NP	I-PER
conducted	VERB	B-VP	O
a	DET	B-NP	O
press	NOUN	I-NP	O
conference	NOUN	I-NP	O
at	ADP	B-PP	O
the	DET	B-NP	O
U.N.	PROPN	I-NP	B-ORG
lasting	VERB	B-VP	O
an	DET	B-NP	O
hour	NOUN	I-NP	O
.	PUNCT	O	O

# sentence 7
Here	ADV	B-ADVP	O
,	PUNCT	O	O
he	PRON	B-NP	O
openly	ADV	B-ADVP	O
attacked	VERB	B-VP	O
Bang-Jensen	PROPN	B-NP	B-PER
and	CCONJ	O	O
referred	VERB	B-VP	O
to	ADP	B-PP	O
his	PRON	B-NP	O
``	PUNCT	I-NP	O
aberrant	ADJ	I-NP	O
conduct	NOUN	I-NP	O
``	PUNCT	O	O
.	PUNCT	O	O

# sentence 8
This	DET	B-NP	O
conference	NOUN	I-NP	O
was	AUX	B-VP	O
held	VERB	I-VP	O
despite	ADP	B-PP	O
Stavropoulos	PROPN	B-NP	B-PER
'	PART	B-NP	O
assurance	NOUN	I-NP	O
to	ADP	B-PP	O
Adolf	PROPN	B-NP	B-PER
Berle	PROPN	I-NP	I-PER
,	PUNCT	O	O
who	PRON	B-NP	O
was	AUX	B-VP	O
leaving	VERB	I-VP	O
the	DET	B-NP	O
same	ADJ	I-NP	O
day	NOUN	I-NP	O
for	ADP	B-PP	O
Puerto	PROPN	B-NP	B-LOC
Rico	PROPN	I-NP	I-LOC
,	PUNCT	O	O
that	SCONJ	B-SCONJ	O
nothing	PRON	B-NP	O
would	AUX	B-VP	O
be	AUX	I-VP	O
done	VERB	I-VP	O
until	ADP	B-PP	O
his	PRON	B-NP	O
return	NOUN	I-NP	O
on	ADP	B-PP	O
January	PROPN	B-NP	B-DATE
22	NUM	I-NP	I-DATE
,	PUNCT	O	O
except	SCONJ	B-PP	O
that	SCONJ	B-SCONJ	O
the	DET	B-NP	O
Secretary	PROPN	I-NP	O
General	PROPN	I-NP	O
would	AUX	B-VP	O
probably	ADV	B-ADVP	O
order	VERB	B-VP	O
the	DET	B-NP	O
list	NOUN	I-NP	O
destroyed	VERB	B-VP	O
.	PUNCT	O	O

# sentence 9
On	ADP	B-PP	O
January	PROPN	B-NP	B-DATE
24	NUM	I-NP	I-DATE
Paul	PROPN	B-NP	O
Bang-Jensen	PROPN	I-NP	B-PER
,	PUNCT	O	O
accompanied	VERB	B-VP	O
by	ADP	B-PP	O
Adolf	PROPN	B-NP	B-PER
Berle	PROPN	I-NP	I-PER
,	PUNCT	O	O
was	AUX	B-VP	O
met	VERB	I-VP	O
by	ADP	B-PP	O
Dragoslav	PROPN	B-NP	B-PER
Protitch	PROPN	I-NP	I-PER
and	CCONJ	O	O
Colonel	PROPN	B-NP	O
Frank	PROPN	I-NP	B-PER
Begley	PROPN	I-NP	I-PER
,	PUNCT	O	O
former	ADJ	B-NP	O
Police	PROPN	I-NP	O
Chief	PROPN	I-NP	O
of	ADP	I-NP	O
Farmington	PROPN	I-NP	B-LOC
,	PUNCT	O	I-LOC
Conn.	PROPN	B-NP	I-LOC
,	PUNCT	O	O
and	CCONJ	O	O
now	ADV	B-ADVP	O
head	NOUN	B-NP	O
of	ADP	B-PP	O
U.N.	PROPN	B-NP	B-ORG
special	ADJ	I-NP	O
police	NOUN	I-NP	O
.	PUNCT	O	O

# sentence 10
The	DET	B-NP	O
four	NUM	I-NP	O
,	PUNCT	O	O
bundled	VERB	B-VP	O
in	ADP	B-PP	O
overcoats	NOUN	B-NP	O
,	PUNCT	O	O
mounted	VERB	B-VP	O
to	ADP	B-PP	O
the	DET	B-NP	O
wind-swept	ADJ	I-NP	O
roof	NOUN	I-NP	O
of	ADP	B-PP	O
the	DET	B-NP	O
U.N	PROPN	I-NP	O
.	PUNCT	O	O
There	ADV	B-ADVP	O
,	PUNCT	O	O
Begley	PROPN	B-NP	O
lit	VERB	B-VP	O
a	DET	B-NP	O
fire	NOUN	I-NP	O
in	ADP	B-PP	O
a	DET	B-NP	O
wire	NOUN	I-NP	O
basket	NOUN	I-NP	O
,	PUNCT	O	O
and	CCONJ	O	O
Bang-Jensen	PROPN	B-NP	B-PER
dropped	VERB	B-VP	O
four	NUM	B-NP	O
sealed	ADJ	I-NP	O
envelopes	NOUN	I-NP	O
into	ADP	B-PP	O
the	DET	B-NP	O
flames	NOUN	I-NP	O
.	PUNCT	O	O

Now annotate the sentences:

# sentence 101
It sounded like a fair enough invitation, Peter Marshall reflected, and Bang-Jensen must have thought so too, because on the thirteenth, he met the group of three on the thirty-sixth floor of the U.N..

# sentence 102
There, Ernest Gross further assured him : `` We were requested by the Secretary General, as I understand it, to discuss with you such matters as appear to us to be relevant, and we are not of course either a formal group or a committee in the sense of being guided by any rules or regulations of the Secretariat.

# sentence 103
The only rules which I think we shall follow will be those of common sense, justice, and fairness ''.

# sentence 104
Peter Marshall noted that Bang-Jensen had later referred to his two interviews with the Gross group as `` unfortunate experiences '', and after his second meeting on the sixteenth the Dane refused to attend further hearings without legal counsel.

# sentence 105
Marshall pondered the reason for this, and pondered too the replacement of one member of the three-man group.

# sentence 106
J. A. C. Robertson, after serving Gross one week, left for England.

# sentence 107
Livery stable -- J. Vernon, prop.

# sentence 108
''.

# sentence 109
Coaching had declined considerably by 1905, but the sign was still there, near the old Wells Fargo building in San Francisco, creaking in the fog as it had for thirty years.

# sentence 110
John Vernon had had all the patronage he cared for -- he had prospered, but he could not retire from horsedom.

# sentence 111
Coaching was in his blood.

# sentence 112
He had two interests in life : the pleasures of the table and driving.

# sentence 113
Twice a week he drove his tallyho over the Santa Cruz road, upland and through the redwood forest, with orchards below him at one hand, and glimpses of the Pacific at the other.

# sentence 114
The journey back he made along the coast road, traveling hell-for-leather, every lantern of the tallyho ablaze.

# sentence 115
The southward route was the classic run in California, and the most fashionable.

# sentence 116
His patronage on this stretch was made up largely of San Franciscans -- regulars, most of them, and trenchermen like himself.

# sentence 117
They did not complain at the inhuman hour of starting ( seven in the morning ), nor of the tariff, which was reasonable since it covered everything but the tobacco.

# sentence 118
Breakfast was at the Palace Hotel, luncheon was somewhere in the mountain forest, and dinner was either at Boulder Creek or at Santa Cruz.

# sentence 119
Gazing too long at the scenery could be tiring, so halts were contrived between meals.

# sentence 120
Then the Chinese hostler, who rode with Vernon on the box, would break open a hamper and produce filets of smoked bass or sturgeon, sandwiches, pickled eggs, and a rum sangaree to be heated over a spirit lamp.

# sentence 121
In spring and in autumn the run was made for a group of botanists which included an old friend of mine.

# sentence 122
They gathered roots, bulbs, odd ferns, leaves, and bits of resin from the rare Santa Lucia fir, which exists only on a forty-five mile strip on the westerly side of these mountains.

# sentence 123
In the Spanish days Franciscan monks roamed here to collect the resin for incense.

# sentence 124
It yields a fragrance as Orphic as that of the pastilles of Malabar.

# sentence 125
Vernon was serviceable on the botanical field trips, but he could arrange no schedule with the cooks, and he was glad when the trips dropped off, and the botanists began to motor out by themselves.

# sentence 126
My friend often breakfasted with Vernon on the morning of the regular tallyho run.

# sentence 127
This was an honor, like dining with a captain at his private table.

# sentence 128
Vernon's office adjoined the stable, and the walls were adorned with brightly colored lithographs, the folk art of the period.

# sentence 129
They advertised harness polish, liniments, Ball's Rubber Boots, Green River Whiskey, Hood's Sarsaparilla, patent medicines, shoe blacking, and chewing tobacco.

# sentence 130
The hostler would have the table ready and a pot of coffee hissing on the stove ; ; then a porter from Manning's Fish House would trot in with a tray on his head.

# sentence 131
It was draped with snowy napkins that kept hot a platter of oyster salt roast and a mound of corn fritters.

# sentence 132
Vernon was consummately fond of oysters, and Manning's had been famous for them since the Civil War.

# sentence 133
Oyster salt roast -- oysters on the half shell, cooked on a bed of coarse salt that kept them hot when served -- was a standby at Manning's.

# sentence 134
Its early morning patrons were coachmen, who fortified themselves for the day with that delicacy.

# sentence 135
In the 1890's the Palace Hotel began serving an oyster dish named after its manager, John C. Kirkpatrick.

# sentence 136
This dish much resembles the oysters Rockefeller made famous by Antoine's in New Orleans, though the Palace chef announced it as a variant of Manning's roast oysters.

# sentence 137
( Gastronomes have long argued about which came first, the Palace's or Antoine's.

# sentence 138
Antoine's held as mandatory a splash of absinthe or Pernod on the parsley or spinach which was used for the underbedding.

# sentence 139
The Kirkpatrick version holds liqueur as optional. )

# sentence 140
Vernon, however, held out for plain oyster roast, and plenty of it, unadorned by herbs or any seasoning but salt, though he did fancy a bit of lemon.

# sentence 141
After the meal, he and his guests went out to inspect the rig ; ; this was merely a ritual, to please all hands concerned.

# sentence 142
The tallyho had cost Vernon $2,300.

# sentence 143
A replica of two coaches made in England for the Belmont Club in the East, and matchless west of the Rockies, it was the despair of whips on the Santa Cruz run.

# sentence 144
One could shave in the reflection of its French-polished panels, and its axles were greased like those of roulette wheels.

# sentence 145
The horses were groomed to a high gloss ; ; departing, they stepped solemnly with knees lifted to the jaw, for they had been trained to drag at important funerals.

# sentence 146
But for the start of the Santa Cruz run, the whip fell.

# sentence 147
The clients boarded the tallyho at the Palace promptly at seven.

# sentence 148
They had been fed a hunting breakfast, so called because a kedgeree, the dish identified with fox hunting, was on the bill.

# sentence 149
There are many ways of making a kedgeree, every one of which is right.

# sentence 150
Here is an original kedgeree recipe from the Family Club's kitchen : Club Kedgeree Flake ( for three ) a cupful of cold boiled haddock, mix with a cupful of cooked rice, two minced hard-boiled eggs, some buttery white sauce done with cream, cayenne, pepper, salt, a pinch of curry, a tablespoonful of minced onion fried, and a bit of anchovy.

# sentence 151
Heat and serve hot on toast.

# sentence 152
The omelet named for Ernest Arbogast, the Palace's chef, was even more in demand.

# sentence 153
For decades it was the most popular dish served in the Ladies' Grill at breakfast, and it is one of the few old Palace dishes that still survive.

# sentence 154
Native California oysters, salty and piquant, as coppery as Delawares and not much larger than a five-cent piece, went into it.

# sentence 155
The original formula goes thus : omelet Arbogast Fry in butter a small minced onion, rub with a tablespoonful of flour, add half a cup of cream, six beaten eggs, pepper, celery salt, a teaspoonful of minced chives, a dash of cayenne, and a pinch of nutmeg.

# sentence 156
A jigger of dry Sherry follows, and as the mixture stiffens, in go a hundred of the little oysters.

# sentence 157
Louis Sherry once stayed a fortnight at the Palace, and he was so pleased with omelet Arbogast that he introduced it at his restaurant in New York J. Pierpont Morgan had come in his private train to San Francisco, to attend an Episcopal convention, and brought the restaurateur with him.

# sentence 158
As things happened, Morgan was installed in the Nob Hill residence of a magnate friend, whose kitchen swarmed with cooks of approved talent.

# sentence 159
Sherry remained in his hotel suite, where he amused himself as best he could.

# sentence 160
Twice he left everything to his entourage, and fled to make the Santa Cruz tour under Vernon's guidance.

# sentence 161
In the grand court of the Palace, notable for its tiers of Moorish galleries that looked down on the maelstrom of vehicles below, Vernon's station was at the entrance.

# sentence 162
It was a post of honor, held inviolate for him ; ; he had the primacy among the coachmen.

# sentence 163
Of majestic build, rubicund and slash-mouthed, he resembled the late General Winfield Scott, who was said to be the most imposing general of his century, if not of all centuries.

# sentence 164
Vernon wore a gray tall hat, a gardenia, and maroon Wellington boots that glistened like currant jelly.

# sentence 165
Promptly at seven he would clatter out of the court with twelve in the tallyho.

# sentence 166
He had style : he held his reins in a loose bunch at the third button of his checked Epsom surtout, and when the horses leaned at a curve, as if bent by the force of a gale, he leaned with them.

# sentence 167
They cantered down the peninsula, not slackening until the coach reached Woodside where the Santa Cruz uplands begin.

# sentence 168
The road maps of the region have changed since 1905 ; ; inns have burned down, moved elsewhere, or taken other names.

# sentence 169
Once on the road ( and especially if the passengers were all regulars and masculine ), the schedule meant nothing.

# sentence 170
An agreeable ease suffused Vernon and the passengers of the tallyho, from which there issued clouds of smoke.

# sentence 171
Vernon would tilt his hat over one ear as he lounged with his feet on the dashboard, indulging in a huge cigar.

# sentence 172
The horses moved at a clump ; ; they were no more on parade than was their driver ; ; one fork of the road was as good as another.

# sentence 173
The Santa Cruz mountains sprawl over three counties, and the roads twist through sky-tapping redwoods down whose furrowed columns ripple streams of rain, even when heat bakes the Santa Clara valley below at the left.

# sentence 174
The water splashes into shoulder-high tracts of fernery.

# sentence 175
You arrive there in seersucker, and feel you were half-witted not to bring a mackintosh.

# sentence 176
Vernon kept an account book with a list of all the establishments that he thought worthy of patronage.

# sentence 177
A number of them must have fallen into disfavor ; ; they were struck out with remarks in red ink, denouncing both the cooks and the management.

# sentence 178
He was copious in his praise of those that served food that was good to eat.

# sentence 179
The horses seemed to know these by instinct, he used to say : such places invariably had stables with superior feed bins.

# sentence 180
There was Wright's, for one, lost amongst trees, its wide verandas strewn with rockers.

# sentence 181
Many of its sojourners were devoted to seclusion and quiet, and lived there to the end of their days.

# sentence 182
It was the haunt of writer Ambrose Bierce, who admired its redwoods.

# sentence 183
Acorns from the great oaks fed the small black pigs ( akin to Berkshires ), whose `` carcass sweepstakes '' were renowned.

# sentence 184
Their ham butts, cured in oak-log smoke, were also esteemed when roasted or boiled, and served with this original sauce : Wright's devil sauce ; ; put into a saucepan a cupful of the baked ham gravy, or of the boiled ham liquor, with a half stick of butter, three teaspoonfuls of made mustard, and two mashed garlic cloves.

# sentence 185
Contribute also an onion, a peeled tomato and two pickled gherkins, and a mashed lime.

# sentence 186
After this has simmered an hour, add two tablespoons each of Worcestershire, catsup, and chutney, two pickled walnuts, and a pint of Sherry.

# sentence 187
Then simmer fifteen minutes longer.

# sentence 188
Every winter a kegful of this sauce was made and placed at the end of a row of four other kegs in the cellar, so that when its turn came, it was properly mellowed.

# sentence 189
Vineyards and orchards also grew around Wright's, and deer were rather a nuisance ; ; they leaped six-foot fences with the agility of panthers.

# sentence 190
But no one complained when they wound up, regardless of season, in venison pies.

# sentence 191
No one complained of the white wine either : at this altitude of two thousand feet, grapes acquire a dryness and the tang of gunflint.

# sentence 192
( The Almaden vineyards have now climbed to this height. )

# sentence 193
Apple trees grew there also.

# sentence 194
Though creeks in the Santa Cruz mountains flow brimful the year round and it is forever spring, the apples that grow there have a wintry crackle.

# sentence 195
Dwellers thereabouts preferred to get their apple pies at the local bakery, which had a brick oven fired with redwood billets.

# sentence 196
The merit of the pie, Vernon believed, was due more to its making than to the waning heat of the oven.

# sentence 197
The recipe, which he got from the baker, and wrote down in his ledger, is basically this : Wright's apple pie ; ; peel, core, and slice across enough apples to make a dome in the pie tin, and set aside.

# sentence 198
In a saucepan put sufficient water to cover them, an equal amount of sugar, a sliced lemon, a tablespoonful of apricot preserve or jam, a pinch each of clove and nutmeg, and a large bay leaf.

# sentence 199
Let this boil gently for twenty minutes, then strain.

# sentence 200
Poach the apples in this syrup for twelve minutes, drain them, and cool.

"""

prompt_text_3= """

Annotate the following Hindi sentences in CoNLL format. The POS column must be tagged using 
the BIS (Bureau of Indian Standards) tagset. The CHUNK and NER columns must be tagged using 
the IOB tagging scheme.


Columns: TOKEN POS CHUNK NER

Sentences:

# sentence 1
﻿बंद पिंजरे से पूरा शेर पिघल कर बाहर निकल गया

# sentence 2
बीरबल की चतुराई पर बादशाह अति प्रसन्न हुए और पूछा की बीरबल तुमको कैसे पता चला की इसके अन्दर लाख का शेर हैं

# sentence 3
जहापनाह इस पत्र ने साफ साफ लिख रखा हैं की इस शेर को पिंजरे से निकालना हैं वो भी बिना इसको खोले तो इसका मतलब हैं की जरूर शेर किसी धातु का नही हैं, हमने तो केवल देखने के लिए सरिया मंगाया था की क्या वाकई शेर पिघालता हैं की नहीं

# sentence 4
हमने सही अंदाजा लगाया और शेर पिघल गया

# sentence 5
बादशाह एक बार और बीरबल की चतुराई से प्रसन्न हो गए और कहा - जब तक तुम मेरे साथ हो मुझे फ़ारसी क्या किसी से भी डरने की जरुरत नहीं हैं

# sentence 6
फिर क्या था फ़ारसी का दूत एक और पत्र लेकर गया और राजा को एक और बीरबल की बुद्दिमानी की कहानी सुनाई

# sentence 7
फ़ारसी का राजा भी बीरबल की चतुराई से अति प्रस्सनन हुआ और अगला तोहफा बीरबल के लिए भेजा

# sentence 8
मुगल बादशाह अकबर उदारतावादी थे

# sentence 9
इसलिए बादशाह अकबर समय समय पर अपनी प्रजा


से मिलने के लिए प्रजा मिलन दरबार लगाया करते थे

# sentence 10
दरबार में बादशाह अकबर लोगो से मिलते उनको सुनते और जिनसे प्रसन्न होते उनको उपहार देते

# sentence 11
एक बार इसी प्रकार का दरबार लगाया था

# sentence 12
दूर दूर से सभी लोग मिलने आ रहे थे

# sentence 13
एक दूर दुराज गाँव में महेशदास नाम का आदमी रहता था

# sentence 14
महेशदास ने भी मन बनाया की ये बादशाह लोग किस प्रकार रहते हैं, उनकी जीवनशैली कैसी है

# sentence 15
चलो, एक बार देखकर आते हैं

# sentence 16
यह विचार बना कर महेशदास निकल पड़े

# sentence 17
महेश दास जब महल के बाहर पहुंचे तो देखा कि बहुत सारे लोग बादशाह से मिलने के लिए पंक्ति बनाकर खड़े थे

# sentence 18
पहरेदार एक एक करके सभी से एक एक स्वर्ण मुद्रा ले रहा था

# sentence 19
लेकिन महेशदास तो खाली हाथ आये थे

# sentence 20
फिर भी महेश दास पंक्ति में लगे रहे

# sentence 21
जब महेश दास की बारी आयी और पहरेदार ने मुद्रा मांगी तो, भाई मेरे पास तो कुछ नहीं हैं, मैं तो बस एसे ही बादशाह से मिलने आया

# sentence 22
पहरेदार ने मना कर दिया, एसे तो हम नही जाने देंगे

# sentence 23
महेश दास के निवेदन के बाद, एक शर्त पर जाने की मंजूरी दी

# sentence 24
महेश दास ने भी हा भर दी

# sentence 25
और शर्त को पूरा करने का वादा किया और महल के द्वार में प्रवेश कर गया

# sentence 26
महेश दास महल में प्रवेश करते ही पूरे महल को ध्यान से देखने लगा

# sentence 27
महल की नक्काशी और बारीक़ कारीगरी देखखर महेशदास चौंक गया

# sentence 28
घूमते फिरते महेशदास वहां पहुँच गया

# sentence 29
जहाँ बादशाह अकबर प्रजा से मिल रहे थे

# sentence 30
एक एक करके सभी बादशाह के सामने अपनी हाजिरी दे रहे थे, अपनी समस्या, अपनी इच्छा बादशाह के सामने पेश करते और बादशाह उनको सुलझाने की कोशिश करते

# sentence 31
महेशदास खड़े खड़े सोच रहे थे की मैंने तो सोचा ही नही कि मुझे क्या मांगना हैं

# sentence 32
सोचते सोचते महेशदास की बारी आ गयी और महेशदास बादशाह के सामने पेश हुआ

# sentence 33
बोलो क्या नाम हैं तुम्हारा

# sentence 34
और कहाँ से आये हो तुम

# sentence 35
जी

# sentence 36
जहापनाह मेरा नाम महेशदास हैं और मैं आपके ही सल्तनत के दूर गाव का आम नागरिक हूँ बोलो क्या फरिहाद लेकर आये हो

# sentence 37
जी जहापनाह मुझे कुछ नही चाहिए

# sentence 38
मैं तो बस आपसे ही मिलने आया हूँ

# sentence 39
तुमने अपना नाम क्या बताया

# sentence 40
जी महेशदास हा

# sentence 41
महेशदास

# sentence 42
हम तुम्हारी उदारता से अति प्रसन्न हुए

# sentence 43
तुम बादशाह अकबर के दरबार में खडे हो

# sentence 44
हम तुमको एसे ही खाली नही जाने देंगे

# sentence 45
और तुम यहाँ से खाली हाथ जाओ, हमारी शानो शौकत को शोभा नही देता

# sentence 46
तुम कुछ भी मांगो

# sentence 47
बादशाह के इतने आग्रह पर महेशदास ने अपनी फरमाइश पेश की

# sentence 48
जहापनाह मुझे अपनी नंगी पीठ पर एक सौ कोड़े चाहिए

# sentence 49
बादशाह एसी फरमाइश सुनकर चोंक गये

# sentence 50
बादशाह ने कारण पुछा

# sentence 51
तो महेशदास ने कहा- बाहर जो आपका पहरेदार खड़ा हैं, उसके साथ हमरी एक शर्त लगी हैं की दरबार से हमको जो कुछ भी मिलेगा उसका आधा हिस्सा, उसको देना पड़ेगा

# sentence 52
बादशाह ये सुनकर थोड़े बौखला गए और और उन्होंने मुह बनाकर

# sentence 53
पहरेदार को बुलाने को भेजा

# sentence 54
पहरेदार ने बादशाह को झुककर सलाम किया

# sentence 55
बादशाह ने व्यंग्य में उससे कहा हम तुम्हारी पहरेदारी से प्रसन्न हुए

# sentence 56
हमनें निश्चय किया हैं महेश दास ने जो भी माँगा उसका सौ फीसदी तुमको देंगे

# sentence 57
पहरेदार खुस हुआ

# sentence 58
जी जहापनाह

# sentence 59
जैसा आप उचित समझे

# sentence 60
क्या तुम सुनना नही चाहोंगे कि इसने फरियाद की

# sentence 61
- बादशाह अकबर बोले

# sentence 62
जी जहापनाह जरूर- पहरेदार बोला

# sentence 63
इसने(महेशदास) सौ कौड़े मांगे, और हमने इसकी मंजूरी भी दे दी बादशाह ने गुस्से में आकर सैनिको से कहा इसे गिरफ्तार कर लो और इसकी अच्छे से फरियाद पूरी करो

# sentence 64
हा तो महेशदास तुम हमको बेहद पसंद आये

# sentence 65
क्या तुम हमारी दरबारी में कोई काम करना चाहोगे

# sentence 66
मुल्ला दो प्याजा बोले जहापनाह एसे कैसे किसी को भी आप दरबारी में रख सखते हैं

# sentence 67
मेरा मतलब ना कोई जान पहचान न कोई

# sentence 68
लेना देना

# sentence 69
मुल्ला दो प्याजा अपनी जबान को सँभालते हुए बोले

# sentence 70
मुल्ला तुम भी ठीक ही कहते हो, अच्छा तुम ही बताओ की इसको कैसे परखा जाये

# sentence 71
बादशाह बोले

# sentence 72
मुल्ला दो प्याजा सोचकर बोलते हैं - अगर ये यह बता दे की मेरे दिमाग मे क्या चल रहा हैं तो शायद बात बन जाये

# sentence 73
महेशदास क्या तुम इस प्रश्न का जवाब देना चाहोंगे

# sentence 74
जी जहापनाह जरूर

# sentence 75
मुल्लाजी आपके दिमाग में अभी ये चल रहा हैं कि बादशाह अच्छे हैं, और वो हम सभी का कल्याण करते हैं

# sentence 76
हमे बादशाह से कोई शिकायत नही हैं

# sentence 77
क्या मुल्लाजी हम सही कह रहे हैं न

# sentence 78
मुल्लाजी बनावटी मुस्कान के साथ जी जहापनाह ये बिलकुल ठीक कह रहा हैं

# sentence 79
क्या मुल्ला अभी तुम्हे कोई प्रश्न पूछना हैं क्या

# sentence 80
नही जहापनाह

# sentence 81
तो महेशदास हम तुम्हे अपनी दरबारी में काम करने को आमंत्रित करते हैं

# sentence 82
लेकिन हम तुमको एक नाम देना चाहेंगे

# sentence 83
जी जहापनाह आपका हुक्म सर आँखों पर

# sentence 84
हमारा दरबार और पूरी मुगलिया सल्तनत तुमको बीरबल के नाम

# sentence 85
अकबर और बीरबल दोनो का रिश्ता राजा और मंत्री से बढकर था

# sentence 86
दोनों के बीच कुछ न कुछ लतीफे चलते ही रहते

# sentence 87
अकबर और बीरबल के बीच कभी कभी एसी बाते भी होती जिनको परखने में जान का खतरा भी होता

# sentence 88
एक बार अकबर ने बीरबल से पुछा संसार में सबसे बड़ा हथियार कोनसा हैं

# sentence 89
बादशाह संसार में सबसे बड़ा हथियार हैं - आत्म-विश्वास

# sentence 90
बीरबल ने जवाब दिया

# sentence 91
बादशाह अकबर ने इस बात को अपने दिल में रख लिया और किसी दिन इसकी परख करने का निश्चय किया

# sentence 92
देवयोग से एक दिन एक हाथी पागल हो गया

# sentence 93
हाथी को काबू करने के लिए उसे जंजीरों में जकड़ा गया

# sentence 94
अकबर ने आज बीरबल के आत्मविश्वास को परखने की सोची

# sentence 95
अकबर ने बीरबल के आत्म विस्वाश की परख करने के लिए एक तरफ बीरबल को बुलावा भेजा

# sentence 96
दूसरी तरफ महावत को हाथी की जंजीरों को खोलने का आदेश दिया

# sentence 97
बीरबल को इस बात का पता नही था

# sentence 98
जब बीरबल, बादशाह अकबर से मिलने के लिए दरबार जा रहे थे तो पागल हाथी की जंजीरों को खोल दिया गया

# sentence 99
बीरबल अपनी मस्ती में ही चले जा रहे थे, उनकी नज़र पागल हाथी पर पड़ी

# sentence 100
हाथी चिंघाड़ता हुआ उनकी तरफ आ रहा था
"""

prompt_text_4 = """

Annotate the following Hindi sentences in CoNLL format. The POS column must be tagged using 
the BIS (Bureau of Indian Standards) tagset. The CHUNK and NER columns must be tagged using 
the IOB tagging scheme.

Columns: TOKEN POS CHUNK NER

Take help from these examples:

# sentence 1
बादशाह	NN	B-NP	O
अकबर	NNP	I-NP	B-PER
अपने	PRP	B-NP	O
पड़ोसी	JJ	I-NP	O
मुल्को	NN	I-NP	O
से	PSP	B-PP	O
अच्छी	JJ	B-NP	O
मित्रता	NN	I-NP	O
रखते	VM	B-VP	O
थे	VAUX	I-VP	O
।	PUNC	O	O

# sentence 2
एसे	DEM	B-NP	O
ही	RP	I-NP	O
एक	QF	B-NP	O
फारसी	JJ	I-NP	B-LOC
मित्र	NN	I-NP	O
थे	VM	B-VP	O
जो	PRP	B-NP	O
की	CC	O	O
बहुत	INTF	B-ADJP	O
ही	RP	I-ADJP	O
विशाल	JJ	I-ADJP	O
साम्राज्य	NN	B-NP	O
के	PSP	B-PP	O
राजा	NN	B-NP	O
थे	VM	B-VP	O
।	PUNC	O	O

# sentence 3
बादशाह	NN	B-NP	O
और	CC	O	O
उनका	PRP	B-NP	O
मित्र	NN	I-NP	O
दोनों	NN	I-NP	O
एक	QF	B-NP	O
दुसरे	NN	I-NP	O
को	PSP	B-PP	O
अक्सर	RB	B-ADVP	O
पत्र	NN	B-NP	O
लिखा	VM	B-VP	O
करते	VAUX	I-VP	O
और	CC	O	O
एक	QF	B-NP	O
दुसरे	NN	I-NP	O
से	PSP	B-PP	O
मजाक	NN	B-NP	O
चलती	VM	B-VP	O
रहती	VAUX	I-VP	O
।	PUNC	O	O

# sentence 4
बादशाह	NN	B-NP	O
अक्सर	RB	B-ADVP	O
चुटकले	NN	B-NP	O
और	CC	O	O
शायरिया	NN	B-NP	O
लिखकर	VM	B-VP	O
भेजते	VM	I-VP	O
।	PUNC	O	O

# sentence 5
और	CC	O	O
फारसी	PROPN	B-NP	B-LOC
का	PSP	B-PP	O
राजा	NN	B-NP	O
उनको	PRON	B-NP	O
अक्सर	RB	B-ADVP	O
तोहफे	NN	B-NP	O
भेजा	VM	B-VP	O
करता	VAUX	I-VP	O
।	PUNC	O	O

# sentence 6
एक	QF	B-NP	O
दिन	NN	I-NP	O
फारसी	PROPN	B-NP	B-LOC
के	PSP	B-PP	O
राजा	NN	B-NP	O
ने	PSP	B-PP	O
एक	QF	B-NP	O
ऐसा	DEM	I-NP	O
तोह्फा	NN	I-NP	O
और	CC	O	O
पत्र	NN	B-NP	O
भेजा	VM	B-VP	O
जिसको	PRP	B-NP	O
देखकर	VM	B-VP	O
बादशाह	NN	B-NP	O
चौंक	VM	B-VP	O
गये	VAUX	I-VP	O
।	PUNC	O	O

# sentence 7
तोहफे	NN	B-NP	O
के	PSP	B-PP	O
अन्दर	NST	B-NP	O
से	PSP	B-PP	O
एक	QF	B-NP	O
पिंजरा	NN	I-NP	O
और	CC	O	O
एक	QF	B-NP	O
पत्र	NN	I-NP	O
निकला	VM	B-VP	O
।	PUNC	O	O

# sentence 8
पिंजरे	NN	B-NP	O
के	PSP	B-PP	O
अन्दर	NST	B-NP	O
एक	QF	B-NP	O
शेर	NN	I-NP	O
था	VM	B-VP	O
।	PUNC	O	O

# sentence 9
बादशाह	NN	B-NP	O
ने	PSP	B-PP	O
पत्र	NN	B-NP	O
खोलकर	VM	B-VP	O
देखा	VM	B-VP	O
तो	CC	O	O
उसके	PRP	B-NP	O
अन्दर	NST	B-NP	O
लिखा	VM	B-VP	O
था	VAUX	I-VP	O
की	CC	O	O
इस	DEM	B-NP	O
शेर	NN	I-NP	O
को	PSP	B-PP	O
कैसे	WQ	B-ADVP	O
भी	RP	I-ADVP	O
करके	VM	B-VP	O
बाहर	NST	B-ADVP	O
निकालना	VM	B-VP	O
हैं	VAUX	I-VP	O
और	CC	O	O
इस	DEM	B-NP	O
पिंजरे	NN	I-NP	O
को	PSP	B-PP	O
खोलना	VM	B-VP	O
भी	RP	O	O
नहीं	NEG	B-VP	O
हैं	VM	I-VP	O
।	PUNC	O	O

# sentence 10
और	CC	O	O
अगर	SCONJ	O	O
ऐसा	DEM	B-NP	O
नहीं	NEG	B-VP	O
किया	VM	I-VP	O
तो	CC	O	O
हम	PRP	B-NP	O
आपकी	PRP	B-NP	O
सल्तनत	NN	I-NP	O
पर	PSP	B-PP	O
हमला	NN	B-NP	O
करेंगे	VM	B-VP	O
।	PUNC	O	O

Now annotate the given sentences:

# sentence 101
बीरबल बेहद बुद्धिमान, हाजिर जवाब और शातिर दिमाग के थे

# sentence 102
बीरबल तुरंत समझ गये की बादशाह ने आत्मविश्वास की परख के लिए इस हाथी की जंजीरे खोल दी गयी हैं

# sentence 103
हाथी दौड़कर सुन्ड ऊँची करके बीरबल की तरफ आ रहा था

# sentence 104
बीरबल इसे स्थान पर खड़े थे कि भागकर भी नही बच सकते थे

# sentence 105
ठीक उसी समय बीरबल को कुत्ता दिखायी दिया

# sentence 106
हाथी इतना करीब आ गया कि बीरबल को सुन्ड में लपेट लेता

# sentence 107
तभी बीरबल ने कुत्ते की पिछली दोनों टांगो को पकडकर तेजी से हाथी पर फेंका

# sentence 108
कुत्ते की भयानक चिके सुनकर हाथी गबरा गया और भागने लगा

# sentence 109
अकबर को इस बात की खबर मिल गयी, और उनको यह मानना पड़ा की - वाकई संसार का सबसे बड़ा हथियार “आत्मविश्वास” हैं

# sentence 110
और बीरबल ने जो कुछ भी कहा वो सच हैं

# sentence 111
एक दिन अकबर और उसके दरबारी दरबार में बैठे थे

# sentence 112
तभी राजा सीलोन का दूत वहां आ पहुंचा

# sentence 113
वो किसी विशेष काम के लिए यहाँ पर आया था

# sentence 114
सलाम बादशाह

# sentence 115
मैं राजा सीलोन के दरबार से आया हूँ

# sentence 116
हमारी सल्तनत में आपका स्वागत हैं

# sentence 117
आपके दरबार में बहुत सारे बुद्धिमान दरबारी हैं और हमारे राजा ने समझदारी से भरे घड़े की गुजारिश की हैं

# sentence 118
कुछ दरबारी बोले - समझदारी से भरा हुआ घड़ा

# sentence 119
अब ये कहाँ से भरकर लायेंगे

# sentence 120
ये तो बहुत ही बेहूदा गुजारिश हैं

# sentence 121
(फुसफुसाते हुए) किसी मंत्री ने सलाह दी की बादशाह सिलोन के राजा हमे मात देना चाहते हैं

# sentence 122
और वो सफल भी हो जायेंगा

# sentence 123
कोई भी हमे नही बचा पायेंग

# sentence 124
यहाँ तक बीरबल भी

# sentence 125
ये तो बहुत मुश्किल गुजारिश की हैं सीलोन के राजा ने- अकबर ने कहा

# sentence 126
खैर तुम्हारा इसके बारे मे क्या कहना हैं बीरबल

# sentence 127
बीरबल बोले हाँ

# sentence 128
हम थोड़ी तो समझदारी तो भेज ही सकते हैं सीलोन के राजा के लिए

# sentence 129
आख़िरकार उन्होंने गुजारिश की हैं तो, हमको उमकी गुजारिश पूरी करनी चाहिए

# sentence 130
अकबर बोले - अगर तुम ऐसा कहते हो तो ठीक है, तुम जो भी करोगे ठीक ही करोगे

# sentence 131
मझे तुम पर पूरा यकीन हैं

# sentence 132
शुक्रिया जहापनाह

# sentence 133
मुझे घड़े को भरने के लिए कुछ हफ्तों की जरुरत पड़ेगी

# sentence 134
आप जितना चाहे वक्त ले सकते हैं- दूत ने कहा

# sentence 135
अकबर ने कहा बीरबल जरा ध्यान से क्योंकि तुमने जिस चुनोती को स्वीकार की हैं

# sentence 136
उस पर हमारी भी इज्जत दाव पर लगी हैं

# sentence 137
बीरबल ने कहा जहापनाह सब्र रखिये, सीलोन के राजा को समझदारी से भरा घड़ा जरूर मिलेगा

# sentence 138
उसी शाम को बीरबल ने अपने सहायक को बुलाया

# sentence 139
बीरबल के दिमाग में एक गजब की योजना चल रही थी

# sentence 140
बीरबल ने अपने सहायक से कहा की मुझे कुछ मिट्टी के घड़े चाहिए

# sentence 141
और ध्यान रहे उन घडो की गर्दन कुछ पतली रहे

# sentence 142
इतना कहकर बीरबल बगीचे में चले गये, और कुछ समय में सहायक भी मिट्टी के गड़े भी लेकर आ गया

# sentence 143
बीरबल ने उसको उन घडो को लेकर कह्द के क्यारी में आने को कहा

# sentence 144
बीरबल ने एक घड़ा माँगा और घड़े के चारों और लकड़ीयां को रस्सी से लपेटकर बांध दी

# sentence 145
बीरबल ने उन घडो को उल्टा करके कद्दू के फूल पर रख दिया

# sentence 146
इसी तरह सभी घडो को बांध कर उल्टा रख दिया

# sentence 147
सभी घडो को रखने के बाद बीरबल ने सहायक से बोला इन कह्द्‌ के बेलों को खाद पानी देते रहना

# sentence 148
और इसको किसी को छूने मत देना

# sentence 149
और किसी को बताना भी मत

# sentence 150
इतना कहकर बीरबल वहां से चल दिए

# sentence 151
माली सहायक ने उन कहुओ और घडो का खूब ख्याल रखा

# sentence 152
कुछ हफ्तों बाद अकबर ने बीरबल से पूछा

# sentence 153
बीरबल कुछ काम को आगे बढाया की नही

# sentence 154
तुम्हारी तरफ से कोई समाचार भी नही आया

# sentence 155
जहापनाह काम लगभग समाप्त हो ही गया - ऐसा बीरबल ने कहा

# sentence 156
मैं ये देखने के लिए बहुत ही उत्साहित हूँ - ऐसा बादशाह ने कहा

# sentence 157
लेकिन तुम घड़े को समझदारी से कैसे भरोगे

# sentence 158
अब मुझे दो हफ्ते और चाहिए

# sentence 159
फिर काम पूरा हो जायेंगा

# sentence 160
फीर हम सीलोन के दूत को बुला कर समझदारी के घड़े दे सकते हैं

# sentence 161
उम्मीद करता हूँ हमारी इज्जत पर कोई दाग नहीं लगेगा -अकबर ने कहा

# sentence 162
ऐसा बिकुल नहीं होगा जहापनाह - बीरबल ने कहा

# sentence 163
नज़र बीरबल पर थी

# sentence 164
सभी ये सोच रहे थे कि आखिर बीरबल ने क्या किया होगा

# sentence 165
समझदारी के घड़े को भरने के लिए

# sentence 166
कोई मंत्री बोल रहा था की मुझे नही लगता की बीरबल इस चुनौती को पूरा कर पाया होगा

# sentence 167
मुझे भी ऐसा ही लगता है

# sentence 168
ऐसा कर पाना किसी के लिए भी नामुमकिन हैं

# sentence 169
अरे वो बीरबल हैं

# sentence 170
जरूर उसने कोई न कोई रास्ता निकल ही दिया होगा - बुढा मंत्री बोला

# sentence 171
सभी इस चुनौती और इसके परिणाम के बारे में बातें कर रहे थे

# sentence 172
बीरबल और दूत दोनों दरबार में हाजिर होते हैं

# sentence 173
समझदारी से भरे घड़े को दिखाने के लिए क्या तुम तैयार हो बीरबल- बादशाह अकबर ने कहा

# sentence 174
जी हाँ जहापनाह - अकबर ने कहा

# sentence 175
बीरबल ने दो तली बजाई, सभी दरवाजे की तरफ देखते हैं

# sentence 176
बीरबल का सहायक घड़े को थाली में रखकर हाजिर होता हैं

# sentence 177
ये लीजिये जहापनाह आपके सामने समझदारी से भरा घड़ा हाजिर हैं

# sentence 178
घड़े को ऊपर से कपडे से ढका हुआ था ताकि कोई अन्दर से देख न सके की अन्दर क्या भरा हुआ था

# sentence 179
दरबारी चिल्लाने लगे - ऐसा कैसे हो सकता हैं, ऐसा हो ही नही सकता, ये नामुमकिन हैं

# sentence 180
शांत हो जाओ - अकबर ने कहा

# sentence 181
इस घड़े को तुम अपने राजा के पास ले जाओ

# sentence 182
लेकिन याद रहे तुम्हें ये सारे पड़े खाली करके लौटाने होंगे, वो भी बिना कोई नुकसान पहुंचाए

# sentence 183
और आप समझदारी के फल को बाहर निकालने चाहते हो तो उसे भी कोई खरोच नही आनी चाहिए

# sentence 184
क्या मैं इसे देख सकता हूँ- दूत ने कहा

# sentence 185
हा जरूर अब ये आपका ही हैं - बीरबल ने कहा

# sentence 186
दूत उस घड़े के अन्दर देखता हैं और चोंक जाता हैं

# sentence 187
उसने घड़े के अन्दर एक कह्दू देखा

# sentence 188
दूत कुछ बोले उसके पहले बीरबल बोले एसे हमारे पास पांच घड़े हैं

# sentence 189
अगर तुम्हारे राजा को और समझदारी चाहिए तो हम और दे देंगे

# sentence 190
तुम्हारे सामने कोई खड़ा हो सकता हैं भला

# sentence 191
तुम लाखो में एक हो बीरबल

# sentence 192
दूत घड़ा लेकर चला जाता हैं

# sentence 193
बीरबल मैं बहुत ज्यादा उत्साहित हूँ

# sentence 194
तुमने कहा तुम्हारे पास और पांच घड़े हैं जरा हमे भी दिखाओ - अकबर ने कहा

# sentence 195
बीरबल ने दूसरा घड़ा मंगाया

# sentence 196
सहायक दूसरा घड़ा भी ले आया

# sentence 197
अकबर देखकर जोर जोर से हंसने लगा

# sentence 198
बिलकुल

# sentence 199
यही हैं समझदारी का फल

# sentence 200
सीलोन के राजा देखकर जरूर समझदार बन जायेंगे

"""

if __name__ == "__main__":
    prompts = [
        ("prompt_1", prompt_text_1),
        ("prompt_2", prompt_text_2),
        ("prompt_3", prompt_text_3),
        ("prompt_4", prompt_text_4)
    ]
    
    for name, text in prompts:
        print(f"Annotating {name}...")
        try:
            response = get_llm_annotation(text)
            filename = f"{name}.conll"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(response)
            print(f"Saved to {filename}")
        except Exception as e:
            print(f"Error annotating {name}: {e}")
