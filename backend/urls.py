from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from accounts.views import leave_log

from accounts.views import (
    current_user,
    register_teacher,
    register_student,
    create_room,
    list_rooms,
    list_teachers,
    list_students,
    manage_teacher,
    manage_student,
    manage_room,
    request_room,
    coordinator_requests,
    coordinator_action,
    my_leaves,
    apply_leave,
    coordinator_leave_action,
    coordinator_leave_requests
)
from accounts.views import hod_requests, hod_action
from accounts.views import my_room_requests
from accounts.views import room_booking_log

# --------------------
# URL patterns
# --------------------
urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT Auth
    path('api/login/', TokenObtainPairView.as_view()),
    path('api/refresh/', TokenRefreshView.as_view()),
    path('api/room-booking-log/', room_booking_log),

    # User / Auth
    path('api/me/', current_user),
    path('api/leave/log/', leave_log),

    # Registration
    path('api/register-teacher/', register_teacher),
    path('api/register-student/', register_student),

    # Rooms
    path('api/create-room/', create_room),
    path('api/rooms/', list_rooms),
    path('api/rooms/<int:room_id>/', manage_room),
    path('api/teachers/', list_teachers),
    path('api/teachers/<int:teacher_id>/', manage_teacher),
    path('api/students/', list_students),
    path('api/students/<int:student_id>/', manage_student),
    path('api/request-room/', request_room),

    # Coordinator approvals
    path('api/coordinator/requests/', coordinator_requests),
    path('api/coordinator/action/<int:booking_id>/', coordinator_action),
    path('api/hod/requests/', hod_requests),
    path('api/hod/action/<int:booking_id>/', hod_action),
    path('api/my-room-requests/', my_room_requests),
    path('api/leave/apply/', apply_leave),
    path('api/leave/my/', my_leaves),
    path('api/leave/coordinator/', coordinator_leave_requests),
    path('api/leave/coordinator/action/<int:leave_id>/', coordinator_leave_action),


]

# --------------------
# Media files (DEV only)
# --------------------
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
