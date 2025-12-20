from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import FAQ
from .decorators import faq_admin_required, is_faq_admin
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
import json

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


# Fungsi semua FAQ dalam format JSON
def show_json(request):
    data = FAQ.objects.all().order_by('-created_at')
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

# Fungsi FAQ berdasarkan kategori
def show_json_by_category(request, category):
    data = FAQ.objects.filter(category=category).order_by('-created_at')
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

# Fungsi create FAQ Flutter
@csrf_exempt
def create_faq_flutter(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get("question", "")
        answer = data.get("answer", "")
        category = data.get("category", "")
        
        new_faq = FAQ.objects.create(
            question=question,
            answer=answer,
            category=category,
            created_by=request.user if request.user.is_authenticated else None
        )
        new_faq.save()

        return JsonResponse({"status": "success", "id": str(new_faq.id)}, status=200)
    else:
        return JsonResponse({"status": "error"}, status=401)

# Fungsi delete FAQ Flutter
@csrf_exempt
def delete_faq_flutter(request, faq_id):
    if request.method == 'POST':
        try:
            faq = FAQ.objects.get(id=faq_id)
            faq.delete()
            return JsonResponse({"status": "success"}, status=200)
        except FAQ.DoesNotExist:
            return JsonResponse({"status": "error", "message": "FAQ not found"}, status=404)
    else:
        return JsonResponse({"status": "error"}, status=401)

# Fungsi update FAQ Flutter
@csrf_exempt
def update_faq_flutter(request, faq_id):
    if request.method == 'POST':
        try:
            faq = FAQ.objects.get(id=faq_id)
            data = json.loads(request.body)
            
            faq.question = data.get("question", faq.question)
            faq.answer = data.get("answer", faq.answer)
            faq.category = data.get("category", faq.category)
            faq.save()
            
            return JsonResponse({"status": "success"}, status=200)
        except FAQ.DoesNotExist:
            return JsonResponse({"status": "error", "message": "FAQ not found"}, status=404)
        except ValueError:
            return JsonResponse({"status": "error", "message": "Invalid UUID"}, status=400)
    else:
        return JsonResponse({"status": "error"}, status=401)