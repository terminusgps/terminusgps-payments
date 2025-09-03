from django.core import serializers


class AuthorizenetXMLSerializer(serializers.python.Serializer):
    def get_dump_object(self, obj): ...
    def end_object(self, obj): ...
    def get_value(self):
        return super(serializers.python.Serializer, self).getvalue()
