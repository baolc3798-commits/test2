from django.contrib import admin
from .models import Module, Question, Choice, ExamConfiguration, QuizAttempt, UserAnswer

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('content', 'module', 'question_type', 'created_at')
    list_filter = ('module', 'question_type')
    search_fields = ('content',)
    inlines = [ChoiceInline]

class ExamConfigurationInline(admin.StackedInline):
    model = ExamConfiguration
    can_delete = False

class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)
    inlines = [ExamConfigurationInline]

class UserAnswerInline(admin.TabularInline):
    model = UserAnswer
    extra = 0
    readonly_fields = ('question', 'selected_choices', 'text_answer')
    can_delete = False

    def has_add_permission(self, request, obj):
        return False

class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'start_time', 'end_time', 'score')
    list_filter = ('module', 'user')
    readonly_fields = ('user', 'module', 'start_time', 'end_time', 'score')
    # inlines = [UserAnswerInline] # Can be heavy if many answers

admin.site.register(Module, ModuleAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuizAttempt, QuizAttemptAdmin)
# ExamConfiguration is inline in Module, but can also be registered if needed.
admin.site.register(ExamConfiguration)
