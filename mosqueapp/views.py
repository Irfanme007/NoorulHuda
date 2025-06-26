from django.shortcuts import render,redirect,get_object_or_404
import csv
from django.http import HttpResponse,JsonResponse,HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.db.utils import IntegrityError
from mosqueapp.models import Member,MonthlyPayment,MonthlyAmountSetting
from mosqueapp.form import AddmemberForm,SetAmountForm
import datetime,calendar
from datetime import datetime
from django.utils import timezone

# Create your views here.

def LoginView(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')    

        user=authenticate(username=username,password=password)
        if user:
            login(request,user)
            request.session['username']=username
            return redirect('dashboard')
        else:
            messages.error(request,'Unable to Login',extra_tags='login_message')
            return redirect('login')

    return render(request,"login.html")

@login_required
def LogoutView(request):
    request.session.flush()
    logout(request)
    return redirect('login')

@login_required
def Dashboard(request):
    total_members = Member.objects.count()
    members_paid = Member.objects.filter(payment_status=True).count()
    members_due = Member.objects.filter(payment_status=False).count()
    active_members=Member.objects.filter(is_active=True).count()
    inactive_members=Member.objects.filter(is_active=False).count()

    context = {
        'total_members': total_members,
        'payment_received': members_paid,
        'payment_due': members_due,
        'username': request.user.username,
        "active_members":active_members,
        "inactive_members":inactive_members,
    }
    return render(request, 'dashboard.html', context)

@login_required
def add_member(request):
    if request.method == 'POST':
        form = AddmemberForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Member added successfully', extra_tags='add-members')
                return redirect('member-list')
            except IntegrityError as e:
                # General duplicate handling
                error_message = "A member with this information already exists."
                if 'member_id' in str(e):
                    form.add_error('member_id', 'Member ID already exists.')
                    error_message = "Member ID already exists."
                elif 'member_phone' in str(e):
                    form.add_error('member_phone', 'Phone number already exists.')
                    error_message = "Phone number already exists."

                messages.error(request, error_message, extra_tags='add-members')
        else:
            messages.error(request, 'Please correct the errors below.', extra_tags='add-members')
    else:
        form = AddmemberForm()

    return render(request, 'add_member.html', {'form': form})

@login_required
def member_list(request):
    query=request.GET.get('q','').strip()
    status=request.GET.get('status','').lower()
    page_number=request.GET.get('page',1)
    page_size=request.GET.get('page_size',10)
    members=Member.objects.filter(deleted=False)
    if query:
        members=members.filter(member_name__icontains=query)
    if status =='active':
        members=members.filter(is_active=True)
    elif status=='inactive':
        members=members.filter(is_active=False)
    
    paginator=Paginator(members,page_size)
    page_obj=paginator.get_page(page_number)
    context={
        'members':page_obj.object_list,
        'query':query,
        'status':status,
        'page_obj':page_obj,
        'page_size':page_size,
    }
    return render(request,'members_list.html',context)


@login_required
def edit_member_details(request, id):
    member = get_object_or_404(Member, id=id)
    if request.method == 'POST':
        form = AddmemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member updated successfully!', extra_tags="add-members")
            return redirect('member-list')
        else:
            messages.error(request, 'Unable to modify member.', extra_tags="add-members")
    else:
        form = AddmemberForm(instance=member)

    return render(request, 'add_member.html', {'form': form, 'edit_mode': True})


@login_required
def export_members_csv(request):
    members = Member.objects.all()

    # Optional: apply same filters as in your member_list view
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').lower()
    if query:
        members = members.filter(member_name__icontains=query)
    if status == 'active':
        members = members.filter(is_active=True)
    elif status == 'inactive':
        members = members.filter(is_active=False)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=members.csv'

    writer = csv.writer(response)
    writer.writerow(['Member ID', 'Name', 'Phone', 'Email', 'Address'])

    for member in members:
        writer.writerow([
            member.member_id,
            member.member_name,
            member.member_phone,
            member.member_email,
            member.address,
        ])

    return response

@login_required
def delete_member(request,id):
    member=get_object_or_404(Member,id=id)
    member.deleted=True
    member.is_active=False
    member.save()
    return redirect('member-list')

@login_required
def PaymentDetails(request):
    details = MonthlyPayment.objects.select_related('member').all()
    current_amount = MonthlyAmountSetting.objects.order_by('-updated_at').first()

    # Filters from GET
    name = request.GET.get('member_name', '').strip()
    phone = request.GET.get('member_phone', '').strip()
    member_id = request.GET.get('member_id', '').strip()
    year = request.GET.get('year', '').strip()
    start_month = request.GET.get('start_month')
    end_month = request.GET.get('end_month')

    # Apply filters
    if name:
        details = details.filter(member__member_name__icontains=name)
    if phone:
        details = details.filter(member__member_phone__icontains=phone)
    if member_id:
        details = details.filter(member__member_id__icontains=member_id)
    if year:
        try:
            details = details.filter(year=int(year))
        except ValueError:
            pass
    if start_month and end_month:
        try:
            start = int(start_month)
            end = int(end_month)
            if 1 <= start <= 12 and 1 <= end <= 12 and start <= end:
                details = details.filter(month__gte=start, month__lte=end)
        except ValueError:
            pass

    # Order results
    details = details.order_by('-year', '-month', 'member__member_name')

    # Paginate
    paginator = Paginator(details, 10)  # 50 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Context for dropdowns
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    year_range = range(2020, timezone.now().year + 1)

    context = {
        "details": page_obj,
        "months": months,
        "year_range": year_range,
        'current_amount': current_amount,
        'filters': {
            'member_name': name,
            'member_phone': phone,
            'member_id': member_id,
            'year': year,
            'start_month': start_month,
            'end_month': end_month,
        }
    }
    return render(request, 'payment_details.html', context)


@login_required
def fetch_member_info(request):
    member_id=request.GET.get('member_id').strip().zfill(5)
    try:
        member=Member.objects.get(member_id=member_id)
        return JsonResponse({
            'name':member.member_name,
            'phone':member.member_phone,
        })
    except Member.DoesNotExist:
        return JsonResponse({'error':'member not found'},status=404)

@login_required
def get_member_payments_for_year(request):
    member_id = request.GET.get('member_id', '').strip().zfill(5)
    try:
        year = int(request.GET.get('year'))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid year'}, status=400)

    try:
        member = Member.objects.get(member_id=member_id)
    except Member.DoesNotExist:
        return JsonResponse({'error': 'Member not found'}, status=404)

    months = {str(m): False for m in range(1, 13)}
    payments = MonthlyPayment.objects.filter(member=member, year=year)
    for p in payments:
        months[str(p.month)] = p.paid

    return JsonResponse({'payments': months})

@login_required
def set_monthly_amount(request):
    if request.method == 'POST':
        form = SetAmountForm(request.POST)
        if form.is_valid():
            # Always use the same record (e.g., id=1) or just the latest one
            instance = MonthlyAmountSetting.objects.order_by('-updated_at').first() or MonthlyAmountSetting()
            instance.amount = form.cleaned_data['amount']
            instance.save()
            messages.success(request, "Monthly amount updated successfully.")
        else:
            messages.error(request, "Invalid input. Please try again.")
    return redirect('payment-details')  # Update to your desired redirect URL

@login_required
def set_inactive(request,id):
    member=get_object_or_404(Member,id=id)
    member.is_active=False
    member.save()
    return redirect('member-list')

def set_active(request,id):
    member=get_object_or_404(Member,id=id)
    member.is_active=True
    member.deleted=False
    member.save()
    return redirect('member-list')

@require_POST
@login_required
def collect_payment(request):
    member_id = request.POST.get('member_id').strip().zfill(5)
    year = int(request.POST.get('year', datetime.now().year))
    months = request.POST.getlist('months')

    if not member_id or not months:
        return JsonResponse({'status': 'Error', 'error': 'Missing member ID or months'}, status=400)

    try:
        member = Member.objects.get(member_id=member_id)
    except Member.DoesNotExist:
        return JsonResponse({'status': 'Error', 'error': 'Member not found'}, status=404)
    amount = MonthlyAmountSetting.objects.latest('updated_at').amount

    for m in months:
        MonthlyPayment.objects.get_or_create(
            member=member,
            month=int(m),
            year=year,
            defaults={'paid': True, 'amount': amount}
        )


    return JsonResponse({'status': 'Success'})

@login_required
def collect_payment_page(request):
    current_year = datetime.now().year
    year_range = range(current_year - 2, current_year + 2)
    return render(request, 'collect_payment.html', {
        'current_year': current_year,
        'year_range': year_range
    })

@login_required
def export_payments_csv(request):
    payments = MonthlyPayment.objects.select_related('member').all()

    # Optional filters
    query = request.GET.get('q', '').strip()
    year = request.GET.get('year')
    paid_status = request.GET.get('paid')

    if query:
        payments = payments.filter(member__member_name__icontains=query)
    if year:
        payments = payments.filter(year=year)
    if paid_status == 'paid':
        payments = payments.filter(paid=True)
    elif paid_status == 'unpaid':
        payments = payments.filter(paid=False)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=monthly_payments.csv'

    writer = csv.writer(response)
    writer.writerow(['Member Name', 'Year', 'Month', 'Amount', 'Paid', 'Paid On'])

    for p in payments:
        writer.writerow([
            p.member.member_name,
            p.year,
            calendar.month_name[p.month],
            p.amount,
            'Yes' if p.paid else 'No',
            p.paid_on.strftime('%Y-%m-%d') if p.paid_on else ''
        ])

    return response

def see_inactive_members(request):
    inactive_members = Member.objects.filter(deleted=True)
    data = [
        {   
            "id":m.id,
            "member_id": m.member_id,
            "member_name": m.member_name,
            "member_email": m.member_email,
            "address": m.address,
        }
        for m in inactive_members
    ]
    return JsonResponse({"inactive_members": data})