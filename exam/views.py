from rest_framework import generics, mixins, status
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import ExamSerializers, SubjectSerializers, QuestionSerializers, ListQuestionSerializers, CalendarSerializer
from .models import Subject, Exam, Question, ExamQuestionMap, Calendar
from .utils import extract_docx_data
from decouple import config
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist, ValidationError
import random
from django.db.models import Q
import re
from .utils import ask
import json


#----------------Exam Class View------------------
# Create exam and also question for that exam to QuestionExamMap
class ExamCreateAPIView(generics.CreateAPIView, generics.RetrieveAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ExamSerializers

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            try:
                with transaction.atomic():
                    subject_id = request.data.get('subject')
                    subject = Subject.objects.get(pk=subject_id)
                    number_of_questions = serializer.validated_data['number_of_questions']
                    print(Question.objects.filter(subject_id=subject_id).count())
                    if number_of_questions > Question.objects.filter(subject_id=subject_id).count():
                        return Response({"message" : "Question in pool in less than number of questions"})

                    # Fetch random question IDs
                    question_ids = list(
                        Question.objects.filter(subject=subject).values_list('id', flat=True)
                    )

                    if len(question_ids) < number_of_questions:
                        raise ValidationError(
                            "Not enough questions available for the selected subject."
                        )

                    # Create (or update) the exam
                    exam, created = Exam.objects.update_or_create(
                        subject=subject,
                        name=serializer.validated_data['name'],
                        defaults={  
                            "duration": serializer.validated_data['duration'],
                            "number_of_questions": number_of_questions,
                        },
                    )

                    # Sample random question IDs
                    random_question_ids = random.sample(question_ids, number_of_questions)

                    # Create exam-question mappings
                    exam_question_maps = [
                        ExamQuestionMap(exam=exam, question_id=question_id)
                        for question_id in random_question_ids
                    ]
                    ExamQuestionMap.objects.bulk_create(exam_question_maps)

                    exam_serializer = ExamSerializers(exam)
                    status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
                    return Response(exam_serializer.data, status=status_code)
            except Subject.DoesNotExist:
                return Response({"message": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)
            except ValidationError as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Get all exams
class GetExamsAPIView(generics.ListAPIView):
    serializer_class = ExamSerializers
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Exam.objects.all()

#----------------Subject Class View------------------
# Create new subject
class SubjectListCreateAPIView(generics.CreateAPIView, generics.ListAPIView):
    queryset = Subject.objects.all()  # Use the model's manager
    serializer_class = SubjectSerializers

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            response.data = {
                "message": f"Subject {response.data.get('name')} created successfully"
            }
        return response
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

#----------------Questions Class View------------------
# Get all questions from bank questions
class QuestionCreateAPIView(generics.CreateAPIView):
    serializer_class = QuestionSerializers
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
   
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            blob_name = serializer.validated_data.get('blob_name')
            container_name = serializer.validated_data.get('container_name')

            try:
                with transaction.atomic():
                    
                    question_lst, exam_common_info = extract_docx_data(container_name, blob_name)
                    
                    subject_name = exam_common_info['subject']
                    subject, _ = Subject.objects.get_or_create(name=subject_name)

                    question_fields = ["content", "answer_a", "answer_b", "answer_c", "answer_d", "correct_answer", "mark", "unit", "mix_choices", "image_path"]
                    new_question_objs = []
                    _duplicated = []

                    for question in question_lst:
                        question_list = list(map(lambda x: re.sub("\n", " ",x).strip(), question))
                        question_list = list(map(lambda x: True if x.strip() == "Yes" else False if x.strip() == "No" else x, question_list))
                        question_dict = {field: question_list[i] for i, field in enumerate(question_fields)}
                        question_dict['subject'] = subject

                        existing_questions = Question.objects.filter(answer_a = question_dict['answer_a'],
                                                           answer_b = question_dict['answer_b'],
                                                           answer_c = question_dict['answer_c'],
                                                           answer_d = question_dict['answer_d'],
                                                           content = question_dict['content'])
                        
                        if not existing_questions:
                            new_question_objs.append(Question(**question_dict))
                        else:
                            print("Duplicate Question:", question_dict['content']) # Notify or log duplicate questions
                            _duplicated.append(question_dict['content'])

                    # Bulk create only the new questions
                    print(new_question_objs.__len__())
                    new_questions = Question.objects.bulk_create(new_question_objs)
                    print("okkk")
                    if len(_duplicated) > 0:
                        return Response({"message" : f"duplicated items {str.join(";", _duplicated)}"})

            except FileNotFoundError:
                return Response({"message": "File not found"}, status=status.HTTP_404_NOT_FOUND)
            except (KeyError, IndexError) as e:
                return Response({"message": f"Error parsing question data: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                return Response({"message": f"Subject '{subject_name}' not found"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:  
                return Response({"message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            get_quesions_serializer = ListQuestionSerializers(new_questions, many=True)
            
            return Response(get_quesions_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Get all questions from bank
class GetAllQuestionsFromBankAPIView(generics.ListAPIView):
    serializer_class = ListQuestionSerializers
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Question.objects.all()

# Get questions with specific exam id
class GetQuestionWithExamIDAPIView(generics.ListAPIView):
    serializer_class = ListQuestionSerializers
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        exam_id = self.kwargs['exam_id']
        try:
            exam = Exam.objects.get(id = exam_id)
        except Exception:
            return Response({"message" : "Exam with exam id is not exists"}, status= status.HTTP_400_BAD_REQUEST)
        question_ids = ExamQuestionMap.objects.filter(exam=exam).values_list('question_id', flat=True)
        questions = Question.objects.filter(id__in = question_ids)
        return questions

#----------------Calendar Class View------------------
# Create and get calendar
class CalendarListCreateAPIView(mixins.ListModelMixin,
                                mixins.CreateModelMixin,
                                generics.GenericAPIView):
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]  # Add authentication if needed

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data 

            # Extract relevant data for creating Calendar instance
            start_time = validated_data['start_time']
            exam = validated_data['exam']
            # Create the Calendar object
            Calendar.objects.create(exam=exam, start_time=start_time)

            return Response(
                {"message": f"Calendar created for exam: {exam.name}, start time: {start_time}"}, 
                status=status.HTTP_201_CREATED
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#----------------GEN AI-------------------------------
class AdviceQuestionListView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        val = [
                {
                    "id": 60,
                    "content": "See the figure and choose the right type of B2B E-Commerce [file:8435.jpg]",
                    "image_path": "Template.docx2.png",
                    "answer_a": "Sell-side B2B",
                    "answer_b": "Electronic Exchange",
                    "answer_c": "Buy-side B2B",
                    "answer_d": "Supply Chain Improvements and Collaborative Commerce",
                    "mark": "0.50",
                    "mix_choices": True,
                    "unit": "Chapter1",
                    "correct_answer": "B",
                    "subject": 2
                },
                {
                    "id": 61,
                    "content": "What is this website?",
                    "image_path": "Template.docx5.png",
                    "answer_a": "Microsoft website",
                    "answer_b": "X Website",
                    "answer_c": "Facebook",
                    "answer_d": "ICHelper",
                    "mark": "1.00",
                    "mix_choices": True,
                    "unit": "Chapter 2",
                    "correct_answer": "A",
                    "subject": 2
                },
                {
                    "id": 62,
                    "content": "Can you name this website?",
                    "image_path": "Template.docx10.png",
                    "answer_a": "Microsoft website",
                    "answer_b": "X Website",
                    "answer_c": "Facebook",
                    "answer_d": "ICHelper",
                    "mark": "1.00",
                    "mix_choices": True,
                    "unit": "Chapter 2",
                    "correct_answer": "A",
                    "subject": 2
                }
                ]
        answer = ask(str(val) + '\n Return id of similar question with in json format {int : list of int} where key is is question id if no context is match return "id" : [0], each question is in one object let make it mostly based on content')
        print(str)
        print(answer)
        try: 
            answer = json.loads(answer)
            return Response(answer, status=status.HTTP_202_ACCEPTED)
        except Exception: 
            return Response({'message' : 'No advice for duplicate question database now'}, status=status.HTTP_400_BAD_REQUEST)

#-----------------------------------------------------
exam_create_api_view = ExamCreateAPIView.as_view()
get_exams_api_view = GetExamsAPIView.as_view()
subject_list_create_api_view = SubjectListCreateAPIView.as_view()
question_create_api_view = QuestionCreateAPIView.as_view()
question_get_based_on_exam_view = GetQuestionWithExamIDAPIView.as_view()
list_create_calendar_view = CalendarListCreateAPIView.as_view()
get_all_questions_from_bank = GetAllQuestionsFromBankAPIView.as_view()
advice_question_list_view = AdviceQuestionListView.as_view()
        


