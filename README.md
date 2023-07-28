# Simulation of Bystander Effect in Python

## Project summary

The bystander effect is a theory that says that individuals are less likely to
offer help to a victim in presence of other individuals. A number of real world
experiments conducted in controlled and green field environments using recordings
from security proved this theory to have a solid background.

Having a formula that describes the behavior of individuals makes it possible to
use simulations to predict the reaction of people in various situations. This repo
uses a modified version of a known [formula](https://www.guokr.com/article/6172/)
that accounts for two additional parameters:

- **individual probability** of **not calling** help  
- distance between an individual and an event  

The project is based on a simulation university that runs itself and does not
require a user to explicitly define the parameters of interactions between the
agents. The practical importance of this simulation is that it can be used in
city planning, legislation improvement and placement of city cameras.

## Explanation of how it works

The simulation uses **OOP** concept to run a network of agent which represent
bystanders and events and exist in an instance of a universe described by two
dimensions. The agents are placed randomly in the world when a simulation starts.

A simulation runs for a certain time defined by a number of steps (think of them as minutes).
At each step a bystander evaluates its distance to an event and to other bystanders.
The proximity to the event increases the probability of calling help. Bystanders
surrended closely by other agents most likely will not call police. 

At the end of a step a bystander moves. The direction of the movement is selected
at random until all conditions are met or until the number of iterations reaches
a certain value -- then a bystander does not move. A bystander won't move if 
their position is further away from an event then the hearing distance.

Conditions for moving a bystander:

- do not move closer to an event then you are now;  
- do not cross the border of the universe;  

![Simulation output](https://github.com/GeorgyMakarov/bystander_effect/blob/main/record_screen.gif)  

## Sources

[Practical Time Series Analysis](https://www.oreilly.com/library/view/practical-time-series/9781492041641/ch04.html)  
[Object-Oriented Programming](https://realpython.com/python3-object-oriented-programming/)  
[Bystander Effect on Wikipedia](https://en.wikipedia.org/wiki/Bystander_effect)  
[Bystander Effect on Cornell University](https://blogs.cornell.edu/info2040/2016/10/25/the-bystander-effect/)  
