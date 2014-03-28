__author__ = 'dc'
import uuid
import random
import tornado.web
import sae.kvdb

kv = sae.kvdb.KVClient()

op_set = ('up', 'down', 'left', 'right')
status_set = ('start', 'running', 'finish')

main_info = '''<html>

<head>
<title>2048judge</title>
</head>

<body>
<p>welcome to 2048 ai judge</p>

<p>first use</p>

    <samp>GET /judge/</samp>

<p>to get table and uid. then use</p>
    <samp>GET /judge/?uid=XXXXXXXX&op=left</samp>
<p>to do op in the table, it will return your op, the new table and the status.</p>
<p>op should in ('up', 'down', 'left', 'right')</p>
<p>the return status will in ('start', 'running','finish')</p>
<p>when you receive 'finish', it means you got 2048.</p>
</body>

</html>
'''


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(main_info)


class JudgeHandler(tornado.web.RequestHandler):
    def get(self):
        op = self.get_argument('op', None)
        uid = str(self.get_argument('uid', None))
        if uid and op:
            # add op
            assert op in op_set, 'op error'
            log = kv.get(uid)
            assert log, 'uid error'
            assert log[-1]['status'] != 'finish', 'game finished!'
            table = log[-1]['table']
            push_line(table, op)
            sum_line(table, op)
            push_line(table, op)
            add_number(table)
            status = check_status(table)
            log.append({'table': table, 'op': op, 'status': status})
            kv.set(uid, log)
            self.write(log[-1])
            pretty_print(table)
        else:
            # first round
            uid = uuid.uuid1().hex
            kv.set(uid, [{'table': gen_table(), 'op': None, 'status': 'start'}])
            self.write({'uid': uid, 'log': kv.get(uid)})


def gen_table():
    table = [[0 for j in range(4)] for i in range(4)]
    add_number(table, 2)
    return table


def op_table(table, op):
    assert op in op_set
    if op == 'up':
        pass
    add_number(table)
    return table


def push_line(table, op):
    for i in range(4):
        if op == 'up':
            line = [table[j][i] for j in range(4)]
            for j in range(line.count(0)): line.remove(0)
            for j in range(4 - len(line)): line.append(0)
            for j in range(4): table[j][i] = line[j]
        elif op == 'down':
            line = [table[j][i] for j in range(4)]
            for j in range(line.count(0)): line.remove(0)
            for j in range(4 - len(line)): line.insert(0, 0)
            for j in range(4): table[j][i] = line[j]
        elif op == 'left':
            line = [table[i][j] for j in range(4)]
            for j in range(line.count(0)): line.remove(0)
            for j in range(4 - len(line)): line.append(0)
            for j in range(4): table[i][j] = line[j]
        elif op == 'right':
            line = [table[i][j] for j in range(4)]
            for j in range(line.count(0)): line.remove(0)
            for j in range(4 - len(line)): line.insert(0, 0)
            for j in range(4): table[i][j] = line[j]


def sum_line(table, op):
    for i in range(4):
        if op == 'up':
            for j in range(3):
                if table[j][i] == table[j + 1][i]:
                    table[j][i] *= 2
                    table[j + 1][i] = 0
        elif op == 'down':
            for j in range(3, 0, -1):
                if table[j][i] == table[j - 1][i]:
                    table[j][i] *= 2
                    table[j - 1][i] = 0
        elif op == 'left':
            for j in range(3):
                if table[i][j] == table[i][j + 1]:
                    table[i][j] *= 2
                    table[i][j + 1] = 0
        elif op == 'right':
            for j in range(3, 0, -1):
                if table[i][j] == table[i][j - 1]:
                    table[i][j] *= 2
                    table[i][j - 1] = 0


def check_status(table):
    for i in range(4):
        for j in range(4):
            if table[i][j] == 2048:
                return 'finish'
    return 'running'


def add_number(table, num=1):
    select = []
    # find empty
    for i in range(4):
        for j in range(4):
            if table[i][j] == 0:
                select.append([i, j])
        # choice pos
    select = random.sample(select, num)
    # set to 2
    for i, j in select:
        # table[i][j] = random.choice([2, 4])
        table[i][j] = 2


def pretty_print(table):
    for i in range(4):
        for j in range(4):
            print table[i][j],
        print
