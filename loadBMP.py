import sys
import math

#Suma de strings hexadecimales
def add_hex2(hex1, hex2):
    return hex(int(hex1, 16) + int(hex2, 16))

#Quitar componente verde de la imagen (24bpp) - For testing
def removeGreen(data, start, rowSize, imageHeight):
    for i in range(0, imageHeight):
        for j in range(start, rowSize + start, 3):
            if(rowSize + start - j < 3): #Padding
                break
            data[(j + 1) + (i * rowSize)] = 0
    return data

#Cambiar imagen a negativo
def negativeImg(data, start, rowSize, imageHeight, pixelFormat):
#    if(pixelFormat == 24): #24 bpp
#        for i in range(0, imageHeight):
#            for j in range(start, rowSize + start, 3):
#                if(rowSize + start - j < 3): #Padding
#                    break
#                data[(j + 0) + (i * rowSize)] = 255 - data[(j + 0) + (i * rowSize)]
#                data[(j + 1) + (i * rowSize)] = 255 - data[(j + 1) + (i * rowSize)]
#                data[(j + 2) + (i * rowSize)] = 255 - data[(j + 2) + (i * rowSize)]
                
#    elif(pixelFormat == 8 or pixelFormat == 4 or pixelFormat == 2 or pixelFormat == 1): #8/4/2/1bpp
    print ("Invirtiendo colores")
    for i in range(0, imageHeight):
        for j in range(start, rowSize + start):
            data[j + (i * rowSize)] = 255 - data[j + (i * rowSize)]
                
    return data

def storeColorData(data, start, rowSize, imageHeight, pixelFormat):
    #Raw data
    rawColor = list()
    rawCount = 0
    
    rowSizeMult = 1

    if(pixelFormat == 1): #1 Byte = 8 Colors
        rowSizeMult = 8
        for i in range(0, imageHeight):
            for j in range(start, rowSize + start):
                rawColor.append((128 & data[j + (i * rowSize)]) >> 7)
                rawColor.append((64  & data[j + (i * rowSize)]) >> 6)
                rawColor.append((32  & data[j + (i * rowSize)]) >> 5)
                rawColor.append((16  & data[j + (i * rowSize)]) >> 4)
                rawColor.append((8   & data[j + (i * rowSize)]) >> 3)
                rawColor.append((4   & data[j + (i * rowSize)]) >> 2)
                rawColor.append((2   & data[j + (i * rowSize)]) >> 1)
                rawColor.append( 1   & data[j + (i * rowSize)])
                
    elif(pixelFormat == 2): #1 Byte = 4 Colors
        rowSizeMult = 4
        for i in range(0, imageHeight):
            for j in range(start, rowSize + start):
                rawColor.append((192 & data[j + (i * rowSize)]) >> 6)
                rawColor.append((48  & data[j + (i * rowSize)]) >> 4)
                rawColor.append((12  & data[j + (i * rowSize)]) >> 2)
                rawColor.append( 3   & data[j + (i * rowSize)])
                
    elif(pixelFormat == 4): #1 Byte = 2 Colors
        rowSizeMult = 2
        #Store all colors individually
        for i in range(0, imageHeight):
            for j in range(start, rowSize + start):
                rawColor.append((240 & data[j + (i * rowSize)]) >> 4)
                rawColor.append( 15  & data[j + (i * rowSize)])
                #print ("Append:", (240 & data[j + (i * rowSize)]) >> 4, 15  & data[j + (i * rowSize)])
                #rawColor.append(data[j + (i * rowSize)])
                #if(i == 5 and (rowSize + initialStart) - j < 5):
                #    print ("RawColor:", (240 & data[j + (i * rowSize)]) >> 4, 15 & data[j + (i * rowSize)])
                
    elif(pixelFormat == 8): #1 Byte = 1 Color
        rowSizeMult = 1
        #Store all colors individually
        for i in range(0, imageHeight):
            for j in range(start, rowSize + start):
                rawColor.append(data[j + (i * rowSize)])

    elif (pixelFormat == 24):
        rowSizeMult = 1/3
        #Store all colors individually
        for i in range(0, imageHeight):
            for j in range(start, rowSize + start, 3):
                if(rowSize + start - j < 3): #Padding
                    break
                #Store 3 colors at a time
                rawColor.append([data[j + (i * rowSize) + 0], data[j + (i * rowSize) + 1], data[j + (i * rowSize) + 2]])

    return (rawColor, rowSizeMult)

