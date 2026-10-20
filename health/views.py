from django.db import connection
from django.db.utils import DatabaseError
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

HealthSerializer = inline_serializer(
    name="Health",
    fields={
        "status": serializers.CharField(),
        "database": serializers.CharField(),
    },
)


class HealthCheckView(APIView):
    @extend_schema(
        summary="Health check",
        responses={200: HealthSerializer, 503: HealthSerializer},
    )
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            db_status = "ok"
        except DatabaseError:
            db_status = "unavailable"

        healthy = db_status == "ok"
        return Response(
            {"status": "ok" if healthy else "error", "database": db_status},
            status=status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        )
