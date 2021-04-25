import pygame
import random
import time
from itertools import cycle

# colors
BLACK           = (0, 0, 0)
DARKER_GREY     = (50, 50, 50)
DARK_GREY       = (100, 100, 100)
GREY            = (150, 150, 150)
LIGHT_GREY      = (200, 200, 200)
LIGHTER_GREY    = (220, 220, 220)
WHITE           = (255, 255, 255)

# pygame event.key:value mapping
keyMappings = {
    pygame.K_1: 1,
    pygame.K_2: 2,
    pygame.K_3: 3,
    pygame.K_4: 4,
    pygame.K_5: 5,
    pygame.K_6: 6,
    pygame.K_7: 7,
    pygame.K_8: 8,
    pygame.K_9: 9,
    pygame.K_BACKSPACE: ''
}

# pygame window 

WINDOW_HEIGHT = 500
WINDOW_WIDTH = 500

blockSize = 100 # size of the grid cell
blockBorder = 25

pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Arial', 60)

class Rect:
    def __init__(self, rect, position):
        self.rect = rect
        self.val = ''
        self.position = position
        self.horizontal = False
        self.textColor = BLACK

    def draw(self):
        pygame.draw.rect(SCREEN, self.color, self.rect)
        if self.val:
            self.drawVal(self.val)
            
    def highlight(self):
        self.color = self.colorPalette[0]

    def unhighlight(self):
        self.color = self.colorPalette[1]

    def drawVal(self, val):
        pygame.draw.rect(SCREEN, self.color, self.rect) # draw over any previous val

        text = font.render(str(val), True, self.textColor)
        if self.horizontal:
            text = pygame.transform.rotate(text, -90)
        text_rect = text.get_rect(center=(self.rect.center))
        SCREEN.blit(text, text_rect)

class Cell(Rect):
    def __init__(self, rect, position):
        super().__init__(rect, position)
        self.colorPalette = (DARK_GREY, LIGHT_GREY)
        self.color = self.colorPalette[1] # 0 == highlight color, 1 == unhighlighted color
        self.inequalities = {}
        self.isValid = None

    def setValidState(self, state):
        self.isValid = state

        if state == True or state == None:
            self.colorPalette = (DARK_GREY, LIGHT_GREY)
        elif state == False:
            self.colorPalette = ((150, 0, 0), (200, 0, 0))

        return self

    # def validate(self, grid, visitedBefore=[]):
    def validateInequalities(self, grid):
        # """ 
        #     recursively evaluate adjacent cell values (if they have an inequality between them)
        #     will evaluate every linked cell along the chain of inequalities
        # """

        # visitedBefore.append(self) # so we dont backtrack during recursion
        validFlag = True

        for k, v in self.inequalities.items():
            # direction:ineq-object
            # cell-to-visit:how-to-evaluate-that-cell
            if k == 'up':
                posToVisit = (self.position[0] - 1, self.position[1])
                cellToVisit = grid.positions[posToVisit]

                leftCell, rightCell = cellToVisit, self
            elif k == 'down':
                posToVisit = (self.position[0] + 1, self.position[1])
                cellToVisit = grid.positions[posToVisit]

                leftCell, rightCell = self, cellToVisit

            elif k == 'left':
                posToVisit = (self.position[0], self.position[1] - 1)
                cellToVisit = grid.positions[posToVisit]

                leftCell, rightCell = cellToVisit, self

            elif k == 'right':
                posToVisit = (self.position[0], self.position[1] + 1)
                cellToVisit = grid.positions[posToVisit]

                leftCell, rightCell = self, cellToVisit
            
            if leftCell.val == '' or rightCell.val == '':
                continue # cannot evaluate the inequality, skip

            # if cellToVisit not in visitedBefore: # we probably traversed in from this cell
            #     result = cellToVisit.validate(grid) # recursion

            # evaluate this cell's inequality
            if v.val == '': # there is no inequality rect is empty, skip
                continue
            elif v.val == '<': 
                evaluation = leftCell.val < rightCell.val
            elif v.val == '>':
                evaluation = leftCell.val > rightCell.val

            if evaluation == False: # one invalid inequality affects the cell permanently
                validFlag = False

            leftCell.setValidState(validFlag)
            rightCell.setValidState(validFlag)
        
        return validFlag

