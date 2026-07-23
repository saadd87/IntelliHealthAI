from .forms import HealthRecordForm
import joblib
import os
import json
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import HealthRecord
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib import messages
from django.db.models import Count
import json
from django.db.models.functions import ExtractMonth
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from openpyxl import Workbook
from django.core.mail import send_mail
from django.conf import settings
from .utils import calculate_health_score

from ai.openrouter import ask_ai
from django.http import HttpResponse

def test_ai(request):
    try:
        answer = ask_ai("Hello! Introduce yourself in one sentence.")
        return HttpResponse(answer)
    except Exception as e:
        return HttpResponse(f"Error: {e}")

model_path = os.path.join(
    settings.BASE_DIR,
    'ml',
    'health_model.pkl'
)

from django.shortcuts import render
from ai.openrouter import ask_ai
from .models import HealthRecord


def ai_chat(request):

    answer = None

    if request.method == "POST":

        prompt = request.POST.get("prompt")

        latest = HealthRecord.objects.filter(
            user=request.user
        ).order_by("-id").first()

        if latest:

            full_prompt = f"""
You are IntelliHealth AI.

User's latest health record:

Age: {latest.age}
Height: {latest.height} cm
Weight: {latest.weight} kg
Blood Pressure: {latest.blood_pressure}
Glucose: {latest.glucose_level}
Predicted Risk: {latest.risk}

User Question:
{prompt}

Give a professional, easy-to-understand health recommendation.
Mention healthy lifestyle suggestions.
Do not prescribe medicines.
Advise consulting a doctor for serious concerns.
"""

        else:

            full_prompt = prompt

        answer = ask_ai(full_prompt)

    return render(
        request,
        "ai/chat.html",
        {
            "answer": answer
        }
    )

model = joblib.load(model_path)

from .models import HealthRecord
from ai.openrouter import ask_ai

def ai_report(request):

    latest = HealthRecord.objects.filter(
        user=request.user
    ).order_by("-id").first()

    if not latest:

        return render(
            request,
            "ai/report.html",
            {
                "report":"No health records found."
            }
        )

    prompt = f"""
You are IntelliHealth AI.

Generate a professional health report.

Patient Information

Age: {latest.age}

Height: {latest.height} cm

Weight: {latest.weight} kg

Blood Pressure: {latest.blood_pressure}

Glucose: {latest.glucose_level}

Predicted Risk: {latest.risk}

Generate the report in this format:

# Overall Health Summary

# Risk Assessment

# Diet Recommendations

# Exercise Plan

# Lifestyle Improvements

# Sleep Recommendations

# Hydration Advice

# Follow-up Suggestions

# Medical Disclaimer

Keep the report simple, professional and easy to understand.

Do not prescribe medicines.
"""

    report = ask_ai(prompt)

    return render(
        request,
        "ai/report.html",
        {
            "report": report
        }
    )

@login_required
def add_record(request):

    if request.method == 'POST':

        form = HealthRecordForm(request.POST)

        if form.is_valid():

            record = form.save(commit=False)
            record.user = request.user
            record.save()

            messages.success(
                request,
                "Health record added successfully."
            )

            return redirect('/')

    else:

        form = HealthRecordForm()

    return render(
        request,
        'health_records/add_record.html',
        {
            'form': form
        }
    )

@login_required
def my_records(request):

    records = HealthRecord.objects.filter(
        user=request.user
    ).order_by('-created_at')

    search = request.GET.get('search')

    if search:

        records = records.filter(
            age__icontains=search
        )

    bp = request.GET.get('bp')

    if bp:
        records = records.filter(
            blood_pressure__icontains=bp
        )

    glucose = request.GET.get('glucose')

    if glucose:
        records = records.filter(
            glucose_level=glucose
    )

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if from_date:
        records = records.filter(
            created_at__date__gte=from_date
    )

    if to_date:
        records = records.filter(
            created_at__date__lte=to_date
    )
        
    context = {

        'records': records,
        'search': search,
        'bp': bp,
        'glucose': glucose,
        'from_date': from_date,
        'to_date': to_date,

    }

    return render(

        request,
        'health_records/my_records.html',
        context

    )

@login_required
def edit_record(request, id):

    record = get_object_or_404(
        HealthRecord,
        id=id,
        user=request.user
    )

    if request.method == 'POST':

        record.age = request.POST['age']
        record.weight = request.POST['weight']
        record.height = request.POST['height']
        record.blood_pressure = request.POST['blood_pressure']
        record.glucose_level = request.POST['glucose_level']

        record.save()

        messages.success(
        request,
            "Health record updated successfully."
        )

        return redirect('/health/my-records/')

    return render(
        request,
        'health_records/edit_record.html',
        {'record': record}
    )

@login_required
def delete_record(request, id):

    record = get_object_or_404(
        HealthRecord,
        id=id,
        user=request.user
    )

    record.delete()

    messages.success(
        request,
            "Health record deleted successfully."
    )

    return redirect('/health/my-records/')

@login_required
def predict_risk(request, id):

    record = get_object_or_404(
        HealthRecord,
        id=id,
        user=request.user
    )

    prediction = model.predict([[
        record.age,
        record.weight,
        record.height,
        int(record.blood_pressure.split('/')[0]),
        record.glucose_level
    ]])

    risk_labels = {
        0: 'LOW RISK',
        1: 'MEDIUM RISK',
        2: 'HIGH RISK'
    }

    risk = risk_labels[prediction[0]]
    record.risk = risk
    record.save()

    return render(
        request,
        'health_records/prediction.html',
        {
            'record': record,
            'risk': risk
        }
    )

