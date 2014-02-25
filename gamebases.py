import threading
from Queue import Queue
from msgproxy import MsgProxy

# Generic mixin for a queue-based worker thread
# Assumes sub-classes have do_work and cleanup methods
class WorkerThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.input_queue = Queue()
    def send(self, item):
        self.input_queue.put(item)
    def close(self):
        self.input_queue.put(None)
    def run(self):
        while True:
            item = self.input_queue.get()
            if item is None: break
            self.do_work(item)
        print 'thread closing'
        self.cleanup()

# Handle turn taking and communication for a two player game using sockets
class TwoPlayerGame(WorkerThread):
    def __init__(self):
        WorkerThread.__init__(self)
        self.msg = MsgProxy()
        self.players = [None, None]
        self.next_player = 0
        self.game_over = False
        self.winner = None
        self.move_count = 0
    # release resources before exiting
    def cleanup(self):
        for p in self.players:
            if p: p.socket.close()
    # send the same message to all players
    def broadcast(self, data):
        return all((self.msg.send(p.socket, data) for p in self.players))
    # play the game but only after both players have been passed
    def do_work(self, player):
        try:
            if all(self.players): return
            self.players[player.id - 1] = player
            if not all(self.players): return
            game_title = '\n{0} Vs {1}\n'.format(*[p.name for p in self.players])
            assert self.broadcast(game_title + self.format_board())
            while not self.game_over:
                p = self.players[self.next_player]
                while True:
                    move = self.msg.recv(p.socket)
                    print 'received move %s from player %s' % (str(move), p.name)
                    valid, result = self.do_move(move)
                    if valid: break
                    assert self.msg.send(p.socket, result)                
                assert self.broadcast(result)
                self.next_player = 1 - self.next_player        
            print 'GAME OVER: %s Vs %s' % (self.players[0].name, self.players[1].name)
            self.close()
        except BaseException as e:
            print 'ERROR:', game_title, e.__class__.__name__, e.args
            self.close()
