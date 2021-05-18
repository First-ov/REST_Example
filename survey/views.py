from rest_framework import status,serializers
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from survey.models import Survey,Question,Answer,SurveyUser
from datetime import datetime


surveyparams=['id','title','start','finish', 'description']
questionparams=['id','survey','text','type']
answerparams=['text','user','question']

def GetUser(request):
    if not request.user.is_authenticated:
        # create anonymous user
        request.session.save()
        username = str(request.session.session_key) + '@dummy.com'
        try:
            user = SurveyUser.objects.create(username=username)
        except:
            user = SurveyUser.objects.get(username=username)
        return user.username
    else:
        request.user.id


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = surveyparams
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = questionparams
class AnswerSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()
    class Meta:
        model = Answer
        fields = answerparams
class AnswerWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = answerparams


@api_view(['GET','POST', 'UPDATE', 'DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAdminUser])
def AdminSurveyView(request):
    if request.method == 'GET':#все опросы
        surveys = Survey.objects.all()  # выбор всех объектов
        serializer = SurveySerializer(surveys, many=True)  # Serializer для вывода всех объектов
        return Response({"surveys":serializer.data},
                        status=status.HTTP_200_OK)
    if request.method == 'POST':
        for each in request.data:#добавление данных полей из параметра запроса
            if each not in surveyparams:
                 return Response('поле не существует', status=status.HTTP_400_BAD_REQUEST)#поле не существует
        serializer = SurveySerializer(data=request.data)
        if serializer.is_valid():#проверка JSON объекта
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'UPDATE':
        data={}#создание словаря обновляемых полей
        for each in request.data:#добавление данных полей из параметра запроса
            if each in surveyparams:
                data[each] = request.data[each]
            else:
                 return Response('поле не существует', status=status.HTTP_400_BAD_REQUEST)#поле не существует
        if not('id' in data):
            return Response('отсутсвует id', status=status.HTTP_400_BAD_REQUEST)#отсутсвует id
        if ('start' in data):
            return Response('Нельзя изменить дату начала у сществующего опроса',
                            status=status.HTTP_400_BAD_REQUEST)
        if Survey.objects.filter(id=data['id']).count():
            survey = Survey.objects.filter(id=data['id'])[0]#выбор объекта по id
            serializer = SurveySerializer(survey,
                                           data=request.data,
                                           partial=True)#Serializer для обновления объекта
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            else:
                Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        return Response('id не найден', status=status.HTTP_400_BAD_REQUEST)#id не найден

    elif request.method == 'DELETE':
        data = request.data
        if not 'id' in data:
            return Response('отсутсвует id', status=status.HTTP_400_BAD_REQUEST)#отсутсвует id
        if Survey.objects.filter(id=request.data['id']).count():
            Survey.objects.filter(id=request.data['id']).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('id не найден', status=status.HTTP_400_BAD_REQUEST)#id не найден


@api_view(['GET','POST', 'UPDATE', 'DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAdminUser])
def AdminQuestionView(request):
    if request.method == 'GET':
            questions = Question.objects.all()  # выбор всех объектов
            surveys=[]
            data={}
            for each in questions:
                if each.survey.id not in surveys:
                    surveys.append(each.survey.id)
            for each in surveys:
                serializer = QuestionSerializer(questions.filter(survey=each), many=True)
                data[each] = {'questions': serializer.data}
            return Response(data, status=status.HTTP_200_OK)
    if request.method == 'POST':
        for each in request.data:#добавление данных полей из параметра запроса
            if each not in questionparams:
                 return Response('поле не существует', status=status.HTTP_400_BAD_REQUEST)#поле не существует
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():  # проверка JSON объекта
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'UPDATE':
        data = {}  # создание словаря обновляемых полей
        for each in request.data:  # добавление данных полей из параметра запроса
            if each in questionparams:
                data[each] = request.data[each]
            else:
                return Response('поле не существует', status=status.HTTP_400_BAD_REQUEST)  # поле не существует
        if not ('id' in data):
            return Response('отсутсвует id', status=status.HTTP_400_BAD_REQUEST)  # отсутсвует id
        else:
            question = Question.objects.filter(id=data['id'])[0]  # выбор объекта по id
            serializer = QuestionSerializer(question,
                                          data=request.data,
                                          partial=True)  # Serializer для обновления объекта
            if serializer.is_valid():
                serializer.save()
                return Response('', status=status.HTTP_202_ACCEPTED)
            else:
                Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        return Response('id не найден', status=status.HTTP_400_BAD_REQUEST)  # id не найден
    elif request.method == 'DELETE':
        data = request.data
        if not 'id' in data:
            return Response('отсутсвует id', status=status.HTTP_400_BAD_REQUEST)  # отсутсвует id
        else:
            Question.objects.filter(id=request.data['id']).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('id не найден', status=status.HTTP_400_BAD_REQUEST)  # id не найден


@api_view(['GET'])#только актуальные
@authentication_classes([])
@permission_classes([])
def SurveyView(request):
    if request.method == 'GET':
        surveys = Survey.objects.all().filter(finish__gte=datetime.now(),
                                              start__lte=datetime.now())  # выбор всех активных опросов
        serializer = SurveySerializer(surveys, many=True)  # Serializer для вывода всех объектов
        return Response({"surveys": serializer.data},
                        status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def QuestionView(request):
    if request.method == 'GET':
        data = request.data
        if not 'survey' in data:
            return Response('', status=status.HTTP_400_BAD_REQUEST)#отсутсвует survey
        else:
            if Survey.objects.filter(id=data['survey']).count():
                questions = Question.objects.all().filter(survey=Survey.objects.filter(id=data['survey'])[0])  # выбор всех объектов
                serializer = QuestionSerializer(questions, many=True)  # Serializer для вывода всех объектов
                return Response(serializer.data,
                        status=status.HTTP_200_OK)
            else:
                Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def MyAnswersView(request):
    user = GetUser(request)
    if request.method == 'GET':
            answers = Answer.objects.all().filter(
                user=user)  # выбор всех объектов
            surveys=[]
            data={}
            for each in answers:
                if each.question.survey.id not in surveys:
                    surveys.append(each.question.survey.id)
            for each in surveys:
                serializer = AnswerSerializer(answers.filter(question__survey=each), many=True)
                data[each] = {'answers': serializer.data}
            return Response(data,status=status.HTTP_200_OK)
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def SendAnswerView(request):
    user = GetUser(request)
    if request.method == 'POST':
        data=request.data
        data["user"]=user
        if 'text' in data and 'question' in data:
            if Answer.objects.filter(question=data['question'],user=user).count():
                serializer = AnswerWriteSerializer(Answer.objects.filter(question=data['question'],user=user)[0],
                                                   data=request.data,partial=True)
                if serializer.is_valid():  # проверка JSON объекта
                  serializer.save()
                  return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
                else:
                  return Response(status=status.HTTP_400_BAD_REQUEST)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = AnswerWriteSerializer(data=request.data)
                if serializer.is_valid():  # проверка JSON объекта
                    serializer.save()
                    return Response('ответ принят', status=status.HTTP_201_CREATED)
                else:
                    return Response('', status=status.HTTP_400_BAD_REQUEST)
        else:
          return Response(status=status.HTTP_400_BAD_REQUEST)