@login_required
def dashboard(request):

    records = HealthRecord.objects.filter(
        user=request.user
    )

    total_records = records.count()

    avg_weight = records.aggregate(
        Avg('weight')
    )['weight__avg']

    avg_glucose = records.aggregate(
        Avg('glucose_level')
    )['glucose_level__avg']

    latest_record = records.order_by(
        '-created_at'
    ).first()

    weights = list(records.values_list('weight', flat=True))
    glucose = list(records.values_list('glucose_level', flat=True))
    dates = [
        record.created_at.strftime("%d-%m")
        for record in records
    ]
    avg_weight = round(avg_weight, 1) if avg_weight else 0
    avg_glucose = round(avg_glucose, 1) if avg_glucose else 0

    

    risk_counts = HealthRecord.objects.filter(
    user=request.user
        ).values('risk').annotate(
    total=Count('risk')
    )

    risk_labels = []
    risk_values = []

    for item in risk_counts:
        risk_labels.append(item['risk'])
        risk_values.append(item['total'])

    monthly_data = records.annotate(
    month=ExtractMonth('created_at')
        ).values('month').annotate(
    total=Count('id')
        ).order_by('month')

    months = []
    monthly_counts = []

    for item in monthly_data:
        months.append(item['month'])
        monthly_counts.append(item['total'])

    if latest_record:
        health_score = calculate_health_score(latest_record)
    else:
        health_score = 0

 # Weight Status
    if latest_record.weight < 50:
        weight_status = "Underweight"
    elif latest_record.weight <= 90:
        weight_status = "Normal"
    else:
        weight_status = "Overweight"

# Glucose Status
    if latest_record.glucose_level < 70:
        glucose_status = "Low"
    elif latest_record.glucose_level <= 140:
        glucose_status = "Normal"
    else:
        glucose_status = "High"

# Recommendation
    if health_score >= 80:
        recommendation = "Excellent health. Keep maintaining your healthy lifestyle."

    elif health_score >= 60:
        recommendation = "Good health. Exercise regularly and eat a balanced diet."

    else:
        recommendation = "Health risk detected. Please consult your doctor and improve your lifestyle."

    context = {
    'total_records': total_records,
    'avg_weight': avg_weight,
    'avg_glucose': avg_glucose,
    'latest_record': latest_record,

    'dates': json.dumps(dates),
    'weights': json.dumps(weights),
    'glucose': json.dumps(glucose),
    'risk_labels': json.dumps(risk_labels),
    'risk_values': json.dumps(risk_values),
    'months': json.dumps(months),
    'monthly_counts': json.dumps(monthly_counts),
    'health_score': health_score,
    'weight_status': weight_status,
    'glucose_status': glucose_status,
    'recommendation': recommendation,
    }

    return render(
        request,
        'health_records/dashboard.html',
        context
    )


@login_required
def export_pdf(request):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="health_report.pdf"'

    pdf = SimpleDocTemplate(response)

    records = HealthRecord.objects.filter(user=request.user)

    data = [
        ['Age', 'Weight', 'Height', 'BP', 'Glucose', 'Risk']
    ]

    for record in records:
        data.append([
            record.age,
            record.weight,
            record.height,
            record.blood_pressure,
            record.glucose_level,
            record.risk
        ])

    table = Table(data)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))

    pdf.build([table])

    return response

@login_required
def export_excel(request):

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = (
        'attachment; filename="health_report.xlsx"'
    )

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Health Report"

    worksheet.append([
        'Age',
        'Weight',
        'Height',
        'Blood Pressure',
        'Glucose',
        'Risk'
    ])

    records = HealthRecord.objects.filter(user=request.user)

    for record in records:

        worksheet.append([
            record.age,
            record.weight,
            record.height,
            record.blood_pressure,
            record.glucose_level,
            record.risk
        ])

    workbook.save(response)

    return response

@login_required
def send_health_report(request):

    send_mail(
    subject='IntelliHealth AI - Health Report',

    message=f'''
Hello {request.user.username},

Your health report has been generated successfully.

Summary:

• Total Records: {HealthRecord.objects.filter(user=request.user).count()}

Please login to IntelliHealth AI to view your complete dashboard.

Thank you,
IntelliHealth AI Team
''',

    from_email=settings.DEFAULT_FROM_EMAIL,

    recipient_list=[request.user.email],

    fail_silently=False,
)

    messages.success(
        request,
        "Health report email sent successfully."
    )

    return redirect('/health/dashboard/')

from django.contrib.auth.decorators import login_required

@login_required
def ai_report(request):

    latest = HealthRecord.objects.filter(
        user=request.user
    ).order_by("-id").first()

    if not latest:
        return render(
            request,
            "ai/report.html",
            {
                "report": {
                    "summary": "No health records found.",
                    "risk": "-",
                    "diet": "-",
                    "exercise": "-",
                    "sleep": "-",
                    "hydration": "-",
                    "followup": "-",
                    "disclaimer": "-"
                },
                "health_score": 0
            }
        )

    score = calculate_health_score(latest)

    # ==========================
    # AI Prompt
    # ==========================

    prompt = f"""
You are IntelliHealth AI.

Patient Information

Age: {latest.age}
Height: {latest.height} cm
Weight: {latest.weight} kg
Blood Pressure: {latest.blood_pressure}
Glucose: {latest.glucose_level}
Predicted Risk: {latest.risk}

Health Score: {score}/100

Generate ONLY valid JSON in this format:

{{
"summary":"",
"risk":"Low",
"diet":"",
"exercise":"",
"sleep":"",
"hydration":"",
"followup":"",
"disclaimer":""
}}

Rules:

- Risk should be one of:
Low
Moderate
High

- Return ONLY JSON.

Do not use markdown.

Do not explain anything.

Return only JSON.
"""

    report = ask_ai(prompt)

    return render(
        request,
        "ai/report.html",
        {
            "report": report,
            "health_score": score
        }
)