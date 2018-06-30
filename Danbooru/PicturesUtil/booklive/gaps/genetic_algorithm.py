
from operator import attrgetter
from gaps import image_helpers
from gaps.selection import roulette_selection
from gaps.crossover import Crossover
from gaps.individual import Individual
from gaps.image_analysis import ImageAnalysis
from gaps.plot import Plot
from gaps.progress_bar import print_progress
import random

class GeneticAlgorithm(object):

    TERMINATION_THRESHOLD = 100
    MUTATION_PROBABILITY = 0.1

    def __init__(self, image, piece_size, population_size, generations, eliteFrac=0.10):
        self._image = image
        self._piece_size = piece_size
        self._generations = generations
        pieces, rows, columns = image_helpers.flatten_image(image, piece_size, indexed=True)
        self._elite_size = int(len(pieces)*eliteFrac)
        self._population = [Individual(pieces, rows, columns) for _ in range(population_size)]
        self._pieces = pieces

    def start_evolution(self, verbose):
        print(("=== Pieces:      {}\n".format(len(self._pieces))))

        if verbose:
            plot = Plot(self._image)

        ImageAnalysis.analyze_image(self._pieces)

        fittest = None
        best_fitness_score = float("-inf")
        termination_counter = 0

        for generation in range(self._generations):
            print_progress(generation, self._generations - 1,
                           prefix="=== Solving puzzle: ",
                           suffix = ' | '+str(best_fitness_score))

            new_population = []

            # Elitism
            elite = self._get_elite_individuals(elites=self._elite_size)

            selected_parents = roulette_selection(self._population, elites=self._elite_size)

            for first_parent, second_parent in selected_parents:
                crossover = Crossover(first_parent, second_parent)
                crossover.run()
                child = crossover.child()
                new_population.append(child)
                
            tomutate = new_population
            newMutatedPop = []
            while tomutate:
                child= tomutate.pop(0)
                if random.random() < self.MUTATION_PROBABILITY:
                    child.mutate()
                    tomutate.append(child)
                else:
                    newMutatedPop.append(child)
            self._population = newMutatedPop
            self._population.extend(elite)

            fittest = self._best_individual()

            if fittest.fitness <= best_fitness_score:
                termination_counter += 1
            else:
                best_fitness_score = fittest.fitness

            if not self.MUTATION_PROBABILITY and termination_counter == self.TERMINATION_THRESHOLD:
                print("\n\n=== GA terminated")
                print(("=== There was no improvement for {} generations".format(self.TERMINATION_THRESHOLD)))
                return fittest

            if verbose:
                plot.show_fittest(fittest.to_image(), "Generation: {} / {}".format(generation + 1, self._generations))
        return fittest

    def _get_elite_individuals(self, elites):
        """Returns first 'elite_count' fittest individuals from population"""
        return sorted(self._population, key=attrgetter("fitness"))[-elites:]

    def _best_individual(self):
        """Returns the fittest individual from population"""
        return max(self._population, key=attrgetter("fitness"))
