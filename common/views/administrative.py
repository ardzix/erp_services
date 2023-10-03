from rest_framework import viewsets, mixins
from django_filters import rest_framework as filters
from ..models import AdministrativeLvl1, AdministrativeLvl2, AdministrativeLvl3, AdministrativeLvl4
from ..serializers.administrative import (AdministrativeLvl1ListSerializer, AdministrativeLvl2ListSerializer, 
                          AdministrativeLvl3ListSerializer, AdministrativeLvl4ListSerializer)

class AdministrativeLvl1ViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = AdministrativeLvl1.objects.all()
    serializer_class = AdministrativeLvl1ListSerializer

class AdministrativeLvl2Filter(filters.FilterSet):
    lvl1 = filters.NumberFilter(field_name='lvl1__id', required=True)

    class Meta:
        model = AdministrativeLvl2
        fields = ['lvl1']

class AdministrativeLvl2ViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = AdministrativeLvl2.objects.all()
    serializer_class = AdministrativeLvl2ListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = AdministrativeLvl2Filter

class AdministrativeLvl3Filter(filters.FilterSet):
    lvl2 = filters.NumberFilter(field_name='lvl2__id', required=True)

    class Meta:
        model = AdministrativeLvl3
        fields = ['lvl2']

class AdministrativeLvl3ViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = AdministrativeLvl3.objects.all()
    serializer_class = AdministrativeLvl3ListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = AdministrativeLvl3Filter

class AdministrativeLvl4Filter(filters.FilterSet):
    lvl3 = filters.NumberFilter(field_name='lvl3__id', required=True)

    class Meta:
        model = AdministrativeLvl4
        fields = ['lvl3']

class AdministrativeLvl4ViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = AdministrativeLvl4.objects.all()
    serializer_class = AdministrativeLvl4ListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = AdministrativeLvl4Filter
