from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', '学生'),
        ('teacher', '教师'),
        ('admin', '管理员'),
    )
    
    user_type = models.CharField('用户类型', max_length=10, choices=USER_TYPE_CHOICES, default='student')
    student_id = models.CharField('学号/工号', max_length=20, unique=True, null=True, blank=True)
    phone_regex = RegexValidator(
        regex=r'^1[3-9]\d{9}$',
        message='请输入有效的手机号码'
    )
    phone = models.CharField('手机号码', max_length=11, validators=[phone_regex], blank=True, null=True)
    email = models.EmailField('邮箱', max_length=254, blank=True)
    max_books = models.IntegerField('最大借阅数量', default=5)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        swappable = 'AUTH_USER_MODEL'

    def save(self, *args, **kwargs):
        # 根据用户类型设置最大借阅数量
        if not self.pk:  # 只在创建时设置
            if self.user_type == 'student':
                self.max_books = 5
            elif self.user_type == 'teacher':
                self.max_books = 10
            elif self.user_type == 'admin':
                self.max_books = 15
        super().save(*args, **kwargs)
