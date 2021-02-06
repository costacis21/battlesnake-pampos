import os
import random
from pprint import pprint
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.heuristic import manhattan, octile
from pathfinding.core.grid import Grid
import numpy as np

import cherrypy

"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""

# given current position and next, find which move will lead us there
def choose_move(curr, next):
  if next[0] != curr[0]:
    x_diff = next[0] - curr[0]
    if x_diff > 0:
      return "right"
    else:
      return "left" 

  if next[1] != curr[1]:
    y_diff = next[1] - curr[1]
    if y_diff > 0:
      return "up"
    else:
      return "down"
  


def dict_to_list(dict):
      # example: dict = {'x' : 3, 'y' : 5}
      return (dict['x'], dict['y'])

class Battlesnake(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        # This function is called when you register your Battlesnake on play.battlesnake.com
        # It controls your Battlesnake appearance and author permissions.
        # TIP: If you open your Battlesnake URL in browser you should see this data
        return {
            "apiversion": "1",
            "author": "",  # TODO: Your Battlesnake Username
            "color": "#888888",  # TODO: Personalize
            "head": "default",  # TODO: Personalize
            "tail": "default",  # TODO: Personalize
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        data = cherrypy.request.json

        pprint(data)
        print("START")
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def get_closest_food(self, data):
         
      d=[]
      for food in data["board"]["food"]:
        youX = data["you"]["head"]["x"]
        foodX = food['x']
        youY = data["you"]["head"]["y"]
        foodY = food['y']

        curD = ( ( ( ( foodX - youX)**2 ) + ( (foodY - youY)**2) ) ** (1/2) ) # 0.5 ????
        d.append((int(curD)))

      minIndex = d.index(min(d))
      

      print(minIndex)
      return data["board"]["food"][minIndex]

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def obstacles(self, data):
      height = data['board']['height']
      width = data['board']['width']

      obstacles = list()

      snakes = data["board"]["snakes"]

      for snake in snakes:
        for part in snake['body']:
          if dict_to_list(part) not in obstacles:
            obstacles.append(dict_to_list(part))
        if not (snake["id"]==data["you"]["id"]):
          head = dict_to_list(snake['head'])

          if head[0] + 1 < width:
            obstacles.append((head[0]+1, head[1]))

          if head[0] - 1 >= 0:
            obstacles.append((head[0]-1, head[1]))

          if head[1] + 1 < height:
            obstacles.append((head[0], head[1]+1))

          if head[1] - 1 >= 0:
            obstacles.append((head[0], head[1]-1))

      obstacles = set(obstacles) # remove duplicates

      # your_head = dict_to_list(data['you']['head'])
      # your_body_list = data['you']['body']
      # your_body_coordinates = list()
      # your_next_coordinates = list()

      # for elt in your_body_list:
      #   your_body_coordinates.append(dict_to_list(elt))

      # if your_head[0] + 1 < width:
      #     your_next_coordinates.append((your_head[0]+1, your_head[1]))

      # if your_head[0] - 1 >= 0:
      #   your_next_coordinates.append((your_head[0]-1, your_head[1]))

      # if your_head[1] + 1 < height:
      #   your_next_coordinates.append((your_head[0], your_head[1]+1))

      # if your_head[1] - 1 >= 0:
      #   your_next_coordinates.append((your_head[0], your_head[1]-1))

      #remove your head's next available moves if that's its body
      # your_next_possible_coordinates = set()
      # for elt in your_next_coordinates:
      #   if elt not in your_body_coordinates:
      #     your_next_possible_coordinates.add(elt)

      # obstacles = obstacles - your_next_possible_coordinates
      # obstacles = obstacles - set(your_head)
      return obstacles


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        # TODO: Use the information in cherrypy.request.json to decide your next move.
        data = cherrypy.request.json
        width = data['board']['width']
        height = data['board']['height']

        grid = np.ones((height,width), dtype=np.int8)

        obstacles = self.obstacles(data)
        print(obstacles)

        food = self.get_closest_food(data)
        print("food")
        head_x = data['you']['head']['x']
        head_y = data['you']['head']['y']
        head = (head_x, head_y)
        food = dict_to_list(food)
        print(food)
        print("head")
        print(head)

        for elt in obstacles:
          # mark where are the obstacles
          if list(elt) != list(head):
            grid[elt[1], elt[0]] = 0

        # FOR VISUAL PURPOSES ONLY
        # CHANGING VALUE WILL CHANGE THE WEIGHT
        # mark where is the food
        #grid[(height-1)-food[1], food[0]] = 2
        # FOR VISUAL PURPOSES ONLY
        # CHANGING VALUE WILL CHANGE THE WEIGHT
        #mark where is the head
        #grid[(height-1)-head[1], head[0]] = 5

        print(data['turn'])
        print(grid)

        # if data["you"]["health"] <20:
        
        #lets choose a move
        finder = AStarFinder(heuristic=manhattan)
        grid = Grid(matrix = grid)
        start = grid.node(head[0], head[1])
        end = grid.node(food[0], food[1])
        path, runs = finder.find_path(start, end, grid)
        next_coordinate = path[1]
        print("path:")
        print(path)
        print(" next coordinate is :")
        print(next_coordinate)

        #now we need to decide what move will take the snake to the next coordinate
        move = choose_move(head, next_coordinate)
        # else:
        #   # move = "left"
        #   if (data["you"]["head"]["x"] == 0):
        #     move = "up"
        #     if (data["you"]["head"]["y"]==0):
        #       return {"move": move}

        #   if(data["you"]["head"]["y"] == data["board"]["height"]-1):
        #     move = "right"

        #   if(data["you"]["head"]["x"] == data["board"]["width"]-1):
        #     move = "down"

        #   if(data["you"]["head"]["y"] == 0):
        #     move = "left"

        print(f"MOVE: {move}")
        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json

        print("END")
        return "ok"


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
