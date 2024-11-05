# views/account_views.py
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages


@login_required
def delete_account(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)


        if user:
            user.delete()
            messages.success(request, "계정이 삭제되었습니다.")
            return redirect('home')
        else:
            messages.error(request, "비밀번호가 올바르지 않습니다.")

    return render(request, 'users/delete_account.html')
