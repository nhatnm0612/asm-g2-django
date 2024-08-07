from rest_framework import serializers
from .models import Question, Exam, ExamQuestionMap, Calendar
from .models import Subject

class QuestionSerializers(serializers.ModelSerializer):
    blob_name = serializers.CharField(required=True)
    container_name = serializers.CharField(required=True)
    class Meta:
        model = Question
        fields = ['blob_name', "container_name"]

class ListQuestionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class ExamSerializers(serializers.ModelSerializer):
    subject = serializers.PrimaryKeyRelatedField(queryset = Subject.objects.all())
    class Meta:
        model = Exam
        fields = ['id','name', 'duration', 'number_of_questions', 'subject']

class SubjectSerializers(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id','name']

class ExamQuestionMapSerializers(serializers.ModelSerializer):
    class Meta:
        model = ExamQuestionMap
        fields = []

class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = [ 'id', 'start_time', 'exam'] 

class AdviceSerializer(serializers.ModelSerializer):
    query_string = serializers.CharField(required=True)
    class Meta:
        fields = ['query_string']
    
