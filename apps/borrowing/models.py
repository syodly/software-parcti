from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.books.models import Book

class BorrowRecord(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='borrow_records',
        verbose_name='借阅者'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='borrow_records',
        verbose_name='图书'
    )
    borrow_date = models.DateTimeField('借阅时间', default=timezone.now)
    due_date = models.DateTimeField('应还时间')
    return_date = models.DateTimeField('归还时间', null=True, blank=True)
    returned = models.BooleanField('是否已归还', default=False)
    
    class Meta:
        verbose_name = '借阅记录'
        verbose_name_plural = '借阅记录'
        ordering = ['-borrow_date']

    def __str__(self):
        return f'{self.user.username} 借阅 {self.book.title}'

    @property
    def is_overdue(self):
        if not self.returned and timezone.now() > self.due_date:
            return True
        return False 