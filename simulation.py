import random, sys
random.seed(42)
from person import Person
from logger import Logger
from virus import Virus

class Simulation(object):
    ''' Main class that will run the herd immunity simulation program.
    Expects initialization parameters passed as command line arguments when file is run.

    Simulates the spread of a virus through a given population.  The percentage of the
    population that are vaccinated, the size of the population, and the amount of initially
    infected people in a population are all variables that can be set when the program is run.
    '''
    def __init__(self, pop_size, vacc_percentage, virus, initial_infected=1):

        ''' Logger object logger records all events during the simulation.
        Population represents all Persons in the population.
        The next_person_id is the next available id for all created Persons,
        and should have a unique _id value.
        The vaccination percentage represents the total percentage of population
        vaccinated at the start of the simulation.
        You will need to keep track of the number of people currently infected with the disease.
        The total infected people is the running total that have been infected since the
        simulation began, including the currently infected people who died.
        You will also need to keep track of the number of people that have die as a result
        of the infection.

        All arguments will be passed as command-line arguments when the file is run.
        HINT: Look in the if __name__ == "__main__" function at the bottom.
        '''
        self.vacc_count = 0
        self.vacc_saves = 0
        self.vacc = vacc_percentage * pop_size
        self.vacc_percentage = vacc_percentage
        self.file_name = "{}_simulation_pop_{}_vp_{}_infected_{}.txt".format(virus_name, pop_size, vacc_percentage, initial_infected)
        logger = Logger(self.file_name)
        self.virus = virus # Virus object
        self.pop_size = pop_size # Int
        self.initial_infected = initial_infected # Int
        self.logger = logger
        self.total_infected = 0 # Int
        self.current_infected = 0 # Int
        self.total_dead = 0 # Int
        self.newly_infected = []
        self.population = self._create_population(self.initial_infected) # List of Person objects

    def _create_population(self, initial_infected):

        '''This method will create the initial population.
            Args:
                initial_infected (int): The number of infected people that the simulation
                will begin with.

            Returns:
                list: A list of Person objects.

        '''
        output = []
        for x in range(self.pop_size):
            if self.initial_infected > 0:
                person = Person(x, False, self.virus.name)
                output.append(person)
                self.newly_infected.append(person._id)
                self.initial_infected -= 1
                self.total_infected += 1
            elif self.vacc > 0:
                person = Person(x, True, None)
                output.append(person)
                self.vacc -= 1
                self.vacc_count += 1
            else:
                person = Person(x, False, None)
                output.append(person)
        self.logger.write_metadata(self.pop_size, self.vacc_percentage, self.virus.name, self.virus.mortality_rate, self.virus.repro_rate)
        return output

    def _simulation_should_continue(self):
        ''' The simulation should only end if the entire population is dead
        or everyone is vaccinated.

            Returns:
                bool: True for simulation should continue, False if it should end.
        '''
        if self.vacc_count + self.total_dead >= self.pop_size:
            return False
        print(self.vacc_count + self.total_dead)
        return True

    def run(self):
        ''' This method should run the simulation until all requirements for ending
        the simulation are met.
        '''
        time_step_counter = 0
        while self._simulation_should_continue():
            self.time_step()
            time_step_counter += 1
        print('The simulation has ended after {} turns.'.format(time_step_counter))
        print('Total Death percentage: {}'.format((self.total_dead/self.pop_size) * 100))
        print('Percent Infected: {}'.format((self.total_infected/self.pop_size) * 100))
        print('Vaccination saves: {}'.format(self.vacc_saves))

    def time_step(self):
        ''' This method should contain all the logic for computing one time step
        in the simulation.

        This includes:
            1. 100 total interactions with a randon person for each infected person
                in the population
            2. If the person is dead, grab another random person from the population.
                Since we don't interact with dead people, this does not count as an interaction.
            3. Otherwise call simulation.interaction(person, random_person) and
                increment interaction counter by 1.
            '''
        interactions = 0
        interacted = []
        same = True
        for x in self.population:
            if x.is_alive:
                if not x.is_vaccinated:
                    if x.infection == self.virus.name:
                        while interactions < 100:
                            rand = self.population[random.randint(0, len(self.population)-1)]
                            while same:
                                if rand not in interacted:
                                    interacted.append(rand)
                                    same = False
                                else:
                                    rand = self.population[random.randint(0, len(self.population)-1)]
                            if rand.is_alive:
                                interactions += 1
                                self.interaction(x, rand)
            interacted = []
            interactions = 0

        self.kill_infected()
        self._infect_newly_infected()


    def interaction(self, person, random_person):
        '''This method should be called any time two living people are selected for an
        interaction. It assumes that only living people are passed in as parameters.

        Args:
            person1 (person): The initial infected person
            random_person (person): The person that person1 interacts with.
        '''
        # Assert statements are included to make sure that only living people are passed
        # in as params
        if not random_person.is_vaccinated:
            if not random_person.infection == self.virus.name:
                if random.random() < self.virus.repro_rate:
                    self.newly_infected.append(random_person._id)
                    self.logger.log_interaction(person, random_person, False, False, True)
                else:
                    self.logger.log_interaction(person, random_person, False, False, False)
                    self.vacc_count += 1
            else:
                self.logger.log_interaction(person, random_person, True, False, False)
        else:
            self.logger.log_interaction(person, random_person, False, True, False)
            self.vacc_saves += 1


    def _infect_newly_infected(self):
        ''' This method should iterate through the list of ._id stored in self.newly_infected
        and update each Person object with the disease. '''
        for x in self.newly_infected:
            for i in self.population:
                if i._id == x:
                    i.infection = self.virus.name
                    self.total_infected += 1
                    self.current_infected += 1
        self.newly_infected = []

    def kill_infected(self):
        subject = None
        for i in self.population:
            if i.infection == self.virus.name:
                subject = i
            if subject.is_alive:
                if not subject.is_vaccinated:
                    if random.random() < self.virus.mortality_rate:
                        subject.is_alive = False
                        self.logger.log_infection_survival(subject, True)
                        self.total_dead += 1
                        subject.infection = None
                        self.current_infected -= 1
                    else:
                        subject.is_vaccinated = True
                        self.logger.log_infection_survival(subject, False)
                        subject.infection = None
                        self.vacc_count += 1

if __name__ == "__main__":
    params = sys.argv[1:]
    virus_name = str(params[0])
    repro_num = float(params[1])
    mortality_rate = float(params[2])

    pop_size = int(params[3])
    vacc_percentage = float(params[4])

    if len(params) == 6:
        initial_infected = int(params[5])
    else:
        initial_infected = 1

    virus = Virus(virus_name, repro_num, mortality_rate)
    sim = Simulation(pop_size, vacc_percentage, virus, initial_infected)

    sim.run()
