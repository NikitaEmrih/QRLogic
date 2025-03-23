from django.shortcuts import render, get_object_or_404
from createqr_app.models import QrCode
import datetime,os
from user_app.models import Profile
from QRLogic import settings
from django.http import HttpRequest
# from django.contrib import now
# Create your views here.

def render_yourqr_app(request: HttpRequest):
    # Створюємо словник контексту з початковим значенням
    context = {'page': 'myqr'}

    # Отримуємо профіль користувача
    profile = Profile.objects.get(user=request.user)
    
    # Отримуємо всі QR-коди, що належать користувачеві
    qrcodess = QrCode.objects.filter(owner=request.user.profile)
    
    # Отримуємо QR-коди користувача та сортуємо їх за датою створення (від новішого до старішого)
    qrcodes = QrCode.objects.filter(owner=profile).order_by('-create_date')
    
    # Перевіряємо кожен QR-код у списку
    for qr in qrcodess:
        # Якщо дата закінчення QR-коду не співпадає з поточною датою, оновлюємо контекст
        if qr.expire_date != datetime.datetime.now():
            context = {'page': 'myqr', 'qrcodes': qrcodess}

    # Повторно отримуємо відфільтрований список QR-кодів
    qrcodes = QrCode.objects.filter(owner=profile).order_by('-create_date')

    # Перевіряємо, чи є запит POST і чи містить він запит на видалення QR-коду
    if request.method == "POST" and "delete_qr" in request.POST:
        # Отримуємо ID QR-коду для видалення
        qr_id = request.POST.get("delete_qr")
        # Отримуємо QR-код або видаємо помилку 404, якщо він не знайдений
        qr = get_object_or_404(QrCode, id=qr_id, owner__user=request.user)
         
        # Формуємо шлях до файлу QR-коду
        file_path = os.path.join(settings.MEDIA_ROOT, f"{request.user.username}_{request.user.id}", qr.name)
        
        # Перевіряємо, чи файл існує, і видаляємо його
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Видаляємо QR-код із бази даних
        qr.delete()

    # Перевіряємо, чи є запит POST
    if request.method == "POST":
        # Отримуємо значення фільтра за датою з POST-запиту
        date_filter = request.POST.get('date_filter')
        if date_filter:  
            # Конвертуємо отримане значення у формат дати
            selected_date = datetime.datetime.strptime(date_filter, "%Y-%m-%d").date()
            # Фільтруємо QR-коди за обраною датою
            qrcodes = qrcodes.filter(create_date__date=selected_date)
    
    # Отримуємо значення фільтра за URL
    url_filter = request.POST.get('url_filter')
    if url_filter:
        # Фільтруємо QR-коди, які містять заданий URL
        qrcodes = qrcodes.filter(url__icontains=url_filter)

    # Створюємо список для збереження інформації про зображення QR-кодів
    qr_images = []
    for qr in qrcodes:
        # Формуємо URL-адресу для зображення QR-коду
        image_url = f"{settings.MEDIA_URL}{request.user.username}_{request.user.id}/{qr.name}"  
        qr_images.append({
            'name': qr.name,
            'image_url': image_url,
            'url': qr.url,
            'date': qr.create_date
        })

    # Оновлюємо контекст сторінки, додаючи QR-коди та їхні зображення
    context = {
        'page': 'myqr',
        'qrcodes': qrcodes,
        'qr_images': qr_images
    }

    # Якщо користувач автентифікований, відображаємо сторінку QR-кодів
    if request.user.is_authenticated:
        return render(request, 'yourqr_app/yourqrr.html', context=context)
    
    # Якщо користувач не авторизований, перенаправляємо на сторінку автентифікації
    else:
        return render(request, 'createqr_app/authentication_required.html', context=context)