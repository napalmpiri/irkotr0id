#/usr/bin/env python
# -*- coding: Utf8 -*-

import event
import cgi
import boto3
class Plugin:


    def __init__(self, client):
        self.client = client
        try:
            botclient = boto3.client('lex-runtime')
        except:
            pass
        self.botclient=botclient

    @event.privmsg()
    def get_notice(self, e):
        target = e.values['target']
        msg = e.values['msg'][1:]
        baremsg=self.sanitize(self.strip_nick(msg, self.client.nick_name))
        nick = e.values['nick']

        if nick == self.client.nick_name:
            # don't talk to self
            return
            # channel chat, not speaking with me,
        if nick != self.client.nick_name and target != self.client.nick_name and self.client.nick_name not in msg:
            return

        #channel chat, speking with me, answer in channel
        if nick != self.client.nick_name and target!=self.client.nick_name and self.client.nick_name in msg:
            self.get_respose_bot(baremsg, target)
        #private chat, answer in private
        if nick != self.client.nick_name and target==self.client.nick_name:
            self.get_respose_bot(baremsg, target)

    def get_respose_bot(self,input,target):
        try:
            response = self.botclient.post_text(
                    botName='sgrulliver',
                    botAlias='sgrulliverfirst',
                    userId='fiacco',
                    sessionAttributes={
                        'string': 'string'
                    },
                    requestAttributes={
                        'x-amz-lex:accept-content-types': 'PlainText'
                    },
                    inputText=input
                )
        except:
            message ="senti non ho tempo per queste cose dai"
        if response['dialogState'] == 'Fulfilled':
            message =self.sanitize(response['message'])
        elif response['dialogState'] == 'ElicitIntent':
            message = 'Non ho ben capito eh'
        else:
            message ='patate'
        print message
        self.client.priv_msg(target, message)
    
    def help(self, target):
        message = "Sono away"
        self.client.priv_msg(target, message)

    def strip_nick(self, msg, nick):
        nicktwodot=nick+":"
        nicktwospacedot = nick + " :"
        if nicktwodot in msg:
            message = msg.replace(nicktwodot,"",1)
        elif nicktwospacedot in msg:
            message = msg.replace(nicktwospacedot, "", 1)
        elif nick in msg:
            message = msg.replace(nick, "", 1)
        else:
            message=msg
        return message

    def sanitize(self, msg):
        message=msg.encode('utf-8').strip()
        message = cgi.escape(msg)
        return message