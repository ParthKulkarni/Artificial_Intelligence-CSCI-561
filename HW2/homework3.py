import math
import os

class Solution(object):
	def __init__(self):
		self.params = Solution.getInputParams(self)
	
		if self.params["game_mode"] == "SINGLE":
			best = self.endGame2(self.params["game_board"], self.params["my_color"])
			#print("ENdgame ",best)
			if not best:
				best = self.returnSingleMove(self.params["game_board"], self.params["my_color"])
			#print(best)
		elif self.params["game_mode"] == "GAME":
			print("Game")
			camp_move = self.evacuateMyCamp(self.params["game_board"], self.params["my_color"])

			if camp_move != "DONE":
				best = camp_move
			else:
				print(self.params["my_color"])
				best = self.endGame2(self.params["game_board"], self.params["my_color"])
				if not best:
					best, _ = self.alphabeta(self.params["game_board"], self.params["my_color"], 3)
					print(best)

		writestring = ""
		if best[0] == "J":
			visited = set()
			visited.add(best[1])
			parents = {}
			parents[best[2]] = best[1]
			jumps, parents = self.returnJumpPath(best[1], best[2], self.params["game_board"], visited, self.params["my_color"], [], parents)

			end = best[2]
			start = best[1]
			path = []

			while end != start:
				path.append(("J", parents[end], end))
				end = parents[end]

			path = path[::-1] 

			for jump in path:
				writestring += jump[0] + " " + str(jump[1][1]) + "," + str(jump[1][0]) + " " + str(jump[2][1]) + "," + str(jump[2][0]) + "\n"
		else:
			writestring += best[0] + " " + str(best[1][1]) + "," + str(best[1][0]) + " " + str(best[2][1]) + "," + str(best[2][0])

		outfile = open("output.txt", "w+")
		outfile.write(writestring.rstrip())
		outfile.close()

	def getInputParams(self):
		params = {}

		f = open("endgame3.txt", "r")
		lines = f.readlines()
		f.close()

		game_mode = lines[0]
		params["game_mode"] = game_mode.rstrip()

		my_color = lines[1][0]
		params["my_color"] = my_color

		time_remaining = lines[2]
		params["time_remaining"] = float(time_remaining.rstrip())

		game_board = []
		for i in range(16):
			game_board.append(list(lines[3 + i].rstrip()))
		params["game_board"] = game_board

		return params

	def returnSingleMove(self, game_board, my_color):
		valid_moves = []
		adjacent_moves = []

		if my_color == "W":
			move_x = [0, 1, -1, -1, -1]
			move_y = [-1, -1, 1, 0, -1]
			my_camp = {(15, 15), (15, 14), (15, 13), (15, 12), (15, 11), (14, 15), (14, 14), (14, 13), (14, 12), (14, 11), \
						(13, 15), (13, 14), (13, 13), (13, 12), (12, 15), (12, 14), (12, 13), (11, 15), (11, 14)}
			opp_camp = {(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (2, 0), (2, 1), \
						(2, 2), (2, 3), (3, 0), (3, 1), (3, 2), (4, 0), (4, 1)}
			my_corner = (15,15)
		else:
			move_x = [1, 1, 1, 0, -1]
			move_y = [-1, 0, 1, 1, 1]
			my_camp = {(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (2, 0), (2, 1), \
						(2, 2), (2, 3), (3, 0), (3, 1), (3, 2), (4, 0), (4, 1)}
			opp_camp = {(15, 15), (15, 14), (15, 13), (15, 12), (15, 11), (14, 15), (14, 14), (14, 13), (14, 12), (14, 11), \
						(13, 15), (13, 14), (13, 13), (13, 12), (12, 15), (12, 14), (12, 13), (11, 15), (11, 14)}
			my_corner = (0,0)

		diagonal_move_edge = None
		diagonal_move_jump = None
		camp_move = None
		camp_dist = -1
		for from_x in range(16):
			for from_y in range(16):

				if game_board[from_x][from_y] == my_color:

					for i in range(5):
						to_x = from_x + move_x[i]
						to_y = from_y + move_y[i]

						if self.isSafe(to_x, to_y) and game_board[to_x][to_y] == ".":
							if (from_x, from_y) in opp_camp and (to_x, to_y) not in opp_camp:
								continue
							if (from_x, from_y) in my_camp and (to_x, to_y) not in my_camp:
								return ('E', (from_x, from_y), (to_x, to_y))
							if (from_x, from_y) in my_camp and ((move_x[i] == 1 and move_y[i]==1) or (move_x[i] == -1 and move_y[i]==-1)):
								diagonal_move_edge = ('E', (from_x, from_y), (to_x, to_y))
							if (from_x, from_y) in my_camp and ((move_x[i] == 1 and move_y[i]==-1) or (move_x[i] == -1 and move_y[i]==1)):
								continue
							if (from_x, from_y) in my_camp and math.sqrt(abs(to_x - my_corner[0])**2 + abs(to_y - my_corner[1])**2) > camp_dist:
								camp_move = ('E', (from_x, from_y), (to_x, to_y))
								camp_dist = math.sqrt(abs(to_x - my_corner[0])**2 + abs(to_y - my_corner[1])**2)
							adjacent_moves.append(('E', (from_x, from_y), (to_x, to_y)))	
						elif self.isSafe(to_x, to_y) and game_board[to_x][to_y] != ".":
							jump_x = to_x + move_x[i]
							jump_y = to_y + move_y[i]
							if self.isSafe(jump_x, jump_y) and game_board[jump_x][jump_y] == ".":

								visited = set()
								visited.add((from_x, from_y))

								self.executeMove(game_board, from_x, from_y, jump_x, jump_y, my_color)

								jumps, _ = self.findMoreJumps(jump_x, jump_y, game_board, visited, my_color, [], {})

								self.executeMove(game_board, jump_x, jump_y, from_x, from_y, my_color)

								jumps.append((jump_x, jump_y))
								jumps = list(set(jumps))

								for jump in jumps:
									if (from_x, from_y) in opp_camp and (jump[0], jump[1]) not in opp_camp:
										continue
									if (from_x, from_y) in my_camp and (jump[0], jump[1]) not in my_camp:										
										return ('J', (from_x, from_y), (jump[0], jump[1]))
									if (from_x, from_y) in my_camp and from_x - jump[0] == from_y - jump[1]:
										diagonal_move_jump = ('J', (from_x, from_y), (jump[0], jump[1]))
									if (from_x, from_y) in my_camp and (from_x - jump[0] == -(from_y - jump[1])):
										continue
									if (from_x, from_y) in my_camp and math.sqrt(abs(jump[0] - my_corner[0])**2 + abs(jump[1] - my_corner[1])**2) > camp_dist:
										camp_move = ('J', (from_x, from_y), (jump[0], jump[1]))
										camp_dist = math.sqrt(abs(jump[0] - my_corner[0])**2 + abs(jump[1] - my_corner[1])**2)

									valid_moves.append(('J', (from_x, from_y), (jump[0], jump[1])))
		if diagonal_move_jump:
			return diagonal_move_jump
		if diagonal_move_edge:
			return diagonal_move_edge
		if camp_move:
			return camp_move

		move = (valid_moves + adjacent_moves)[0]
		
		return move

	def evacuateMyCamp(self, game_board, my_color):
		if my_color == "W":
			first_move = "E 13,13 12,12"
			evac_sequence = ['E 12,13 11,12', 'E 13,12 12,11', 'J 14,15 10,11', 'J 11,15 9,11',\
			'J 15,14 11,10', 'J 15,11 11,9', 'J 13,15 11,13', 'J 15,13 13,11', 'J 12,15 10,13',\
			'J 15,12 13,10', 'J 12,14 8,10', 'J 14,12 10,8', 'J 15,15 11,11', 'J 14,14 10,10',\
			'J 11,14 9,12', 'J 14,11 12,9', 'E 13,14 12,14', 'J 12,14 10,12', 'E 14,13 14,12', 'J 14,12 12,10']
		elif my_color == "B":
			first_move = "E 2,2 3,3"
			evac_sequence = ['E 3,2 4,3', 'E 2,3 3,4', 'J 1,0 5,4', 'J 0,1 4,5',\
			'J 4,0 6,4', 'J 0,4 4,6', 'J 2,0 4,2', 'J 0,2 2,4', 'J 0,3 2,5', \
			'J 3,0 5,2', 'J 3,1 7,5', 'J 1,3 5,7', 'J 0,0 4,4', 'J 1,1 5,5', \
			'J 4,1 6,3', 'J 1,4 3,6', 'E 2,1 3,1', 'J 3,1 5,3', 'E 1,2 1,3', 'J 1,3 3,5']

		evacuate_camp_string = '\n'.join(evac_sequence).rstrip()

		if os.path.exists("playdata.txt"):
			with open("playdata.txt", "r") as fin:
				file_contents = fin.read().splitlines(True)
				first_line = file_contents[0]
				file_len = len(file_contents)
				if first_line == "DONE":
					camp_empty = True
					move = first_line
					return move
				else:
					camp_empty = False
					move = first_line
					move = self.parseMove(move)

			if not camp_empty:
				with open("playdata.txt", "w") as fout:
					if file_len == 1:
						data = "DONE"
						fout.writelines(data)
					else:
						fout.writelines(file_contents[1:])

					return move
		else:
			f = open("playdata.txt", "w")
			first_move = self.parseMove(first_move)

			f.write(evacuate_camp_string)
			f.close()

			return first_move


	def parseMove(self, move):
		move = move.split()
		move_from = move[1].split(",")
		move_from = (int(move_from[0]), int(move_from[1]))
		move_to = move[2].split(",")
		move_to = (int(move_to[0]), int(move_to[1]))

		parsed_move = (move[0], move_from, move_to)

		return parsed_move

	def inOppQuarter(self, game_board, color):
		if color == "W":
			start, end = 0, 8
		elif color == "B":
			start, end = 8, 16

		pawn_count = 0
		for i in range(start, end):
			for j in range(start, end):
				if game_board[i][j] == color:
					pawn_count += 1

		if pawn_count == 19:
			return True
		return False

	def endGame2(self, game_board, my_color):
		if my_color == "W":
			opp_color = "B"
			opp_quarter_x, opp_quarter_y = 0, 8
			move_x = [0, 1, -1, -1, -1]
			move_y = [-1, -1, 1, 0, -1]

			opp_camp = [(0, 0), (0, 1), (1, 0), (1, 1), (0, 2), (2, 0), (1, 2), (2, 1), (0, 3), (3, 0), (2, 2), (1, 3), \
						(3, 1), (0, 4), (4, 0), (2, 3), (3, 2), (1, 4), (4, 1)]
			opp_camp_priorities = {(0, 0):5, (0, 1):4, (1, 0):4, (1, 1):3, (0, 2):3, (2, 0):3, (1, 2):2, (2, 1):2, (0, 3):2, (3, 0):2, (2, 2):1, (1, 3):1, \
						(3, 1):1, (0, 4):1, (4, 0):1, (2, 3):0, (3, 2):0, (1, 4):0, (4, 1):0}
		elif my_color == "B":
			opp_color = "W"
			move_x = [1, 1, 1, 0, -1]
			move_y = [-1, 0, 1, 1, 1]
			opp_quarter_x, opp_quarter_y = 8, 16

			opp_camp = [(15, 15), (15, 14), (14, 15), (14, 14), (15, 13), (13, 15), (14, 13), (13, 14), (15, 12), (12, 15), \
						(13, 13), (14, 12), (12, 14), (15, 11), (11, 15), (13, 12), (12, 13), (14, 11), (11, 14)]
			opp_camp_priorities = {(15, 15):5, (15, 14):4, (14, 15):4, (14, 14):3, (15, 13):3, (13, 15):3, (14, 13):2, (13, 14):2, (15, 12):2, (12, 15):2, \
						(13, 13):1, (14, 12):1, (12, 14):1, (15, 11):1, (11, 15):1, (13, 12):0, (12, 13):0, (14, 11):0, (11, 14):0}

		quarter_count = 0

		for i in range(opp_quarter_x, opp_quarter_y):
			for j in range(opp_quarter_x, opp_quarter_y):
				if game_board[i][j] == my_color:
					quarter_count += 1

		num_pawns_in_opp_camp = 0
		free_positions = []
		occupied_positions = set()
		opp_camp_set = set(opp_camp)

		for x, y in opp_camp:
			if game_board[x][y] == my_color:
				num_pawns_in_opp_camp += 1
				occupied_positions.add((x, y))
			elif game_board[x][y] == ".":
				free_positions.append((x, y))

		if num_pawns_in_opp_camp > 9 and quarter_count == 19:
			if not free_positions:
				return "SUCCESS"

			go_to_pos = free_positions[0]

			jump_inside = None
			jump_outside_to_inside = None
			joi_dist = float("-inf")
			edge_inside = None
			camp_move = None
			camp_dist = float("inf")
			for from_x in range(16):
				for from_y in range(16):

					if game_board[from_x][from_y] == my_color:

						for i in range(5):
							to_x = from_x + move_x[i]
							to_y = from_y + move_y[i]

							if self.isSafe(to_x, to_y) and game_board[to_x][to_y] != ".":
								jump_x = to_x + move_x[i]
								jump_y = to_y + move_y[i]
								if self.isSafe(jump_x, jump_y) and game_board[jump_x][jump_y] == ".":

									visited = set()
									visited.add((from_x, from_y))

									self.executeMove(game_board, from_x, from_y, jump_x, jump_y, my_color)

									jumps, _ = self.findMoreJumps(jump_x, jump_y, game_board, visited, my_color, [], {})

									self.executeMove(game_board, jump_x, jump_y, from_x, from_y, my_color)

									jumps.append((jump_x, jump_y))
									jumps = list(set(jumps))

									for jump in jumps:
										if (from_x, from_y) in opp_camp_set and (jump[0], jump[1]) not in opp_camp_set:
											continue
										if (from_x, from_y) not in occupied_positions and math.sqrt(abs(jump[0] - go_to_pos[0])**2 + abs(jump[1] - go_to_pos[1])**2) < camp_dist:
											camp_move = ('J', (from_x, from_y), (jump[0], jump[1]))
											camp_dist = math.sqrt(abs(jump[0] - go_to_pos[0])**2 + abs(jump[1] - go_to_pos[1])**2)

										elif (from_x, from_y) in occupied_positions and (jump[0], jump[1]) not in occupied_positions and \
											(jump[0], jump[1]) in opp_camp_set and opp_camp_priorities[(from_x, from_y)] < opp_camp_priorities[(jump[0], jump[1])]:
											jump_inside =  ('J', (from_x, from_y), (jump[0], jump[1]))

										if (from_x, from_y) not in opp_camp_set and (jump[0], jump[1]) in opp_camp_set and math.sqrt(abs(from_x - jump[0])**2 + abs(from_y - jump[1])) > joi_dist:
											jump_outside_to_inside = ('J', (from_x, from_y), (jump[0], jump[1]))
											joi_dist = math.sqrt(abs(from_x - jump[0])**2 + abs(from_y - jump[1])) 

							elif self.isSafe(to_x, to_y) and game_board[to_x][to_y] == ".":
								if (from_x, from_y) in opp_camp_set and (to_x, to_y) not in opp_camp_set:
									continue
								if (from_x, from_y) not in opp_camp_set and (to_x, to_y) in opp_camp_set:
									return ('E', (from_x, from_y), (to_x, to_y))
								if (from_x, from_y) not in occupied_positions and math.sqrt(abs(to_x - go_to_pos[0])**2 + abs(to_y - go_to_pos[1])**2) < camp_dist:
									camp_move = ('E', (from_x, from_y), (to_x, to_y))
									camp_dist = math.sqrt(abs(to_x - go_to_pos[0])**2 + abs(to_y - go_to_pos[1])**2)

								elif (from_x, from_y) in occupied_positions and (to_x, to_y) not in occupied_positions and \
									(to_x, to_y) in opp_camp_set and opp_camp_priorities[(from_x, from_y)] < opp_camp_priorities[(to_x, to_y)]:
									edge_inside = ('E', (from_x, from_y), (to_x, to_y))

			if jump_outside_to_inside:
				return jump_outside_to_inside
			if jump_inside:
				return jump_inside
			if edge_inside:
				return edge_inside
			if camp_move:
				return camp_move
			return None

		else:
			return None


	def returnMoveUtility(self, board, move, utility_board, color):

		if color == "W":
			towards_x, towards_y, from_x, from_y = 0, 0, 15, 15
			my_camp = {(15, 15), (15, 14), (15, 13), (15, 12), (15, 11), (14, 15), (14, 14), (14, 13), (14, 12), (14, 11), \
						(13, 15), (13, 14), (13, 13), (13, 12), (12, 15), (12, 14), (12, 13), (11, 15), (11, 14)}

		else:
			towards_x, towards_y, from_x, from_y = 15, 15, 0, 0
			my_camp = {(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (2, 0), (2, 1), \
						(2, 2), (2, 3), (3, 0), (3, 1), (3, 2), (4, 0), (4, 1)}


		utility_move_before = move[1][0] + move[1][1]

		utility_move_after = move[2][0] + move[2][1]

		if color == "W":
			utility_move = utility_board + utility_move_before - utility_move_after
		else:
			utility_move = utility_board - utility_move_before + utility_move_after
				
		return utility_move 

	def returnUtilityBoard(self, board, color):
		if color == "W":
			towards_x, towards_y, from_x, from_y = 0, 0, 15, 15

		else:
			towards_x, towards_y, from_x, from_y = 15, 15, 0, 0

		utility_white = 0
		utility_black = 0

		for i in range(16):
			for j in range(16):
				if board[i][j] == "W":
					utility_white += i + j
				elif board[i][j] == "B":
					utility_black += 30 - (i + j)

		if color == "W":
			return utility_black - utility_white

		return utility_white - utility_black

	def executeMove(self, game_board, from_x, from_y, to_x, to_y, color):
		game_board[from_x][from_y] = "."
		game_board[to_x][to_y] = color
		return

	def reversePlayer(self, color):
		if color == "W":
			return "B"
		return "W"

	def isSafe(self, x, y):
		if x >= 0 and x < 16 and y >= 0 and y < 16:
			return True
		return False

	def returnJumpPath(self, from_pos, to_pos, game_board, visited, color, jumps, parents):
		if color == "W":
			move_x = [-1, -1, 0, -1, 1]
			move_y = [-1, 0, -1, 1, -1]
		else:
			move_x = [1, 1, 0, 1, -1]
			move_y = [1, 0, 1, -1, 1]

		for i in range(5):
			to_x = from_pos[0] + move_x[i]
			to_y = from_pos[1] + move_y[i]

			if self.isSafe(to_x, to_y) and game_board[to_x][to_y] == ".":
				continue
			elif self.isSafe(to_x, to_y) and game_board[to_x][to_y] != ".":
				jump_x = to_x + move_x[i]
				jump_y = to_y + move_y[i]
				if self.isSafe(jump_x, jump_y) and game_board[jump_x][jump_y] == ".":
					if (jump_x, jump_y) in visited:
						continue
					else:
						jumps.append(((from_pos[0], from_pos[1]), (jump_x, jump_y)))
						parents[(jump_x, jump_y)] = (from_pos[0], from_pos[1])
						
						self.executeMove(game_board, from_pos[0], from_pos[1], jump_x, jump_y, color)
						visited.add((jump_x, jump_y))
						self.returnJumpPath((jump_x, jump_y), to_pos, game_board, visited, color, jumps, parents)
						
						#jumps.append((jump_x, jump_y))
						self.executeMove(game_board, jump_x, jump_y, from_pos[0], from_pos[1], color)

						if (jump_x, jump_y) == to_pos:
							return jumps, parents
		return jumps, parents

	def findMoreJumps(self, from_x, from_y, game_board, visited, color, jumps, parents):
		if color == "W":
			move_x = [0, 1, -1, -1, -1]
			move_y = [-1, -1, 1, 0, -1]
		else:
			move_x = [1, 1, 1, 0, -1]
			move_y = [-1, 0, 1, 1, 1]

		for i in range(5):
			to_x = from_x + move_x[i]
			to_y = from_y + move_y[i]

			if self.isSafe(to_x, to_y) and game_board[to_x][to_y] == ".":
				continue
			elif self.isSafe(to_x, to_y) and game_board[to_x][to_y] != ".":
				jump_x = to_x + move_x[i]
				jump_y = to_y + move_y[i]
				if self.isSafe(jump_x, jump_y) and game_board[jump_x][jump_y] == ".":
					if (jump_x, jump_y) in visited:
						continue
					else:
						parents[(from_x, from_y)] = (jump_x, jump_y)
						
						self.executeMove(game_board, from_x, from_y, jump_x, jump_y, color)
						visited.add((jump_x, jump_y))
						self.findMoreJumps(jump_x, jump_y, game_board, visited, color, jumps, parents)
						jumps.append((jump_x, jump_y))
						self.executeMove(game_board, jump_x, jump_y, from_x, from_y, color)
		return jumps, parents

	def returnValidMoves(self, game_board, my_color):
		valid_moves = []
		adjacent_moves = []

		if my_color == "W":
			move_x = [0, 1, -1, -1, -1]
			move_y = [-1, -1, 1, 0, -1]
			opp_camp = {(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (2, 0), (2, 1), \
						(2, 2), (2, 3), (3, 0), (3, 1), (3, 2), (4, 0), (4, 1)}
		else:
			move_x = [1, 1, 1, 0, -1]
			move_y = [-1, 0, 1, 1, 1]
			opp_camp = {(15, 15), (15, 14), (15, 13), (15, 12), (15, 11), (14, 15), (14, 14), (14, 13), (14, 12), (14, 11), \
						(13, 15), (13, 14), (13, 13), (13, 12), (12, 15), (12, 14), (12, 13), (11, 15), (11, 14)}

		for from_x in range(16):
			for from_y in range(16):
				if game_board[from_x][from_y] == my_color:
					for i in range(5):
						to_x = from_x + move_x[i]
						to_y = from_y + move_y[i]

						if self.isSafe(to_x, to_y) and game_board[to_x][to_y] == ".":
							if (from_x, from_y) in opp_camp and (to_x, to_y) not in opp_camp:
								continue
							adjacent_moves.append(('E', (from_x, from_y), (to_x, to_y)))	
						elif self.isSafe(to_x, to_y) and game_board[to_x][to_y] != ".":
							jump_x = to_x + move_x[i]
							jump_y = to_y + move_y[i]
							if self.isSafe(jump_x, jump_y) and game_board[jump_x][jump_y] == ".":
								visited = set()
								visited.add((from_x, from_y))

								self.executeMove(game_board, from_x, from_y, jump_x, jump_y, my_color)

								jumps, _ = self.findMoreJumps(jump_x, jump_y, game_board, visited, my_color, [], {})

								self.executeMove(game_board, jump_x, jump_y, from_x, from_y, my_color)

								jumps.append((jump_x, jump_y))
								jumps = list(set(jumps))
								for jump in jumps:
									if (from_x, from_y) in opp_camp and (jump[0], jump[1]) not in opp_camp:
										continue
									valid_moves.append(('J', (from_x, from_y), (jump[0], jump[1])))
		
		return valid_moves + adjacent_moves

	def isEndGame(self, game_board, color):
		if color == "W":
			opp_camp = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (2, 0), (2, 1), \
						(2, 2), (2, 3), (3, 0), (3, 1), (3, 2), (4, 0), (4, 1)]
		else:
			opp_camp = [(15, 15), (15, 14), (15, 13), (15, 12), (15, 11), (14, 15), (14, 14), (14, 13), (14, 12), (14, 11), \
						(13, 15), (13, 14), (13, 13), (13, 12), (12, 15), (12, 14), (12, 13), (11, 15), (11, 14)]

		my_pawn_in_opp_camp = False

		for x, y in opp_camp:
			if game_board[x][y] == ".":
				return False
			if game_board[x][y] == color:
				my_pawn_in_opp_camp = True

		if my_pawn_in_opp_camp:
			return True
		return False

	def alphabeta(self, game_board, my_color, max_depth):
		utility_board = self.returnUtilityBoard(game_board, my_color)
		best = self.maxValue(game_board, my_color, utility_board, float("-inf"), float("inf"), 0, max_depth)
		return best

	def maxValue(self, game_board, my_color, utility_board, alpha, beta, cur_depth, max_depth):
		if cur_depth == max_depth or self.isEndGame(game_board, my_color):
			return (None, utility_board)

		best = (None, float("-inf"))
		moves = self.returnValidMoves(game_board, my_color)

		for move in moves:
			self.executeMove(game_board, move[1][0], move[1][1], move[2][0], move[2][1], my_color)
			new_utility_board = self.returnMoveUtility(game_board, move, utility_board, my_color)

			m, score = self.minValue(game_board, self.reversePlayer(my_color), new_utility_board, alpha, beta, cur_depth+1, max_depth)

			if score > best[1]:
				best = (move, score)

			self.executeMove(game_board, move[2][0], move[2][1], move[1][0], move[1][1], my_color)

			if best[1] >= beta:
				return best
			alpha = max(alpha, best[1])
		return best	

	def minValue(self, game_board, my_color, utility_board, alpha, beta, cur_depth, max_depth):
		if cur_depth == max_depth or self.isEndGame(game_board, my_color):
			return (None, utility_board)

		best = (None, float("inf"))

		moves = self.returnValidMoves(game_board, my_color)

		for move in moves:
			self.executeMove(game_board, move[1][0], move[1][1], move[2][0], move[2][1], my_color)
			new_utility_board = self.returnMoveUtility(game_board, move, utility_board, my_color)

			m, score = self.maxValue(game_board, self.reversePlayer(my_color), new_utility_board, alpha, beta, cur_depth+1, max_depth)

			if score < best[1]:
				best = (move, score)

			self.executeMove(game_board, move[2][0], move[2][1], move[1][0], move[1][1], my_color)

			if best[1] <= alpha:
				return best
			beta = min(beta, best[1])
		return best

if __name__ == '__main__':
	
	solution = Solution()
	
