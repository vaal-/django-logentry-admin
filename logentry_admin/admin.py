# -*- coding:utf-8 -*-
from django.contrib import admin
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter

class ActionListFilter(SimpleListFilter):
    title = _('action')
    parameter_name = 'action_flag'

    def lookups(self, request, model_admin):
        return (
            (ADDITION, _('addition')),
            (DELETION, _('deletion')),
            (CHANGE, _('change')),
        )

    def queryset(self, request, queryset):
        return queryset.filter(action_flag=self.value()) if self.value() else queryset

class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'
    actions = None
    readonly_fields = LogEntry._meta.get_all_field_names()
    list_display_links = ['action_time']

    list_filter = [
        'content_type',
        ActionListFilter
    ]

    search_fields = [
        'user__username',
        'object_repr',
        'change_message'
    ]

    list_display = [
        'id',
        'action_time',
        'user',
        'content_type',
        'object_link',
        'action_description',
        'change_message',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser and request.method != 'POST'

    def has_delete_permission(self, request, obj=None):
        return False

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            link = '<a href="%s">%s</a>' % (
                reverse('admin:%s_%s_change' % (ct.app_label, ct.model),
                        args=[obj.object_id]),
                escape(obj.object_repr),
            )
        return link
    object_link.allow_tags = True
    object_link.admin_order_field = 'object_repr'
    object_link.short_description = _('object')

    def action_description(self, obj):
        action_names = {
            ADDITION: _('addition'),
            DELETION: _('deletion'),
            CHANGE: _('change'),
        }
        return action_names[obj.action_flag]
    action_description.short_description = _('action')

    fieldsets = [
        (None, {'fields':()}),
    ]

    def __init__(self, *args, **kwargs):
        super(LogEntryAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

admin.site.register(LogEntry, LogEntryAdmin)
