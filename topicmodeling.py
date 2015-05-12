import numpy as np
import lda
import lda.datasets
import unicodedata
import re
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from tutorial.DataModel import Lecture, Course


def main():
    #download stop-words during first run
    #nltk.download("stopwords")

    courses = Course.select()#.limit(5)

    #Get data for each course
    course_combined_text = []
    course_titles = []
    for course in courses:
        lectures = Lecture.select().where(Lecture.course == course)
        course_combined_text.append(unicode.join(u' ', [lecture.content for lecture in lectures]))
        course_titles.append(remove_accents(course.name))

    #Get the vocabulary and the word count per document matrix
    res = get_bag_of_words(course_combined_text)

    #Print all the words and their counts
    #print_word_dist(res)

    #Perform lda with 5000 iterations, total 20 topics
    model = lda.LDA(n_topics=20, n_iter=5000, random_state=1)
    n_top_words = 8

    #Fit model
    model.fit(res['X'].astype('int32'))

    for i, topic_dist in enumerate(model.topic_word_):
        topic_words = np.array(res['vocab'])[np.argsort(topic_dist)][:-n_top_words:-1]
        print('Topic {}: {}'.format(i, ' '.join(topic_words)))

    #Document-topic distributions
    doc_topic = model.doc_topic_

    for i in range(len(course_titles)):
        print("{} (top topic: {})".format(course_titles[i], doc_topic[i].argmax()))


def get_bag_of_words(courses_material):
    # Initialize the "CountVectorizer" object, which is scikit-learn's
    # bag of words tool.
    vectorizer = CountVectorizer(analyzer="word", max_features=None)

    # fit_transform() does two functions: First, it fits the model
    # and learns the vocabulary; second, it transforms our training data
    # into feature vectors. The input to fit_transform should be a list of
    # strings.
    train_data_features = vectorizer.fit_transform([clean_text(x) for x in courses_material])

    # Convert the result to an array
    train_data_features = train_data_features.toarray()

    #Get the vocabulary
    vocab = vectorizer.get_feature_names()

    return {'X': train_data_features, 'vocab': vocab}


def print_word_dist(data):
    # Sum up the counts of each vocabulary word
    dist = np.sum(data['X'], axis=0)

    # For each, print the vocabulary word and the number of times it
    # appears in the training set
    for tag, count in zip(data['vocab'], dist):
        print count, tag


def clean_text(raw_text):
    # 1.Unicode normalized and encoded to ASCII
    text_str = remove_accents(raw_text)

    # 2. Remove non-letters
    letters_only = re.sub("[^a-zA-Z]", " ", text_str)

    # 3. Convert to lower case, split into individual words
    words = letters_only.lower().split()

    # 4. In Python, searching a set is much faster than searching
    #   a list, so convert the stop words to a set
    stops = set(stopwords.words("english"))

    # 5. Remove english stop words
    meaningful_words = [w for w in words if not w in stops]

    # 6. Return as one string with words separated by space
    return ' '.join(meaningful_words)


def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nkfd_form.encode('ASCII', 'ignore')
    return only_ascii


if __name__ == '__main__':
    main()
