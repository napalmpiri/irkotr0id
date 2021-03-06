#/usr/bin/env python
# -*- coding: Utf8 -*-

import event
import time
import cgi
import boto3
import random
from random import randint



class Plugin:


    def __init__(self, client):
        self.client = client
        try:
            botclient = boto3.client('lex-runtime')
        except Exception as ex:
            messageex='Exception during initialization %s %s' %(type(ex), ex.args)
            self.client.logger.error(messageex)
        if botclient is not None:
            self.botclient=botclient
            self.client.logger.debug('>> DEBUG: Initialized')

    @event.privmsg()
    def get_notice(self, e):
        """ manages privmsg event
        """
        target = self.sanitize(e.values['target'])
        msg = self.sanitize(e.values['msg'][1:])
        baremsg=self.strip_nick(e.values['msg'][1:], self.client.nick_name)
        nick = self.sanitize(e.values['nick'])

        if nick == self.client.nick_name:
            # don't talk to self
            self.client.logger.debug('will not talk to myself')
            return
            # channel chat, not speaking with me,
        if nick != self.client.nick_name and target != self.client.nick_name and self.client.nick_name not in msg:
            self.client.logger.debug('they are not talking to me I will not answer')
            return

        # channel chat, speaking with me, answer in channel
        if nick != self.client.nick_name and target!=self.client.nick_name and self.client.nick_name in msg:
            self.client.logger.debug('they are  talking to me in channell, in channel  I will answer')
            self.get_respose_bot(baremsg, target)
        # private chat, answer in private
        if nick != self.client.nick_name and target==self.client.nick_name:
            self.client.logger.debug('they are  talking to me in private, in private  I will answer')
            self.get_respose_bot(baremsg, target)


    def targetstrip(self, target):
        """When talking in channel target is the channel names and contains #, which lex bot doesn't like as user-id.
        we strip them. Returns the target name without ##
        """
        trg=target.replace("#", "")
        return trg

    def get_respose_bot(self,input,target):
        """send message to lex bot and get response.
        returns nothing.
        """
        if self.botclient is None:
            # fallback
            message='ZZZzzzzz'
            self.client.priv_msg(target, message)
            return
        botname=self.client.config['saitto']['BOTNAME'][0]
        botalias=self.client.config['saitto']['BOTALIAS'][0]
        trg=self.targetstrip(target)
        if not botname or not botalias or not trg:
            # fallback
            message = 'ZZZzzzzzZZZZ'
            self.client.priv_msg(target, message)
            return
        try:
            response = self.botclient.post_text(
                    botName=botname,
                    botAlias=botalias,
                    userId=trg,
                    sessionAttributes={
                        'string': 'string'
                    },
                    requestAttributes={
                        'x-amz-lex:accept-content-types': 'PlainText'
                    },
                    inputText=input
                )
            if response['dialogState'] == 'Fulfilled':
                message = self.sanitize(response['message'])
            elif response['dialogState'] == 'ElicitIntent':
                message = 'wot'
            else:
                # fallback
                message = 'wuzzap?!'
            self.client.logger.info('>> INFO Sending: ' + message)
        except Exception as ex:
            # fallback
            message = 'no time for this, srsly'
            messageex= 'Exception %s %s' % (type(ex), ex.args)
            self.client.logger.error(messageex)
        self.delay_letters(target, message)

    def strip_nick(self, msg, snick):
        """Strip nicks from message, lex bot doesn't need it in message.
        returns string message after <nick:> or <nick :>.
        """
        message = self.sanitize(msg)
        nick= self.sanitize(snick)
        nicktwodot=nick+":"
        nicktwospacedot = nick + " :"
        if nicktwodot in message:
            message = message.replace(nicktwodot,"",1)
        elif nicktwospacedot in message:
            message = message.replace(nicktwospacedot, "", 1)
        elif nick in message:
            message = message.replace(nick, "", 1)
        return message

    def sanitize(self, msg):
        """Sanitize the input string stripping outer spaces, encoding in utf8, escaping strange characters.
        returns saanitized string.
        """
        # fallback
        message ='uh-uh'
        try:
            message=msg.decode('utf-8','ignore').strip()
            message = cgi.escape(message)
        except Exception as ex:
            messageex='exception %s %s' %(type(ex), ex.args)
            self.client.logger.error(messageex)
        return message

    def delay_letters(self,target, msg):
        """Delay the answer at random, and also simulate typing .
        returns nothing.
        """
        nwords =float(len(msg.split()))
        longerwait=bool(random.getrandbits(1))
        baselinewaitsecs=0
        # 50% of the time I am not looking at the screen right now.
        if longerwait:
            baselinewaitsecs=randint(10, 60);
        if nwords>0:
            # typical word per minute speed
            wps=0.73
            secondstowait=(nwords/wps)+randint(0, 6)
        else:
            secondstowait=randint(0, 9)
        secondstowait=baselinewaitsecs+secondstowait
        self.client.logger.info('waiting for %d seconds before sending \'%s\' to %s' %(secondstowait,msg,target))
        time.sleep(secondstowait)
        self.client.priv_msg(target, msg)
        self.client.logger.debug('just sent \'%s\' to %s after %d seconds' %(msg,target, secondstowait))
