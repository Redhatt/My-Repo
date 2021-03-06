from engine import *
from collision import *
from force import *

length, breadth = 1500, 700

diff = 0.15
OX, OY, X, Y = diff, diff, length / scale -diff, breadth / scale - diff

top = [[OX, OY], [X, OY]]
lef = [[OX, OY], [OX, Y]]
car_vert = [[0, 0], [5, 0], [5, 2], [0, 2]]
car = Polygon(car_vert, 500, 500, color='blue', e=1)
f_wheel = Cirlce([6, 5], 0.5, 50, 20, color='red', e=0.1, mu=0.9)
r_wheel = Cirlce([1, 5], 0.5, 50, 20, color='red', e=0.1, mu=0.9)
car.place((3.5, 3))
car.points = [[2.0, 3], [5.0, 3]]

gravity = GravityWorld()
drag = Drag()
drag_ang = DragAng()
k = 5000
beta = 500
rod1 = RodSlide(delta=0.15)
rod2 = RodSlide(delta=0.15)
rod3 = Rod()
rod4 = Rod()
rod5 = Rod()

spring1 = Spring(k=k, beta=beta)
spring2 = Spring(k=k, beta=beta)

spring1.attach(car, f_wheel, index=[1], adjust=True)
spring2.attach(car, r_wheel, index=[0], adjust=True)

rod1.attach(car, f_wheel, index=[1], adjust=True)
rod2.attach(car, r_wheel, index=[0], adjust=True)

rod3.attach(car, f_wheel, index=[0], adjust=True)
rod4.attach(car, r_wheel, index=[1], adjust=True)
rod5.attach(f_wheel, r_wheel, adjust=True)
# rod3.attach(r_wheel, f_wheel, index=[], adjust=True)


wall_top = Line(top, 1e9, 1e9, color='olive', e=0.5, move=False, type='Line')
wall_down = Line(top, 1e9, 1e9, color='olive', e=0.5, move=False, type='Line')
wall_left = Line(lef, 1e9, 1e9, color='olive', e=0.5, move=False, type='Line')
wall_right = Line(lef, 1e9, 1e9, color='olive', e=0.5, move=False, type='Line')
wall_down.shift([0, Y-OY])
wall_right.shift([X-OX, 0])

bumps = []
nt = 5
for i in range(nt):
    bump = Cirlce([4.5, 4.9], 0.25, 50, 20, color='red', e=1, mu=0.1, move=False)
    pos = ((OX + X)*(i+1)/nt, Y)
    bump.place(pos)
    bumps.append(bump)

contianer = []
walls = [wall_left, wall_right, wall_top, wall_down] + bumps
boxes = [car, f_wheel, r_wheel]

control = [f_wheel, r_wheel]
for i in boxes:
    i.attach_force(gravity)
    i.attach_force(drag)
    i.attach_force(drag_ang)
    i.shift((0, 8))
    contianer.append(i)

forces = [rod1, rod2, rod3, rod4, rod5, spring1, spring2, gravity]

FPS = 1000
pygame.init()
pygame.font.init()
pygame.display.set_caption("Nuclear Reaction !")
screen = pygame.display.set_mode((length, breadth))
clock = pygame.time.Clock()
run = True
start, end = 0, 0
ff = 1 # frame frame
dt = 0.01

while run:
    start = time()
    clock.tick(FPS)

    key = pygame.key.get_pressed()
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run = False
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            run = False

        if e.type == pygame.MOUSEMOTION:
                x, y = e.pos
                # control.place([x / scale, y/scale])
                # p.impulse_force(0.1*(np.array([x / scale, y/scale]) - p.cm_pos))
                # r.impulse_force(0.1*(np.array([x / scale, y/scale]) - r.cm_pos))


    if key[pygame.K_LEFT]:
        for i in control:
            i.impulse_torque(1.5)
        
    if key[pygame.K_RIGHT]:
        for i in control:
            i.impulse_torque(-1.5)

    if key[pygame.K_a]:
        for i in control:
            i.impulse_force(np.array([-0.5, 0]))

    if key[pygame.K_d]:
        for i in control:
            i.impulse_force(np.array([0.5, 0]))

    if key[pygame.K_w]:
        for i in control:
            i.impulse_force(np.array([0, -1.5]))

    if key[pygame.K_s]:
        for i in control:
            i.impulse_force(np.array([0, 1.5]))

    screen.fill('grey')

    for shape in boxes:
        shape.motion_dynamics(time(), dt=dt)

    for shape in walls:
        shape.draw(screen)

    for shape in contianer:
        shape.draw(screen)

    for force in forces:
        force.apply(time(), dt=dt)
        force.draw(screen, scale)

    points = collision_handler(contianer, walls)
    draw_points(screen, points)

    text(screen, f"FPS: {1000 // (ff)}, T: {ff} ms", length-150, 10, color=clr('black'))
    pygame.display.flip()
    end = time()
    if (time()%10 == 0): 
        ff = end - start