import json
import logging
from django.utils.crypto import get_random_string
from apps.message.lib.upload import upload_file_s3
from itertools import chain
from urllib.parse import urljoin
import requests
from bandwidth.serializers import MessageSerializer
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from apps.message.receive_message_utils.receive_utils import save_received_message_maps
from apps.message.send_message_utils.send_utils import upload_byte_file
from .get_conversations import get_conversation
from .models import Conversation, Message, MessageSendMap, MessageReceivedMap, UserNumber, ExternalNumber, MMSLink
from .send_message_utils.send_utils import save_send_message_maps, send_external, _data
from .send_message_utils.send_message_to_account_number import send_to_account_number
from .send_message_utils.send_message_to_external import send_to_external_number
from .serializers import NumberSerializer, ExternalNumberSerializer
from .validator.validator import validate_number, get_callback_url, make_headers
from apps.message.send_message_utils.enum import MessageTypeEnum


logger = logging.getLogger(__name__)


class SmsView(ViewSet):

    @transaction.atomic
    def create(self, request, format=None):
        message = request.data.get('message').lstrip()
        message_to = request.data.get('message_to')
        message_from = request.data.get('message_from')
        media = request.data.get('media', None)
        if None in [message_to, message_from]:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        message_to = validate_number(message_to)
        message_from = validate_number(message_from)

        if any([message_to is False, message_from is False]):
            return Response(
                {'error': 'The Number is not Correct. Please Enter valid Number. Sample Format: +1-xxx-xxx-xxxx (US)'},
                status=status.HTTP_400_BAD_REQUEST)

        event_type = MessageTypeEnum.SMS.value

        if media is not None:
            if media == []:
                return Response({'error': 'You must send list of links here.'}, status=status.HTTP_400_BAD_REQUEST)
            event_type = MessageTypeEnum.MMS.value

        user_id = request.user.id
        message_from = UserNumber.objects.filter(number=message_from).first()
        if message_from is None:
            return Response({'error': 'The From number is not exists!'}, status=status.HTTP_400_BAD_REQUEST)

        # saving conversation start
        conversation_instance = get_conversation(sender=message_from.number, receiver=message_to)
        callback_url = get_callback_url(user_id)
        headers = make_headers()

        # Now we have to check if the message_to has any external number to send
        cell_numbers = ExternalNumber.objects.filter(number__number=message_to).values_list('e164', flat=True)

        if cell_numbers.count() == 0:  # means :  message_to has no external for forwarding to cell phone
            data = _data(_from=message_from.number, to=message_to, text=message, callback_url=callback_url, media=media)

            send_sms = send_to_account_number(data)
            if send_sms.status_code == 201:
                save_send_message = save_send_message_maps(text=message, conversation_id=conversation_instance.id,
                                                           event_type=event_type, media=media)
                return Response(send_sms.text, status=status.HTTP_201_CREATED)
            else:
                response = json.loads(send_sms.content.decode('utf-8'))
                return Response({'error': response['message']}, status=status.HTTP_400_BAD_REQUEST)

        else:  # means :  message_to has has external . We need to use souce here
            logger.info('Sending message to External number list  %s', cell_numbers)
            actual_from_number = message_from.number

            # call here send_external
            number_to_obj = UserNumber.objects.filter(number=message_to).first()
            res = send_external(number_to_obj, actual_from_number, cell_numbers, message, callback_url,
                                headers, media=media)  # return true or false

            if res:
                # Now save on Message and MessageSendMap
                save_send_message = save_send_message_maps(text=message, conversation_id=conversation_instance.id,
                                                           event_type=event_type, media=media)

                # Okay .. I shouldn't save the receive map right here ..But I had to . Why ?
                # because i found every time it's send messge from OUR source to any Number CALLBACK
                # is basically state==sent. That's why i couldn't save there . So try here :(
                save_received_message = save_received_message_maps(text=message,
                                                                   conversation_id=conversation_instance.id,
                                                                   event_type=event_type, media=media)

                return Response(status=status.HTTP_201_CREATED)

            else:
                return Response({'error': 'Message sending process failed to your external numbers. '},
                                status=status.HTTP_400_BAD_REQUEST)


