from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Module, QuizAttempt, Question, Choice, UserAnswer, ExamConfiguration
from django.utils import timezone
import random
import json

from django.db.models import Max

@login_required
def module_list(request):
    modules = Module.objects.all()
    user_attempts = QuizAttempt.objects.filter(user=request.user).order_by('-start_time')

    # Stats for Chart.js
    # Performance per module (labels: Module names, data: Max Score)
    performance_data = QuizAttempt.objects.filter(user=request.user).values('module__title').annotate(max_score=Max('score')).order_by('module__title')

    chart_labels = [item['module__title'] for item in performance_data]
    chart_data = [item['max_score'] for item in performance_data]

    return render(request, 'quiz/module_list.html', {
        'modules': modules,
        'user_attempts': user_attempts,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    })

@login_required
def start_quiz(request, module_id):
    module = get_object_or_404(Module, pk=module_id)

    # Check for existing active attempt (not ended)
    active_attempt = QuizAttempt.objects.filter(user=request.user, module=module, end_time__isnull=True).first()
    if active_attempt:
        return redirect('take_quiz', attempt_id=active_attempt.id, question_index=active_attempt.current_question_index + 1)

    questions = list(module.questions.values_list('id', flat=True))
    if not questions:
        return render(request, 'quiz/error.html', {'message': 'Module này chưa có câu hỏi nào.'})

    # Randomize if configured
    if hasattr(module, 'exam_config') and module.exam_config.randomize_questions:
        random.shuffle(questions)

    question_order = ",".join(map(str, questions))

    attempt = QuizAttempt.objects.create(
        user=request.user,
        module=module,
        question_order=question_order,
        current_question_index=0
    )

    return redirect('take_quiz', attempt_id=attempt.id, question_index=1)

@login_required
def take_quiz(request, attempt_id, question_index):
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id, user=request.user)

    if attempt.end_time:
        return redirect('quiz_result', attempt_id=attempt.id)

    # Check Time Limit
    if hasattr(attempt.module, 'exam_config') and attempt.module.exam_config.time_limit > 0:
        time_limit_seconds = attempt.module.exam_config.time_limit * 60
        elapsed_time = (timezone.now() - attempt.start_time).total_seconds()
        remaining_time = time_limit_seconds - elapsed_time

        if remaining_time <= 0:
            attempt.end_time = timezone.now()
            attempt.save()
            return redirect('quiz_result', attempt_id=attempt.id)
        remaining_time = int(remaining_time)
    else:
        remaining_time = None

    question_ids = attempt.question_order.split(',') if attempt.question_order else []
    total_questions = len(question_ids)

    if question_index < 1 or question_index > total_questions:
        return redirect('quiz_result', attempt_id=attempt.id)

    question_id = int(question_ids[question_index - 1])
    current_question = get_object_or_404(Question, pk=question_id)

    # Get or create user answer placeholder
    user_answer, created = UserAnswer.objects.get_or_create(attempt=attempt, question=current_question)

    if request.method == 'POST':
        action = request.POST.get('action') # 'next', 'finish', etc.

        # Save Answer
        if current_question.question_type in ['single', 'multiple']:
            selected_ids = request.POST.getlist('choice')
            user_answer.selected_choices.set(selected_ids)
        else:
            text = request.POST.get('text_answer')
            user_answer.text_answer = text
            user_answer.save()

        # Update current index
        attempt.current_question_index = question_index - 1 # 0-based
        attempt.save()

        # Handle Immediate Feedback
        config = getattr(attempt.module, 'exam_config', None)
        if config and config.show_result_mode == 'immediate':
             is_correct = False
             if current_question.question_type == 'single':
                 selected = user_answer.selected_choices.first()
                 if selected and selected.is_correct:
                     is_correct = True
             elif current_question.question_type == 'multiple':
                 correct_choices = set(current_question.choices.filter(is_correct=True).values_list('id', flat=True))
                 selected_choices = set(user_answer.selected_choices.values_list('id', flat=True))
                 if correct_choices == selected_choices and correct_choices:
                     is_correct = True

             # Render page again with feedback
             return render(request, 'quiz/take_quiz.html', {
                 'attempt': attempt,
                 'question': current_question,
                 'question_index': question_index,
                 'total_questions': total_questions,
                 'question_range': range(1, total_questions + 1),
                 'user_answer': user_answer,
                 'remaining_time': remaining_time, # Already int or None
                 'config': config,
                 'show_feedback': True,
                 'is_correct': is_correct
             })

        if question_index >= total_questions:
            attempt.end_time = timezone.now()
            attempt.save()
            return redirect('quiz_result', attempt_id=attempt.id)
        else:
            return redirect('take_quiz', attempt_id=attempt.id, question_index=question_index + 1)

    return render(request, 'quiz/take_quiz.html', {
        'attempt': attempt,
        'question': current_question,
        'question_index': question_index,
        'total_questions': total_questions,
        'question_range': range(1, total_questions + 1),
        'user_answer': user_answer,
        'remaining_time': remaining_time,
        'config': getattr(attempt.module, 'exam_config', None)
    })

@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id, user=request.user)

    if not attempt.end_time:
         attempt.end_time = timezone.now()
         attempt.save()

    question_ids = attempt.question_order.split(',') if attempt.question_order else []
    total_questions = len(question_ids)

    results = []
    correct_count = 0

    for q_id in question_ids:
        try:
            question = Question.objects.get(pk=q_id)
        except Question.DoesNotExist:
            continue

        answer = attempt.answers.filter(question=question).first()
        is_correct = False

        if answer:
            if question.question_type == 'single':
                selected = answer.selected_choices.first()
                if selected and selected.is_correct:
                    is_correct = True
            elif question.question_type == 'multiple':
                correct_choices = set(question.choices.filter(is_correct=True).values_list('id', flat=True))
                selected_choices = set(answer.selected_choices.values_list('id', flat=True))
                if correct_choices == selected_choices and correct_choices:
                    is_correct = True

        if is_correct:
            correct_count += 1

        results.append({
            'question': question,
            'is_correct': is_correct,
            'user_answer': answer,
            'skipped': answer is None
        })

    score_percent = (correct_count / total_questions) * 100 if total_questions > 0 else 0
    attempt.score = score_percent
    attempt.save()

    config = getattr(attempt.module, 'exam_config', None)
    show_details = config and config.show_result_mode != 'hidden'

    return render(request, 'quiz/result.html', {
        'attempt': attempt,
        'score_percent': score_percent,
        'correct_count': correct_count,
        'total_questions': total_questions,
        'results': results,
        'show_details': show_details
    })
