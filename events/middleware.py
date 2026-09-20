from django.http import JsonResponse


class AuthenticationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Public URLs
        public_urls = [
            "/auth/register/",
            "/auth/login/",
            "/events/",
        ]

        # Allow public URLs
        if request.path in public_urls:
            return self.get_response(request)

        # Protected: current logged-in user
        if request.path == "/auth/me/":
            if not request.user.is_authenticated:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Authentication required"
                    },
                    status=401
                )

        # Protected: logout
        if request.path == "/auth/logout/":
            if not request.user.is_authenticated:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Authentication required"
                    },
                    status=401
                )

        # Protected: create event
        if request.path == "/events/" and request.method == "POST":
            if not request.user.is_authenticated:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Authentication required"
                    },
                    status=401
                )

        # Protected: update/delete event
        if request.path.startswith("/events/"):
            if request.method in ["PUT", "DELETE"]:
                if not request.user.is_authenticated:
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "Authentication required"
                        },
                        status=401
                    )

        # Protected: event registration
        if request.path.endswith("/register/"):
            if not request.user.is_authenticated:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Authentication required"
                    },
                    status=401
                )

        return self.get_response(request)