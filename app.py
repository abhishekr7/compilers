from flask import Flask, request, render_template,jsonify
import codecs
from collections import defaultdict
app = Flask(__name__)
def do_something(text1,text2):
   text1 = text1.upper()
   text2 = text2.upper()
   combine = text1 + text2
   return combine

vowels =[u'\u0900',u'\u0901',u'\u0902',u'\u0903',u'\u093A',u'\u093B',u'\u093C',u'\u093D',u'\u093E',u'\u093F',u'\u0940',u'\u0941',u'\u0942',u'\u0943',u'\u0944',u'\u0945',u'\u0946',u'\u0947',u'\u0948',u'\u0949',u'\u094A',u'\u094B',u'\u094C',u'\u094D',u'\u094E',u'\u094F']
digits = [u'\u0966',u'\u0967',u'\u0968',u'\u0969',u'\u096A',u'\u096B',u'\u096C',u'\u096D',u'\u096E',u'\u096F']

def hmm_pos_tagger(input_sentence) :

    stringOutput = ""

    all_tags = []
    trainfile = codecs.open("Dataset/training_sentences.txt", mode = "r", encoding = "utf-8")

    for sentence in trainfile.readlines() :
        tokens = sentence.split()
        for token in tokens :
            all_tags.append(token.split('|')[2].split('.')[0].strip(':?'))
    all_tags = list(set(all_tags))

    wordprobfile = codecs.open("Dataset/word_probability_training_sentences.txt", mode = "r", encoding = "utf-8")
    wordprob = {}

    for term in wordprobfile.readlines() :
        wordprob[term.split('\t')[0]] = float(term.split('\t')[1])

    tagprobfile = codecs.open("Dataset/tag_probability_training_sentences.txt", mode = "r", encoding = "utf-8")
    tagprob = {}

    for term in tagprobfile.readlines() :
        tagprob[term.split('\t')[0]] = float(term.split('\t')[1])

    prev = '$'
    #print(input_sentence)
    tokens = input_sentence.split()[::-1]
    #print(tokens)
    for token in tokens :
        #print("token : " + token)
        predicted_tag = 'none'
        for digit in digits :
            if digit in token :
                predicted_tag = u'QC'
                prev = u'QC'
        else :
            if token[0] in [',','.','|','\'','\"','(',')',':',';','?','-','!','+','*','%','@','#','&','_','='] :
                predicted_tag = u'SYM'
                prev = u'SYM'
            else :
                ans = -1 * float('inf')
                word = token.strip('(').strip(')').strip('\'').strip('\"').strip('-').strip('[').strip(']').strip(':').strip(';').strip(',').strip('?').strip('-').strip('!').strip('@').strip('#').strip('&').strip('_').strip('=')
                #suffix = "" #added

                #for letter in word :
                #    if letter not in vowels :
                #        suffix += '*'
                #    else :
                #        suffix += letter

                for tag in all_tags :
                    try :
                        tp = tagprob[tag + '|' + prev]
                    except:
                        tp = 1e-8
                    try :
                        wp = wordprob[word + '|' + tag]
                    except:
                        wp = 1e-8
                    #try :
                    #    sp = suffprob[suffix + '|' + tag]
                    #except:
                    #    sp = 1e-8
                    if tp * wp > ans :
                        ans = tp * wp
                        predicted_tag = tag
                prev = predicted_tag

        stringOutput = (token + " : " + predicted_tag) + "<br/>" + stringOutput

    trainfile.close()
    wordprobfile.close()
    tagprobfile.close()

    return stringOutput

def innit():
    inputfile = codecs.open("Dataset/training_sentences.txt", mode = "r", encoding = "utf-8")
    count_tag_sequences = defaultdict(int)
    count_word_tag = defaultdict(int)
    total_words = 0

    for sentence in inputfile.readlines() :
        sentence = sentence.strip()
        if len(sentence) == 0 :
            continue
        tags = []
        tokens = sentence.split()[::-1]

        #print("\'" + sentence + "\'")
        #print("Length :" + str(len(sentence)))
        for token in tokens :
            #print(token)
            word = token.split('|')[0].split('.')[0]
            tag = token.split('|')[2].split('.')[0].strip(':?')
            tags.append(tag)
            total_words += 1
            count_word_tag[(word + "|" + tag)] += 1

        count_tag_sequences[(tags[0] + "|" + '$')] += 1
        for i in range(1, len(tags)) :
            count_tag_sequences[(tags[i] + '|' + tags[i - 1])] += 1

    probability_tag_sequences = {}
    for tag_sequence in count_tag_sequences :
        probability_tag_sequences[tag_sequence] = count_tag_sequences[tag_sequence] / (total_words * 1.0)

    outputfile = codecs.open("Dataset/tag_probability_training_sentences.txt", mode = "w", encoding = "utf-8")

    for term in probability_tag_sequences :
        outputfile.write(term + '\t' + str(probability_tag_sequences[term]) + '\n')

    outputfile.close()
    inputfile.close()

    probability_word_tag = {}
    for word_tag in count_word_tag :
        probability_word_tag[word_tag] = count_word_tag[word_tag] / (total_words * 1.0)

    outputfile = codecs.open("Dataset/word_probability_training_sentences.txt", mode = "w", encoding = "utf-8")

    for term in probability_word_tag :
        outputfile.write(term + '\t' + str(probability_word_tag[term]) + '\n')

    outputfile.close()

