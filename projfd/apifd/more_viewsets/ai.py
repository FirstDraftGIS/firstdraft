from braces.views import CsrfExemptMixin, LoginRequiredMixin
from rest_framework.decorators import action, detail_route
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import GenericViewSet

from apifd.serializers import MapRequestSerializer, OrderSerializer
from appfd.models import Order
from appfd.views import request_map_from_sources
 

class AIViewSet(CsrfExemptMixin, LoginRequiredMixin, GenericViewSet):

    authentication_classes = []
    base_name = "ai"
    parser_classes = (MultiPartParser,)
    permission_classes = [AllowAny]
    http_method_names = ["post"]
    serializer_class = MapRequestSerializer

    # you create an order indirectly by passing it some inital data 
    #@detail_route(methods=['post'])
    @action(methods=['post'], detail=False)
    def request_map(self, request):
        print("starting request_map")
        return request_map_from_sources(request)
