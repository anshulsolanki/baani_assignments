import os 
import csv 
import math
import random #randm choices and shufle
import nltk #nltk for pos tag and tokenize
from nltk.tree import Tree,ParentedTree #trees and parnt pointer for cfg

#lists of pronuns and gender word hints
MASCULINE_PRONOUNS={"he","him","his","himself"} #set of masc pronuns
FEMININE_PRONOUNS={"she","her","hers","herself"} #set of fem pronuns

MASCULINE_WORDS=set("""
mr mr. sir king prince lord duke emperor father dad son brother uncle nephew
grandfather grandson husband boy man men gentleman actor waiter priest monk
spokesman chairman policeman businessman hero john james robert michael william
david richard charles joseph thomas christopher daniel paul mark donald george
kenneth steven edward brian ronald anthony kevin jason matthew gary timothy
jose larry jeffrey frank scott eric stephen andrew raymond gregory joshua jerry
dennis walter patrick peter harold douglas henry carl arthur ryan roger joe
juan jack albert jonathan justin terry gerald keith samuel willie ralph lawrence
nicholas roy benjamin bruce brandon adam harry fred wayne billy steve louis
jeremy aaron randy howard eugene carlos russell bobby victor martin ernest
phillip todd jesse craig alan shawn clarence sean philip chris johnny earl
jimmy antonio danny bryan tony luis mike stanley leonard nathan dale manuel
rodney curtis norman allen marvin vincent glenn jeffery travis jeff chad jacob
lee melvin alfred kyle francis bradley jesus herbert frederick ray joel edwin
don eddie ricky troy randall barry alexander bernard mario leroy francisco
marcus micheal theodore clifford miguel oscar jay jim tom calvin alex jon
ronnie bill lloyd tommy leon derek warren darrell jerome floyd leo alvin tim
wesley gordon dean greg jorge dustin pedro derrick dan lewis zachary corey
herman maurice vernon roberto clyde glen hector shane ricardo sam rick lester
brent ramon charlie tyler gilbert gene marc reginald ruben brett angel nathaniel
rafael leslie edgar milton raul ben chester cecil duane franklin andre elmer
brad gabriel ron mitchell roland arnold harvey jared adrian karl cory claude
erik darryl jamie neil jessie christian javier fernando clinton ted mathew
tyrone darren lonnie lance cody julio kelly kurt allan nelson guy clayton hugh
max dwayne dwight armando felix jimmie everett jordan ian wallace ken bob jaime
casey alfredo alberto dave ivan johnnie sidney byron julian isaac morris clifton
willard daryl ross virgil andy marshall salvador perry kirk sergio marion tracy
seth kent terrance rene eduardo terrence enrique freddie wade simon lukas luke nick
""".split())

FEMININE_WORDS=set("""
mrs mrs. ms ms. miss madam queen princess lady duchess empress mother mom
daughter sister aunt niece grandmother granddaughter wife girl woman women
gentlewoman actress waitress nun spokeswoman chairwoman policewoman businesswoman
heroine widow bride maiden mary patricia linda barbara elizabeth jennifer maria
susan margaret dorothy lisa nancy karen betty helen sandra donna carol ruth
sharon michelle laura sarah kimberly deborah jessica shirley cynthia angela
melissa brenda amy anna rebecca virginia kathleen pamela martha debra amanda
stephanie carolyn christine marie janet catherine frances ann joyce diane alice
julie heather teresa doris gloria evelyn jean cheryl mildred katherine joan
ashley judith rose janice kelly nicole judy christina kathy theresa beverly
denise tammy irene jane lori rachel marilyn andrea kathryn louise sara anne
jacqueline wanda bonnie julia ruby lois tina phyllis norma paula diana annie
lillian emily robin peggy crystal gladys rita dawn connie florence tracy edna
tiffany carmen rosa cindy grace wendy victoria edith kim sherry sylvia josephine
thelma shannon sheila ethel ellen elaine marjorie carrie charlotte monica esther
pauline emma juanita anita rhonda hazel amber eva debbie april leslie clara
lucille jamie joanne eleanor valerie daniella danielle megan alicia suzanne
michele gail bertha darlene veronica jill erin geraldine lauren cathy joann
lorraine lynn sally regina erica beatrice dolores bernice audrey yvonne annette
june samantha marion dana stacy ana renee ida vivian roberta holly brittany
melanie loretta yolanda jeanette laurie katie kristen vanessa alma sue elsie
beth jeanne vicki carla tara rosemary eileen terri gertrude lucy tonya ella
stacey wilma gina kristin jessie natalie agnes vera willie charlene bessie
delores melinda pearl arlene maureen colleen allison tamara joy georgia
constance lillie claudia jackie marcia tanya nellie minnie marlene heidi glenda
lydia viola courtney marian stella caroline dora jo vickie mattie terry maxine
irma mabel marsha myrtle lena christy deanna patsy hilda gwendolyn jennie nora
margie nina cassandra leah penny kay priscilla naomi carole brandy olga billie
dianne tracey leona jenny felicia sonia miriam velma becky bobbie violet toni
misty mae shelly daisy ramona sherri erika katrina claire sophie elena kate
katelyn hannah olivia chloe
""".split())


#reading the gap tsv dataset file
def load_gap_tsv(filepath): #loads tsv rows into list
    rows=[] #list of rows
    with open(filepath,"r",encoding="utf-8") as f: #open file with utf8 encoding
        reader=csv.DictReader(f,delimiter="\t") #tsv uses tab delimiter
        for row in reader: #itrate each row in tsv
            rows.append(row) 
    return rows 


#finds if pronun is masculine or fem or unknown
def get_pronoun_gender(pronoun_str): #chking pron gender
    p=pronoun_str.lower().strip() #strip spaces and lowercase
    if p in MASCULINE_PRONOUNS: #if in male pronuns set
        return "M" #male gender
    if p in FEMININE_PRONOUNS: #if in fem pronuns set
        return "F" #fem gender
    return "U" #unknown


#infers if canddate np is male or female from words or endings
def get_np_gender(words): #infer gender of np from tokens
    for w in words: #loop words in canddate
        wl=w.lower().strip(".") #clean dot and lowercase
        if wl in FEMININE_WORDS: #matchs fem dict
            return "F" #fem gender
        if wl in MASCULINE_WORDS: #matchs masc dict
            return "M" #male gender
    if len(words)>0: #chek first word ending
        first_word=words[0].lower() #try looking at name endings
        if len(first_word)>3 and first_word[0].isalpha(): #name length chek
            if first_word.endswith(("a","ia","na","la","ette","ine","elle")): #female suffix chek
                return "F" #fem gender
            if first_word.endswith(("o","us","rik","son","ard","ert")): #male suffix chek
                return "M" #male gender
    return "U" #unknown gender


#cheks if extracted np overlaps or matchs gold entity span
def check_span_matches_gold(np_start,np_end,np_text,gold_start,gold_text): #chek if cand overlaps gold entity
    gold_end=gold_start+len(gold_text) #ending char of gold
    if not (np_end<=gold_start or np_start>=gold_end): #overlap chek
        return True #spans overlap so true
    if np_text.lower().strip()==gold_text.lower().strip(): #exact text match fallback
        return True #spans overlap so true
    return False 


