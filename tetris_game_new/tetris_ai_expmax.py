#!/usr/bin/python3
# -*- coding: utf-8 -*-

from tetris_model import BOARD_DATA, Shape
import math
from datetime import datetime
import numpy as np
def takeSecond(elem):
    return elem[1]
class TetrisExpMaxAI(object):
    def getPossibleDirections(self, shape):
        if shape in (Shape.shapeI, Shape.shapeZ, Shape.shapeS):
            directions = (0, 1)
        elif shape == Shape.shapeO:
            directions = (0,)
        else:
            directions = (0, 1, 2, 3)
        return directions

    def enumerationPossibleResult(self):
        from copy import copy
        import itertools
        Shapes = [BOARD_DATA.currentShape] + [Shape for Shape in BOARD_DATA.nextShape]
        allDirections = [self.getPossibleDirections(Shape.shape) for Shape in Shapes]
        allPossibleActions = []
        for index in range(len(Shapes)):
            allPossibleActions.append([])
            for direction in allDirections[index]:
                minX, maxX, _, _ = Shapes[index].getBoundingOffsets(direction)
                for x in range(-minX, BOARD_DATA.width - maxX):
                    allPossibleActions[index].append((x, direction))
        result = list(itertools.product(*allPossibleActions))
        return Shapes, result

    def generateBoardBySingleAction(self, Shape, action, board):
        (x0, direction) = action
        dy = BOARD_DATA.height - 1
        for x, y in Shape.getCoords(direction, x0, 0):
            yy = 0
            print(board)
            print(board[(y + yy), x])
            while yy + y < BOARD_DATA.height and (yy + y < 0 or board[(y + yy), x] == Shape.shapeNone):
                yy += 1
            yy -= 1
            if yy < dy:
                dy = yy
        self.dropDownByDist(board, Shape, direction, x0, dy)
        return board

    def generateBoardByActions(self, Shapes, actionSequence):
        board = np.array(BOARD_DATA.getData()).reshape((BOARD_DATA.height, BOARD_DATA.width))
        for index in range(len(Shapes)):
            (x0, direction) = actionSequence[index]
            dy = BOARD_DATA.height - 1
            for x, y in Shapes[index].getCoords(direction, x0, 0):
                yy = 0
                while yy + y < BOARD_DATA.height and (yy + y < 0 or board[(y + yy), x] == Shape.shapeNone):
                    yy += 1
                yy -= 1
                if yy < dy:
                    dy = yy
            self.dropDownByDist(board, Shapes[index], direction, x0, dy)
        return board

    def dropDownByDist(self, data, shape, direction, x0, dist):
        for x, y in shape.getCoords(direction, x0, 0):
            data[y + dist, x] = shape.shape

    def evaluationScore(self, board):
        width = BOARD_DATA.width
        height = BOARD_DATA.height
        # print(datetime.now() - t1)

        fullLines, nearFullLines = 0, 0
        roofY = [0] * width
        holeCandidates = [0] * width
        holeConfirm = [0] * width
        vHoles, vBlocks = 0, 0
        for y in range(height - 1, -1, -1):
            hasHole = False
            hasBlock = False
            for x in range(width):
                if board[y, x] == Shape.shapeNone:
                    hasHole = True
                    holeCandidates[x] += 1
                else:
                    hasBlock = True
                    roofY[x] = height - y
                    if holeCandidates[x] > 0:
                        holeConfirm[x] += holeCandidates[x]
                        holeCandidates[x] = 0
                    if holeConfirm[x] > 0:
                        vBlocks += 1
            if not hasBlock:
                break
            if not hasHole and hasBlock:
                fullLines += 1
        vHoles = sum([x ** .7 for x in holeConfirm])
        maxHeight = max(roofY) - fullLines
        # print(datetime.now() - t1)

        roofDy = [roofY[i] - roofY[i+1] for i in range(len(roofY) - 1)]

        if len(roofY) <= 0:
            stdY = 0
        else:
            stdY = math.sqrt(sum([y ** 2 for y in roofY]) / len(roofY) - (sum(roofY) / len(roofY)) ** 2)
        if len(roofDy) <= 0:
            stdDY = 0
        else:
            stdDY = math.sqrt(sum([y ** 2 for y in roofDy]) / len(roofDy) - (sum(roofDy) / len(roofDy)) ** 2)

        absDy = sum([abs(x) for x in roofDy])
        maxDy = max(roofY) - min(roofY)
        
        score = fullLines * 1.8 - vHoles * 1.0 - vBlocks * 0.5 - maxHeight ** 2 * 0.02 \
            - stdY * 0.0 - stdDY * 0.01 - absDy * 0.2 - maxDy * 0.3
        return score

    

    def nextMoveByEnumeration(self):
        # t1 = datetime.now()
        # print("**")
        if BOARD_DATA.currentShape == Shape.shapeNone:
            return None
        # print("=======")
        Shapes, allPossibleActionSequence = self.enumerationPossibleResult()
        # print(len(allPossibleActionSequence))
        (maxScore, bestActionSequence) = (-float('inf'), None)
        for actionSequence in allPossibleActionSequence:
            tempBoard = self.generateBoardByActions(Shapes, actionSequence)
            tempScore = self.evaluationScore(tempBoard)
            if tempScore > maxScore:
                (maxScore, bestActionSequence) = (tempScore, actionSequence)
        return (bestActionSequence[0][1], bestActionSequence[0][0], maxScore)
    # def nextMoveByEnumerationWithPurning(self):
    #     Shapes = list([BOARD_DATA.currentShape] + [Shape for Shape in BOARD_DATA.nextShape])
    #     allDirections = [self.getPossibleDirections(Shape.shape) for Shape in Shapes]
    #     lamda = 1
    #     boards = [(np.array(BOARD_DATA.getData()).reshape((BOARD_DATA.height, BOARD_DATA.width)), 0)]
    #     for index in range(len(Shapes)):
    #         # print(boards)
    #         newBoards = []
    #         for board in boards:
    #             for direction in allDirections[index]:
    #                 minX, maxX, _, _ = Shapes[index].getBoundingOffsets(direction)
    #                 for x in range(-minX, BOARD_DATA.width - maxX):
    #                     newBoard = self.generateBoardBySingleAction(Shapes[index], (x, direction), board)
    #                     newScore = self.evaluationScore(newBoard)
    #                     newBoards.append((newBoards, newScore))
    #         boards = newBoards
    #         boards.sort(key = takeSecond)

    def nextMove(self):
        return self.nextMoveByEnumeration()
# TETRIS_AI = TetrisAI()
TETRIS_AI = TetrisExpMaxAI()

