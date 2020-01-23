import json
import logging
from itertools import chain

import requests
from apps.message.receive_message_utils.receive_utils import save_received_message_maps
from apps.message.send_message_utils.enum import MessageTypeEnum
from apps.message.send_message_utils.send_utils import save_send_message_maps, _data, send_external
from apps.message.validator.validator import make_headers
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from message.get_conversations import get_conversation
from message.models import UserNumber, Conversation, Message, MessageSendMap, MessageReceivedMap, ExternalNumber, \
    TrackExternalConversation
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CallbackURLInfo
from .serializers import MessageSerializer

logger = logging.getLogger(__name__)


class CallBackView(APIView):

    @transaction.atomic
    def post(self, request, format=None):
        logger.info("I am callback  %s", request.data)

        number_from = request.data['from']
        number_to = request.data['to']
        text = request.data['text']
        state = request.data['state']
        eventType = request.data['eventType']
        media = request.data.get('media', None)

        if state == 'sent':
            logger.info('I am state==sent')
            pass

            # source_list = open(settings.FILE_PATH)
            # source_numbers = source_list.read().split(', ')
            #
            # is_come_from_external_number_with_source = False
            #
            # if number_from not in source_numbers:
            #     sender = number_from
            #     receiver = number_to
            # else:
            #     # that's mean user has external number and it is using our system sources
            #     is_come_from_external_number_with_source = True
            #
            #     system_number, original_text = text.split(' - ')
            #     sender = system_number
            #     cell_number = number_to
            #
            #     receiver_number_obj = ExternalNumber.objects.filter(source=number_from, e164=cell_number).first().number
            #     receiver = receiver_number_obj.number
            #
            # # saving conversation start
            # conversation_instance = get_conversation(sender=sender, receiver=receiver)
            #
            # #     when user sent a message to this will come.. But this might be problem ..
            # #     As every time when you Called External this callback will come
            # # eta Ami hide raklam karon Jokhon SMS send hossilo eki data 2 bar save hossilo
            #
            # if is_come_from_external_number_with_source:
            #     save_send_message_map = save_send_message_maps(text=text, conversation_id=conversation_instance.pk,
            #                                                    event_type=eventType, media=media)

        else:  # state=='received'

            logger.info('I am state==received')
            # first check if the number_to is on our system
            system_number_instances = UserNumber.objects.filter(number=number_to)

            if not system_number_instances.exists():  # New number.Not in system/ accountnumber
                logger.info('New number.Not in system/ accountnumber   number_to %s ', number_to)
                logger.info('New number.Not in system/ accountnumber   number_from %s ', number_from)
                source = number_to  # +13464040600

                external_number_instances = ExternalNumber.objects.filter(source=source, e164=number_from)

                if not external_number_instances.exists():
                    return Response({'error': 'We don\'t found any match for this number! '},
                                    status=status.HTTP_400_BAD_REQUEST)

                sender_number_obj = external_number_instances.first().number
                cell_number_owner = sender_number_obj.user

                sender_cell_number = number_from
                sender_system_number = sender_number_obj.number  # +12816388201  system number mean accountNumber

                pre_con_instance = TrackExternalConversation.objects.filter(source=source,
                                                                            receiver=sender_cell_number).last()
                if pre_con_instance is None:
                    return Response({'error': 'No Tracking for External Conversation found on system! '},
                                    status=status.HTTP_400_BAD_REQUEST)

                receiver = pre_con_instance.sender  # +19402209677
                # saving conversation start
                conversation_instance = get_conversation(sender=sender_system_number, receiver=receiver)

                # ============================    Saving  MessageSendMap   start=====================================

                save_send_message_map = save_send_message_maps(text=text, conversation_id=conversation_instance.pk,
                                                               event_type=eventType, media=media)

                # ============================    Saving  MessageSendMap   end=====================================

                # ==========================Now think User A send message from his cell number to User B Routable Account Numer .
                # if the pre_con_instance.sender was not web...and he was from mobile user then he must get the reply start===========
                # that's mean pre_con_instance.sender should not be in Number object

                if not UserNumber.objects.filter(number=pre_con_instance.sender).exists():
                    headers = make_headers()
                    callback_url = settings.CUSTOM_SMS_CALLBACKURL

                    data = _data(_from=sender_system_number, to=receiver, text=text, callback_url=callback_url,
                                 media=media)

                    send_sms = requests.post(settings.MESSAGE_URL, data=json.dumps(data), headers=headers,
                                             auth=(settings.BANDWIDTH_API_TOKEN, settings.BANDWIDTH_API_SECRETE_KEY))

                # ==========================Now think if the pre_con_instance.sender was not web...and he was from mobile user then he must get the reply  end===========


            else:  # System Number
                logger.info('I am in system Number')
                # saving conversation start
                conversation_instance = get_conversation(sender=number_from, receiver=number_to)

                logger.info('I am conversation_instance ',conversation_instance.pk)

                # Now time to check if receiver (number_to)  has routing ...Remember if he has then We can avoid CALLBACK .
                # Otherwise same data will save multiple time

                # =====================================  System number has Routing start============================
                cell_numbers = ExternalNumber.objects.filter(number__number=number_to).values_list('e164', flat=True)
                if cell_numbers.count() > 0:
                    logger.info('I am receiving for Outer number to system number who has external routes ')
                    callback_url = settings.CUSTOM_SMS_CALLBACKURL
                    headers = make_headers()

                    number_to_obj = UserNumber.objects.filter(number=number_to).first()
                    res = send_external(number_to_obj, number_from, cell_numbers, text, callback_url,
                                        headers, media=media)  # return true or false

                    if not res:
                        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                # =====================================  System number has Routing end ============================

                # ============================  From Phone to System number start ===================
                # suppose Jarrod send from his cell to our system number . then save send_message_map for jarrod
                system_number_instances_2 = UserNumber.objects.filter(number=number_from)
                if not system_number_instances_2.exists():
                    logger.info('saving send history for-- From Phone to System number')
                    save_send_message_map_data = save_send_message_maps(text=text, conversation_id=conversation_instance.pk,
                                                                   event_type=eventType, media=media)


                # ============================  From Phone to System number end ===================

            # saving conversation end
            save_received_message_map = save_received_message_maps(text=text, conversation_id=conversation_instance.pk,
                                                                   event_type=eventType, media=media)
        logger.info('I am end of successful callback  ')
        return Response(status=status.HTTP_200_OK)


