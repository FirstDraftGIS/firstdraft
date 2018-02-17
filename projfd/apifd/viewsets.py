from appfd.models import Basemap, Feature, Order, Place, Test
from appfd.scripts.ai import update_popularity_for_order
from apifd.mixins import CsrfExemptSessionAuthentication
from apifd.serializers import BasemapSerializer, FeatureSerializer, OrderSerializer, PlaceSerializer, TestSerializer
from braces.views import CsrfExemptMixin
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
from multiprocessing import Process
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet



# ViewSets define the view behavior.
class BasemapViewSet(ModelViewSet):
    http_method_names = ["get"]
    queryset = Basemap.objects.all()
    serializer_class = BasemapSerializer

class FeatureViewSet(ModelViewSet):
    http_method_names = ["get", "patch"]
    filter_fields = ["order__token"]
    permission_classes = [AllowAny]
    serializer_class = FeatureSerializer

    def get_queryset(self):
        order__token = self.request.query_params.get("order__token", None)
        if order__token:
            return Feature.objects.filter(order__token=order__token)
        else:
            return Feature.objects.none()

    @list_route(methods=['patch'])
    def verify(self, request):
        try:
            token = self.request.query_params.get("order__token", None)
            if token:
                self.get_queryset().update(verified=True)
                status = "success"

                # updates popularity for places that are mentioned int the order
                Process(target=update_popularity_for_order.run, args=(token,)).start()
            else:
                status = "failure"
            return HttpResponse(json.dumps({"status": status}))
        except Exception as e:
            print(e)


# need to write method that overwrited retrieve method with token
# or just null it out
class OrderViewSet(ModelViewSet):

    http_method_names = ["get"]
    filter_fields = ["token"]
    serializer_class = OrderSerializer

    def get_queryset(self):
        token = self.request.query_params.get("token", None)
        if token:
            return Order.objects.filter(token=token)
        else:
            return Order.objects.none()

    """
    # overriding the default list behavior
    # so you can only get an order if you specify a token
    def list(self, request):
        queryset = self.queryset.get(token=request.query_params['token'])

        # duplicating what regular list method gives the serializer
        # need to do this in order for fields params to work
        serializer = OrderSerializer(queryset, context={"view": self, "request": request, "format": None})
        return Response(serializer.data)
    """


    # overriding retrieve, so can get order using token not internal id
    def retrieve(self, request, pk=None):
        queryset = Order.objects.all()
        order = get_object_or_404(queryset, token=pk)
        serializer = OrderSerializer(order, context={"view": self, "request": request, "format": None})
        return Response(serializer.data)
        

# ViewSets define the view behavior.
class PlaceViewSet(ModelViewSet):
    http_method_names = ["get"]
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    filter_fields = ('id','name')

    @list_route(methods=['get'])
    def typeahead(self, request):
        return Response(Place.objects.filter(name__startswith=request.query_params['name']).distinct("name").values_list("name", flat=True)[:5])

class TestViewSet(ModelViewSet):
    http_method_names = ["get"]
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    filter_fields = ("accuracy", "created")