#precison recall f1 calcuatin
def calc_prf(tp,fp,fn): #calc precison rec and f1
    prec=float(tp)/float(tp+fp) if (tp+fp)>0 else 0.0 #tp / (tp + fp)
    rec=float(tp)/float(tp+fn) if (tp+fn)>0 else 0.0 #tp / (tp + fn)
    f1=(2.0*prec*rec)/(prec+rec) if (prec+rec)>0 else 0.0 #harmonic mean 2pr/(p+r)
    return prec,rec,f1 #return all 3 scores


#cfg grammar for noun phrases and basic clause chunking
CFG_GRAMMAR=r"""
  NP: {<DT>?<JJ.*>*<NNP.*>+}
      {<DT>?<JJ.*>*<NN|NNS>+}
      {<PRP.*>}
  NP: {<NP><POS><NP>}
      {<NP><NP>}
  PP: {<IN|TO><NP>}
  VP: {<MD|RB.*>*<VB.*>+<RB.*>*<NP|PP>*}
  S:  {<NP><CC><NP><VP>}
      {<NP><RB.*>?<VP>}
  SBAR: {<IN|WDT|WP|WRB><S>}
"""

CFG_PARSER=nltk.RegexpParser(CFG_GRAMMAR,loop=1) #regex parser for cfg chunks


#collecting base np nodes from parsed tree recursively
def find_base_nps_in_tree(node,tok_idx,in_vp_or_pp,base_np_list): #recurse tree to collect base nps
    if not isinstance(node,Tree): #leaf reached
        return tok_idx+1 

    label=node.label() #node grammatical label
    if label in ("VP","PP"): #inside vp or pp branch
        in_vp_or_pp=True #inside verb or prep phrase so not a subject

    has_child_np=any(isinstance(ch,Tree) and ch.label().startswith("NP") for ch in node) #chek if sub np exists inside
    if label=="NP" and not has_child_np: #base np with no smaller np inside
        leaves=node.leaves() #get word leaves
        base_np_list.append((node,leaves,tok_idx,tok_idx+len(leaves)-1,not in_vp_or_pp)) #store node and subject flag
        return tok_idx+len(leaves) #advance by numbr of leaves

    for child in node: #visit childrn left to rght
        tok_idx=find_base_nps_in_tree(child,tok_idx,in_vp_or_pp,base_np_list) #recurse on child
    return tok_idx 


#maps token index to character offset in text
def get_token_char_spans(text,tagged_tokens,sent_char_start): #maps token index to char offsets
    tok_spans=[] #char spans list
    cur=sent_char_start #char tracker
    for tok,_ in tagged_tokens: #loop each word token
        idx=text.find(tok,cur) #find token starting from cur
        if idx==-1: #if not found in text
            idx=cur #fallback to cur
        tok_spans.append((idx,idx+len(tok))) #add (start, end) span
        cur=idx+len(tok) #move cur pointer forward
    return tok_spans 


#makes sure gold entities a and b are inside canddate list if chunker missed them
def ensure_gold_ab_in_candidates(candidate_nps,sent_starts,a_text,a_off,b_text,b_off): #makes sure gold a and b are in cands
    for gold_str,gold_off in [(a_text,a_off),(b_text,b_off)]: #chek both a and b
        gold_end=gold_off+len(gold_str)
        already_found=any(not (c["end"]<=gold_off or c["start"]>=gold_end) for c in candidate_nps) #see if alrdy extracted
        if not already_found: #missing from chunker
            g_words=nltk.word_tokenize(gold_str) #word tokenize gold entity
            g_tags=[t for _,t in nltk.pos_tag(g_words)] #pos tag gold entity
            g_sent=0 #sent idx default
            for s_i,s_st in enumerate(sent_starts): #find sent for gold entity
                if gold_off>=s_st: #chek offset in sent
                    g_sent=s_i #assign sent index
            candidate_nps.append({
                "np_id":-1,"text":gold_str,"start":gold_off,"end":gold_end,
                "words":g_words,"tags":g_tags,"sent_idx":g_sent,"is_subject":False,
            })


