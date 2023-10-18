from django_filters import rest_framework as filters

class CreatedAtFilterMixin(filters.FilterSet):
    created_at_range = filters.CharFilter(method='filter_created_at_range')

    def filter_created_at_range(self, queryset, name, value):
        if value:
            # Split the value on a comma to extract the start and end dates
            dates = value.split(',')
            if len(dates) == 2:
                start_date, end_date = dates
                return queryset.filter(created_at__gte=start_date, created_at__lte=end_date)
        return queryset
