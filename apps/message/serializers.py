from rest_framework import serializers
from message.models import UserNumber, ExternalNumber


# Serializers define the API representation.
# class SMSSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SMS
#         fields = (
#             'id',
#             'direction',
#             'state',
#             'text',
#             'to_user',
#             'from_user',
#             'time')


class NumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNumber
        fields = ('id', 'user', 'number')

        def create(self, valid_data):
            initial_data = self.initial_data
            number = initial_data['number']

            number = UserNumber(number=number, user=initial_data['user'])
            number.save()
            return number


class ExternalNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalNumber
        fields = ('id', 'source', 'e164')

        # def create(self, valid_data):
        #     initial_data = self.initial_data
        #     number = initial_data['number']
        #
        #     number = UserNumber(number=number, user=initial_data['user'])
        #     number.save()
        #     return number