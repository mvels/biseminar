import numpy as np
import lda
import unicodedata
import lda.datasets
from sklearn.feature_extraction import DictVectorizer
from tutorial.DataModel import Course, Lecture, CourseWord, LectureWord


def main():
    #Perform LDA in scope of all courses
    #lda_for_all_courses()

    #Perform LDA for all material in scope of one course
    #Test on course 'Andmekaeve'
    courses = Course.select().where(Course.id == 2)
    for course in courses:
        lda_for_course_material(course)


def lda_for_course_material(course):
    lectures = Lecture.select().where(Lecture.course == course)
    lecture_dict = []
    lecture_titles = []
    for lecture in lectures:
        lecture_words = LectureWord.select().where(LectureWord.lecture == lecture)
        lecture_dict.append(dict([(x.word, x.count) for x in lecture_words]))
        lecture_titles.append(remove_accents(lecture.path).split("/")[-1])

    print("LDA for course: "+course.name)
    perform_lda(lecture_dict, lecture_titles, 10, 15, 5)


def lda_for_all_courses():
    courses = Course.select()
    courses_dict = []
    course_titles = []
    for course in courses:
        course_words = CourseWord.select().where(CourseWord.course == course)
        courses_dict.append(dict([(x.word, x.count) for x in course_words]))
        course_titles.append(remove_accents(course.name))

    perform_lda(courses_dict, course_titles, 100, 10, 5)


def perform_lda(word_dict, titles, n_topics, n_top_words, n_top_topic):
    #Get the vocabulary and the word count per document matrix
    res = get_bag_of_words(word_dict)

    #Print all the words and their counts
    #print_word_dist(res)

    #Init lda
    model = lda.LDA(n_topics=n_topics, n_iter=5000, random_state=1)

    #Fit model
    model.fit(res['X'].astype('int32'))

    #Iterate over topic word distributions
    for i, topic_dist in enumerate(model.topic_word_):
        top_topic_words = np.array(res['vocab'])[np.argsort(topic_dist)][:-n_top_words-1:-1]

        print('Topic {}: {}'.format(i, " ".join(top_topic_words)))

    #Document-topic distributions
    doc_topic = model.doc_topic_

    for i in range(len(titles)):
        top_topics = np.argsort(doc_topic[i])[:-n_top_topic-1:-1]
        topic_probs = doc_topic[i][top_topics]

        doc_topic_str = ", ".join([str(x)+"("+str(round(y, 2)*100)+"%)" for x, y in zip(top_topics, topic_probs)])
        print("{} (top {} topics: {})".format(titles[i], n_top_topic, doc_topic_str))


def get_bag_of_words(courses_material):
    # Initialize the "DictVectorizer" object, which is scikit-learn's
    # bag of words tool.
    vectorizer = DictVectorizer()

    # fit_transform() does two functions: First, it fits the model
    # and learns the vocabulary; second, it transforms our training data
    # into feature vectors.
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

    for tag, count in zip(data['vocab'], dist):
        print count, tag


if __name__ == '__main__':
    main()