class ForwardSmsView(ViewSet):
    @transaction.atomic
    def create(self, request, message_id):
        forward_number = request.data.get('forward_number').strip()
        message_from = request.data.get('message_from')
        event_type = None

        if forward_number == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)

        forward_number = validate_number(forward_number)
        message_from = validate_number(message_from)
        if any([forward_number is False, message_from is False]):
            return Response(
                {'error': 'The Number is not Correct. Please Enter valid Number. Sample Formate: +1-xxx-xxx-xxxx (US)'},
                status=status.HTTP_400_BAD_REQUEST)

        user_id = request.user.id
        message_history = Message.objects.filter(id=message_id).first()
        media = MMSLink.objects.filter(message_id=message_id).values_list('link', flat=True)
        media = list(media)

        if message_history is None:
            return Response({'error': 'Message not found!'}, status=status.HTTP_400_BAD_REQUEST)

        message_from = UserNumber.objects.filter(number=message_from).first()
        if message_from is None:
            return Response({'error': 'message_from   Number is not valid!'}, status=status.HTTP_400_BAD_REQUEST)

        if message_history.type == MessageTypeEnum.MMS.value:
            event_type = MessageTypeEnum.MMS.value

        # saving conversation start
        conversation_instance = get_conversation(sender=message_from.number, receiver=forward_number)
        callback_url = get_callback_url(user_id)
        headers = make_headers()
        # Now we have to check if the message_to has any external number to send
        cell_numbers = ExternalNumber.objects.filter(number__number=forward_number).values_list('e164', flat=True)

        if cell_numbers.count() == 0:  # means :  message_to has no external for forwarding to cell phone
            if ' - ' in message_history.text:
                system_number, original_text = (message_history.text).split(' - ')
            else:
                original_text = message_history.text
            data = _data(_from=message_from.number, to=forward_number, text=original_text, callback_url=callback_url,
                         media=media)

            # send_sms = requests.post(settings.MESSAGE_URL, data=json.dumps(data), headers=headers,
            #                          auth=(settings.BANDWIDTH_API_TOKEN, settings.BANDWIDTH_API_SECRETE_KEY))

            send_sms = send_to_account_number(data)
            if send_sms.status_code == 201:
                # saving conversation end
                save_forward_message = save_send_message_maps(text=message_history.text,
                                                              conversation_id=conversation_instance.id,
                                                              event_type=event_type, media=media)
                return Response(send_sms.text, status=status.HTTP_201_CREATED)
            else:

                response = json.loads(send_sms.content.decode('utf-8'))
                return Response({'error': response['message']}, status=status.HTTP_400_BAD_REQUEST)

        else:  # means :  message_to has external . We need to use souce here
            actual_from_number = message_from.number
            # call here send_external
            number_to_obj = UserNumber.objects.filter(number=forward_number).first()
            res = send_external(number_to_obj, actual_from_number, cell_numbers, message_history.text, callback_url,
                                headers, media=media)  # return true or false
            if res:
                # Now save on Message and MessageSendMap
                save_forward_message = save_send_message_maps(text=message_history.text,
                                                              conversation_id=conversation_instance.id,
                                                              event_type=event_type, media=media)

                save_received_message = save_received_message_maps(text=message_history.text,
                                                                   conversation_id=conversation_instance.id,
                                                                   event_type=event_type, media=media)
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Message sending process failed to your external numbers. '},
                                status=status.HTTP_400_BAD_REQUEST)


class NumberView(APIView):

    @transaction.atomic
    def post(self, request, format=None):

        number = request.data.get('number')

        if number == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)

        number = validate_number(number)
        if number is False:
            return Response(
                {'error': 'The Number is not Correct. Please Enter valid Number. Sample Format: +1-xxx-xxx-xxxx (US)'},
                status=status.HTTP_400_BAD_REQUEST)

        check_number = UserNumber.objects.filter(number=number).exists()
        if check_number:
            return Response({'error': 'This number is already taken'},
                            status=status.HTTP_400_BAD_REQUEST)

        data = {
            'number': number,
            'user': request.user.id
        }

        serializer = NumberSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NumberListView(viewsets.ModelViewSet):
    serializer_class = NumberSerializer

    def get_queryset(self):
        data = UserNumber.objects.filter(user=self.request.user).order_by('id')
        return data


class DeleteNumberView(ViewSet):
    @transaction.atomic
    def destroy(self, request, number_id, format=None):
        delete_number = UserNumber.objects.filter(id=number_id, user_id=request.user.id).first()
        delete_number.delete()
        return Response({'message': 'Number deleted!'}, status=status.HTTP_204_NO_CONTENT)