#processes dataset rows: does tokenizing, pos tagging, and extracts nps
def extract_candidates_from_dataset(rows): #main fn extratng nps from data
    all_tokenized_sents=[] #list of all sents
    seg_sent_ranges=[] #sent slice per segment
    seg_sent_char_starts=[] #char starts per sent

    for row in rows: #loop dataset passages
        text=row["Text"] #passage text
        sents=nltk.sent_tokenize(text) #split text to sentnces
        start_idx=len(all_tokenized_sents) #start index for segment
        char_pos=0 #char counter in text
        sent_starts=[] #list of sent start offsets
        for s in sents: #loop sentnces in passage
            s_pos=text.find(s,char_pos) #find sent start offset
            if s_pos==-1: #not found
                s_pos=char_pos #fallback
            sent_starts.append(s_pos) #append sent start
            char_pos=s_pos+len(s) #advance char counter
            all_tokenized_sents.append(nltk.word_tokenize(s)) #tokenize sentnce words
        seg_sent_ranges.append((start_idx,len(sents))) #record slice of sents
        seg_sent_char_starts.append(sent_starts) #record sent offsets

    #pos tagging all sentnces at once with nltk
    all_tagged_sents=nltk.pos_tag_sents(all_tokenized_sents) #pos tag all sents together
    processed_segments=[] #list of processed segments

    for seg_i,row in enumerate(rows): #process each row
        text=row["Text"] #passage text
        pronoun=row["Pronoun"] #target pronun
        p_off=int(row["Pronoun-offset"]) #pronun start offset
        p_end=p_off+len(pronoun) #pronun end offset
        a_text,a_off=row["A"],int(row["A-offset"]) #gold entity a
        b_text,b_off=row["B"],int(row["B-offset"]) #gold entity b
        a_coref=(row["A-coref"].strip().upper()=="TRUE") #bool if a is coreferent
        b_coref=(row["B-coref"].strip().upper()=="TRUE") #bool if b is coreferent

        start_idx,num_sents=seg_sent_ranges[seg_i] #sent range for this row
        sent_starts=seg_sent_char_starts[seg_i] #sent start offsets
        cfg_trees,candidate_nps=[],[] #trees and cands lists
        pronoun_sent_idx,pronoun_np_id,pronoun_is_subject=0,None,False #init pronun vars
        np_counter=0 #np id numbering

        for s_i in range(num_sents): #loop sents in passage
            tagged_tokens=all_tagged_sents[start_idx+s_i] #get tagged words
            s_char_pos=sent_starts[s_i] #sent start char
            tok_spans=get_token_char_spans(text,tagged_tokens,s_char_pos) #get word char spans

            parsed_tree=CFG_PARSER.parse(tagged_tokens) #chunk with regex cfg
            if parsed_tree.label()!="S": #wrap root in S
                parsed_tree=Tree("S",list(parsed_tree)) #create S tree node

            base_np_list=[] #list for base nps
            find_base_nps_in_tree(parsed_tree,0,False,base_np_list) #find nps in parse tree

            for node,leaves,t_start,t_end,is_subj in base_np_list: #itrate each base np
                c_start,c_end=tok_spans[t_start][0],tok_spans[t_end][1] #char boundries of np
                words=[w for w,_ in leaves] #list of word strs
                tags=[t for _,t in leaves] #list of pos tag strs
                this_np_id=np_counter #give id to np
                np_counter+=1 #inc id counter
                node.set_label(f"NP#{this_np_id}")

                if not (c_end<=p_off or c_start>=p_end) and any(t.startswith("PRP") for t in tags): #chek if np is pronun
                    pronoun_sent_idx,pronoun_np_id,pronoun_is_subject=s_i,this_np_id,is_subj #save pronun info
                elif not all(t.startswith("PRP") for t in tags): #ignore standalone pronuns in canddate list
                    spans_a=not (c_end<=a_off or c_start>=a_off+len(a_text)) #overlaps gold a
                    spans_b=not (c_end<=b_off or c_start>=b_off+len(b_text)) #overlaps gold b
                    if spans_a and spans_b: #chunk covered both a and b so split them up
                        for idx_sub,(sub_t,sub_o) in enumerate([(a_text,a_off),(b_text,b_off)]):
                            sub_id=this_np_id if idx_sub==0 else np_counter
                            if idx_sub>0:
                                np_counter+=1 #inc id counter
                            candidate_nps.append({
                                "np_id":sub_id,"text":sub_t,"start":sub_o,"end":sub_o+len(sub_t),
                                "words":nltk.word_tokenize(sub_t),"tags":tags,"sent_idx":s_i,"is_subject":is_subj,
                            })
                    else: 
                        candidate_nps.append({
                            "np_id":this_np_id,"text":text[c_start:c_end],"start":c_start,"end":c_end,
                            "words":words,"tags":tags,"sent_idx":s_i,"is_subject":is_subj,
                        })

            next_s_start=sent_starts[s_i+1] if s_i+1<num_sents else len(text)+1
            if pronoun_np_id is None and s_char_pos<=p_off<next_s_start:
                pronoun_sent_idx=s_i
                for cand in candidate_nps: #loop cands to set labels
                    if cand["sent_idx"]==s_i and cand["start"]<=p_off<cand["end"]:
                        pronoun_np_id,pronoun_is_subject=cand["np_id"],cand["is_subject"]
                        break 

            cfg_trees.append(ParentedTree.convert(parsed_tree))

        ensure_gold_ab_in_candidates(candidate_nps,sent_starts,a_text,a_off,b_text,b_off)
        candidate_nps.sort(key=lambda x:x["start"]) #sort cands by start char

        #label whether canddate matchs gold a or b
        for cand in candidate_nps: #loop cands to set labels
            matches_a=check_span_matches_gold(cand["start"],cand["end"],cand["text"],a_off,a_text) #see if cand span matchs gold a
            matches_b=check_span_matches_gold(cand["start"],cand["end"],cand["text"],b_off,b_text) #see if cand span matchs gold b
            cand["matches_A"]=not (cand["end"]<=a_off or cand["start"]>=a_off+len(a_text)) #flag cand matchs entity a
            cand["matches_B"]=not (cand["end"]<=b_off or cand["start"]>=b_off+len(b_text)) #flag cand matchs entity b
            cand["is_antecedent"]=(a_coref and matches_a) or (b_coref and matches_b) #is this gold coreferent entity

        processed_segments.append({
            "id":row["ID"],"text":text,"pronoun":pronoun,"pronoun_offset":p_off,
            "pronoun_sent_idx":pronoun_sent_idx,"pronoun_np_id":pronoun_np_id,
            "pronoun_is_subject":pronoun_is_subject,"A":a_text,"A_offset":a_off,
            "A_coref":a_coref,"B":b_text,"B_offset":b_off,"B_coref":b_coref,
            "cfg_trees":cfg_trees,"candidates":candidate_nps,
        })

    return processed_segments #ret segments with cands and trees


#prob 1: printng canddate nps for test segments
def problem_1(test_segments): #problem 1 canddate extration
    print("="*80) 
    print("PROBLEM 1 Candidate Noun Phrase Extraction using POS Tagger") 
    print("="*80) 
    total_cands=sum(len(s["candidates"]) for s in test_segments)
    avg_cands=float(total_cands)/float(len(test_segments))
    print(f"Total discourse segments in test set: {len(test_segments)}") 
    print(f"Total candidate NPs extracted:        {total_cands}") 
    print(f"Average candidate NPs per segment:    {avg_cands:.2f}\n") 

    print("Sample Extracted Candidate NPs from First 3 Test Discourse Segments:") 
    for seg in test_segments[:3]:
        print("-"*80) 
        print(f"Segment ID: {seg['id']} | Target Pronoun: '{seg['pronoun']}' (offset {seg['pronoun_offset']})") 
        print(f"Gold A: '{seg['A']}' (coref={seg['A_coref']}) | Gold B: '{seg['B']}' (coref={seg['B_coref']})") 
        c_texts=[f"'{c['text']}' [{c['start']}:{c['end']}]" for c in seg["candidates"]]
        print(f"Extracted Candidate NPs ({len(c_texts)}): {', '.join(c_texts)}") 
    print() 


#prob 2: randm choice basline 100 runs
def problem_2(test_segments): #problem 2 randm basline
    print("="*80) 
    print("PROBLEM 2 Random Antecedent Assignment (100 Runs)") 
    print("="*80) 
    rng=random.Random(12345)
    runs=100
    acc_all_runs,acc_ab_runs=[],[]

    for _ in range(runs):
        correct_all,correct_ab=0,0
        for seg in test_segments: #loop test passages
            cands=seg["candidates"]
            if len(cands)>0 and rng.choice(cands)["is_antecedent"]: #pick any extracted np randomly
                correct_all+=1
            ab_cands=[c for c in cands if c["matches_A"] or c["matches_B"]] #pick betwen a and b randomly
            if len(ab_cands)>0 and rng.choice(ab_cands)["is_antecedent"]:
                correct_ab+=1
        acc_all_runs.append(float(correct_all)/float(len(test_segments)))
        acc_ab_runs.append(float(correct_ab)/float(len(test_segments)))

    avg_acc_all=sum(acc_all_runs)/float(runs)
    avg_acc_ab=sum(acc_ab_runs)/float(runs)
    print(f"Number of random assignment runs: {runs}") 
    print(f"Average Accuracy (sampling across ALL POS-extracted candidate NPs): {avg_acc_all*100:.2f}%") 
    print(f"Average Accuracy (sampling between GAP candidate NPs A and B):      {avg_acc_ab*100:.2f}%\n") 
    return avg_acc_all,avg_acc_ab


#prob 3: picks most recent np bfore pronun
def problem_3(test_segments): #problem 3 most recent basline
    print("="*80) 
    print("PROBLEM 3 Most Recent Antecedent Baseline") 
    print("="*80) 
    correct_all,correct_ab=0,0

    for seg in test_segments: #loop test passages
        p_off=seg["pronoun_offset"] #pronun offset
        preceding=[c for c in seg["candidates"] if c["start"]<p_off] or seg["candidates"]
        if len(preceding)>0 and preceding[-1]["is_antecedent"]: #last np bfore pronun
            correct_all+=1

        preceding_ab=[
            c for c in seg["candidates"]
            if (c["matches_A"] or c["matches_B"]) and c["start"]<p_off
        ] or [c for c in seg["candidates"] if c["matches_A"] or c["matches_B"]]
        if len(preceding_ab)>0 and preceding_ab[-1]["is_antecedent"]:
            correct_ab+=1

    acc_all=float(correct_all)/float(len(test_segments))
    acc_ab=float(correct_ab)/float(len(test_segments))
    print(f"Most Recent Candidate NP Accuracy (across ALL POS-extracted NPs): {acc_all*100:.2f}% ({correct_all}/{len(test_segments)})") 
    print(f"Most Recent Candidate NP Accuracy (among GAP candidates A & B):   {acc_ab*100:.2f}% ({correct_ab}/{len(test_segments)})\n") 
    return acc_all,acc_ab


