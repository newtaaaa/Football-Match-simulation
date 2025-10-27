Each simulation is influenced by player input data, with their shooting, passing, defense, and speed skills measured on a scale of 0 to 100. Each composition is a graph, and the edges are cut as
players move too far apart. A pass is only possible if an edge connects two players (the higher the passing skill, the further apart the players can be), so players tend to want to 
move closer together to connect when they move too far apart. The Astar strategy consists of searching for the shortest passing path to the goal, as in a classic graph path. 

