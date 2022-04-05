from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline

from .forms import TextBoxesItemForm
from .models import Game, TextBoxesGame, TextBoxesTerm, TextBoxesItem, \
    MoveToColumnsGame, MoveToColumnsGroup, MoveToColumnsItem,\
    MatchTermsGame


class GameAdmin(TabbedTranslationAdmin):
    list_filter = ('type', 'author', 'section',)
    list_display = ('id', 'name', 'author', 'section', 'type',)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "author",
                    "section",
                    "start_date",
                    "end_date",
                    "show_related_content",
                    "published",
                )
            },
        ),
        (
            "Access control",
            {
                "fields": (
                    "access_restriction",
                    "author_access_override",

                )
            },
        ),
        (
            "Game settings",
            {
                "fields": (
                    "type",
                )
            }
        )
    )


class TextBoxesTermInline(SortableInlineAdminMixin, TranslationTabularInline):
    model = TextBoxesTerm
    extra = 0


class TextBoxesItemInline(SortableInlineAdminMixin, TranslationTabularInline):
    model = TextBoxesItem
    extra = 0
    form = TextBoxesItemForm


class TextBoxesGameAdmin(GameAdmin):
    def get_queryset(self, request):
        return self.model.text_boxes.all()

    inlines = (TextBoxesTermInline, TextBoxesItemInline)

    # setting type value to TB (Text Boxes)
    def get_form(self, request, obj=None, **kwargs):
        form = super(TextBoxesGameAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['type'].initial = 'TB'
        form.base_fields['type'].disabled = True
        return form


class MoveToColumnsItemAdmin(TabbedTranslationAdmin):
    list_filter = ('game',)
    list_display = ('id', 'text', 'game',)


class MoveToColumnsGroupAdmin(TabbedTranslationAdmin):
    list_filter = ('game',)
    list_display = ('game',)
    filter_horizontal = ('source_items', 'choice1_items', 'choice2_items')


class MoveToColumnsGameAdmin(GameAdmin):
    def get_queryset(self, request):
        return self.model.move_columns.all()

    # setting type value to MC (Move to Columns)
    def get_form(self, request, obj=None, **kwargs):
        form = super(MoveToColumnsGameAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['type'].initial = 'MC'
        form.base_fields['type'].disabled = True
        return form


class MatchTermsGameAdmin(GameAdmin):
    def get_queryset(self, request):
        return self.model.match_terms.all()

    inlines = (TextBoxesTermInline, TextBoxesItemInline)

    # setting type value to MC (Move to Columns)
    def get_form(self, request, obj=None, **kwargs):
        form = super(MatchTermsGameAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['type'].initial = 'MT'
        form.base_fields['type'].disabled = True
        return form


admin.site.register(Game, GameAdmin)
admin.site.register(TextBoxesGame, TextBoxesGameAdmin)
admin.site.register(MoveToColumnsGame, MoveToColumnsGameAdmin)
admin.site.register(MoveToColumnsItem, MoveToColumnsItemAdmin)
admin.site.register(MoveToColumnsGroup, MoveToColumnsGroupAdmin)
admin.site.register(MatchTermsGame, MatchTermsGameAdmin)
