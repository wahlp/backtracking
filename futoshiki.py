import pygame
import random
from itertools import cycle

WINDOW_HEIGHT = 500
WINDOW_WIDTH = 500

blockSize = 100 #Set the size of the grid block
blockBorder = 25

BLACK           = (0, 0, 0)
DARKER_GREY     = (50, 50, 50)
DARK_GREY       = (100, 100, 100)
GREY            = (150, 150, 150)
LIGHT_GREY      = (200, 200, 200)
LIGHTER_GREY    = (220, 220, 220)
WHITE           = (255, 255, 255)

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

    def colorByValidity(self, valid, highlight=True):
        paletteIndex = (not highlight) * 1 # 0 if True, 1 if False

        if not valid:
            self.colorPalette = ((150, 0, 0), (200, 0, 0))
        else:
            self.colorPalette = (DARK_GREY, LIGHT_GREY)

        self.color = self.colorPalette[paletteIndex]

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
            if v.val == '<': 
                validFlag = leftCell.val < rightCell.val
            elif v.val == '>':
                validFlag = leftCell.val > rightCell.val
            else: # there is no inequality rect is empty, skip
                continue

            leftCell.colorByValidity(validFlag, highlight=False)
            rightCell.colorByValidity(validFlag, highlight=False)
        
        return validFlag

        # if goodEvaluation:
        #   return True
        # else:
        #   return False

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

    # def getInequalities(self):
    #     # [4, 4, 4, 4, 4] vertical
    #     # [5, 5, 5, 5] horizontal
    #     # always left to right
    #     down = self.height * (self.width - 1) # vertical
    #     across = (self.height - 1) * self.width # horizontal

    #     for index, ineq in enumerate(self.inequalities):
    #         row = index // (self.width - 1)
    #         if row < self.height: # vertical
    #             print(f"down: {row}")
    #             pass
    #         else: # horizontal
    #             col = (index - down) // self.width
    #             print(f"across: {col}")
    #         print(ineq.neighbouringCells)

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

    # def getValues(self):
    #     width = int(WINDOW_WIDTH / blockSize)
    #     values = [cell.val for cell in self.cells]
    #     gridValues = [values[i:i + width] for i in range(0, len(values), width)] # chunk into grid with (width) values in each row
    #     return gridValues # 2d list

    # def setValues(self, values): # takes 2d list
    #     values = [b for a in values for b in a] # unwrap to 1d 
    #     for index, v in enumerate(values):
    #         self.cells[index].val = v

    def validateCell(self, cell, setColor=True):
        # if cell.val == '':
        #     return False
        validFlag = True

        # example: cell.position = (0, 0)
        # check row - (0, 1), (0, 2), etc
        for i in range(self.width):
            posToCheck = (cell.position[0], i)
            cellToCheck = self.positions[posToCheck]
            if cellToCheck != cell:
                if cellToCheck.val == cell.val: # same value in row
                    validFlag = False
                    if setColor:
                        cellToCheck.colorByValidity(False, highlight=False)

                # to correct previously invalid cells
                # however, will trigger different branches if coming from validateGrid
                else:
                    if setColor:
                        cellToCheck.colorByValidity(True, highlight=False)

        # check col - (1, 0), (2, 0), etc
        for i in range(self.height):
            posToCheck = (i, cell.position[1])
            cellToCheck = self.positions[posToCheck]
            if cellToCheck != cell:
                if cellToCheck.val == cell.val: # same value in col
                    validFlag = False
                    if setColor:
                        cellToCheck.colorByValidity(False, highlight=False)
                else:
                    if setColor:
                        cellToCheck.colorByValidity(True, highlight=False)

        # check inequalities
        ineqResult = cell.validateInequalities(self)
        if not ineqResult:
            validFlag = False

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

            if not cellEvaluation: # one invalid cell will invalidate the whole grid permanently
                validFlag = False 

            cellsValidity.append(cellEvaluation)
            print(f"Evaluation for Cell @ {cell.position}: {cellEvaluation}")

        for cellResult, cell in zip(cellsValidity, self.cells):
            # setting color this way is not permanent, will disappear after clicking
            if cellResult:
                cell.color = (0, 200, 0)
            else:
                cell.color = (200, 0, 0)

        return validFlag

def solve(grid, i, j):
    while grid[i][j]!= 0:
        if i<4:
            i+= 1
        elif i == 4 and j<4:
            i = 0
            j+= 1
        elif i == 4 and j == 4:
            return True
    pygame.event.pump()    
    for it in range(1, 6): # check all possible values
        # if valid(grid, i, j, it)== True: # use first valid value found
        if grid.validateCell(cell):
            grid[i][j]= it
            global x, y
            x = i
            y = j
            # white color background\
            screen.fill((255, 255, 255))
            draw()
            draw_box()
            pygame.display.update()
            pygame.time.delay(20)
            if solve(grid, i, j)== 1: # recurse as long as true
                return True
            else: # recursion returned false, backtrack
                grid[i][j]= 0
            # white color background\
            screen.fill((255, 255, 255))
          
            draw()
            draw_box()
            pygame.display.update()
            pygame.time.delay(50)    
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
                if event.key == pygame.K_1:
                    val = 1
                if event.key == pygame.K_2:
                    val = 2    
                if event.key == pygame.K_3:
                    val = 3
                if event.key == pygame.K_4:
                    val = 4
                if event.key == pygame.K_5:
                    val = 5
                if event.key == pygame.K_6:
                    val = 6 
                if event.key == pygame.K_7:
                    val = 7
                if event.key == pygame.K_8:
                    val = 8
                if event.key == pygame.K_9:
                    val = 9
                if event.key == pygame.K_BACKSPACE:
                    val = ''

                # debugging
                if event.key == pygame.K_SPACE:
                    print('spacebar')
                    if isinstance(highlightTarget, Cell):
                        result = grid.validateCell(highlightTarget, setColor=False)
                        print(f"Evaluation for {highlightTarget.position}: {result}")
                        if result:
                            highlightTarget.color = (0, 200, 0)
                        else:
                            highlightTarget.color = (200, 0, 0)

                if event.key == pygame.K_TAB:
                    print('tab')
                    grid.randomSetup()
                
                # debugging
                if event.key == pygame.K_F1:
                    print('f1')
                    result = grid.validateGrid()
                    print(f"Evaluation for Grid: {result}")


            # the highlighted cell is receiving an input value
            if isinstance(highlightTarget, Cell) and val != None:
                print(val)
                highlightTarget.val = val
                if val != '':
                    result = grid.validateCell(highlightTarget)
                    highlightTarget.colorByValidity(result)

        pygame.display.update()

main()