from django.contrib import admin
from eventtracking.django.models import RegExpFilter


class RegExpFilterAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        has_permission = super().has_add_permission(request)

        if has_permission and RegExpFilter.objects.exists():
            return False

        return has_permission


admin.site.register(RegExpFilter, RegExpFilterAdmin)