def setImageColors(data, start, rowSize, imageHeight, pixelFormat, rotColor, rowSizeMult):
    rotCount = 0
    
    #New Values
    imageHeight = int(format(data[25], '02x') + format(data[24], '02x') + format(data[23], '02x') + format(data[22], '02x'), 16)
    imageWidth = int(format(data[21], '02x') + format(data[20], '02x') + format(data[19], '02x') + format(data[18], '02x'), 16)
        
    rowSize = math.floor((bitsPerPixel * imageWidth + 31) / 32) * 4

    #Set color on respective zone
    if(pixelFormat != 24): # Format = 1 / 2 / 4 / 8
        updateRatio = rowSizeMult
        bitMoveRatio = int(8 / rowSizeMult)
        
        for i in range(0, imageHeight):
            updateRatio = rowSizeMult
            bitMoveRatio = int(8 / rowSizeMult)
            for j in range(start, rowSize + start):
                if(len(data) <= j + (i * rowSize)):
                    data = data + bytearray([255])
                    continue

                while(rotCount + updateRatio >= len(rotColor) or imageWidth - ((j - start) * rowSizeMult) < updateRatio):
                    updateRatio = updateRatio - 1
                    if(updateRatio == 0):
                        break

                data[j + (i * rowSize)] = 0
                for k in range(0, updateRatio):
                    data[j + (i * rowSize)] = data[j + (i * rowSize)] | (rotColor[rotCount + k] << (8 - (bitMoveRatio * (k + 1))))

                rotCount = rotCount + updateRatio
                
    else: #Format = 24
        for i in range(0, imageHeight):
            for j in range(start, rowSize + start, 3):
                if(rowSize + start - j < 3): #Padding
                    break
                
                if(len(data) <= j + (i * rowSize) + 3): #Fill empty spaces
                    data = data + bytearray([255, 255, 255])
                    continue

                if(imageWidth % 2 != 0 and rowSize + start - j < 4):
                    continue

                data[(j + 0) + (i * rowSize)] = rotColor[rotCount][0]
                data[(j + 1) + (i * rowSize)] = rotColor[rotCount][1]
                data[(j + 2) + (i * rowSize)] = rotColor[rotCount][2]

                rotCount = rotCount + 1

    return data

#Invertir la imagen 90° a la derecha
def rotate90Right(data, start, rowSize, imageHeight, pixelFormat):
    #Change Width & Height
    aux0 = data[21]
    aux1 = data[20]
    aux2 = data[19]
    aux3 = data[18]

    data[21] = data[25]
    data[20] = data[24]
    data[19] = data[23]
    data[18] = data[22]

    data[25] = aux0
    data[24] = aux1
    data[23] = aux2
    data[22] = aux3

    #Change Horizontal & Vertical resolution
    aux0 = data[41]
    aux1 = data[40]
    aux2 = data[39]
    aux3 = data[38]

    data[41] = data[45]
    data[40] = data[44]
    data[39] = data[43]
    data[38] = data[42]

    data[45] = aux0
    data[44] = aux1
    data[43] = aux2
    data[42] = aux3

    #Raw data to rotate
    rawColor = list()
    rawCount = 0

    #Rotated List
    rotColor = list()
    rotCount = 0

    #Store all colors individualy
    print ("Guardando datos")
    (rawColor, rowSizeMult) = storeColorData(data, start, rowSize, imageHeight, pixelFormat)

    #Rotate data
    print ("Reubicando colores")
    for i in range(int(rowSize * rowSizeMult -1), -1, -1):
        for j in range(0, imageHeight):
            rotColor.append(rawColor[int(i + (j * rowSize * rowSizeMult))])
            #if(i == rowSize * 2 -1 and imageHeight - j < 10):
            #    print ("RawColor:", rawColor[i + (j * rowSize * 2)])

    #Apply colors and return data
    print ("Aplicando colores")
    return setImageColors(data, start, rowSize, imageHeight, pixelFormat, rotColor, rowSizeMult)

