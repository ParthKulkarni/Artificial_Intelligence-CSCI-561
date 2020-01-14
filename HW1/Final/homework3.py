import queue as q
import heapq as hq
#import time
#import math


class Solution(object):
	def __init__(self):
		self.params = Solution.get_input_params(self)
		#print(self.params["algorithm"])
		if self.params["algorithm"] == "BFS":
			#x = time.time()
			BFS(self.params)
			#print(time.time() - x)
		if self.params["algorithm"] == "UCS":
			#print("UCS")
			#x = time.time()
			UCS(self.params)
			#print(time.time() - x)
		if self.params["algorithm"] == "A*":
			#x = time.time()
			AStar(self.params)
			#print(time.time() - x)


	def get_input_params(self):	
		#x = time.time()
		params = {}

		#Open input file and store content 
		f = open("input.txt", "r")
		#f = open("generated_testcase_A_.txt", "r")
		#f = open("input1000x1000with40.txt", "r")
		lines = f.readlines()
		f.close()

		#Which algorithm to use
		algorithm = lines[0]
		params["algorithm"] = algorithm.rstrip("\n")

		#Size of map
		size = lines[1].split()
		width_map, height_map = int(size[0]), int(size[1])
		params['width_map'] = width_map
		params['height_map'] = height_map
 
		#Co-ordinates of landing site
		landing_site = lines[2].split()
		landing_x, landing_y = int(landing_site[1]), int(landing_site[0])
		params['landing_x'] = landing_x
		params['landing_y'] = landing_y

		#Maximum difference in elevation between two adjacent cells
		max_diff_elev = int(lines[3])
		params['max_diff_elev'] = max_diff_elev

		#Number of target sites
		n_target_sites = int(lines[4])
		params['n_target_sites'] = n_target_sites

		#List of target co-ordinates
		target_coords_list = []
		target_coords_set = set()   
		for i in range(n_target_sites):
			target_coords = lines[5+i].split()
			target_x, target_y = int(target_coords[1]), int(target_coords[0])
			target_coords_list.append((target_x, target_y))
			target_coords_set.add((target_x, target_y))
		params['target_coords_list'] = target_coords_list
		params['target_coords_set'] = target_coords_set

		#Read map
		mars_map = []
		for i in range(height_map):
			map_row = lines[5 + n_target_sites + i].split()
			map_row = list(map(int, map_row))
			mars_map.append(map_row)
		params['mars_map'] = mars_map


		#print(time.time()-x)

		return params

		#print(self.mars_map[self.target_coords_list[0][0]][self.target_coords_list[0][1]])
		#print(self.landing_x, self.landing_y)
		#print(self.mars_map[self.landing_x][self.landing_y])

class Node:
	def __init__(self, cost, position):
		self.cost = cost
		self.position = position
		self.parent = None

