import pygame
import sys, math, time
import quaternions
import numpy as np


class projectOnScreen:
	def __init__(self, frame, cam, nodes, edges, spherical=False, node_color=(200, 0, 0), edge_color=(0, 0, 0)):
		self.coordinates = np.array([1,1,1])
		self.frame = frame
		self.center_x, self.center_y = self.frame[0] * 0.5, self.frame[1] * 0.5
		self.cam = cam
		self.projected_coordinates = np.array([1, 1, 1])
		self.spherical = spherical
		self.edges = edges
		self.edge_color = edge_color
		self.nodes = nodes
		self.node_color = node_color

	# shifting coordinate system...
	def translate(self):
		self.coordinates -= np.array(self.cam.pos)

	def rotate_3D(self):
		vec = quaternions.qrot_vec(self.coordinates, self.cam.rot_x, self.cam.azimuthal_vec, self.cam.pos)
		vec = quaternions.qrot_vec(vec, self.cam.rot_y, self.cam.pitch_vec, self.cam.pos)
		self.coordinates = vec

	def project(self, demanded=False):
		self.coordinates = np.array(self.coordinates)
		some_factor = 10000 # pixel to unit ratio inverse.
		planner = np.dot(self.coordinates, self.cam.roll_vec)
		sphere = np.linalg.norm(self.coordinates)
		if math.copysign(1,planner) == -1:
			visible = 0
		else:
			visible = 1
		if not self.spherical:
			ratio = self.cam.radius/planner
			projected_vec = ratio*self.coordinates-self.cam.roll_vec*self.cam.radius
			along = np.dot(self.cam.azimuthal_vec, projected_vec)
			perpen = np.dot(self.cam.pitch_vec, projected_vec)
			if demanded:
				return [int(perpen*some_factor + self.center_x), int(along*some_factor + self.center_y), visible]
			else:
				self.projected_coordinates = [int(perpen*some_factor + self.center_x), int(along*some_factor + self.center_y), visible]
		else:
			ratio = self.cam.radius/sphere
			projected_vec = ratio*self.coordinates-self.cam.roll_vec*self.cam.radius
			along = np.dot(self.cam.azimuthal_vec, projected_vec)
			perpen = np.dot(self.cam.pitch_vec, projected_vec)
			if demanded:
				return [int(perpen*some_factor + self.center_x), int(along*some_factor + self.center_y), visible]
			else:
				self.projected_coordinates = [int(perpen*some_factor + self.center_x), int(along*some_factor + self.center_y), visible]


	def edgeVisiblePoint(self, visible_points, points):
		point1, point2 = points[0], points[1]
		self.coordinates = np.float32(self.coordinates)
		if point1[2] == 0 and point2[2] == 0:
			return None
		else:
			if point2[2] == 0:
				b = visible_points[1]-visible_points[0]
				# a = visible_points[0]
				# self.coordinates = a+((self.cam.radius-np.dot(a, self.cam.roll_vec))/(np.dot(b,self.cam.roll_vec)))*b
				self.coordinates = visible_points[0]+((self.cam.radius-np.dot(visible_points[0], self.cam.roll_vec))/(np.dot(b,self.cam.roll_vec)))*b
				
				point2 = self.project(demanded=True)
			elif point1[2] == 0:
				b = visible_points[0]-visible_points[1]
				#a = visible_points[1]
				self.coordinates = visible_points[1]+((self.cam.radius-np.dot(visible_points[1], self.cam.roll_vec))/(np.dot(b,self.cam.roll_vec)))*b
				point1 = self.project(demanded=True)
			else:
				return points
		return [point1, point2]



	def select_transform(self):
		self.translate()
		self.project()

	def render_edges(self,screen, edges, vertices, color=None):
		if color == None:
			color = self.edge_color
		for edge in edges:
			points = []
			visible_points = []
			for coordinates in (vertices[edge[0]], vertices[edge[1]]):
				self.coordinates = coordinates
				self.select_transform()
				visible_points += [self.coordinates]
				points += [self.projected_coordinates]
			points = self.edgeVisiblePoint(visible_points, points)
			if points is not None:
				pygame.draw.line(screen, color, points[0][:2], points[1][:2], 3)

	def render_nodes(self, screen, nodes, color=None):
		if color == None:
			color = self.node_color
		for node in nodes:
			self.coordinates = node
			self.select_transform()
			if self.projected_coordinates[2] == 1:
				pygame.draw.circle(screen, color, self.projected_coordinates[:2], 5, 0)

	def render_axis(self, screen):
		axis_color = ((255, 0, 0), (0, 255, 0), (0, 0, 255), (252, 85, 8))
		axis_letter = ('X', 'Y', 'Z')
		vertices_a = [(0,0,0), (3,0,0), (0,3,0), (0,0,3)]
		edges_a = [(0,1), (0,2), (0,3)]
		for i, edge in enumerate(edges_a):
			points = []
			visible_points = []
			for coordinates in (vertices_a[edge[0]], vertices_a[edge[1]]):
				self.coordinates = coordinates
				self.select_transform()
				visible_points += [self.coordinates]
				points += [self.projected_coordinates]
			points = self.edgeVisiblePoint(visible_points, points)
			if points is not None:
				pygame.draw.line(screen, axis_color[i], points[0][:2], points[1][:2], 1)

		font = pygame.font.Font('freesansbold.ttf', 22)
		for i, node in enumerate(vertices_a[1:]):
			self.coordinates = node
			self.select_transform()
			if self.projected_coordinates[2] == 1:
				pygame.draw.circle(screen, axis_color[i], self.projected_coordinates[:2], 5, 0)
				text = font.render(axis_letter[i], True,axis_color[i])
				textRect = text.get_rect()	
				textRect.center = (self.projected_coordinates[0], self.projected_coordinates[1])
				screen.blit(text, textRect)
			# font = pygame.font.Font('freesansbold.ttf', 12)
			# text = font.render(f"{math.degrees(math.acos(self.cam.azimuthal_vec[2]))}", True,(0,0,0))
			# textRect = text.get_rect()
			# textRect.center = (500,10)
			# screen.blit(text, textRect)


	def run(self, edges=True, nodes=True, axis=False):
		pygame.init()
		center_x, center_y = self.frame[0] * 0.5, self.frame[1] * 0.5
		center_x, center_y = int(center_x), int(center_y)
		screen = pygame.display.set_mode(self.frame)
		clock = pygame.time.Clock()
		pygame.event.get()
		pygame.mouse.get_rel()
		pygame.mouse.set_visible(0)
		pygame.event.set_grab(1)

		# mouse_mov = [0,0]
		# m_pos = [-100,-100]
		# t = 0
		# error = True
		while True:
			dt = clock.tick()*0.001
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						pygame.quit()
						sys.exit()
				# if error is False:
				# 	posNew = pygame.mouse.get_pos()
				# 	mouse_mov[0] = posNew[0] - m_pos[0]
				# 	mouse_mov[1] = posNew[1] - m_pos[1]
				# 	if (posNew[0] < 2):
				# 		pygame.mouse.set_pos((self.frame[0]-5, posNew[1]))
				# 		m_pos = pygame.mouse.get_pos()
				# 	if (posNew[0] > self.frame[0]-2):
				# 		pygame.mouse.set_pos((5, posNew[1]))
				# 		m_pos = pygame.mouse.get_pos()
				# 	if (posNew[1] < 2):
				# 		pygame.mouse.set_pos((posNew[0], self.frame[1]-5))
				# 		m_pos = pygame.mouse.get_pos()
				# 	if (posNew[1] > self.frame[1]-2):
				# 		pygame.mouse.set_pos(((posNew[0], 5)))
				# 		m_pos = pygame.mouse.get_pos()
				# 	if m_pos != posNew:
				# 		m_pos = posNew
				# 		error = self.cam.mouse_events(mouse_mov, event)
				# 	else:
				# 		error = self.cam.mouse_events((0,0), event)
				# else:
				# 	error = self.cam.mouse_events(mouse_mov, event)

				# posNew = pygame.mouse.get_pos()
				# if (posNew[0] < 2):
				# 	pygame.mouse.set_pos((self.frame[0]-5, posNew[1]))
				# if (posNew[0] > self.frame[0]-2):
				# 	pygame.mouse.set_pos((5, posNew[1]))
				# if (posNew[1] < 2):
				# 	pygame.mouse.set_pos((posNew[0], self.frame[1]-5))
				# if (posNew[1] > self.frame[1]-2):
				# 	pygame.mouse.set_pos(((posNew[0], 5)))
				# error = self.cam.mouse_events(mouse_mov, event)
				error = self.cam.mouse_events(event)

			screen.fill((200, 200, 200))
			if edges:
				self.render_edges(screen, self.edges, self.nodes)
			if nodes:
				self.render_nodes(screen, self.nodes, self.node_color)
			if axis:
				self.render_axis(screen)
			pygame.display.flip()
			key = pygame.key.get_pressed()
			if key[pygame.K_t]:
				if self.spherical:
					time.sleep(0.5)
					self.spherical=False
				else:
					time.sleep(0.5)
					self.spherical=True
			self.cam.update(dt, key)

			# t += dt
			# if t >5000:
			# 	t = 1