class InequalitySign(Rect):
    def __init__(self, rect, position, neighbouringCells, horizontal):
        super().__init__(rect, position)
        self._states = cycle(['', '<', '>'])
        self.val = next(self._states)
        self.colorPalette = (DARK_GREY, LIGHTER_GREY)
        self.color = self.colorPalette[1]
        self.textColor = DARKER_GREY
        self.neighbouringCells = neighbouringCells
        self.horizontal = horizontal

    def cycleState(self):
        self.val = next(self._states)

class Grid:
    def __init__(self):
        self.height = int(WINDOW_HEIGHT / blockSize)
        self.width = int(WINDOW_WIDTH / blockSize)
        self.cells = []
        self.inequalities = []
        self.positions = {} # mapping of position:cell/ineq pairs

    def draw(self):
        for cell in self.cells:
            cell.draw()

        for ineq in self.inequalities:
            ineq.draw()

    def createCells(self):
        for iy, y in enumerate(range(0, WINDOW_HEIGHT, blockSize)):
            for ix, x in enumerate(range(0, WINDOW_WIDTH, blockSize)):
                position = (iy, ix)
                rect = pygame.Rect(x + blockBorder/2, y + blockBorder/2, blockSize - blockBorder, blockSize - blockBorder)

                cell = Cell(rect, position)
                self.cells.append(cell)
                self.positions[position] = cell

        return self.cells

    def createInequalities(self):
        # Vertical
        for i in range(self.width): # in between horizontal spaces
            for j in range(self.height - 1): # for every row
                neighbouringCells = ((i, j), (i, j+1))
                position = (i, j+0.5)
                x = blockSize * (j + 1) - blockBorder/2
                y = blockSize * i + blockBorder/2
                inequalityRect = pygame.Rect(x, y, blockBorder, blockSize-blockBorder) # create rect

                inequality_sign = InequalitySign(inequalityRect, position, neighbouringCells, False) # use rect to create inequalitysign
                self.inequalities.append(inequality_sign) # add inequalitysign to self.inequalities
                self.positions[position] = inequality_sign

        # Horizontal
        for i in range(self.width - 1): # in between vertical spaces  
            for j in range(self.height): # for every column
                neighbouringCells = ((i, j), (i+1, j))
                position = (i+0.5, j)
                x = blockSize * j + blockBorder/2
                y = blockSize * (i + 1) - blockBorder/2

                inequalityRect = pygame.Rect(x, y, blockSize-blockBorder, blockBorder) # create rect
                inequality_sign = InequalitySign(inequalityRect, position, neighbouringCells, True) # use rect to create inequalitysign
                self.inequalities.append(inequality_sign) # add inequalitysign to self.inequalities

        return self.inequalities

    def linkCellsToInequalities(self):
        for index, cell in enumerate(self.cells):
            # find ineq with pos in ineq.neighbouringCells
            linkableIneq = [ ineq for ineq in self.inequalities if cell.position in ineq.neighbouringCells ]
            # identify their pos relative to this cell
            # ineqLocations = {'up': 0, 'down': 0, 'left': 0, 'right': 0}
            ineqLocations = {}
            for ineq in linkableIneq:
                direction = self.findRelativePosition(ineq.position, cell.position)
                ineqLocations[direction] = ineq
            # tag them to Cell.inequalities
            self.cells[index].inequalities = ineqLocations

    @staticmethod
    def findRelativePosition(pos1, pos2):
        """ 
            takes 2 coordinates which are adjacent to each other
            returns position of pos1 relative to pos2: up, down, left, right
            larger values in coords means closer to bottom right
            [ (0,0) (0, 1)]
            [ (1,0) (1, 1)]
        """
        if pos1[0] < pos2[0]: # pos1 is above pos2
            return 'up'
        if pos1[0] > pos2[0]: # pos1 is below pos2
            return 'down'
        if pos1[1] < pos2[1]: # pos1 is to the left of pos2
            return 'left'
        if pos1[1] > pos2[1]: # pos1 is to the right of pos2
            return 'right'

    def validateCell(self, cell, setColor=True):
        if cell.val == '':
            validFlag = None
        else:
            validFlag = True

            posList = []         
            for i in range(self.width): # check row
                posList.append( (cell.position[0], i) )
            for i in range(self.height): # check col
                posList.append( (i, cell.position[1]) )
                
            for posToCheck in posList:
                cellToCheck = self.positions[posToCheck]
                if cellToCheck != cell:
                    isRepeatValue = cellToCheck.val == cell.val
                    if isRepeatValue:
                        validFlag = False
                        cellToCheck.setValidState(False)

            # check inequalities
            ineqResult = cell.validateInequalities(self)
            if not ineqResult:
                validFlag = False

        cell.setValidState(validFlag)

        return validFlag

    def randomSetup(self):
        for ineq in self.inequalities:
            val = random.choices(
                population=['', '<', '>'],
                weights=[0.9, 0.05, 0.05]
            )[0] # returns a 1 element list

            while ineq.val != val:
                ineq.cycleState()
    
    def validateGrid(self):
        validFlag = True
        cellsValidity = []

        for index, cell in enumerate(self.cells):
            result = self.validateCell(cell, setColor=False)

            cellEvaluation = result and cell.val != ''

            if cellEvaluation == False: # one invalid cell will invalidate the whole grid permanently
                validFlag = False 

            cellsValidity.append(cellEvaluation)
            print(f"Evaluation for Cell @ {cell.position}: {cellEvaluation}")

        for cellResult, cell in zip(cellsValidity, self.cells):
            # setting color this way is not permanent, will disappear after clicking
            if cellResult == True:
                cell.color = (0, 200, 0)
            elif cellResult == False:
                cell.color = (200, 0, 0)

        return validFlag

    def solve(self, i, j):
        # manage position of currently focused cell
        while self.positions[(i, j)].val != '':
            if j < self.width - 1: # move right
                j += 1
            elif j == self.width - 1 and i < self.height - 1: # move to next row
                j = 0
                i += 1
            elif j == self.width - 1 and i == self.height - 1: # end of grid
                return True

        # print(i, j)
        cell = self.positions[(i, j)]

        pygame.event.pump()

        for value in range(1, self.width + 1): # check all possible values
            cell.val = value

            if self.validateCell(cell) == True: # use first valid value found
                print(f"settled on {value} for {(i, j)}")
                
                self.draw() # redraw grid
                # draw_box() # highlight current cell

                pygame.display.update()
                pygame.time.delay(20)

                if self.solve(i, j) == True: # recurse as long as true
                    return True
                else: # recursion returned false, backtrack
                    cell.val = ''
            
                self.draw() # redraw grid
                # draw_box() # highlight current cell

                pygame.display.update()
                pygame.time.delay(50)

        cell.val = ''
        print(f"exhausted solutions for {(i, j)}")

        return False  # no solution found, return false