class AStar(object):
	def __init__(self, params):
		self.params = params
		self.runAStar()

	def isSafeMove(self, pos_x, pos_y):
		if pos_x >= 0 and pos_x < self.params["height_map"] and pos_y >= 0 and pos_y < self.params["width_map"]:
			return True
		return False

	def findDistance(self, node1, node2):
		x1, y1 = node1[0], node1[1]
		x2, y2 = node2[0], node2[1]

		dx = abs(x1 - x2)
		dy = abs(y1 - y2)
		h = 10 * (dx + dy) - 6 * min(dx, dy) + abs(self.params["mars_map"][x1][y1] - self.params["mars_map"][x2][y2]) - 1
		h += h * 0.000001
		
		return h
		#return  10 * math.sqrt(dx*dx + dy*dy) + abs(self.params["mars_map"][x1][y1] - self.params["mars_map"][x2][y2])

	def findClosestTarget(self, node):
		result = float("inf")
		nearest_target = None

		for target in self.params["target_coords_list"]:
			if node != target:
				d = self.findDistance(node, target)
				if d < result:
					result = d
					nearest_target = target
		return result

	def returnSafeMoves(self, node, target):
		#print("In safe_moves")
		cur_x, cur_y = node[0], node[1]

		safe_moves = []
		move_x = [0, 1, 1, 1, 0, -1, -1, -1]
		move_y = [-1, -1, 0, 1, 1, 1, 0, -1]

		#print("In safe_moves")
		#print(cur_x, cur_y)

		for i in range(8):
			new_x = cur_x + move_x[i]
			new_y = cur_y + move_y[i]

			if self.isSafeMove(new_x, new_y) and abs(self.params["mars_map"][new_x][new_y] - self.params["mars_map"][cur_x][cur_y]) <= self.params["max_diff_elev"]:
				#print(mars_map[new_x][new_y] - mars_map[cur_x][cur_y], mars_map[new_x][new_y])
				cost = 0

				if move_x[i] == 0 or move_y[i] == 0:
					g = 10 + abs(self.params["mars_map"][new_x][new_y] - self.params["mars_map"][cur_x][cur_y])
					h = self.findDistance((new_x, new_y), target)
					#cost = g + h
				else:
					g = 14 + abs(self.params["mars_map"][new_x][new_y] - self.params["mars_map"][cur_x][cur_y])
					h = self.findDistance((new_x, new_y), target)
					#cost = g + h

				safe_moves.append((0, g, h, (new_x, new_y)))

		return safe_moves

	def runAStar(self):
		start = (self.params["landing_x"], self.params["landing_y"])
		output = {}
		output_set = set()
		costs = {}
		targets_reached = set()
		g_visited = set()
		g_parents = {}

		for target in self.params["target_coords_set"]:

			if target in g_visited:
				#print("Target already found")
				#print(target, costs[target][0])
				path = []
				t = target

				#print(t == start)

				while t != start:
					#print(type(t), type(start))
					path.append(t)
					t = g_parents[t]
				path.append(start)

				output[target] = [tuple(reversed(tup)) for tup in path][::-1]

				continue

			frontier = []
			frontier_set = set()
			visited = set()
			parents = {}

			frontier.append((0, 0, self.findDistance(start, target), start))
			hq.heapify(frontier)
			frontier_set.add(start)
			costs[start] = (0, self.findDistance(start, target))

			while frontier:
				#print(frontier)
				cur_f, cur_g, cur_h, cur_node = hq.heappop(frontier)
				visited.add(cur_node)

				if cur_node == target:
					#print(cur_node, cur_g)
					#print(len(visited))
					path = []
					targets_reached.add(cur_node)
					t = cur_node

					while cur_node != start:
						path.append(cur_node)
						cur_node = parents[cur_node]
					path.append(start)

					output[target] = [tuple(reversed(tup)) for tup in path][::-1]

					break				

				neighbors = self.returnSafeMoves(cur_node, target)

				for neighbor in neighbors:

					if neighbor[3] in visited:
						continue

					if neighbor[3] in frontier_set:
						new_cost = cur_g + neighbor[1] + neighbor[2]

						if costs[neighbor[3]][0] + costs[neighbor[3]][1] > new_cost:
							hq.heappush(frontier, (new_cost, cur_g + neighbor[1], neighbor[2], neighbor[3]))
							parents[neighbor[3]] = cur_node
							costs[neighbor[3]] = (cur_g + neighbor[1], neighbor[2])

					else:
						hq.heappush(frontier, (cur_g + neighbor[1] + neighbor[2], cur_g + neighbor[1], neighbor[2], neighbor[3]))
						parents[neighbor[3]] = cur_node
						costs[neighbor[3]] = (cur_g + neighbor[1], neighbor[2])
						frontier_set.add(neighbor[3])

			#print(len(visited))
			#print(len(g_visited))
			g_visited = g_visited.union(visited)
			g_parents.update(parents)

		outfile = open("output.txt", "w+")
		outstring = ''
		for target in self.params["target_coords_list"]:
			if target in output:

				for step in output[target]: 
					outstring += (str(step[0]) + "," + str(step[1]) + " ")
				outstring = outstring.strip() + "\n"
			else:
				outstring += "FAIL\n"

		outfile.write(outstring.rstrip())
		outfile.close()


