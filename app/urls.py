from django.urls import path

from app.views import AvatarView

urlpatterns = [path(r'', AvatarView.as_view()), ]
