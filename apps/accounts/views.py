from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.accounts.serializers import CreateUserSerializer, MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class RegisterAPIView(APIView):
    '''контроллер для регистрации юзера'''
    serializer_class = CreateUserSerializer

    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"success"},status=201)
        return Response(serializer.errors,status=400)


# Create your views here.
class MyTokenObtainPairView(TokenObtainPairView):
    '''переорпделелил для кастомного сериализатораЮ передающего доп
    данные при генерации пары jwt токена'''
    
    serializer = MyTokenObtainPairSerializer