class UCS(object):
	def __init__(self, params):
		self.params = params
		self.runUCS()

	def isSafeMove(self, pos_x, pos_y):
		if pos_x >= 0 and pos_x < self.params["height_map"] and pos_y >= 0 and pos_y < self.params["width_map"]:
			return True
		return False

	def returnSafeMoves(self, node):
		#print("In safe_moves")
		cur_x, cur_y = node[0], node[1]

		safe_moves = []
		move_x = [0, 1, 1, 1, 0, -1, -1, -1]
		move_y = [-1, -1, 0, 1, 1, 1, 0, -1]

		#print("In safe_moves")
		#print(cur_x, cur_y)

		for i in range(8):
			new_x = cur_x + move_x[i]
			new_y = cur_y + move_y[i]

			if self.isSafeMove(new_x, new_y) and abs(self.params["mars_map"][new_x][new_y] - self.params["mars_map"][cur_x][cur_y]) <= self.params["max_diff_elev"]:
				#print(mars_map[new_x][new_y] - mars_map[cur_x][cur_y], mars_map[new_x][new_y])
				cost = 0

				if move_x[i] == 0 or move_y[i] == 0:
					cost = 10
				else:
					cost = 14
				safe_moves.append((cost, (new_x, new_y)))

		return safe_moves

			
	def runUCS(self):
		start = (self.params["landing_x"], self.params["landing_y"])
		frontier = []
		frontier_set = set()
		visited = set()
		targets_reached = set()
		parents = {}
		
		output = {}
		output_set = set()
		costs = {}
		outfile = open("output.txt", "w+")

		frontier.append((0, start))
		hq.heapify(frontier)
		frontier_set.add(start)

		#hq.heappush(frontier, (0, start))
		costs[start] = 0
		#i = 0
		while frontier:
			#print("Beginning while")
			# print(frontier.get())
			#cur_cost, cur_node = hq.heappop(frontier)
			#print(cur_cost, cur_node)

			min_frontier = hq.heappop(frontier)
			#min_frontier = min(frontier, key = lambda key: frontier[key])
			#cur_node, cur_cost = min_frontier, frontier[min_frontier]
			#del frontier[min_frontier]
			cur_cost, cur_node = min_frontier[0], min_frontier[1]
			#if i < 10:
			#	print(cur_node, cur_cost)
			#i+=1
			#frontier_set.remove(cur_node)

			
			#print("cur_node, cur_cost: "+ str(cur_node) + str(cur_cost))
			#print(frontier)

			# if cur_node in costs and cur_cost > costs[cur_node]:
			# 	print("Continue")
			# 	continue
			#print("############")
			#print(self.params["target_coords_set"])
			if cur_node in self.params["target_coords_set"] and cur_node not in targets_reached:
				#print("******************")
				#print("Target found")
				#print(cur_node, cur_cost)
				path = []
				#print("Target found")
				target = cur_node
				targets_reached.add(target)
				#print(parents)

				while cur_node != start:
					#print("Creating path")
					path.append(cur_node)
					cur_node = parents[cur_node]
				path.append(start)

				output[target] = [tuple(reversed(tup)) for tup in path][::-1]

				output_set.add(target)
				#print(path)
				cur_node = target

				if len(targets_reached) == len(self.params["target_coords_list"]):
					break

				#continue

			#print("Deleting cur_node")
			#del frontier[cur_node]
			#print(frontier)

			#print("Adding to visited")
			visited.add(cur_node)
			#print(visited)

			neighbors = self.returnSafeMoves(cur_node)
			#print(neighbors)

			for neighbor in neighbors:

				if neighbor[1] in visited:
					continue

				if neighbor[1] in frontier_set:
					new_cost = cur_cost + neighbor[0]
					if costs[neighbor[1]] > new_cost:
						#frontier.remove((costs[neighbor[1]], neighbor[1])) #(juna cost, neighbor) O(n)
						hq.heappush(frontier, (new_cost, (neighbor[1])))
						costs[neighbor[1]] = new_cost
						parents[neighbor[1]] = cur_node

				else:
					#print(cur_cost + neighbor[0], neighbor[1])
					hq.heappush(frontier, (cur_cost + neighbor[0], neighbor[1]))
					costs[neighbor[1]] = cur_cost + neighbor[0]
					parents[neighbor[1]] = cur_node
					frontier_set.add(neighbor[1])
					#costs[neighbor[1]] = cur_cost + neighbor[0]
					#visited.add(neighbor[1])

			#print(output)
			#print("After for")
			#print(neighbors)
			#print(visited)

		#print(output)
		#print(len(visited))
		outstring = ''
		for target in self.params["target_coords_list"]:
			if target in output:

				for step in output[target]: 
					outstring += (str(step[0]) + "," + str(step[1]) + " ")
				outstring = outstring.strip() + "\n"
			else:
				outstring += "FAIL\n"

		outfile.write(outstring.rstrip())
		outfile.close()


