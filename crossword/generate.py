import sys
import copy
from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        domains = copy.deepcopy(self.domains)
        for v in domains:
            for w in domains[v]:
                length = v.length
                if len(w) != v.length:
                    self.domains[v].remove(w)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        signal = False
        removed_words = []
        if self.crossword.overlaps[x, y]:
            (i, j) = self.crossword.overlaps[x, y]
            character_set = set()
            for w in self.domains[y]:
                character_set.add(w[j])
            for w in self.domains[x]:
                if w[i] not in character_set:
                    removed_words.append(w)
                    signal = True
            for w in removed_words:
                self.domains[x].remove(w)
        return signal

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        arc_list = list(self.crossword.overlaps.keys())
        if arcs is not None:
            index = [i for i, x in enumerate(arc_list) if x == arcs]
            arc_list = arc_list[index:, 0:index[0] - 1]
        while len(arc_list):
            if self.revise(arc_list[0][0], arc_list[0][1]):
                for v in self.crossword.neighbors(arc_list[0][0]):
                    arc_list.append((v, arc_list[0][0]))
            arc_list = arc_list[1:]
        for v in self.domains:
            if len(self.domains[v]) == 0:
                return False
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for v in self.domains:
            if v not in assignment.keys():
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # correct length
        length_signal = True
        for key, value in assignment.items():
            if key.length != len(value):
                length_signal = False
                break
        # word distinct between var
        if len(set(assignment.values())) == len(list(assignment.values())):
            value_distinct = True
        else:
            value_distinct = False
        # no conflict in overlaps
        no_conflicts = True
        for k1 in assignment:
            for k2 in self.crossword.neighbors(k1):
                (i, j) = self.crossword.overlaps[k1, k2]
                if k2 in assignment:
                    if assignment[k1][i] != assignment[k2][j]:
                        no_conflicts = False
                        break
        if length_signal and value_distinct and no_conflicts:
            return True
        else:
            return False

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        word = list(set(self.domains[var]) - set(assignment.values()))
        count = dict()
        for w in word:
            n = 0
            neighbors = self.crossword.neighbors(var)
            for v in neighbors:
                if w in self.domains[v]:
                    n += 1
            count[w] = n
        return [i for (i, j) in (sorted(count.items(), key=lambda item: item[1]))]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = set(self.domains.keys()) - set(assignment.keys())
        count = dict()
        degrees = dict()
        for k in unassigned:
            count[k] = len(self.domains[k])
            degrees[k] = len(self.crossword.neighbors(k))
        unassigned_var = [k for k, v in count.items() if
                          v == min(count.values()) and degrees[k] == max(degrees.values())]
        return unassigned_var[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        unassigned_variable = self.select_unassigned_variable(assignment)
        domain = self.order_domain_values(unassigned_variable, assignment)
        for word in domain:
            new_assignment = assignment.copy()
            new_assignment[unassigned_variable] = word
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
        return None


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
