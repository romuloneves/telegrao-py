from api import send_message, edit_message_text
from reborn import log
import threading
import time
import sched


VOTING_DURATION_IN_SECS = 180
MARKUP = "{%22inline_keyboard%22:[[{%22text%22:%22EUVO%22,%22callback_data%22:%221%22},%20{%22text%22:%22nemvo%22,%22callback_data%22:%220%22}]]}"
# hack horrível, mas por enquanto funciona


def started(is_enabled=None):
    if is_enabled is not None:
        started.state = is_enabled

    return started.state


class Voting:
    def __init__(self):
        self.reset()

    def number_going(self):
        return len(self.going)

    def number_not_going(self):
        return len(self.notgoing)

    def going_as_str(self):
        members = ""

        if self.number_going() == 0:
            members = "ninggme"
        else:
            for user in self.going:
                members += "*" + user + "*\n"

        return members

    def not_going_as_str(self):
        members = ""

        if self.number_not_going() == 0:
            members = "ninggme"
        else:
            for user in self.notgoing:
                members += "*" + user + "*\n"

        return members

    def generate_str(self):
        str = ""
        str += "VAMO JOGA " + self.gamename.upper() + " CARAI VCSC TNE 3 MISNUTOS\n\n"
        str += "QUEM VAI::::\n"
        str += self.going_as_str() + "\n\n"
        str += "QUEM N VAI::::\n"
        str += self.not_going_as_str()

        return str

    def reset(self):
        self.active = False
        self.gamename = ""
        self.msg_id = 0
        self.chatid = 0
        self.maxslots = 0
        self.going = []
        self.notgoing = []


voting = Voting()
started(False)


def finishVoting(reason=0):
    # reason 0: tempo expirado
    # reason 1: todos confirmados
    if started():
        log("Terminando votação...")

        if reason == 0:
            send_message(voting.chatid, "acabando com esta merda de votacao......")
            edit_message_text(voting.chatid, voting.msg_id, "cabo esta merda")
        elif reason == 1:
            send_message(voting.chatid, "AE CARAI AGR A VAO JOGA TEU" + voting.gamename + ".....")
            edit_message_text(voting.chatid, voting.msg_id, "cabo a votasao i todos jogo felis para senpre.....\n\nQUEM VAI::::\n" + voting.going_as_str())

        started(False)
        voting.reset()


def startVoting():
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(VOTING_DURATION_IN_SECS, 0, finishVoting)
    scheduler.run()


def on_msg_received(msg, matches):
    if started():
        send_message(msg["chat"]["id"], "ja ten una votasoao aocntecnedo agro ak porra")
    else:
        log("Iniciando votação pra jogar " + matches.group(1) + "...")
        started(True)
        voting.gamename = matches.group(1)
        voting.maxslots = int(matches.group(2))

        voting.active = True
        voting.chatid = msg["chat"]["id"]
        voting.going.append(msg["from"]["first_name"])

        sent_msg = send_message(msg["chat"]["id"], voting.generate_str(), reply_markup=MARKUP)
        voting.msg_id = sent_msg["result"]["message_id"]

        multimanager = threading.Thread(target=startVoting)
        multimanager.start()


def on_callback_query(msg):
    if started() and msg["message"]["message_id"] == voting.msg_id:
        user = msg["from"]["first_name"]

        if user in voting.going: # se já está na votação...
            if msg["data"] == '1': # se estiver confirmando que vai de novo
                log(user + " tentando votar mais de uma vez")
            elif msg["data"] == '0': # se estiver pedindo pra ser retirado da lista...
                log("Removendo " + user + " da votação...")
                voting.going.remove(user)
                voting.notgoing.append(user)
        else:
            if msg["data"] == '1':
                log("Adicionando " + user + " à votação...")
                voting.going.append(user)

                if user in voting.notgoing:
                    voting.notgoing.remove(user)

                if voting.number_going() == voting.maxslots:
                    finishVoting(1)

            elif msg["data"] == '0':
                log("Marcando que " + user + " não vai")
                voting.notgoing.append(user)

                if user in voting.going:
                    voting.going.remove(user)

        edit_message_text(voting.chatid, voting.msg_id, voting.generate_str(), reply_markup=MARKUP)
