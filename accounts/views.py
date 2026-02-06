from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
    parser_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser

from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from .models import (
    User,
    Teacher,
    Student,
    Division,
    Room,
    RoomBooking,
)

# =================================================
# AUTH / USER
# =================================================

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def current_user(request):
    response_data = {
        "username": request.user.username,
        "role": request.user.role
    }
    
    # Add teacher-specific fields if user is a teacher
    if request.user.role == 'teacher':
        try:
            teacher = request.user.teacher_profile
            response_data["is_batch_coordinator"] = teacher.is_batch_coordinator
            response_data["is_hod"] = teacher.is_hod
        except:
            response_data["is_batch_coordinator"] = False
            response_data["is_hod"] = False
    
    return Response(response_data)


# =================================================
# TEACHER REGISTRATION (ADMIN)
# =================================================

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def register_teacher(request):

    if request.user.role != 'admin':
        return Response({"error": "Only admin allowed"}, status=403)

    data = request.data

    try:
        # Check if username already exists
        if User.objects.filter(username=data["username"]).exists():
            return Response({"error": f"Username '{data['username']}' is already taken. Please choose a different username."}, status=400)

        user = User.objects.create(
            username=data["username"],
            password=make_password(data["password"]),
            role="teacher"
        )

        teacher = Teacher(
            user=user,
            qualification=data["qualification"],
            department=data["department"],
            position=data["position"],
            experience_years=data["experience_years"],
            phone=data["phone"],
            date_of_joining=data["date_of_joining"],

            is_hod=bool(data.get("is_hod")),
            hod_course=data.get("hod_course"),

            is_batch_coordinator=bool(data.get("is_batch_coordinator")),
            coordinator_course=data.get("coordinator_course"),
            coordinator_semester=data.get("coordinator_semester"),
            coordinator_division=data.get("coordinator_division"),
        )

        teacher.full_clean()
        teacher.save()

        return Response({"message": "Teacher registered"}, status=201)

    except IntegrityError as e:
        if 'username' in str(e):
            return Response({"error": f"Username '{data['username']}' is already taken. Please choose a different username."}, status=400)
        else:
            return Response({"error": f"Database error: {str(e)}"}, status=400)
    except ValidationError as e:
        return Response({"error": e.message_dict}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


# =================================================
# STUDENT REGISTRATION (ADMIN)
# =================================================

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def register_student(request):

    if request.user.role != 'admin':
        return Response({"error": "Only admin allowed"}, status=403)

    data = request.data

    try:
        # Check if username already exists
        if User.objects.filter(username=data["username"]).exists():
            return Response({"error": f"Username '{data['username']}' is already taken. Please choose a different username."}, status=400)

        # Check if roll number already exists
        if Student.objects.filter(roll_number=data["roll_number"]).exists():
            return Response({"error": f"Roll number '{data['roll_number']}' already exists. Please use a unique roll number."}, status=400)

        division, _ = Division.objects.get_or_create(
            course=data["course"],
            semester=1,
            division=data["division"]
        )

        user = User.objects.create(
            username=data["username"],
            password=make_password(data["password"]),
            role="student"
        )

        student = Student(
            user=user,
            roll_number=data["roll_number"],
            course=data["course"],
            division=division,
            admission_year=data["admission_year"],
            phone=data["phone"],
            address=data["address"],
            guardian_name=data["guardian_name"],
            guardian_phone=data["guardian_phone"],
        )

        student.full_clean()
        student.save()

        return Response({"message": "Student enrolled successfully"}, status=201)

    except IntegrityError as e:
        if 'username' in str(e):
            return Response({"error": f"Username '{data['username']}' is already taken. Please choose a different username."}, status=400)
        elif 'roll_number' in str(e):
            return Response({"error": f"Roll number '{data['roll_number']}' already exists."}, status=400)
        else:
            return Response({"error": f"Database error: {str(e)}"}, status=400)
    except ValidationError as e:
        return Response({"error": e.message_dict}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


# =================================================
# ROOM MANAGEMENT (ADMIN)
# =================================================

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_room(request):

    if request.user.role != 'admin':
        return Response({"error": "Only admin allowed"}, status=403)

    try:
        # Check if room number already exists
        if Room.objects.filter(room_number=request.data["room_number"]).exists():
            return Response({"error": f"Room number '{request.data['room_number']}' already exists. Please use a unique room number."}, status=400)

        room = Room(
            room_number=request.data["room_number"],
            capacity=int(request.data["capacity"]),
            room_type=request.data["room_type"],
            image=request.FILES.get("image"),
        )

        room.full_clean()
        room.save()

        return Response({"message": "Room created successfully"}, status=201)

    except IntegrityError as e:
        if 'room_number' in str(e):
            return Response({"error": f"Room number '{request.data['room_number']}' already exists. Please use a unique room number."}, status=400)
        else:
            return Response({"error": f"Database error: {str(e)}"}, status=400)
    except ValidationError as e:
        return Response({"error": e.message_dict}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_teachers(request):
    teachers = Teacher.objects.all()
    data = [
        {
            "id": teacher.id,
            "username": teacher.user.username,
            "qualification": teacher.qualification,
            "department": teacher.department,
            "position": teacher.position,
            "experience_years": teacher.experience_years,
            "phone": teacher.phone,
        }
        for teacher in teachers
    ]
    return Response(data)


@api_view(['PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def manage_teacher(request, teacher_id):
    if request.user.role != 'admin':
        return Response({"error": "Only admin allowed"}, status=403)

    try:
        teacher = Teacher.objects.get(id=teacher_id)
    except Teacher.DoesNotExist:
        return Response({"error": "Teacher not found"}, status=404)

    if request.method == 'PUT':
        # Update teacher
        teacher.qualification = request.data.get("qualification", teacher.qualification)
        teacher.department = request.data.get("department", teacher.department)
        teacher.position = request.data.get("position", teacher.position)
        teacher.experience_years = request.data.get("experience_years", teacher.experience_years)
        teacher.phone = request.data.get("phone", teacher.phone)
        teacher.save()
        return Response({"message": "Teacher updated successfully"}, status=200)

    elif request.method == 'DELETE':
        # Delete teacher and associated user
        user = teacher.user
        teacher.delete()
        user.delete()
        return Response({"message": "Teacher deleted successfully"}, status=200)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_students(request):
    students = Student.objects.all()
    data = [
        {
            "id": student.id,
            "username": student.user.username,
            "roll_number": student.roll_number,
            "course": student.division.course,
            "semester": student.division.semester,
            "phone": student.phone,
            "address": student.address,
        }
        for student in students
    ]
    return Response(data)


@api_view(['PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def manage_student(request, student_id):
    if request.user.role != 'admin':
        return Response({"error": "Only admin allowed"}, status=403)

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response({"error": "Student not found"}, status=404)

    if request.method == 'PUT':
        # Update student
        student.roll_number = request.data.get("roll_number", student.roll_number)
        student.phone = request.data.get("phone", student.phone)
        student.address = request.data.get("address", student.address)
        student.save()
        return Response({"message": "Student updated successfully"}, status=200)

    elif request.method == 'DELETE':
        # Delete student and associated user
        user = student.user
        student.delete()
        user.delete()
        return Response({"message": "Student deleted successfully"}, status=200)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_rooms(request):

    rooms = Room.objects.all()

    data = [
        {
            "id": room.id,
            "room_number": room.room_number,
            "room_type": room.room_type,
            "capacity": room.capacity,
            "image": room.image.url if room.image else None,  # ✅ REQUIRED
        }
        for room in rooms
    ]

    return Response(data)


@api_view(['PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def manage_room(request, room_id):
    if request.user.role != 'admin':
        return Response({"error": "Only admin allowed"}, status=403)

    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return Response({"error": "Room not found"}, status=404)

    if request.method == 'PUT':
        # Update room
        room.room_number = request.data.get("room_number", room.room_number)
        room.capacity = request.data.get("capacity", room.capacity)
        room.room_type = request.data.get("room_type", room.room_type)
        room.save()
        return Response({"message": "Room updated successfully"}, status=200)

    elif request.method == 'DELETE':
        # Delete room
        room.delete()
        return Response({"message": "Room deleted successfully"}, status=200)

# =================================================
# ROOM BOOKING (STUDENT / TEACHER)
# =================================================
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def request_room(request):

    user = request.user
    data = request.data

    try:
        room = Room.objects.get(id=data["room_id"])

        booking_date = data["booking_date"]
        start_time = data["start_time"]
        end_time = data["end_time"]

        # 🔴 CLASH CHECK (APPROVED BOOKINGS ONLY)
        clash_exists = RoomBooking.objects.filter(
            room=room,
            booking_date=booking_date,
            status="APPROVED",
            start_time__lt=end_time,
            end_time__gt=start_time,
        ).exists()

        if clash_exists:
            return Response(
                {
                    "error": "Room already booked for the selected date and time"
                },
                status=400
            )

        # -----------------------------
        # STUDENT FLOW → COORDINATOR
        # -----------------------------
        if user.role == 'student':
            RoomBooking.objects.create(
                room=room,
                requested_by=user,
                division=user.student_profile.division,
                purpose=data["purpose"],
                booking_date=booking_date,
                start_time=start_time,
                end_time=end_time,
                status="PENDING_COORDINATOR"
            )

            return Response(
                {"message": "Room request sent to Batch Coordinator"},
                status=201
            )

        # -----------------------------
        # TEACHER FLOW → HOD
        # -----------------------------
        elif user.role == 'teacher':
            RoomBooking.objects.create(
                room=room,
                requested_by=user,
                division=None,
                purpose=data["purpose"],
                booking_date=booking_date,
                start_time=start_time,
                end_time=end_time,
                status="PENDING_HOD"
            )

            return Response(
                {"message": "Room request sent to HOD"},
                status=201
            )

        else:
            return Response({"error": "Invalid role"}, status=400)

    except Room.DoesNotExist:
        return Response({"error": "Room not found"}, status=404)

    except Exception as e:
        return Response({"error": str(e)}, status=400)


# =================================================
# BATCH COORDINATOR APPROVAL
# =================================================
# =================================================
# Teacher: Leave Log (Read-only)
# =================================================
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def leave_log(request):

    user = request.user

    # ✅ ONLY BATCH COORDINATOR OR HOD
    if (
        user.role != 'teacher' or
        not (
            user.teacher_profile.is_batch_coordinator or
            user.teacher_profile.is_hod
        )
    ):
        return Response(
            {"error": "Only Batch Coordinators or HOD can view leave log"},
            status=403
        )

    leaves = StudentLeave.objects.select_related(
        'student__user',
        'division'
    ).filter(
        status="APPROVED"   # ✅ Only approved leaves
    ).order_by('-decision_at')

    data = []

    for l in leaves:
        data.append({
            "student": l.student.user.username,
            "division": f"{l.division.course} - Sem {l.division.semester} - {l.division.division}",
            "from": l.from_date,
            "to": l.to_date,
            "status": l.status,
            "remark": l.coordinator_remark,
            "decided_on": l.decision_at,
        })

    return Response(data)

# =================================================
# Room Booking Log (Approved only)
# =================================================
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def room_booking_log(request):

    bookings = RoomBooking.objects.select_related(
        'room',
        'requested_by',
        'division'
    ).filter(
        status="APPROVED"
    ).order_by('booking_date', 'start_time')

    data = []

    for b in bookings:
        data.append({
            "room": b.room.room_number,
            "room_type": b.room.get_room_type_display(),
            "date": b.booking_date,
            "start_time": b.start_time,
            "end_time": b.end_time,
            "booked_by": b.requested_by.username,
            "role": b.requested_by.role,
            "division": (
                f"{b.division.course} - Sem {b.division.semester} - {b.division.division}"
                if b.division else "N/A"
            ),
        })

    return Response(data)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def coordinator_requests(request):

    user = request.user

    if user.role != 'teacher' or not user.teacher_profile.is_batch_coordinator:
        return Response({"error": "Unauthorized"}, status=403)

    t = user.teacher_profile

    bookings = RoomBooking.objects.filter(
        status="PENDING_COORDINATOR",
        division__course=t.coordinator_course,
        division__semester=t.coordinator_semester,
        division__division=t.coordinator_division
    )

    data = [
        {
            "id": b.id,
            "room": b.room.room_number,
            "purpose": b.purpose,
            "date": b.booking_date,
            "time": f"{b.start_time} - {b.end_time}",
            "requested_by": b.requested_by.username,
        }
        for b in bookings
    ]

    return Response(data)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def coordinator_action(request, booking_id):

    user = request.user

    if user.role != 'teacher' or not user.teacher_profile.is_batch_coordinator:
        return Response({"error": "Unauthorized"}, status=403)

    action = request.data.get("action")

    try:
        booking = RoomBooking.objects.get(id=booking_id)

        if action == "approve":
            booking.status = "PENDING_HOD"
            booking.coordinator_approved = True
        elif action == "reject":
            booking.status = "REJECTED"
        else:
            return Response({"error": "Invalid action"}, status=400)

        booking.save()
        return Response({"message": "Action completed"})

    except RoomBooking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)
# =================================================
# HOD: View Pending Room Requests
# =================================================
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def hod_requests(request):

    user = request.user

    if user.role != 'teacher' or not user.teacher_profile.is_hod:
        return Response({"error": "Only HOD allowed"}, status=403)

    hod_course = user.teacher_profile.hod_course

    bookings = RoomBooking.objects.filter(
        status="PENDING_HOD"
    ).select_related("room", "requested_by", "division")

    data = []

    for b in bookings:
        # filter student bookings by HOD course
        if b.division and b.division.course != hod_course:
            continue

        data.append({
            "id": b.id,
            "room": b.room.room_number,
            "purpose": b.purpose,
            "date": b.booking_date,
            "time": f"{b.start_time} - {b.end_time}",
            "requested_by": b.requested_by.username,
            "role": b.requested_by.role,
            "division": (
                f"{b.division.course} - Sem {b.division.semester} - {b.division.division}"
                if b.division else "N/A"
            ),
        })

    return Response(data)
# =================================================
# HOD: Approve / Reject
# =================================================
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def hod_action(request, booking_id):

    user = request.user

    if user.role != 'teacher' or not user.teacher_profile.is_hod:
        return Response({"error": "Only HOD allowed"}, status=403)

    action = request.data.get("action")

    try:
        booking = RoomBooking.objects.get(id=booking_id)

        if action == "approve":
            booking.status = "APPROVED"
            booking.hod_approved = True
        elif action == "reject":
            booking.status = "REJECTED"
        else:
            return Response({"error": "Invalid action"}, status=400)

        booking.save()
        return Response({"message": "Final decision recorded"})

    except RoomBooking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)
# =================================================
# My Room Requests (Student / Teacher)
# =================================================
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def my_room_requests(request):

    user = request.user

    bookings = RoomBooking.objects.filter(
        requested_by=user
    ).select_related("room", "division")

    data = []

    for b in bookings:
        data.append({
            "id": b.id,
            "room": b.room.room_number,
            "room_type": b.room.get_room_type_display(),
            "purpose": b.purpose,
            "date": b.booking_date,
            "time": f"{b.start_time} - {b.end_time}",
            "status": b.status.replace("_", " "),
            "division": (
                f"{b.division.course} - Sem {b.division.semester} - {b.division.division}"
                if b.division else "N/A"
            ),
        })

    return Response(data)
from .models import StudentLeave
from django.utils.timezone import now

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def apply_leave(request):

    user = request.user

    if user.role != 'student':
        return Response({"error": "Only students can apply leave"}, status=403)

    data = request.data

    try:
        student = user.student_profile

        leave = StudentLeave(
            student=student,
            division=student.division,
            reason=data["reason"],
            from_date=data["from_date"],
            to_date=data["to_date"],
            document=request.FILES.get("document"),
        )

        leave.full_clean()
        leave.save()

        return Response(
            {"message": "Leave request sent to Batch Coordinator"},
            status=201
        )

    except ValidationError as e:
        return Response({"error": e.message_dict}, status=400)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def my_leaves(request):

    if request.user.role != 'student':
        return Response({"error": "Unauthorized"}, status=403)

    leaves = StudentLeave.objects.filter(
        student=request.user.student_profile
    ).order_by('-applied_at')

    data = [
        {
            "id": l.id,
            "reason": l.reason,
            "from": l.from_date,
            "to": l.to_date,
            "status": l.status,
            "remark": l.coordinator_remark,
        }
        for l in leaves
    ]

    return Response(data)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def coordinator_leave_requests(request):

    user = request.user

    if user.role != 'teacher' or not user.teacher_profile.is_batch_coordinator:
        return Response({"error": "Unauthorized"}, status=403)

    t = user.teacher_profile

    leaves = StudentLeave.objects.filter(
        status='PENDING',
        division__course=t.coordinator_course,
        division__semester=t.coordinator_semester,
        division__division=t.coordinator_division
    )

    data = [
        {
            "id": l.id,
            "student": l.student.user.username,
            "reason": l.reason,
            "from": l.from_date,
            "to": l.to_date,
            "document": l.document.url if l.document else None,
        }
        for l in leaves
    ]

    return Response(data)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def coordinator_leave_action(request, leave_id):

    user = request.user

    if user.role != 'teacher' or not user.teacher_profile.is_batch_coordinator:
        return Response({"error": "Unauthorized"}, status=403)

    action = request.data.get("action")
    remark = request.data.get("remark", "")

    try:
        leave = StudentLeave.objects.get(id=leave_id)

        if action == "approve":
            leave.status = "APPROVED"
        elif action == "reject":
            leave.status = "REJECTED"
        else:
            return Response({"error": "Invalid action"}, status=400)

        leave.coordinator_remark = remark
        leave.decision_at = now()
        leave.save()

        return Response({"message": "Leave decision recorded"})

    except StudentLeave.DoesNotExist:
        return Response({"error": "Leave not found"}, status=404)
