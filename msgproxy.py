import marshal

class MsgProxy(object):
    def __init__(self, EOM='~~'):
        self.msg_q = []
        self.EOM = EOM

    def clear(self):
        self.msg_q = []
        
    def recv(self, sock):
        try:
            if not self.msg_q:  # msg_q is empty so recv data
                new_msgs = sock.recv(1024).split(self.EOM)
                # ensure we don't read a partial message
                while len(new_msgs[-1]) > 0:
                    msg_tail = sock.recv(1024).split(self.EOM)
                    new_msgs[-1] += msg_tail[0]
                    new_msgs.extend(msg_tail[1:])
                # update the msg_q
                new_msgs.pop()    
                new_msgs.reverse()
                self.msg_q = new_msgs + self.msg_q
            # return next complete message
            return marshal.loads(self.msg_q.pop())
        except BaseException as e:
            print e.__class__.__name__, e.args
            return ''

    def send(self, sock, obj):
        try:
            msg = marshal.dumps(obj)
            if self.EOM in msg:
                raise ValueError('End-Of-Message token "%s" found in message body' % self.EOM)
            sock.send(msg + self.EOM)
            return True
        except BaseException as e:
            print e.__class__.__name__, e.args
            return False
