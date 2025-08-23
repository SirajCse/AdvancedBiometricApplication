# src/biometric/zk_lib/base.py
# -*- coding: utf-8 -*-
import sys
from datetime import datetime
from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM, socket, timeout
from struct import pack, unpack
import codecs
import logging
from typing import List, Optional, Dict, Any, Generator, Union, Tuple

from . import const
from .attendance import Attendance
from .exception import ZKErrorConnection, ZKErrorResponse, ZKNetworkError
from .user import User
from .finger import Finger

logger = logging.getLogger(__name__)

def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default

def make_commkey(key, session_id, ticks=50):
    """
    take a password and session_id and scramble them to send to the machine.
    copied from commpro.c - MakeKey
    """
    key = int(key)
    session_id = int(session_id)
    k = 0
    for i in range(32):
        if key & (1 << i):
            k = (k << 1) | 1
        else:
            k = k << 1
    k += session_id
    k = pack(b'I', k)
    k = unpack(b'BBBB', k)
    k = pack(b'BBBB', k[0] ^ ord('Z'), k[1] ^ ord('K'), k[2] ^ ord('S'), k[3] ^ ord('O'))
    k = unpack(b'HH', k)
    k = pack(b'HH', k[1], k[0])
    B = 255 & ticks
    k = unpack(b'BBBB', k)
    k = pack(b'BBBB', k[0] ^ B, k[1] ^ B, B, k[3] ^ B)
    return k

class ZK_helper(object):
    """
    ZK helper class
    """

    def __init__(self, ip, port=4370):
        """
        Construct a new 'ZK_helper' object.
        """
        self.address = (ip, port)
        self.ip = ip
        self.port = port

    def test_ping(self):
        """
        Returns True if host responds to a ping request

        :return: bool
        """
        import subprocess
        import platform
        ping_str = '-n 1' if platform.system().lower() == 'windows' else '-c 1 -W 5'
        args = 'ping ' + ping_str + ' ' + self.ip
        need_sh = False if platform.system().lower() == 'windows' else True
        return subprocess.call(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=need_sh) == 0

    def test_tcp(self):
        """
        test TCP connection
        """
        self.client = socket(AF_INET, SOCK_STREAM)
        self.client.settimeout(10)
        res = self.client.connect_ex(self.address)
        self.client.close()
        return res

    def test_udp(self):
        """
        test UDP connection
        """
        self.client = socket(AF_INET, SOCK_DGRAM)
        self.client.settimeout(10)
        return True

