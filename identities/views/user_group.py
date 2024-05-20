from rest_framework import viewsets, decorators, permissions, filters
from rest_framework.response import Response
from libs.pagination import CustomPagination
from django.db.models import Value, F, CharField, Q
from django.db.models.functions import Concat
from django.contrib.auth.models import User, Group
from django_filters import rest_framework as django_filters
from django.utils.translation import gettext_lazy as _
from ..serializers.user_group import UserGroupSerializer, GroupSerializer, SetGroupSerializer


class UserFilter(django_filters.FilterSet):
    created_at_range = django_filters.CharFilter(method='filter_created_at_range', help_text=_(
        'Put date range in this format: start_date,end_date [YYYY-MM-DD,YYYY-MM-DD]'))
    group_id = django_filters.CharFilter(
        method='filter_group_id', help_text=_('Filter by group id'))
    group_name = django_filters.CharFilter(
        method='filter_group_name', help_text=_('Filter by group name'))
    search = django_filters.CharFilter(
        method="filter_search", help_text=_("Search by name or email"))

    def filter_created_at_range(self, queryset, name, value):
        if value:
            # Split the value on a comma to extract the start and end dates
            dates = value.split(',')
            if len(dates) == 2:
                start_date, end_date = dates
                return queryset.filter(date_joined__date__gte=start_date, date_joined__date__lte=end_date)
        return queryset

    def filter_group_id(self, queryset, name, value):
        if value and value.isdigit():
            return queryset.filter(groups__id=int(value))
        return queryset

    def filter_group_name(self, queryset, name, value):
        if value:
            return queryset.filter(groups__name=value)
        return queryset

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.annotate(
            full_name=Concat(F('first_name'), Value(' '), F(
                'last_name'), output_field=CharField())
        ).filter(Q(full_name__icontains=value) | Q(email__icontains=value))


class UserViewSet(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin, viewsets.mixins.RetrieveModelMixin):
    pagination_class = CustomPagination
    queryset = User.objects.filter()
    serializer_class = UserGroupSerializer
    lookup_field = "id"
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    filter_backends = (django_filters.DjangoFilterBackend,
                       filters.OrderingFilter)
    filterset_class = UserFilter

    def get_serializer_class(self):
        return {
            "set_group": SetGroupSerializer
        }.get(self.action, UserGroupSerializer)

    @decorators.action(methods=["POST"], detail=True, url_path="set-group")
    def set_group(self, request, id=None):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance.groups.set(serializer.validated_data["group_ids"])

        return Response({"detail": "Set user group successfully."})


class GroupViewSet(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin, viewsets.mixins.RetrieveModelMixin):
    pagination_class = CustomPagination
    queryset = Group.objects.filter()
    serializer_class = GroupSerializer
