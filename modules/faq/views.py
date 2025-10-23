from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import FAQ
from .decorators import faq_admin_required, is_faq_admin
from django.contrib import messages

def faq_list(request):
    faqs = FAQ.objects.all().order_by('-created_at')
    categories = FAQ.CATEGORY_CHOICES
    is_admin = is_faq_admin(request.user)
    
    context = {
        'faqs': faqs,
        'categories': categories,
        'is_admin': is_admin,
    }
    return render(request, 'faq.html', context)

def filter_faq(request):
    category = request.GET.get('category', 'all')
    
    if category == 'all':
        faqs = FAQ.objects.all().order_by('-created_at')
    else:
        faqs = FAQ.objects.filter(category=category).order_by('-created_at')
    
    is_admin = is_faq_admin(request.user)
    
    context = {
        'faqs': faqs,
        'is_admin': is_admin
    }
    
    return render(request, 'faq_list.html', context)

@login_required
@faq_admin_required
def add_faq(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        answer = request.POST.get('answer')
        category = request.POST.get('category')
        
        FAQ.objects.create(
            question=question,
            answer=answer,
            category=category,
            created_by=request.user
        )
        messages.success(request, 'FAQ berhasil ditambahkan')
        return redirect('faq:faq_list')
    
    categories = FAQ.CATEGORY_CHOICES
    return render(request, 'faq_form.html', {'categories': categories})

@login_required
@faq_admin_required
def edit_faq(request, faq_id):
    faq = get_object_or_404(FAQ, id=faq_id)
    
    if request.method == 'POST':
        faq.question = request.POST.get('question')
        faq.answer = request.POST.get('answer')
        faq.category = request.POST.get('category')
        faq.save()
        messages.success(request, 'FAQ berhasil diupdate')
        return redirect('faq:faq_list')
    
    categories = FAQ.CATEGORY_CHOICES
    context = {
        'faq': faq,
        'categories': categories
    }
    return render(request, 'faq_form.html', context)

@login_required
@faq_admin_required
def delete_faq(request, faq_id):
    faq = get_object_or_404(FAQ, id=faq_id)
    faq.delete()
    messages.success(request, 'FAQ berhasil dihapus')
    return redirect('faq:faq_list')