from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


# -------------------------------------------------
# Custom User Model
# -------------------------------------------------
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return self.username


# -------------------------------------------------
# Teacher Model
# -------------------------------------------------
class Teacher(models.Model):

    POSITION_CHOICES = (
        ('assistant_prof', 'Assistant Professor'),
        ('associate_prof', 'Associate Professor'),
        ('professor', 'Professor'),
    )

    COURSE_CHOICES = (
        ('MCA', 'MCA'),
        ('MMS', 'MMS'),
    )

    SEMESTER_CHOICES = (
        (1, 'Semester 1'),
        (2, 'Semester 2'),
        (3, 'Semester 3'),
        (4, 'Semester 4'),
    )

    DIVISION_CHOICES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile'
    )

    qualification = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)

    experience_years = models.PositiveIntegerField()
    phone = models.CharField(max_length=15)
    date_of_joining = models.DateField()

    # -------- Batch Coordinator --------
    is_batch_coordinator = models.BooleanField(default=False)
    coordinator_course = models.CharField(
        max_length=10, choices=COURSE_CHOICES, null=True, blank=True
    )
    coordinator_semester = models.IntegerField(
        choices=SEMESTER_CHOICES, null=True, blank=True
    )
    coordinator_division = models.CharField(
        max_length=1, choices=DIVISION_CHOICES, null=True, blank=True
    )

    # -------- HOD --------
    is_hod = models.BooleanField(default=False)
    hod_course = models.CharField(
        max_length=10, choices=COURSE_CHOICES, null=True, blank=True
    )

    def clean(self):
        # Batch coordinator rules
        if self.is_batch_coordinator:
            if not self.coordinator_course:
                raise ValidationError("Batch Coordinator must have a course.")
            if not self.coordinator_semester:
                raise ValidationError("Batch Coordinator must have a semester.")
            if not self.coordinator_division:
                raise ValidationError("Batch Coordinator must have a division.")
        else:
            if self.coordinator_course or self.coordinator_semester or self.coordinator_division:
                raise ValidationError(
                    "Coordinator fields allowed only if teacher is Batch Coordinator."
                )

        # HOD rules
        if self.is_hod and not self.hod_course:
            raise ValidationError("HOD must be assigned a course.")
        if not self.is_hod and self.hod_course:
            raise ValidationError("Only HOD can have hod_course.")

    def __str__(self):
        return self.user.username


# -------------------------------------------------
# Division Model
# -------------------------------------------------
class Division(models.Model):

    COURSE_CHOICES = (
        ('MCA', 'MCA'),
        ('MMS', 'MMS'),
    )

    SEMESTER_CHOICES = (
        (1, 'Semester 1'),
        (2, 'Semester 2'),
        (3, 'Semester 3'),
        (4, 'Semester 4'),
    )

    DIVISION_CHOICES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    )

    course = models.CharField(max_length=10, choices=COURSE_CHOICES)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    division = models.CharField(max_length=1, choices=DIVISION_CHOICES)

    class Meta:
        unique_together = ('course', 'semester', 'division')

    def __str__(self):
        return f"{self.course} - Sem {self.semester} - {self.division}"


# -------------------------------------------------
# Student Model
# -------------------------------------------------
class Student(models.Model):

    COURSE_CHOICES = (
        ('MCA', 'MCA'),
        ('MMS', 'MMS'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )

    roll_number = models.CharField(max_length=20, unique=True)
    course = models.CharField(max_length=10, choices=COURSE_CHOICES)

    semester = models.IntegerField(default=1, editable=False)

    division = models.ForeignKey(
        Division,
        on_delete=models.PROTECT,
        related_name='students'
    )

    admission_year = models.PositiveIntegerField()
    phone = models.CharField(max_length=15)
    address = models.TextField()

    guardian_name = models.CharField(max_length=100)
    guardian_phone = models.CharField(max_length=15)

    def clean(self):
        if self.semester != 1:
            raise ValidationError("New students must be in Semester 1.")

        if self.division.course != self.course:
            raise ValidationError("Division course mismatch.")

        if self.division.semester != 1:
            raise ValidationError("Division must be Semester 1.")

    def __str__(self):
        return f"{self.roll_number} - {self.user.username}"


# -------------------------------------------------
# Subject Model
# -------------------------------------------------
class Subject(models.Model):

    COURSE_CHOICES = (
        ('MCA', 'MCA'),
        ('MMS', 'MMS'),
    )

    SEMESTER_CHOICES = (
        (1, 'Semester 1'),
        (2, 'Semester 2'),
        (3, 'Semester 3'),
        (4, 'Semester 4'),
    )

    name = models.CharField(max_length=100)
    course = models.CharField(max_length=10, choices=COURSE_CHOICES)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)

    class Meta:
        unique_together = ('name', 'course', 'semester')

    def __str__(self):
        return f"{self.name} ({self.course} - Sem {self.semester})"


# -------------------------------------------------
# Subject Assignment Model
# -------------------------------------------------
class SubjectAssignment(models.Model):

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('subject', 'division')

    def clean(self):
        if self.subject.course != self.division.course:
            raise ValidationError("Subject and Division course must match.")
        if self.subject.semester != self.division.semester:
            raise ValidationError("Subject and Division semester must match.")

    def __str__(self):
        return f"{self.subject} - {self.division}"


# -------------------------------------------------
# Room Model
# -------------------------------------------------
class Room(models.Model):

    ROOM_TYPE_CHOICES = (
        ('seminar_hall', 'Seminar Hall'),
        ('tutorial_room', 'Tutorial Room'),
        ('lecture_hall', 'Lecture Hall'),
        ('lab', 'Lab'),
        ('auditorium', 'Auditorium'),
    )

    room_number = models.CharField(max_length=20, unique=True)
    capacity = models.PositiveIntegerField()
    room_type = models.CharField(max_length=30, choices=ROOM_TYPE_CHOICES)

    image = models.ImageField(
        upload_to='rooms/',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.room_number} - {self.get_room_type_display()}"


# -------------------------------------------------
# Room Booking Model
# -------------------------------------------------
class RoomBooking(models.Model):

    STATUS_CHOICES = (
        ('PENDING_COORDINATOR', 'Pending Batch Coordinator'),
        ('PENDING_HOD', 'Pending HOD'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    room = models.ForeignKey(Room, on_delete=models.PROTECT)

    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='room_requests'
    )

    # 🔑 Nullable because TEACHER requests don’t belong to a division
    division = models.ForeignKey(
        Division,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    purpose = models.CharField(max_length=200)
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='PENDING_COORDINATOR'
    )

    coordinator_approved = models.BooleanField(default=False)
    hod_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.room} | {self.booking_date} | {self.status}"
# -------------------------------------------------
# Student Leave Model
# -------------------------------------------------
class StudentLeave(models.Model):

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='leaves'
    )

    division = models.ForeignKey(
        Division,
        on_delete=models.PROTECT
    )

    reason = models.TextField()

    from_date = models.DateField()
    to_date = models.DateField()

    document = models.FileField(
        upload_to='leave_documents/',
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    coordinator_remark = models.TextField(
        null=True,
        blank=True
    )

    applied_at = models.DateTimeField(auto_now_add=True)
    decision_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.to_date < self.from_date:
            raise ValidationError("To date cannot be before From date.")

    def __str__(self):
        return f"{self.student.user.username} | {self.from_date} - {self.to_date} | {self.status}"