class ZK(object):
    """
    ZK main class - Complete version with all original functions
    """

    def __init__(self, ip, port=4370, timeout=60, password=0, force_udp=False,
                 ommit_ping=False, verbose=False, encoding='UTF-8'):
        """
        Construct a new 'ZK' object.
        """
        User.encoding = encoding
        self.__address = (ip, port)
        self.__sock = None
        self.__timeout = timeout
        self.__password = password
        self.__session_id = 0
        self.__reply_id = const.USHRT_MAX - 1
        self.__data_recv = None
        self.__data = None
        self.is_connect = False
        self.is_enabled = True
        self.helper = ZK_helper(ip, port)
        self.force_udp = force_udp
        self.ommit_ping = ommit_ping
        self.verbose = verbose
        self.encoding = encoding
        self.tcp = not force_udp
        self.users = 0
        self.fingers = 0
        self.records = 0
        self.dummy = 0
        self.cards = 0
        self.fingers_cap = 0
        self.users_cap = 0
        self.rec_cap = 0
        self.faces = 0
        self.faces_cap = 0
        self.fingers_av = 0
        self.users_av = 0
        self.rec_av = 0
        self.next_uid = 1
        self.next_user_id = '1'
        self.user_packet_size = 28
        self.end_live_capture = False
        self.__create_socket()

    def __create_socket(self):
        """Create appropriate socket based on connection type"""
        if self.tcp:
            self.__sock = socket(AF_INET, SOCK_STREAM)
        else:
            self.__sock = socket(AF_INET, SOCK_DGRAM)
        self.__sock.settimeout(self.__timeout)

    def __create_tcp_top(self, packet):
        """
        witch the complete packet set top header
        """
        length = len(packet)
        top = pack('<HHI', const.MACHINE_PREPARE_DATA_1, const.MACHINE_PREPARE_DATA_2, length)
        return top + packet

    def __create_header(self, command, command_string, session_id, reply_id):
        """
        Puts a the parts that make up a packet together and packs them into a byte string
        """
        buf = pack('<4H', command, 0, session_id, reply_id) + command_string
        buf = unpack('8B' + '%sB' % len(command_string), buf)
        checksum = unpack('H', self.__create_checksum(buf))[0]
        reply_id += 1
        if reply_id >= const.USHRT_MAX:
            reply_id -= const.USHRT_MAX
        buf = pack('<4H', command, checksum, session_id, reply_id)
        return buf + command_string

    def __create_checksum(self, p):
        """
        Calculates the checksum of the packet to be sent to the time clock
        Copied from zkemsdk.c
        """
        l = len(p)
        checksum = 0
        while l > 1:
            checksum += unpack('H', pack('BB', p[0], p[1]))[0]
            p = p[2:]
            if checksum > const.USHRT_MAX:
                checksum -= const.USHRT_MAX
            l -= 2
        if l:
            checksum = checksum + p[-1]
        while checksum > const.USHRT_MAX:
            checksum -= const.USHRT_MAX
        checksum = ~checksum
        while checksum < 0:
            checksum += const.USHRT_MAX
        return pack('H', checksum)

    def __test_tcp_top(self, packet):
        """
        return size!
        """
        if len(packet) <= 8:
            return 0
        tcp_header = unpack('<HHI', packet[:8])
        if tcp_header[0] == const.MACHINE_PREPARE_DATA_1 and tcp_header[1] == const.MACHINE_PREPARE_DATA_2:
            return tcp_header[2]
        return 0

    def __send_command(self, command, command_string=b'', response_size=8):
        """
        send command to the terminal
        """
        if command not in (const.CMD_CONNECT, const.CMD_AUTH) and (not self.is_connect):
            raise ZKErrorConnection('instance are not connected.')

        buf = self.__create_header(command, command_string, self.__session_id, self.__reply_id)

        try:
            if self.tcp:
                top = self.__create_tcp_top(buf)
                self.__sock.send(top)
                self.__tcp_data_recv = self.__sock.recv(response_size + 8)
                self.__tcp_length = self.__test_tcp_top(self.__tcp_data_recv)
                if self.__tcp_length == 0:
                    raise ZKNetworkError('TCP packet invalid')
                self.__header = unpack('<4H', self.__tcp_data_recv[8:16])
                self.__data_recv = self.__tcp_data_recv[8:]
            else:
                self.__sock.sendto(buf, self.__address)
                self.__data_recv = self.__sock.recv(response_size)
                self.__header = unpack('<4H', self.__data_recv[:8])
        except Exception as e:
            raise ZKNetworkError(str(e))

        self.__response = self.__header[0]
        self.__reply_id = self.__header[3]
        self.__data = self.__data_recv[8:]

        if self.__response in [const.CMD_ACK_OK, const.CMD_PREPARE_DATA, const.CMD_DATA]:
            return {'status': True, 'code': self.__response}
        return {'status': False, 'code': self.__response}

    def __ack_ok(self):
        """
        event ack ok
        """
        buf = self.__create_header(const.CMD_ACK_OK, b'', self.__session_id, const.USHRT_MAX - 1)
        try:
            if self.tcp:
                top = self.__create_tcp_top(buf)
                self.__sock.send(top)
            else:
                self.__sock.sendto(buf, self.__address)
        except Exception as e:
            raise ZKNetworkError(str(e))

    def __get_data_size(self):
        """
        Checks a returned packet to see if it returned CMD_PREPARE_DATA,
        indicating that data packets are to be sent

        Returns the amount of bytes that are going to be sent
        """
        response = self.__response
        if response == const.CMD_PREPARE_DATA:
            size = unpack('I', self.__data[:4])[0]
            return size
        return 0

    def __reverse_hex(self, hex):
        data = ''
        for i in reversed(range(len(hex) // 2)):
            data += hex[i * 2:i * 2 + 2]
        return data

    def __decode_time(self, t):
        """
        Decode a timestamp retrieved from the timeclock

        copied from zkemsdk.c - DecodeTime
        """
        t = unpack('<I', t)[0]
        second = t % 60
        t = t // 60
        minute = t % 60
        t = t // 60
        hour = t % 24
        t = t // 24
        day = t % 31 + 1
        t = t // 31
        month = t % 12 + 1
        t = t // 12
        year = t + 2000
        d = datetime(year, month, day, hour, minute, second)
        return d

    def __decode_timehex(self, timehex):
        """
        timehex string of six bytes
        """
        year, month, day, hour, minute, second = unpack('6B', timehex)
        year += 2000
        d = datetime(year, month, day, hour, minute, second)
        return d

    def __encode_time(self, t):
        """
        Encode a timestamp so that it can be read on the timeclock
        """
        d = (t.year % 100 * 12 * 31 + (t.month - 1) * 31 + t.day - 1) * 86400 + (t.hour * 60 + t.minute) * 60 + t.second
        return d

    def connect(self):
        """
        connect to the device

        :return: bool
        """
        self.end_live_capture = False
        if not self.ommit_ping and (not self.helper.test_ping()):
            raise ZKNetworkError("can't reach device (ping %s)" % self.__address[0])

        if not self.force_udp and self.helper.test_tcp() == 0:
            self.user_packet_size = 72

        self.__create_socket()
        self.__session_id = 0
        self.__reply_id = const.USHRT_MAX - 1

        # Connect to the device
        if self.tcp:
            self.__sock.connect(self.__address)

        cmd_response = self.__send_command(const.CMD_CONNECT)
        self.__session_id = self.__header[2]

        if cmd_response.get('code') == const.CMD_ACK_UNAUTH:
            if self.verbose:
                logger.debug('try auth')
            command_string = make_commkey(self.__password, self.__session_id)
            cmd_response = self.__send_command(const.CMD_AUTH, command_string)

        if cmd_response.get('status'):
            self.is_connect = True
            logger.info(f"Connected to device {self.__address[0]}:{self.__address[1]}")
            return self

        if cmd_response['code'] == const.CMD_ACK_UNAUTH:
            raise ZKErrorResponse('Unauthenticated')

        if self.verbose:
            logger.debug('connect err response {} '.format(cmd_response['code']))
        raise ZKErrorResponse("Invalid response: Can't connect")

    def disconnect(self):
        """
        diconnect from the connected device

        :return: bool
        """
        if self.is_connect:
            try:
                cmd_response = self.__send_command(const.CMD_EXIT)
                if cmd_response.get('status'):
                    self.is_connect = False
            except:
                pass

        if self.__sock:
            try:
                self.__sock.close()
            except:
                pass
            finally:
                self.__sock = None

        logger.info(f"Disconnected from device {self.__address[0]}:{self.__address[1]}")
        return True

    def enable_device(self):
        """
        re-enable the connected device and allow user activity in device again

        :return: bool
        """
        cmd_response = self.__send_command(const.CMD_ENABLEDEVICE)
        if cmd_response.get('status'):
            self.is_enabled = True
            return True
        raise ZKErrorResponse("Can't enable device")

    def disable_device(self):
        """
        disable (lock) device, to ensure no user activity in device while some process run

        :return: bool
        """
        cmd_response = self.__send_command(const.CMD_DISABLEDEVICE)
        if cmd_response.get('status'):
            self.is_enabled = False
            return True
        raise ZKErrorResponse("Can't disable device")

    def get_firmware_version(self):
        """
        :return: the firmware version
        """
        cmd_response = self.__send_command(const.CMD_GET_VERSION, b'', 1024)
        if cmd_response.get('status'):
            firmware_version = self.__data.split(b'\x00')[0]
            return firmware_version.decode()
        raise ZKErrorResponse("Can't read firmware version")

    def get_serialnumber(self):
        """
        :return: the serial number
        """
        command = const.CMD_OPTIONS_RRQ
        command_string = b'~SerialNumber\x00'
        response_size = 1024
        cmd_response = self.__send_command(command, command_string, response_size)
        if cmd_response.get('status'):
            serialnumber = self.__data.split(b'=', 1)[-1].split(b'\x00')[0]
            serialnumber = serialnumber.replace(b'=', b'')
            return serialnumber.decode()
        raise ZKErrorResponse("Can't read serial number")

    def get_platform(self):
        """
        :return: the platform name
        """
        command = const.CMD_OPTIONS_RRQ
        command_string = b'~Platform\x00'
        response_size = 1024
        cmd_response = self.__send_command(command, command_string, response_size)
        if cmd_response.get('status'):
            platform = self.__data.split(b'=', 1)[-1].split(b'\x00')[0]
            platform = platform.replace(b'=', b'')
            return platform.decode()
        raise ZKErrorResponse("Can't read platform name")

    def get_mac(self):
        """
        :return: the machine's mac address
        """
        command = const.CMD_OPTIONS_RRQ
        command_string = b'MAC\x00'
        response_size = 1024
        cmd_response = self.__send_command(command, command_string, response_size)
        if cmd_response.get('status'):
            mac = self.__data.split(b'=', 1)[-1].split(b'\x00')[0]
            return mac.decode()
        raise ZKErrorResponse("can't read mac address")

    def get_device_name(self):
        """
        return the device name

        :return: str
        """
        command = const.CMD_OPTIONS_RRQ
        command_string = b'~DeviceName\x00'
        response_size = 1024
        cmd_response = self.__send_command(command, command_string, response_size)
        if cmd_response.get('status'):
            device = self.__data.split(b'=', 1)[-1].split(b'\x00')[0]
            return device.decode()
        return ''

    def get_face_version(self):
        """
        :return: the face version
        """
        command = const.CMD_OPTIONS_RRQ
        command_string = b'ZKFaceVersion\x00'
        response_size = 1024
        cmd_response = self.__send_command(command, command_string, response_size)
        if cmd_response.get('status'):
            response = self.__data.split(b'=', 1)[-1].split(b'\x00')[0]
            return safe_cast(response, int, 0) if response else 0
        return 0

    def get_fp_version(self):
        """
        :return: the fingerprint version
        """
        command = const.CMD_OPTIONS_RRQ
        command_string = b'~ZKFPVersion\x00'
        response_size = 1024
        cmd_response = self.__send_command(command, command_string, response_size)
        if cmd_response.get('status'):
            response = self.__data.split(b'=', 1)[-1].split(b'\x00')[0]
            response = response.replace(b'=', b'')
            return safe_cast(response, int, 0) if response else 0
        return 0

    def _clear_error(self, command_string=b''):
        """
        clear ACK_error
        """
        cmd_response = self.__send_command(const.CMD_ACK_ERROR, command_string, 1024)
        cmd_response = self.__send_command(const.CMD_ACK_UNKNOWN, command_string, 1024)
        cmd_response = self.__send_command(const.CMD_ACK_UNKNOWN, command_string, 1024)
        cmd_response = self.__send_command(const.CMD_ACK_UNKNOWN, command_string, 1024)

    def get_extend_fmt(self):
        """
        determine extend fmt
        """
        command = const.CMD_OPTIONS_RRQ
        command_string = b'~ExtendFmt\x00'
        response_size = 1024
        cmd_response = self.__send_command(command, command_string, response_size)
        if cmd_response.get('status'):
            fmt = self.__data.split(b'=', 1)[-1].split(b'\x00')[0]
            return safe_cast(fmt, int, 0) if fmt else 0
        self._clear_error(command_string)
        return 0

    def get_user_extend_fmt(self):
        """
        determine user extend fmt
        """
        command = const.CMD_OPTIONS_RRQ
        command_string = b'~UserExtFmt\x00'
        response_size = 1024
        cmd_response = self.__send_command(command, command_string, response_size)
        if cmd_response.get('status'):
            fmt = self.__data.split(b'=', 1)[-1].split(b'\x00')[0]
            return safe_cast(fmt, int, 0) if fmt else 0
        self._clear_error(command_string)
        return 0

    def get_face_fun_on(self):
        """
        determine extend fmt
        """
        command = const.CMD_OPTIONS_RRQ
        command_string = b'FaceFunOn\x00'
        response_size = 1024
        cmd_response = self.__send_command(command, command_string, response_size)
        if cmd_response.get('status'):
            response = self.__data.split(b'=', 1)[-1].split(b'\x00')[0]
            return safe_cast(response, int, 0) if response else 0
        self._clear_error(command_string)
        return 0

    def get_compat_old_firmware(self):
        """
        determine old firmware
        """
        command = const.CMD_OPTIONS_RRQ
        command_string = b'CompatOldFirmware\x00'
        response_size = 1024
        cmd_response = self.__send_command(command, command_string, response_size)
        if cmd_response.get('status'):
            response = self.__data.split(b'=', 1)[-1].split(b'\x00')[0]
            return safe_cast(response, int, 0) if response else 0
        self._clear_error(command_string)
        return 0

    def get_network_params(self):
        """
        get network params
        """
        ip = self.__address[0]
        mask = b''
        gate = b''
        cmd_response = self.__send_command(const.CMD_OPTIONS_RRQ, b'IPAddress\x00', 1024)
        if cmd_response.get('status'):
            ip = self.__data.split(b'=', 1)[-1].split(b'\x00')[0]
        cmd_response = self.__send_command(const.CMD_OPTIONS_RRQ, b'NetMask\x00', 1024)
        if cmd_response.get('status'):
            mask = self.__data.split(b'=', 1)[-1].split(b'\x00')[0]
        cmd_response = self.__send_command(const.CMD_OPTIONS_RRQ, b'GATEIPAddress\x00', 1024)
        if cmd_response.get('status'):
            gate = self.__data.split(b'=', 1)[-1].split(b'\x00')[0]
        return {'ip': ip.decode(), 'mask': mask.decode(), 'gateway': gate.decode()}

    def get_pin_width(self):
        """
        :return: the PIN width
        """
        command = const.CMD_GET_PINWIDTH
        command_string = b' P'
        response_size = 9
        cmd_response = self.__send_command(command, command_string, response_size)
        if cmd_response.get('status'):
            width = self.__data.split(b'\x00')[0]
            return bytearray(width)[0]
        raise ZKErrorResponse('can0t get pin width')

    def free_data(self):
        """
        clear buffer

        :return: bool
        """
        command = const.CMD_FREE_DATA
        cmd_response = self.__send_command(command)
        if cmd_response.get('status'):
            return True
        raise ZKErrorResponse("can't free data")

    def read_sizes(self):
        """
        read the memory ussage
        """
        command = const.CMD_GET_FREE_SIZES
        response_size = 1024
        cmd_response = self.__send_command(command, b'', response_size)
        if cmd_response.get('status'):
            if self.verbose:
                print(codecs.encode(self.__data, 'hex'))
            size = len(self.__data)
            if len(self.__data) >= 80:
                fields = unpack('20i', self.__data[:80])
                self.users = fields[4]
                self.fingers = fields[6]
                self.records = fields[8]
                self.dummy = fields[10]
                self.cards = fields[12]
                self.fingers_cap = fields[14]
                self.users_cap = fields[15]
                self.rec_cap = fields[16]
                self.fingers_av = fields[17]
                self.users_av = fields[18]
                self.rec_av = fields[19]
                self.__data = self.__data[80:]
            if len(self.__data) >= 12:
                fields = unpack('3i', self.__data[:12])
                self.faces = fields[0]
                self.faces_cap = fields[2]
            return True
        raise ZKErrorResponse("can't read sizes")

    def unlock(self, time=3):
        """
        unlock the door

        thanks to https://github.com/SoftwareHouseMerida/pyzk/

        :param time: define delay in seconds
        :return: bool
        """
        command = const.CMD_UNLOCK
        command_string = pack('I', int(time) * 10)
        cmd_response = self.__send_command(command, command_string)
        if cmd_response.get('status'):
            return True
        raise ZKErrorResponse("Can't open door")

    def __str__(self):
        """
        for debug
        """
        return 'ZK %s://%s:%s users[%i]:%i/%i fingers:%i/%i, records:%i/%i faces:%i/%i' % ('tcp' if self.tcp else 'udp', self.__address[0], self.__address[1], self.user_packet_size, self.users, self.users_cap, self.fingers, self.fingers_cap, self.records, self.rec_cap, self.faces, self.faces_cap)

    def restart(self):
        """
        restart the device

        :return: bool
        """
        command = const.CMD_RESTART
        cmd_response = self.__send_command(command)
        if cmd_response.get('status'):
            self.is_connect = False
            self.next_uid = 1
            return True
        raise ZKErrorResponse("can't restart device")

    def get_time(self):
        """
        :return: the machine's time
        """
        command = const.CMD_GET_TIME
        response_size = 1032
        cmd_response = self.__send_command(command, b'', response_size)
        if cmd_response.get('status'):
            return self.__decode_time(self.__data[:4])
        raise ZKErrorResponse("can't get time")

    def set_time(self, timestamp):
        """
        set Device time (pass datetime object)

        :param timestamp: python datetime object
        """
        command = const.CMD_SET_TIME
        command_string = pack(b'I', self.__encode_time(timestamp))
        cmd_response = self.__send_command(command, command_string)
        if cmd_response.get('status'):
            return True
        raise ZKErrorResponse("can't set time")

    def poweroff(self):
        """
        shutdown the machine
        """
        command = const.CMD_POWEROFF
        command_string = b''
        response_size = 1032
        cmd_response = self.__send_command(command, command_string, response_size)
        if cmd_response.get('status'):
            self.is_connect = False
            self.next_uid = 1
            return True
        raise ZKErrorResponse("can't poweroff")

    def refresh_data(self):
        command = const.CMD_REFRESHDATA
        cmd_response = self.__send_command(command)
        if cmd_response.get('status'):
            return True
        raise ZKErrorResponse("can't refresh data")

    def test_voice(self, index=0):
        """
        play test voice
        """
        command = const.CMD_TESTVOICE
        command_string = pack('I', index)
        cmd_response = self.__send_command(command, command_string)
        if cmd_response.get('status'):
            return True
        return False

    def set_user(self, uid=None, name='', privilege=0, password='', group_id='', user_id='', card=0):
        """
        create or update user by uid
        """
        command = const.CMD_USER_WRQ
        if uid is None:
            uid = self.next_uid
            if not user_id:
                user_id = self.next_user_id
        if not user_id:
            user_id = str(uid)
        if privilege not in (const.USER_DEFAULT, const.USER_ADMIN):
            privilege = const.USER_DEFAULT
        privilege = int(privilege)

        if self.user_packet_size == 28:
            if not group_id:
                group_id = 0
            try:
                command_string = pack('HB5s8sIxBHI', uid, privilege, password.encode(self.encoding, errors='ignore'), name.encode(self.encoding, errors='ignore'), card, int(group_id), 0, int(user_id))
            except Exception as e:
                raise ZKErrorResponse("Can't pack user")
        else:
            name_pad = name.encode(self.encoding, errors='ignore').ljust(24, b'\x00')[:24]
            card_str = pack('<I', int(card))[:4]
            command_string = pack('HB8s24s4sx7sx24s', uid, privilege, password.encode(self.encoding, errors='ignore'), name_pad, card_str, group_id.encode(), user_id.encode())

        response_size = 1024
        cmd_response = self.__send_command(command, command_string, response_size)

        if not cmd_response.get('status'):
            raise ZKErrorResponse("Can't set user")

        self.refresh_data()
        if self.next_uid == uid:
            self.next_uid += 1
        if self.next_user_id == user_id:
            self.next_user_id = str(self.next_uid)

        return True

    def _send_with_buffer(self, buffer):
        MAX_CHUNK = 1024
        size = len(buffer)
        self.free_data()
        command = const.CMD_PREPARE_DATA
        command_string = pack('I', size)
        cmd_response = self.__send_command(command, command_string)
        if not cmd_response.get('status'):
            raise ZKErrorResponse("Can't prepare data")

        remain = size % MAX_CHUNK
        packets = (size - remain) // MAX_CHUNK
        start = 0

        for _wlk in range(packets):
            self.__send_chunk(buffer[start:start + MAX_CHUNK])
            start += MAX_CHUNK

        if remain:
            self.__send_chunk(buffer[start:start + remain])

    def __send_chunk(self, command_string):
        command = const.CMD_DATA
        cmd_response = self.__send_command(command, command_string)
        if cmd_response.get('status'):
            return True
        raise ZKErrorResponse("Can't send chunk")

    def save_user_template(self, user, fingers=[]):
        """
        save user and template
        """
        if not isinstance(user, User):
            users = self.get_users()
            tusers = list(filter(lambda x: x.uid == user, users))
            if len(tusers) == 1:
                user = tusers[0]
            else:
                tusers = list(filter(lambda x: x.user_id == str(user, users)))
                if len(tusers) == 1:
                    user = tusers[0]
                else:
                    raise ZKErrorResponse("Can't find user")

        if isinstance(fingers, Finger):
            fingers = [fingers]

        fpack = b''
        table = b''
        fnum = 16
        tstart = 0

        for finger in fingers:
            tfp = finger.repack_only()
            table += pack('<bHbI', 2, user.uid, fnum + finger.fid, tstart)
            tstart += len(tfp)
            fpack += tfp

        if self.user_packet_size == 28:
            upack = user.repack29()
        else:
            upack = user.repack73()

        head = pack('III', len(upack), len(table), len(fpack))
        packet = head + upack + table + fpack
        self._send_with_buffer(packet)

        command = 110
        command_string = pack('<IHH', 12, 0, 8)
        cmd_response = self.__send_command(command, command_string)

        if not cmd_response.get('status'):
            raise ZKErrorResponse("Can't save utemp")

        self.refresh_data()
        return True

    def delete_user_template(self, uid=0, temp_id=0, user_id=''):
        """
        Delete specific template
        """
        if self.tcp and user_id:
            command = 134
            command_string = pack('<24sB', str(user_id), temp_id)
            cmd_response = self.__send_command(command, command_string)
            if cmd_response.get('status'):
                return True
            return False

        if not uid:
            users = self.get_users()
            users = list(filter(lambda x: x.user_id == str(user_id), users))
            if not users:
                return False
            uid = users[0].uid

        command = const.CMD_DELETE_USERTEMP
        command_string = pack('hb', uid, temp_id)
        cmd_response = self.__send_command(command, command_string)

        if cmd_response.get('status'):
            return True
        return False

    def delete_user(self, uid=0, user_id=''):
        """
        delete specific user by uid or user_id
        """
        if not uid:
            users = self.get_users()
            users = list(filter(lambda x: x.user_id == str(user_id), users))
            if not users:
                return False
            uid = users[0].uid

        command = const.CMD_DELETE_USER
        command_string = pack('h', uid)
        cmd_response = self.__send_command(command, command_string)

        if not cmd_response.get('status'):
            raise ZKErrorResponse("Can't delete user")

        self.refresh_data()
        if uid == self.next_uid - 1:
            self.next_uid = uid

        return True

    def get_user_template(self, uid, temp_id=0, user_id=''):
        """
        get user template
        """
        if not uid:
            users = self.get_users()
            users = list(filter(lambda x: x.user_id == str(user_id), users))
            if not users:
                return False
            uid = users[0].uid

        for _retries in range(3):
            command = 88
            command_string = pack('hb', uid, temp_id)
            response_size = 1032
            cmd_response = self.__send_command(command, command_string, response_size)
            data = self.__recieve_chunk()
            if data is not None:
                resp = data[:-1]
                if resp[-6:] == b'\x00\x00\x00\x00\x00\x00':
                    resp = resp[:-6]
                return Finger(uid, temp_id, 1, resp)

        return None

    def get_templates(self):
        """
        get all templates
        """
        self.read_sizes()
        if self.fingers == 0:
            return []

        templates = []
        templatedata, size = self.read_with_buffer(const.CMD_DB_RRQ, const.FCT_FINGERTMP)

        if size < 4:
            return []

        total_size = unpack('i', templatedata[0:4])[0]
        templatedata = templatedata[4:]

        while total_size:
            size, uid, fid, valid = unpack('HHbb', templatedata[:6])
            template = unpack('%is' % (size - 6), templatedata[6:size])[0]
            finger = Finger(uid, fid, valid, template)
            templates.append(finger)
            templatedata = templatedata[size:]
            total_size -= size

        return templates

    def cancel_capture(self):
        """
        cancel capturing finger
        """
        command = const.CMD_CANCELCAPTURE
        cmd_response = self.__send_command(command)
        return bool(cmd_response.get('status'))

    def verify_user(self):
        """
        start verify finger mode
        """
        command = const.CMD_STARTVERIFY
        cmd_response = self.__send_command(command)
        if cmd_response.get('status'):
            return True
        raise ZKErrorResponse('Cant Verify')

    def reg_event(self, flags):
        """
        reg events
        """
        command = const.CMD_REG_EVENT
        command_string = pack('I', flags)
        cmd_response = self.__send_command(command, command_string)
        if not cmd_response.get('status'):
            raise ZKErrorResponse("cant' reg events %i" % flags)

    def set_sdk_build_1(self):
        command = const.CMD_OPTIONS_WRQ
        command_string = b'SDKBuild=1'
        cmd_response = self.__send_command(command, command_string)
        if not cmd_response.get('status'):
            return False
        return True

    def enroll_user(self, uid=0, temp_id=0, user_id=''):
        """
        start enroll user
        """
        command = const.CMD_STARTENROLL
        done = False

        if not user_id:
            users = self.get_users()
            users = list(filter(lambda x: x.uid == uid, users))
            if len(users) >= 1:
                user_id = users[0].user_id
            else:
                return False

        if self.tcp:
            command_string = pack('<24sbb', str(user_id).encode(), temp_id, 1)
        else:
            command_string = pack('<Ib', int(user_id), temp_id)

        self.cancel_capture()
        cmd_response = self.__send_command(command, command_string)

        if not cmd_response.get('status'):
            raise ZKErrorResponse('Cant Enroll user #%i [%i]' % (uid, temp_id))

        self.__sock.settimeout(60)
        attempts = 3

        while attempts:
            data_recv = self.__sock.recv(1032)
            self.__ack_ok()
            data_recv = self.__sock.recv(1032)
            self.__ack_ok()
            attempts -= 1

        self.__sock.settimeout(self.__timeout)
        self.verify_user()
        return True

    def get_attendance(self):
        """
        return attendance record
        """
        self.read_sizes()
        if self.records == 0:
            return []

        users = self.get_users()
        attendances = []
        attendance_data, size = self.read_with_buffer(const.CMD_ATTLOG_RRQ)

        if size < 4:
            return []

        total_size = unpack('I', attendance_data[:4])[0]
        record_size = total_size / self.records
        attendance_data = attendance_data[4:]

        if record_size == 8:
            while len(attendance_data) >= 8:
                uid, status, timestamp, punch = unpack('HB4sB', attendance_data.ljust(8, b'\x00')[:8])
                attendance_data = attendance_data[8:]
                tuser = list(filter(lambda x: x.uid == uid, users))
                if not tuser:
                    user_id = str(uid)
                else:
                    user_id = tuser[0].user_id
                timestamp = self.__decode_time(timestamp)
                attendance = Attendance(user_id, timestamp, status, punch, uid)
                attendances.append(attendance)
        else:
            while record_size == 16 and len(attendance_data) >= 16:
                user_id, timestamp, status, punch, reserved, workcode = unpack('<I4sBB2sI', attendance_data.ljust(16, b'\x00')[:16])
                user_id = str(user_id)
                attendance_data = attendance_data[16:]
                tuser = list(filter(lambda x: x.user_id == user_id, users))
                if not tuser:
                    uid = str(user_id)
                else:
                    uid = tuser[0].uid
                    user_id = tuser[0].user_id
                timestamp = self.__decode_time(timestamp)
                attendance = Attendance(user_id, timestamp, status, punch, uid)
                attendances.append(attendance)
            else:
                while len(attendance_data) >= 40:
                    uid, user_id, status, timestamp, punch, space = unpack('<H24sB4sB8s', attendance_data.ljust(40, b'\x00')[:40])
                    user_id = user_id.split(b'\x00')[0].decode(errors='ignore')
                    timestamp = self.__decode_time(timestamp)
                    attendance = Attendance(user_id, timestamp, status, punch, uid)
                    attendances.append(attendance)
                    attendance_data = attendance_data[40:]

        return attendances

    def clear_attendance(self):
        """
        clear all attendance record
        """
        command = const.CMD_CLEAR_ATTLOG
        cmd_response = self.__send_command(command)
        if cmd_response.get('status'):
            return True
        raise ZKErrorResponse("Can't clear attendance")

    def get_users(self):
        """
        get all users
        """
        self.read_sizes()
        if self.users == 0:
            self.next_uid = 1
            self.next_user_id = '1'
            return []

        users = []
        max_uid = 0
        userdata, size = self.read_with_buffer(const.CMD_USERTEMP_RRQ, const.FCT_USER)

        if size <= 4:
            return []

        total_size = unpack('I', userdata[:4])[0]
        self.user_packet_size = total_size / self.users
        userdata = userdata[4:]

        if self.user_packet_size == 28:
            while len(userdata) >= 28:
                uid, privilege, password, name, card, group_id, timezone, user_id = unpack('<HB5s8sIxBhI', userdata.ljust(28, b'\x00')[:28])
                if uid > max_uid:
                    max_uid = uid
                password = password.split(b'\x00')[0].decode(self.encoding, errors='ignore')
                name = name.split(b'\x00')[0].decode(self.encoding, errors='ignore').strip()
                group_id = str(group_id)
                user_id = str(user_id)
                if not name:
                    name = 'NN-%s' % user_id
                user = User(uid, name, privilege, password, group_id, user_id, card)
                users.append(user)
                userdata = userdata[28:]
        else:
            while len(userdata) >= 72:
                uid, privilege, password, name, card, group_id, user_id = unpack('<HB8s24sIx7sx24s', userdata.ljust(72, b'\x00')[:72])
                password = password.split(b'\x00')[0].decode(self.encoding, errors='ignore')
                name = name.split(b'\x00')[0].decode(self.encoding, errors='ignore').strip()
                group_id = group_id.split(b'\x00')[0].decode(self.encoding, errors='ignore').strip()
                user_id = user_id.split(b'\x00')[0].decode(self.encoding, errors='ignore')
                if uid > max_uid:
                    max_uid = uid
                if not name:
                    name = 'NN-%s' % user_id
                user = User(uid, name, privilege, password, group_id, user_id, card)
                users.append(user)
                userdata = userdata[72:]

        max_uid += 1
        self.next_uid = max_uid
        self.next_user_id = str(max_uid)

        while True:
            if any((u for u in users if u.user_id == self.next_user_id)):
                max_uid += 1
                self.next_user_id = str(max_uid)
            else:
                break

        return users

    def live_capture(self, new_timeout=2) -> Generator[Optional[Attendance], None, None]:
        """
        try live capture of events
        """
        was_enabled = self.is_enabled
        users = self.get_users()
        self.cancel_capture()
        self.verify_user()

        if not self.is_enabled:
            self.enable_device()

        logger.info('Starting live capture')
        self.reg_event(const.EF_ATTLOG)
        self.__sock.settimeout(new_timeout)
        self.end_live_capture = False

        while not self.end_live_capture:
            try:
                data_recv = self.__sock.recv(1032)
                self.__ack_ok()

                if self.tcp:
                    size = unpack('<HHI', data_recv[:8])[2]
                    header = unpack('HHHH', data_recv[8:16])
                    data = data_recv[16:]
                else:
                    size = len(data_recv)
                    header = unpack('<4H', data_recv[:8])
                    data = data_recv[8:]

                if not header[0] == const.CMD_REG_EVENT:
                    continue

                if not len(data):
                    continue

                while len(data) >= 12:
                    if len(data) == 12:
                        user_id, status, punch, timehex = unpack('<IBB6s', data)
                        data = data[12:]
                    elif len(data) == 32:
                        user_id, status, punch, timehex = unpack('<24sBB6s', data[:32])
                        data = data[32:]
                    elif len(data) == 36:
                        user_id, status, punch, timehex, _other = unpack('<24sBB6s4s', data[:36])
                        data = data[36:]
                    elif len(data) >= 52:
                        user_id, status, punch, timehex, _other = unpack('<24sBB6s20s', data[:52])
                        data = data[52:]

                    if isinstance(user_id, int):
                        user_id = str(user_id)
                    else:
                        user_id = user_id.split(b'\x00')[0].decode(errors='ignore')

                    timestamp = self.__decode_timehex(timehex)
                    tuser = list(filter(lambda x: x.user_id == user_id, users))

                    if not tuser:
                        uid = int(user_id)
                    else:
                        uid = tuser[0].uid

                    yield Attendance(user_id, timestamp, status, punch, uid)

            except timeout:
                yield None
            except (KeyboardInterrupt, SystemExit):
                break

        self.__sock.settimeout(self.__timeout)
        self.reg_event(0)

        if not was_enabled:
            self.disable_device()

        logger.info('Live capture ended')

    def clear_data(self):
        """
        clear all data
        """
        command = const.CMD_CLEAR_DATA
        command_string = ''
        cmd_response = self.__send_command(command, command_string)
        if cmd_response.get('status'):
            self.next_uid = 1
            return True
        raise ZKErrorResponse("can't clear data")

    def __recieve_chunk(self):
        """ recieve a chunk """
        if self.__response == const.CMD_DATA:
            if self.tcp:
                if len(self.__data) < self.__tcp_length - 8:
                    need = self.__tcp_length - 8 - len(self.__data)
                    more_data = self.__recieve_raw_data(need)
                    return b''.join([self.__data, more_data])
                return self.__data
            return self.__data

        if self.__response == const.CMD_PREPARE_DATA:
            data = []
            size = self.__get_data_size()

            if self.tcp:
                if len(self.__data) >= 8 + size:
                    data_recv = self.__data[8:]
                else:
                    data_recv = self.__data[8:] + self.__sock.recv(size + 32)
                resp, broken_header = self.__recieve_tcp_data(data_recv, size)
                data.append(resp)
                if len(broken_header) < 16:
                    data_recv = broken_header + self.__sock.recv(16)
                else:
                    data_recv = broken_header
                if len(data_recv) < 16:
                    data_recv += self.__sock.recv(16 - len(data_recv))
                if not self.__test_tcp_top(data_recv):
                    return None
                response = unpack('HHHH', data_recv[8:16])[0]
                if response == const.CMD_ACK_OK:
                    return b''.join(data)
                return None

            while True:
                data_recv = self.__sock.recv(1032)
                response = unpack('<4H', data_recv[:8])[0]
                if response == const.CMD_DATA:
                    data.append(data_recv[8:])
                    size -= 1024
                else:
                    if response == const.CMD_ACK_OK:
                        break
            return b''.join(data)

        return None

    def __recieve_raw_data(self, size):
        """ partial data ? """
        data = []
        while size > 0:
            data_recv = self.__sock.recv(size)
            recieved = len(data_recv)
            data.append(data_recv)
            size -= recieved
        return b''.join(data)

    def __recieve_tcp_data(self, data_recv, size):
        """ data_recv, raw tcp packet """
        data = []
        tcp_length = self.__test_tcp_top(data_recv)

        if tcp_length <= 0:
            return (None, b'')

        if tcp_length - 8 < size:
            resp, bh = self.__recieve_tcp_data(data_recv, tcp_length - 8)
            data.append(resp)
            size -= len(resp)
            data_recv = bh + self.__sock.recv(size + 16)
            resp, bh = self.__recieve_tcp_data(data_recv, size)
            data.append(resp)
            return (b''.join(data), bh)

        recieved = len(data_recv)
        response = unpack('HHHH', data_recv[8:16])[0]

        if recieved >= size + 32:
            if response == const.CMD_DATA:
                resp = data_recv[16:size + 16]
                return (resp, data_recv[size + 16:])
            return (None, b'')

        data.append(data_recv[16:size + 16])
        size -= recieved - 16
        broken_header = b''

        if size < 0:
            broken_header = data_recv[size:]

        if size > 0:
            data_recv = self.__recieve_raw_data(size)
            data.append(data_recv)

        return (b''.join(data), broken_header)

    def __read_chunk(self, start, size):
        """
        read a chunk from buffer
        """
        for _retries in range(3):
            command = 1504
            command_string = pack('<ii', start, size)
            if self.tcp:
                response_size = size + 32
            else:
                response_size = 1032
            cmd_response = self.__send_command(command, command_string, response_size)
            data = self.__recieve_chunk()
            if data is not None:
                return data
        else:
            raise ZKErrorResponse("can't read chunk %i:[%i]" % (start, size))

    def read_with_buffer(self, command, fct=0, ext=0):
        """
        Test read info with buffered command
        """
        if self.tcp:
            MAX_CHUNK = 65472
        else:
            MAX_CHUNK = 16384

        command_string = pack('<bhii', 1, command, fct, ext)
        response_size = 1024
        data = []
        start = 0
        cmd_response = self.__send_command(1503, command_string, response_size)

        if not cmd_response.get('status'):
            raise ZKErrorResponse('RWB Not supported')

        if cmd_response['code'] == const.CMD_DATA:
            if self.tcp:
                if len(self.__data) < self.__tcp_length - 8:
                    need = self.__tcp_length - 8 - len(self.__data)
                    more_data = self.__recieve_raw_data(need)
                    return (b''.join([self.__data, more_data]), len(self.__data) + len(more_data))
                size = len(self.__data)
                return (self.__data, size)
            size = len(self.__data)
            return (self.__data, size)

        size = unpack('I', self.__data[1:5])[0]
        remain = size % MAX_CHUNK
        packets = (size - remain) // MAX_CHUNK

        for _wlk in range(packets):
            data.append(self.__read_chunk(start, MAX_CHUNK))
            start += MAX_CHUNK

        if remain:
            data.append(self.__read_chunk(start, remain))
            start += remain

        self.free_data()
        return (b''.join(data), start)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()