class BFS(object):
	def __init__(self, params):
		self.params = params
		self.runBFS()
		#print("In BFS!" + str(params))

	def isSafeMove(self, pos_x, pos_y):
		if pos_x >= 0 and pos_x < self.params["height_map"] and pos_y >= 0 and pos_y < self.params["width_map"]:
			return True
		return False

	def returnSafeMoves(self, mars_map, cur_x, cur_y):
		#print("In safe_moves")
		safe_moves = []
		move_x = [0, 1, 1, 1, 0, -1, -1, -1]
		move_y = [-1, -1, 0, 1, 1, 1, 0, -1]

		#print(cur_x, cur_y)

		for i in range(8):
			new_x = cur_x + move_x[i]
			new_y = cur_y + move_y[i]

			if self.isSafeMove(new_x, new_y) and abs(mars_map[new_x][new_y] - mars_map[cur_x][cur_y]) <= self.params["max_diff_elev"]:
				safe_moves.append((new_x, new_y))

		return safe_moves

	def runBFS(self):
		visited = set([(self.params["landing_x"], self.params["landing_y"])])
		targets_reached = set()
		
		path = []
		frontier = q.Queue()
		parents = {}
		output = {}

		outfile = open("output.txt", "w+")

		start = (self.params["landing_x"], self.params["landing_y"])

		#path.append(start)
		frontier.put(start)
		
		while not frontier.empty():

			cur_node = frontier.get()
			#print(cur_node)

			if cur_node not in self.params["target_coords_set"]:
				#print(self.params["target_coords_list"], "curr", cur_node)
				#print("Not target")
				neighbors = self.returnSafeMoves(self.params["mars_map"], cur_node[0], cur_node[1])
				#print("Neighbors", neighbors)

				for neighbor in neighbors:

				 	if neighbor not in visited:

				 		frontier.put(neighbor)
				 		parents[neighbor] = cur_node
				 		visited.add(neighbor)

			elif cur_node in self.params["target_coords_set"] and cur_node not in targets_reached:
				neighbors = self.returnSafeMoves(self.params["mars_map"], cur_node[0], cur_node[1])
				#print("Neighbors", neighbors)

				for neighbor in neighbors:

				 	if neighbor not in visited:

				 		frontier.put(neighbor)
				 		parents[neighbor] = cur_node
				 		visited.add(neighbor)
				
				#print("In target")
				target = cur_node
				targets_reached.add(cur_node)

				while cur_node != start:
					path.append(cur_node)
					cur_node = parents[cur_node]
				path.append(start)

				output[target] = [tuple(reversed(tup)) for tup in path][::-1]

				path = []

				if len(targets_reached) == len(self.params["target_coords_list"]):
					break
		
		outstring = ''
		for target in self.params["target_coords_list"]:
			if target in output:

				for step in output[target]: 
					outstring += (str(step[0]) + "," + str(step[1]) + " ")
				outstring = outstring.strip() + "\n"
			else:
				outstring += "FAIL\n"

		outfile.write(outstring.rstrip())
		outfile.close()


if __name__ == '__main__':
	#x = time.time()
	solution = Solution()
	#print(time.time() - x)