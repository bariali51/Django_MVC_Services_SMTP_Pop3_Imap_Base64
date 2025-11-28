# service_app/views.py
import os
import tempfile

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .controllers import SMTPController, POP3Controller, IMAPController, B64Controller
import json

# ------------------ HTML Views ------------------
def index(request):
    return render(request, 'service_app/index.html')

def smtp_view(request):
    return render(request, 'service_app/smtp.html')

def pop3_view(request):
    return render(request, 'service_app/pop3.html')

def imap_view(request):
    return render(request, 'service_app/imap.html')

def b64_view(request):
    return render(request, 'service_app/b64.html')


# ------------------ API Endpoints ------------------
@csrf_exempt
def send_smtp_email(request):
    if request.method == "POST":
        try:
            sender = request.POST.get('sender')
            pwd = request.POST.get('pwd')
            receiver = request.POST.get('receiver')
            subject = request.POST.get('subject')
            message = request.POST.get('message')

            attachments = request.FILES.getlist('attachments')  # list of files

            # Create temporary files
            attachment_paths = []  # (temporary path, original filename)
            for f in attachments:
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(f.name)[1]) as tmp:
                    for chunk in f.chunks():
                        tmp.write(chunk)
                    attachment_paths.append((tmp.name, f.name))

            controller = SMTPController()
            # Send email with attachments preserving original filenames
            success, msg = controller.send_email(
                sender, pwd, receiver, subject, message,
                attachments=attachment_paths
            )
            # Delete temporary files after sending
            for path, _ in attachment_paths:
                try:
                    os.remove(path)
                except:
                    pass

            return JsonResponse({'success': success, 'message': msg})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request'})


@csrf_exempt
def pop3_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email_addr = data.get('email')
        pwd = data.get('password')
        controller = POP3Controller()
        success, msg = controller.login(email_addr, pwd)
        if success:
            # Fetch emails after login
            fetch_success, emails = controller.fetch_emails()
            if fetch_success:
                return JsonResponse({'success': True, 'message': msg, 'emails': emails})
            else:
                return JsonResponse({'success': False, 'message': 'Failed to fetch emails'})
        return JsonResponse({'success': False, 'message': msg})

    # GET: can be used later to fetch a specific message
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@csrf_exempt
def imap_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email_addr = data.get('email')
        pwd = data.get('password')
        controller = IMAPController()
        success, msg = controller.login(email_addr, pwd)
        if success:
            emails = controller.fetch_emails()
            return JsonResponse({'success': True, 'message': msg, 'emails': emails})
        return JsonResponse({'success': False, 'message': msg})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@csrf_exempt
def b64_action(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            controller = B64Controller()
            action = data.get('action')

            # Text/URL-Safe Operations
            if action in ['encode', 'decode', 'urlsafe_encode', 'urlsafe_decode']:
                text = data.get('text', '')
                urlsafe = action.startswith('urlsafe')

                if 'encode' in action:
                    success, result = controller.encode_text(text, urlsafe=urlsafe)
                else:  # decode
                    success, result = controller.decode_text(text, urlsafe=urlsafe)

            # History Operation
            elif action == 'get_history':
                history = controller.get_history()
                # Prepare history for JSON response
                return JsonResponse({'success': True, 'history': history})

            # File Operations (simplified)
            # NOTE: For a real application, proper Django file upload handling is required.
            elif action in ['file_encode', 'file_decode']:
                input_path = data.get('input_path')
                output_path = data.get('output_path')
                mode = action.split('_')[1]  # 'encode' or 'decode'
                success, result = controller.file_action(input_path, output_path, mode)

            else:
                success, result = False, "Invalid action"

            return JsonResponse({'success': success, 'result': result})
        except Exception as e:
            # Add context to the error message
            return JsonResponse({'success': False, 'result': f"Server Error: {str(e)}"})

    # Handle GET requests for initial page load
    if request.method == 'GET':
        controller = B64Controller()
        history = controller.get_history()
        return JsonResponse({'success': True, 'history': history})  # Or render a template

    return JsonResponse({'success': False, 'result': 'Invalid request method'})