def main():
    global SCREEN, CLOCK

    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pygame.time.Clock()
    SCREEN.fill(WHITE)

    grid = Grid()
    cells = grid.createCells()
    inequalities = grid.createInequalities()
    grid.linkCellsToInequalities()

    highlightTarget = None

    while True:
        grid.draw()

        for event in pygame.event.get():
            val = None

            if event.type == pygame.QUIT:
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for cell in cells:
                    if cell.rect.collidepoint(event.pos): # clicked on this rect
                        if highlightTarget:
                            highlightTarget.unhighlight() # unhighlight prev cell
                            
                        cell.highlight()
                        highlightTarget = cell

                for ineq in inequalities:
                    if ineq.rect.collidepoint(event.pos):
                        if highlightTarget: # was highlighting something before
                            highlightTarget.unhighlight()
                        if highlightTarget == ineq: # second click on this ineq
                            ineq.cycleState()

                        ineq.highlight()
                        highlightTarget = ineq

            if event.type == pygame.KEYDOWN:
                if event.key in keyMappings.keys():
                    val = keyMappings[event.key]

                # debugging
                if event.key == pygame.K_SPACE:
                    print('spacebar')
                    if isinstance(highlightTarget, Cell):
                        result = grid.validateCell(highlightTarget, setColor=False)
                        print(f"Evaluation for {highlightTarget.position}: {result}")
                        if result == True:
                            highlightTarget.color = (0, 200, 0)
                        elif result == False:
                            highlightTarget.color = (200, 0, 0)

                if event.key == pygame.K_TAB:
                    print('tab')
                    grid.randomSetup()

                if event.key == pygame.K_F1:
                    print('f1')
                    t0 = time.time()
                    solution = grid.solve(0, 0)
                    t1 = time.time()

                    duration = round(t1-t0, 2)
                    if solution:
                        print(f'Solved in {duration} seconds')
                    else:
                        print(f'Confirmed impossible in {duration} seconds')

            # the highlighted cell is receiving an input value
            if isinstance(highlightTarget, Cell) and val != None:
                print(val)
                highlightTarget.val = val
                result = grid.validateGrid()
                print(f"Evaluation for Grid: {result}")

        pygame.display.update()

main()