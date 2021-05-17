from django.db import models

# Create your models here.
# Атрибуты опроса: название, дата старта, дата окончания, описание
class Survey(models.Model):
    title = models.CharField(max_length=100)
    start = models.DateField()
    finish = models.DateField()
    description = models.CharField(max_length=400)
# Атрибуты вопросов: текст вопроса,
# тип вопроса (ответ текстом, ответ с выбором одного варианта, ответ с выбором нескольких вариантов)
class Question(models.Model):
    text = models.CharField(max_length=400)
    survey = models.ForeignKey(Survey,on_delete=models.CASCADE)
    type = models.IntegerField()

class Answer(models.Model):
    text = models.CharField(max_length=200)
    user = models.IntegerField()
    question = models.ForeignKey(Question,on_delete=models.CASCADE)