# Generated by Django 4.0.10 on 2024-08-01 14:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('duration', models.DurationField()),
                ('number_of_questions', models.PositiveIntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('image_path', models.CharField(blank=True, max_length=255, null=True)),
                ('answer_a', models.CharField(max_length=255)),
                ('answer_b', models.CharField(max_length=255)),
                ('answer_c', models.CharField(max_length=255)),
                ('answer_d', models.CharField(max_length=255)),
                ('mark', models.DecimalField(decimal_places=2, max_digits=5)),
                ('mix_choices', models.BooleanField(default=False)),
                ('correct_answer', models.CharField(max_length=1)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.subject')),
            ],
        ),
        migrations.CreateModel(
            name='ExamQuestionMap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.exam')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.question')),
            ],
        ),
        migrations.AddField(
            model_name='exam',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exams', to='exam.subject'),
        ),
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exam.exam')),
            ],
        ),
    ]