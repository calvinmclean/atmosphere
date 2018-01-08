from django.utils import timezone
from django.db.models import Q

from api.v2.serializers.details import ImageReportSerializer
from api.v2.views.base import AuthModelViewSet
from api.v2.views.mixins import MultipleFieldLookup


class ImageReportViewSet(MultipleFieldLookup, AuthModelViewSet):

    """
    API endpoint that allows images to be reported as broken.
    """

    image = ImagePrimaryKeyRelatedField(
        source='application',
        queryset=Image.objects.all())
    user = UserSummarySerializer(read_only=True)
    url = UUIDHyperlinkedIdentityField(
        view_name='api:v2:applicationbookmark-detail',
    )

    lookup_fields = ("id", "uuid")
    queryset = ImageBookmark.objects.all()
    serializer_class = ImageBookmarkSerializer
    http_method_names = ['get', 'post', 'delete', 'head', 'options', 'trace']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """
        Filter projects by current user
        """
        user = self.request.user
        now_time = timezone.now()
        application_ids = list(Application.shared_with_user(user).values_list('id', flat=True))
        return ImageBookmark.objects.filter(user=user).filter(
            Q(application__id__in=application_ids)).distinct()
