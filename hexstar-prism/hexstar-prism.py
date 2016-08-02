#!/usr/bin/env python3

# ISC License
# 
# © 2016 Mattias Andrée <maandree@kth.se>
# 
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


import sys, os

i = 0
argv0 = sys.argv[i]
i += 1
randomise = False
equal = 0
while i < len(sys.argv):
    arg = sys.argv[i]
    i += 1
    if arg == '--':
        break
    if arg[:1] == '-':
        for c in arg[1:]:
            if c == 'R':
                randomise = True
            elif c == 'e':
                equal |= 1
            elif c == 'n':
                equal |= 2
            else:
                print('%s: Invalid option: -%s' % (argv0, c), file = sys.stderr)
                sys.exit(1)
    else:
        i -= 1
        break

layers = sys.argv[i:] if len(sys.argv) > i else None
if ((layers is None) != randomise) or (equal == 3):
    print('%s: Invalid command line' % argv0, file = sys.stderr)
    sys.exit(1)
equal = (None, True, False)[equal]


class State:
    def __init__(self, *layers, equal = None):
        state = layers[0] if len(layers) == 1 and isinstance(layers[0], State) else None
        self.equal = equal
        if state is None:
            self.moves = ''
        else:
            layers = state.layers
            self.moves = state.moves
            if self.equal is None:
                self.equal = state.equal
        self.layers = list(layers)
        for i in range(len(layers)):
            self.layers[i] = list(self.layers[i])

    def __permute(self, c):
        a = (c + 1) % 6
        z = (c + 5) % 6
        Ln = len(self.layers)
        for L in range(Ln // 2):
            l = Ln - 1 - L
            self[L][c], self[l][c] = self[l][c], self[L][c]
            self[L][a], self[l][z] = self[l][z], self[L][a]
            self[L][z], self[l][a] = self[l][a], self[L][z]
        if Ln % 2 == 1:
            L = Ln // 2
            self[L][a], self[L][z] = self[L][z], self[L][a]

    def __getitem__(self, i):
        return self.layers[i]

    def permute(self, C, times = 1):
        if not isinstance(C, list):
            C = [C]
        for c in C:
            strc = ('(%i)' % c) if isinstance(c, int) else c
            for t in range(times):
                if isinstance(c, int):
                    L = self.layers[c]
                    L[:] = [L[5]] + L[0:5]
                    continue
                elif c == '↗':
                    self.__permute(0)
                elif c == '→':
                    self.__permute(1)
                elif c == '↘':
                    self.__permute(2)
                elif c == '↙':
                    self.__permute(3)
                elif c == '←':
                    self.__permute(4)
                elif c == '↖':
                    self.__permute(5)
                elif c == '[⤸]':
                    for L in self.layers:
                        L[:] = [L[5]] + L[0:5]
                elif c == '[←]' or c == '[→]':
                    strc = '[→]'
                    self.__permute(1)
                    self.__permute(4)
                elif c == '[↗]' or c == '[↙]':
                    strc = '[↗]'
                    self.__permute(0)
                    self.__permute(3)
                elif c == '[↘]' or c == '[↖]':
                    strc = '[↘]'
                    self.__permute(2)
                    self.__permute(5)
                else:
                    os.abort()
                if self.equal is not None:
                    self.equal = not self.equal
            self.moves += strc * times

    def __eq__(self, o):
        return self.refstr() == o.refstr()

    def __hash__(self):
        return hash(self.refstr())

    def refstr(self):
        best_i = 0
        best = ''.join(self[0])
        for i in range(1, 6):
            cand = ''.join((self[0][i:] + self[0])[:6])
            if cand < best:
                best = cand
                best_i = i
        return ''.join(''.join((L[best_i:] + L)[:6]) for L in self.layers)

    def is_solved(self, fully = True):
        solved = [False] * len(self.layers)
        solved[0] = True
        if not fully:
            for L in range(1, len(self.layers) - 1):
                solved[L] = True
        for i in range(6):
            ref = ''.join((self[0][i:] + self[0])[:6])
            for L in range(1, len(self.layers)):
                if not solved[L]:
                    solved[L] = ''.join(self[L]) == ref
        return all(solved)

    def randomise(self, moves = 100, track = False):
        import random
        old_moves = self.moves
        for i in range(moves):
            if random.randint(0, 1) == 0:
                self.__permute(random.randint(0, 5))
            else:
                self.permute(random.randint(0, len(self.layers) - 1), random.randint(1, 5))
        if not track:
            self.moves = old_moves

    def is_valid(self):
        if any(len(L) != 6 for L in self.layers):
            return False
        for a in range((len(self.layers) + 1) // 2):
            b = len(self.layers) - 1 - a
            colours = {}
            for i in range(6):
                for L in (a, b):
                    colour = self[L][i]
                    if colour not in colours:
                        colours[colour] = 1
                    else:
                        colours[colour] += 1
            if len(colours) != 6:
                return False
            if any(colours[colour] != 2 for colour in colours):
                return False
        return True

    def __str__(self):
        #return ' '.join(''.join(x) for x in zip(*(self.layers)))
        return ' '.join(''.join(x) for x in self.layers)


def swap_h(A, left):
    if isinstance(A, int):
        A = [A]
    B = [len(state.layers) - 1 - x for x in A]
    r1 = ('↗', '→', '↘', '↙', '←', '↖')[left % 6]
    r2 = ('↗', '→', '↘', '↙', '←', '↖')[(left + 4) % 6]
    if any(b in A for b in B):
        os.abort()
    for b in B:
        state.permute(b, 2)
    state.permute(r1)
    for b in B:
        state.permute(b)
    state.permute(r1)
    for b in B:
        state.permute(b)
    state.permute(r2)
    for a in A:
        state.permute(a)
    state.permute(r2)
    for b in B:
        state.permute(b, 3)



if randomise:
    layers = ['wbrygo'] * 5
state = State(*layers, equal = equal)
if randomise:
    state.randomise()
if not state.is_valid():
    print('%s: Invalid initial state' % argv0, file = sys.stderr)
    sys.exit(1)



# Stage 1:  Fix ↗

colour = state[0][0]
for a in range(len(state.layers)):
    b = len(state.layers) - 1 - a
    if a == b:
        continue
    if colour not in state[a]:
        for i in range(1, 6):
            if state[b][i] == colour:
                state.permute((None, '↘', '↘', '↙', '←', '←')[i])
                break
    while state[a][0] != colour:
        state.permute(a)
    state.moves += ' '
state.moves += '\n'


# Stage 2:  Fix →

colour = {}
for L in range(len(state.layers)):
    if L == len(state.layers) - 1 - L:
        continue
    if state[L][1] not in colour:
        colour[state[L][1]] = 1
    else:
        colour[state[L][1]] += 1
colour = max(colour, key = lambda x : colour[x]) if len(colour) > 0 else None
for a in range(len(state.layers)):
    b = len(state.layers) - 1 - a
    if a == b or state[a][1] == colour:
        continue
    if colour not in state[a]:
        state.permute('←' if state[b][5] == colour else '↙')
    if state[a][2] == colour:
        state.permute('↙')
        state.permute(a)
        state.permute('↙')
        state.permute(a, 5)
    elif state[a][3] == colour:
        state.permute(a, 5)
        state.permute('↙')
        state.permute(a, 2)
        state.permute('↙')
        state.permute(a, 5)
    elif state[a][4] == colour:
        state.permute('←')
        state.permute(a)
        state.permute('↙')
        state.permute(a, 5)
    elif state[a][5] == colour:
        state.permute('←')
        state.permute(a)
        state.permute('↙')
        state.permute(a, 5)
        state.permute('↙')
        state.permute(a)
        state.permute('↙')
        state.permute(a, 5)
    else:
        os.abort()
    state.moves += ' '
state.moves += '\n'


# Stage 3:  Fix ↘

colour = {}
for L in range(len(state.layers)):
    if L == len(state.layers) - 1 - L:
        continue
    if state[L][2] not in colour:
        colour[state[L][2]] = 1
    else:
        colour[state[L][2]] += 1
colour = max(colour, key = lambda x : colour[x]) if len(colour) > 0 else None
for a in range(len(state.layers)):
    b = len(state.layers) - 1 - a
    if a == b or state[a][2] == colour:
        continue
    if colour not in state[a]:
        state.permute('←')
    if state[a][5] == colour:
        state.permute('←')
        state.permute(a)
        state.permute('←')
        state.permute(a, 5)
    if state[a][4] == colour:
        state.permute('←')
        state.permute(a)
        state.permute('←')
        state.permute(a, 5)
    state.permute('←')
    state.permute(a)
    state.permute('←')
    state.permute(a, 5)
    state.moves += ' '
state.moves += '\n'


# Stage 4:  Fix ↙

colour = {}
for L in range(len(state.layers)):
    if L == len(state.layers) - 1 - L:
        continue
    if state[L][3] not in colour:
        colour[state[L][3]] = 1
    else:
        colour[state[L][3]] += 1
colour = max(colour, key = lambda x : colour[x]) if len(colour) > 0 else None
for a in range(len(state.layers)):
    b = len(state.layers) - 1 - a
    if a == b or state[a][3] == colour:
        continue
    if colour not in state[a]:
        if state[b][5] == colour:
            swap_h(b, 0)
            state.moves += ' '
            state.permute('↖')
            state.moves += ' '
            swap_h(a, 4)
            state.moves += ' '
            state.permute('↖')
            state.moves += ' '
            swap_h(b, 0)
        else:
            state.permute('↘')
            state.permute('←')
            state.permute('↘')
            state.moves += ' '
            swap_h(a, 4)
            state.moves += ' '
            state.permute('↘')
            state.permute('←')
            state.permute('↘')
    else:
        if state[a][4] == colour:
            swap_h(a, 4)
        else:
            swap_h(a, 5)
            swap_h(a, 4)
    state.moves += '\n'


# Stage 5:  Fix ← and ↖

colour = {}
for L in range(len(state.layers)):
    if L == len(state.layers) - 1 - L:
        continue
    if state[L][4] not in colour:
        colour[state[L][4]] = 1
    else:
        colour[state[L][4]] += 1
colour = max(colour, key = lambda x : colour[x]) if len(colour) > 0 else None
for a in range(len(state.layers)):
    b = len(state.layers) - 1 - a
    if a == b or state[a][4] == colour:
        continue
    if state[a][5] == colour:
        swap_h(a, 5)
    else:
        state.permute('↗')
        state.permute('←')
        state.permute('↗')
        state.moves += ' '
        swap_h(b, 5)
        state.moves += ' '
        state.permute('↗')
        state.permute('←')
        state.permute('↗')
    state.moves += '\n'


# Stage 6:  Fix centre layer

for a in range(len(state.layers)):
    b = len(state.layers) - 1 - a
    if state[a] != state[b]:
        os.abort()
a = len(state.layers) // 2
b = len(state.layers) - 1 - a
A = list(range(a))
B = [len(state.layers) - 1 - x for x in range(a)]
if a == b:
    while state[a][0] != state[0][0]:
        state.permute(a)
    state.moves += '\n'

    if state[a][1] == state[0][1]:
        pass
    elif state[a][3] == state[0][1]:
        for i in range(3):
            state.permute(A, 3)
            state.permute('↘')
    elif state[a][5] == state[0][1]:
        for i in range(3):
            state.permute(A, 3)
            state.permute('↗')
    elif state[0][2] == state[a][1] or state[0][4] == state[a][1]:
        if state[0][4] == state[a][1]:
            state.permute('↙')
            state.moves += ' '
        swap_h(A, 2)
        state.moves += ' '
        swap_h(B, 2)
    else:
        if state[0][5] == state[a][1]:
            state.permute('←')
            state.moves += ' '
        for i in (3, 2):
            swap_h(A, i)
            state.moves += ' '
            swap_h(B, i)
            state.moves += ' '
    state.moves += '\n'

    if state[a][2] == state[0][2]:
        pass
    elif state[a][4] == state[0][2]:
        for i in range(3):
            state.permute(A, 3)
            state.permute('↙')
    elif state[0][4] == state[a][2]:
        for i in (4, 3):
            swap_h(A, i)
            state.moves += ' '
            swap_h(B, i)
            state.moves += ' '
    else:
        if state[0][5] == state[a][2]:
            state.permute('←')
            state.moves += ' '
        swap_h(A, 3)
        state.moves += ' '
        swap_h(B, 3)
    state.moves += '\n'

    if state[a][3] == state[0][3]:
        pass
    elif state[a][5] == state[0][3]:
        for i in range(3):
            state.permute(A, 3)
            state.permute('←')
    elif state[0][4] == state[a][3]:
        swap_h(A, 4)
        state.moves += ' '
        swap_h(B, 4)
    else:
        for i in (5, 4):
            swap_h(A, i)
            state.moves += ' '
            swap_h(B, i)
            state.moves += ' '
    state.moves += '\n'

    if state[a][4] == state[0][4]:
        pass
    else:
        swap_h(A, 5)
        state.moves += ' '
        swap_h(B, 5)
    state.moves += '\n'


# Stage 7:  Remove unnecessary final flips and fix inner circle

moves = state.moves
while len(moves) > 0:
    if moves[-1] in ('↗', '→', '↘', '↙', '←', '↖'):
        state.permute(moves[-1])
    elif moves[-1] not in (' ', '\n'):
        break
    moves = moves[:-1]
state.moves = moves
if state.equal is not None and not state.equal:
    move = '→'
    for c in state.moves:
        if c in ('↗', '→', '↘', '↙', '←', '↖'):
            move = c
    state.permute(move)



# Print solution

moves = state.moves
old_moves = ''
while old_moves != moves:
    old_moves = moves
    while len(moves) > 0 and moves[0] in (' ', '\n'):
        moves = moves[1:]
    while len(moves) > 0 and moves[-1] in (' ', '\n'):
        moves = moves[:-1]
    while '  ' in moves:
        moves = moves.replace('  ', ' ')
    while ' \n' in moves:
        moves = moves.replace(' \n', '\n')
    while '\n ' in moves:
        moves = moves.replace('\n ', '\n')
    while '\n\n' in moves:
        moves = moves.replace('\n\n', '\n')
    for s in ('\n', ' ', ''):
        for c in ('↗', '→', '↘', '↙', '←', '↖'):
            moves = moves.replace(c + s + c, s)
            moves = moves.replace('[' + c + ']' + s + '[' + c + ']', s)
for i in range(len(state.layers)):
    s = '(%i)' % i
    z = str((i + 1))
    for j in range(10):
        z = z.replace(str(j), '₀₁₂₃₄₅₆₇₈₉'[j])
    moves = moves.replace(s * 6, '')
    moves = moves.replace(s * 5, '⤹%s¹' % z)
    moves = moves.replace(s * 4, '⤹%s²' % z)
    moves = moves.replace(s * 3, '⤸%s³' % z)
    moves = moves.replace(s * 2, '⤸%s²' % z)
    moves = moves.replace(s * 1, '⤸%s¹' % z)
moves = moves.replace('[⤸]' * 5, '[⤹¹]')
moves = moves.replace('[⤸]' * 4, '[⤹²]')
moves = moves.replace('[⤸]' * 3, '[⤸³]')
moves = moves.replace('[⤸]' * 2, '[⤸²]')
moves = moves.replace('[⤸]' * 1, '[⤸¹]')
print(moves)
if not state.is_solved():
    print('%s: Failed to solve' % argv0, file = sys.stderr)
    sys.exit(2)
