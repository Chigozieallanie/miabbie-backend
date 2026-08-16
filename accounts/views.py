from django.core.mail import send_mail
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, VerificationCode
from .serializers import SignupSerializer, VerifySerializer, LoginSerializer


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        phone = serializer.validated_data['phone']

        user = User.objects.create_user(email=email, phone=phone)
        code_obj = VerificationCode.generate_for(user)

        # In development this just prints to your terminal (console email
        # backend). Once you're ready to deploy, swap EMAIL_BACKEND in
        # settings.py for a real SMTP provider and this same code will
        # actually email the user.
        send_mail(
            subject='Your MiAbbie verification code',
            message=f'Your verification code is: {code_obj.code}',
            from_email=None,  # uses DEFAULT_FROM_EMAIL
            recipient_list=[email],
        )

        return Response(
            {'message': 'Account created. Check your email for a verification code.'},
            status=status.HTTP_201_CREATED,
        )


class VerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'No account found with this email.'}, status=404)

        code_obj = user.codes.filter(code=code, used=False).order_by('-created_at').first()

        if not code_obj:
            return Response({'error': 'Invalid code.'}, status=400)

        if code_obj.is_expired():
            return Response({'error': 'This code has expired. Please request a new one.'}, status=400)

        code_obj.used = True
        code_obj.save()

        user.is_verified = True
        user.save()

        return Response({'message': 'Account verified. You can now log in.'})


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'No account found with this email. Please sign up first.'}, status=404)

        if not user.is_verified:
            return Response({'error': 'Please verify your email before logging in.'}, status=403)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'email': user.email,
                'phone': user.phone,
            },
        })