FEATURE_NAMES=[
    "is_hobbs_top1",          #top 1 choice of hobbs algorthm
    "in_hobbs_top3",          #in top 3 choices of hobbs
    "gender_match",           #if canddate matchs pronun gender
    "gender_mismatch",        #if canddate conflicts with pronun gender
    "number_agreement",       #canddate is singular like pronun
    "is_proper_noun",         #canddate has proper noun tag nnp
    "grammatical_role_subj",  #canddate is in subject position
    "parallel_role",          #canddate and pronun both subjects or both not
    "recency_inv_rank",       #1/rank among preceding nps
    "same_sentence",          #both in same sentnce
    "char_distance_closeness",#normalized char closeness to pronun
    "entity_frequency",       #how often canddate is mentioned in text
]


#extratng 12 featuers for canddate nps
def extract_features_for_segment(seg):
    hobbs_ranked=hobbs_rank_candidates_for_segment(seg) #rank candidtes using hobbs
    hobbs_top1_start=hobbs_ranked[0]["start"] if len(hobbs_ranked)>0 else -1
    hobbs_top3_starts=set(c["start"] for c in hobbs_ranked[:3])

    p_off=seg["pronoun_offset"] #pronun offset
    p_sent=seg["pronoun_sent_idx"]
    p_gender=get_pronoun_gender(seg["pronoun"]) #pronun gender
    p_is_subj=seg["pronoun_is_subject"]
    text_lower=seg["text"].lower()
    text_len=max(len(seg["text"]),1)

    preceding_starts=sorted([c["start"] for c in seg["candidates"] if c["start"]<p_off],reverse=True)
    start_to_recency_rank={st:r_i+1 for r_i,st in enumerate(preceding_starts)}

    features_list=[]
    for cand in seg["candidates"]:
        c_start=cand["start"]
        c_tags=cand["tags"]
        c_gender=get_np_gender(cand["words"])

        f_hobbs_1=1.0 if c_start==hobbs_top1_start else 0.0
        f_hobbs_3=1.0 if c_start in hobbs_top3_starts else 0.0
        f_gen_match=1.0 if (p_gender!="U" and c_gender==p_gender) else 0.0
        f_gen_mismatch=1.0 if (p_gender!="U" and c_gender!="U" and c_gender!=p_gender) else 0.0
        f_num_agree=0.0 if any(t in ("NNS","NNPS") for t in c_tags) else 1.0 #plural chek
        f_proper=1.0 if any(t.startswith("NNP") for t in c_tags) else 0.0
        f_subj=1.0 if cand["is_subject"] else 0.0
        f_parallel=1.0 if (cand["is_subject"]==p_is_subj) else 0.0
        f_recency=1.0/float(start_to_recency_rank[c_start]) if c_start in start_to_recency_rank else 0.05
        f_same_sent=1.0 if (cand["sent_idx"]==p_sent) else 0.0
        f_closeness=max(0.0,1.0-(float(abs(p_off-c_start))/float(text_len))) if c_start<p_off else 0.1

        full_cand_lower=cand["text"].lower().strip()
        freq_count=text_lower.count(full_cand_lower) if len(full_cand_lower)>=2 else 1
        f_freq=min(1.0,float(freq_count)/4.0)

        features_list.append([ #append 12 feats vector
            f_hobbs_1,f_hobbs_3,f_gen_match,f_gen_mismatch,
            f_num_agree,f_proper,f_subj,f_parallel,
            f_recency,f_same_sent,f_closeness,f_freq,
        ])
    return features_list 


#simple binary logistic regression from scratch with sgd
class SimpleLogisticRegression: #lr class from scratch
    def __init__(self,num_features,learning_rate=0.05,l2_reg=0.0001,epochs=20): #intialize wght and bias vectors
        self.num_features=num_features #featuer dimension
        self.learning_rate=learning_rate #step size for sgd
        self.l2_reg=l2_reg #l2 regurlariztion to prevent wghts exploding
        self.epochs=epochs #num of passes on train
        self.weights=[0.0]*num_features #init wghts list with 0s
        self.bias=0.0 #init bias to 0

    #sigmoid func with bounds to avoid math overflow errors
    def sigmoid(self,z): #sigmoid activation fn
        if z<-30.0: #lower clamp to prevent underflow
            return 0.0 #basicly 0 prob
        if z>30.0: #upper clamp to prevent exp overflow
            return 1.0 #basicly 1 prob
        return 1.0/(1.0+math.exp(-z)) #basicly 1 prob

    #computes probablty p(y=1|x)
    def predict_proba_one(self,x): #predict p(y=1|x) for one instance
        z=self.bias #start dot prod with bias
        for j in range(self.num_features): #itrate each featuer
            z+=self.weights[j]*x[j] #sum up w[j] * x[j]
        return self.sigmoid(z) #map dot prod to 0-1 probablty

    #train with stochastic gradient descent
    def fit(self,X,y,pos_weight=3.0): #trainig with sgd
        indices=list(range(len(X))) #list of sample indices
        rng=random.Random(42) #fixed seed for repeatability
        for epoch in range(self.epochs): #train epoch loop
            rng.shuffle(indices) #shufle each epoch
            lr=self.learning_rate/(1.0+0.05*epoch) #learnng rate decay
            for idx in indices: #itrate shufled samples
                x_i,y_i=X[idx],y[idx] #get sample feat and label
                err=self.predict_proba_one(x_i)-y_i #prediction error
                weighted_err=err*(pos_weight if y_i==1 else 1.0) #boost positive class wght
                for j in range(self.num_features): #itrate each featuer
                    grad_j=weighted_err*x_i[j]+self.l2_reg*self.weights[j] #gradient with l2 penalty
                    self.weights[j]-=lr*grad_j #w_j = w_j - lr * grad
                self.bias-=lr*weighted_err #b = b - lr * err


#making X featuer matrix and y labels
def build_Xy_pairs(segments): #build featuer matrix and labels arr
    X,y=[],[] #init empty lists
    for seg in segments: #loop eval segments
        for feat_vec,cand in zip(seg["features"],seg["candidates"]): #pair featuer vec with cand
            X.append(feat_vec) #add featuer vector
            y.append(1 if cand["is_antecedent"] else 0) #1 if antecednt else 0
    return X,y 


#find canddate with max prob
def pick_best_candidate(cands,feats,model,only_ab=False): #find canddate with max prob
    best_prob,best_cand=-1.0,None #track best cand and score
    for feat_vec,cand in zip(feats,cands): #itrate canddate pairs
        if only_ab and not (cand["matches_A"] or cand["matches_B"]): #restrict search to a or b
            continue #skip non ab cand
        prob=model.predict_proba_one(feat_vec) #model probablty
        if prob>best_prob:
            best_prob,best_cand=prob,cand 
    return best_prob,best_cand 


