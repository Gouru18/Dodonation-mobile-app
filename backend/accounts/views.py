from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = []

class VerifyOTPView(APIView):
    permission_classes = []

    def post(self, request):
        # Implementation for OTP verification
        phone = request.data.get('phone')
        otp = request.data.get('otp')

        #placeholder logic for OTP verification
        if otp == '123456':
            return Response({"Message": "OTP verified successfully"}, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
    