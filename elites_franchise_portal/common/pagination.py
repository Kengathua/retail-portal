"""Custom pagination file."""
from collections import OrderedDict
from rest_framework import pagination
from rest_framework.response import Response


class EnhancedPagination(pagination.PageNumberPagination):
    """An extensive pagination."""

    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        """Get detailed response in paged data."""
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('page_size', self.page.paginator.per_page),
            ('current_page', self.page.number),
            ('total_pages', self.page.paginator.num_pages),
            ('start_index', self.page.start_index()),
            ('end_index', self.page.end_index()),
            ('results', data)
        ]))
