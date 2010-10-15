# Import system modules
import sys


# Column

def setColumns(listControl, columns):
    # For each column,
    for columnIndex, (columnName, columnWidth) in enumerate(columns):
        listControl.InsertColumn(columnIndex, str(columnName))
        listControl.SetColumnWidth(columnIndex, columnWidth)

def getColumnTexts(listControl, columnIndex):
    columnTexts = []
    for rowIndex in xrange(listControl.GetItemCount()):
        columnText = listControl.GetItem(rowIndex, columnIndex).GetText()
        columnTexts.append(columnText)
    return columnTexts


# Row

def insertRow(listControl, rowIndex, columns):
    # If there are no columns, return
    if not columns: return
    # Make sure columns are strings
    columns = [str(x) for x in columns]
    # For each column,
    for columnIndex, column in enumerate(columns):
        if columnIndex == 0: listControl.InsertStringItem(0, columns[0])
        else: listControl.SetStringItem(0, columnIndex, columns[columnIndex])

def prependRow(listControl, columns): 
    insertRow(listControl, 0, columns)

def appendRow(listControl, columns): 
    insertRow(listControl, listControl.GetItemCount(), columns)


# Selection

def getSelections(listControl):
    items = []
    index = listControl.GetFirstSelected()
    while index != -1:
        items.append(index)
        index = listControl.GetNextSelected(index)
    items.sort(reverse=True)
    return items


# Grid

def clearGrid(grid):
    for rowIndex in xrange(grid.GetNumberRows()):
        for columnIndex in xrange(grid.GetNumberCols()):
            grid.SetCellValue(rowIndex, columnIndex, '')


# Feedback

def sendFeedback(feedback):
    print feedback

def printDirectly(feedback):
    sys.stdout.write(feedback)
    sys.stdout.flush()

def printPercentUpdate(currentCount, totalCount):
    printDirectly('\r% 3d %% \t%d        ' % (100 * currentCount / totalCount, currentCount))

def printPercentFinal(totalCount):
    printDirectly('\r100 %% \t%d        \n' % totalCount)

def trackProgress(generator, totalCount, packetLength):
    # Initialize
    items = []
    # For each item,
    for currentCount, item in enumerate(generator):
        items.append(item)
        if currentCount % packetLength == 0: 
            printPercentUpdate(currentCount + 1, totalCount)
    # Return
    printPercentFinal(totalCount)
    return items