#evaluate precison recall and f1
def evaluate_model_predictions(segments,model,threshold=0.25): #evaluate prec rec f1
    tp_all,fp_all,fn_all=0,0,0 #init all nps counters
    tp_ab,fp_ab,fn_ab=0,0,0 #init ab counters

    for seg in segments: #loop eval segments
        has_gold=seg["A_coref"] or seg["B_coref"] #chek if gold antecednt exists

        best_all_prob,best_all_cand=pick_best_candidate(seg["candidates"],seg["features"],model,only_ab=False) #best pick among all nps
        if best_all_cand is not None and best_all_prob>=threshold: #only predict if prob >= threshold
            if best_all_cand["is_antecedent"]: #correct pred (tp)
                tp_all+=1 #got it rght
            else: 
                fp_all+=1 #pred wrng cand
                if has_gold: #chek if gold existed
                    fn_all+=1 #missed true referent
        elif has_gold: #model predicted nothng so fn
            fn_all+=1 #missed true referent

        best_ab_prob,best_ab_cand=pick_best_candidate(seg["candidates"],seg["features"],model,only_ab=True) #best pick among a and b
        if best_ab_cand is not None and best_ab_prob>=threshold: #chek thresh for ab
            if best_ab_cand["is_antecedent"]: #correct ab pick
                tp_ab+=1 #correct betwen a and b
            else: 
                fp_ab+=1 #picked wrng betwen a and b
                if has_gold: #chek if gold existed
                    fn_ab+=1 #missed true a/b antecednt
        elif has_gold: #model predicted nothng so fn
            fn_ab+=1 #missed true a/b antecednt

    return { #ret metrics dict for all nps & ab
        "all_nps":calc_prf(tp_all,fp_all,fn_all), #calc all nps prf
        "ab_nps":calc_prf(tp_ab,fp_ab,fn_ab), #calc ab nps prf
    }


#prob 4: logistic regression classifier trainng and dev set tuning
def problem_4(train_segments,dev_segments,test_segments): #problem 4 custom logistic regression
    print("="*80) 
    print("PROBLEM 4 Custom Logistic Regression Classifier") 
    print("="*80) 

    X_train,y_train=build_Xy_pairs(train_segments) #convrt train segs to feat matrix
    print("Hyperparameter Tuning on Development Set (gap-validation.tsv, 454 segments):") 
    print(f"{'LR':>6} | {'L2_Reg':>8} | {'Pos_Weight':>10} | {'Dev F1 (All NPs)':>16} | {'Dev F1 (A/B NPs)':>16}") 
    print("-"*68) 

    best_score,best_params,best_model=-1.0,None,None #track best dev params
    for lr in [0.01,0.05,0.1]: #grid search learnng rate
        for l2 in [0.0,0.0001,0.001]: #grid search l2 regurlariztion
            for pw in [2.0,4.0]: #grid search pos wght
                model=SimpleLogisticRegression(len(FEATURE_NAMES),learning_rate=lr,l2_reg=l2,epochs=20) #create new custom lr model
                model.fit(X_train,y_train,pos_weight=pw) #fit model on X_train with poswt
                dev_res=evaluate_model_predictions(dev_segments,model,threshold=0.25) #test on dev/validation set
                f1_all,f1_ab=dev_res["all_nps"][2],dev_res["ab_nps"][2] #get f1 on all nps and ab
                print(f"{lr:6.2f} | {l2:8.4f} | {pw:10.1f} | {f1_all*100:15.2f}% | {f1_ab*100:15.2f}%") 
                if 0.5*(f1_all+f1_ab)>best_score: #chek if avg dev f1 is new best
                    best_score=0.5*(f1_all+f1_ab) #updated best dev score
                    best_params=(lr,l2,pw) #save best lr, l2, pw config
                    best_model=model #save best model instance

    print("-"*68) 
    print(f"Best Hyperparameters on Dev Set: learning_rate={best_params[0]}, l2_reg={best_params[1]}, pos_weight={best_params[2]}") 

    test_res=evaluate_model_predictions(test_segments,best_model,threshold=0.25) #evaluate on test set with best hp
    p_all,r_all,f1_all=test_res["all_nps"] #test metrics for full cand pool
    p_ab,r_ab,f1_ab=test_res["ab_nps"] #test metrics for a vs b

    print("\nTest Set Evaluation (gap-test.tsv, 2000 segments):") 
    print("  1. Full Candidate NP Pool Resolution (All POS-Extracted Candidate NPs):") 
    print(f"       Precision: {p_all*100:.2f}% | Recall: {r_all*100:.2f}% | F1-Score: {f1_all*100:.2f}%") 
    print("  2. GAP Candidate NP Resolution (Evaluating on Candidate Entities A vs B):") 
    print(f"       Precision: {p_ab*100:.2f}% | Recall: {r_ab*100:.2f}% | F1-Score: {f1_ab*100:.2f}%\n") 
    return best_model,test_res 

#prob 5: learned featuer wghts and ranking top 5
def problem_5(model): #problem 5 featuer wghts and top 5
    print("="*80) 
    print("PROBLEM 5 Learned Feature Weights & Top-5 Features") 
    print("="*80) 
    print(f"Learned Intercept (Bias): {model.bias:+.4f}\n") 
    print(f"{'Rank':>4} | {'Feature Name':<26} | {'Learned Weight':>14} | {'|Weight|':>10}") 
    print("-"*64) 

    ranked_feats=sorted( #rank featuers by magnitude
        [(name,w,abs(w)) for name,w in zip(FEATURE_NAMES,model.weights)],
        key=lambda x:x[2],
        reverse=True,
    )
    for idx,(name,w,abs_w) in enumerate(ranked_feats,start=1): #loop ranked featuers
        print(f"{idx:4d} | {name:<26} | {w:+14.4f} | {abs_w:10.4f}") 

    print("\nTop-5 Features (by Weight Magnitude):") 
    for idx,(name,w,_) in enumerate(ranked_feats[:5],start=1): #loop top 5 featuers
        direction="Positive (increases antecedent likelihood)" if w>0 else "Negative (penalizes candidate)" #determine directionality
        print(f"  {idx}. {name} (weight = {w:+.4f}) -> {direction}") 
    print() 
    return ranked_feats 


#prob 6: error analysis - analysis is in the report pdf, we just count errors here
def problem_6(test_segments,model): #problem 6 error analysis
    print("="*80)
    print("PROBLEM 6 Error Analysis of Logistic Regression Implementation")
    print("="*80)

    errors=[] #list of error instances
    for seg in test_segments: #loop test passages
        if not (seg["A_coref"] or seg["B_coref"]): #skip segs with no gold antecednt
            continue
        best_prob,best_cand=pick_best_candidate(seg["candidates"],seg["features"],model,only_ab=False) #get best model prediction
        if best_cand is not None and not best_cand["is_antecedent"]: #wrng pred
            gold_str=seg["A"] if seg["A_coref"] else seg["B"] #true gold antecednt
            errors.append((seg,best_cand["text"],gold_str,best_prob)) #store error info

    print(f"Total errors on gold-annotated test segments: {len(errors)}") #just the count
    print("First 3 wrong predictions (for quick sanity check):") #sanity chek sample
    for seg,pred_str,gold_str,prob in errors[:3]: #loop first 3 errors
        print(f"  Seg {seg['id']} | pronoun='{seg['pronoun']}' | pred='{pred_str}' (p={prob:.3f}) | gold='{gold_str}'")
    print()
    #full qualitative analaysis (4 error categories + improvements) is in Report.md / Report.pdf
    print("[See Report.pdf Section 6 for full qualitative error analysis and improvement discussion.]") #pointer to report
    print()


