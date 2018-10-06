# Hybrid vehicles: real-time management of motor coupling
The aim of this project was to determine how to balance thermal and electric motors in a hybrid vehicle in order to limit petrol consumption. The algorithms were tested on the New European Driving Cycle (NEDC) developed in 2014 using the characteristics of a Renault Clio iii (2) collection 1.2 16v 75 zen 3p (Citadines).

## Why use a hybrid vehicle?
|               | Combustion engine       | Electric motors                     |
|---------------|-------------------------|-------------------------------------|
|__Advantages__ | Cheap                   | Low pollution and low noise         |
|               | Efficient at high speed | Efficient at low speeds             |
|               |                         | Instant start                       |
|               |                         | Long motor life cycle (> 100000 km) |
|__Disadvantages __| Pollution               | Low battery autonomy (100km)        |
|               | Loud                    | Low battery life                    |

Combining a combustion engine with an electric motor gets the best of both worlds if done well.

In particular, whilst electric motors are efficient at low speeds, combustion engines are better at high speeds as evidence by the following diagram displaying energy consumption as a function of the applied torque and rpm. Generally speaking, energy consumption is an increasing function of torque and thus of speed assuming the driver stays between 2000 and 3000 rpm as recommended by car manufacturers.

Insert IMAGE

## Algorithm 1 - rule-based workload distribution
Here we designed a real-time algorithm for balancing the power between the thermal and electic motors. The exact driving path is not known beforehand.

### Specifications
#### Objectives
Reduce energy consumption by 30% on a unknown trip.

#### Constraints
* Battery for electric motor needs to be recharged
* Battery adds an additional 80 kg to vehicle weight

### Algorithm design

#### Rules:
1. At low speed (v < 50 km/h) – pur electric mode: if possible the electric motor alone is used to avoid the low efficiency regions of the thermal motor
2. During acceleration - boost mode: both motors work together
3. At high speed - thermal mode or recharge mode: only the thermic motor operates. If possible (and necessary), the motor can work in over-regime to charge the battery
4. Braking - regenerative braking: kinetic energy is used to recharge battery

* Battery charge/decharge: battery level cannot go below 10% except in acceleration phase

#### Results
We tested our algorithm on the NEDC.

INSERT IMAGE

The numbers indicate the type of rule being used at the time. At low speeds, the electric motor (blue) is used most of the time whereas the combustion engine (red) takes over at higher speeds. The electric motor exerces a negative torque during deceleration in order to recharge the battery. Interestingly, in some cases (2), the combustion engine gains from working in a higher regime and recharges the battery at the same time as the electric motor counteracts excess torque.

To understand how this algorithm saves fuel we compared the energy consumption map of the combustion engine in the case of a classic car and in the case of a hybrid vehicle using our algorithm.

INSERT IMAGE


In hybrid mode, the high energy consumption areas are avoided whilst the engine seems to be working more regularly in high efficiency zones (blue). __Overall, using this algorithm, we save 30% of fuel on the NEDC.__

## Algorithm 2 - Greedy algorithm for a known itinerary
We then considered the case where the itinerary was known in advance. This is the case for instance when using GPS.

We defined a new metric called *coupling efficacy* as the ratio of the possible savings in fuel energy over the required electric battery consumption. A high efficacy means we stand to gain a lot from using the battery at that point. COnverserly, a low efficacy means using the electric motor does little to help energy consumption.

The coupling efficacy was calculated at each point of the itinerary and we then applied a greedy algorithm to determine at which points we should use the electric motor.

INSERT IMAGE

### Results
Here we show the calculated *coupling efficacy* as well as the torque distribution between both motors.

INSERT IMAGE

INSERT IMAGE

As in our decision based algorithm, the electric motor is essentially used at low speeds. However, the combustion engine also kicks in at certain points to reduce battery consumption. In addition, at high speeds, the electric motor goes into regenerative mode in order to have sufficient battery to help out during the accelerations. __Overall, using this algorithm, we save 38% of fuel on the NEDC.__ 

Although this algorithm outperforms our decision based one, its similar pattern at high and low speeds validates many of our initial assumptions. One key point as well is that the computation time for this algorithm is by far higher than the previous algorithm. Indeed the algorithm needs to go over all timepoints before being able to take any decision. For a 100km journey, our algorithm typically takes 1mn to run (compared with only a few seconds using the decision based algorithm).

## Conclusion
Both our algorithms show the potential of hybrid vehicles for limiting fuel consumption. The rule-based algorithm can be applied for everyday unplanned trips and achieve 30% energy savings. The greedy algorithm outperforms by approximately 25% the rule-based one but requires knowing the journey, as well as the specific acceleration and breaking points in advance. This data is very hard to predict in advance which suggests that in most settings the rule-based algorithm should be used.

