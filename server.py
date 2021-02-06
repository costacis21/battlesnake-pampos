import os
import random
import pprint

import cherrypy

"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""


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

        print("START")
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def get_closest_food(self):
      data = cherrypy.request.json

     
      
      d=[]
      for food in data["board"]["food"]:
        youX = data["you"]["head"]["x"]
        foodX = food['x']
        youY = data["you"]["head"]["y"]
        foodY = food['y']

        curD = ( ( ( ( foodX - youX)**2 ) + ( (foodY - youY)**2) ) ** (1/2) )
        d.append((int(curD)))

      minIndex = d.index(min(d))
      

      print(minIndex)
      return data["board"]["food"][minIndex]

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def get_snake_obstacles(self):
      data = cherrypy.request.json

      obstacles = []

      for snake in data["board"]["snakes"]:
        for part in snake["body"]:
          obstacles.append(part)
        head_x = snake["head"]["x"]
        head_y = snake["head"]["y"]
        obstacles.append({"x": head_x+1, "y": head_y})
        if(head_y-1>0):
          obstacles.append({"x": head_x, "y": head_y-1})
        if(head_x-1>0):
          obstacles.append({"x": head_x-1, "y": head_y})
        obstacles.append({"x": head_x, "y": head_y+1})


# remove possible duplicates
      seen = set()
      new_l = []
      for d in obstacles:
        t = tuple(d.items())
        if t not in seen:
          seen.add(t)
          new_l.append(d)
        else:
          print("DUPLICATE MALAKA")
          print(t)
      obstacles = new_l.copy()



      print(obstacles)


      """
      example, list of dicts

      [{'x': 1, 'y': 10}, {'x': 1, 'y': 9}, {'x': 1, 'y': 9}, ...]

      """


        


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        # TODO: Use the information in cherrypy.request.json to decide your next move.
        data = cherrypy.request.json

        # Choose a random direction to move in
        possible_moves = ["up", "down", "left", "right"]
        move = "left"
        self.get_snake_obstacles()

        if (data["you"]["head"]["x"] == 0):
          move = "up"
          if (data["you"]["head"]["y"]==0):
            return {"move": move}

        if(data["you"]["head"]["y"] == data["board"]["height"]-1):
          move = "right"

        if(data["you"]["head"]["x"] == data["board"]["width"]-1):
          move = "down"
        
        if(data["you"]["head"]["y"] == 0):
          move = "left"



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
 