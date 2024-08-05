from django.db import models

class Subject(models.Model):
    name = models.CharField(max_length=255, unique=True)

class Exam(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams')
    name = models.CharField(max_length=255, unique=True)
    duration = models.DurationField()
    number_of_questions = models.PositiveIntegerField(default=1)

class Question(models.Model):
    content = models.TextField()
    image_path = models.CharField(max_length=255, blank=True, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    answer_a = models.CharField(max_length=255)
    answer_b = models.CharField(max_length=255)
    answer_c = models.CharField(max_length=255)
    answer_d = models.CharField(max_length=255)
    mark = models.DecimalField(max_digits=5, decimal_places=2) 
    mix_choices = models.BooleanField(default=False)
    unit = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)  # 'a', 'b', 'c', or 'd'

    def __str__(self):
        return self.content[:50]

class ExamQuestionMap(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

class Calendar(models.Model):
    start_time = models.DateTimeField()
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)