#Invertir la imagen 90° a la izquierda
def rotate90Left(data, start, rowSize, imageHeight, pixelFormat):
    #Change Width & Height
    aux0 = data[21]
    aux1 = data[20]
    aux2 = data[19]
    aux3 = data[18]

    data[21] = data[25]
    data[20] = data[24]
    data[19] = data[23]
    data[18] = data[22]

    data[25] = aux0
    data[24] = aux1
    data[23] = aux2
    data[22] = aux3

    #Change Horizontal & Vertical resolution
    aux0 = data[41]
    aux1 = data[40]
    aux2 = data[39]
    aux3 = data[38]

    data[41] = data[45]
    data[40] = data[44]
    data[39] = data[43]
    data[38] = data[42]

    data[45] = aux0
    data[44] = aux1
    data[43] = aux2
    data[42] = aux3

    #Raw data to rotate
    rawColor = list()
    rawCount = 0

    #Rotated List
    rotColor = list()
    rotCount = 0

    #Store all colors individualy
    print ("Guardando datos")
    (rawColor, rowSizeMult) = storeColorData(data, start, rowSize, imageHeight, pixelFormat)

    #Rotate data
    print ("Reubicando colores")
    for i in range(0, int(rowSize * rowSizeMult)):
        for j in range(imageHeight -1, -1, -1):
            rotColor.append(rawColor[int(i + (j * rowSize * rowSizeMult))])
            #if(i == rowSize * 2 -1 and imageHeight - j < 10):
            #    print ("RawColor:", rawColor[i + (j * rowSize * 2)])

    #Apply colors and return data
    print ("Aplicando colores")
    return setImageColors(data, start, rowSize, imageHeight, pixelFormat, rotColor, rowSizeMult)

#Rotate 180
def rotate180(data, start, rowSize, imageHeight, pixelFormat):
    #Raw data to mirror
    rawColor = list()
    rawCount = 0

    #Rotate List
    mirColor = list()
    mirCount = 0

    rowSizeMult = 0
    
    #Store all colors individualy
    print ("Guardando datos")
    (rawColor, rowSizeMult) = storeColorData(data, start, rowSize, imageHeight, pixelFormat)

    #Rotate colors
    print ("Reubicando colores")
    for i in range(imageHeight -1, -1, -1):
        for j in range(int(rowSize * rowSizeMult -1), -1, -1):
            mirColor.append(rawColor[int(j + (i * rowSize * rowSizeMult))])

    #Apply colors and return data
    print ("Aplicando colores")
    return setImageColors(data, start, rowSize, imageHeight, pixelFormat, mirColor, rowSizeMult)

#Mirror Horizontal
def mirrorHorizontal(data, start, rowSize, imageHeight, pixelFormat):
    #Raw data to mirror
    rawColor = list()
    rawCount = 0

    #Mirror List
    mirColor = list()
    mirCount = 0

    rowSizeMult = 0
    
    #Store all colors individualy
    print ("Guardando datos")
    (rawColor, rowSizeMult) = storeColorData(data, start, rowSize, imageHeight, pixelFormat)

    #Mirror colors
    print ("Reubicando colores")
    for i in range(0, imageHeight):
        for j in range(int(rowSize * rowSizeMult -1), -1, -1):
            mirColor.append(rawColor[int(j + (i * rowSize * rowSizeMult))])

    #Apply colors and return data
    print ("Aplicando colores")
    return setImageColors(data, start, rowSize, imageHeight, pixelFormat, mirColor, rowSizeMult)

#Mirror Vertical
def mirrorVertical(data, start, rowSize, imageHeight, pixelFormat):
    #Raw data to mirror
    rawColor = list()
    rawCount = 0

    #Mirror List
    mirColor = list()
    mirCount = 0

    rowSizeMult = 0
    
    #Store all colors individualy
    print ("Guardando datos")
    (rawColor, rowSizeMult) = storeColorData(data, start, rowSize, imageHeight, pixelFormat)

    #Rotate colors
    print ("Reubicando colores")
    for i in range(imageHeight -1, -1, -1):
        for j in range(0, int(rowSize * rowSizeMult)):
            mirColor.append(rawColor[int(j + (i * rowSize * rowSizeMult))])

    #Apply colors and return data
    print ("Aplicando colores")
    return setImageColors(data, start, rowSize, imageHeight, pixelFormat, mirColor, rowSizeMult)

