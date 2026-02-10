import json
import random
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .parameter.average_true_range import average_true_range
from .source.koingecko import market_chart

from .models import AuditLog, SystemSettings, User_Profile


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


def generate_crypto_candlestick_data():

    """Generate crypto candlestick data from CoinGecko API for last 24 hours"""
    market_data = market_chart('bitcoin', 'usd', '1')
    prices = market_data.get('prices', [])

    if not prices:
        return []

    # Group prices by hour
    hourly_data = {}
    for timestamp, price in prices:
        dt = datetime.fromtimestamp(timestamp / 1000)  # timestamp is in milliseconds
        hour_key = dt.replace(minute=0, second=0, microsecond=0)

        if hour_key not in hourly_data:
            hourly_data[hour_key] = {
                'open': price,
                'high': price,
                'low': price,
                'close': price
            }
        else:
            # Update high and low
            hourly_data[hour_key]['high'] = max(hourly_data[hour_key]['high'], price)
            hourly_data[hour_key]['low'] = min(hourly_data[hour_key]['low'], price)
            hourly_data[hour_key]['close'] = price  # Last price becomes close

    # Convert to candlestick format
    candlestick_data = []
    for hour_key, ohlc in sorted(hourly_data.items()):
        candlestick_data.append({
            "x": hour_key.strftime("%Y-%m-%d %H:%M"),
            "o": round(ohlc['open'], 2),
            "h": round(ohlc['high'], 2),
            "l": round(ohlc['low'], 2),
            "c": round(ohlc['close'], 2),
        })

    return candlestick_data


def analyze_crypto_data(candlestick_data):
    """Analyze crypto data and calculate indicators"""
    prices = [candle["c"] for candle in candlestick_data]

    # Calculate Simple Moving Average (SMA)
    sma_7 = sum(prices[-7:]) / 7
    sma_14 = sum(prices[-14:]) / 14

    # Calculate RSI (Relative Strength Index)
    gains = []
    losses = []
    for i in range(1, len(prices)):
        change = prices[i] - prices[i - 1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    avg_gain = sum(gains[-14:]) / 14 if len(gains) >= 14 else 0
    avg_loss = sum(losses[-14:]) / 14 if len(losses) >= 14 else 0

    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    rsi = 100 - (100 / (1 + rs)) if rs > 0 else 0

    # Get latest price and calculate change
    latest_price = prices[-1]
    prev_price = prices[-2] if len(prices) > 1 else latest_price
    price_change = latest_price - prev_price
    price_change_percent = (price_change / prev_price * 100) if prev_price != 0 else 0

    # Determine trend
    trend = "BULLISH" if sma_7 > sma_14 else "BEARISH"

    return {
        "latest_price": round(latest_price, 2),
        "price_change": round(price_change, 2),
        "price_change_percent": round(price_change_percent, 2),
        "sma_7": round(sma_7, 2),
        "sma_14": round(sma_14, 2),
        "rsi": round(rsi, 2),
        "trend": trend,
        "highest_price": round(max(prices), 2),
        "lowest_price": round(min(prices), 2),
    }


@login_required
def dashboard(request):
    """Dashboard admin dengan crypto analysis"""
    log_activity(request.user, "view", "Dashboard", "Viewing dashboard", request)

    # Statistics
    total_users = User.objects.count()
    total_admins = User_Profile.objects.filter(role="admin").count()
    total_logs = AuditLog.objects.count()
    recent_logs = AuditLog.objects.select_related("user")[:10]

    # Generate crypto candlestick data
    candlestick_data = generate_crypto_candlestick_data()

    print(candlestick_data)

    # Analyze crypto data
    crypto_analysis = analyze_crypto_data(candlestick_data)

    atr = average_true_range(candlestick_data, 14)

    context = {
        "total_users": total_users,
        "total_admins": total_admins,
        "total_logs": total_logs,
        "recent_logs": recent_logs,
        "candlestick_data": json.dumps(candlestick_data),
        "crypto_analysis": crypto_analysis,
    }

    return render(request, "admin_app/dashboard-chart.html", context)


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