class Cam:
	def __init__(self, pos=(1,1,1)):
		self.z_axis = np.array([0,0,1])
		self.radius = 0.02
		self.pos = np.array(pos)
		self.rot_x = 0
		self.rot_y = 0
		self.roll_vec = np.array((0,0,-1))
		self.azimuthal_vec = -np.array((1,0,0)) # azimuthal negetive because in pygames pixel coords for y axis is negetive
												# and z projects to y_pixel
		self.pitch_vec = np.cross(self.azimuthal_vec, self.roll_vec)
		self.sensitivity = 800.0
	def mouse_events(self, event):#, m_pos, event):
		try:
			x, y = event.rel
			error = True
		except Exception as e:
			error = True
			#print(error)
			x, y = 0,0#m_pos
		else:
			pass
		finally:
			pass
		self.rot_x = -x/self.sensitivity
		self.rot_y = -y/self.sensitivity
		if abs(self.rot_x)>0.6125:
			self.rot_x = 0
		if abs(self.rot_y)>0.6125:
			self.rot_y = 0
		# x = x/self.sensitivity
		# y = y/self.sensitivity
		# if abs(x)>0.6125:
		# 	x = 0
		# if abs(y)>0.6125:
		# 	y = 0
		# self.rot_x -= x
		# self.rot_y += y
		self.roll_vec = quaternions.qrot_vec(self.roll_vec, self.rot_x, self.z_axis) # rotating about z-axis
		self.azimuthal_vec = quaternions.qrot_vec(self.azimuthal_vec, self.rot_x, self.z_axis)# rotating about z-axiz
		self.pitch_vec = quaternions.qrot_vec(self.pitch_vec, self.rot_x, self.z_axis)# rotating about z-axiz
		self.roll_vec = quaternions.qrot_vec(self.roll_vec, self.rot_y, self.pitch_vec) # rotating about z-axis
		self.azimuthal_vec = quaternions.qrot_vec(self.azimuthal_vec, self.rot_y, self.pitch_vec) # rotating about z-axis
		#return error

	def update(self, dt, key):
		s = dt*5
		self.pos = np.array(self.pos, dtype=np.float32)
		if key[pygame.K_a]: self.pos -= self.pitch_vec*s
		if key[pygame.K_s]: self.pos -= self.roll_vec*s
		if key[pygame.K_w]: self.pos += self.roll_vec*s
		if key[pygame.K_d]: self.pos += self.pitch_vec*s
		if key[pygame.K_q]: self.pos += self.azimuthal_vec*s
		if key[pygame.K_e]: self.pos -= self.azimuthal_vec*s
		if key[pygame.K_r]:
			self.pos = np.array([0,0,5])
			self.roll_vec -= np.array([0,0,-1])
			self.azimuthal_vec -= np.array([1,0,0])

