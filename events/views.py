from django.shortcuts import render

# Create your views here.
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import Event, EventRegistration



@csrf_exempt
def events(request):

    # CREATE EVENT
    if request.method == "POST":

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON data"},
                status=400
            )

        required_fields = [
            "name",
            "description",
            "date",
            "venue",
            "capacity",
            "status"
        ]

        for field in required_fields:
            if field not in data or data[field] == "":
                return JsonResponse(
                    {"error": f"{field} is required"},
                    status=400
                )

        # Check capacity
        try:
            capacity = int(data["capacity"])
        except (ValueError, TypeError):
            return JsonResponse(
                {"error": "Capacity must be a number"},
                status=400
            )

        if capacity <= 0:
            return JsonResponse(
                {"error": "Capacity must be greater than 0"},
                status=400
            )

        # Check date
        try:
            event_date = timezone.datetime.fromisoformat(
                data["date"]
            )
        except ValueError:
            return JsonResponse(
                {"error": "Invalid date format"},
                status=400
            )

        # Check past date
        if event_date < timezone.now().replace(tzinfo=None):
            return JsonResponse(
                {"error": "Event date cannot be in the past"},
                status=400
            )

        # Check status
        valid_statuses = [
            "Upcoming",
            "Ongoing",
            "Completed",
            "Cancelled"
        ]

        if data["status"] not in valid_statuses:
            return JsonResponse(
                {"error": "Invalid status"},
                status=400
            )

        # Duplicate event check
        duplicate = Event.objects.filter(
            name=data["name"],
            date=event_date,
            venue=data["venue"]
        ).exists()

        if duplicate:
            return JsonResponse(
                {"error": "Duplicate event already exists"},
                status=409
            )

        event = Event.objects.create(
            name=data["name"],
            description=data["description"],
            date=event_date,
            venue=data["venue"],
            capacity=capacity,
            status=data["status"]
        )

        return JsonResponse(
            {
                "message": "Event created successfully",
                "event": {
                    "id": event.id,
                    "name": event.name,
                    "description": event.description,
                    "date": event.date,
                    "venue": event.venue,
                    "capacity": event.capacity,
                    "status": event.status
                }
            },
            status=201
        )

    # GET ALL EVENTS
    elif request.method == "GET":

        event_list = Event.objects.all()

        # SEARCH
        search = request.GET.get("search")

        if search:
            event_list = event_list.filter(
                name__icontains=search
            )

        # VENUE FILTER
        venue = request.GET.get("venue")

        if venue:
            event_list = event_list.filter(
                venue__icontains=venue
            )

        # STATUS FILTER
        status = request.GET.get("status")

        if status:
            event_list = event_list.filter(
                status=status
            )

        # SORTING
        sort = request.GET.get("sort", "date")

        if sort == "name":
            event_list = event_list.order_by("name")

        elif sort == "capacity":
            event_list = event_list.order_by("capacity")

        else:
            event_list = event_list.order_by("date")

        # PAGINATION
        try:
            page = int(request.GET.get("page", 1))
            limit = int(request.GET.get("limit", 10))
        except ValueError:
            return JsonResponse(
                {"error": "Page and limit must be numbers"},
                status=400
            )

        if page <= 0 or limit <= 0:
            return JsonResponse(
                {"error": "Page and limit must be greater than 0"},
                status=400
            )

        total = event_list.count()

        start = (page - 1) * limit
        end = start + limit

        event_list = event_list[start:end]

        events_data = []

        for event in event_list:
            events_data.append({
                "id": event.id,
                "name": event.name,
                "description": event.description,
                "date": event.date,
                "venue": event.venue,
                "capacity": event.capacity,
                "status": event.status
            })

        return JsonResponse({
            "page": page,
            "limit": limit,
            "total": total,
            "events": events_data
        })


