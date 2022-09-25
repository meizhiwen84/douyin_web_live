import gzip
import json
import threading
from typing import TYPE_CHECKING

import requests

from config.helper import config
from messages.chat import ChatMessage
from messages.control import ControlMessage
from messages.fansclub import FansclubMessage
from messages.gift import GiftMessage
from messages.like import LikeMessage
from messages.member import MemberMessage
from messages.roomuserseq import RoomUserSeqMessage
from messages.social import SocialMessage
from output.debug import DebugWriter
from output.print import Print
from output.xml import XMLWriter
from protobuf import message_pb2, wss_pb2
from proxy.queues import MESSAGE_QUEUE

if TYPE_CHECKING:
    from typing import Type, Optional, List
    from output.IOutput import IOutput
    from proxy.common import MessagePayload


class OutputManager():
    _mapping: "dict[str, Type[IOutput]]" = {
        "print": Print,
        "xml": XMLWriter,
        "debug": DebugWriter,
    }
    _writer: "List[IOutput]" = []
    _thread: "Optional[threading.Thread]"= None
    _should_exit = threading.Event()

    def __init__(self,tableSingal):
        self.mainSignal=tableSingal
        _config = config()['output']['use']
        if type(_config) != list:
            _config = [_config]
        for _c in _config:
            if _c not in self._mapping:
                raise Exception("不支持的输出方式")
            self._writer.append(self._mapping[_c]())

    def __del__(self):
        self.terminate()

    def decode_payload(self, message: "MessagePayload"):
        try:
            response = message_pb2.Response()
            wss = wss_pb2.WssResponse()
            wss.ParseFromString(message.body)
            decompressed = gzip.decompress(wss.data)
            response.ParseFromString(decompressed)
            self.decode_message(response.messages)
        except Exception as e:
            for writer in self._writer:
                writer.error_output("ParseError", message.body, e)

    def queryUserData(self,uid):
        userUrl='https://live.douyin.com/webcast/user/?aid=6383&target_uid='+str(uid)

        Headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        }
        result = requests.get(url=userUrl, headers=Headers)
        jo = json.loads(result.content)
        return (jo.get("data").get("share_qrcode_uri"),jo.get("data").get("sec_uid"))


    def decode_message(self, message_list: "List[message_pb2.Message]"):
        for message in message_list:
            try:
                if message.method == 'WebcastMemberMessage':
                    member_message = MemberMessage()
                    member_message.set_payload(message.payload)
                    for writer in self._writer:
                        writer.member_output(member_message)

                        tempUser=member_message.user()
                        tempContent=member_message.content()
                        sexStr = "男" if tempUser.gender == 1 else ("女" if tempUser.gender == 2 else "人妖")

                        # userData=self.queryUserData(tempUser.id)
                        # todo meizhiwen secUid是不是可以加到proto文件里面
                        commentlist = [
                            [tempUser.id, tempUser.displayId, 2, tempUser.nickname,
                             tempUser.followInfo.followingCount, tempUser.followInfo.followerCount, 3002, 13,
                             sexStr, "上海", tempContent]
                        ]
                        self.mainSignal.emit(commentlist)
                elif message.method == 'WebcastSocialMessage':
                    social_message = SocialMessage()
                    social_message.set_payload(message.payload)
                    for writer in self._writer:
                        writer.social_output(social_message)

                        tempUser = social_message.user()
                        tempContent = social_message.commentContent()
                        sexStr="男" if tempUser.gender == 1 else ("女" if tempUser.gender == 2 else "人妖")

                        # userData = self.queryUserData(tempUser.id)

                        commentlist = [
                            [tempUser.id, tempUser.displayId, 2, tempUser.nickname,
                             tempUser.followInfo.followingCount, tempUser.followInfo.followerCount, 3002, 13,
                             sexStr,  "上海", tempContent]
                        ]
                        self.mainSignal.emit(commentlist)
                elif message.method == 'WebcastChatMessage':
                    chat_message = ChatMessage()
                    chat_message.set_payload(message.payload)
                    for writer in self._writer:
                        writer.chat_output(chat_message)

                        tempUser = chat_message.user()
                        tempContent = chat_message.commentContent()
                        sexStr = "男" if tempUser.gender == 1 else ("女" if tempUser.gender == 2 else "人妖")

                        # userData = self.queryUserData(tempUser.id)

                        commentlist = [
                            [tempUser.id, tempUser.displayId, 2, tempUser.nickname,
                             tempUser.followInfo.followingCount, tempUser.followInfo.followerCount, 3002, 13,
                             sexStr, "上海",  tempContent]
                        ]
                        self.mainSignal.emit(commentlist)
                elif message.method == 'WebcastLikeMessage':
                    like_message = LikeMessage()
                    like_message.set_payload(message.payload)
                    for writer in self._writer:
                        writer.like_output(like_message)

                        tempUser = like_message.user()
                        tempContent = like_message.commentContent()
                        sexStr = "男" if tempUser.gender == 1 else ("女" if tempUser.gender == 2 else "人妖")

                        # userData = self.queryUserData(tempUser.id)

                        commentlist = [
                            [tempUser.id, tempUser.displayId, 2, tempUser.nickname,
                             tempUser.followInfo.followingCount, tempUser.followInfo.followerCount, 3002, 13,
                             sexStr, "上海", tempContent]
                        ]
                        self.mainSignal.emit(commentlist)
                elif message.method == 'WebcastGiftMessage':
                    gift_message = GiftMessage()
                    gift_message.set_payload(message.payload)
                    for writer in self._writer:
                        writer.gift_output(gift_message)

                        tempUser = gift_message.user()
                        tempContent = gift_message.format_content()
                        sexStr = "男" if tempUser.gender == 1 else ("女" if tempUser.gender == 2 else "人妖")

                        # userData = self.queryUserData(tempUser.id)

                        commentlist = [
                            [tempUser.id, tempUser.displayId, 2, tempUser.nickname,
                             tempUser.followInfo.followingCount, tempUser.followInfo.followerCount, 3002, 13,
                             sexStr, "上海", tempContent]
                        ]
                        self.mainSignal.emit(commentlist)
                elif message.method == 'WebcastRoomUserSeqMessage':
                    room_user_seq_message = RoomUserSeqMessage()
                    room_user_seq_message.set_payload(message.payload)
                    for writer in self._writer:
                        writer.userseq_output(room_user_seq_message)

                        tempUser = room_user_seq_message.user()
                        tempContent = room_user_seq_message.format_content()
                        sexStr = "男" if tempUser.gender == 1 else ("女" if tempUser.gender == 2 else "人妖")

                        # userData = self.queryUserData(tempUser.id)

                        commentlist = [
                            [tempUser.id, tempUser.displayId, 2, tempUser.nickname,
                             tempUser.followInfo.followingCount, tempUser.followInfo.followerCount, 3002, 13,
                             sexStr, "上海", tempContent]
                        ]
                        self.mainSignal.emit(commentlist)
                elif message.method == 'WebcastControlMessage':
                    control_message = ControlMessage()
                    control_message.set_payload(message.payload)
                    for writer in self._writer:
                        writer.control_output(control_message)
                elif message.method == 'WebcastFansclubMessage':
                    fansclub_message = FansclubMessage()
                    fansclub_message.set_payload(message.payload)
                    for writer in self._writer:
                        writer.fansclub_output(fansclub_message)

                        tempUser = fansclub_message.user()
                        tempContent = fansclub_message.format_content()
                        sexStr = "男" if tempUser.gender == 1 else ("女" if tempUser.gender == 2 else "人妖")

                        # userData = self.queryUserData(tempUser.id)

                        commentlist = [
                            [tempUser.id, tempUser.displayId, 2, tempUser.nickname,
                             tempUser.followInfo.followingCount, tempUser.followInfo.followerCount, 3002, 13,
                             sexStr, "上海",  tempContent]
                        ]
                        self.mainSignal.emit(commentlist)
                else:
                    for writer in self._writer:
                        writer.other_output(message.method, message.payload)
            except Exception as e:
                for writer in self._writer:
                    writer.error_output(message.method, message.payload, e)

    def start_loop(self):
        self._should_exit.clear()
        self._thread = threading.Thread(target=self._handle)
        self._thread.start()

    def _handle(self):
        while True:
            message = MESSAGE_QUEUE.get()
            if self._should_exit.is_set():
                break
            if message is None:
                continue
            self.decode_payload(message)

    def terminate(self):
        if not self._should_exit.is_set():
            self._should_exit.set()
        MESSAGE_QUEUE.put(None)

        for writer in self._writer:
            writer.terminate()
