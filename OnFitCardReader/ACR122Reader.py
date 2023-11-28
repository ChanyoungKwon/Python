# -*- coding: utf-8 -*-

import os
import sys
import time
import psutil
import socket
import logging
from datetime import datetime
from distutils import dir_util
from configparser import ConfigParser
from logging import StreamHandler
from logging.handlers import TimedRotatingFileHandler
from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard import Exceptions as CardExceptions
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver

class ACR122Reader():
    def __init__(self, cfg_file='setting.cfg'):
        # ACS ACR122U NFC Reader
        self.COMMAND = [0xFF, 0xCA, 0x00, 0x00, 0x00]  # Get UID
        self.cardsvc = None

        # configuration
        home_dir = ''
        if getattr(sys, 'frozen', False):
            # The application is frozen
            home_dir = os.path.dirname(sys.executable)
        else:
            # The application is not frozen
            # Change this bit to match where you store your data files:
            home_dir = os.path.dirname(os.path.abspath(__file__))

        self.CFG_FILE = os.path.join(home_dir, cfg_file)
        self.LOG_DIR = os.path.join(home_dir, 'log')
        self.LOG_FILE = os.path.join(self.LOG_DIR, 'OnFitCardReader.log')
        config = ConfigParser()
        config.read(self.CFG_FILE)
        self.UDP_IPADDR = config.get('ONFIT_CARD_READER', 'UDP_IPADDR')
        self.UDP_PORT = config.getint('ONFIT_CARD_READER', 'UDP_PORT')
        self.LOG_LEVEL = config.getint('ONFIT_CARD_READER', 'LOG_LEVEL')
        #self.PC_ID = config.get('ONFIT_CARD_READER', 'PC_ID')

        # log setting
        dir_util.mkpath(self.LOG_DIR)
        self.log_file_handler = TimedRotatingFileHandler(filename=self.LOG_FILE,
                                                    when='D', interval=1, backupCount=7)
        self.log_console_handler = StreamHandler(sys.stdout)
        self.log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] : %(message)s')

        self.log_file_handler.setFormatter(self.log_formatter)
        self.log_console_handler.setFormatter(self.log_formatter)

        self.logger = logging.getLogger('OnFit')
        self.logger.addHandler(self.log_file_handler)
        self.logger.addHandler(self.log_console_handler)
        self.logger.setLevel(self.LOG_LEVEL)

        # udp setting
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # logging test
        # self.logger.debug('debug message')
        # self.logger.info('info message')
        # self.logger.warn('warn message')
        # self.logger.error('error message')
        # self.logger.critical('critical message')

        # clear existing process
        self.kill_previous_proc()
        return

    def kill_previous_proc(self):
        "Return a list of processes matching 'name'."
        # assert name, name
        for p in psutil.process_iter():
            try:
                if len(p.cmdline()) == 1:
                    if p.cmdline()[0].find('OnFitCardReader') >= 0:
                        if p.pid != os.getpid():
                            p.kill()
                            self.logger.warning("Previous driver process[{PID}] killed!!!".format(PID=p.pid))
                if len(p.cmdline()) == 2:
                    if p.cmdline()[0].find('python') >= 0 and p.cmdline()[1].find('OnFitCardReader') >= 0:
                        if p.pid != os.getpid():
                            p.kill()
                            self.logger.warning("Previous driver process[{PID}] killed!!!".format(PID=p.pid))
            except (psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except psutil.NoSuchProcess:
                continue

    def waitCardTouch(self, timeout=10):
        time.sleep(1)  # cool-down time
        cardtype = AnyCardType()
        cardreq = CardRequest(timeout=timeout, cardType=cardtype)
        self.logger.info("Waiting for Card Touch...")
        self.cardsvc = cardreq.waitforcard()
        #observer = ConsoleCardConnectionObserver()
        #self.cardsvc.connection.addObserver(observer)
        self.cardsvc.connection.connect()
        resp = self.cardsvc.connection.transmit(self.COMMAND)
        self.cardsvc.connection.disconnect()
        self.cardsvc = None
        return resp

    def parseNFCUID(self, data):
        if isinstance(data, tuple) and len(data) == 3:
            if data[1] != 144:
                return ''
            else:
                if isinstance(data[0], list):
                    uid = ''
                    for val in data[0]:
                        uid += format(val, '#04x')[2:]
                    return uid.upper()
        else:
            return ''

    def send_udp_message(self, message):
        self.udp_socket.sendto(message.encode('utf-8'), (self.UDP_IPADDR, self.UDP_PORT))
        self.logger.info("Message[{MESSAGE}] to UDP[{PORT}]".format(MESSAGE=message, PORT=self.UDP_PORT))
        self.log_file_handler.flush()

    def run(self):
        self.logger.info("Start OnFit Card Reader!")
        while True:
            try:
                res = self.waitCardTouch()
                uid = self.parseNFCUID(res)
                if len(uid) == 8:
                    message = "OnFitUIDCard[{TOUCHTIME}]:[{OnFitUID}]"
                    self.send_udp_message(message.format(TOUCHTIME=datetime.now().strftime("%H%M%S"), OnFitUID=uid))
            except CardExceptions.CardRequestTimeoutException as TOE:
                self.logger.info("Waiting for Card Touch...")
                continue
            except CardExceptions.NoCardException as NCE:
                self.logger.info("Too short Card Touch...")
                continue
            except CardExceptions.ListReadersException as LRE:
                self.logger.info("Cannot detect Card Reader...")
                if self.cardsvc:
                    self.cardsvc.connection.disconnect()
                    self.cardsvc = None
                continue
            except UnicodeDecodeError:
                self.logger.exception("Internal Error...")
                continue

