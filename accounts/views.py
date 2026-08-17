from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, VerificationCode
from .serializers import SignupSerializer, VerifySerializer, LoginSerializer
from .email_utils import send_verification_email


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        phone = serializer.validated_data['phone']

        user = User.objects.create_user(email=email, phone=phone)
        code_obj = VerificationCode.generate_for(user)

        # Sent via SendGrid's HTTPS API (not Django's SMTP backend) —
        # this works both locally and on Render, since SMTP ports get
        # blocked on Render's free tier but HTTPS never does.
        send_verification_email(email, code_obj.code)

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