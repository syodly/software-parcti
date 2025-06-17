from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden
from .models import Book
from apps.borrowing.models import BorrowRecord
from .forms import BookForm

# Create your views here.

def book_list(request):
    query = request.GET.get('q')
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(authors__icontains=query) |
            Q(isbn__icontains=query)
        )
    else:
        books = Book.objects.all()
    return render(request, 'books/book_list.html', {'books': books})

@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book_records = BorrowRecord.objects.filter(book=book).order_by('-borrow_date')[:5]
    return render(request, 'books/book_detail.html', {
        'book': book,
        'book_records': book_records
    })

@login_required
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            messages.success(request, '图书创建成功！')
            return redirect('books:book_detail', pk=book.pk)
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form, 'title': '新增图书'})

@login_required
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save()
            messages.success(request, '图书更新成功！')
            return redirect('books:book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form, 'title': '编辑图书'})

@login_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, '图书删除成功！')
        return redirect('books:book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})

@login_required
def borrow_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    user = request.user
    
    # 检查用户是否已达到最大借阅数量
    current_borrowed = BorrowRecord.objects.filter(user=user, returned=False).count()
    if current_borrowed >= user.max_books:
        messages.error(request, f'您已达到最大借阅数量限制（{user.max_books}本）')
        return redirect('books:book_detail', pk=pk)
    
    # 检查图书是否有库存
    if book.quantity <= 0:
        messages.error(request, '抱歉，该图书暂无库存')
        return redirect('books:book_detail', pk=pk)
    
    if request.method == 'POST':
        # 创建借阅记录
        from datetime import datetime, timedelta
        
        due_date = datetime.now() + timedelta(days=30)  # 设置30天的借阅期限
        
        BorrowRecord.objects.create(
            user=user,
            book=book,
            due_date=due_date
        )
        
        # 更新图书库存
        book.quantity -= 1
        book.save()
        
        messages.success(request, f'成功借阅《{book.title}》，请在{due_date.strftime("%Y-%m-%d")}前归还')
        return redirect('books:book_detail', pk=pk)
    
    return redirect('books:book_detail', pk=pk)
