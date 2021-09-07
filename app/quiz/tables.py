import django_tables2 as tables
from .models import QuestionAttempt

class QuestionAttemptTable(tables.Table):
    class Meta:
        model = QuestionAttempt
        template_name = "django_tables2/bootstrap4.html"
        fields = ("id", "question", "multiplechoice_answer", "answer_content")