#Save Image
def saveBMP(data, name):
    with open(name, 'wb') as f:
        f.write(data)


#Begin Main
#Pedir imagen a modificar
imagePath = input("Coloque la ruta de la imagen: ")

#Abrir imagen
with open(imagePath, 'rb') as f:
    data = bytearray(f.read())

#Validaciones
if(chr(data[0]) + chr(data[1]) != "BM") : #Si la imagen esta en un formato distinto al que este programa puede procesar
    print ('Imagen en formato invalido. Format:', chr(data[0]) + chr(data[1]))
    print ('Use imagen con formato BM')
    exit()

if(int(format(data[33], '02x') + format(data[32], '02x') + format(data[31], '02x') + format(data[30], '02x'), 16) != 0): #Si la imagen posee un formato de compresion
    print ('Imagen con un formato de compresion, use una imagen sin compresion')
    exit()

#End Validaciones

userOption = 0

while(userOption != 10):
    #Inicializar variables
    bitsPerPixel = int(format(data[29], '02x') + format(data[28], '02x'), 16)
    imageWidth = int(format(data[21], '02x') + format(data[20], '02x') + format(data[19], '02x') + format(data[18], '02x'), 16)
    imageHeight = int(format(data[25], '02x') + format(data[24], '02x') + format(data[23], '02x') + format(data[22], '02x'), 16)

    rawSize = int(format(data[37], '02x') + format(data[36], '02x') + format(data[35], '02x') + format(data[34], '02x'), 16)

    #Posicion inicial del arreglo de pixeles
    pivotPos = int(format(data[13], '02x') + format(data[12], '02x') + format(data[11], '02x') + format(data[10], '02x'), 16);

    #Tamano horizontal
    rowSize = math.floor((bitsPerPixel * imageWidth + 31) / 32) * 4
    pixelArraySize = rowSize * abs(imageHeight)
    
    #Mostrar opciones
    print ()
    print ("Introduzca el numero correspondiente a la opcion deseada")
    print ("1) Negativo")
    print ("2) Rotar 90° a la izquierda")
    print ("3) Rotar 90° a la derecha")
    print ("4) Rotar 180°")
    print ("5) Rotar 270° a la izquierda")
    print ("6) Rotar 270° a la derecha")
    print ("7) Espejo Horizontal")
    print ("8) Espejo Vertical")
    print ("9) Cambiar Imagen")
    print ("10) Salir")

    userOption = int(input())

    if(userOption == 1):
        data = negativeImg(data, pivotPos, rowSize, imageHeight, bitsPerPixel)
        saveBMP(data, 'RES' + imagePath)
    elif(userOption == 2 or userOption == 6):
        data = rotate90Left(data, pivotPos, rowSize, imageHeight, bitsPerPixel)
        saveBMP(data, 'RES' + imagePath)
    elif(userOption == 3 or userOption == 5):
        data = rotate90Right(data, pivotPos, rowSize, imageHeight, bitsPerPixel)
        saveBMP(data, 'RES' + imagePath)
    elif(userOption == 4):
        data = rotate180(data, pivotPos, rowSize, imageHeight, bitsPerPixel)
        saveBMP(data, 'RES' + imagePath)
    elif(userOption == 7):
        data = mirrorHorizontal(data, pivotPos, rowSize, imageHeight, bitsPerPixel)
        saveBMP(data, 'RES' + imagePath)
    elif(userOption == 8):
        data = mirrorVertical(data, pivotPos, rowSize, imageHeight, bitsPerPixel)
        saveBMP(data, 'RES' + imagePath)
    elif(userOption == 9):
        print ("Imagen anterior guardada con ruta:", 'RES' + imagePath)
        #Pedir imagen a modificar
        imagePath = input("Coloque la ruta de la nueva imagen: ")

        #Abrir imagen
        with open(imagePath, 'rb') as f:
            data = bytearray(f.read())
    else:
        print ("Saliendo del programa")
        break


