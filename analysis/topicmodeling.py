import numpy as np
import lda
import unicodedata
import lda.datasets
from sklearn.feature_extraction import DictVectorizer
from db.DataModel import Course, Lecture, CourseWord, LectureWord, LectureTopic, LectureTopicWord
import peewee
from db.DataModel import db, TopicWord, CourseTopic, LDALogLikelihood


def main():
    # Perform LDA over all courses
    lda_over_courses(10, 5)

    # Perform LDA over all material in scope of one course
    lda_over_lectures(10, 5)


def lda_over_lectures(n_top_words, n_top_topic):
    courses = Course.select()
    for course in courses:
        print("LDA for course: " + course.name)
        lda_for_course_material(course, n_top_words, n_top_topic)


def lda_for_course_material(course, n_top_words, n_top_topic):
    lectures = Lecture.select().where(Lecture.course == course)
    lectures_size = Lecture.select().where(Lecture.course == course).count()
    lecture_dict = []
    for lecture in lectures:
        lecture_words = LectureWord.select().where(LectureWord.lecture == lecture)
        lecture_dict.append(dict([(x.word, x.count) for x in lecture_words]))

    if not lecture_dict:
        return

    model, vocab = perform_lda(lecture_dict, lectures_size)

    for i, topic_dist in enumerate(model.topic_word_):
        top_topic_words = np.array(vocab)[np.argsort(topic_dist)][:-n_top_words - 1:-1]
        top_word_probs = topic_dist[np.argsort(topic_dist)][:-n_top_words - 1:-1]

        for top_word, top_weight in zip(top_topic_words, top_word_probs):
            try:
                with db.transaction() as txn:
                    LectureTopicWord.create(
                        course=course,
                        topic=i,
                        word=top_word,
                        weight=round(top_weight * 100, 2)
                    )
                    txn.commit()
            except peewee.OperationalError as e:
                print "Could not create a record for topic {}, word {}, {}".format(i, top_word, e)

        top_word_str = ", ".join([remove_accents(x) + "(" + str(round(y, 2) * 100) + "%)"
                                  for x, y in zip(top_topic_words, top_word_probs)])

        print('Topic {}: {}'.format(i, top_word_str))

    # Document-topic distributions
    doc_topic = model.doc_topic_

    for i in range(lectures_size):
        top_topics = np.argsort(doc_topic[i])[:-n_top_topic - 1:-1]
        topic_probs = doc_topic[i][top_topics]


        #Substitude this
        title = remove_accents(lectures[i].path.split("/")[-1])

        for top_topic, top_weight in zip(top_topics, topic_probs):
            try:
                with db.transaction() as txn:
                    LectureTopic.create(
                        lecture=lectures[i],
                        topic=top_topic,
                        weight=round(top_weight * 100, 2)
                    )
                    txn.commit()
            except peewee.OperationalError as e:
                print "Could not create a record for lecture {0}, topic {1}, {2}" \
                    .format(remove_accents(lectures[i].name), i, e)

        doc_topic_str = ", ".join(
            [str(x) + "(" + str(round(y * 100, 2)) + "%)" for x, y in zip(top_topics, topic_probs)])
        print("{} (top {} topics: {})".format(title, n_top_topic, doc_topic_str))


def lda_over_courses(n_top_words, n_top_topic):
    courses = Course.select()
    courses_size = Course.select(Course.code).distinct().count()
    courses_dict = []
    for course in courses:
        course_words = CourseWord.select().where(CourseWord.course == course)
        courses_dict.append(dict([(x.word, x.count) for x in course_words]))

    print "Performing LDA over all courses.."
    model, vocab = perform_lda(courses_dict, courses_size)

    for i, x in enumerate(model.loglikelihoods_):
        try:
            with db.transaction() as txn:
                LDALogLikelihood.create(
                    iteration=i * 10,
                    loglikelihood=round(x, 2),
                )
                txn.commit()
        except peewee.OperationalError as e:
            print "Could not create a record for loglikelihood {}, {}".format(x, e)

    # Iterate over topic word distributions
    for i, topic_dist in enumerate(model.topic_word_):
        top_topic_words = np.array(vocab)[np.argsort(topic_dist)][:-n_top_words - 1:-1]
        top_word_probs = topic_dist[np.argsort(topic_dist)][:-n_top_words - 1:-1]

        for top_word, top_weight in zip(top_topic_words, top_word_probs):
            try:
                with db.transaction() as txn:
                    TopicWord.create(
                        topic=i,
                        word=top_word,
                        weight=round(top_weight * 100, 2)
                    )
                    txn.commit()
            except peewee.OperationalError as e:
                print "Could not create a record for topic {}, word {}, {}".format(i, top_word, e)

        top_word_str = ", ".join([remove_accents(x) + "(" + str(round(y * 100, 2)) + "%)"
                                  for x, y in zip(top_topic_words, top_word_probs)])

        print('Topic {}: {}'.format(i, top_word_str))

    # Document-topic distributions
    doc_topic = model.doc_topic_

    for i in range(courses_size):
        top_topics = np.argsort(doc_topic[i])[:-n_top_topic - 1:-1]
        topic_probs = doc_topic[i][top_topics]

        for top_topic, top_weight in zip(top_topics, topic_probs):
            try:
                with db.transaction() as txn:
                    CourseTopic.create(
                        course=courses[i],
                        topic=top_topic,
                        weight=round(top_weight * 100, 2)
                    )
                    txn.commit()
            except peewee.OperationalError as e:
                print "Could not create a record for course {0}, topic {1}, {2}" \
                    .format(remove_accents(courses[i].name), i, e)

        doc_topic_str = ", ".join(
            [str(x) + "(" + str(round(y * 100, 2)) + "%)" for x, y in zip(top_topics, topic_probs)])
        print("{} (top {} topics: {})".format(remove_accents(courses[i].name), n_top_topic, doc_topic_str))


def perform_lda(word_dict, n_topics):
    # Initialize the "DictVectorizer" object, which is scikit-learn's
    # bag of words tool.
    vectorizer = DictVectorizer()

    # fit_transform() does two functions: First, it fits the model
    # and learns the vocabulary; second, it transforms our training data
    # into feature vectors(bag of words)
    train_data_features = vectorizer.fit_transform(word_dict)

    # Convert the result to an array
    train_data_features = train_data_features.toarray()

    # Get the vocabulary
    vocab = vectorizer.get_feature_names()

    # Print all the words and their counts
    # print_word_dist(res)

    # Init lda
    model = lda.LDA(n_topics=n_topics, n_iter=1000, random_state=1)

    #Fit model
    model.fit(train_data_features.astype('int32'))

    return model, vocab


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