if __name__ == "__main__":
	cube = ((-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
					(-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1))

	cube_edges = ((0, 1), (1, 2), (2, 3), (3, 0),
			 (0, 4), (1, 5), (2, 6), (3, 7),
			 (4, 5), (5, 6), (6, 7), (7, 4))

	vertices = []
	edges = []
	for i in range(4):
		for c_nodes in cube:
			value = list(c_nodes[:])
			value[0] += i*2
			vertices.append(value)
		for c_edge in cube_edges:
			value2 = list(c_edge[:])
			for j in range(len(value2)):
				value2[j] += i*8
			edges.append(value2)

		for c_nodes in cube:
			value = list(c_nodes[:])
			value[1] += i*2
			vertices.append(value)
		for c_edge in cube_edges:
			value2 = list(c_edge[:])
			for j in range(len(value2)):
				value2[j] += i*8
			edges.append(value2)

	for i in range(8):
		for c_edge in cube_edges:
			value2 = list(c_edge[:])
			for j in range(len(value2)):
				value2[j] += i*8
			edges.append(value2)
	#print(edges)

	myscreen = projectOnScreen((1000, 600),Cam(pos=(0,0,5)), vertices, edges, spherical=False, node_color=(200, 0, 0))
	myscreen.run(edges=True, nodes=False, axis=False)

