from django.shortcuts import render,redirect
from .models import *
from.serializers import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRegisterView(APIView):
   def post(self,request,format=None):
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token = get_tokens_for_user(user)
    return Response({'token':token,'msg':'Registration Success'},status=status.HTTP_201_CREATED)
   

class UserLoginView(APIView):
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            token = get_tokens_for_user(user)
            return Response({'token':token,'msg':'Login Success'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        try:
            refresh_token = request.META.get('HTTP_REFRESH')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'msg':'Logout Success'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg':'Invalid Token'}, status=status.HTTP_401_UNAUTHORIZED)
        


class IncidentListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        incidents = IncidentModel.objects.filter(user=user)
        serializer = IncidentSerializer(incidents, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = IncidentSerializer(data=request.data,context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class IncidentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return IncidentModel.objects.get(pk=pk, user=self.request.user)
        except IncidentModel.DoesNotExist:
            return None

    def get(self, request, pk):
        incident = self.get_object(pk)
        if incident is not None:
            serializer = IncidentSerializer(incident)
            return Response(serializer.data)
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        incident = self.get_object(pk)
        if incident is not None:
            serializer = IncidentSerializer(incident, data=request.data, partial=True,context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        incident = self.get_object(pk)
        if incident is not None:
            incident.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    

class IncidentSearchView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        incident_id = request.query_params.get('incident_id', None)
        user = request.user

        if incident_id is None:
            return Response({'detail': 'Please provide an incident_id to search.'}, status=status.HTTP_400_BAD_REQUEST)

        incident = IncidentModel.objects.filter(incident_id=incident_id, user=user).first()

        if not incident:
            return Response({'detail': 'No incident found with this ID.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = IncidentSerializer(incident)
        return Response(serializer.data, status=status.HTTP_200_OK)