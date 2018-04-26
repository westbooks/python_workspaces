# -*- coding: utf-8 -*-

class Student(object):

    def __init__(self,name,score):
        self.name = name
        self.score = score

    def print_score(self):
        print('%s:%s' % (self.name,self.score))

    def get_grade(self):
        if self.score >= 90:
            return 'A'
        elif self.score >=80:
            return 'B'
        elif self.score >=60:
            return 'C'
        else:
            return 'D'


Lisa = Student('Lisa',99)
Sxf = Student('Sxf',58)

Lisa.print_score()
Sxf.print_score()

a = Lisa.get_grade()
print(a)
b = Sxf.get_grade()
print(b)