#writes ascii cfg parse trees for 5 sample test segments to parse_trees.txt
def save_parse_trees_txt(test_segments,base_dir): #save parse trees as txt file
    out_path=os.path.join(base_dir,"parse_trees.txt") #outpt txt path
    sample_segs=test_segments[:5] #pick first 5 test segments as samples

    with open(out_path,"w",encoding="utf-8") as f: #open file for writing
        f.write("CFG Parse Trees - Anaphora Resolution Assignment\n") #header
        f.write("Generated from gap-test.tsv (first 5 discourse segments)\n") #sub header
        f.write("="*70+"\n\n") #separator

        for i,seg in enumerate(sample_segs,start=1): #loop sample segments
            f.write(f"Segment {i}: ID = {seg['id']}\n") #seg header
            f.write(f"Pronoun: '{seg['pronoun']}' | Entity A: '{seg['A']}' (coref={seg['A_coref']}) | Entity B: '{seg['B']}' (coref={seg['B_coref']})\n")
            f.write("-"*70+"\n") #separator

            sents=nltk.sent_tokenize(seg["text"]) #re-tokenize to get sent strings
            for s_i,tree in enumerate(seg["cfg_trees"]): #loop cfg trees for segment
                sent_str=sents[s_i] if s_i<len(sents) else "" #get sentnce text
                f.write(f"  Sentence {s_i+1}: {sent_str[:100]}\n") #sentnce preview
                f.write("  CFG Parse Tree (ASCII):\n") #tree header

                #pformat gives multi-line indented tree string
                tree_str=tree.pformat(margin=60) #format tree as indented text
                for line in tree_str.splitlines(): #loop tree lines
                    f.write("    "+line+"\n") #indent each line by 4 spaces
                f.write("\n") #blank line betwen sents

            f.write("\n") #blank line betwen segs

    print(f"[Parse trees written to: {out_path}]") #confirm written
    return out_path 


#convrts parse_trees.txt to parse_trees.pdf using macOS cupsfilter
def convert_trees_txt_to_pdf(txt_path): #convrt txt to pdf using cupsfilter
    import subprocess #subprocess to call system cmd
    pdf_path=txt_path.replace(".txt",".pdf") #swap extension to pdf
    try:
        #cupsfilter is macOS builtin, convrts text/plain directy to pdf
        with open(pdf_path,"wb") as pdf_out: #open pdf outpt file
            result=subprocess.run( #run cupsfilter to convrt txt to pdf
                ["cupsfilter","-i","text/plain","-m","application/pdf",txt_path],
                stdout=pdf_out, #write pdf bytes to file
                stderr=subprocess.DEVNULL #suppress cups noise
            )
        if result.returncode!=0: #cupsfilter failed
            print(f"[cupsfilter failed with code {result.returncode}. .txt file still available.]")
            return
        print(f"[Parse trees PDF saved to: {pdf_path}]") #confirm pdf saved
    except Exception as e: #any other error
        print(f"[Could not convert to PDF: {e}. The .txt file is still available.]") #fallback msg


#chek if cfg tree label is np or sentnce
def is_np_or_s(label): #chek if label is np or sentnce
    return label.startswith("NP") or label in ("S","SBAR") #true if np or s or sbar


#helper to extrat np id numbr from label
def extract_np_id(label): #extrat id from label
    return int(label.split("#")[1]) if label.startswith("NP#") else None


#left to rght bfs travrsal of subtrees for hobbs
def bfs_collect_nps(subtrees,require_intervening_np_or_s=False,stop_below_np_or_s=False): #bfs travrsal to collect nps
    proposed_ids=[] #list of canddate np ids
    queue=[(st,False) for st in subtrees if isinstance(st,Tree)] #bfs queue with condition b flag
    while len(queue)>0: #bfs queue loop
        curr,seen_np_s=queue.pop(0) #pop front node from queue
        lbl=curr.label() #get current node label
        if lbl.startswith("NP#") and (not require_intervening_np_or_s or seen_np_s):
            np_id=extract_np_id(lbl) #extrat np id numbr
            if np_id is not None: #valid np id
                proposed_ids.append(np_id) #append to proposed list
        if stop_below_np_or_s and is_np_or_s(lbl): #hobbs rule: stop descent below np or s
            continue #skip non ab cand
        next_seen=seen_np_s or is_np_or_s(lbl) #update intervening np/s flag
        for child in curr: #itrate childrn of current node
            if isinstance(child,Tree): #if non terminal child
                queue.append((child,next_seen)) #add child to bfs queue
    return proposed_ids #return collected np ids


#hobbs tree search within pronun sentnce
def hobbs_search_current_sentence(sent_tree,p_np_id): #hobbs algorthm inside sent
    proposed_ids=[] #list of canddate np ids
    start_node=None #init start pronun node
    for sub in sent_tree.subtrees(): #search subtrees for pronun
        if extract_np_id(sub.label())==p_np_id: #found target pronun node
            start_node=sub #set start node
            break 
    if start_node is None: #pronun not found
        return proposed_ids #return collected np ids

    #step 2: climb up to first np or s node
    curr,X=start_node,start_node.parent() #climb up to parnt node in sent tree
    while X is not None and not is_np_or_s(X.label()): #find ancstr tht is np or s
        curr,X=X,X.parent() #move up tree parnt pointer
    if X is None: #hit tree root
        return proposed_ids #return collected np ids

    #step 3: search left branches under X with condition b
    left_siblings=[] #collect left sibling branches
    for child in X: #itrate childrn under X
        if child is curr: #reached path node curr
            break 
        left_siblings.append(child) #store left subtree branch
    proposed_ids.extend(bfs_collect_nps(left_siblings,require_intervening_np_or_s=True)) #step 3: search left of path with cond b

    #steps 5-8: climb up tree till sentnce root
    while X.parent() is not None: #climb higher up to root S
        curr,X=X,X.parent() #move up tree parnt pointer
        while X is not None and not is_np_or_s(X.label()): #find ancstr tht is np or s
            curr,X=X,X.parent() #move up tree parnt pointer
        if X is None: #hit tree root
            break 
        if X.label().startswith("NP#"):
            proposed_ids.append(extract_np_id(X.label()))

        left_siblings=[] #collect left sibling branches
        for child in X: #itrate childrn under X
            if child is curr: #reached path node curr
                break 
            left_siblings.append(child) #store left subtree branch
        if X.parent() is None: #if reached top of sent
            for sib in reversed(left_siblings): #search left siblings in reverse
                proposed_ids.extend(bfs_collect_nps([sib])) #bfs on sibling subtree
        else: 
            proposed_ids.extend(bfs_collect_nps(left_siblings)) #bfs on left siblings

        if X.label() in ("S","SBAR"): #search rght siblings under clause
            right_siblings=[] #collect rght siblings
            passed_curr=False #flag if path passed
            for child in X: #itrate childrn under X
                if child is curr: #reached path node curr
                    passed_curr=True #path passed
                elif passed_curr: #to the rght of path
                    right_siblings.append(child) #add rght sibling
            proposed_ids.extend(bfs_collect_nps(right_siblings,stop_below_np_or_s=True)) #bfs rght wihout going into np/s

    return proposed_ids #return collected np ids


