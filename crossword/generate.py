import sys

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
                        w, h = draw.textsize(letters[i][j], font=font)
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
        for v in self.domains:
            tmp = self.domains[v].copy()
            for x in tmp:
                if len(x) != v.length :
                    self.domains[v].remove(x)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        changed = False
        overlap = self.crossword.overlaps[(x,y)]

        if overlap:
            words_x = self.domains[x].copy()
            for word_x in words_x:
                remove = True
                for word_y in self.domains[y]:
                    if word_x[overlap[0]] == word_y[overlap[1]]:
                        remove = False
                        break
                if remove:
                    self.domains[x].remove(word_x)
                    changed = True

        return changed

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if not arcs:
            queue = list(self.crossword.overlaps.keys())

        while queue:
            (x,y) = queue.pop()
            if self.revise(x,y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x):
                    if z != y:
                        queue.append((z,x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for v in self.domains.keys():
            if v not in assignment.keys():
                return False
        return True
            

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        for variable in assignment:
            # get all variables that have the same string value to check doubles
            keys = [k for k, v in assignment.items() if v == assignment[variable]]
            if len(keys) > 1:
                return False
            # check for length of word
            if len(assignment[variable]) != variable.length:
                return false
            # for the current variable, check if for an overlap, if the value is filled, the cell is ok
            neighbors = self.crossword.neighbors(variable)
            for variable2 in neighbors:
                if variable2 in assignment.keys():
                    overlap = self.crossword.overlaps[(variable, variable2)]
                    if assignment[variable][overlap[0]] != assignment[variable2][overlap[1]]:
                        return False
        return True

    def inconsistency(self, x, y, word_x, word_y):
        overlap = self.crossword.overlaps[(x, y)]
        if word_x[overlap[0]] != word_y[overlap[1]]:
            return True


    def number_ruled_out(self, assignment, var, word):
            neighbors = self.crossword.neighbors(var)
            not_assigned_neighbors = list(set(neighbors) - set(assignment.keys()))

            n = 0
            for var2 in not_assigned_neighbors:
                for word2 in self.domains[var2]:
                    if self.inconsistency(var, var2, word, word2):
                         n = n + 1
            return n
    
    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        tmp = list(self.domains[var].copy())
        return sorted(tmp, key=lambda x: self.number_ruled_out(assignment, var, x))

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        variables = list(set(self.domains.keys()) - set(assignment.keys()))
        sorted(variables, key=lambda x: (len(self.domains[x]), len(self.crossword.neighbors(x))))
        return variables[0]

    def recursive_backtrack(self, assignment, solution):

        if not self.consistent(assignment):
            return None
        if self.assignment_complete(assignment):
            solution.append(assignment)
            return assignment

        else:
            var = self.select_unassigned_variable(assignment)
            word_list = self.order_domain_values(var, assignment)
            for word in word_list:
                temp = assignment.copy()
                if word not in assignment.values():
                    temp[var] = word
                    self.recursive_backtrack(temp, solution)
                    if solution:
                        return solution[0]

    
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        temp = list()
        return self.recursive_backtrack(assignment, temp)


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
