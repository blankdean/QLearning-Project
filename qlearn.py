import random
import sys


DEFAULT_STATE = '       | ###  -| # #  +| # ####|       '


class Action:

    def __init__(self, name, dx, dy):
        self.name = name
        self.dx = dx
        self.dy = dy


ACTIONS = [
    Action('UP', 0, -1),
    Action('RIGHT', +1, 0),
    Action('DOWN', 0, +1),
    Action('LEFT', -1, 0)
]


class State:

    def __init__(self, env, x, y):
        self.env = env
        self.x = x
        self.y = y

    def clone(self):
        return State(self.env, self.x, self.y)

    def is_legal(self, action):
        cell = self.env.get(self.x + action.dx, self.y + action.dy)
        return cell is not None and cell in ' +-'
    
    def legal_actions(self, actions):
        legal = []
        for action in actions:
            if self.is_legal(action):
                legal.append(action)
        return legal
    
    def reward(self):
        cell = self.env.get(self.x, self.y)
        if cell is None:
            return None
        elif cell == '+':
            return +10
        elif cell == '-':
            return -10
        else:
            return 0

    def at_end(self):
        return self.reward() != 0

    def execute(self, action):
        self.x += action.dx
        self.y += action.dy
        return self

    def __str__(self):
        tmp = self.env.get(self.x, self.y)
        self.env.put(self.x, self.y, 'A')
        s = ' ' + ('-' * self.env.x_size) + '\n'
        for y in range(self.env.y_size):
            s += '|' + ''.join(self.env.row(y)) + '|\n'
        s += ' ' + ('-' * self.env.x_size)
        self.env.put(self.x, self.y, tmp)
        return s


class Env:

    def __init__(self, string):
        self.grid = [list(line) for line in string.split('|')]
        self.x_size = len(self.grid[0])
        self.y_size = len(self.grid)

    def get(self, x, y):
        if x >= 0 and x < self.x_size and y >= 0 and y < self.y_size:
            return self.grid[y][x]
        else:
            return None

    def put(self, x, y, val):
        if x >= 0 and x < self.x_size and y >= 0 and y < self.y_size:
            self.grid[y][x] = val

    def row(self, y):
        return self.grid[y]

    def random_state(self):
        x = random.randrange(0, self.x_size)
        y = random.randrange(0, self.y_size)
        while self.get(x, y) != ' ':
            x = random.randrange(0, self.x_size)
            y = random.randrange(0, self.y_size)
        return State(self, x, y)


class QTable:

    def __init__(self, env, actions):
        self.q = [[[0 for k in range(7)] for j in range(5)] for i in range(4)]
        self.env = env
        self.actions = actions


    def get_q(self, state, action):
        # return the value of the q table for the given state, action
        if action.name == 'UP':
            return self.q[0][state.y][state.x]
        elif action.name == 'RIGHT':
            return self.q[1][state.y][state.x]
        elif action.name == 'DOWN':
            return self.q[2][state.y][state.x]
        elif action.name == 'LEFT':
            return self.q[3][state.y][state.x]


    def get_q_row(self, state):
        # return the row of q table corresponding to the given state
        qrow = []
        for action in self.q:
            qrow.append(action[state.y][state.x])
        return qrow

    def set_q(self, state, action, val):
        # set the value of the q table for the given state, action

        if action.name == 'UP':
            self.q[0][state.y][state.x] = val
        elif action.name == 'RIGHT':
            self.q[1][state.y][state.x] = val
        elif action.name == 'DOWN':
            self.q[2][state.y][state.x] = val
        elif action.name == 'LEFT':
            self.q[3][state.y][state.x] = val

    def learn_episode(self, alpha=.10, gamma=.90):
        state = self.env.random_state()  # random initial state
        while not state.at_end():
            print(state)
            legalActions = state.legal_actions(self.actions)  # legal actions
            randAction = random.choice(legalActions)  # random legal action
            newState = state.clone()  # executing random legal action
            newState.execute(randAction)
            reward = newState.reward()

            val = (1-alpha)*self.get_q(state, randAction) + alpha*(reward + gamma*(max(self.get_q_row(newState))))
            self.set_q(state, randAction, val)  # updating the q table
            state = newState
        print(state)


    def learn(self, episodes, alpha=.10, gamma=.90):
        # run <episodes> number of episodes for learning with the given alpha and gamma
        for _ in range(episodes + 1):
            self.learn_episode(alpha, gamma)

    def __str__(self):

        directions = ["UP", "RIGHT", "DOWN", "LEFT"]
        str1 = ""
        for i in range(len(self.q)):

            str1 = str1 + directions[i] + "\n"
            for j in self.q[i]:
                for k in j:
                    if (k):
                        str1 = str1 + '{:.2f}'.format(k)
                    else:
                        str1 = str1 + '----'
                    str1 = str1 + " "
                str1 = str1 + "\n"
            str1 = str1 + "\n"

        return str1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        env = Env(sys.argv[2] if len(sys.argv) > 2 else DEFAULT_STATE)
        if cmd == 'learn':
            qt = QTable(env, ACTIONS)
            qt.learn_episode()
            qt.learn(100)
            print(qt)