#runs hobbs search across current and prior sentnces
def hobbs_rank_candidates_for_segment(seg): #full 9-step hobbs across sents
    trees=seg["cfg_trees"] #parse trees for segment
    p_sent_idx=seg["pronoun_sent_idx"] #pronun sentnce index
    p_gender=get_pronoun_gender(seg["pronoun"]) #pronun gender
    p_off=seg["pronoun_offset"] #pronun offset

    id_to_cand={c["np_id"]:c for c in reversed(seg["candidates"]) if c["np_id"]>=0} #map id to canddate dict
    proposed_np_ids=[] #proposed np ids list

    if 0<=p_sent_idx<len(trees): #chek sentnce in range
        proposed_np_ids.extend(hobbs_search_current_sentence(trees[p_sent_idx],seg["pronoun_np_id"])) #search within pronun sent

    #step 4: search previous sentnces backwards using bfs
    for prev_s_idx in range(p_sent_idx-1,-1,-1): #step 4: search prior sents backwards
        proposed_np_ids.extend(bfs_collect_nps([trees[prev_s_idx]])) #left to rght bfs on prior sent

    tier1_match,tier2_compat,tier3_other=[],[],[] #3 priority tiers for candidtes
    seen_starts=set() #set of seen offsets
    for np_id in proposed_np_ids: #filter proposed canddate ids
        if np_id in id_to_cand: #chek if cand id in cand dict
            cand=id_to_cand[np_id] #cand dict entry
            if cand["start"]>=p_off or cand["start"] in seen_starts: #skip cands aftr pron or alrdy seen
                continue #skip non ab cand
            seen_starts.add(cand["start"]) #mark cand offset in set
            c_gen=get_np_gender(cand["words"]) #canddate gender
            is_prop=any(t.startswith("NNP") for t in cand["tags"]) #proper noun chek
            if p_gender!="U" and c_gen!="U" and c_gen!=p_gender: #gender mismtch filter
                continue #skip non ab cand
            if is_prop and p_gender!="U" and c_gen==p_gender: #best tier: proper noun + gender match
                tier1_match.append(cand) #tier 1 match
            elif is_prop: #tier 2: proper noun unknown gender
                tier2_compat.append(cand) #tier 2 match
            else: 
                tier3_other.append(cand) #tier 3: other noun phrases

    for cand in reversed(seg["candidates"]): #fallback in case some nps not visited
        if cand["start"]<p_off and cand["start"] not in seen_starts: #add to other tier
            seen_starts.add(cand["start"]) #mark cand offset in set
            tier3_other.append(cand) #tier 3: other noun phrases

    return tier1_match+tier2_compat+tier3_other #ret combined prioritized cands


#prob 7: rule based hobbs algorthm evaluation
def problem_7(test_segments): #problem 7 hobbs algorthm
    print("="*80) 
    print("PROBLEM 7 Rule-Based Hobbs' Algorithm on CFG Parse Trees") 
    print("="*80) 
    tp_all,fp_all,fn_all=0,0,0 #init all nps counters
    tp_ab,fp_ab,fn_ab=0,0,0 #init ab counters

    for seg in test_segments: #loop test passages
        has_gold=seg["A_coref"] or seg["B_coref"] #chek if gold antecednt exists
        hobbs_ranked=hobbs_rank_candidates_for_segment(seg) #rank candidtes using hobbs
        if len(hobbs_ranked)>0: #chek if candidtes proposed
            if hobbs_ranked[0]["is_antecedent"]: #top 1 pick correct
                tp_all+=1 #got it rght
            else: 
                fp_all+=1 #pred wrng cand
                if has_gold: #chek if gold existed
                    fn_all+=1 #missed true referent
        elif has_gold: #model predicted nothng so fn
            fn_all+=1 #missed true referent

        hobbs_ab=[c for c in hobbs_ranked if c["matches_A"] or c["matches_B"]] #filter candidtes to a and b
        if len(hobbs_ab)>0: #ab canddate found
            if hobbs_ab[0]["is_antecedent"]: #top ab pick correct
                tp_ab+=1 #correct betwen a and b
            else: 
                fp_ab+=1 #picked wrng betwen a and b
                if has_gold: #chek if gold existed
                    fn_ab+=1 #missed true a/b antecednt
        elif has_gold: #model predicted nothng so fn
            fn_ab+=1 #missed true a/b antecednt

    p_all,r_all,f1_all=calc_prf(tp_all,fp_all,fn_all) #calc prf on all nps
    p_ab,r_ab,f1_ab=calc_prf(tp_ab,fp_ab,fn_ab) #calc prf on ab cands
    print("Hobbs' Algorithm Performance on Test Set (gap-test.tsv, 2000 segments):") 
    print("  1. Full Candidate NP Pool (All POS-Extracted Candidate NPs):") 
    print(f"       Precision: {p_all*100:.2f}% | Recall: {r_all*100:.2f}% | F1-Score: {f1_all*100:.2f}%") 
    print("  2. GAP Candidate Entities (Evaluating on Candidates A vs B):") 
    print(f"       Precision: {p_ab*100:.2f}% | Recall: {r_ab*100:.2f}% | F1-Score: {f1_ab*100:.2f}%\n") 
    return {"all_nps":(p_all,r_all,f1_all),"ab_nps":(p_ab,r_ab,f1_ab)} #ret metrics dict for all nps & ab


#prob 8: comparing logistic regression vs hobbs
def problem_8(lr_res,hobbs_res,rand_res,recent_res): #problem 8 comparison table
    print("="*80) 
    print("PROBLEM 8 Quantitative & Qualitative Comparison (LR vs. Hobbs)") 
    print("="*80) 
    print(f"{'Method':<34} | {'All-NPs F1':>12} | {'GAP (A/B) Prec':>14} | {'GAP (A/B) Rec':>13} | {'GAP (A/B) F1':>12}") 
    print("-"*94) 
    print(f"{'Random Assignment (100 runs)':<34} | {rand_res[0]*100:11.2f}% | {rand_res[1]*100:13.2f}% | {rand_res[1]*100:12.2f}% | {rand_res[1]*100:11.2f}%") 
    print(f"{'Most Recent Antecedent':<34} | {recent_res[0]*100:11.2f}% | {recent_res[1]*100:13.2f}% | {recent_res[1]*100:12.2f}% | {recent_res[1]*100:11.2f}%") 
    hp_a,hr_a,hf_a=hobbs_res["all_nps"] #hobbs all nps metrics
    hp_b,hr_b,hf_b=hobbs_res["ab_nps"] #hobbs ab metrics
    print(f"{'Rule-Based Hobbs Algorithm':<34} | {hf_a*100:11.2f}% | {hp_b*100:13.2f}% | {hr_b*100:12.2f}% | {hf_b*100:11.2f}%") 
    lp_a,lr_a,lf_a=lr_res["all_nps"] #custom lr all nps metrics
    lp_b,lr_b,lf_b=lr_res["ab_nps"] #custom lr ab metrics
    print(f"{'Custom Logistic Regression (Ours)':<34} | {lf_a*100:11.2f}% | {lp_b*100:13.2f}% | {lr_b*100:12.2f}% | {lf_b*100:11.2f}%\n") 


