import django_tables2 as tables

from .models import QuestionAttempt


class QuestionAttemptTable(tables.Table):
    class Meta:
        model = QuestionAttempt
        template_name = "django_tables2/bootstrap4.html"
        # TODO: improve to support other question types (open ended)
        fields = ("id", "question", "multiplechoice_answer", "answer_content")
        order_by = "id"

    def before_render(self, request):
        self.columns.hide("id")