class ContactList(APIView):

    def get(self, request):
        user_id = request.user.id

        number_instances = UserNumber.objects.filter(user_id=user_id)
        number_list = [number_instance.number for number_instance in number_instances]

        conversations = Conversation.objects.filter(Q(sender__in=number_list) | Q(receiver__in=number_list))

        contact_number_list = []
        for conversation in conversations:
            contact_number_list += [conversation.sender]
            contact_number_list += [conversation.receiver]

        unique_contact_number_list = set(contact_number_list)
        # removing owm number list
        for number in number_list:
            if number in unique_contact_number_list:
                unique_contact_number_list.remove(number)

        chat_numbers_arr = []
        for contact_number in unique_contact_number_list:
            for my_number in number_list:
                chat_numbers = Conversation.objects.filter(
                    Q(sender=contact_number, receiver=my_number) | Q(sender=my_number,
                                                                     receiver=contact_number))
                if chat_numbers:
                    temp = {}
                    temp['my_number'] = my_number
                    temp['contact_number'] = contact_number
                    chat_numbers_arr.append(temp)

        response = {
            "results": chat_numbers_arr
        }
        return Response(response, status=status.HTTP_200_OK)


class SingleChatHistory(APIView):
    def post(self, request):
        my_number = request.data.get('my_number')
        contact_number = request.data.get('contact_number')

        # send message history start
        send_conversation_ids = Conversation.objects.filter(
            sender=my_number, receiver=contact_number).values_list('id', flat=True)

        send_messase_objs = MessageSendMap.objects.filter(message__conversation_id__in=send_conversation_ids).order_by(
            '-time').values_list('message', flat=True)
        ordered_send_messages_ids = Message.objects.filter(id__in=send_messase_objs).values_list('id', flat=True)
        # send message history end

        # receive message history start
        receive_conversation_ids = Conversation.objects.filter(
            sender=contact_number, receiver=my_number).values_list('id', flat=True)

        receive_messase_objs = MessageReceivedMap.objects.filter(
            message__conversation_id__in=receive_conversation_ids).values_list('message', flat=True).all()
        ordered_receive_messages_ids = Message.objects.filter(id__in=receive_messase_objs).values_list('id', flat=True)
        # receive message history end

        combine_result_message_ids = list(chain(ordered_send_messages_ids, ordered_receive_messages_ids))
        chats_history = Message.objects.filter(id__in=combine_result_message_ids).order_by('-time')

        serializers = MessageSerializer(chats_history, many=True)

        response = {
            "results": serializers.data,
            'count': len(serializers.data)
        }
        return Response(response, status=status.HTTP_200_OK)


class P2PChatHistory(viewsets.ModelViewSet):
    serializer_class = MessageSerializer

    def get_queryset(self):
        e164 = self.kwargs.get('e164')
        contact_number = self.kwargs.get('number')

        # send message history start
        send_conversation_ids = Conversation.objects.filter(
            sender=e164, receiver=contact_number).values_list('id', flat=True)

        send_messase_objs = MessageSendMap.objects.filter(message__conversation_id__in=send_conversation_ids).order_by(
            '-time').values_list('message', flat=True)
        ordered_send_messages_ids = Message.objects.filter(id__in=send_messase_objs).values_list('id', flat=True)
        # send message history end

        # receive message history start
        receive_conversation_ids = Conversation.objects.filter(
            sender=contact_number, receiver=e164).values_list('id', flat=True)

        receive_messase_objs = MessageReceivedMap.objects.filter(
            message__conversation_id__in=receive_conversation_ids).values_list('message', flat=True).all()
        ordered_receive_messages_ids = Message.objects.filter(id__in=receive_messase_objs).values_list('id', flat=True)
        # receive message history end

        combine_result_message_ids = list(chain(ordered_send_messages_ids, ordered_receive_messages_ids))
        chats_history = Message.objects.filter(id__in=combine_result_message_ids).order_by('-time')

        return chats_history


