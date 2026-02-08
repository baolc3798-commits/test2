from django.db import models
from django.conf import settings

class Module(models.Model):
    title = models.CharField(max_length=255, verbose_name="Tên Module")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Danh sách Module"

class Question(models.Model):
    QUESTION_TYPES = (
        ('single', 'Trắc nghiệm 1 đáp án'),
        ('multiple', 'Trắc nghiệm nhiều đáp án'),
        ('text', 'Trả lời ngắn'),
    )
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='questions', verbose_name="Thuộc Module")
    content = models.TextField(verbose_name="Nội dung câu hỏi")
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='single', verbose_name="Loại câu hỏi")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_question_type_display()}] {self.content[:50]}..."

    class Meta:
        verbose_name = "Câu hỏi"
        verbose_name_plural = "Danh sách Câu hỏi"

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', verbose_name="Câu hỏi")
    content = models.CharField(max_length=255, verbose_name="Nội dung đáp án")
    is_correct = models.BooleanField(default=False, verbose_name="Là đáp án đúng")

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = "Đáp án"
        verbose_name_plural = "Danh sách Đáp án"

class ExamConfiguration(models.Model):
    RESULT_MODES = (
        ('immediate', 'Hiển thị ngay sau mỗi câu'),
        ('after_submit', 'Hiển thị sau khi nộp bài'),
        ('hidden', 'Không hiển thị kết quả'),
    )
    module = models.OneToOneField(Module, on_delete=models.CASCADE, related_name='exam_config', verbose_name="Module")
    time_limit = models.PositiveIntegerField(help_text="Thời gian làm bài (phút). 0 là không giới hạn.", default=0, verbose_name="Thời gian (phút)")
    show_result_mode = models.CharField(max_length=20, choices=RESULT_MODES, default='after_submit', verbose_name="Chế độ hiển thị kết quả")
    randomize_questions = models.BooleanField(default=False, verbose_name="Trộn câu hỏi")

    def __str__(self):
        return f"Cấu hình thi cho {self.module.title}"

    class Meta:
        verbose_name = "Cấu hình bài thi"
        verbose_name_plural = "Cấu hình bài thi"

class QuizAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attempts', verbose_name="Học viên")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='attempts', verbose_name="Module")
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="Bắt đầu")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Kết thúc")
    score = models.FloatField(default=0.0, verbose_name="Điểm số")
    question_order = models.TextField(blank=True, null=True, help_text="Danh sách ID câu hỏi theo thứ tự, ngăn cách bởi dấu phẩy")
    current_question_index = models.IntegerField(default=0, verbose_name="Câu hỏi hiện tại")

    def __str__(self):
        return f"{self.user.username} - {self.module.title}"

    class Meta:
        verbose_name = "Lượt thi"
        verbose_name_plural = "Lịch sử thi"

class UserAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choices = models.ManyToManyField(Choice, blank=True)
    text_answer = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Answer for {self.question.id}"