def check_accuracy() :
    outputResult = ""
    testfile = codecs.open("Dataset/new_test.txt", mode = "r", encoding = "utf-8")
    all_tags = []
    trainfile = codecs.open("Dataset/new_train.txt", mode = "r", encoding = "utf-8")

    for sentence in trainfile.readlines() :
        tokens = sentence.split()
        for token in tokens :
            all_tags.append(token.split('|')[2].split('.')[0].strip(':?'))
    all_tags = list(set(all_tags))
    print("Total tags : " + str(len(all_tags)))

    wordprobfile = codecs.open("Dataset/word_prob_rev.txt", mode = "r", encoding = "utf-8")
    wordprob = {}

    for term in wordprobfile.readlines() :
        wordprob[term.split('\t')[0]] = float(term.split('\t')[1])

    tagprobfile = codecs.open("Dataset/tag_prob_rev.txt", mode = "r", encoding = "utf-8")
    tagprob = {}

    for term in tagprobfile.readlines() :
        tagprob[term.split('\t')[0]] = float(term.split('\t')[1])

    final_word_count = 0
    final_match_count = 0

    dict_actual_tag = defaultdict(int)
    dict_predicted_tag = defaultdict(int)
    dict_true_positive = defaultdict(int)
    dict_false_positive = defaultdict(int)
    dict_false_negative = defaultdict(int)

    for sentence in testfile.readlines() :
        prev = '$'
        total_words = 0
        total_matches = 0

        tokens = sentence.split()[::-1]
        for token in tokens :
            word = token.split('|')[0]
            actual_tag = token.split('|')[2].split('.')[0].strip(':?')

            dict_actual_tag[actual_tag] += 1
            ans = -1 * float('inf')

            for digit in digits:
                if digit in word :
                    predicted_tag = u'QC'
                    prev = u'QC'
            else :
                if word[0] in [',','.','|','\'','\"','(',')',':',';','?','-','!','+','*','%','@','#','&','_','='] :
                    predicted_tag = u'SYM'
                    prev = u'SYM'
                else :
                    word = token.split('|')[0].strip('(').strip(')').strip('\'').strip('\"').strip('-').strip('[').strip(']').strip(':').strip(';').strip(',').strip('?').strip('-').strip('!').strip('@').strip('#').strip('&').strip('_').strip('=')
                    for tag in all_tags :
                        try :
                            tp = tagprob[tag + "|" + prev]
                        except :
                            tp = 1e-8
                        try :
                            wp = wordprob[word + "|" + tag]
                        except :
                            wp = 1e-8
                        if tp * wp > ans :
                            ans = tp * wp
                            predicted_tag = tag
                    prev = predicted_tag
            dict_predicted_tag[predicted_tag] += 1
            if actual_tag == predicted_tag or actual_tag == 'UNK' or actual_tag.strip(":?") == predicted_tag.strip(":?") :
                total_matches += 1
                dict_true_positive[predicted_tag] += 1
            else :
                dict_false_positive[predicted_tag] += 1
                dict_false_negative[actual_tag] += 1
            total_words += 1
        final_word_count += total_words
        final_match_count += total_matches

    trainfile.close()
    testfile.close()
    wordprobfile.close()
    tagprobfile.close()

    accuracy = (final_match_count / final_word_count) * 100.0

    outputResult += "Total words in the test dataset : " + str(final_word_count) + "<br/>"
    outputResult += "Number of words correctly tagged : " + str(final_match_count) + "<br/>"
    outputResult += "Accuracy : " + str(accuracy) + "<br/>"

    for tag in dict_actual_tag :
        true_positives = dict_true_positive[tag]
        false_negatives = dict_false_negative[tag]
        false_positives = dict_false_positive[tag]

        if true_positives == 0 and false_positives == 0:
            precision = "undefined"
        else :
            precision = true_positives / (true_positives + false_positives)
        if true_positives == 0 and false_negatives == 0:
            recall = "undefined"
        else :
            recall = true_positives / (true_positives + false_negatives)
        if (precision == 0 and recall == 0) or precision == "undefined" or recall == "undefined" :
            fscore = "undefined"
        else :
            fscore = (2 * precision * recall) / (precision + recall)

        #print(tag + " Precision " + str(precision) + " Recall " + str(recall) + " F-score " + str(fscore))

    return outputResult

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/join', methods=['GET','POST'])
def my_form_post():
    text1 = request.form['text1']
    #word = request.args.get('text1')
    #text2 = request.form['text2']

    innit()
    #check_accuracy()
    combine = hmm_pos_tagger(text1)
    result = {
        "output": combine
    }
    result = {str(key): value for key, value in result.items()}
    return jsonify(result=result)

@app.route('/results', methods=['GET','POST'])
def my_results_post():
    #text1 = request.form['text1']
    #word = request.args.get('text1')
    #text2 = request.form['text2']

    innit()
    combine = check_accuracy()
    #combine = hmm_pos_tagger(text1)
    result = {
        "output": combine
    }
    result = {str(key): value for key, value in result.items()}
    return jsonify(result=result)

if __name__ == '__main__':
    app.run(debug=True)
