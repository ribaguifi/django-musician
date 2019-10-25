from django.views.generic.base import ContextMixin

from . import get_version


class CustomContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO generate menu items
        context.update({
            'version': get_version(),
        })

        return context