#print (sys.argv)

#print (rawSize, pixelArraySize)
#print ("File Stats")
#print ("Header. ID:",               chr(data[0]) + chr(data[1]))
#print ("Header. File Size:",        int(format(data[5], '02x') + format(data[4], '02x') + format(data[3], '02x') + format(data[2], '02x'), 16), 'bytes')
#print ("Header. Reserved-1:",       chr(data[7]) + chr(data[6]))
#print ("Header. Reserved-2:",       chr(data[9]) + chr(data[8]))
#print ("Header. Start Position:",   pivotPos)

#print ("DIB Header. Header Size:",          int(format(data[17], '02x') + format(data[16], '02x') + format(data[15], '02x') + format(data[14], '02x'), 16), 'bytes')
#print ("DIB Header. Width:",                imageWidth, 'pixels')
#print ("DIB Header. Height:",               imageHeight, 'pixels')
#print ("DIB Header. Color Planes:",         int(format(data[27], '02x') + format(data[26], '02x'), 16))
#print ("DIB Header. Color Depth:",          bitsPerPixel)
#print ("DIB Header. Compression:",          int(format(data[33], '02x') + format(data[32], '02x') + format(data[31], '02x') + format(data[30], '02x'), 16))
#print ("DIB Header. Raw Size:",             rawSize, 'bytes')
#print ("DIB Header. Horizontal Resolution:",int(format(data[41], '02x') + format(data[40], '02x') + format(data[39], '02x') + format(data[38], '02x'), 16), 'ppm')
#print ("DIB Header. Vertical Resolution:",  int(format(data[45], '02x') + format(data[44], '02x') + format(data[43], '02x') + format(data[42], '02x'), 16), 'ppm')
#print ("DIB Header. Color Palette:",        int(format(data[49], '02x') + format(data[48], '02x') + format(data[47], '02x') + format(data[46], '02x'), 16))
#print ("DIB Header. Important Colors:",     int(format(data[53], '02x') + format(data[52], '02x') + format(data[51], '02x') + format(data[50], '02x'), 16))

#Cambiar colores
#data = negativeImg(data, pivotPos, rowSize, imageHeight, bitsPerPixel)

#Invertir 270
#data = mirrorVertical(data, pivotPos, rowSize, imageHeight, bitsPerPixel)

#bitsPerPixel = int(format(data[29], '02x') + format(data[28], '02x'), 16)
#imageWidth = int(format(data[21], '02x') + format(data[20], '02x') + format(data[19], '02x') + format(data[18], '02x'), 16)
#imageHeight = int(format(data[25], '02x') + format(data[24], '02x') + format(data[23], '02x') + format(data[22], '02x'), 16)

#rowSize = math.floor((bitsPerPixel * imageWidth + 31) / 32) * 4

#data = rotate90Right(data, pivotPos, rowSize, imageHeight, bitsPerPixel)

#bitsPerPixel = int(format(data[29], '02x') + format(data[28], '02x'), 16)
#imageWidth = int(format(data[21], '02x') + format(data[20], '02x') + format(data[19], '02x') + format(data[18], '02x'), 16)
#imageHeight = int(format(data[25], '02x') + format(data[24], '02x') + format(data[23], '02x') + format(data[22], '02x'), 16)

#rowSize = math.floor((bitsPerPixel * imageWidth + 31) / 32) * 4

#data = rotate90Right(data, pivotPos, rowSize, imageHeight, bitsPerPixel)

#360
#bitsPerPixel = int(format(data[29], '02x') + format(data[28], '02x'), 16)
#imageWidth = int(format(data[21], '02x') + format(data[20], '02x') + format(data[19], '02x') + format(data[18], '02x'), 16)
#imageHeight = int(format(data[25], '02x') + format(data[24], '02x') + format(data[23], '02x') + format(data[22], '02x'), 16)

#rowSize = math.floor((bitsPerPixel * imageWidth + 31) / 32) * 4

#data = rotate90Right(data, pivotPos, rowSize, imageHeight, bitsPerPixel)
