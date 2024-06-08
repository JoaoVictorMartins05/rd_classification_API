"""
@author: joaov
"""

import SimpleITK as sitk
from radiomics import featureextractor
import cv2
import numpy as np
import six
import mahotas as mt
from numpy import savetxt
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_selection import SelectKBest, chi2
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import normalize,StandardScaler
import os

# Definir parâmetros para a extração de características
params = { 'force2D': True,
          'force2Dextration': True,
          'force2Ddimension': True,
          'label' : 255,
          'featureClass' : 'firstorder, glcm, gldm, glrlm, glszm, ngtdm, shape2D'}

extractor = featureextractor.RadiomicsFeatureExtractor( **params)


def executar(imagem):

    # Salvar a imagem em um local temporário
    imagem_path = os.path.join("temp", imagem.name)  # Define o caminho da imagem temporária
    os.makedirs("temp", exist_ok=True)  # Crie o diretório "temp"
    with open(imagem_path, 'wb+') as destination:
        for chunk in imagem.chunks():
            destination.write(chunk)

    image = criar_imagem(imagem_path)
    mask = criar_mascara(imagem_path)
    image_mahotas = cv2.imread(imagem_path,0)
    data = extrair_caracteristicas(image, mask, image_mahotas)
    
    x = select_best_100_features(data)
    return classificar_imagem(x)


def criar_imagem(imagem_path):
    img = cv2.imread(imagem_path)
    outputImage = pyGreen(img)
    outputImage = pyCLAHE(outputImage)
    outputImage = cv2.bitwise_not(outputImage)
    gray = cv2.cvtColor(outputImage, cv2.COLOR_BGR2RGB)       
    cv2.imwrite(os.path.join("temp", "img_processed.png"), gray)  # Salva a imagem processada    
    return sitk.ReadImage(os.path.join("temp", "img_processed.png"), sitk.sitkVectorInt8)


def criar_mascara(imagem_path):
    img = cv2.imread(imagem_path, cv2.IMREAD_GRAYSCALE)  # Lê a imagem como grayscale
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(2,2))
    img = clahe.apply(img)
    blur = cv2.GaussianBlur(img,(5,5),0)
    ret3,th3 = cv2.threshold(blur,160,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    kernel = np.ones((12,12),np.uint8)
    closing = cv2.morphologyEx(th3, cv2.MORPH_CLOSE, kernel)
    cv2.imwrite(os.path.join("temp", "mask.jpg"), closing)  # Salva a máscara   
    return sitk.ReadImage(os.path.join("temp", "mask.jpg"))


def pyCLAHE(inputImage):
    try:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        outputImage = clahe.apply(inputImage)
        return outputImage
    except Exception as e:
        print('ERROR (pyCLAHE): ' + str(e))  


def pyGreen(inputImage):
    try:
        imageGreenBRG=inputImage[:,:,1]
        rgb = cv2.cvtColor(imageGreenBRG, cv2.COLOR_BGR2RGB)
        outputImage=rgb[:,:,1]
        return outputImage
    except Exception as e:
        print('ERROR (pyGreen): ' + str(e)) 


def extrair_caracteristicas(imagem, mascara, imagem_mahotas):
    data = []
    features = []
    print("----------------")
    radiomics = extract_radiomics(imagem, mascara)
    featuresMahotas = extractMahotas(imagem_mahotas)
    features = np.concatenate((radiomics, featuresMahotas), axis=None) 
    #features = np.append(features, 0)
    data.append(features)
    #data.append(features)
    #savetxt("mahotas.csv", data, delimiter=',')
    print("Total de caracteristicas => ",len(features))
    print("----------------")
    return data


def extract_radiomics(imagem,mascara):
    data = []
    color_channel = 0
    im = imagem
    selector = sitk.VectorIndexSelectionCastImageFilter()
    selector.SetIndex(color_channel)
    im = selector.Execute(im)
    results = extractor.execute(im, mascara, 255)
    
    print("results.keys => ", len(results.keys()))
    
    i =0
    for key, val in six.iteritems(results):
        if(i>21):
            data.append(val)
        i = i + 1; 
    print("radiomic "+str(len(data)))
    return data


def extractMahotas(image):
    data = []       
    lbp = mt.features.lbp(image, radius=8, points=8)     
    print("lbp " + str(len(lbp)))
    zernike = mt.features.zernike(image,10, 10)   
    print("zernike " + str(len(zernike)))
    tas = mt.features.tas(image)
    print("tas " + str(len(tas)))    
    data = np.concatenate((lbp,tas,zernike),axis=None)
    print("mahotas Total: "+str(len(data)))
    return data


def load_images_to_normalize_database():
    
    infer_dataset = pd.read_csv('../features.csv')
    X_infer = infer_dataset.iloc[:, 0:219].values
    return X_infer
        

def select_best_100_features(raw_data):
    # Transforma o array de características em um array numpy
    X_infer = np.array(raw_data)
    X_infer = X_infer.astype(np.float32)
    
    
    print("Dados de entrada:")
    print(X_infer)
    
    train_data = load_images_to_normalize_database()
    train_data =  np.array(train_data)
    
    print(train_data)
    
    # Adicionar novas amostras à matriz train_data
    train_data = np.vstack((train_data, X_infer))    
    
    # Normaliza a base de dados
    minimax = MinMaxScaler()
    data = minimax.fit_transform(train_data)
    
    #np.set_printoptions(suppress=True)
    
    print("\nDados normalizados:")
    print(data)
    
    # Define o índice das 100 melhores características (existe melhor forma de pegar essas dados?)
    indices_importantes = [0, 1, 4, 5, 7, 8, 9, 12, 13, 14, 17, 18, 19, 21, 22, 24, 26, 29,
                           34, 39, 41, 47, 48, 50, 54, 58, 59, 70, 71, 74, 75, 83, 84, 90, 91, 92,
                           93, 95, 96, 97, 104, 105, 108, 109, 116, 120, 121, 122, 124, 130, 131,
                           132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145,
                           146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159,
                           160, 161, 162, 163, 164, 174, 175, 176, 177, 178, 179, 180, 181, 182,
                           184, 203, 205, 207, 212, 213, 215]

    #Pega o array da imagem que veio do input    
    ultimo_array = data[-1:]

    # Seleciona as características importantes
    important_features = ultimo_array[:,indices_importantes]
    
    print("\nCaracterísticas selecionadas:", len(important_features[0]))
    print(important_features)
    
    
    return important_features


def classificar_imagem(X_infer):
    model = keras.models.load_model(f'../best_model.h5')

    prediction = model.predict(X_infer)
    
    # Aplica um threshold no resultado do sigmoid
    threshold = 0.5
    binary_prediction = (prediction > threshold).astype(int)
    
    result = "Saudavel" if binary_prediction[0][0] else "Doente"
    print("binary_prediction => ", binary_prediction)
 
    print("Classificacao => ", result)

    return result
