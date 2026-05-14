from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Doctor, Appointment, Patient
from .forms import UserRegistrationForm

def index(request):
    return render(request, 'doctor/index.html')

def profile(request):
    query = request.GET.get('q', '')    
    if query:
        doctors = Doctor.objects.filter(
            Q(name__icontains=query) |
            Q(specialty__icontains=query) |
            Q(location__icontains=query)
        )
    else:
        doctors = Doctor.objects.all()
    return render(request, 'doctor/profile.html', {'doctors': doctors, 'query': query})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user, profile = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'doctor/register.html', {'form': form})

@login_required
def dashboard_redirect(request):
    if hasattr(request.user, 'doctor'):
        return redirect('doctor_dashboard')
    return redirect('patient_dashboard')

@login_required
def patient_dashboard(request):
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        messages.error(request, 'Patient profile not found.')
        return redirect('index')
    
    appointments = Appointment.objects.filter(patient=patient).order_by('-date', '-time')
    return render(request, 'doctor/patient_dashboard.html', {'patient': patient, 'appointments': appointments})

@login_required
def doctor_dashboard(request):
    try:
        doctor = request.user.doctor
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('index')
    
    if request.method == 'POST':
        if 'toggle_availability' in request.POST:
            doctor.availability = not doctor.availability
            doctor.save()
            status = 'Available' if doctor.availability else 'Unavailable'
            messages.success(request, f'Status updated to {status}.')
        elif 'update_status' in request.POST:
            appt_id = request.POST.get('appointment_id')
            new_status = request.POST.get('status')
            appt = get_object_or_404(Appointment, id=appt_id, doctor=doctor)
            appt.status = new_status
            appt.save()
            messages.success(request, f'Appointment status updated to {new_status}.')
        
        return redirect('doctor_dashboard')
        
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-date', '-time')
    return render(request, 'doctor/doctor_dashboard.html', {'doctor': doctor, 'appointments': appointments})

@login_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        messages.error(request, 'Only patients can book appointments.')
        return redirect('dashboard')

    if request.method == 'POST':
        date = request.POST.get('date')
        time = request.POST.get('time')
        
        if date and time:
            Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                date=date,
                time=time
            )
            messages.success(request, f'Appointment booked successfully with Dr. {doctor.name}!')
            return redirect('dashboard')
            
    return render(request, 'doctor/book_appointment.html', {'doctor': doctor})

@login_required
def my_appointments(request):
    return redirect('dashboard')
