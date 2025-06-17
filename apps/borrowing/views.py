from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import BorrowRecord
from apps.books.models import Book

@login_required
def my_borrowings(request):
    active_borrowings = BorrowRecord.objects.filter(
        user=request.user,
        returned=False
    ).select_related('book')
    
    history_borrowings = BorrowRecord.objects.filter(
        user=request.user,
        returned=True
    ).select_related('book').order_by('-return_date')[:10]
    
    return render(request, 'borrowing/my_borrowings.html', {
        'active_borrowings': active_borrowings,
        'history_borrowings': history_borrowings
    })

@login_required
def borrow_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    user = request.user
    
    # 检查用户是否已达到最大借阅数量
    current_borrowed = BorrowRecord.objects.filter(
        user=user,
        returned=False
    ).count()
    
    if current_borrowed >= user.max_books:
        messages.error(request, f'您已达到最大借阅数量限制（{user.max_books}本）')
        return redirect('books:book_detail', pk=pk)
    
    # 检查图书是否有库存
    if book.quantity <= 0:
        messages.error(request, '抱歉，该图书暂无库存')
        return redirect('books:book_detail', pk=pk)
    
    if request.method == 'POST':
        # 创建借阅记录
        due_date = timezone.now() + timedelta(days=30)  # 设置30天的借阅期限
        
        BorrowRecord.objects.create(
            user=user,
            book=book,
            due_date=due_date
        )
        
        # 更新图书库存
        book.quantity -= 1
        book.save()
        
        messages.success(request, f'成功借阅《{book.title}》，请在{due_date.strftime("%Y-%m-%d")}前归还')
        return redirect('borrowing:my_borrowings')
    
    return redirect('books:book_detail', pk=pk)

@login_required
def return_book(request, pk):
    borrow_record = get_object_or_404(
        BorrowRecord,
        pk=pk,
        user=request.user,
        returned=False
    )
    
    if request.method == 'POST':
        # 更新借阅记录
        borrow_record.returned = True
        borrow_record.return_date = timezone.now()
        borrow_record.save()
        
        # 更新图书库存
        book = borrow_record.book
        book.quantity += 1
        book.save()
        
        messages.success(request, f'《{book.title}》已成功归还')
    
    return redirect('borrowing:my_borrowings') 