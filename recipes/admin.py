from django.contrib import admin
from .models import Recipe, Comment, SearchHistory


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'recipe', 'text', 'created_at')  # Поля для отображения в списке
    list_filter = ('created_at', 'author')  # Фильтры
    search_fields = ('text', 'author__username')  # Поиск по тексту и имени автора

    # Добавляеadм кастомное действие
    actions = ['delete_selected_comments']

    def delete_selected_comments(self, request, queryset):
        """
        Кастомное дейстasddвие для удаления выбранных комментариев.
        """
        deleted_count = queryset.count()  # Считаем количество удаляемых комментариев
        queryset.delete()  # Удаляем выбранные комментарии
        self.message_user(request, f"Успешно удалено {deleted_count} комментариев.")

    delete_selected_comments.short_description = "Удалить выбранные комментарии"


admin.site.register(Comment, CommentAdmin)
admin.site.register(Recipe)
admin.site.register(SearchHistory)