@csrf_exempt
def event_detail(request, event_id):

    try:
        event = Event.objects.get(id=event_id)

    except Event.DoesNotExist:
        return JsonResponse(
            {"error": "Event not found"},
            status=404
        )

    # GET SINGLE EVENT
    if request.method == "GET":

        return JsonResponse({
            "id": event.id,
            "name": event.name,
            "description": event.description,
            "date": event.date,
            "venue": event.venue,
            "capacity": event.capacity,
            "status": event.status
        })

    # UPDATE EVENT
    elif request.method == "PUT":

        if event.status in ["Completed", "Cancelled"]:
            return JsonResponse(
                {
                    "error":
                    "Completed or Cancelled events cannot be updated"
                },
                status=409
            )

        try:
            data = json.loads(request.body)

        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON data"},
                status=400
            )

        required_fields = [
            "name",
            "description",
            "date",
            "venue",
            "capacity",
            "status"
        ]

        for field in required_fields:
            if field not in data or data[field] == "":
                return JsonResponse(
                    {"error": f"{field} is required"},
                    status=400
                )

        try:
            capacity = int(data["capacity"])

        except (ValueError, TypeError):
            return JsonResponse(
                {"error": "Capacity must be a number"},
                status=400
            )

        if capacity <= 0:
            return JsonResponse(
                {"error": "Capacity must be greater than 0"},
                status=400
            )

        try:
            event_date = timezone.datetime.fromisoformat(
                data["date"]
            )

        except ValueError:
            return JsonResponse(
                {"error": "Invalid date format"},
                status=400
            )

        if event_date < timezone.now().replace(tzinfo=None):
            return JsonResponse(
                {"error": "Event date cannot be in the past"},
                status=400
            )

        valid_statuses = [
            "Upcoming",
            "Ongoing",
            "Completed",
            "Cancelled"
        ]

        if data["status"] not in valid_statuses:
            return JsonResponse(
                {"error": "Invalid status"},
                status=400
            )

        duplicate = Event.objects.filter(
            name=data["name"],
            date=event_date,
            venue=data["venue"]
        ).exclude(id=event.id).exists()

        if duplicate:
            return JsonResponse(
                {"error": "Duplicate event already exists"},
                status=409
            )

        event.name = data["name"]
        event.description = data["description"]
        event.date = event_date
        event.venue = data["venue"]
        event.capacity = capacity
        event.status = data["status"]

        event.save()

        return JsonResponse({
            "message": "Event updated successfully"
        })

    # DELETE EVENT
    elif request.method == "DELETE":

        if event.status == "Completed":
            return JsonResponse(
                {
                    "error":
                    "Completed events cannot be deleted"
                },
                status=409
            )

        event.delete()

        return JsonResponse({
            "message": "Event deleted successfully"
        })

    return JsonResponse(
        {"error": "Method not allowed"},
        status=405
    )
@csrf_exempt
def register_user(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "Method not allowed"
            },
            status=405
        )

    try:
        data = json.loads(request.body)

    except json.JSONDecodeError:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid JSON data"
            },
            status=400
        )

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    # Required fields
    if not name or not email or not password:
        return JsonResponse(
            {
                "success": False,
                "message": "Name, email and password are required"
            },
            status=400
        )

    # Validate email
    try:
        validate_email(email)

    except ValidationError:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid email address"
            },
            status=400
        )

    # Validate password
    if len(password) < 6:
        return JsonResponse(
            {
                "success": False,
                "message": "Password must contain at least 6 characters"
            },
            status=400
        )

    # Duplicate email
    if User.objects.filter(email=email).exists():
        return JsonResponse(
            {
                "success": False,
                "message": "Email already registered"
            },
            status=409
        )

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=name
    )

    return JsonResponse(
        {
            "success": True,
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "name": user.first_name,
                "email": user.email,
                "created_at": user.date_joined
            }
        },
        status=201
    )
@csrf_exempt
def login_user(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "Method not allowed"
            },
            status=405
        )

    try:
        data = json.loads(request.body)

    except json.JSONDecodeError:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid JSON data"
            },
            status=400
        )

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return JsonResponse(
            {
                "success": False,
                "message": "Email and password are required"
            },
            status=400
        )

    user = authenticate(
        request,
        username=email,
        password=password
    )

    if user is None:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid email or password"
            },
            status=401
        )

    login(request, user)

    return JsonResponse({
        "success": True,
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.first_name,
            "email": user.email
        }
    })
@csrf_exempt
def current_user(request):

    if request.method != "GET":
        return JsonResponse(
            {
                "success": False,
                "message": "Method not allowed"
            },
            status=405
        )

    return JsonResponse({
        "success": True,
        "user": {
            "id": request.user.id,
            "name": request.user.first_name,
            "email": request.user.email,
            "created_at": request.user.date_joined
        }
    })
@csrf_exempt
def logout_user(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "Method not allowed"
            },
            status=405
        )

    logout(request)

    return JsonResponse({
        "success": True,
        "message": "Logout successful"
    })
@csrf_exempt
def register_event(request, event_id):

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "Method not allowed"
            },
            status=405
        )

    try:
        event = Event.objects.get(id=event_id)

    except Event.DoesNotExist:
        return JsonResponse(
            {
                "success": False,
                "message": "Event not found"
            },
            status=404
        )

    # Check duplicate registration
    if EventRegistration.objects.filter(
        user=request.user,
        event=event
    ).exists():

        return JsonResponse(
            {
                "success": False,
                "message": "You are already registered for this event"
            },
            status=409
        )

    # Check capacity
    registration_count = EventRegistration.objects.filter(
        event=event
    ).count()

    if registration_count >= event.capacity:
        return JsonResponse(
            {
                "success": False,
                "message": "Event capacity is full"
            },
            status=409
        )

    registration = EventRegistration.objects.create(
        user=request.user,
        event=event
    )

    return JsonResponse(
        {
            "success": True,
            "message": "Successfully registered for event",
            "registration": {
                "id": registration.id,
                "event_id": event.id,
                "event_name": event.name,
                "user_id": request.user.id
            }
        },
        status=201
    )