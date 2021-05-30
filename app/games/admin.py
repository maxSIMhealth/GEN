from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline

from .models import Game, TextBoxesGame, TextBoxesTerm, TextBoxesItem, \
    MoveToColumnsGame, MoveToColumnsGroup, MoveToColumnsItem


class GameAdmin(TabbedTranslationAdmin):
    list_filter = ('type', 'author', 'section',)
    list_display = ('id', 'name', 'author', 'section', 'type',)


class TextBoxesTermInline(SortableInlineAdminMixin, TranslationTabularInline):
    model = TextBoxesTerm
    extra = 0


class TextBoxesItemInline(SortableInlineAdminMixin, TranslationTabularInline):
    model = TextBoxesItem
    extra = 0


class TextBoxesGameAdmin(GameAdmin):
    def get_queryset(self, request):
        return self.model.text_boxes.all()
    inlines = (TextBoxesTermInline, TextBoxesItemInline)


class MoveToColumnsItemAdmin(TabbedTranslationAdmin):
    list_filter = ('game',)
    list_display = ('id', 'text', 'game', )


class MoveToColumnsGroupAdmin(TabbedTranslationAdmin):
    list_filter = ('game',)
    list_display = ('game',)
    filter_horizontal = ('source_items', 'choice1_items', 'choice2_items')


class MoveToColumnsGameAdmin(GameAdmin):
    def get_queryset(self, request):
        return self.model.move_columns.all()


admin.site.register(Game, GameAdmin)
admin.site.register(TextBoxesGame, TextBoxesGameAdmin)
admin.site.register(MoveToColumnsGame, MoveToColumnsGameAdmin)
admin.site.register(MoveToColumnsItem, MoveToColumnsItemAdmin)
admin.site.register(MoveToColumnsGroup, MoveToColumnsGroupAdmin)