class Last10MessageHistoryView(APIView):

    # if we need last 10 messages
    def get(self, request):
        user_id = request.user.id
        numbers = UserNumber.objects.filter(user_id=user_id)
        number_list = [number.number for number in numbers]

        # send message history start
        send_conversation_ids = Conversation.objects.filter(
            Q(sender__in=number_list)).values_list('id', flat=True)

        send_messase_objs = MessageSendMap.objects.filter(message__conversation_id__in=send_conversation_ids).order_by(
            '-time').values_list('message', flat=True)
        ordered_send_messages_ids = Message.objects.filter(id__in=send_messase_objs).values_list('id', flat=True)
        # send message history end

        # receive message history start
        receive_conversation_ids = Conversation.objects.filter(
            Q(receiver__in=number_list)).values_list('id', flat=True)

        receive_messase_objs = MessageReceivedMap.objects.filter(
            message__conversation_id__in=receive_conversation_ids).values_list('message', flat=True)
        ordered_receive_messages_ids = Message.objects.filter(id__in=receive_messase_objs).values_list('id', flat=True)
        # receive message history end

        combine_result_message_ids = list(chain(ordered_send_messages_ids, ordered_receive_messages_ids))
        order_combine_result_message_objs = Message.objects.filter(id__in=combine_result_message_ids).order_by('-time')[
                                            :10]

        serializers = MessageSerializer(order_combine_result_message_objs, many=True)
        response = {
            "results": serializers.data,
            "count": len(serializers.data)
        }
        return Response(response, status=status.HTTP_200_OK)


class SingleHistoryView(APIView):

    def get(self, request, message_id, format=None):
        data = Message.objects.filter(id=message_id).first()

        if data:
            serializer = MessageSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'History Not Found'}, status.HTTP_400_BAD_REQUEST)


class ChangeCallBackUrlView(APIView):
    @transaction.atomic
    def post(self, request, format=None):
        url = request.data.get('url').strip()
        if url == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)

        callback = CallbackURLInfo.objects.filter(user_id=request.user.id).first()
        if callback is None:
            callback = CallbackURLInfo(url=url, user_id=request.user.id)
            callback.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            callback.url = url
            callback.save()
            # return Response({'error': 'The URL Already Exists!'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_201_CREATED)


class GetNotification(APIView):

    def get(self, request):
        user_id = request.user.id
        numbers = UserNumber.objects.filter(user_id=user_id)
        number_list = [number.number for number in numbers]

        # receive message history start
        receive_conversation_ids = Conversation.objects.filter(
            Q(receiver__in=number_list)).values_list('id', flat=True)

        receive_messase_objs = MessageReceivedMap.objects.filter(
            message__conversation_id__in=receive_conversation_ids).values_list('message', flat=True)
        ordered_receive_messages_ids = Message.objects.filter(id__in=receive_messase_objs).values_list('id', flat=True)
        # receive message history end

        order_combine_result_message_objs = Message.objects.filter(id__in=ordered_receive_messages_ids).order_by(
            '-time')[:10]

        serializers = MessageSerializer(order_combine_result_message_objs, many=True)

        response = {
            "results": serializers.data,
            "count": len(serializers.data)
        }
        return Response(response, status=status.HTTP_200_OK)
