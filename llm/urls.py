from django.urls import path
from .views import (
    DbChatRecommendedQuery,
    DbChatMySQL
)

urlpatterns = [
    path("query/recommend/",DbChatRecommendedQuery.as_view(),name="recommend_query"),
    path("query/question/",DbChatMySQL.as_view(),name="quetion_query"),
]