import json


class Teacher(object):
    def __init__(self):
        self.names = self.get_names()

    def get_names(self):
        data = open('teachers.json').read()
        teachers = json.loads(data)

        names = []
        for teacher in teachers:
            for name in teacher['name'].split():
                names.append(name.lower())

        return names


def main():
    t = Teacher()
    for name in t.names:
        print "{}: {}".format(type(name), name.encode('utf8'))


if __name__ == '__main__':
    main()
