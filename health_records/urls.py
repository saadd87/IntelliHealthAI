from django.urls import path
from . import views

urlpatterns = [

    path(
        'add/',
        views.add_record,
        name='add_record'
    ),
    path(
    'my-records/',
    views.my_records,
    name='my_records'
    ),
    path(
    'edit/<int:id>/',
    views.edit_record,
    name='edit_record'
    ),
    path(
    'delete/<int:id>/',
    views.delete_record,
    name='delete_record'
    ),
    path(
    'predict/<int:id>/',
    views.predict_risk,
    name='predict_risk'
    ),
    path(
    'dashboard/',
    views.dashboard,
    name='dashboard'
    ),
    path(
    'export/pdf/',
    views.export_pdf,
    name='export_pdf'
    ),
    path(
    'export/excel/',
    views.export_excel,
    name='export_excel'
    ),
    path(
    'send-report/',
    views.send_health_report,
    name='send_health_report'
    ),
    path("test-ai/", views.test_ai, name="test_ai"),

    path(
    "ai-chat/",
    views.ai_chat,
    name="ai_chat"
    ),

    path(
    "ai-report/",
    views.ai_report,
    name="ai_report"
    ),


]