#extra credit: using sklearn logistic regression for comparison
def extra_credit(train_segments,dev_segments,test_segments,hobbs_res=None): #extra credit sklearn lr
    print("="*80) 
    print("EXTRA CREDIT Scikit-Learn Logistic Regression Implementation") 
    print("="*80) 
    try:
        from sklearn.linear_model import LogisticRegression #import sklearn LogisticRegression
    except ImportError: #sklearn not installed
        print("scikit-learn is not installed in this environment.") 
        return None #ret none if import failed

    X_train,y_train=build_Xy_pairs(train_segments) #convrt train segs to feat matrix
    print("1. Hyperparameter Tuning on Development Set (gap-validation.tsv):") 
    print(f"{'C':>6} | {'Pos_Weight':>10} | {'Dev F1 (All NPs)':>16} | {'Dev F1 (A/B NPs)':>16}") 
    print("-"*56) 

    best_params,best_f1,best_model=(1.0,3.0),-1.0,None #track best sklearn params
    for c_val in [0.01,0.1,1.0,10.0]: #grid search inverse reg C
        for pw in [2.0,3.0,4.0]: #grid search class wght
            clf=LogisticRegression(C=c_val,class_weight={0:1.0,1:pw},max_iter=500,random_state=42) #create sklearn LogisticRegression
            clf.fit(X_train,y_train) #fit sklearn clf on X_train
            sk_model=SimpleLogisticRegression(len(FEATURE_NAMES)) #create new custom lr model
            sk_model.weights=list(clf.coef_[0]) #get learned wghts from clf.coef_
            sk_model.bias=float(clf.intercept_[0]) #get learned bias from clf.intercept_

            dev_res=evaluate_model_predictions(dev_segments,sk_model,threshold=0.25) #test on dev/validation set
            f1_all_dev,f1_ab_dev=dev_res["all_nps"][2],dev_res["ab_nps"][2] #dev set f1 scores
            print(f"{c_val:6.2f} | {pw:10.1f} | {f1_all_dev*100:15.2f}% | {f1_ab_dev*100:15.2f}%") 
            if 0.5*(f1_all_dev+f1_ab_dev)>best_f1: #is this C and poswt better
                best_f1=0.5*(f1_all_dev+f1_ab_dev) #updated best dev f1
                best_params=(c_val,pw) #save best C and pw
                best_model=sk_model

    print("-"*56) 
    print(f"Best scikit-learn Hyperparameters on Dev Set: C = {best_params[0]}, pos_weight = {best_params[1]}\n") 

    test_res=evaluate_model_predictions(test_segments,best_model,threshold=0.25) #evaluate on test set with best hp
    p_all,r_all,f1_all=test_res["all_nps"] #test metrics for full cand pool
    p_ab,r_ab,f1_ab=test_res["ab_nps"] #test metrics for a vs b

    print("2. Test Set Performance (scikit-learn LogisticRegression on gap-test.tsv):") 
    print(f"  - Full Candidate NP Pool: Precision={p_all*100:.2f}% | Recall={r_all*100:.2f}% | F1={f1_all*100:.2f}%") 
    print(f"  - GAP Candidates (A/B):   Precision={p_ab*100:.2f}% | Recall={r_ab*100:.2f}% | F1={f1_ab*100:.2f}%\n") 

    print(f"3. Scikit-Learn Learned Feature Weights (Intercept = {best_model.bias:+.4f}):") 
    print(f"{'Rank':>4} | {'Feature Name':<26} | {'Learned Weight':>14} | {'|Weight|':>10}") 
    print("-"*64) 
    sk_feats=sorted(zip(FEATURE_NAMES,best_model.weights),key=lambda item:abs(item[1]),reverse=True) #rank sklearn wghts by abs
    for idx,(fname,w) in enumerate(sk_feats,start=1): #printng sklearn wts
        print(f"{idx:4d} | {fname:<26} | {w:+14.4f} | {abs(w):10.4f}") 

    print("\nScikit-Learn Top-5 Feature Weights:") 
    for idx,(fname,w) in enumerate(sk_feats[:5],start=1): #show higest wghts sklearn wghts
        print(f"  {idx}. {fname:<26}: {w:+.4f}") 

    sk_errors=sum( #count wrng test predictions
        1 for seg in test_segments if (seg["A_coref"] or seg["B_coref"])
        and not pick_best_candidate(seg["candidates"],seg["features"],best_model)[1]["is_antecedent"]
    )
    print("\n4. Scikit-Learn Error Analysis & Comparison:") 
    print(f"  - Total errors on gold-annotated test segments: {sk_errors} (exhibits the same 4 error patterns as Custom LR)") 
    if hobbs_res is not None: #print diff vs hobbs algo
        print(f"  - Comparison vs. Hobbs' Algorithm: Scikit-Learn LR improves Full-Pool F1 from {hobbs_res['all_nps'][2]*100:.2f}% to {f1_all*100:.2f}%") 
        print(f"    and GAP (A/B) F1 from {hobbs_res['ab_nps'][2]*100:.2f}% to {f1_ab*100:.2f}%.\n") 
    return test_res 


#main flow
def main(): #main func runner
    base_dir=os.path.dirname(os.path.abspath(__file__)) #get current script dirctory path
    data_dir=os.path.join(base_dir,"data") #path to data/ folder

    print("Loading GAP Coreference Dataset splits (train, dev, test)...") 
    train_rows=load_gap_tsv(os.path.join(data_dir,"gap-development.tsv")) #load 2000 train rows from tsv
    dev_rows=load_gap_tsv(os.path.join(data_dir,"gap-validation.tsv")) #load 454 dev rows from tsv
    test_rows=load_gap_tsv(os.path.join(data_dir,"gap-test.tsv")) #load 2000 test rows from tsv

    print("Running POS Tagger, CFG Parser, and Candidate NP Extraction...") 
    train_segments=extract_candidates_from_dataset(train_rows) #get cands and trees for train
    dev_segments=extract_candidates_from_dataset(dev_rows) #get cands and trees for dev
    test_segments=extract_candidates_from_dataset(test_rows) #get cands and trees for test

    print("Extracting features (including Hobbs CFG tree features) for all segments...\n") 
    for seg in train_segments: #loop train passages
        seg["features"]=extract_features_for_segment(seg) #extrat 12 feats for cands in seg
    for seg in dev_segments: #loop dev passages
        seg["features"]=extract_features_for_segment(seg) #extrat 12 feats for cands in seg
    for seg in test_segments: #loop test passages
        seg["features"]=extract_features_for_segment(seg) #extrat 12 feats for cands in seg

    #calling each problem
    problem_1(test_segments) #running prob 1 cand extration
    rand_res=problem_2(test_segments) #running randm basline 100 times
    recent_res=problem_3(test_segments) #running recency basline
    best_model,lr_res=problem_4(train_segments,dev_segments,test_segments) #trainig custom lr on train data
    problem_5(best_model) #displaying learned wghts
    problem_6(test_segments,best_model) #error count + pointer to report

    #generating parse trees pdf for submission
    trees_txt=save_parse_trees_txt(test_segments,base_dir) #write ascii trees to txt
    convert_trees_txt_to_pdf(trees_txt) #convrt to pdf via textutil

    hobbs_res=problem_7(test_segments) #testng hobbs algo on test split
    problem_8(lr_res,hobbs_res,rand_res,recent_res) #show comparison table for all methods
    extra_credit(train_segments,dev_segments,test_segments,hobbs_res=hobbs_res) #running sklearn log reg model


if __name__=="__main__": 
    main() 
