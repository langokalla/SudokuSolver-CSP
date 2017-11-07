
import copy
import itertools


class CSP:
    def __init__(self):
        # self.variables is a list of the variable names in the CSP
        self.variables = []

        # self.domains[i] is a list of legal values for variable i
        self.domains = {}

        # self.constraints[i][j] is a list of legal value pairs for
        # the variable pair (i, j)
        self.constraints = {}

    def add_variable(self, name, domain):
        """Add a new variable to the CSP. 'name' is the variable name
        and 'domain' is a list of the legal values for the variable.
        """
        self.variables.append(name)
        self.domains[name] = list(domain)
        self.constraints[name] = {}

    def get_all_possible_pairs(self, a, b):
        """Get a list of all possible pairs (as tuples) of the values in
        the lists 'a' and 'b', where the first component comes from list
        'a' and the second component comes from list 'b'.
        """
        return itertools.product(a, b)

    def get_all_arcs(self):
        """Get a list of all arcs/constraints that have been defined in
        the CSP. The arcs/constraints are represented as tuples (i, j),
        indicating a constraint between variable 'i' and 'j'.
        """
        return [ (i, j) for i in self.constraints for j in self.constraints[i] ]

    def get_all_neighboring_arcs(self, var):
        """Get a list of all arcs/constraints going to/from variable
        'var'. The arcs/constraints are represented as in get_all_arcs().
        """
        return [ (i, var) for i in self.constraints[var] ]

    def add_constraint_one_way(self, i, j, filter_function):
        """Add a new constraint between variables 'i' and 'j'. The legal
        values are specified by supplying a function 'filter_function',
        that returns True for legal value pairs and False for illegal
        value pairs. This function only adds the constraint one way,
        from i -> j. You must ensure that the function also gets called
        to add the constraint the other way, j -> i, as all constraints
        are supposed to be two-way connections!
        """
        if not j in self.constraints[i]:
            # First, get a list of all possible pairs of values between variables i and j
            self.constraints[i][j] = self.get_all_possible_pairs(self.domains[i], self.domains[j])

        # Next, filter this list of value pairs through the function
        # 'filter_function', so that only the legal value pairs remain
        self.constraints[i][j] = filter(lambda value_pair: filter_function(*value_pair), self.constraints[i][j])

    def add_all_different_constraint(self, variables):
        """Add an Alldiff constraint between all of the variables in the
        list 'variables'.
        """
        for (i, j) in self.get_all_possible_pairs(variables, variables):
            if i != j:
                self.add_constraint_one_way(i, j, lambda x, y: x != y)

    def backtracking_search(self):
        """This functions starts the CSP solver and returns the found
        solution.
        """
        # Make deep copy.
        assignment = copy.deepcopy(self.domains)

        # Run AC-3 on all constraints in the CSP, to weed out all of the
        # values that are not arc-consistent to begin with
        self.inference(assignment, self.get_all_arcs())

        # Call backtrack with the partial assignment 'assignment'
        return self.backtrack(assignment)

    def backtrack(self, assignment):
        """The function 'Backtrack' from the pseudocode in the
        textbook.

        The function is called recursively, with a partial assignment of
        values 'assignment'. 'assignment' is a dictionary that contains
        a list of all legal values for the variables that have *not* yet
        been decided, and a list of only a single value for the
        variables that *have* been decided.

        When all of the variables in 'assignment' have lists of length
        one, i.e. when all variables have been assigned a value, the
        function should return 'assignment'. Otherwise, the search
        should continue. When the function 'inference' is called to run
        the AC-3 algorithm, the lists of legal values in 'assignment'
        should get reduced as AC-3 discovers illegal values.

        IMPORTANT: For every iteration of the for-loop in the
        pseudocode, you need to make a deep copy of 'assignment' into a
        new variable before changing it. Every iteration of the for-loop
        should have a clean slate and not see any traces of the old
        assignments and inferences that took place in previous
        iterations of the loop.
        """
        # Find out if board is completed.
        # That is when all domains has length one.
        complete = True
        for x in assignment.keys():
            if len(assignment[x]) != 1:
                complete = False
                break

        # Return assignment if complete.
        if complete:
            return assignment

        # Select an unassigned variable
        unassigned = self.select_unassigned_variable(assignment)

        # Iterate all values in unassigned's domain.
        # Make a deep compy of assignment and add value
        # to unassigned's domain in the copy.
        for value in assignment[unassigned]:
            domain_copy = copy.deepcopy(assignment)
            domain_copy[unassigned] = [value]
            # Fetch all arcs and put them in list (used as queue).
            queue = self.get_all_arcs()
            # If we have a interference, set new result to recursive backtracking.
            if self.inference(domain_copy, queue):
                result = self.backtrack(domain_copy)
                # If we are finished, return the result.
                if result:
                    return result
        # Not finished, return result as False.
        return False

    def select_unassigned_variable(self, assignment):
        """The function 'Select-Unassigned-Variable' from the pseudocode
        in the textbook. Should return the name of one of the variables
        in 'assignment' that have not yet been decided, i.e. whose list
        of legal values has a length greater than one.
        """
        # Select the first, unassigned variable we find;
        # that is when the domain has more than one item.
        for key, val in assignment.iteritems():
            if len(val) > 1:
                return key

    def inference(self, assignment, queue):
        """The function 'AC-3' from the pseudocode in the textbook.
        'assignment' is the current partial assignment, that contains
        the lists of legal values for each undecided variable. 'queue'
        is the initial queue of arcs that should be visited.
        """
        # Run while we have a non-empty queue.
        while queue:
            # Pop from start in queue.
            i, j = queue.pop(0)
            # If revised is success, proceed.
            if self.revise(assignment, i, j):
                # If the domain is empty, return negative interference.
                if len(assignment[i]) == 0:
                    return False
                # Get all neighbours of i, if j isn't there, append it to queue.
                neighbors = self.get_all_neighboring_arcs(i)
                for n in neighbors:
                    if j not in n[0]:
                        queue.append((n[0], i))
        return True

    def revise(self, assignment, i, j):
        """The function 'Revise' from the pseudocode in the textbook.
        'assignment' is the current partial assignment, that contains
        the lists of legal values for each undecided variable. 'i' and
        'j' specifies the arc that should be visited. If a value is
        found in variable i's domain that doesn't satisfy the constraint
        between i and j, the value should be deleted from i's list of
        legal values in 'assignment'.
        """
        # Get constraints between two cells.
        constraints = self.constraints[i][j]
        # Set revised to False.
        revised = False
        # Iterate through i's domain.
        for x in assignment[i]:
            # Set variable satisfied. Check if revising is satisfied.
            satisfied = False
            for y in assignment[j]:
                # Iterate through y's domain.
                # If x and y is satisfied in constraints,
                # break when satisfied.
                if (x, y) in constraints:
                    satisfied = True
                    break
            # If the revision is not satisfied, remove i from x's domain,
            # and set process to succeeded.
            if not satisfied:
                assignment[i].remove(x)
                revised = True
        return revised
