from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import AuditLog, SystemSettings, User_Profile
from .service.dashboard import service_dashboard


@login_required
def dashboard(request):
    """Dashboard admin dengan crypto analysis"""
    log_activity(request.user, "view", "Dashboard", "Viewing dashboard", request)

    context = service_dashboard()
    return render(request, "admin_app/dashboard-chart.html", context)


def get_client_ip(request):
    """Dapatkan IP address dari request"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def log_activity(user, action, model_name, description, request=None, object_id=None):
    """Log aktivitas user"""
    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=object_id,
        description=description,
        ip_address=get_client_ip(request) if request else None,
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500] if request else "",
    )


@require_http_methods(["GET", "POST"])
def login_view(request):
    """View untuk login"""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            log_activity(user, "login", "Auth", f"User {username} login", request)
            messages.success(
                request, f"Selamat datang {user.get_full_name() or user.username}!"
            )
            return redirect("dashboard")
        else:
            messages.error(request, "Username atau password salah!")

    return render(request, "admin_app/login.html")


@login_required
@require_http_methods(["GET"])
def logout_view(request):
    """View untuk logout"""
    user = request.user
    username = user.username
    logout(request)
    log_activity(user, "logout", "Auth", f"User {username} logout", request)
    messages.success(request, "Anda telah logout!")
    return redirect("login")


@login_required
def user_list(request):
    """Daftar semua user"""
    log_activity(request.user, "view", "User", "Viewing user list", request)

    search_query = request.GET.get("q", "")
    users = User.objects.all().select_related("profile")

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(email__icontains=search_query)
        )

    paginator = Paginator(users, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "total_users": User.objects.count(),
    }

    return render(request, "admin_app/user_list.html", context)


@login_required
def user_detail(request, user_id):
    """Detail user"""
    user = get_object_or_404(User, pk=user_id)
    log_activity(
        request.user, "view", "User", f"Viewing user {user.username}", request, user_id
    )

    try:
        profile = user.profile
    except User_Profile.DoesNotExist:
        profile = User_Profile.objects.create(user=user)

    context = {
        "user": user,
        "profile": profile,
    }

    return render(request, "admin_app/user_detail.html", context)


@login_required
def user_edit(request, user_id):
    """Edit user"""
    user = get_object_or_404(User, pk=user_id)

    if not request.user.is_staff and request.user != user:
        messages.error(request, "Anda tidak memiliki izin untuk mengedit user ini!")
        return redirect("user_detail", user_id=user_id)

    try:
        profile = user.profile
    except User_Profile.DoesNotExist:
        profile = User_Profile.objects.create(user=user)

    if request.method == "POST":
        user.first_name = request.POST.get("first_name", "")
        user.last_name = request.POST.get("last_name", "")
        user.email = request.POST.get("email", "")
        user.save()

        profile.phone = request.POST.get("phone", "")
        profile.address = request.POST.get("address", "")
        profile.city = request.POST.get("city", "")
        profile.country = request.POST.get("country", "")
        profile.role = request.POST.get("role", profile.role)
        profile.save()

        log_activity(
            request.user,
            "update",
            "User",
            f"Updated user {user.username}",
            request,
            user_id,
        )
        messages.success(request, "Data user berhasil diperbarui!")
        return redirect("user_detail", user_id=user_id)

    context = {
        "user": user,
        "profile": profile,
        "role_choices": User_Profile.ROLE_CHOICES,
    }

    return render(request, "admin_app/user_edit.html", context)


@login_required
def audit_logs(request):
    """Lihat audit logs"""
    log_activity(request.user, "view", "AuditLog", "Viewing audit logs", request)

    filter_action = request.GET.get("action", "")
    filter_user = request.GET.get("user", "")
    search_query = request.GET.get("q", "")

    logs = AuditLog.objects.select_related("user").all()

    if filter_action:
        logs = logs.filter(action=filter_action)

    if filter_user:
        logs = logs.filter(user__username__icontains=filter_user)

    if search_query:
        logs = logs.filter(
            Q(description__icontains=search_query)
            | Q(model_name__icontains=search_query)
        )

    paginator = Paginator(logs, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    action_choices = [choice[0] for choice in AuditLog.ACTION_CHOICES]

    context = {
        "page_obj": page_obj,
        "filter_action": filter_action,
        "filter_user": filter_user,
        "search_query": search_query,
        "action_choices": action_choices,
    }

    return render(request, "admin_app/audit_logs.html", context)


@login_required
def settings_view(request):
    """System settings"""
    if not request.user.is_staff:
        messages.error(request, "Anda tidak memiliki izin mengakses halaman ini!")
        return redirect("dashboard")

    log_activity(
        request.user, "view", "SystemSettings", "Viewing system settings", request
    )

    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("setting_"):
                setting_key = key.replace("setting_", "")
                setting, created = SystemSettings.objects.get_or_create(key=setting_key)
                setting.value = value
                setting.save()

        log_activity(
            request.user, "update", "SystemSettings", "Updated system settings", request
        )
        messages.success(request, "Pengaturan berhasil disimpan!")
        return redirect("settings")

    settings_obj = SystemSettings.objects.all()
    context = {
        "settings": settings_obj,
    }

    return render(request, "admin_app/settings.html", context)
