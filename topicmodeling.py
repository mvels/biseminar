import numpy as np
import lda
import unicodedata
import lda.datasets
from sklearn.feature_extraction import DictVectorizer
from tutorial.DataModel import Course, CourseWord, LectureWord


def main():

    # Get data for each course
    courses = Course.select()
    courses_dict = []
    course_titles = []
    for course in courses:
        course_words = CourseWord.select().where(CourseWord.course == course)
        courses_dict.append(dict([(x.word, x.count) for x in course_words]))
        course_titles.append(remove_accents(course.name))

    #Get the vocabulary and the word count per document matrix
    res = get_bag_of_words(courses_dict)

    #Print all the words and their counts
    #print_word_dist(res)

    #Perform lda with 5000 iterations, total 20 topics
    model = lda.LDA(n_topics=20, n_iter=5000, random_state=1)
    n_top_words = 11

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
    # Initialize the "DictVectorizer" object, which is scikit-learn's
    # bag of words tool.
    vectorizer = DictVectorizer()

    # fit_transform() does two functions: First, it fits the model
    # and learns the vocabulary; second, it transforms our training data
    # into feature vectors. The input to fit_transform should be a list of
    # strings.
    train_data_features = vectorizer.fit_transform(courses_material)

    # Convert the result to an array
    train_data_features = train_data_features.toarray()

    #Get the vocabulary
    vocab = vectorizer.get_feature_names()

    return {'X': train_data_features, 'vocab': vocab}


def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nkfd_form.encode('ASCII', 'ignore')
    return only_ascii


def print_word_dist(data):
    # Sum up the counts of each vocabulary word
    dist = np.sum(data['X'], axis=0)

    # For each, print the vocabulary word and the number of times it
    # appears in the training set
    for tag, count in zip(data['vocab'], dist):
        print count, tag


if __name__ == '__main__':
    main()
