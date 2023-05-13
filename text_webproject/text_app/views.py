from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Snippet, Tag
from .serializers import SnippetSerializer, TagSerializer
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.http import Http404


class LoginApi(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        """
        User can log in using username and password
        :param request: username, password
        :return: Returns login success, access token if user verified. Access Token expires in 1 day.
                User can use this access token for authentication.
        """
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                access_token.set_exp(lifetime=timedelta(days=1))
                return Response({'message': 'Login Success', "success": True,
                                 'refresh': str(refresh),
                                 'access': str(access_token)})
            else:
                return Response({'message': 'Login Failed', "success": False},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": str(e), "success": False}, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(APIView):

    def post(self, request):
        """
        API for getting new access token using the refresh token obtained during signin.
        :param request: POST
        :return: New access token
        """
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response('Refresh token not provided', status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
        except Exception as e:
            return Response({"message": str(e), "success": False}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'access_token': access_token}, status=status.HTTP_200_OK)


class SnippetListCreateView(generics.ListCreateAPIView):
    """
    List and create snippets
    """
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """
        Create a snippet instance with current logged-in user as user_id.
        Checks if tag_title entered by user already exists, if not creates and link to it.
        :param request: POST
        :return: Creates snippet instance
        """
        try:
            data = request.data
            tag_title = data.get('tag_title')
            tag, created = Tag.objects.get_or_create(title=tag_title)
            snippet_obj = Snippet(title=data.get('title'),
                                  content=data.get('content'),
                                  user_id_id=request.user.id,
                                  tag_id_id=tag.id)
            snippet_obj.save()
            serializer = SnippetSerializer(snippet_obj, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e), "success": False}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        """
        :param request: GET
        :return: Returns list of all snippets with count
        """
        try:
            queryset = Snippet.objects.all()
            serializer = SnippetSerializer(queryset, many=True, context={'request': request})
            return Response({"count": len(queryset), "results": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e), "success": False}, status=status.HTTP_400_BAD_REQUEST)


class SnippetDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, snippet_id):
        try:
            return Snippet.objects.get(pk=snippet_id)
        except Snippet.DoesNotExist:
            raise Http404("Snippet not found")

    def get(self, request, snippet_id):
        try:
            snippet = self.get_object(snippet_id)
            serializer = SnippetSerializer(snippet, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return Response({"message": str(e), "success": False}, status=status.HTTP_400_BAD_REQUEST)


class SnippetUpdateView(generics.UpdateAPIView):
    """
    Update a snippet
    """
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        try:
            snippet = Snippet.objects.get(pk=kwargs.get('snippet_id'))
        except Snippet.DoesNotExist:
            return Response(status=404)
        try:
            if request.data.get('title'):
                snippet.title = request.data.get('title')
            if request.data.get('content'):
                snippet.content = request.data.get('content')
            if request.data.get('tag_title'):
                tag_title = request.data.get('tag_title')
                tag, created = Tag.objects.get_or_create(title=tag_title)
                snippet.tag_id_id = tag.id
            snippet.save()
            serializer = SnippetSerializer(snippet, context={'request': request})
            return Response(serializer.data, status=200)
        except Exception as e:
            return Response({"message": str(e), "success": False}, status=status.HTTP_400_BAD_REQUEST)


class SnippetDeleteView(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        """
        :param request: DELETE
        :return: Takes a list of snippet_id to be deleted and returns existing snippet list
        """
        try:
            snippet_id = request.data.get('snippet_id')
            snippets = Snippet.objects.filter(id__in=snippet_id)
            snippets.delete()
            queryset = Snippet.objects.all()
            serializer = SnippetSerializer(queryset, many=True, context={'request': request})
            return Response({"success": True, "message": "List of Snippets", "results": serializer.data},
                            status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"message": str(e), "success": False}, status=status.HTTP_400_BAD_REQUEST)


class TagListView(generics.ListAPIView):
    """
    List tags
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticated,)


class SnippetListByTag(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, tag_id):
        """
        :param request: GET
        :param tag_id: tag_id
        :return: Gets the tag id and return list of snippets related to the tag
        """
        try:
            tag = Tag.objects.get(pk=tag_id)
        except Tag.DoesNotExist:
            return Response({'message': 'Tag not found'}, status=404)
        try:
            snippets = Snippet.objects.filter(tag_id=tag)
            serializer = SnippetSerializer(snippets, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return Response({"message": str(e), "success": False}, status=status.HTTP_400_BAD_REQUEST)
