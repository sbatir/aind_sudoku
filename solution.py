assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'
#reverse columns" 
revcol = '987654321'

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

#Defining essential units 
boxes = cross(rows,cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
# Incorporate diagonal constraint as an additional "unit" 
diag1_units = [r1+c1 for r1,c1 in zip(rows, cols)]
diag2_units = [r2+c2 for r2,c2 in zip(rows, revcol)]
# List of lists = Mother containing the additional constraint. 
motherDiagonal = [diag1_units, diag2_units]
unitlist = row_units + column_units + square_units  + motherDiagonal

#unitlist = row_units + column_units + square_units <- Previous implementation without diagonal constraint. 

# Use generator expression for dictionary because iterating through all boxes only once. 
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    #Values is the most important output, since it is passed into nearly all of our functions. Values= Dictionary{Box ID i.e. A1/C2: String of values i.e. '1234'}
    return values


        
def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Store all possible naked twins as {Twin Pair String: Possible Box/Units with Twin Pair} 
    nakedTwinDict = {}
    
    # Eliminate the naked twins as possibilities for their peers
    for unit in unitlist:
        #Dictionary twins: {Key is'Twin Pair as string',: Value is the box identity i.e. 'A7' of possible twins}
        twins = {}
        for box in unit: 
            if len(values[box]) ==2: #Exclusively examine if you have naked twins! 
                if values[box] in twins:
                    twins[values[box]].append(box)
                else:
                    twins[values[box]] = [box]

        for key in twins:
           # For every twin pair, either append the unit in question if it is truly a pair, or set the key of a potential twin pair equal to the value of an entire unit. 
            if len(twins[key]) ==2:
                if key in nakedTwinDict:
                    nakedTwinDict[key].append(unit)
                else:
                    nakedTwinDict[key] = [unit]

                    
    #NakedTwinDict stores {Twin Pair: List of Possible Boxes with Twin Pairs}              
    for key in nakedTwinDict:
        firstTwin = key[0]
        secondTwin = key[1]
        #Extract the first and second Twins, to then remove in the second loop below. 
        for unit in nakedTwinDict[key]:
            for box in unit:
                if values[box] != key:
                    #The luxury meat of code, where each twin component is removed from the possible values of the box through the replace(old, new) function on values[box]. 
                    assign_value(values, box, values[box].replace(firstTwin, ''))
                    assign_value(values, box, values[box].replace(secondTwin, ''))
                                    
    return values
    

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    values = []
    all_digits = '123456789'
    for c in grid:
        if c == '.':
            #Replace '.' with all_digits
            values.append(all_digits)
        elif c in all_digits:
            #Add each component to list of values. 
            values.append(c)
    assert len(grid) == 81
    return dict(zip(boxes,values))
  

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF':
            print(line)
    print

def eliminate(values):
    solved_values = [box for box in values.keys() if len(values[box]) ==1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
    return values

def only_choice(values):
    for unit in unitlist:
        #For each list of "unit", detect dplaces. Some units will only have 1 value in dplace, while others will have several values in dplace. 
        for digit in '123456789':
            #dplaces is a list comprehension
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                #converts string of digit to list of string. Why? List comprehension for dplace. 
                values[dplaces[0]] = digit
    return values

def reduce_puzzle(values):
    #Once the values (possible number output) are narrowed down to 1 for each key (box position), the value has been "solved." Store in a list comprehension. solved_values. 
    solved_values = [box for box in values.keys() if len(values[box]) ==1] 
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        #Run eliminate, only choice, and naked_twins to return values. 
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) ==1])
        stalled = solved_values_before == solved_values_after #Use this as the "stopping condition," When delta between before and after =0. 
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all(len(values[s]) == 1 for s in boxes):
        return values
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) >1)
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    values = search(values)
    return values

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(grid_values(diag_sudoku_grid))
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
