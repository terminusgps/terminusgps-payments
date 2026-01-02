from django.contrib.auth.mixins import UserPassesTestMixin

from ..models import CustomerProfile


class CustomerProfileExclusiveMixin(UserPassesTestMixin):
    def test_func(self) -> bool:
        if self.request.user.is_staff:
            return True
        try:
            cprofile = CustomerProfile.objects.get(
                pk=self.kwargs["customerprofile_pk"]
            )
            return cprofile.user.pk == self.request.user.pk
        except CustomerProfile.DoesNotExist:
            return False