class ExternalNumberView(viewsets.ModelViewSet):
    serializer_class = ExternalNumberSerializer

    @transaction.atomic
    def create(self, request):
        system_number = request.data.get('system_number')
        cell_phone = request.data.get('cell_phone')
        if system_number == '' or cell_phone == '':
            return Response({"error": "Field can\'t be empty."})

        cell_phone = validate_number(cell_phone)
        if cell_phone is False:
            return Response({
                'error': 'The Cell Number is not Correct. Please Enter valid Number. Sample Formate: +1-xxx-xxx-xxxx (US)'},
                status=status.HTTP_400_BAD_REQUEST)

        system_number_instance = UserNumber.objects.filter(number=system_number).first()
        if system_number_instance is None:
            return Response({'error': 'The Number is doesn\'t exists!'}, status=status.HTTP_400_BAD_REQUEST)

        is_already_exists = ExternalNumber.objects.filter(e164=cell_phone, number_id=system_number_instance.pk).exists()

        if is_already_exists:
            return Response({'error': 'Cell number already forworded.'}, status=status.HTTP_400_BAD_REQUEST)

        source_list = open(settings.FILE_PATH)
        source_numbers = source_list.read().split(', ')
        random_number = None

        all_used_sources = ExternalNumber.objects.filter(number_id=system_number_instance).values_list('source',
                                                                                                       flat=True)
        all_used_sources = all_used_sources.distinct()

        for sn in source_numbers:
            if sn not in all_used_sources:
                random_number = sn
                break

        if random_number is None:
            return Response({'error': 'Sorry ! You have crossed our conversation limit.'},
                            status=status.HTTP_400_BAD_REQUEST)

        ex_num = ExternalNumber(source=random_number, e164=cell_phone, number_id=system_number_instance.pk)
        ex_num.save()
        return Response(status=status.HTTP_201_CREATED)

    def get_queryset(self):
        user_id = self.request.user.id
        number_instances = UserNumber.objects.filter(user_id=user_id).values_list('id', flat=True)
        data = ExternalNumber.objects.filter(id__in=number_instances).order_by('id')
        return data


class SingleNumberContactList(APIView):

    def get(self, request, e164):
        recent = request.GET.get('recent')
        e164 = validate_number(e164)

        user_id = request.user.id

        conversations = Conversation.objects.filter(Q(sender=e164) | Q(receiver=e164)).order_by('-last_updated_on')

        contact_number_list = []
        for conversation in conversations:
            contact_number_list += [(conversation.sender).strip()]
            contact_number_list += [(conversation.receiver).strip()]

        unique_contact_number_list = []
        for c_number in contact_number_list:
            if c_number not in unique_contact_number_list:
                unique_contact_number_list.append(c_number)
         # removing owm number list
        # for number in number_list:
        #     if number in unique_contact_number_list:
        #         unique_contact_number_list.remove(number)

        chat_numbers_arr = []
        for contact_number in unique_contact_number_list:

            conversation_ids = Conversation.objects.filter(
                Q(sender=contact_number, receiver=e164) | Q(sender=e164, receiver=contact_number)).order_by(
                '-last_updated_on').values_list('id', flat=True)
            if conversation_ids:
                temp = {}
                last_msg = Message.objects.filter(conversation_id__in=conversation_ids).order_by('-time').first()

                media = []

                temp['number'] = contact_number
                temp['msg_text'] = last_msg.text
                temp['msg_type'] = last_msg.type
                temp['msg_time'] = last_msg.time

                if last_msg.type == MessageTypeEnum.MMS.value:
                    links = MMSLink.objects.filter(message_id=last_msg.pk).values_list('link', flat=True)
                    media = list(links)

                temp['media'] = media

                chat_numbers_arr.append(temp)

        if recent:
            chat_numbers_arr = chat_numbers_arr[:int(recent)]

        response = {
            "results": chat_numbers_arr
        }
        return Response(response, status=status.HTTP_200_OK)


class SingleExternalView(viewsets.ModelViewSet):
    serializer_class = ExternalNumberSerializer

    def destroy(self, request, number):
        external_instance = ExternalNumber.objects.filter(number__number=number).first()
        if external_instance:
            external_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        number = self.kwargs.get('number')
        data = ExternalNumber.objects.filter(number__number=number).order_by('-id')
        return data


class UploadView(APIView):

    def post(self, request, format=None):
        file = request.FILES.get('file', None)

        if file is None:
            return Response({"error": "No file selected!"}, status=status.HTTP_400_BAD_REQUEST)

        filename = upload_file_s3(file=file)

        file_link = 'https://s3.us-east-2.amazonaws.com/' + settings.MESSAGE_BUCKET_NAME + '/' + filename

        response = {
            'link': file_link,
        }
        return Response(response, status=status.HTTP_200_OK)
