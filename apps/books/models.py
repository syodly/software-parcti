from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.

class Book(models.Model):
    title = models.CharField('书名', max_length=200)
    authors = models.CharField('作者', max_length=200)
    isbn = models.CharField('ISBN', max_length=13, unique=True)
    publisher = models.CharField('出版社', max_length=200)
    publication_date = models.DateField('出版日期')
    introduction = models.TextField('简介')
    cover = models.ImageField('封面', upload_to='book_covers/', null=True, blank=True)
    quantity = models.PositiveIntegerField('库存数量', default=0)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '图书'
        verbose_name_plural = '图书'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Category(models.Model):
    code = models.CharField('分类编码', max_length=20, unique=True)
    name = models.CharField('分类名称', max_length=50)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name='父分类')
    
    class Meta:
        verbose_name = '图书分类'
        verbose_name_plural = '图书分类'

    def __str__(self):
        return self.name
