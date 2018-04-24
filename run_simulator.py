import pygame

from simulator import map, robot, OutsideBoundryError, SimulatorStatus
from algorithm import action
from settings import *

screen_height = grid_dimension[0] * WIDTH + grid_dimension[0] + 1
screen_width = grid_dimension[1] * HEIGHT + grid_dimension[1] + 1

map = map(grid_dimension)

for x,y in map.get_robot_init_place("robot_init.csv"):
    if not map.is_location_in_environment(x, y, grid_dimension):
        raise OutsideBoundryError('init robot (x, y) not in map!')
    map.grid[x][y] = ROBOT_AREA
    map.robots.append(robot(x, y))    # add robots

for x,y in map.get_blocks_init_place("blocks.csv"):
    if not map.is_location_in_environment(x, y, grid_dimension):
        raise OutsideBoundryError('init block (x, y) not in map!')
    map.grid[x][y] = BLOCK_AREA
    map.blocks.append((x, y))


# Initialize pygame
pygame.init()

# Set the HEIGHT and WIDTH of the screen
WINDOW_SIZE = [screen_width, screen_height]
screen = pygame.display.set_mode(WINDOW_SIZE)


# Set title of screen
pygame.display.set_caption("Frontier-based Unknown Environment Exploration")

# Loop until the user clicks the close button.
done = False
block = False
# Used to manage how fast the screen updates
clock = pygame.time.Clock()
simulator_status = SimulatorStatus()
# -------- Main Program Loop -----------
while not (done or block):
    # for event in pygame.event.get():  # User did something
    #     if event.type == pygame.QUIT:  # If user clicked close
    #         done = True  # Flag that we are done so we exit this loop
    #     else:
    #         break
    #     # elif event.type == pygame.MOUSEBUTTONDOWN:
    #     #     # User clicks the mouse. Get the position
    #     #     pos = pygame.mouse.get_pos()
    #     #     # Change the x/y screen coordinates to grid coordinates
    #     #     column = pos[0] // (WIDTH + MARGIN)
    #     #     row = pos[1] // (HEIGHT + MARGIN)
    #     #     # Set that location to one
    #     #     grid[row][column] = 4
    #     #     print("Click ", pos, "Grid coordinates: ", row, column)

    # Set the screen background
    screen.fill(BLACK)
    actions = action(map)
    real_action_this_interval = 0

    for i, robot_i in enumerate(map.robots):
        map.grid[robot_i.x][robot_i.y] = EXPLORATED_AREA
        
        real_action_this_interval += robot_i.move(map, action=actions[i])
        map.grid[robot_i.x][robot_i.y] = ROBOT_AREA

    for robot_i in map.robots:
        view_real_area_i = robot_i.view_real_area(map.blocks, map.grid_dimension)
        for j in view_real_area_i:
            map.grid[j[0]][j[1]] = EXPLORATED_AREA

    for robot_i in map.robots:
        map.grid[robot_i.x][robot_i.y] = ROBOT_AREA

    map.view_real_exploration_bounds()
    simulator_status.update_time()
    simulator_status.update_robot_route_length(real_action_this_interval)
    
    
    block = simulator_status.judge_blocking()
    done = simulator_status.judge_over(map)
    if done:
        simulator_status.update_status("success")
    print(simulator_status)  # for debug
    # Draw the grid
    for row in range(grid_dimension[0]):
        for column in range(grid_dimension[1]):
            color = GREY
            if map.grid[row][column] == ROBOT_AREA:
                color = RED
            elif map.grid[row][column] == BLOCK_AREA:
                color = BLACK
            elif map.grid[row][column] == EXPLORATED_AREA:
                color = WHITE
            elif map.grid[row][column] == EXPLORATED_BOUND:
                color = BLUE
            pygame.draw.rect(screen,
                             color,
                             [(MARGIN + WIDTH) * column + MARGIN,
                              (MARGIN + HEIGHT) * row + MARGIN,
                              WIDTH,
                              HEIGHT])

    # Limit to 60 frames per second
    clock.tick(CLOCK_TICK)

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

# Be IDLE friendly. If you forget this line, the program will 'hang'
# on exit.
pygame.quit()