"""
Created on Mon Jun  8 19:05:18 2020

Trabalho de conclusão de curso de Engenharia de Exploração e Produção de Petróleo do Laboratório de Engenharia e Exploração de Petróleo.

Universidade Estadual do Norte Fluminense Darcy Ribeiro
LENEP - Laboratório de Engenharia e Exploração de Petróleo (http://uenf.br/cct/lenep/)

@author: Lucas Isaac Vieira Oliveira
Orientador: FERNANDO DIOGO DE SIQUEIRA, D.Sc.
E-mail: lucas.isaac10@gmail.com
"""

from tkinter import *
import re 
from tkinter import filedialog
import numpy as np
import math as mt
import pandas as pd 
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import Ellipse
from matplotlib.transforms import Affine2D
import mpl_toolkits.mplot3d.art3d as art3d

class EntradaDeDados:      

    def __init__(self):
        
        self.GravidadeTotal = float
        self.CampoMagTotal = float
        self.DipMag = float
        self.Latitude = float
        self.tipoPlataforma = int
        self.tool = int
        
        self.plataformaFixa = int       
        self.correcaoAxial = int
        
        self.modoGyro = int
        
        self.EnderecoArquivosTxt = []
        self.lines = []
        
        self.DadosLocaisPoco()
        
    def DadosLocaisPoco(self):    
    
        print('Dados de Imput para cálculo dos modelos de erro.\nNúmeros flutuantes devem ser sepados por ponto(".").\n')
        
        #self.GravidadeTotal = float(input("Insira o valor total da gravidade: "))
        #self.CampoMagTotal = float(input("Insira o valor do campo magnético total: "))
        #self.DipMag = float(input("Insira o valor do mergulho (Dip) magnético: "))
        #self.Latitude = float(input("Insira o valor da latidude: "))
        #self.plataformaFixa = int(input("Se a plataforma for fixa digite 0.\nSe a plataforma for flutuante digite 1.\n"))
        #self.tipoGyro = int(input("Qual o tipo de em relação aos eixos existentes na ferramenta? \nSe o GYRO for do tipo XY digite 0.\nSe o GYRO for do tipo XYZ digite 1.\n))
        
        self.G = 9.80665        #   self.G = DadosGeograficos[0]
        self.B = 48000          #   self.B = DadosGeograficos[1]
        self.DipMag = -43       #   self.DipMag = DadosGeograficos[2]
        self.Latitude = 28      #   self.Latitude = DadosGeograficos[3]
        self.deltaD = 30        #   metros - distancia entre estações
        self.rotacaoTerra = 465 #   m/s
        
        self.plataformaFixa = 0
        self.tipoGyro = 0
        
        if self.plataformaFixa == 0:
             self.correcaoAxial = 1 # 0 Para aplicar a correção Axial e 1 para Não aplicar a correção axial
             
        print("Escolha o arquivo de dados referentes as ferramentas Magnéticas:\n")
        self.tool = 1
        self.EscolhaArquivo()
        self.DadosSurveysCrus()
        
        print("Escolha o arquivo de dados referentes as ferramentas Gyro:\n")
        self.tool = 2
        self.EscolhaArquivo()
        self.DadosSurveysCrus()
        
    def EscolhaArquivo(self):

        root = Tk()
       
        root.title('Seleção banco de dados')
        
        self.EnderecoArquivosTxt = filedialog.askopenfilenames(parent=root, title="Selecione os arquivos com banco de dados", filetypes=(("Txt files", "*.txt"),("all files", "*.*")))
        
        root.splitlist(self.EnderecoArquivosTxt)
        root.mainloop()
        
        with open(self.EnderecoArquivosTxt[0]) as Arquivo:

            self.lines=Arquivo.readlines()
            
        Arquivo.close()
    
    def DadosSurveysCrus(self):
        
        teste           = []
        valuePosition   = []
        values          = []
        startValues     = int
        endValues       = int
        teste           = []
        
        valuePosition = [x for x in range(len(self.lines)) if 'MD     INC      AZT       TVD' in self.lines[x]]
        
        startValues = valuePosition[0] + 2

        endValues = valuePosition[1] - 2
        
        Column_number = 0
        
        for f in self.lines:
    
            values.append(f.split('\t')[Column_number])
        
        del values[endValues+1:len(values)]
        del values[0:startValues]
        
        count = 0

        while count<len(values):
            teste.append(values[count].split())
            del teste[count][4:len(teste[count])] #Aqui deleto a quarta coluna pra frente
            dadosOriginais = np.array(teste, float)
            count = count + 1

        if self.tool == 1:
            self.dadosOriginaisMWD = dadosOriginais

        if self.tool == 2:
            self.dadosOriginaisGWD = dadosOriginais 
              
class InterpolacaoDados(EntradaDeDados):
    
    def __init__(self):
        
        super().__init__()
        
        self.MDinicialMWD           = self.dadosOriginaisMWD[0][0]
        self.MDinicialGWD           = self.dadosOriginaisGWD[0][0]
        self.MDfinalMWD             = self.dadosOriginaisMWD[len(self.dadosOriginaisMWD)-1][0]
        self.MDfinalGWD             = self.dadosOriginaisGWD[len(self.dadosOriginaisGWD)-1][0]
        self.menorMD                = float
        self.maiorMD                = float
        self.numeroEstacoes         = int

        self.CompararMD()
        self.Interpolar()
        
    def CompararMD(self):
        
        if self.MDinicialMWD > self.MDinicialGWD:
            self.menorMD = self.MDinicialGWD
        else:
            self.menorMD = self.MDinicialMWD
        
        if self.MDfinalMWD < self.MDfinalGWD:
            self.maiorMD = self.MDfinalGWD
        else:
            self.maiorMD = self.MDfinalMWD
        
        self.numeroEstacoes = int(round((self.maiorMD - self.menorMD)/30,0))
       # print(self.numeroEstacoes)
        
        self.dadosInterpoladosMWD   = np.zeros((self.numeroEstacoes, np.shape(self.dadosOriginaisMWD)[1]))
        self.dadosInterpoladosGWD   = np.zeros((self.numeroEstacoes, np.shape(self.dadosOriginaisGWD)[1]))
        
        self.novaMD = np.zeros((self.numeroEstacoes, 1))
        self.novaMD[0] = self.menorMD
        
        self.novaMD[0] = self.menorMD 
        for contador in range(1,self.numeroEstacoes):
            self.novaMD[contador] = (self.novaMD[contador-1] + 30)
          
    def Interpolar(self):
        
        inclinacaoMWD    = float
        azimulteMWD      = float
        tvdMWD           = float
        inclinacaoGYRO   = float
        azimulteGYRO     = float
        tvdGYRO          = float
        
        for contadorX in range(self.numeroEstacoes):
            
            for contadorY in range(len(self.dadosOriginaisMWD)):
                
                if self.novaMD[contadorX] > self.dadosOriginaisMWD[contadorY-1][0]:
                    
                    if self.novaMD[contadorX] < self.dadosOriginaisMWD[contadorY][0]:
                        
                        inclinacaoMWD = self.dadosOriginaisMWD[contadorY-1][1] + ((self.novaMD[contadorX] - self.dadosOriginaisMWD[contadorY-1][0]) * (self.dadosOriginaisMWD[contadorY][1] - self.dadosOriginaisMWD[contadorY-1][1]) / (self.dadosOriginaisMWD[contadorY][0] - self.dadosOriginaisMWD[contadorY-1][0]))
                         
                        azimulteMWD = self.dadosOriginaisMWD[contadorY-1][2] + ((self.novaMD[contadorX] - self.dadosOriginaisMWD[contadorY-1][0]) * (self.dadosOriginaisMWD[contadorY][2] - self.dadosOriginaisMWD[contadorY-1][2]) / (self.dadosOriginaisMWD[contadorY][0] - self.dadosOriginaisMWD[contadorY-1][0]))
                                      
                        tvdMWD = self.dadosOriginaisMWD[contadorY-1][3] + ((self.novaMD[contadorX] - self.dadosOriginaisMWD[contadorY-1][0]) * (self.dadosOriginaisMWD[contadorY][3] - self.dadosOriginaisMWD[contadorY-1][3]) / (self.dadosOriginaisMWD[contadorY][0] - self.dadosOriginaisMWD[contadorY-1][0]))
    
                        self.dadosInterpoladosMWD[contadorX][0] = self.novaMD[contadorX]
                        self.dadosInterpoladosMWD[contadorX][1] = inclinacaoMWD
                        self.dadosInterpoladosMWD[contadorX][2] = azimulteMWD
                        self.dadosInterpoladosMWD[contadorX][3] = tvdMWD
        
            for contadorZ in range(len(self.dadosOriginaisGWD)):
                
                if self.novaMD[contadorZ] > self.dadosOriginaisGWD[contadorZ-1][0]:
                    
                    if self.novaMD[contadorZ] < self.dadosOriginaisGWD[contadorZ][0]:
                        
                        inclinacaoGYRO = self.dadosOriginaisGWD[contadorZ-1][1] + ((self.novaMD[contadorX] - self.dadosOriginaisGWD[contadorZ-1][0]) * (self.dadosOriginaisGWD[contadorZ][1] - self.dadosOriginaisGWD[contadorZ-1][1]) / (self.dadosOriginaisGWD[contadorZ][0] - self.dadosOriginaisGWD[contadorZ-1][0]))
                        
                        azimulteGYRO = self.dadosOriginaisGWD[contadorZ-1][2] + ((self.novaMD[contadorX] - self.dadosOriginaisGWD[contadorZ-1][0]) *  (self.dadosOriginaisGWD[contadorZ][2] - self.dadosOriginaisGWD[contadorZ-1][2]) /  (self.dadosOriginaisGWD[contadorZ][0] - self.dadosOriginaisGWD[contadorZ-1][0]))
                                                                                
                        tvdGYRO = self.dadosOriginaisGWD[contadorZ-1][3] + ((self.novaMD[contadorX] - self.dadosOriginaisGWD[contadorZ-1][0]) * (self.dadosOriginaisGWD[contadorZ][3] - self.dadosOriginaisGWD[contadorZ-1][3]) / (self.dadosOriginaisGWD[contadorZ][0] - self.dadosOriginaisGWD[contadorZ-1][0]))
                    
                        self.dadosInterpoladosGWD[contadorX][0] = self.novaMD[contadorX]
                        self.dadosInterpoladosGWD[contadorX][1] = inclinacaoGYRO
                        self.dadosInterpoladosGWD[contadorX][2] = azimulteGYRO
                        self.dadosInterpoladosGWD[contadorX][3] = tvdGYRO
                        

class ModeloErroMWD(EntradaDeDados):

    def __init__(self):
        
        super().__init__()
        self.I_MWD = np.zeros((len(self.dadosOriginaisMWD),1))
        self.Azm_MWD = np.zeros((len(self.dadosOriginaisMWD),1))
        self.Md_MWD = np.zeros((len(self.dadosOriginaisMWD),1))
        self.tvd_MWD = np.zeros((len(self.dadosOriginaisMWD),1))
        
        for contador in range(0,len(self.dadosOriginaisMWD)):
            
            self.Md_MWD[contador] = self.dadosOriginaisMWD[contador][0]
            self.I_MWD[contador] = self.dadosOriginaisMWD[contador][1]
            self.Azm_MWD[contador] = self.dadosOriginaisMWD[contador][2]
            self.tvd_MWD[contador] = self.dadosOriginaisMWD[contador][3]
            
        self.ABXY_TI1  = np.zeros((len(self.dadosOriginaisMWD),3))
        self.ABXY_TI2  = np.zeros((len(self.dadosOriginaisMWD),3)) #Função singular em poços verticais
        self.ABZ       = np.zeros((len(self.dadosOriginaisMWD),3))
        self.ASXY_TI1  = np.zeros((len(self.dadosOriginaisMWD),3))
        self.ASXY_TI2  = np.zeros((len(self.dadosOriginaisMWD),3))
        self.ASXY_TI3  = np.zeros((len(self.dadosOriginaisMWD),3))
        self.ASZ       = np.zeros((len(self.dadosOriginaisMWD),3))
        self.ABIXY_TI1 = np.zeros((len(self.dadosOriginaisMWD),3))
        self.ABIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),3)) #Função singular em poços verticais
        self.ABIZ      = np.zeros((len(self.dadosOriginaisMWD),3))
        self.ASIXY_TI1 = np.zeros((len(self.dadosOriginaisMWD),3))
        self.ASIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),3))
        self.ASIXY_TI3 = np.zeros((len(self.dadosOriginaisMWD),3))
        self.ASIZ      = np.zeros((len(self.dadosOriginaisMWD),3))
        
        self.MBXY_TI1  = np.zeros((len(self.dadosOriginaisMWD),3))
        self.MBXY_TI2  = np.zeros((len(self.dadosOriginaisMWD),3))
        self.MBZ       = np.zeros((len(self.dadosOriginaisMWD),3))
        self.MSXY_TI1  = np.zeros((len(self.dadosOriginaisMWD),3))
        self.MSXY_TI2  = np.zeros((len(self.dadosOriginaisMWD),3))   
        self.MSXY_TI3  = np.zeros((len(self.dadosOriginaisMWD),3))
        self.MSZ       = np.zeros((len(self.dadosOriginaisMWD),3))
        self.MBIXY_TI1 = np.zeros((len(self.dadosOriginaisMWD),3))
        self.MBIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),3))
        self.MSIXY_TI1 = np.zeros((len(self.dadosOriginaisMWD),3))
        self.MSIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),3))
        self.MSIXY_TI3 = np.zeros((len(self.dadosOriginaisMWD),3))
        self.MFI       = np.zeros((len(self.dadosOriginaisMWD),3))
        self.MDI       = np.zeros((len(self.dadosOriginaisMWD),3))
        
        self.DREF_R = np.zeros((len(self.dadosOriginaisMWD),3))
        self.DREF_S = np.zeros((len(self.dadosOriginaisMWD),3))
        self.DSF_S  = np.zeros((len(self.dadosOriginaisMWD),3))
        self.DST_G  = np.zeros((len(self.dadosOriginaisMWD),3))
        
        self.DEC  = np.zeros((len(self.dadosOriginaisMWD),3))
        self.DBH  = np.zeros((len(self.dadosOriginaisMWD),3))
        self.SAG  = np.zeros((len(self.dadosOriginaisMWD),3))
        self.AMIC = np.zeros((len(self.dadosOriginaisMWD),3))
        self.AMID = np.zeros((len(self.dadosOriginaisMWD),3))
        self.XYM1 = np.zeros((len(self.dadosOriginaisMWD),3))
        self.XYM2 = np.zeros((len(self.dadosOriginaisMWD),3))
        self.XYM3 = np.zeros((len(self.dadosOriginaisMWD),3))       #Função singular em poços verticais
        self.XYM4 = np.zeros((len(self.dadosOriginaisMWD),3))       #Função singular em poços verticais
                
        self.ErroAcelerometro()
        self.ErroMagnetico()
        self.ErroProfundidade()
        self.ErroDeclinidadeDesalinhamento()
        self.EscreverErrosDisco()
        
    def ErroAcelerometro(self):
            
        for contador in range(0,len(self.dadosOriginaisMWD)):
            
            self.ABXY_TI1[contador] = np.array([0, -np.cos(self.I_MWD[contador])/self.G, np.tan(self.DipMag)*np.cos(self.I_MWD[contador])*np.sin(self.Azm_MWD[contador])/self.G],dtype=object)
            
            if self.I_MWD[contador] <= 0.1:
                
                self.ABXY_TI2[contador] = np.array([-1 * np.sin(self.Azm_MWD[contador])/self.G, np.cos(self.Azm_MWD[contador])/self.G, 0 ],dtype=object)
                
                self.ABIXY_TI2[contador] = np.array([-1 * np.sin(self.Azm_MWD[contador])/self.G, np.cos(self.Azm_MWD[contador])/self.G, 0 ],dtype=object)
                
            else:
                
                self.ABXY_TI2[contador] = np.array([0, 0, np.arctan(self.I_MWD[contador]) - np.tan(self.DipMag)*np.cos(self.Azm_MWD[contador])/self.G],dtype=object)
                
                self.ABIXY_TI2[contador] = np.array([0, 0, -1 * (np.tan(self.DipMag)*np.cos(self.Azm_MWD[contador]) - np.tan(self.I_MWD[contador])) /(self.G * (1 - mt.pow(np.sin(self.I_MWD[contador]),2) * mt.pow(np.sin(self.Azm_MWD[contador]),2)))],dtype=object)
                
            self.ABZ[contador] = np.array([0, -np.sin(self.I_MWD[contador])/self.G, np.tan(self.DipMag)*np.sin(self.I_MWD[contador])*np.sin(self.Azm_MWD[contador])/self.G],dtype=object)
            
            self.ASXY_TI1[contador] = np.array([0, np.sin(self.I_MWD[contador]) * np.cos(self.I_MWD[contador])/mt.sqrt(2),-np.tan(self.DipMag)*np.sin(self.I_MWD[contador])*np.cos(self.I_MWD[contador])*np.sin(self.Azm_MWD[contador])/mt.sqrt(2)],dtype=object)
        
            self.ASXY_TI2[contador]  = np.array([0, np.sin(self.I_MWD[contador]) * np.cos(self.I_MWD[contador])/mt.sqrt(2),-np.tan(self.DipMag)*np.sin(self.I_MWD[contador])*np.cos(self.I_MWD[contador])*np.sin(self.Azm_MWD[contador])/2],dtype=object)
            
            self.ASXY_TI3[contador]  = np.array([0, 0 ,-(np.tan(self.DipMag) * np.sin(self.I_MWD[contador])*np.cos(self.Azm_MWD[contador]) - np.cos(self.I_MWD[contador]))/2],dtype=object)
            
            self.ASZ[contador]       = np.array([0, -np.sin(self.I_MWD[contador]) * np.cos(self.I_MWD[contador]), (np.tan(self.DipMag)*np.sin(self.I_MWD[contador]) * np.cos(self.I_MWD[contador]) * np.sin(self.Azm_MWD[contador]))],dtype=object)
            
            self.MSXY_TI2[contador]  = np.array([0, 0, (np.sin(self.Azm_MWD[contador]) * (np.tan(self.DipMag) * np.cos(self.I_MWD[contador]) * np.sin(self.I_MWD[contador]) - np.cos(self.Azm_MWD[contador]) * mt.pow(np.cos(self.I_MWD[contador]),2) - np.tan(self.DipMag) * np.sin(self.I_MWD[contador]) * np.cos(self.Azm_MWD[contador])))/2],dtype=object)
            
            self.ABIXY_TI1[contador] = np.array([0, np.cos(self.I_MWD[contador])/self.G,  mt.pow(np.cos(self.I_MWD[contador]),2) * np.sin(self.I_MWD[contador])* ( (np.tan(self.DipMag) * np.cos(self.I_MWD[contador]) + np.sin(self.I_MWD[contador]) * np.cos(self.Azm_MWD[contador]))) / self.G * (1 - mt.pow(np.sin(self.I_MWD[contador]),2) * mt.pow(np.sin(self.Azm_MWD[contador]),2))],dtype=object)
            
            self.ABIZ[contador]      = np.array([0, -np.sin(self.I_MWD[contador])/self.G, np.sin(self.I_MWD[contador]) * np.cos(self.I_MWD[contador]) * np.sin(self.Azm_MWD[contador]) * ( np.tan(self.DipMag) * np.cos(self.I_MWD[contador]) + np.cos(self.Azm_MWD[contador]) * np.sin(self.I_MWD[contador])) / (self.G * (1 - mt.pow(np.sin(self.I_MWD[contador]),2) * mt.pow(np.sin(self.Azm_MWD[contador]),2)))],dtype=object)
            
            self.ASIXY_TI1[contador] = np.array([0, np.cos(self.I_MWD[contador]) * np.sin(self.I_MWD[contador])/ mt.sqrt(2), - np.sin(self.I_MWD[contador]) * mt.pow(np.cos(self.I_MWD[contador]),2) * np.sin(self.Azm_MWD[contador]) * ( np.tan(self.DipMag) * np.cos(self.I_MWD[contador]) + np.cos(self.Azm_MWD[contador]) * np.sin(self.I_MWD[contador])) / (mt.sqrt(2) * (1 - mt.pow(np.sin(self.I_MWD[contador]),2) * mt.pow(np.sin(self.Azm_MWD[contador]),2)))],dtype=object)
            
            self.ASIXY_TI2[contador] = np.array([0, np.cos(self.I_MWD[contador]) * np.sin(self.I_MWD[contador])/ mt.sqrt(2), - np.sin(self.I_MWD[contador]) * mt.pow(np.cos(self.I_MWD[contador]),2) * np.sin(self.Azm_MWD[contador]) * ( np.tan(self.DipMag) * np.cos(self.I_MWD[contador]) + np.cos(self.Azm_MWD[contador]) * np.sin(self.I_MWD[contador])) / 2 * (1 - mt.pow(np.sin(self.I_MWD[contador]),2) * mt.pow(np.sin(self.Azm_MWD[contador]),2))],dtype=object)
            
            self.ASIXY_TI3[contador] = np.array([0, 0, - (np.tan(self.DipMag) * np.sin(self.I_MWD[contador]) + np.cos(self.Azm_MWD[contador]) - np.cos(self.I_MWD[contador])) / 2 * (1 - mt.pow(np.sin(self.I_MWD[contador]),2) * mt.pow(np.sin(self.Azm_MWD[contador]),2))],dtype=object)       
            
            self.ASIZ[contador] = np.array([0, - np.sin(self.I_MWD[contador])/np.cos(self.I_MWD[contador]), np.sin(self.I_MWD[contador]) * mt.pow(np.cos(self.I_MWD[contador]),2) * np.sin(self.Azm_MWD[contador]) * ( np.tan(self.DipMag) * np.cos(self.I_MWD[contador]) + np.cos(self.Azm_MWD[contador]) * np.sin(self.I_MWD[contador])) / self.G * (1 - mt.pow(np.sin(self.I_MWD[contador]),2)  * mt.pow(np.sin(self.Azm_MWD[contador]),2))],dtype=object)
        
    def ErroMagnetico(self):
        
        for contador in range(0,len(self.dadosOriginaisMWD)):
        
            self.MBXY_TI1[contador]  =  np.array([0, 0, - np.sin(self.Azm_MWD[contador]) * np.cos(self.I_MWD[contador]) / (self.B * np.cos(self.DipMag)) ],dtype=object)
            
            self.MBXY_TI2[contador]  =  np.array([0, 0,  np.cos(self.Azm_MWD[contador]) / (self.B * np.cos(self.DipMag)) ],dtype=object)
            
            self.MBZ[contador]       =  np.array([0, 0, - np.sin(self.Azm_MWD[contador]) * np.sin(self.I_MWD[contador]) / (self.B * np.cos(self.DipMag))],dtype=object)
            
            self.MSXY_TI1[contador]  =  np.array([0, 0, (np.sin(self.Azm_MWD[contador]) * np.sin(self.I_MWD[contador]) * (np.tan(self.DipMag) * np.cos(self.I_MWD[contador]) + np.sin(self.I_MWD[contador]) *  np.cos(self.Azm_MWD[contador]))) / mt.sqrt(2) ],dtype=object)
                                                                                               
            self.MSXY_TI2[contador]  =  np.array([0, 0, np.sin(self.Azm_MWD[contador]) * ( np.tan(self.DipMag) * np.sin(self.I_MWD[contador]) * np.cos(self.I_MWD[contador]) - mt.pow(np.cos(self.I_MWD[contador]),2) * np.cos(self.Azm_MWD[contador]) - np.cos(self.Azm_MWD[contador])) / 2 ],dtype=object)
            
            self.MSXY_TI3[contador]  =  np.array([0, 0, (np.cos(self.I_MWD[contador]) * mt.pow(np.cos(self.Azm_MWD[contador]),2) - np.cos(self.I_MWD[contador]) * mt.pow(np.sin(self.Azm_MWD[contador]),2) - np.tan(self.DipMag) * np.sin(self.I_MWD[contador])  * np.cos(self.Azm_MWD[contador])) / 2 ],dtype=object) 
            
            self.MSZ[contador]       =  np.array([0, 0, - (np.sin(self.I_MWD[contador]) * np.cos(self.Azm_MWD[contador]) + np.tan(self.DipMag) * np.cos(self.I_MWD[contador])) * np.sin(self.I_MWD[contador]) * np.sin(self.Azm_MWD[contador]) ],dtype=object)
            
            self.MBIXY_TI1[contador] =  np.array([0, 0, - (np.cos(self.I_MWD[contador]) * np.sin(self.Azm_MWD[contador])) / (self.B * np.cos(self.DipMag) * ( 1 - mt.pow(np.sin(self.I_MWD[contador]),2) * mt.pow(np.sin(self.Azm_MWD[contador]),2))) ],dtype=object)
            
            self.MBIXY_TI2[contador] =  np.array([0, 0, np.cos(self.Azm_MWD[contador]) / (self.B * np.cos(self.DipMag) * ( 1 - mt.pow(np.sin(self.I_MWD[contador]),2) * mt.pow(np.sin(self.Azm_MWD[contador]),2))) ],dtype=object)
            
            self.MSIXY_TI1[contador] =  np.array([0, 0, - (np.sin(self.I_MWD[contador]) * np.sin(self.Azm_MWD[contador]) * (np.tan(self.DipMag) * np.cos(self.I_MWD[contador]) + np.sin(self.I_MWD[contador]) * np.cos(self.Azm_MWD[contador]))) / ( mt.sqrt(2) * ( 1 - mt.pow(np.sin(self.I_MWD[contador]),2) * mt.pow(np.sin(self.Azm_MWD[contador]),2))) ],dtype=object)
            
            self.MSIXY_TI2[contador] =  np.array([0, 0, - (np.sin(self.Azm_MWD[contador]) * (np.tan(self.DipMag) * np.sin(self.I_MWD[contador]) *  np.cos(self.I_MWD[contador]) - mt.pow(np.cos(self.I_MWD[contador]),2) * np.cos(self.Azm_MWD[contador] - np.cos(self.Azm_MWD[contador])))) / ( 2 * ( 1 - mt.pow(np.sin(self.I_MWD[contador]),2) * mt.pow(np.sin(self.Azm_MWD[contador]),2))) ],dtype=object)
            
            self.MSIXY_TI3[contador] =  np.array([0, 0, (np.cos(self.I_MWD[contador]) * mt.pow(np.cos(self.Azm_MWD[contador]),2) -  np.cos(self.I_MWD[contador]) * mt.pow(np.sin(self.Azm_MWD[contador]),2) - np.tan(self.DipMag) * np.sin(self.I_MWD[contador]) * np.cos(self.Azm_MWD[contador])) / ( 2 * ( 1 - mt.pow(np.sin(self.I_MWD[contador]),2) * mt.pow(np.sin(self.Azm_MWD[contador]),2))) ],dtype=object)
            
            self.MFI[contador]       =  np.array([0, 0, - (np.sin(self.I_MWD[contador]) * np.sin(self.Azm_MWD[contador]) * ( np.tan(self.DipMag) * np.cos(self.I_MWD[contador]) + np.sin(self.I_MWD[contador]) * np.cos(self.Azm_MWD[contador]))) / ( self.B * ( 1 - mt.pow(np.sin(self.I_MWD[contador]),2) * mt.pow(np.sin(self.Azm_MWD[contador]),2))) ],dtype=object)
            
            self.MDI[contador]       =  np.array([0, 0, - (np.sin(self.I_MWD[contador]) * np.sin(self.Azm_MWD[contador]) * (np.cos(self.I_MWD[contador]) - np.tan(self.DipMag) * np.sin(self.I_MWD[contador]) * np.cos(self.Azm_MWD[contador]))) / ( 1 - mt.pow(np.sin(self.I_MWD[contador]),2) * mt.pow(np.sin(self.Azm_MWD[contador]),2)) ],dtype=object)
        
    def ErroProfundidade(self):
       
        for contador in range(0,len(self.dadosOriginaisMWD)):
                        
            self.DREF_R[contador] = np.array([1, 0, 0])                                    
            self.DREF_S[contador] = np.array([1, 0, 0]) 
            
            self.DSF_S[contador]  = np.array([self.Md_MWD[contador], 0, 0], dtype=object)                               
            self.DST_G[contador]  = np.array([(self.Md_MWD[contador] + self.tvd_MWD[contador] * np.cos(self.I_MWD[contador])) * (self.Md_MWD[contador] - self.Md_MWD[contador - 1 ]), 0, 0], dtype=object) 
            
            #self.DST_G[contador]  = np.array([self.Md_MWD[contador] * self.tvd_MWD[contador], 0, 0], dtype=object) 
            
    def ErroDeclinidadeDesalinhamento(self):           
              
        for contador in range(0,len(self.dadosOriginaisMWD)):          
            
            w12 = np.sin(self.I_MWD[contador])
            
            w34 = np.cos(self.I_MWD[contador])
            
            self.DEC[contador]  =  np.array([0, 0, 1],dtype=object)
            
            self.DBH[contador]  =  np.array([0, 0, 1/(self.B * np.cos(self.DipMag)) ],dtype=object)
                            
            self.SAG[contador]  =  np.array([0, np.sin(self.I_MWD[contador]), 0],dtype=object)
                
            self.AMIC[contador] =  np.array([0, 0, 0])
            
            self.AMID[contador] =  np.array([0, 0, (np.sin(self.I_MWD[contador]) * np.sin(self.Azm_MWD[contador]))/(self.B * np.cos(self.DipMag))],dtype=object)
            
            self.XYM1[contador] =  np.array([0, abs(w12), 0],dtype=object)
            
            self.XYM2[contador] =  np.array([0, 0, - 1],dtype=object)
            
            if self.I_MWD[contador] <= 5:
                
                self.XYM3[contador] =  np.array([1, 0, 0],dtype=object)
            
                self.XYM4[contador] =  np.array([0, 1, 0],dtype=object)
                
            else:

                self.XYM3[contador] =  np.array([0, abs(w34) * np.cos(self.Azm_MWD[contador]), -1 * (abs(w34) * np.sin(self.Azm_MWD[contador]))/np.sin(self.I_MWD[contador])],dtype=object)
            
                self.XYM4[contador] =  np.array([0, abs(w34) * np.sin(self.Azm_MWD[contador]), (abs(w34) * np.cos(self.Azm_MWD[contador]))/np.sin(self.I_MWD[contador])],dtype=object)
            
    def EscreverErrosDisco(self):
    
        df = pd.DataFrame([[self.ABXY_TI1, self.ABXY_TI2, self.ABZ, self.ASXY_TI1  , self.ASXY_TI2  , self.ASXY_TI3  , self.ASZ       , self.ABIXY_TI1 , self.ABIXY_TI2 , self.ABIZ      , self.ASIXY_TI1 , self.ASIXY_TI2 , self.ASIXY_TI3 , self.ASIZ , self.MBXY_TI1  , self.MBXY_TI2  , self.MBZ       , self.MSXY_TI1  , self.MSXY_TI2  , self.MSXY_TI3  , self.MSZ       , self.MBIXY_TI1,  self.MBIXY_TI2 , self.MSIXY_TI1 , self.MSIXY_TI2 , self.MSIXY_TI3 , self.MFI       , self.MDI       , self.DREF_R , self.DREF_S , self.DSF_S  , self.DST_G  , self.DEC  , self.DBH  , self.SAG  , self.AMIC , self.AMID , self.XYM1 , self.XYM2 , self.XYM3 , self.XYM4]], columns=['ABXY_TI1', 'ABXY_TI2', 'ABZ', 'ASXY_TI1', 'ASXY_TI2', 'ASXY_TI3', 'ASZ', 'ABIXY_TI1', 'ABIXY_TI2', 'ABIZ','ASIXY_TI1', 'ASIXY_TI2 ', 'ASIXY_TI3', 'ASIZ', 'MBXY_TI1', 'MBXY_TI2', 'MBZ', 'MSXY_TI1', 'MSXY_TI2', 'MSXY_TI3', 'MSZ', 'MBIXY_TI1',  'MBIXY_TI2', 'MSIXY_TI1', 'MSIXY_TI2', 'MSIXY_TI3', 'MFI', 'MDI', 'DREF_R', 'DREF_S', 'DSF_S', 'DST_G', 'DEC', 'DBH', 'SAG', 'AMIC', 'AMID', 'XYM1', 'XYM2', 'XYM3', 'XYM4'])   
        
        writer = pd.ExcelWriter('Erros__ferramentas_MWD.xlsx')
        
        df.to_excel(writer,'Erros MWD',float_format='%.5f')
        
        writer.save()

class ModeloErroGyro(EntradaDeDados):

    def __init__(self):
        
        super().__init__()

        self.anguloAcelerometro = 0
        self.fatorReducaoRuido = 1

        self.I_GYRO = np.zeros((len(self.dadosOriginaisGWD),1))
        self.Azm_GYRO = np.zeros((len(self.dadosOriginaisGWD),1))
        self.Md_GYRO = np.zeros((len(self.dadosOriginaisGWD),1))
        self.tvd_GYRO = np.zeros((len(self.dadosOriginaisGWD),1))

        for contador in range(0,len(self.dadosOriginaisGWD)):
            
            self.Md_GYRO[contador] = self.dadosOriginaisGWD[contador][0]
            self.I_GYRO[contador] = self.dadosOriginaisGWD[contador][1]
            self.Azm_GYRO[contador] = self.dadosOriginaisGWD[contador][2]
            self.tvd_GYRO[contador] = self.dadosOriginaisGWD[contador][3]      
        
        self.AXYZ_XYB   = np.zeros((len(self.dadosOriginaisGWD),3))
        self.AXYZ_ZB    = np.zeros((len(self.dadosOriginaisGWD),3))
        self.AXYZ_SF    = np.zeros((len(self.dadosOriginaisGWD),3))
        self.AXYZ_MS    = np.zeros((len(self.dadosOriginaisGWD),3))
        self.AXY_B      = np.zeros((len(self.dadosOriginaisGWD),3))
        self.AXY_SF     = np.zeros((len(self.dadosOriginaisGWD),3))
        self.AXY_MS     = np.zeros((len(self.dadosOriginaisGWD),3))  
        self.AXY_GB     = np.zeros((len(self.dadosOriginaisGWD),3))
        
        self.GXYZ_XYB1  = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXYZ_XYB2  = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXYZ_XYRN  = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXYZ_XYG1  = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXYZ_XYG2  = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXYZ_XYG3  = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXYZ_XYG4  = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXYZ_ZB    = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXYZ_ZRN   = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXYZ_ZG1   = np.zeros((len(self.dadosOriginaisGWD),3))  
        self.GXYZ_ZG2   = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXYZ_SF    = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXYZ_MIS   = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXY_B1     = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXY_B2     = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXY_RN     = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXY_G1     = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXY_G2     = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXY_G3     = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXY_G4     = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXY_SF     = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXY_MIS    = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXYZ_GD    = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXYZ_RW    = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXY_GD     = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GXY_RW     = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GZ_GD      = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GZ_RW      = np.zeros((len(self.dadosOriginaisGWD),3))
        self.GZ_GD      = np.zeros((len(self.dadosOriginaisGWD),3))
        
        self.XYM1_GYRO      = np.zeros((len(self.dadosOriginaisGWD),3))
        self.XYM2_GYRO      = np.zeros((len(self.dadosOriginaisGWD),3))
        self.XYM3_GYRO       = np.zeros((len(self.dadosOriginaisGWD),3))
        self.XYM4_GYRO       = np.zeros((len(self.dadosOriginaisGWD),3))
        
        self.VSAG       = np.zeros((len(self.dadosOriginaisGWD),3))

        self.DRF_R      = np.zeros((len(self.dadosOriginaisGWD),3))
        self.DRF_S      = np.zeros((len(self.dadosOriginaisGWD),3))
        self.DSF_W      = np.zeros((len(self.dadosOriginaisGWD),3))
        self.DST_G_GYRO      = np.zeros((len(self.dadosOriginaisGWD),3))
        
                
        self.EXTREF     = np.zeros((len(self.dadosOriginaisGWD),3))
        self.EXTTIE     = np.zeros((len(self.dadosOriginaisGWD),3))
        self.EXTMIS     = np.zeros((len(self.dadosOriginaisGWD),3))
        
        self.ErroAcelerometroGyro()
        self.ErroGyro()
        self.ErroDesalinhamentoGyro()
        self.ErroSagGyro()
        self.ErroProfundidadeGyro()
        self.ErroTieon()
        
    def ErroAcelerometroGyro(self):
                 
        for contador in range(0,len(self.dadosOriginaisGWD)):
            
            self.anguloAcelerometro = self.I_GYRO[contador]
            
            if self.I_GYRO[contador] <= 90:
                k = 1 
            else:
                k = - 1 
            
            self.AXYZ_XYB[contador]   = np.array([0, np.cos(self.I_GYRO[contador]) / self.G ,0],dtype=object)
            
            self.AXYZ_ZB[contador]    = np.array([0, np.sin(self.I_GYRO[contador]) / self.G ,0],dtype=object)
            
            self.AXYZ_SF[contador]    = np.array([0, 1.3 * (np.sin(self.I_GYRO[contador]) * np.cos(self.I_GYRO[contador])) ,0],dtype=object)
            
            self.AXYZ_MS[contador]    = np.array([0, 1 ,0])
            
            self.AXY_B[contador]      = np.array([0, 1 / (self.G * np.cos(1 - k * self.anguloAcelerometro)) ,0],dtype=object)
            
            self.AXY_SF[contador]     = np.array([0, np.tan(self.I_GYRO[contador] * k * self.anguloAcelerometro) ,0],dtype=object)
            
            self.AXY_MS[contador]     = np.array([0, 1 ,0])
            
            self.AXY_GB[contador]     = np.array([0, np.tan(self.I_GYRO[contador] * k * self.anguloAcelerometro) / self.G,0],dtype=object)
            
    def ErroGyro(self):
                
        for contador in range(0,len(self.dadosOriginaisGWD)):
            
            self.GXYZ_XYB1[contador]  = np.array([0, 0, np.sin(self.Azm_GYRO[contador]) * np.cos(self.I_GYRO[contador]) / (self.rotacaoTerra * np.cos(self.Latitude)) ],dtype=object)
                                                  
            self.GXYZ_XYB2[contador]  = np.array([0, 0, np.cos(self.Azm_GYRO[contador]) / (self.rotacaoTerra * np.cos(self.Latitude) )],dtype=object)
                                                  
            self.GXYZ_XYRN[contador]  = np.array([0, 0, self.fatorReducaoRuido * (mt.sqrt(1 - (mt.pow(np.sin(self.Azm_GYRO[contador]),2) * mt.pow(np.sin(self.I_GYRO[contador]),2)))) /( self.rotacaoTerra * np.cos(self.Latitude)) ],dtype=object)
            
            self.GXYZ_XYG1[contador]  = np.array([0, 0, np.cos(self.Azm_GYRO[contador]) * np.sin(self.I_GYRO[contador]) / ( self.rotacaoTerra * np.cos(self.Latitude)) ],dtype=object)
            
            self.GXYZ_XYG2[contador]  = np.array([0, 0, np.cos(self.Azm_GYRO[contador]) * np.cos(self.I_GYRO[contador]) / ( self.rotacaoTerra * np.cos(self.Latitude)) ],dtype=object)
            
            self.GXYZ_XYG3[contador]  = np.array([0, 0, np.sin(self.Azm_GYRO[contador]) * mt.pow(np.cos(self.I_GYRO[contador]),2) / ( self.rotacaoTerra * np.cos(self.Latitude)) ],dtype=object)
            
            self.GXYZ_XYG4[contador]  = np.array([0, 0,  np.sin(self.Azm_GYRO[contador]) * np.sin(self.I_GYRO[contador]) * np.cos(self.I_GYRO[contador]) / ( self.rotacaoTerra * np.cos(self.Latitude)) ],dtype=object)
            
            self.GXYZ_ZB  [contador]  = np.array([0, 0,  np.sin(self.Azm_GYRO[contador]) * np.sin(self.I_GYRO[contador]) / ( self.rotacaoTerra * np.cos(self.Latitude)) ],dtype=object)
            
            self.GXYZ_ZRN [contador]  = np.array([0, 0,  np.sin(self.Azm_GYRO[contador]) * np.sin(self.I_GYRO[contador]) / ( self.rotacaoTerra * np.cos(self.Latitude)) ],dtype=object)
            
            self.GXYZ_ZG1 [contador]  = np.array([0, 0,  np.sin(self.Azm_GYRO[contador]) * mt.pow(np.sin(self.I_GYRO[contador]),2) / ( self.rotacaoTerra * np.cos(self.Latitude)) ],dtype=object)
                                                  
            self.GXYZ_ZG2 [contador]  = np.array([0, 0,  np.sin(self.Azm_GYRO[contador]) * np.sin(self.I_GYRO[contador]) * np.cos(self.I_GYRO[contador]) / ( self.rotacaoTerra * np.cos(self.Latitude)) ],dtype=object)
                                                  
            self.GXYZ_SF  [contador]  = np.array([0, 0,  np.tan(self.Latitude) * np.sin(self.Azm_GYRO[contador]) * np.sin(self.I_GYRO[contador]) * np.cos(self.I_GYRO[contador])],dtype=object)
                                                  
            self.GXYZ_MIS [contador]  = np.array([0, 0, (1/np.cos(self.Latitude)) ],dtype=object)
                                                  
            self.GXY_B1   [contador]  = np.array([0, 0, np.sin(self.Azm_GYRO[contador]) /  ( self.rotacaoTerra * np.cos(self.Latitude) * np.cos(self.I_GYRO[contador])) ],dtype=object)
            
            self.GXY_B2   [contador]  = np.array([0, 0, np.cos(self.Azm_GYRO[contador]) /  ( self.rotacaoTerra * np.cos(self.Latitude)) ],dtype=object)
            
            self.GXY_RN   [contador]  = np.array([0, 0, self.fatorReducaoRuido * (mt.sqrt(1 - (mt.pow(np.cos(self.Azm_GYRO[contador]),2) * mt.pow(np.sin(self.I_GYRO[contador]),2)))) /( self.rotacaoTerra * np.cos(self.Latitude) * np.cos(self.I_GYRO[contador])) ],dtype=object)
                                                  
            self.GXY_G1   [contador]  = np.array([0, 0, np.cos(self.Azm_GYRO[contador]) * np.sin(self.I_GYRO[contador]) / ( self.rotacaoTerra * np.cos(self.Latitude)) ],dtype=object)
            
            self.GXY_G2   [contador]  = np.array([0, 0, np.cos(self.Azm_GYRO[contador]) * np.cos(self.I_GYRO[contador]) / ( self.rotacaoTerra * np.cos(self.Latitude)) ],dtype=object)
            
            self.GXY_G3   [contador]  = np.array([0, 0, np.sin(self.Azm_GYRO[contador]) / ( self.rotacaoTerra * np.cos(self.Latitude)) ],dtype=object)
                                                  
            self.GXY_G4   [contador]  = np.array([0, 0, np.sin(self.Azm_GYRO[contador]) * np.tan(self.I_GYRO[contador]) / ( self.rotacaoTerra * np.cos(self.Latitude)) ],dtype=object)
            
            self.GXY_SF   [contador]  = np.array([0, 0, np.tan(self.I_GYRO[contador]) * np.tan(self.Latitude) * np.sin(self.Azm_GYRO[contador]) ],dtype=object)
                                                  
            self.GXY_MIS  [contador]  = np.array([0, 0, (1 / (np.cos(self.Latitude) * np.cos(self.I_GYRO[contador]))) ],dtype=object)  
              
    def ErroDesalinhamentoGyro(self):

        for contador in range(0,len(self.dadosOriginaisGWD)):
            
            w12 = np.sin(self.I_GYRO[contador])
            w34 = np.cos(self.I_GYRO[contador])
            
            self.XYM1_GYRO[contador]  = np.array([0, abs(w12), 0],dtype=object)
            
            self.XYM2_GYRO[contador]  = np.array([0, 0, - 1],dtype=object) 

            if self.I_GYRO[contador] <= 5:
                    
                self.XYM3_GYRO[contador] =  np.array([1, 0, 0],dtype=object)
                
                self.XYM4_GYRO[contador] =  np.array([0, 1, 0],dtype=object)
                    
            else:
                    
                self.XYM3_GYRO[contador]  = np.array([0, abs(w34) * np.cos(self.Azm_GYRO[contador]), -1 * (abs(w34) * np.sin(self.Azm_GYRO[contador]))/np.sin(self.I_GYRO[contador])],dtype=object)
            
            
                self.XYM4_GYRO[contador]  = np.array([0, abs(w34) * np.sin(self.Azm_GYRO[contador]), (abs(w34) * np.cos(self.Azm_GYRO[contador]))/np.sin(self.I_GYRO[contador])],dtype=object)
            
    def ErroSagGyro(self):
          
        for contador in range(0,len(self.dadosOriginaisGWD)):
            
            self.VSAG[contador]  = np.array([0, np.sin(self.I_GYRO[contador]), 0],dtype=object)
    
    def ErroProfundidadeGyro(self):
            
        for contador in range(0,len(self.dadosOriginaisGWD)):
            
            self.tvd_GYRO[contador] = self.Md_GYRO[contador]
            
            self.DRF_R[contador]      = np.array([1, 0, 0])
            self.DRF_S[contador]      = np.array([1, 0, 0])
            self.DSF_W[contador]      = np.array([self.Md_GYRO[contador], 0, 0], dtype=object)   
            self.DST_G_GYRO[contador] = np.array([(self.Md_GYRO[contador] + self.tvd_GYRO[contador] * np.cos(self.I_GYRO[contador])) * (self.Md_GYRO[contador] - self.Md_GYRO[contador - 1 ]), 0, 0], dtype=object) 
            
    def  ErroTieon(self):
        
        for contador in range(0,len(self.dadosOriginaisGWD)):
            
            self.EXTREF[contador]  = np.array([0, 0, 1])
    
            self.EXTTIE[contador]  = np.array([0, 0, 1])
            
            self.EXTMIS[contador]  = np.array([0, 0, 1],dtype=object) #/np.sin(self.I_GYRO[contador])],dtype=object)                   

class EfeitoErroSurveyMWD(ModeloErroMWD):

    def __init__(self):
        
        super().__init__()
        
        self.drk_dpk_MWD = np.zeros((len(self.dadosOriginaisMWD),3,3,1),dtype=np.float64)
        self.drk_dpk1_MWD = np.zeros((len(self.dadosOriginaisMWD),3,3,1),dtype=np.float64)
        self.efeitoErroSurveyMWD = np.zeros((len(self.dadosOriginaisMWD),3,3,1),dtype=np.float64)
        
        self.EfeitoSurveyEstacaoK_MWD()
        self.EfeitoSurveyEstacaoK1_MWD()
        self.EfeitoSurveyEstacaoTotal_MWD()
        
    def EfeitoSurveyEstacaoK_MWD(self):
        
        drk_dDk_MWD = np.zeros((len(self.dadosOriginaisMWD),3,1),dtype=np.float64)
        drk_dIk_MWD = np.zeros((len(self.dadosOriginaisMWD),3,1),dtype=np.float64)
        drk_dAk_MWD = np.zeros((len(self.dadosOriginaisMWD),3,1),dtype=np.float64)
        
        for contador in range(1,len(self.dadosOriginaisMWD)):
            
            drk_dDk_MWD[contador] = np.array([(np.sin(self.I_MWD[contador - 1]) * np.cos(self.Azm_MWD[contador - 1]) + np.sin(self.I_MWD[contador]) * np.cos(self.Azm_MWD[contador])), (np.sin(self.I_MWD[contador - 1]) * np.cos(self.Azm_MWD[contador - 1]) + np.sin(self.I_MWD[contador]) * np.sin(self.Azm_MWD[contador])), (np.cos(self.I_MWD[contador - 1]) + np.cos(self.I_MWD[contador]))])
            
            drk_dIk_MWD[contador] = np.array([ ((self.Md_MWD[contador] - self.Md_MWD[contador-1]) * np.cos(self.I_MWD[contador]) * np.cos(self.Azm_MWD[contador])), ((self.Md_MWD[contador] - self.Md_MWD[contador - 1]) * np.cos(self.I_MWD[contador]) * np.sin(self.Azm_MWD[contador])), (-1 * (self.Md_MWD[contador] - self.Md_MWD[contador - 1]) * np.sin(self.I_MWD[contador])) ])
                                    
            drk_dAk_MWD[contador] = np.array([ (-(self.Md_MWD[contador] - self.Md_MWD[contador-1]) * np.sin(self.I_MWD[contador]) * np.sin(self.Azm_MWD[contador])),((self.Md_MWD[contador]-self.Md_MWD[contador - 1]) * np.sin(self.I_MWD[contador]) * np.cos(self.Azm_MWD[contador])), [0]])

            self.drk_dpk_MWD[contador] = 0.5 * np.array([drk_dDk_MWD[contador],drk_dIk_MWD[contador],drk_dAk_MWD[contador]])
        
        df = pd.DataFrame([[drk_dDk_MWD, drk_dIk_MWD, drk_dAk_MWD, self.drk_dpk_MWD]], columns=['drk_dDk_MWD','drk_dIk_MWD','drk_dAk_MWD','self.drk_dpk_MWD'])
        
        writer = pd.ExcelWriter('EfeitoErro-MD-Inc-Azm-MWD_k.xlsx')
        
        df.to_excel(writer,'Efeito MWD',float_format='%.5f')
        
        writer.save()
        
    def EfeitoSurveyEstacaoK1_MWD(self):
        
        drk_dDk1_MWD = np.zeros((len(self.dadosOriginaisMWD),3,1))
        drk_dIk1_MWD = np.zeros((len(self.dadosOriginaisMWD),3,1))
        drk_dAk1_MWD = np.zeros((len(self.dadosOriginaisMWD),3,1))
         
        for contador in range(0,len(self.dadosOriginaisMWD) - 1):
            
            drk_dDk1_MWD[contador + 1] = np.array([(-1 *(np.sin(self.I_MWD[contador]) * np.cos(self.Azm_MWD[contador])) - np.sin(self.I_MWD[contador + 1]) * np.cos(self.Azm_MWD[contador + 1])), (- np.sin(self.I_MWD[contador]) * np.sin(self.Azm_MWD[contador]) - np.sin(self.I_MWD[contador + 1]) * np.sin(self.Azm_MWD[contador + 1])), (- np.cos(self.I_MWD[contador]) - np.cos(self.I_MWD[contador + 1]))])
            
            drk_dIk1_MWD[contador + 1] = np.array([ ((self.Md_MWD[contador + 1] - self.Md_MWD[contador]) * np.cos(self.I_MWD[contador + 1]) * np.cos(self.Azm_MWD[contador + 1])), ((self.Md_MWD[contador + 1] - self.Md_MWD[contador]) * np.cos(self.I_MWD[contador + 1]) * np.sin(self.Azm_MWD[contador + 1])), (-1 * (self.Md_MWD[contador + 1] - self.Md_MWD[contador]) * np.sin(self.I_MWD[contador + 1])) ])
                                    
            drk_dAk1_MWD[contador + 1] = np.array([ (-1 * (self.Md_MWD[contador + 1] - self.Md_MWD[contador]) * np.sin(self.I_MWD[contador + 1]) * np.sin(self.Azm_MWD[contador + 1])),((self.Md_MWD[contador + 1] - self.Md_MWD[contador]) * np.sin(self.I_MWD[contador + 1]) * np.cos(self.Azm_MWD[contador + 1])), [0]])

            self.drk_dpk1_MWD[contador] = 0.5 * np.array([drk_dDk1_MWD[contador],drk_dIk1_MWD[contador],drk_dAk1_MWD[contador]])
        
        df = pd.DataFrame([[drk_dDk1_MWD, drk_dIk1_MWD, drk_dAk1_MWD, self.drk_dpk1_MWD]], columns=['drk_dDk1_MWD','drk_dIk1_MWD','drk_dAk1_MWD','self.drk_dpk1_MWD'])
        
        writer = pd.ExcelWriter('EfeitoErro-MD-Inc-Azm-MWD_k1.xlsx')
        
        df.to_excel(writer,'Efeito MWD',float_format='%.5f')
        
        writer.save()
        
    def EfeitoSurveyEstacaoTotal_MWD(self):
        
        for contador in range(0,len(self.dadosOriginaisMWD)-1):
            
            
            self.efeitoErroSurveyMWD[contador] = self.drk_dpk1_MWD[contador] + self.drk_dpk_MWD[contador]   
            
        self.efeitoErroSurveyMWD[len(self.dadosOriginaisMWD)-1] = self.drk_dpk_MWD[len(self.dadosOriginaisMWD)-1]
        
        df = pd.DataFrame([[[self.efeitoErroSurveyMWD]]])
        
        writer = pd.ExcelWriter('EfeitoErroSurveyMWD.xlsx')
        
        df.to_excel(writer,'Efeito MWD',float_format='%.5f')
        
        writer.save()
        
        
class EfeitoErroSurveyGWD(ModeloErroGyro):

    def __init__(self):
        
        super().__init__()
        
        self.drk_dpk_GYRO = np.zeros((len(self.dadosOriginaisGWD),3,3,1),dtype=np.float64)
        self.drk_dpk1_GYRO = np.zeros((len(self.dadosOriginaisGWD),3,3,1),dtype=np.float64)
        self.efeitoErroSurveyGWD = np.zeros((len(self.dadosOriginaisGWD),3,3,1),dtype=np.float64)
        
        self.EfeitoSurveyEstacaoK_GYRO()
        self.EfeitoSurveyEstacaoK1_GYRO()
        self.EfeitoSurveyEstacaoTotal_GYRO()
        
    def EfeitoSurveyEstacaoK_GYRO(self):
        
        drk_dDk_GYRO = np.zeros((len(self.dadosOriginaisGWD),3,1),dtype=np.float64)
        drk_dIk_GYRO = np.zeros((len(self.dadosOriginaisGWD),3,1),dtype=np.float64)
        drk_dAk_GYRO = np.zeros((len(self.dadosOriginaisGWD),3,1),dtype=np.float64)
         
        for contador in range(1,len(self.dadosOriginaisGWD)):
            
            drk_dDk_GYRO[contador] = np.array([(np.sin(self.I_GYRO[contador - 1]) * np.cos(self.Azm_GYRO[contador - 1]) + np.sin(self.I_GYRO[contador]) * np.cos(self.Azm_GYRO[contador])), (np.sin(self.I_GYRO[contador - 1]) * np.cos(self.Azm_GYRO[contador - 1]) + np.sin(self.I_GYRO[contador]) * np.sin(self.Azm_GYRO[contador])), (np.cos(self.I_GYRO[contador - 1]) + np.cos(self.I_GYRO[contador]))])
            
            drk_dIk_GYRO[contador] = np.array([ ((self.Md_GYRO[contador] - self.Md_GYRO[contador-1]) * np.cos(self.I_GYRO[contador]) * np.cos(self.Azm_GYRO[contador])), ((self.Md_GYRO[contador] - self.Md_GYRO[contador - 1]) * np.cos(self.I_GYRO[contador]) * np.sin(self.Azm_GYRO[contador])), (-1 * (self.Md_GYRO[contador] - self.Md_GYRO[contador - 1]) * np.sin(self.I_GYRO[contador])) ])
                                    
            drk_dAk_GYRO[contador] = np.array([ (-(self.Md_GYRO[contador] - self.Md_GYRO[contador-1]) * np.sin(self.I_GYRO[contador]) * np.sin(self.Azm_GYRO[contador])),((self.Md_GYRO[contador]-self.Md_GYRO[contador - 1]) * np.sin(self.I_GYRO[contador]) * np.cos(self.Azm_GYRO[contador])), [0]])

            self.drk_dpk_GYRO[contador] = 0.5 * np.array([drk_dDk_GYRO[contador],drk_dIk_GYRO[contador],drk_dAk_GYRO[contador]])
    
    def EfeitoSurveyEstacaoK1_GYRO(self):
        
        drk_dDk1_GYRO = np.zeros((len(self.dadosOriginaisGWD),3,1),dtype=np.float64)
        drk_dIk1_GYRO = np.zeros((len(self.dadosOriginaisGWD),3,1),dtype=np.float64)
        drk_dAk1_GYRO = np.zeros((len(self.dadosOriginaisGWD),3,1),dtype=np.float64)
         
        for contador in range(0,len(self.dadosOriginaisGWD) - 1):
            
            drk_dDk1_GYRO[contador + 1] = np.array([(-1 *(np.sin(self.I_GYRO[contador]) * np.cos(self.Azm_GYRO[contador])) - np.sin(self.I_GYRO[contador + 1]) * np.cos(self.Azm_GYRO[contador + 1])), (- np.sin(self.I_GYRO[contador]) * np.sin(self.Azm_GYRO[contador]) - np.sin(self.I_GYRO[contador + 1]) * np.sin(self.Azm_GYRO[contador + 1])), (- np.cos(self.I_GYRO[contador]) - np.cos(self.I_GYRO[contador + 1]))])
            
            drk_dIk1_GYRO[contador + 1] = np.array([ ((self.Md_GYRO[contador + 1] - self.Md_GYRO[contador]) * np.cos(self.I_GYRO[contador + 1]) * np.cos(self.Azm_GYRO[contador + 1])), ((self.Md_GYRO[contador + 1] - self.Md_GYRO[contador]) * np.cos(self.I_GYRO[contador + 1]) * np.sin(self.Azm_GYRO[contador + 1])), (-1 * (self.Md_GYRO[contador + 1] - self.Md_GYRO[contador]) * np.sin(self.I_GYRO[contador + 1])) ])
                                    
            drk_dAk1_GYRO[contador + 1] = np.array([ (-1 * (self.Md_GYRO[contador + 1] - self.Md_GYRO[contador]) * np.sin(self.I_GYRO[contador + 1]) * np.sin(self.Azm_GYRO[contador + 1])),((self.Md_GYRO[contador + 1] - self.Md_GYRO[contador]) * np.sin(self.I_GYRO[contador + 1]) * np.cos(self.Azm_GYRO[contador + 1])), [0]])

            self.drk_dpk1_GYRO[contador] = 0.5 * np.array([drk_dDk1_GYRO[contador],drk_dIk1_GYRO[contador],drk_dAk1_GYRO[contador]])
            
    def EfeitoSurveyEstacaoTotal_GYRO(self):
        
        for contador in range(0,len(self.dadosOriginaisGWD) - 1):
            
            self.efeitoErroSurveyGWD[contador] = self.drk_dpk1_GYRO[contador] + self.drk_dpk_GYRO[contador]

        self.efeitoErroSurveyGWD[len(self.dadosOriginaisGWD)-1] = self.drk_dpk_GYRO[len(self.dadosOriginaisGWD)-1]
        

class TamanhoErroSurveyMWD(EfeitoErroSurveyMWD):
    
    def __init__(self):
        
        super().__init__()
        
        #Magnitude comum aos erros randomicos e sistematicos
        self.Mag_ASXY_TI2 = 0.0005 #ms-2
        self.Mag_ABXY_TI2 = 0.004  #Função singular quando vertical
        self.Mag_ABZ = 0.004
        self.Mag_ASXY_TI3 = 0.0005
        self.Mag_MBXY_TI1 = 70      #nT
        self.Mag_MBXY_TI2 = 70      #nT
        self.Mag_MSXY_TI2 = 0.0016  
        self.Mag_MSXY_TI3 = 0.0016
        self.Mag_XYM1 = 0.06        #°
        self.Mag_XYM2 = 0.06        #°
        self.Mag_XYM3 = 0.06        #° /Função singular quando vertical
        self.Mag_XYM4 = 0.06        #° /Função singular quando vertical
        
        #Magnitude comum aos erros randomicos e sistematicos com correção axial
        if (self.correcaoAxial) == 0:

            self.Mag_ABIXY_TI1 = 0.004  #ms-2
            self.Mag_ABIXY_TI2 = 0.004  #ms-2 /Função singular quando vertical
            self.Mag_ASIXY_TI2 = 0.0005
            self.Mag_ASIXY_TI3 = 0.0005
            self.Mag_MBIXY_TI1 = 70     #nT
            self.Mag_MBIXY_TI2 = 70     #nT
            self.Mag_MSIXY_TI2 = 0.0016
            self.Mag_MSIXY_TI3 = 0.0016
        
        #Magnitude dos erros randomicos
        self.Mag_ABXY_TI1 = 0.004       #ms-2
        
        #Magnitude dos erros Randomicos com correção de acordo com a plataforma
        
        if self.plataformaFixa==0:
            
            #Erro Randomico plataforma fixa
            
            self.Mag_DREF_R = 0.035     #n
        else:
            #Erro Randomico plataforma flutuante
            
            self.Mag_DREF_R = 2.20      #m
        
        #Magnitude dos Erros Sistematicos
        self.Mag_ASZ       = 0.004      #ms-2
        self.Mag_MBZ       = 70         #nT
        self.Mag_MSXY_TI1  = 0.0016
        self.Mag_MSZ       = 0.0016
        self.Mag_SAG       = 0.2        #˚
        self.Mag_AMID      = 220        #nT
        self.Mag_DSF_S     = 5.6 * mt.pow(10,-4)
        
        #Magnitude dos Erros sistematicos com correção Axial 
        if (self.correcaoAxial) == 0:
            self.Mag_ABIZ      = 0.004      #ms-2
            self.Mag_ASIXY_TI1 = 0.0005
            self.Mag_ASIZ      = 0.0005
            self.Mag_MSIXY_TI1 = 0.0016     #nT
        
        #Magnitude dos erros Sistematicos com correção de acordo com a plataforma
        if self.plataformaFixa==0:
            #Erro Sistematico
            self.Mag_DREF_S    = 0.00 #m
        else:
            #Erro Sistematico
            self.Mag_DREF_S    = 1.00 #m
        
        #Vetores erro Globais/Well por Estação
        self.Mag_DEC   = 0.36 #˚
        self.Mag_DBH   = 5000 #nT
        self.Mag_DST_G = 2.5 * mt.pow(10,-7) #m-1
        
        #Magnitude dos Erros globais/well com correção Axial 
        if (self.correcaoAxial) == 0:
            self.Mag_MFI   = 130  #nT
            self.Mag_MDI   = 0.20 #˚

        #Vetores erro Randomico por Estação
        self.RtamanhoErroABXY_TI1  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroABXY_TI2  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64) #Função singular
        self.RtamanhoErroASXY_TI2  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroASXY_TI3  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroMBXY_TI1  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroMBXY_TI2  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroMSXY_TI2  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroMSXY_TI3  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroXYM1      = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroXYM2      = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroDREF_R    = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroABIXY_TI1 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroASIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroASIXY_TI3 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroMBIXY_TI1 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroMBIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroMSIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroMSIXY_TI3 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        
        #Vetores erro Randomico TOTAL por Estação
        self.Rtamanho_Total_ErroABXY_TI1  = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Rtamanho_Total_ErroABXY_TI2  = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Rtamanho_Total_ErroASXY_TI2  = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Rtamanho_Total_ErroASXY_TI3  = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Rtamanho_Total_ErroMBXY_TI1  = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Rtamanho_Total_ErroMBXY_TI2  = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Rtamanho_Total_ErroMSXY_TI2  = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Rtamanho_Total_ErroMSXY_TI3  = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Rtamanho_Total_ErroXYM1      = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Rtamanho_Total_ErroXYM2      = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Rtamanho_Total_ErroDREF_R    = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Rtamanho_Total_ErroABIXY_TI1 = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Rtamanho_Total_ErroASIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Rtamanho_Total_ErroASIXY_TI3 = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Rtamanho_Total_ErroMBIXY_TI1 = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Rtamanho_Total_ErroMBIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Rtamanho_Total_ErroMSIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Rtamanho_Total_ErroMSIXY_TI3 = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        
        #Matriz soma dos erros Randomicos por estação
        self.ErroRandomicoTotal = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        
        #Vetores erro Sistematico por Estação
        self.StamanhoErroASXY_TI2  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroASXY_TI3  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroASZ       = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroMBXY_TI1  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroMBXY_TI2  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroMBZ       = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroMSXY_TI1  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroMSXY_TI2  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroMSXY_TI3  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroMSZ       = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroSAG       = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroAMID      = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroXYM1      = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroXYM2      = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroXYM3      = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroXYM4      = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroABIXY_TI1 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroABIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroABIZ      = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroASIXY_TI1 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroASIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroASIXY_TI3 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroASIZ      = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroABZ       = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroMBIXY_TI1 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroMBIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroMSIXY_TI1 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroMSIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroMSIXY_TI3 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroDREF_S    = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.StamanhoErroDSF_S     = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        
        #Vetores erro Sistematico total por Estação
        self.Stamanho_Total_ErroASXY_TI2  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroASXY_TI3  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroASZ       = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroMBXY_TI1  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroMBXY_TI2  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroMBZ       = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroMSXY_TI1  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroMSXY_TI2  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroMSXY_TI3  = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroMSZ       = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroSAG       = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroAMID      = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroXYM1      = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroXYM2      = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroXYM3      = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroXYM4      = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroABIXY_TI1 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroABIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroABIZ      = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroASIXY_TI1 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroASIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroASIXY_TI3 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroASIZ      = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroABZ       = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroMBIXY_TI1 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroMBIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroMSIXY_TI1 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroMSIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroMSIXY_TI3 = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroDREF_S    = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Stamanho_Total_ErroDSF_S     = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        
        #Produto entre vetor por erro e sua matriz transposta por estação
        self.Stamanho_Produto_ErroASXY_TI2  = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroASXY_TI3  = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroASZ       = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroMBXY_TI1  = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroMBXY_TI2  = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroMBZ       = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroMSXY_TI1  = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroMSXY_TI2  = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroMSXY_TI3  = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroMSZ       = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroSAG       = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroAMID      = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroXYM1      = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroXYM2      = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroXYM3      = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroXYM4      = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroABIXY_TI1 = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroABIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroABIZ      = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroASIXY_TI1 = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroASIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroASIXY_TI3 = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroASIZ      = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroABZ       = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroMBIXY_TI1 = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroMBIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroMSIXY_TI1 = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroMSIXY_TI2 = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroMSIXY_TI3 = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroDREF_S    = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Stamanho_Produto_ErroDSF_S     = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        
        #Matriz soma dos erros Sistematicos por estação
        self.ErroSistematicoTotal = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        
        #Vetores erro Globais/Well por Estação
        self.WtamanhoErroDEC   = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.WtamanhoErroDBH   = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.WtamanhoErroMFI   = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.WtamanhoErroMDI   = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.WtamanhoErroDST_G = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        
        #Vetores erro Globais/Well TOTAL por estação 
        self.Wtamanho_Total_ErroDEC   = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Wtamanho_Total_ErroDBH   = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Wtamanho_Total_ErroMFI   = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Wtamanho_Total_ErroMDI   = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        self.Wtamanho_Total_ErroDST_G = np.zeros((len(self.dadosOriginaisMWD),1,3,1),dtype=np.float64)
        
        #Vetores erro Globais/Well TOTAL por estação 
        self.Wtamanho_Produto_ErroDEC   = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Wtamanho_Produto_ErroDBH   = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Wtamanho_Produto_ErroMFI   = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Wtamanho_Produto_ErroMDI   = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        self.Wtamanho_Produto_ErroDST_G = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        
        #Matriz soma dos erros Globais/Well por estação
        self.ErroWellTotal = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        
        #Matriz soma dos erros Randomicos, sistematicos, globais/well total por estação
        self.ErroTotalMWD = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        
        self.ErroRandomicoMWD()
        self.ErroSistematicoMWD()
        self.ErroWellMWD()
        self.ErroSurveyMWD()

    def ErroRandomicoMWD(self):
        
        for Estacao in range(0,len(self.dadosOriginaisMWD)):    
            for coluna in range(0,1):
                for linha in range(0,3):
                    
                    #Erro acelerometro
                    self.RtamanhoErroABXY_TI1[Estacao][coluna][linha] = self.Mag_ABXY_TI1 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.ABXY_TI1[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.ABXY_TI1[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.ABXY_TI1[Estacao][coluna + 2]))
                    
                    if self.I_MWD[Estacao] <= 5:
                        
                        if Estacao == 0:
                            
                            MDauxiliar = 0.0
                            self.RtamanhoErroABXY_TI2[Estacao][coluna][linha] = self.Mag_ABXY_TI2 * 0.5 * ((self.Md_MWD[Estacao + 1] - MDauxiliar) * (self.ABXY_TI2[Estacao][coluna]))
                        elif Estacao == len(self.dadosOriginaisMWD):
                            MDauxiliar = self.Md_MWD[Estacao - 1]
                            self.RtamanhoErroABXY_TI2[Estacao][coluna][linha] = self.Mag_ABXY_TI2 * 0.5 * ((self.Md_MWD[Estacao] - MDauxiliar) * (self.ABXY_TI2[Estacao][coluna]))
                        else:
                            MDauxiliar = self.Md_MWD[Estacao - 1]
                            self.RtamanhoErroABXY_TI2[Estacao][coluna][linha] = self.Mag_ABXY_TI2 * 0.5 * ((self.Md_MWD[Estacao + 1] - MDauxiliar) * (self.ABXY_TI2[Estacao][coluna]))
                            
                    else:
                        
                        self.RtamanhoErroABXY_TI2[Estacao][coluna][linha] = self.Mag_ABXY_TI2 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.ABXY_TI2[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.ABXY_TI2[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.ABXY_TI2[Estacao][coluna + 2]))
                        
                    #Erro acelerometro
                    self.RtamanhoErroASXY_TI2[Estacao][coluna][linha] = self.Mag_ASXY_TI2 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.ASXY_TI2[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.ASXY_TI2[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.ASXY_TI2[Estacao][coluna + 2]))
                    #Erro acelerometro
                    self.RtamanhoErroASXY_TI3[Estacao][coluna][linha] = self.Mag_ASXY_TI3 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.ASXY_TI3[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.ASXY_TI3[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.ASXY_TI3[Estacao][coluna + 2]))
                    #Erro magnetometro
                    self.RtamanhoErroMBXY_TI1[Estacao][coluna][linha] = self.Mag_MBXY_TI1 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.MBXY_TI1[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MBXY_TI1[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MBXY_TI1[Estacao][coluna + 2]))                
                    #Erro magnetometro
                    self.RtamanhoErroMBXY_TI2[Estacao][coluna][linha] = self.Mag_MBXY_TI2 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.MBXY_TI2[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MBXY_TI2[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MBXY_TI2[Estacao][coluna + 2]))                    
                    
                    self.RtamanhoErroMSXY_TI2[Estacao][coluna][linha] = self.Mag_MSXY_TI2* ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.MSXY_TI2[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MSXY_TI2[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MSXY_TI2[Estacao][coluna + 2]))                    
                    #Erro magnetometro
                    self.RtamanhoErroMSXY_TI3[Estacao][coluna][linha] = self.Mag_MSXY_TI3 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.MSXY_TI3[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MSXY_TI3[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MSXY_TI3[Estacao][coluna + 2]))                 
                    #Erro desalinhamento
                    self.RtamanhoErroXYM1[Estacao][coluna][linha] = self.Mag_XYM1 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.XYM1[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.XYM1[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.XYM1[Estacao][coluna + 2]))
                    
                    #Erro desalinhamento
                    self.RtamanhoErroXYM2[Estacao][coluna][linha] = self.Mag_XYM2 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.XYM2[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.XYM2[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.XYM2[Estacao][coluna + 2]))
                    
                    #Erro Profundidade
                    self.RtamanhoErroDREF_R[Estacao][coluna][linha] = self.Mag_DREF_R * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.DREF_R[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.DREF_R[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.DREF_R[Estacao][coluna + 2]))
                    
                    #Erros da correção Axial
                    if self.correcaoAxial == 0:
                        
                        #Erro acelerometro
                        self.RtamanhoErroABIXY_TI1[Estacao][coluna][linha] = self.Mag_ABIXY_TI1 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.ABIXY_TI1[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.ABIXY_TI1[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.ABIXY_TI1[Estacao][coluna + 2]))
                        
                        #Erro acelerometro
                        self.RtamanhoErroASIXY_TI2[Estacao][coluna][linha] = self.Mag_ASIXY_TI2 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.ASIXY_TI2[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.ASIXY_TI2[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.ASIXY_TI2[Estacao][coluna + 2]))
                        
                        #Erro acelerometro
                        self.RtamanhoErroASIXY_TI3[Estacao][coluna][linha] = self.Mag_ASIXY_TI3 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.ASIXY_TI3[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.ASIXY_TI3[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.ASIXY_TI3[Estacao][coluna + 2]))
                        
                        #Erro magnetometro
                        self.RtamanhoErroMBIXY_TI1[Estacao][coluna][linha] = self.Mag_MBIXY_TI1 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.MBIXY_TI1[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MBIXY_TI1[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MBIXY_TI1[Estacao][coluna + 2]))
                        
                        #Erro magnetometro
                        self.RtamanhoErroMBIXY_TI2[Estacao][coluna][linha] = self.Mag_MBIXY_TI2 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.MBIXY_TI2[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MBIXY_TI2[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MBIXY_TI2[Estacao][coluna + 2]))
                        
                        #Erro magnetometro
                        self.RtamanhoErroMSIXY_TI2[Estacao][coluna][linha] = self.Mag_MSIXY_TI2 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.MSIXY_TI2[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MSIXY_TI2[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MSIXY_TI2[Estacao][coluna + 2]))
                        
                        #Erro magnetometro
                        self.RtamanhoErroMSIXY_TI3[Estacao][coluna][linha] = self.Mag_MSIXY_TI3 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha] * self.MSIXY_TI3[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MSIXY_TI3[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MSIXY_TI3[Estacao][coluna + 2]))              
                        

        for Estacao in range(0,len(self.dadosOriginaisMWD)):
            for linha in range(0,3):
                for coluna in range(0,3):
                    
                    self.Rtamanho_Total_ErroABXY_TI1[Estacao][0][linha][coluna] = self.RtamanhoErroABXY_TI1[Estacao][0][linha] *  self.RtamanhoErroABXY_TI1[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroABXY_TI2[Estacao][0][linha][coluna] = self.RtamanhoErroABXY_TI2[Estacao][0][linha] *  self.RtamanhoErroABXY_TI2[Estacao][0][coluna]

                    self.Rtamanho_Total_ErroASXY_TI2[Estacao][0][linha][coluna] = self.RtamanhoErroASXY_TI2[Estacao][0][linha] *  self.RtamanhoErroASXY_TI2[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroASXY_TI3[Estacao][0][linha][coluna] = self.RtamanhoErroASXY_TI3[Estacao][0][linha] *  self.RtamanhoErroASXY_TI3[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroMBXY_TI1[Estacao][0][linha][coluna] = self.RtamanhoErroMBXY_TI1[Estacao][0][linha] *  self.RtamanhoErroMBXY_TI1[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroMBXY_TI2[Estacao][0][linha][coluna] = self.RtamanhoErroMBXY_TI2[Estacao][0][linha] *  self.RtamanhoErroMBXY_TI2[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroMSXY_TI2[Estacao][0][linha][coluna] = self.RtamanhoErroMSXY_TI2[Estacao][0][linha] *  self.RtamanhoErroMSXY_TI2[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroMSXY_TI3[Estacao][0][linha][coluna] = self.RtamanhoErroMSXY_TI3[Estacao][0][linha] *  self.RtamanhoErroMSXY_TI3[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroXYM1[Estacao][0][linha][coluna] = self.RtamanhoErroXYM1[Estacao][0][linha] *  self.RtamanhoErroXYM1[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroXYM2[Estacao][0][linha][coluna] = self.RtamanhoErroXYM2[Estacao][0][linha] *  self.RtamanhoErroXYM2[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroDREF_R[Estacao][0][linha][coluna] = self.RtamanhoErroDREF_R[Estacao][0][linha] *  self.RtamanhoErroDREF_R[Estacao][0][coluna]                 
                    
                    self.Rtamanho_Total_ErroABIXY_TI1[Estacao][0][linha][coluna] = self.RtamanhoErroABIXY_TI1[Estacao][0][linha] *  self.RtamanhoErroABIXY_TI1[Estacao][0][coluna]                  
                    
                    self.Rtamanho_Total_ErroASIXY_TI2[Estacao][0][linha][coluna] = self.RtamanhoErroASIXY_TI2[Estacao][0][linha] *  self.RtamanhoErroASIXY_TI2[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroASIXY_TI3[Estacao][0][linha][coluna] = self.RtamanhoErroASIXY_TI3[Estacao][0][linha] *  self.RtamanhoErroASIXY_TI3[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroMBIXY_TI1[Estacao][0][linha][coluna] = self.RtamanhoErroMBIXY_TI1[Estacao][0][linha] *  self.RtamanhoErroMBIXY_TI1[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroMBIXY_TI2[Estacao][0][linha][coluna] = self.RtamanhoErroMBIXY_TI2[Estacao][0][linha] *  self.RtamanhoErroMBIXY_TI2[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroMSIXY_TI2[Estacao][0][linha][coluna] = self.RtamanhoErroMSIXY_TI2[Estacao][0][linha] *  self.RtamanhoErroMSIXY_TI2[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroMSIXY_TI3[Estacao][0][linha][coluna] = self.RtamanhoErroMSIXY_TI3[Estacao][0][linha] *  self.RtamanhoErroMSIXY_TI3[Estacao][0][coluna]
                    
        for Estacao in range(1,len(self.dadosOriginaisMWD)):
       
            self.Rtamanho_Total_ErroABXY_TI1[Estacao]   =  self.Rtamanho_Total_ErroABXY_TI1[Estacao] +  self.Rtamanho_Total_ErroABXY_TI1[Estacao - 1]        
            
            self.Rtamanho_Total_ErroABXY_TI2[Estacao]   =  self.Rtamanho_Total_ErroABXY_TI2[Estacao] +  self.Rtamanho_Total_ErroABXY_TI2[Estacao - 1]        

            self.Rtamanho_Total_ErroASXY_TI2[Estacao]   =  self.Rtamanho_Total_ErroASXY_TI2[Estacao] +  self.Rtamanho_Total_ErroASXY_TI2[Estacao - 1]
            
            self.Rtamanho_Total_ErroASXY_TI3[Estacao]   =  self.Rtamanho_Total_ErroASXY_TI3[Estacao] +  self.Rtamanho_Total_ErroASXY_TI3[Estacao - 1]
            
            self.Rtamanho_Total_ErroMBXY_TI1[Estacao]   =  self.Rtamanho_Total_ErroMBXY_TI1[Estacao] +  self.Rtamanho_Total_ErroMBXY_TI1[Estacao - 1]
            
            self.Rtamanho_Total_ErroMBXY_TI2[Estacao]   =  self.Rtamanho_Total_ErroMBXY_TI2[Estacao] +  self.Rtamanho_Total_ErroMBXY_TI2[Estacao - 1]
            
            self.Rtamanho_Total_ErroMSXY_TI2[Estacao]   =  self.Rtamanho_Total_ErroMSXY_TI2[Estacao] +  self.Rtamanho_Total_ErroMSXY_TI2[Estacao - 1]
            
            self.Rtamanho_Total_ErroMSXY_TI3[Estacao]   =  self.Rtamanho_Total_ErroMSXY_TI3[Estacao] +  self.Rtamanho_Total_ErroMSXY_TI3[Estacao - 1]
            
            self.Rtamanho_Total_ErroXYM1[Estacao]       =  self.Rtamanho_Total_ErroXYM1[Estacao] +  self.Rtamanho_Total_ErroXYM1[Estacao - 1]
            
            self.Rtamanho_Total_ErroXYM2[Estacao]       =  self.Rtamanho_Total_ErroXYM2[Estacao] +  self.Rtamanho_Total_ErroXYM2[Estacao - 1]
            
            self.Rtamanho_Total_ErroDREF_R[Estacao]     =  self.Rtamanho_Total_ErroDREF_R[Estacao] +  self.Rtamanho_Total_ErroDREF_R[Estacao - 1]
            
            self.Rtamanho_Total_ErroABIXY_TI1[Estacao]   =  self.Rtamanho_Total_ErroABIXY_TI1[Estacao] +  self.Rtamanho_Total_ErroABIXY_TI1[Estacao - 1]
             
            self.Rtamanho_Total_ErroASIXY_TI2[Estacao]   =  self.Rtamanho_Total_ErroASIXY_TI2[Estacao] +  self.Rtamanho_Total_ErroASIXY_TI2[Estacao - 1]
              
            self.Rtamanho_Total_ErroASIXY_TI3[Estacao]   =  self.Rtamanho_Total_ErroASIXY_TI3[Estacao] +  self.Rtamanho_Total_ErroASIXY_TI3[Estacao - 1]
            
            self.Rtamanho_Total_ErroMBIXY_TI1[Estacao]   =  self.Rtamanho_Total_ErroMBIXY_TI1[Estacao] +  self.Rtamanho_Total_ErroMBIXY_TI1[Estacao - 1]
            
            self.Rtamanho_Total_ErroMBIXY_TI2[Estacao]   =  self.Rtamanho_Total_ErroMBIXY_TI2[Estacao] +  self.Rtamanho_Total_ErroMBIXY_TI2[Estacao - 1]
            
            self.Rtamanho_Total_ErroMSIXY_TI2[Estacao]   =  self.Rtamanho_Total_ErroMSIXY_TI2[Estacao] +  self.Rtamanho_Total_ErroMSIXY_TI2[Estacao - 1]
            
            self.Rtamanho_Total_ErroMSIXY_TI3[Estacao]   =  self.Rtamanho_Total_ErroMSIXY_TI3[Estacao] +  self.Rtamanho_Total_ErroMSIXY_TI3[Estacao - 1]
            
            #Soma erros de modo de propagação ramdomico total
            self.ErroRandomicoTotal[Estacao] =  self.Rtamanho_Total_ErroABXY_TI1[Estacao] + self.Rtamanho_Total_ErroABXY_TI2[Estacao]   +  self.Rtamanho_Total_ErroASXY_TI2[Estacao]   + self.Rtamanho_Total_ErroASXY_TI3[Estacao]   + self.Rtamanho_Total_ErroMBXY_TI1[Estacao]   +  self.Rtamanho_Total_ErroMBXY_TI2[Estacao]   +  self.Rtamanho_Total_ErroMSXY_TI2[Estacao]  + self.Rtamanho_Total_ErroMSXY_TI3[Estacao]    + self.Rtamanho_Total_ErroDREF_R[Estacao] # +     self.Rtamanho_Total_ErroMSIXY_TI2[Estacao]  + self.Rtamanho_Total_ErroMSIXY_TI3[Estacao]        +    self.Rtamanho_Total_ErroXYM1[Estacao]       +     self.Rtamanho_Total_ErroXYM2[Estacao] + self.Rtamanho_Total_ErroABIXY_TI1[Estacao] + self.Rtamanho_Total_ErroASIXY_TI2[Estacao]  + self.Rtamanho_Total_ErroASIXY_TI3[Estacao]  + self.Rtamanho_Total_ErroMBIXY_TI1[Estacao]  + self.Rtamanho_Total_ErroMBIXY_TI2[Estacao] 
        
        df = pd.DataFrame([[self.ErroRandomicoTotal, self.RtamanhoErroABXY_TI1, self.RtamanhoErroABXY_TI2, self.RtamanhoErroASXY_TI2, self.RtamanhoErroASXY_TI3,        self.RtamanhoErroMBXY_TI1   , self.RtamanhoErroMBXY_TI2, self.RtamanhoErroMSXY_TI2   , self.RtamanhoErroMSXY_TI3,  self.RtamanhoErroXYM1, self.RtamanhoErroXYM2, self.RtamanhoErroDREF_R     , self.RtamanhoErroABIXY_TI1  ,        self.RtamanhoErroASIXY_TI2  , self.RtamanhoErroASIXY_TI3, self.RtamanhoErroMBIXY_TI1, self.RtamanhoErroMBIXY_TI2  , self.RtamanhoErroMSIXY_TI2  ,        self.RtamanhoErroMSIXY_TI3  , self.Rtamanho_Total_ErroABXY_TI1   ,           self.Rtamanho_Total_ErroABXY_TI2   , self.Rtamanho_Total_ErroASXY_TI2   , self.Rtamanho_Total_ErroASXY_TI3   , self.Rtamanho_Total_ErroMBXY_TI1   , self.Rtamanho_Total_ErroMBXY_TI2   , self.Rtamanho_Total_ErroMSXY_TI2   , self.Rtamanho_Total_ErroMSXY_TI3   , self.Rtamanho_Total_ErroXYM1       , self.Rtamanho_Total_ErroXYM2       , self.Rtamanho_Total_ErroDREF_R     , self.Rtamanho_Total_ErroABIXY_TI1  , self.Rtamanho_Total_ErroASIXY_TI2  , self.Rtamanho_Total_ErroASIXY_TI3  , self.Rtamanho_Total_ErroMBIXY_TI1  , self.Rtamanho_Total_ErroMBIXY_TI2  , self.Rtamanho_Total_ErroMSIXY_TI2  , self.Rtamanho_Total_ErroMSIXY_TI3  ]], columns=['self.ErroRandomicoTotal', 'self.RtamanhoErroABXY_TI1   ',         'self.RtamanhoErroABXY_TI2   ', 'self.RtamanhoErroASXY_TI2   ',         'self.RtamanhoErroASXY_TI3   ',         'self.RtamanhoErroMBXY_TI1   ',         'self.RtamanhoErroMBXY_TI2   ',         'self.RtamanhoErroMSXY_TI2   ',         'self.RtamanhoErroMSXY_TI3   ',         'self.RtamanhoErroXYM1       ',         'self.RtamanhoErroXYM2       ',         'self.RtamanhoErroDREF_R     ',         'self.RtamanhoErroABIXY_TI1  ',         'self.RtamanhoErroASIXY_TI2  ',         'self.RtamanhoErroASIXY_TI3  ',         'self.RtamanhoErroMBIXY_TI1  ',         'self.RtamanhoErroMBIXY_TI2  ',        'self.RtamanhoErroMSIXY_TI2  ',         'self.RtamanhoErroMSIXY_TI3  ',         'self.Rtamanho_Total_ErroABXY_TI1   ',            'self.Rtamanho_Total_ErroABXY_TI2   ',         'self.Rtamanho_Total_ErroASXY_TI2   ',         'self.Rtamanho_Total_ErroASXY_TI3   ',         'self.Rtamanho_Total_ErroMBXY_TI1   ',         'self.Rtamanho_Total_ErroMBXY_TI2',        'self.Rtamanho_Total_ErroMSXY_TI2   ',         'self.Rtamanho_Total_ErroMSXY_TI3   ',         'self.Rtamanho_Total_ErroXYM1       ',         'self.Rtamanho_Total_ErroXYM2',        'self.Rtamanho_Total_ErroDREF_R     ',         'self.Rtamanho_Total_ErroABIXY_TI1  ',         'self.Rtamanho_Total_ErroASIXY_TI2  ',         'self.Rtamanho_Total_ErroASIXY_TI3',    'self.Rtamanho_Total_ErroMBIXY_TI1  ',         'self.Rtamanho_Total_ErroMBIXY_TI2  ',         'self.Rtamanho_Total_ErroMSIXY_TI2  ',   'self.Rtamanho_Total_ErroMSIXY_TI31'])
        
        writer = pd.ExcelWriter('Randomico_Tamanho_Erro.xlsx')
        
        df.to_excel(writer,'Efeito MWD',float_format='%.5f')
        
        writer.save()
        
    def ErroSistematicoMWD(self):
        
        for Estacao in range(0,len(self.dadosOriginaisMWD)):
            for coluna in range(0,1):
                for linha in range(0,3):
                    
                    #Erro acelerometro
                    self.StamanhoErroASXY_TI2[Estacao][coluna][linha]  = self.Mag_ASXY_TI2 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.ASXY_TI2[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.ASXY_TI2[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.ASXY_TI2[Estacao][coluna + 2]))                    
                    
                    #Erro acelerometro
                    self.StamanhoErroASXY_TI3[Estacao][coluna][linha]  = self.Mag_ASXY_TI3 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.ASXY_TI3[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.ASXY_TI3[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.ASXY_TI3[Estacao][coluna + 2]))                    
                     
                    #Erro acelerometro
                    self.StamanhoErroASZ[Estacao][coluna][linha]       = self.Mag_ASZ * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.ASZ[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.ASZ[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.ASZ[Estacao][coluna + 2]))      
                    #Erro magnetometro
                    self.StamanhoErroMBXY_TI1[Estacao][coluna][linha]  = self.Mag_MBXY_TI1 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.MBXY_TI1[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MBXY_TI1[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MBXY_TI1[Estacao][coluna + 2]))    
                    
                    #Erro magnetometro
                    self.StamanhoErroMBXY_TI2[Estacao][coluna][linha]  = self.Mag_MBXY_TI2 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.MBXY_TI2[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MBXY_TI2[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MBXY_TI2[Estacao][coluna + 2]))               
                    
                    #Erro magnetometro
                    self.StamanhoErroMBZ[Estacao][coluna][linha]       = self.Mag_MBZ * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.MBZ[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MBZ[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MBZ[Estacao][coluna + 2]))
                    
                    #Erro magnetometro
                    self.StamanhoErroMSXY_TI1[Estacao][coluna][linha]  = self.Mag_MSXY_TI1 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.MSXY_TI1[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MSXY_TI1[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MSXY_TI1[Estacao][coluna + 2]))                   
                    #Erro magnetometro
                    self.StamanhoErroMSXY_TI2[Estacao][coluna][linha]  = self.Mag_MSXY_TI2 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.MSXY_TI2[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MSXY_TI2[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MSXY_TI2[Estacao][coluna + 2]))
                     #Erro magnetometro
                    self.StamanhoErroMSXY_TI3[Estacao][coluna][linha]  = self.Mag_MSXY_TI3 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.MSXY_TI3[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MSXY_TI3[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MSXY_TI3[Estacao][coluna + 2]))
                    #Erro magnetometro
                    self.StamanhoErroMSZ[Estacao][coluna][linha]       = self.Mag_MSZ * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.MSZ[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MSZ[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MSZ[Estacao][coluna + 2]))
                    
                    #Erro magnetometro
                    self.StamanhoErroSAG[Estacao][coluna][linha]       = self.Mag_SAG * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.SAG[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.SAG[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.SAG[Estacao][coluna + 2]))
                    
                    #Erro magnetometro
                    self.StamanhoErroAMID[Estacao][coluna][linha]      = self.Mag_AMID * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.AMID[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.AMID[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.AMID[Estacao][coluna + 2]))
                    
                    #Erro magnetometro
                    self.StamanhoErroXYM1[Estacao][coluna][linha]      = self.Mag_XYM1 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.XYM1[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.XYM1[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.XYM1[Estacao][coluna + 2]))
                   
                    #Erro magnetometro
                    self.StamanhoErroXYM2[Estacao][coluna][linha]      = self.Mag_XYM2 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.XYM2[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.XYM2[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.XYM2[Estacao][coluna + 2]))

                    if self.I_MWD[Estacao] <= 5:
                        
                        if Estacao == 0:
                            MDauxiliar = 0.0
                            self.StamanhoErroXYM3[Estacao][coluna][linha] = self.Mag_XYM3 * 0.5 * ((self.Md_MWD[Estacao + 1] - MDauxiliar) * (self.XYM3[Estacao][coluna]))
                            self.StamanhoErroXYM4[Estacao][coluna][linha] = self.Mag_XYM4 * 0.5 * ((self.Md_MWD[Estacao + 1] - MDauxiliar) * (self.XYM4[Estacao][coluna]))
                        
                        
                        elif Estacao == len(self.dadosOriginaisMWD):
                            MDauxiliar = self.Md_MWD[Estacao - 1]
                            self.StamanhoErroXYM3[Estacao][coluna][linha] = self.Mag_XYM3 * 0.5 * ((self.Md_MWD[Estacao] - MDauxiliar) * (self.XYM3[Estacao][coluna]))
                            self.StamanhoErroXYM4[Estacao][coluna][linha] = self.Mag_XYM4 * 0.5 * ((self.Md_MWD[Estacao] - MDauxiliar) * (self.XYM4[Estacao][coluna]))
                        
                        else:
                            MDauxiliar = self.Md_MWD[Estacao - 1]
                            self.StamanhoErroXYM3[Estacao][coluna][linha] = self.Mag_XYM3 * 0.5 * ((self.Md_MWD[Estacao + 1] - MDauxiliar) * (self.XYM3[Estacao][coluna]))
                            self.StamanhoErroXYM4[Estacao][coluna][linha] = self.Mag_XYM4 * 0.5 * ((self.Md_MWD[Estacao + 1] - MDauxiliar) * (self.XYM4[Estacao][coluna]))
                        
                    else:
                        
                        #Erro magnetometro
                        self.StamanhoErroXYM3[Estacao][coluna][linha]      = self.Mag_XYM3 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.XYM3[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.XYM3[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.XYM3[Estacao][coluna + 2]))
                        
                        #Erro magnetometro
                        self.StamanhoErroXYM4[Estacao][coluna][linha]      = self.Mag_XYM4 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.XYM4[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.XYM4[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.XYM4[Estacao][coluna + 2]))
                    
                      
                    
                    #Erro Profundidade
                    self.StamanhoErroDREF_S[Estacao][coluna][linha]    = self.Mag_DREF_S * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.DREF_S[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.DREF_S[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.DREF_S[Estacao][coluna + 2]))
                   
                    #Erro Profundidade
                    self.StamanhoErroDSF_S[Estacao][coluna][linha]     = self.Mag_DSF_S * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.DSF_S[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.DSF_S[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.DSF_S[Estacao][coluna + 2]))
    
                    if (self.correcaoAxial) == 0:
                        #Erro 
                        self.StamanhoErroABIZ[Estacao][coluna][linha]      = self.Mag_ABIZ * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.ABIZ[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.ABIZ[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.ABIZ[Estacao][coluna + 2]))
                        
                        #Erro 
                        self.StamanhoErroASIXY_TI1[Estacao][coluna][linha] = self.Mag_ASIXY_TI1 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.ASIXY_TI1[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.ASIXY_TI1[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.ASIXY_TI1[Estacao][coluna + 2]))
                        
                            #Erro magnetometro
                        self.StamanhoErroABIXY_TI1[Estacao][coluna][linha] = self.Mag_ABIXY_TI1 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.ABIXY_TI1[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.ABIXY_TI1[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.ABIXY_TI1[Estacao][coluna + 2]))
                        
                        #Erro acelerometro   
                        self.StamanhoErroASIXY_TI2[Estacao][coluna][linha] = self.Mag_ASIXY_TI2 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.ASIXY_TI2[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.ASIXY_TI2[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.ASIXY_TI2[Estacao][coluna + 2]))
                        
                        #Erro acelerometro
                        self.StamanhoErroASIXY_TI3[Estacao][coluna][linha] = self.Mag_ASIXY_TI3 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.ASIXY_TI3[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.ASIXY_TI3[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.ASIXY_TI3[Estacao][coluna + 2]))
                        
                        #Erro magnetometro
                        self.StamanhoErroMBIXY_TI2[Estacao][coluna][linha] = self.Mag_MBIXY_TI2 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.MBIXY_TI2[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MBIXY_TI2[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MBIXY_TI2[Estacao][coluna + 2]))
                        
                        #Erro magnetometro
                        self.StamanhoErroMSIXY_TI1[Estacao][coluna][linha] = self.Mag_MSIXY_TI1 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.MSIXY_TI1[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MSIXY_TI1[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MSIXY_TI1[Estacao][coluna + 2]))
                        
                        #Erro magnetometro
                        self.StamanhoErroMSIXY_TI2[Estacao][coluna][linha] = self.Mag_MSIXY_TI2 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.MSIXY_TI2[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MSIXY_TI2[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MSIXY_TI2[Estacao][coluna + 2]))    
                        
                        #Erro magnetometro
                        self.StamanhoErroMSIXY_TI3[Estacao][coluna][linha] = self.Mag_MSIXY_TI3 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.MSIXY_TI3[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MSIXY_TI3[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MSIXY_TI3[Estacao][coluna + 2])) 
                    
                        if self.I_MWD[Estacao] <= 5:
                            
                            self.StamanhoErroASIZ[Estacao][coluna][linha]     = 0
                            self.StamanhoErroABZ[Estacao][coluna][linha]      = 0
                        else:
                            
                            #Erro 
                            self.StamanhoErroASIZ[Estacao][coluna][linha]      = self.Mag_ASIZ * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.ASIZ[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.ASIZ[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.ASIZ[Estacao][coluna + 2]))
                        
                            self.StamanhoErroABZ[Estacao][coluna][linha]      = self.Mag_ABZ * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.ABZ[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.ABZ[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.ABZ[Estacao][coluna + 2]))
                        
                        if self.I_MWD[Estacao] <= 5:
                            
                            if Estacao == 0:
                                
                                MDauxiliar = 0.0
                                self.StamanhoErroABIXY_TI2[Estacao][coluna][linha] = self.Mag_ABIXY_TI2 * 0.5 * ((self.Md_MWD[Estacao + 1] - MDauxiliar) * (self.ABIXY_TI2[Estacao][coluna]))
                                
                            elif Estacao == len(self.dadosOriginaisMWD):
                                 MDauxiliar = 0.0
                                 self.StamanhoErroABIXY_TI2[Estacao][coluna][linha] = self.Mag_ABIXY_TI2 * 0.5 * ((self.Md_MWD[Estacao] - MDauxiliar) * (self.ABIXY_TI2[Estacao][coluna]))   
                            else:
                                MDauxiliar = self.Md_MWD[Estacao - 1]
                                self.StamanhoErroABIXY_TI2[Estacao][coluna][linha] = self.Mag_ABIXY_TI2 * 0.5 * ((self.Md_MWD[Estacao + 1] - MDauxiliar) * (self.ABIXY_TI2[Estacao][coluna]))
                        else:
                            
                            #Erro magnetometro
                            self.StamanhoErroABIXY_TI2[Estacao][coluna][linha] = self.Mag_ABIXY_TI2 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.ABIXY_TI2[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.ABIXY_TI2[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.ABIXY_TI2[Estacao][coluna + 2]))
                    
                        #Erro magnetometro
                        self.StamanhoErroMBIXY_TI1[Estacao][coluna][linha] = self.Mag_MBIXY_TI1 * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.MBIXY_TI1[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MBIXY_TI1[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MBIXY_TI1[Estacao][coluna + 2]))
        
        
        for Estacao in range(1,len(self.dadosOriginaisMWD)):

            self.Stamanho_Total_ErroASXY_TI2[Estacao] = self.StamanhoErroASXY_TI2[Estacao] +  self.Stamanho_Total_ErroASXY_TI2[Estacao - 1]  
            
            self.Stamanho_Total_ErroASXY_TI3[Estacao] = self.StamanhoErroASXY_TI3[Estacao] +  self.Stamanho_Total_ErroASXY_TI3[Estacao - 1]     
            
            self.Stamanho_Total_ErroASZ[Estacao] = self.StamanhoErroASZ[Estacao] +  self.Stamanho_Total_ErroASZ[Estacao - 1]     
            
            self.Stamanho_Total_ErroMBXY_TI1[Estacao] = self.StamanhoErroMBXY_TI1[Estacao] +  self.Stamanho_Total_ErroMBXY_TI1[Estacao - 1]        
            
            self.Stamanho_Total_ErroMBXY_TI2[Estacao] = self.StamanhoErroMBXY_TI2[Estacao] +  self.Stamanho_Total_ErroMBXY_TI2[Estacao - 1]        
            
            self.Stamanho_Total_ErroMBZ[Estacao] = self.StamanhoErroMBZ[Estacao] +  self.Stamanho_Total_ErroMBZ[Estacao - 1]        
            
            self.Stamanho_Total_ErroMSXY_TI1[Estacao] = self.StamanhoErroMSXY_TI1[Estacao] +  self.Stamanho_Total_ErroMSXY_TI1[Estacao - 1]        
            
            self.Stamanho_Total_ErroMSXY_TI2[Estacao] = self.StamanhoErroMSXY_TI2[Estacao] +  self.Stamanho_Total_ErroMSXY_TI2[Estacao - 1]        
            
            self.Stamanho_Total_ErroMSXY_TI3[Estacao] = self.StamanhoErroMSXY_TI3[Estacao] +  self.Stamanho_Total_ErroMSXY_TI3[Estacao - 1]        
            
            self.Stamanho_Total_ErroMSZ[Estacao] = self.StamanhoErroMSZ[Estacao] +  self.Stamanho_Total_ErroMSZ[Estacao - 1]        
            
            self.Stamanho_Total_ErroSAG[Estacao] = self.StamanhoErroSAG[Estacao] +  self.Stamanho_Total_ErroSAG[Estacao - 1]        
            
            self.Stamanho_Total_ErroAMID[Estacao] = self.StamanhoErroAMID[Estacao] +  self.Stamanho_Total_ErroAMID[Estacao - 1]        
            
            self.Stamanho_Total_ErroXYM1[Estacao] = self.StamanhoErroXYM1[Estacao] +  self.Stamanho_Total_ErroXYM1[Estacao - 1]        
            
            self.Stamanho_Total_ErroXYM2[Estacao] = self.StamanhoErroXYM2[Estacao] +  self.Stamanho_Total_ErroXYM2[Estacao - 1]     
            
            self.Stamanho_Total_ErroXYM3[Estacao] = self.StamanhoErroXYM3[Estacao] +  self.Stamanho_Total_ErroXYM3[Estacao - 1]        
            
            self.Stamanho_Total_ErroXYM4[Estacao] = self.StamanhoErroXYM4[Estacao] +  self.Stamanho_Total_ErroXYM4[Estacao - 1]     

            self.Stamanho_Total_ErroABIXY_TI1[Estacao] = self.StamanhoErroABIXY_TI1[Estacao] +  self.Stamanho_Total_ErroABIXY_TI1[Estacao - 1]        
            
            self.Stamanho_Total_ErroABIXY_TI2[Estacao] = self.StamanhoErroABIXY_TI2[Estacao] +  self.Stamanho_Total_ErroABIXY_TI2[Estacao - 1]        

            self.Stamanho_Total_ErroABIZ[Estacao] = self.StamanhoErroABIZ[Estacao] +  self.Stamanho_Total_ErroABIZ[Estacao - 1]        
            
            self.Stamanho_Total_ErroASIXY_TI1[Estacao] = self.StamanhoErroASIXY_TI1[Estacao] +  self.Stamanho_Total_ErroASIXY_TI1[Estacao - 1]        
            
            self.Stamanho_Total_ErroASIXY_TI2[Estacao] = self.StamanhoErroASIXY_TI2[Estacao] +  self.Stamanho_Total_ErroASIXY_TI2[Estacao - 1]        
            
            self.Stamanho_Total_ErroASIXY_TI3[Estacao] = self.StamanhoErroASIXY_TI3[Estacao] +  self.Stamanho_Total_ErroASIXY_TI3[Estacao - 1]        
            
            self.Stamanho_Total_ErroASIZ[Estacao] = self.StamanhoErroASIZ[Estacao] +  self.Stamanho_Total_ErroASIZ[Estacao - 1]        
            
            self.Stamanho_Total_ErroABZ [Estacao] = self.StamanhoErroABZ[Estacao] +  self.Stamanho_Total_ErroABZ[Estacao - 1]  
            
            self.Stamanho_Total_ErroMBIXY_TI1[Estacao] = self.StamanhoErroMBIXY_TI1[Estacao] +  self.Stamanho_Total_ErroMBIXY_TI1[Estacao - 1]        
            
            self.Stamanho_Total_ErroMBIXY_TI2[Estacao] = self.StamanhoErroMBIXY_TI2[Estacao] +  self.Stamanho_Total_ErroMBIXY_TI2[Estacao - 1]        
            
            self.Stamanho_Total_ErroMSIXY_TI1[Estacao] = self.StamanhoErroMSIXY_TI1[Estacao] +  self.StamanhoErroMSIXY_TI1[Estacao - 1]        
            
            self.Stamanho_Total_ErroMSIXY_TI2[Estacao] = self.StamanhoErroMSIXY_TI2[Estacao] +  self.Stamanho_Total_ErroMSIXY_TI2[Estacao - 1]        
            
            self.Stamanho_Total_ErroMSIXY_TI3[Estacao] = self.StamanhoErroMSIXY_TI3[Estacao] +  self.Stamanho_Total_ErroMSIXY_TI3[Estacao - 1]        
            
            self.Stamanho_Total_ErroDREF_S[Estacao] = self.StamanhoErroDREF_S[Estacao] +  self.Stamanho_Total_ErroDREF_S[Estacao - 1]        
            
            self.Stamanho_Total_ErroDSF_S[Estacao] = self.StamanhoErroDSF_S[Estacao] +  self.Stamanho_Total_ErroDSF_S[Estacao - 1]        
        
        for Estacao in range(0,len(self.dadosOriginaisMWD)):
            for linha in range(0,3):
                for coluna in range(0,3):
                
                    self.Stamanho_Produto_ErroASXY_TI2[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroASXY_TI2[Estacao][0][linha] * self.Stamanho_Total_ErroASXY_TI2[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroASXY_TI3[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroASXY_TI3[Estacao][0][linha] *  self.Stamanho_Total_ErroASXY_TI3[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroASZ[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroASZ[Estacao][0][linha] *  self.Stamanho_Total_ErroASZ[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroMBXY_TI1[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroMBXY_TI1[Estacao][0][linha] *  self.Stamanho_Total_ErroMBXY_TI1[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroMBXY_TI2[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroMBXY_TI2[Estacao][0][linha] *  self.Stamanho_Total_ErroMBXY_TI2[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroMBZ[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroMBZ[Estacao][0][linha] *  self.Stamanho_Total_ErroMBZ[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroMSXY_TI1[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroMSXY_TI1[Estacao][0][linha] *  self.Stamanho_Total_ErroMSXY_TI1[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroMSXY_TI2[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroMSXY_TI2[Estacao][0][linha] *  self.Stamanho_Total_ErroMSXY_TI2[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroMSXY_TI3[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroMSXY_TI3[Estacao][0][linha] *  self.Stamanho_Total_ErroMSXY_TI3[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroMSZ[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroMSZ[Estacao][0][linha] *  self.Stamanho_Total_ErroMSZ[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroSAG[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroSAG[Estacao][0][linha] *  self.Stamanho_Total_ErroSAG[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroAMID[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroAMID[Estacao][0][linha] *  self.Stamanho_Total_ErroAMID[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroXYM1[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroXYM1[Estacao][0][linha] *  self.Stamanho_Total_ErroXYM1[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroXYM2[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroXYM2[Estacao][0][linha] *  self.Stamanho_Total_ErroXYM2[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroXYM3[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroXYM3[Estacao][0][linha] *  self.Stamanho_Total_ErroXYM3[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroXYM4[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroXYM4[Estacao][0][linha] *  self.Stamanho_Total_ErroXYM4[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroABIXY_TI1[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroABIXY_TI1[Estacao][0][linha] *  self.Stamanho_Total_ErroABIXY_TI1[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroABIXY_TI2[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroABIXY_TI2[Estacao][0][linha] *  self.Stamanho_Total_ErroABIXY_TI2[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroABIZ[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroABIZ[Estacao][0][linha] *  self.Stamanho_Total_ErroABIZ[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroASIXY_TI1[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroASIXY_TI1[Estacao][0][linha] *  self.Stamanho_Total_ErroASIXY_TI1[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroASIXY_TI2[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroASIXY_TI2[Estacao][0][linha] *  self.Stamanho_Total_ErroASIXY_TI2[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroASIXY_TI3[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroASIXY_TI3[Estacao][0][linha] *  self.Stamanho_Total_ErroASIXY_TI3[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroASIZ[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroASIZ[Estacao][0][linha] *  self.Stamanho_Total_ErroASIZ[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroABZ [Estacao][0][linha][coluna] = self.Stamanho_Total_ErroABZ[Estacao][0][linha] *  self.Stamanho_Total_ErroABZ[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroMBIXY_TI1[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroMBIXY_TI1[Estacao][0][linha] *  self.Stamanho_Total_ErroMBIXY_TI1[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroMBIXY_TI2[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroMBIXY_TI2[Estacao][0][linha] *  self.Stamanho_Total_ErroMBIXY_TI2[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroMSIXY_TI1[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroMSIXY_TI1[Estacao][0][linha] *  self.Stamanho_Total_ErroMSIXY_TI1[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroMSIXY_TI2[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroMSIXY_TI2[Estacao][0][linha] *  self.Stamanho_Total_ErroMSIXY_TI2[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroMSIXY_TI3[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroMSIXY_TI3[Estacao][0][linha] *  self.Stamanho_Total_ErroMSIXY_TI3[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroDREF_S[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroDREF_S[Estacao][0][linha] *  self.Stamanho_Total_ErroDREF_S[Estacao][0][coluna]
                    
                    self.Stamanho_Produto_ErroDSF_S[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroDSF_S[Estacao][0][linha] *  self.Stamanho_Total_ErroDSF_S[Estacao][0][coluna]
                
            self.ErroSistematicoTotal[Estacao] = + self.Stamanho_Produto_ErroAMID[Estacao] + self.Stamanho_Produto_ErroASXY_TI2[Estacao] +  self.Stamanho_Produto_ErroMSZ[Estacao] + self.Stamanho_Produto_ErroASXY_TI3[Estacao] + self.Stamanho_Produto_ErroMSXY_TI1[Estacao]  + self.Stamanho_Produto_ErroMSXY_TI2[Estacao]  + self.Stamanho_Produto_ErroMSXY_TI3[Estacao]  + self.Stamanho_Produto_ErroMBXY_TI1[Estacao]  + self.Stamanho_Produto_ErroMBXY_TI2[Estacao]     + self.Stamanho_Produto_ErroMBZ[Estacao] + self.Stamanho_Produto_ErroSAG[Estacao]  + self.Stamanho_Produto_ErroASZ[Estacao]  + self.Stamanho_Produto_ErroXYM1[Estacao]      + self.Stamanho_Produto_ErroXYM2[Estacao] + self.Stamanho_Produto_ErroXYM3[Estacao]      + self.Stamanho_Produto_ErroXYM4[Estacao]     + self.Stamanho_Produto_ErroABZ[Estacao] + self.Stamanho_Produto_ErroDSF_S[Estacao] + self.Stamanho_Produto_ErroDREF_S[Estacao]
            
            #                + self.Stamanho_Produto_ErroABIXY_TI1[Estacao] + self.Stamanho_Produto_ErroABIXY_TI2[Estacao] + self.Stamanho_Produto_ErroABIZ[Estacao]   + self.Stamanho_Produto_ErroASIXY_TI1[Estacao] + self.Stamanho_Produto_ErroASIXY_TI2[Estacao] + self.Stamanho_Produto_ErroASIXY_TI3[Estacao]  + self.Stamanho_Produto_ErroMBIXY_TI1[Estacao] + self.Stamanho_Produto_ErroMBIXY_TI2[Estacao]      + self.Stamanho_Produto_ErroASIZ[Estacao] + self.Stamanho_Produto_ErroMSIXY_TI1[Estacao] + self.Stamanho_Produto_ErroMSIXY_TI2[Estacao] + self.Stamanho_Produto_ErroMSIXY_TI3[Estacao] 
        
        df = pd.DataFrame([[self.ErroSistematicoTotal, self.StamanhoErroASXY_TI2, self.StamanhoErroASXY_TI3, self.StamanhoErroASZ, self.StamanhoErroMBXY_TI1, self.StamanhoErroMBXY_TI2, self.StamanhoErroMBZ, self.StamanhoErroMSXY_TI1, self.StamanhoErroMSXY_TI2, self.StamanhoErroMSXY_TI3, self.StamanhoErroMSZ, self.StamanhoErroSAG, self.StamanhoErroAMID, self.StamanhoErroXYM1, self.StamanhoErroXYM2, self.StamanhoErroXYM3, self.StamanhoErroXYM4, self.StamanhoErroABIXY_TI1, self.StamanhoErroABIXY_TI2, self.StamanhoErroABIZ, self.StamanhoErroASIXY_TI1, self.StamanhoErroASIXY_TI2, self.StamanhoErroASIXY_TI3, self.StamanhoErroASIZ, self.StamanhoErroABZ, self.StamanhoErroMBIXY_TI1, self.StamanhoErroMBIXY_TI2, self.StamanhoErroMSIXY_TI1, self.StamanhoErroMSIXY_TI2, self.StamanhoErroMSIXY_TI3, self.StamanhoErroDREF_S, self.StamanhoErroDSF_S, self.Stamanho_Total_ErroASXY_TI2, self.Stamanho_Total_ErroASXY_TI3, self.Stamanho_Total_ErroASZ, self.Stamanho_Total_ErroMBXY_TI1, self.Stamanho_Total_ErroMBXY_TI2,      self.Stamanho_Total_ErroMBZ, self.Stamanho_Total_ErroMSXY_TI1, self.Stamanho_Total_ErroMSXY_TI2, self.Stamanho_Total_ErroMSXY_TI3, self.Stamanho_Total_ErroMSZ, self.Stamanho_Total_ErroSAG, self.Stamanho_Total_ErroAMID, self.Stamanho_Total_ErroXYM1, self.Stamanho_Total_ErroXYM2, self.Stamanho_Total_ErroXYM3, self.Stamanho_Total_ErroXYM4, self.Stamanho_Total_ErroABIXY_TI1 , self.Stamanho_Total_ErroABIXY_TI2, self.Stamanho_Total_ErroABIZ, self.Stamanho_Total_ErroASIXY_TI1, self.Stamanho_Total_ErroASIXY_TI2   , self.Stamanho_Total_ErroASIXY_TI3   , self.Stamanho_Total_ErroASIZ, self.Stamanho_Total_ErroABZ, self.Stamanho_Total_ErroMBIXY_TI1 ,        self.Stamanho_Total_ErroMBIXY_TI2   , self.Stamanho_Total_ErroMSIXY_TI1   , self.Stamanho_Total_ErroMSIXY_TI2 , self.Stamanho_Total_ErroMSIXY_TI3 ,        self.Stamanho_Total_ErroDREF_S      , self.Stamanho_Total_ErroDSF_S       , self.Stamanho_Produto_ErroASXY_TI2, self.Stamanho_Produto_ErroASXY_TI3, self.Stamanho_Produto_ErroASZ, self.Stamanho_Produto_ErroMBXY_TI1 , self.Stamanho_Produto_ErroMBXY_TI2, self.Stamanho_Produto_ErroMBZ, self.Stamanho_Produto_ErroMSXY_TI1  ,        self.Stamanho_Produto_ErroMSXY_TI2  , self.Stamanho_Produto_ErroMSXY_TI3  , self.Stamanho_Produto_ErroMSZ       , self.Stamanho_Produto_ErroSAG       ,     self.Stamanho_Produto_ErroAMID      , self.Stamanho_Produto_ErroXYM1      , self.Stamanho_Produto_ErroXYM2      , self.Stamanho_Produto_ErroXYM3      , self.Stamanho_Produto_ErroXYM4      , self.Stamanho_Produto_ErroABIXY_TI1 , self.Stamanho_Produto_ErroABIXY_TI2 , self.Stamanho_Produto_ErroABIZ      , self.Stamanho_Produto_ErroASIXY_TI1 , self.Stamanho_Produto_ErroASIXY_TI2 , self.Stamanho_Produto_ErroASIXY_TI3 , self.Stamanho_Produto_ErroASIZ      ,        self.Stamanho_Produto_ErroABZ       , self.Stamanho_Produto_ErroMBIXY_TI1 , self.Stamanho_Produto_ErroMBIXY_TI2 , self.Stamanho_Produto_ErroMSIXY_TI1 ,      self.Stamanho_Produto_ErroMSIXY_TI2 , self.Stamanho_Produto_ErroMSIXY_TI3 , self.Stamanho_Produto_ErroDREF_S    , self.Stamanho_Produto_ErroDSF_S     ]], 
                          columns=['self.ErroSistematicoTotal', 'self.StamanhoErroASXY_TI2  ',        'self.StamanhoErroASXY_TI3  ', 'self.StamanhoErroASZ       ', 'self.StamanhoErroMBXY_TI1  ', 'self.StamanhoErroMBXY_TI2  ',        'self.StamanhoErroMBZ       ',        'self.StamanhoErroMSXY_TI1  ',        'self.StamanhoErroMSXY_TI2  ', 'self.StamanhoErroMSXY_TI3  ', 'self.StamanhoErroMSZ       ',        'self.StamanhoErroSAG       ', 'self.StamanhoErroAMID      ',        'self.StamanhoErroXYM1      ', 'self.StamanhoErroXYM2      ','self.StamanhoErroXYM3      ', 'self.StamanhoErroXYM4      ',        'self.StamanhoErroABIXY_TI1 ',  'self.StamanhoErroABIXY_TI2 ', 'self.StamanhoErroABIZ      ','self.StamanhoErroASIXY_TI1 ', 'self.StamanhoErroASIXY_TI2 ',      'self.StamanhoErroASIXY_TI3 ',        'self.StamanhoErroASIZ      ', 'self.StamanhoErroABZ       ','self.StamanhoErroMBIXY_TI1 ', 'self.StamanhoErroMBIXY_TI2 ',        'self.StamanhoErroMSIXY_TI1 ',        'self.StamanhoErroMSIXY_TI2 ', 'self.StamanhoErroMSIXY_TI3 ','self.StamanhoErroDREF_S    ', 'self.StamanhoErroDSF_S     ',        'self.Stamanho_Total_ErroASXY_TI2  ',        'self.Stamanho_Total_ErroASXY_TI3  ','self.Stamanho_Total_ErroASZ       ',        'self.Stamanho_Total_ErroMBXY_TI1  ',
        'self.Stamanho_Total_ErroMBXY_TI2  ',        'self.Stamanho_Total_ErroMBZ ', 'self.Stamanho_Total_ErroMSXY_TI1  ', 'self.Stamanho_Total_ErroMSXY_TI2  ',        'self.Stamanho_Total_ErroMSXY_TI3  ', 'self.Stamanho_Total_ErroMSZ       ', 'self.Stamanho_Total_ErroSAG       ', 'self.Stamanho_Total_ErroAMID      ',        'self.Stamanho_Total_ErroXYM1      ', 'self.Stamanho_Total_ErroXYM2      ', 'self.Stamanho_Total_ErroXYM3      ', 'self.Stamanho_Total_ErroXYM4      ',        'self.Stamanho_Total_ErroABIXY_TI1 ', 'self.Stamanho_Total_ErroABIXY_TI2 ', 'self.Stamanho_Total_ErroABIZ      ', 'self.Stamanho_Total_ErroASIXY_TI1 ',        'self.Stamanho_Total_ErroASIXY_TI2 ', 'self.Stamanho_Total_ErroASIXY_TI3 ', 'self.Stamanho_Total_ErroASIZ      ', 'self.Stamanho_Total_ErroABZ       ',        'self.Stamanho_Total_ErroMBIXY_TI1 ', 'self.Stamanho_Total_ErroMBIXY_TI2 ',  'self.Stamanho_Total_ErroMSIXY_TI1 ', 'self.Stamanho_Total_ErroMSIXY_TI2 ',        'self.Stamanho_Total_ErroMSIXY_TI3 ', 'self.Stamanho_Total_ErroDREF_S    ', 'self.Stamanho_Total_ErroDSF_S     ', 'self.Stamanho_Produto_ErroASXY_TI2  ',        'self.Stamanho_Produto_ErroASXY_TI3  ', 'self.Stamanho_Produto_ErroASZ       ', 'self.Stamanho_Produto_ErroMBXY_TI1  ', 'self.Stamanho_Produto_ErroMBXY_TI2  ',        'self.Stamanho_Produto_ErroMBZ       ', 'self.Stamanho_Produto_ErroMSXY_TI1  ', 'self.Stamanho_Produto_ErroMSXY_TI2  ', 'self.Stamanho_Produto_ErroMSXY_TI3  ',        'self.Stamanho_Produto_ErroMSZ       ', 'self.Stamanho_Produto_ErroSAG       ', 'self.Stamanho_Produto_ErroAMID      ', 'self.Stamanho_Produto_ErroXYM1      ',        'self.Stamanho_Produto_ErroXYM2      ', 'self.Stamanho_Produto_ErroXYM3      ', 'self.Stamanho_Produto_ErroXYM4      ', 'self.Stamanho_Produto_ErroABIXY_TI1 ',        'self.Stamanho_Produto_ErroABIXY_TI2 ', 'self.Stamanho_Produto_ErroABIZ      ', 'self.Stamanho_Produto_ErroASIXY_TI1 ', 'self.Stamanho_Produto_ErroASIXY_TI2 ',        'self.Stamanho_Produto_ErroASIXY_TI3 ', 'self.Stamanho_Produto_ErroASIZ      ', 'self.Stamanho_Produto_ErroABZ       ', 'self.Stamanho_Produto_ErroMBIXY_TI1 ',        'self.Stamanho_Produto_ErroMBIXY_TI2 ', 'self.Stamanho_Produto_ErroMSIXY_TI1 ', 'self.Stamanho_Produto_ErroMSIXY_TI2 ', 'self.Stamanho_Produto_ErroMSIXY_TI3 ',        'self.Stamanho_Produto_ErroDREF_S    ', 'self.Stamanho_Produto_ErroDSF_S'     ])      
        
        writer = pd.ExcelWriter('Sistematico_Tamanho_Erro_MWD.xlsx')
        
        df.to_excel(writer,'Efeito MWD',float_format='%.5f')
        
        writer.save()
        
        
    def ErroWellMWD(self):
        
        for Estacao in range(0,len(self.dadosOriginaisMWD)):
            for coluna in range(0,1):
                for linha in range(0,3):
                    
                    #Erro Declinividade
                    self.WtamanhoErroDEC[Estacao][coluna][linha] = self.Mag_DEC * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.DEC[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.DEC[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.DEC[Estacao][coluna + 2]))
                    #Erro Declinividade
                    self.WtamanhoErroDBH[Estacao][coluna][linha] = self.Mag_DBH * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.DBH[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.DBH[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.DBH[Estacao][coluna + 2]))
                    
                    #Erro profundidade
                    self.WtamanhoErroDST_G[Estacao][coluna][linha] = self.Mag_DST_G * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.DST_G[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.DST_G[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.DST_G[Estacao][coluna + 2]))
                    if (self.correcaoAxial) == 0:
                        
                        #Erro magnetometro
                        self.WtamanhoErroMFI[Estacao][coluna][linha] = self.Mag_MFI * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.MFI[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MFI[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MFI[Estacao][coluna + 2]))
                        #Erro magnetometro
                        self.WtamanhoErroMDI[Estacao][coluna][linha] = self.Mag_MDI * ((self.efeitoErroSurveyMWD[Estacao][coluna][linha]) * (self.MDI[Estacao][coluna]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 1][linha]) * (self.MDI[Estacao][coluna + 1]) + (self.efeitoErroSurveyMWD[Estacao][coluna + 2][linha]) * (self.MDI[Estacao][coluna + 2]))
                    
        for Estacao in range(1,len(self.dadosOriginaisMWD)):
            
            self.Wtamanho_Total_ErroDEC[Estacao]= self.WtamanhoErroDEC[Estacao] +  self.Wtamanho_Total_ErroDEC[Estacao - 1]
                    
            self.Wtamanho_Total_ErroDBH[Estacao] = self.WtamanhoErroDBH[Estacao] +  self.Wtamanho_Total_ErroDBH[Estacao - 1]
                    
            self.Wtamanho_Total_ErroMFI[Estacao] = self.WtamanhoErroMFI[Estacao] +  self.Wtamanho_Total_ErroMFI[Estacao - 1]
                    
            self.Wtamanho_Total_ErroMDI[Estacao] = self.WtamanhoErroMDI[Estacao] +  self.Wtamanho_Total_ErroMDI[Estacao - 1]
             
            self.Wtamanho_Total_ErroDST_G[Estacao] =self.WtamanhoErroDST_G[Estacao] +  self.Wtamanho_Total_ErroDST_G[Estacao - 1]
                                
        for Estacao in range(0,len(self.dadosOriginaisMWD)):
            for linha in range(0,3):
                for coluna in range(0,3):
                
                    self.Wtamanho_Produto_ErroDEC[Estacao][0][linha][coluna] = self.Wtamanho_Total_ErroDEC[Estacao][0][linha] *  self.Wtamanho_Total_ErroDEC[Estacao][0][coluna]
                    
                    self.Wtamanho_Produto_ErroDBH[Estacao][0][linha][coluna] = self.Wtamanho_Total_ErroDBH[Estacao][0][linha] *  self.Wtamanho_Total_ErroDBH[Estacao][0][coluna]
                    
                    self.Wtamanho_Produto_ErroMFI[Estacao][0][linha][coluna] = self.Wtamanho_Total_ErroMFI[Estacao][0][linha] *  self.Wtamanho_Total_ErroMFI[Estacao][0][coluna]
                    
                    self.Wtamanho_Produto_ErroMDI[Estacao][0][linha][coluna] = self.Wtamanho_Total_ErroMDI[Estacao][0][linha] *  self.Wtamanho_Total_ErroMDI[Estacao][0][coluna]
                    
                    self.Wtamanho_Produto_ErroDST_G[Estacao][0][linha][coluna] = self.Wtamanho_Total_ErroDST_G[Estacao][0][linha] *  self.Wtamanho_Total_ErroDST_G[Estacao][0][coluna]
                    
            self.ErroWellTotal[Estacao] = self.Wtamanho_Produto_ErroDST_G[Estacao] + self.Wtamanho_Produto_ErroDEC[Estacao] + self.Wtamanho_Produto_ErroDBH[Estacao] 
            
            # + self.Wtamanho_Produto_ErroMDI[Estacao]   + self.Wtamanho_Produto_ErroMFI[Estacao]
        
        df = pd.DataFrame([[self.ErroWellTotal, self.WtamanhoErroDEC , self.WtamanhoErroDBH , self.WtamanhoErroMFI, self.WtamanhoErroMDI, self.WtamanhoErroDST_G, self.Wtamanho_Total_ErroDEC, self.Wtamanho_Total_ErroDBH, self.Wtamanho_Total_ErroMFI, self.Wtamanho_Total_ErroMDI, self.Wtamanho_Total_ErroDST_G,        self.Wtamanho_Produto_ErroDEC , self.Wtamanho_Produto_ErroDBH , self.Wtamanho_Produto_ErroMFI , self.Wtamanho_Produto_ErroMDI , self.Wtamanho_Produto_ErroDST_G ]], columns=[        'self.ErroWellTotal', 'self.WtamanhoErroDEC'   ,        'self.WtamanhoErroDBH '  ,        'self.WtamanhoErroMFI '  ,        'self.WtamanhoErroMDI '  ,        'self.WtamanhoErroDST_G' ,        'self.Wtamanho_Total_ErroDEC'   ,        'self.Wtamanho_Total_ErroDBH'   ,        'self.Wtamanho_Total_ErroMFI'   ,        'self.Wtamanho_Total_ErroMDI'   ,        'self.Wtamanho_Total_ErroDST_G' ,        'self.Wtamanho_Produto_ErroDEC'   ,        'self.Wtamanho_Produto_ErroDBH'   ,        'self.Wtamanho_Produto_ErroMFI'   ,        'self.Wtamanho_Produto_ErroMDI'   ,        'self.Wtamanho_Produto_ErroDST_G'  ])
        
        writer = pd.ExcelWriter('Global_Tamanho_Erro.xlsx')
        
        df.to_excel(writer,'Efeito MWD',float_format='%.5f')
        
        writer.save()
        
        
    def ErroSurveyMWD(self):
        
        for Estacao in range(0,len(self.dadosOriginaisMWD)):
            
            self.ErroTotalMWD[Estacao] = self.ErroSistematicoTotal[Estacao] + self.ErroWellTotal[Estacao] +   self.ErroRandomicoTotal[Estacao] 
            
            print("\nMatriz Covariancia MWD - Estacao: ", Estacao + 1)    
            
            print(self.ErroTotalMWD[Estacao])
        
class TamanhoErroSurveyGyro(EfeitoErroSurveyGWD):

    def __init__(self):
        
        super().__init__()
        
#Magnitude erros modo Continuo e estacionário

    #Modo de propagação sistematico e randomico
        self.Mag_AXYZ_XYB   = 0.005 #m/s² 
        self.Mag_AXY_B      = 0.005 #m/s² 
    
    #Modo de propagação sistemático
        self.Mag_AXYZ_ZB    = 0.0017 #m/s² 
        self.Mag_AXYZ_SF    = 0.000266
        self.Mag_AXYZ_MS    = 0.05 #deg
        self.Mag_AXY_SF     = 0.0005
        self.Mag_AXY_MS     = 0.005 #m/s² 
        self.Mag_AXY_GB     = 0.005 #m/s²

#Magnitude erros modo estacionário

    #Modo de propagação sistematico e randomico
        self.Mag_GXYZ_XYB1  = 0.1 #deg/h
        self.Mag_GXYZ_XYB2  = 0.1 #deg/h
        self.Mag_GXYZ_XYG2  = 0.5 #deg/h
        self.Mag_GXYZ_XYG3  = 0.5 #deg/h
        self.Mag_GXYZ_ZG1   = 0.5 #deg/h
        self.Mag_GXY_B1     = 0.023 #deg/h 
        self.Mag_GXY_B2     = 0.023 #deg/h
        self.Mag_GXY_G2     = 0.5 #deg/h
        self.Mag_GXY_G3     = 0.5 #deg/h
    
    #Modo de propagação randomico
        self.Mag_GXYZ_XYRN  = 0.1 #deg/h
        self.Mag_GXYZ_ZRN   = 0.1 #deg/h
        self.Mag_GXY_RN     = 0.072 #deg/h
        
    #Modo de propagação sistematico 
        self.Mag_GXYZ_XYG1  = 0.5 #deg/h
        self.Mag_GXYZ_XYG4  = 0.5 #deg/h
        self.Mag_GXYZ_ZB    = 0.1 #deg/h
        self.Mag_GXYZ_ZG2   = 0.5 #deg/h
        self.Mag_GXYZ_SF    = 0.001
        self.Mag_GXYZ_MIS   = 0.05 #deg/h
        self.Mag_GXY_G1     = 0.28 #deg/h
        self.Mag_GXY_G4     = 0.03 #deg/h
        self.Mag_GXY_SF     = 0.001
        self.Mag_GXY_MIS    = 0.05 #deg/h
        self.Mag_EXTREF     = 5.0 #deg
        self.Mag_EXTTIE     = 0.0 #deg
        self.Mag_EXTMIS     = 0.0 #deg
        
#Magnitude erros modo continuo

     #Modo de propagação sistematico 
        self.Mag_GXYZ_GD    = 0.5 #deg/h
        self.Mag_GXYZ_RW    = 0.5 #deg/sqrt(h)
        self.Mag_GXY_GD     = 0.028 #deg/h
        self.Mag_GXY_RW     = 0.5 #deg/sqrt(h)
        self.Mag_GZ_GD      = 1.0 #deg/h
        self.Mag_GZ_RW      = 1.0 #deg/sqrt(h)

#Magnitude erros modo Continuo e estacionário

    #Modo de propagação sistematico 
        self.Mag_XYM1_GYRO       = 0.04 #deg
        self.Mag_XYM2_GYRO       = 0.04 #deg
        self.Mag_XYM3_GYRO       = 0.04 #deg
        self.Mag_XYM4_GYRO       = 0.04 #deg
        self.Mag_VSAG       = 0.08 #deg
        self.Mag_DRF_S      = 0.5 #m
        
    #Modo de propagação randomico 
        self.Mag_DRF_R      = 0.5 #m
    
    #Modo de propagação sistematico e global 
        self.Mag_DSF_W      = 0.001
        
    #Modo de propagação global 
        self.Mag_DST_G_GYRO      = 5 * mt.pow(10,-7) #1/m
         
##Vetores erros modo Continuo e estacionário

    #Vetores erro de propagação sistematico e randomico
        self.StamanhoErroAXYZ_XYB   = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64) 
        self.StamanhoErroAXY_B      = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)

        self.RtamanhoErroAXYZ_XYB   = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64) 
        self.RtamanhoErroAXY_B      = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
    #Vetores erro de propagação sistemático
        self.StamanhoErroAXYZ_ZB    = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroAXYZ_SF    = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroAXYZ_MS    = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroAXY_SF     = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroAXY_MS     = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroAXY_GB     = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)

#Vetores erro modo estacionário

    #Vetores erro de propagação sistematico e randomico
        self.StamanhoErroGXYZ_XYB1  = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGXYZ_XYB2  = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGXYZ_XYG2  = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGXYZ_XYG3  = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGXYZ_ZG1   = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGXY_B1     = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGXY_B2     = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGXY_G2     = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGXY_G3     = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        self.RtamanhoErroGXYZ_XYB1  = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroGXYZ_XYB2  = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroGXYZ_XYG2  = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroGXYZ_XYG3  = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroGXYZ_ZG1   = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroGXY_B1     = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroGXY_B2     = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroGXY_G2     = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroGXY_G3     = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
    #Vetores erro de propagação randomico
        self.RtamanhoErroGXYZ_XYRN  = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroGXYZ_ZRN   = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.RtamanhoErroGXY_RN     = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
    #Vetores erro de propagação sistematico 
        self.StamanhoErroGXYZ_XYG1  = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGXYZ_XYG4  = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGXYZ_ZB    = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGXYZ_ZG2   = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGXYZ_SF    = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGXYZ_MIS   = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGXY_G1     = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGXY_G4     = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGXY_SF     = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGXY_MIS    = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroEXTREF     = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroEXTTIE     = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroEXTMIS     = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
#Vetores erro modo continuo

     #Vetores erro de propagação sistematico 
        self.StamanhoErroGXYZ_GD    = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGXYZ_RW    = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGXY_GD     = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGXY_RW     = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGZ_GD      = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroGZ_RW      = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)

#Vetores erro modo Continuo e estacionário

    #Vetores erro de propagação sistematico 
        self.StamanhoErroXYM1_GYRO       = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroXYM2_GYRO       = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroXYM3_GYRO       = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroXYM4_GYRO       = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroVSAG       = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        self.StamanhoErroDRF_S      = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
    #Vetores erro de propagação randomico 
        self.RtamanhoErroDRF_R      = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
    
    #Vetores erro de propagação sistematico e global 
        self.GtamanhoErroDSF_W      = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
    #Vetores erro de propagação global 
        self.GtamanhoErroDST_G_GYRO      = np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        self.Rtamanho_Total_ErroAXYZ_XYB  = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
                    
        self.Rtamanho_Total_ErroAXY_B  = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        self.Rtamanho_Total_ErroGXYZ_XYB1   = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        self.Rtamanho_Total_ErroGXYZ_XYB2   = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        self.Rtamanho_Total_ErroGXYZ_XYG2 = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        self.Rtamanho_Total_ErroGXYZ_XYG3   = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        self.Rtamanho_Total_ErroGXYZ_ZG1   = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        self.Rtamanho_Total_ErroGXY_B1  = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        self.Rtamanho_Total_ErroGXY_B2 = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        self.Rtamanho_Total_ErroGXY_G2  = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        self.Rtamanho_Total_ErroGXY_G3  = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        self.Rtamanho_Total_ErroGXYZ_XYRN  = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        self.Rtamanho_Total_ErroGXYZ_ZRN   = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        self.Rtamanho_Total_ErroGXY_RN  = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        self.Rtamanho_Total_ErroDRF_R  = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        
        self.Stamanho_Total_ErroAXYZ_XYB  =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        #Erro acelerometro
        self.Stamanho_Total_ErroAXY_B  =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        #Erro acelerometro
        self.Stamanho_Total_ErroAXYZ_ZB  =        np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        #Erro acelerometro
        self.Stamanho_Total_ErroAXYZ_SF    =    np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64) 
        
        #Erro acelerometro
        self.Stamanho_Total_ErroAXYZ_MS  =       np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64) 
        
        #Erro acelerometro
        self.Stamanho_Total_ErroAXY_SF  =        np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64) 
        
        #Erro acelerometro
        self.Stamanho_Total_ErroAXY_MS  =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        #Erro acelerometro
        self.Stamanho_Total_ErroAXY_GB =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
       
        #Erro Gyro XYZ
        self.Stamanho_Total_ErroGXYZ_XYB1      =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        #Erro Gyro XYZ
        self.Stamanho_Total_ErroGXYZ_XYB2   =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        #Erro Gyro XYZ
        self.Stamanho_Total_ErroGXYZ_XYG2     =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        #Erro Gyro XYZ
        self.Stamanho_Total_ErroGXYZ_XYG3       =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        #Erro Gyro XYZ
        self.Stamanho_Total_ErroGXYZ_ZG1  =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        #Erro Gyro XY
        self.Stamanho_Total_ErroGXY_B1 =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        #Erro Gyro XY
        self.Stamanho_Total_ErroGXY_B2 =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        #Erro Gyro XY
        self.Stamanho_Total_ErroGXY_G2 =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        #Erro Gyro XY
        self.Stamanho_Total_ErroGXY_G3 =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        #Erro Gyro XYZ
        self.Stamanho_Total_ErroGXYZ_XYG1       =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
       
        #Erro Gyro XYZ
        self.Stamanho_Total_ErroGXYZ_XYG4   =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        #Erro Gyro XYZ
        self.Stamanho_Total_ErroGXYZ_ZB     =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        #Erro Gyro XYZ
        self.Stamanho_Total_ErroGXYZ_ZG2    =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        #Erro Gyro XYZ
        self.Stamanho_Total_ErroGXYZ_SF =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        #Erro Gyro XYZ
        self.Stamanho_Total_ErroGXYZ_MIS     =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        #Erro Gyro XY
        self.Stamanho_Total_ErroGXY_G1 =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        #Erro Gyro XY
        self.Stamanho_Total_ErroGXY_G4 =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        #Erro Gyro XY
        self.Stamanho_Total_ErroGXY_SF =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
      
        #Erro Gyro XY
        self.Stamanho_Total_ErroGXY_MIS     =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        #Erro GyroXY   
        self.Stamanho_Total_ErroGXYZ_GD     =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
       
        #Erro Gyro
        self.Stamanho_Total_ErroGXYZ_RW     =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
     
        #Erro Gyro XY
        self.Stamanho_Total_ErroGXY_GD =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
     
        #Erro Gyro XY
        self.Stamanho_Total_ErroGXY_RW =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
      
        #Erro Gyro Z
        self.Stamanho_Total_ErroGZ_GD  =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
     
        #Erro Gyro Z
        self.Stamanho_Total_ErroGZ_RW  =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
      
        #Erro desalinhamento
        self.Stamanho_Total_ErroXYM1_GYRO  =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
     
        #Erro desalinhamento
        self.Stamanho_Total_ErroXYM2_GYRO   =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
     
        #Erro desalinhamento
        self.Stamanho_Total_ErroXYM3_GYRO =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
    
        #Erro desalinhamento
        self.Stamanho_Total_ErroXYM4_GYRO   =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
     
        #Erro vertical SAG
        self.Stamanho_Total_ErroVSAG =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
      
        #Erro profundidade
        self.Stamanho_Total_ErroDRF_S =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        #Erro Externo
        self.Stamanho_Total_ErroEXTREF =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
      
        #Erro Externo
        self.Stamanho_Total_ErroEXTTIE =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
      
        #Erro Externo
        self.Stamanho_Total_ErroEXTMIS =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
  
        self.Gtamanho_Total_ErroDSF_W =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        self.Gtamanho_Total_ErroDST_G_GYRO =         np.zeros((len(self.dadosOriginaisGWD),1,3,1),dtype=np.float64)
        
        self.Stamanho_Produto_ErroAXYZ_XYB  =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        #Erro acelerometro
        self.Stamanho_Produto_ErroAXY_B  =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        #Erro acelerometro
        self.Stamanho_Produto_ErroAXYZ_ZB  =        np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        #Erro acelerometro
        self.Stamanho_Produto_ErroAXYZ_SF    =    np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64) 
        
        #Erro acelerometro
        self.Stamanho_Produto_ErroAXYZ_MS  =       np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64) 
        
        #Erro acelerometro
        self.Stamanho_Produto_ErroAXY_SF  =        np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64) 
        
        #Erro acelerometro
        self.Stamanho_Produto_ErroAXY_MS  =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        #Erro acelerometro
        self.Stamanho_Produto_ErroAXY_GB =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
       
        #Erro Gyro XYZ
        self.Stamanho_Produto_ErroGXYZ_XYB1      =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        #Erro Gyro XYZ
        self.Stamanho_Produto_ErroGXYZ_XYB2   =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        #Erro Gyro XYZ
        self.Stamanho_Produto_ErroGXYZ_XYG2     =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        #Erro Gyro XYZ
        self.Stamanho_Produto_ErroGXYZ_XYG3       =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        #Erro Gyro XYZ
        self.Stamanho_Produto_ErroGXYZ_ZG1  =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        #Erro Gyro XY
        self.Stamanho_Produto_ErroGXY_B1 =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        #Erro Gyro XY
        self.Stamanho_Produto_ErroGXY_B2 =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        #Erro Gyro XY
        self.Stamanho_Produto_ErroGXY_G2 =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        #Erro Gyro XY
        self.Stamanho_Produto_ErroGXY_G3 =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        #Erro Gyro XYZ
        self.Stamanho_Produto_ErroGXYZ_XYG1       =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
       
        #Erro Gyro XYZ
        self.Stamanho_Produto_ErroGXYZ_XYG4   =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        #Erro Gyro XYZ
        self.Stamanho_Produto_ErroGXYZ_ZB     =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        #Erro Gyro XYZ
        self.Stamanho_Produto_ErroGXYZ_ZG2    =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        #Erro Gyro XYZ
        self.Stamanho_Produto_ErroGXYZ_SF =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        #Erro Gyro XYZ
        self.Stamanho_Produto_ErroGXYZ_MIS     =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        #Erro Gyro XY
        self.Stamanho_Produto_ErroGXY_G1 =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        #Erro Gyro XY
        self.Stamanho_Produto_ErroGXY_G4 =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        #Erro Gyro XY
        self.Stamanho_Produto_ErroGXY_SF =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
      
        #Erro Gyro XY
        self.Stamanho_Produto_ErroGXY_MIS     =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        #Erro GyroXY   
        self.Stamanho_Produto_ErroGXYZ_GD     =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
       
        #Erro Gyro
        self.Stamanho_Produto_ErroGXYZ_RW     =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
     
        #Erro Gyro XY
        self.Stamanho_Produto_ErroGXY_GD =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
     
        #Erro Gyro XY
        self.Stamanho_Produto_ErroGXY_RW =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
      
        #Erro Gyro Z
        self.Stamanho_Produto_ErroGZ_GD  =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
     
        #Erro Gyro Z
        self.Stamanho_Produto_ErroGZ_RW  =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
      
        #Erro desalinhamento
        self.Stamanho_Produto_ErroXYM1_GYRO  =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
     
        #Erro desalinhamento
        self.Stamanho_Produto_ErroXYM2_GYRO   =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
     
        #Erro desalinhamento
        self.Stamanho_Produto_ErroXYM3_GYRO =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
    
        #Erro desalinhamento
        self.Stamanho_Produto_ErroXYM4_GYRO   =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
     
        #Erro vertical SAG
        self.Stamanho_Produto_ErroVSAG =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
      
        #Erro profundidade
        self.Stamanho_Produto_ErroDRF_S =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        #Erro Externo
        self.Stamanho_Produto_ErroEXTREF =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
      
        #Erro Externo
        self.Stamanho_Produto_ErroEXTTIE =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
      
        #Erro Externo
        self.Stamanho_Produto_ErroEXTMIS =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
  
        self.Gtamanho_Produto_ErroDSF_W =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        self.Gtamanho_Produto_ErroDST_G_GYRO =         np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        
        self.ErroRandomicoTotal_GYRO_XY = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        self.ErroSistematicoTotal_GYRO_XY = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        self.ErroRandomicoTotal_GYRO_XYZ = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        self.ErroSistematicoTotal_GYRO_XYZ = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        self.ErroWellTotal_GYRO = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
                    
        self.ErroTotalGYRO = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
        
        if self.tipoGyro == 0:
            
            self.ErroSistematicoGYRO_XY()
            self.ErroRandomicoGYRO_XY()
            
        if self.tipoGyro == 1:
            
            self.ErroSistematicoGYRO_XYZ()
            self.ErroRandomicoGYRO_XYZ()
        
        self.ErroWellGYRO()
        self.ErroSurveyGYRO()
        
    def ErroSistematicoGYRO_XYZ(self):
        
        for Estacao in range(0,len(self.dadosOriginaisGWD)):
            for coluna in range(0,1):
                for linha in range(0,3):
                    
                    self.StamanhoErroAXYZ_XYB[Estacao][coluna][linha]  = self.Mag_AXYZ_XYB * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.AXYZ_XYB[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.AXYZ_XYB[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.AXYZ_XYB[Estacao][coluna + 2]))                     

                    #Erro acelerometro
                    self.StamanhoErroAXYZ_ZB     [Estacao][coluna][linha]  = self.Mag_AXYZ_ZB  * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.AXYZ_ZB[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.AXYZ_ZB[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.AXYZ_ZB[Estacao][coluna + 2]))                    
                    
                    #Erro acelerometro
                    self.StamanhoErroAXYZ_SF     [Estacao][coluna][linha]  = self.Mag_AXYZ_SF  * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.AXYZ_SF [Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.AXYZ_SF [Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.AXYZ_SF [Estacao][coluna + 2]))                    
                    
                    #Erro acelerometro
                    self.StamanhoErroAXYZ_MS     [Estacao][coluna][linha]  = self.Mag_AXYZ_MS * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.AXYZ_MS[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.AXYZ_MS[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.AXYZ_MS[Estacao][coluna + 2]))                    
                                           
                    #Erro Gyro XYZ
                    self.StamanhoErroGXYZ_XYB1   [Estacao][coluna][linha]  = self.Mag_GXYZ_XYB1 * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXYZ_XYB1[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXYZ_XYB1[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXYZ_XYB1[Estacao][coluna + 2]))                    
                    
                    #Erro Gyro XYZ
                    self.StamanhoErroGXYZ_XYB2   [Estacao][coluna][linha]  = self.Mag_GXYZ_XYB2 * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXYZ_XYB2[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXYZ_XYB2[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXYZ_XYB2[Estacao][coluna + 2]))                    
                    
                    #Erro Gyro XYZ
                    self.StamanhoErroGXYZ_XYG2   [Estacao][coluna][linha]  = self.Mag_GXYZ_XYG2 * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXYZ_XYG2[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXYZ_XYG2[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXYZ_XYG2[Estacao][coluna + 2]))                    
                    
                    #Erro Gyro XYZ
                    self.StamanhoErroGXYZ_XYG3   [Estacao][coluna][linha]  = self.Mag_GXYZ_XYG3 * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXYZ_XYG3[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXYZ_XYG3[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXYZ_XYG3[Estacao][coluna + 2]))                    
                    
                    #Erro Gyro XYZ
                    self.StamanhoErroGXYZ_ZG1    [Estacao][coluna][linha]  = self.Mag_GXYZ_ZG1 * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXYZ_ZG1[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXYZ_ZG1[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXYZ_ZG1[Estacao][coluna + 2]))                    
                    
                    #Erro Gyro XYZ
                    self.StamanhoErroGXYZ_XYG1   [Estacao][coluna][linha]  = self.Mag_GXYZ_XYG1 * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXYZ_XYG1[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXYZ_XYG1[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXYZ_XYG1[Estacao][coluna + 2]))                    
                   
                    #Erro Gyro XYZ
                    self.StamanhoErroGXYZ_XYG4   [Estacao][coluna][linha]  = self.Mag_GXYZ_XYG4  * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXYZ_XYG4 [Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXYZ_XYG4 [Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXYZ_XYG4 [Estacao][coluna + 2]))                    
                    
                    #Erro Gyro XYZ
                    self.StamanhoErroGXYZ_ZB     [Estacao][coluna][linha]  = self.Mag_GXYZ_ZB * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXYZ_ZB[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXYZ_ZB[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXYZ_ZB[Estacao][coluna + 2]))                    
                    
                    #Erro Gyro XYZ
                    self.StamanhoErroGXYZ_ZG2    [Estacao][coluna][linha]  = self.Mag_GXYZ_ZG2 * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXYZ_ZG2[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXYZ_ZG2[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXYZ_ZG2[Estacao][coluna + 2]))                    
                    
                    #Erro Gyro XYZ
                    self.StamanhoErroGXYZ_SF     [Estacao][coluna][linha]  = self.Mag_GXYZ_SF * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXYZ_SF[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXYZ_SF[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXYZ_SF[Estacao][coluna + 2]))                    
                    
                    #Erro Gyro XYZ
                    self.StamanhoErroGXYZ_MIS[Estacao][coluna][linha]  = self.Mag_GXYZ_MIS * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXYZ_MIS[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXYZ_MIS[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXYZ_MIS[Estacao][coluna + 2]))                    
                    
                    #Erro Gyro XYZ   
                    self.StamanhoErroGXYZ_GD     [Estacao][coluna][linha]  = self.Mag_GXYZ_GD * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXYZ_GD[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXYZ_GD[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXYZ_GD[Estacao][coluna + 2]))  
                    
                    #Erro Gyro XYZ
                    self.StamanhoErroGXYZ_RW     [Estacao][coluna][linha]  = self.Mag_GXYZ_RW * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXYZ_RW[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXYZ_RW[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXYZ_RW[Estacao][coluna + 2]))                    
                 
                    #Erro Gyro Z
                    self.StamanhoErroGZ_GD  [Estacao][coluna][linha]  = self.Mag_GZ_GD * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GZ_GD[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GZ_GD[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GZ_GD[Estacao][coluna + 2]))                    

                    #Erro Gyro Z
                    self.StamanhoErroGZ_RW  [Estacao][coluna][linha]  = self.Mag_GZ_RW * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GZ_RW[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GZ_RW[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GZ_RW[Estacao][coluna + 2]))                    
                  
                    #Erro desalinhamento
                    self.StamanhoErroXYM1_GYRO   [Estacao][coluna][linha]  = self.Mag_XYM1_GYRO * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.XYM1_GYRO[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.XYM1_GYRO[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.XYM1_GYRO[Estacao][coluna + 2]))                    
                 
                    #Erro desalinhamento
                    self.StamanhoErroXYM2_GYRO   [Estacao][coluna][linha]  = self.Mag_XYM2_GYRO * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.XYM2_GYRO[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.XYM2_GYRO[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.XYM2_GYRO[Estacao][coluna + 2]))                    
                    
                    if self.I_GYRO[Estacao] <= 0.2:
                        
                        if Estacao == 0:
                            MDauxiliar = 0.0
                        else:
                            MDauxiliar = self.Md_GYRO[Estacao - 1]

                            self.StamanhoErroXYM3_GYRO[Estacao][coluna][linha] = self.Mag_XYM3_GYRO * 0.5 * ((self.Md_GYRO[Estacao + 1] - MDauxiliar) * (self.XYM3_GYRO[Estacao][coluna]))
                            self.StamanhoErroXYM4_GYRO[Estacao][coluna][linha] = self.Mag_XYM4_GYRO * 0.5 * ((self.Md_GYRO[Estacao + 1] - MDauxiliar) * (self.XYM4_GYRO[Estacao][coluna]))
                        
                    else:

                        #Erro desalinhamento
                        self.StamanhoErroXYM3_GYRO   [Estacao][coluna][linha]  = self.Mag_XYM3_GYRO * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.XYM3_GYRO[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.XYM3_GYRO[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.XYM3_GYRO[Estacao][coluna + 2]))                    
                    
                        #Erro desalinhamento
                        self.StamanhoErroXYM4_GYRO   [Estacao][coluna][linha]  = self.Mag_XYM4_GYRO * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.XYM4_GYRO[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.XYM4_GYRO[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.XYM4_GYRO[Estacao][coluna + 2]))                    
                 
                    #Erro vertical SAG
                    self.StamanhoErroVSAG   [Estacao][coluna][linha]  = self.Mag_VSAG * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.VSAG[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.VSAG[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.VSAG[Estacao][coluna + 2]))                    
                  
                    #Erro profundidade
                    self.StamanhoErroDRF_S [Estacao][coluna][linha]  = self.Mag_DRF_S * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.DRF_S[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.DRF_S[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.DRF_S[Estacao][coluna + 2]))
                    
                    #Erro Externo
                    self.StamanhoErroEXTREF [Estacao][coluna][linha]  = self.Mag_EXTREF * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.EXTREF[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.EXTREF[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.EXTREF[Estacao][coluna + 2]))                    
                  
                    #Erro Externo
                    self.StamanhoErroEXTTIE[Estacao][coluna][linha]  = self.Mag_EXTTIE * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.EXTTIE[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.EXTTIE[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.EXTTIE[Estacao][coluna + 2]))                    
                  
                    #Erro Externo
                    self.StamanhoErroEXTMIS[Estacao][coluna][linha]  = self.Mag_EXTMIS * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.EXTMIS[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.EXTMIS[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.EXTMIS[Estacao][coluna + 2]))                    
      
                    self.GtamanhoErroDSF_W[Estacao][coluna][linha]  = self.Mag_DSF_W * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.DSF_W[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.DSF_W[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.DSF_W[Estacao][coluna + 2]))
                    
        for Estacao in range(1,len(self.dadosOriginaisGWD)):
           
            #Erro acelerometro
            self.Stamanho_Total_ErroAXYZ_XYB [Estacao]  =         self.Stamanho_Total_ErroAXYZ_XYB [Estacao - 1] +         self.StamanhoErroAXYZ_XYB [Estacao]
            
            #Erro acelerometro
            self.Stamanho_Total_ErroAXYZ_ZB [Estacao]    =         self.Stamanho_Total_ErroAXYZ_ZB [Estacao - 1]   +         self.StamanhoErroAXYZ_ZB [Estacao]
            
            #Erro acelerometro
            self.Stamanho_Total_ErroAXYZ_SF [Estacao]   =         self.Stamanho_Total_ErroAXYZ_SF [Estacao - 1]  +         self.StamanhoErroAXYZ_SF [Estacao]   
            
            #Erro acelerometro
            self.Stamanho_Total_ErroAXYZ_MS [Estacao]   =         self.Stamanho_Total_ErroAXYZ_MS [Estacao - 1]  +         self.StamanhoErroAXYZ_MS [Estacao]
            
            #Erro Gyro XYZ
            self.Stamanho_Total_ErroGXYZ_XYB1[Estacao]  =         self.Stamanho_Total_ErroGXYZ_XYB1[Estacao - 1] +         self.StamanhoErroGXYZ_XYB1[Estacao]          
            
            #Erro Gyro XYZ
            self.Stamanho_Total_ErroGXYZ_XYB2 [Estacao] =         self.Stamanho_Total_ErroGXYZ_XYB2 [Estacao - 1] +         self.StamanhoErroGXYZ_XYB2 [Estacao]  
            
            #Erro Gyro XYZ
            self.Stamanho_Total_ErroGXYZ_XYG2 [Estacao] =         self.Stamanho_Total_ErroGXYZ_XYG2 [Estacao - 1] +         self.StamanhoErroGXYZ_XYG2 [Estacao]    
            
            #Erro Gyro XYZ
            self.Stamanho_Total_ErroGXYZ_XYG3 [Estacao] =         self.Stamanho_Total_ErroGXYZ_XYG3 [Estacao - 1] +         self.StamanhoErroGXYZ_XYG3 [Estacao]          
            
            #Erro Gyro XYZ
            self.Stamanho_Total_ErroGXYZ_ZG1[Estacao]   =         self.Stamanho_Total_ErroGXYZ_ZG1[Estacao - 1]   +         self.StamanhoErroGXYZ_ZG1[Estacao]   
            
            #Erro Gyro XYZ
            self.Stamanho_Total_ErroGXYZ_XYG1 [Estacao] =         self.Stamanho_Total_ErroGXYZ_XYG1 [Estacao - 1] +         self.StamanhoErroGXYZ_XYG1   [Estacao]    
           
            #Erro Gyro XYZ
            self.Stamanho_Total_ErroGXYZ_XYG4 [Estacao] =         self.Stamanho_Total_ErroGXYZ_XYG4 [Estacao - 1] +         self.StamanhoErroGXYZ_XYG4   [Estacao]
            
            #Erro Gyro XYZ
            self.Stamanho_Total_ErroGXYZ_ZB [Estacao]   =         self.Stamanho_Total_ErroGXYZ_ZB [Estacao - 1]   +         self.StamanhoErroGXYZ_ZB     [Estacao]
            
            #Erro Gyro XYZ
            self.Stamanho_Total_ErroGXYZ_ZG2 [Estacao]  =         self.Stamanho_Total_ErroGXYZ_ZG2 [Estacao - 1]  +         self.StamanhoErroGXYZ_ZG2 [Estacao]   
            
            #Erro Gyro XYZ
            self.Stamanho_Total_ErroGXYZ_SF [Estacao]   =         self.Stamanho_Total_ErroGXYZ_SF [Estacao - 1]   +         self.StamanhoErroGXYZ_SF [Estacao]
            
            #Erro Gyro XYZ
            self.Stamanho_Total_ErroGXYZ_MIS [Estacao]  =         self.Stamanho_Total_ErroGXYZ_MIS [Estacao - 1]  +         self.StamanhoErroGXYZ_MIS [Estacao]    
            
            #Erro Gyro XYZ
            self.Stamanho_Total_ErroGXYZ_GD [Estacao]  =         self.Stamanho_Total_ErroGXYZ_GD [Estacao - 1]  +         self.StamanhoErroGXYZ_GD [Estacao]   
                    
            #Erro Gyro XYZ
            self.Stamanho_Total_ErroGXYZ_RW [Estacao]   =         self.Stamanho_Total_ErroGXYZ_RW [Estacao - 1]   +         self.StamanhoErroGXYZ_RW     [Estacao]
         
            #Erro Gyro Z
            self.Stamanho_Total_ErroGZ_GD  [Estacao]    =         self.Stamanho_Total_ErroGZ_GD  [Estacao - 1]    +         self.StamanhoErroGZ_GD  [Estacao]
         
            #Erro Gyro Z
            self.Stamanho_Total_ErroGZ_RW  [Estacao]    =         self.Stamanho_Total_ErroGZ_RW  [Estacao - 1]    +         self.StamanhoErroGZ_RW  [Estacao]
          
            #Erro desalinhamento
            self.Stamanho_Total_ErroXYM1_GYRO   [Estacao]    =         self.Stamanho_Total_ErroXYM1_GYRO   [Estacao - 1]    +         self.StamanhoErroXYM1_GYRO   [Estacao]
         
            #Erro desalinhamento
            self.Stamanho_Total_ErroXYM2_GYRO   [Estacao]    =         self.Stamanho_Total_ErroXYM2_GYRO   [Estacao - 1]    +         self.StamanhoErroXYM2_GYRO   [Estacao]
         
            #Erro desalinhamento
            self.Stamanho_Total_ErroXYM3_GYRO   [Estacao]    =         self.Stamanho_Total_ErroXYM3_GYRO   [Estacao - 1]    +         self.StamanhoErroXYM3_GYRO   [Estacao]
        
            #Erro desalinhamento
            self.Stamanho_Total_ErroXYM4_GYRO   [Estacao]    =         self.Stamanho_Total_ErroXYM4_GYRO   [Estacao - 1]    +         self.StamanhoErroXYM4_GYRO   [Estacao]
         
            #Erro vertical SAG
            self.Stamanho_Total_ErroVSAG [Estacao]      =         self.Stamanho_Total_ErroVSAG [Estacao - 1]      +         self.StamanhoErroVSAG [Estacao]
          
            #Erro profundidade
            self.Stamanho_Total_ErroDRF_S [Estacao]     =         self.Stamanho_Total_ErroDRF_S [Estacao - 1]     +         self.StamanhoErroDRF_S [Estacao]
            
            #Erro Externo
            self.Stamanho_Total_ErroEXTREF [Estacao]    =         self.Stamanho_Total_ErroEXTREF [Estacao - 1]    +         self.StamanhoErroEXTREF [Estacao]
          
            #Erro Externo
            self.Stamanho_Total_ErroEXTTIE [Estacao]     =         self.Stamanho_Total_ErroEXTTIE[Estacao - 1]     +         self.StamanhoErroEXTTIE [Estacao]
          
            #Erro Externo
            self.Stamanho_Total_ErroEXTMIS [Estacao]     =         self.Stamanho_Total_ErroEXTMIS [Estacao - 1]     +         self.StamanhoErroEXTMIS [Estacao]
      
            self.Gtamanho_Total_ErroDSF_W [Estacao]      =         self.Gtamanho_Total_ErroDSF_W [Estacao - 1]      +         self.GtamanhoErroDSF_W [Estacao]

        for Estacao in range(0,len(self.dadosOriginaisGWD)):
            for linha in range(0,3):
                for coluna in range(0,3):
        
                    #Erro acelerometro
                    self.Stamanho_Produto_ErroAXYZ_XYB [Estacao][0][linha][coluna]  = self.Stamanho_Total_ErroAXYZ_XYB [Estacao][0][linha] * self.Stamanho_Total_ErroAXYZ_XYB [Estacao][0][coluna]
                    
                    #Erro acelerometro
                    self.Stamanho_Produto_ErroAXYZ_ZB [Estacao]    = self.Stamanho_Total_ErroAXYZ_ZB [Estacao][0][linha]  * self.Stamanho_Total_ErroAXYZ_ZB[Estacao][0][coluna]   
                    
                    #Erro acelerometro
                    self.Stamanho_Produto_ErroAXYZ_SF [Estacao][0][linha][coluna]   = self.Stamanho_Total_ErroAXYZ_SF [Estacao][0][linha] * self.Stamanho_Total_ErroAXYZ_SF [Estacao][0][coluna]   
                    
                    #Erro acelerometro
                    self.Stamanho_Produto_ErroAXYZ_MS [Estacao][0][linha][coluna]   = self.Stamanho_Total_ErroAXYZ_MS [Estacao][0][linha] * self.Stamanho_Total_ErroAXYZ_MS [Estacao][0][coluna]
                    
                    #Erro Gyro XYZ
                    self.Stamanho_Produto_ErroGXYZ_XYB1[Estacao][0][linha][coluna]  = self.Stamanho_Total_ErroGXYZ_XYB1 [Estacao][0][linha] *         self.Stamanho_Total_ErroGXYZ_XYB1[Estacao][0][coluna]
                    
                    #Erro Gyro XYZ
                    self.Stamanho_Produto_ErroGXYZ_XYB2 [Estacao][0][linha][coluna] = self.Stamanho_Total_ErroGXYZ_XYB2 [Estacao][0][linha] * self.Stamanho_Total_ErroGXYZ_XYB2 [Estacao][0][coluna]
                    
                    #Erro Gyro XYZ
                    self.Stamanho_Produto_ErroGXYZ_XYG2 [Estacao][0][linha][coluna] = self.Stamanho_Total_ErroGXYZ_XYG2 [Estacao][0][linha] * self.Stamanho_Total_ErroGXYZ_XYG2 [Estacao][0][coluna]
                    
                    #Erro Gyro XYZ
                    self.Stamanho_Produto_ErroGXYZ_XYG3 [Estacao][0][linha][coluna] = self.Stamanho_Total_ErroGXYZ_XYG3 [Estacao][0][linha] * self.Stamanho_Total_ErroGXYZ_XYG3 [Estacao][0][coluna]
    
                    #Erro Gyro XYZ
                    self.Stamanho_Produto_ErroGXYZ_ZG1[Estacao][0][linha][coluna] = self.Stamanho_Total_ErroGXYZ_ZG1 [Estacao][0][linha] * self.Stamanho_Total_ErroGXYZ_ZG1[Estacao][0][coluna]
                    
                    #Erro Gyro XYZ
                    self.Stamanho_Produto_ErroGXYZ_XYG1 [Estacao][0][linha][coluna] = self.Stamanho_Total_ErroGXYZ_XYG1 [Estacao][0][linha] * self.Stamanho_Total_ErroGXYZ_XYG1   [Estacao][0][coluna]    
                   
                    #Erro Gyro XYZ
                    self.Stamanho_Produto_ErroGXYZ_XYG4 [Estacao][0][linha][coluna] = self.Stamanho_Total_ErroGXYZ_XYG4 [Estacao][0][linha] * self.Stamanho_Total_ErroGXYZ_XYG4   [Estacao][0][coluna]
                    
                    #Erro Gyro XYZ
                    self.Stamanho_Produto_ErroGXYZ_ZB [Estacao][0][linha][coluna]   = self.Stamanho_Total_ErroGXYZ_ZB [Estacao][0][linha]   * self.Stamanho_Total_ErroGXYZ_ZB [Estacao][0][coluna]
                    
                    #Erro Gyro XYZ
                    self.Stamanho_Produto_ErroGXYZ_ZG2 [Estacao][0][linha][coluna]  = self.Stamanho_Total_ErroGXYZ_ZG2 [Estacao][0][linha] * self.Stamanho_Total_ErroGXYZ_ZG2 [Estacao][0][coluna]   
                    
                    #Erro Gyro XYZ
                    self.Stamanho_Produto_ErroGXYZ_SF [Estacao][0][linha][coluna]   = self.Stamanho_Total_ErroGXYZ_ZG2 [Estacao][0][linha] * self.StamanhoErroGXYZ_SF [Estacao][0][coluna]
                    
                    #Erro Gyro XYZ
                    self.Stamanho_Produto_ErroGXYZ_MIS [Estacao][0][linha][coluna]  = self.Stamanho_Total_ErroGXYZ_MIS [Estacao][0][linha] * self.Stamanho_Total_ErroGXYZ_MIS [Estacao][0][coluna]    
                    
                    #Erro Gyro XYZ
                    self.Stamanho_Produto_ErroGXYZ_GD[Estacao][0][linha][coluna]  = self.Stamanho_Total_ErroGXYZ_GD [Estacao][0][linha] * self.Stamanho_Total_ErroGXYZ_GD [Estacao][0][coluna]   
                    
                    #Erro Gyro XYZ
                    self.Stamanho_Produto_ErroGXYZ_RW [Estacao][0][linha][coluna]   = self.Stamanho_Total_ErroGXYZ_RW [Estacao][0][linha] * self.Stamanho_Total_ErroGXYZ_RW [Estacao][0][coluna]
                 
                    #Erro Gyro Z
                    self.Stamanho_Produto_ErroGZ_GD  [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroGZ_GD [Estacao][0][linha] * self.Stamanho_Total_ErroGZ_GD  [Estacao][0][coluna]
                 
                    #Erro Gyro Z
                    self.Stamanho_Produto_ErroGZ_RW  [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroGZ_RW [Estacao][0][linha] * self.Stamanho_Total_ErroGZ_RW  [Estacao][0][coluna]
                  
                    #Erro desalinhamento
                    self.Stamanho_Produto_ErroXYM1_GYRO   [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroXYM1_GYRO [Estacao][0][linha] * self.Stamanho_Total_ErroXYM1_GYRO   [Estacao][0][coluna]
                 
                    #Erro desalinhamento
                    self.Stamanho_Produto_ErroXYM2_GYRO   [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroXYM2_GYRO [Estacao][0][linha] * self.Stamanho_Total_ErroXYM2_GYRO   [Estacao][0][coluna]
                 
                    #Erro desalinhamento
                    self.Stamanho_Produto_ErroXYM3_GYRO   [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroXYM3_GYRO [Estacao][0][linha] * self.Stamanho_Total_ErroXYM3_GYRO   [Estacao][0][coluna]
                
                    #Erro desalinhamento
                    self.Stamanho_Produto_ErroXYM4_GYRO   [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroXYM4_GYRO [Estacao][0][linha] * self.Stamanho_Total_ErroXYM4_GYRO   [Estacao][0][coluna]
                 
                    #Erro vertical SAG
                    self.Stamanho_Produto_ErroVSAG [Estacao][0][linha][coluna]      = self.Stamanho_Total_ErroVSAG [Estacao][0][linha]  * self.Stamanho_Total_ErroVSAG [Estacao][0][coluna]
                  
                    #Erro profundidade
                    self.Stamanho_Produto_ErroDRF_S [Estacao][0][linha][coluna]     = self.Stamanho_Total_ErroDRF_S [Estacao][0][linha]  * self.Stamanho_Total_ErroDRF_S [Estacao][0][coluna]
                    
                    #Erro Externo
                    self.Stamanho_Produto_ErroEXTREF [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroEXTREF [Estacao][0][linha] * self.Stamanho_Total_ErroDRF_S [Estacao][0][coluna]
                  
                    #Erro Externo
                    self.Stamanho_Produto_ErroEXTTIE[Estacao][0][linha][coluna]     = self.Stamanho_Total_ErroEXTTIE [Estacao][0][linha] * self.Stamanho_Total_ErroEXTTIE[Estacao][0][coluna]
                  
                    #Erro Externo
                    self.Stamanho_Produto_ErroEXTMIS[Estacao][0][linha][coluna]     = self.Stamanho_Total_ErroEXTMIS [Estacao][0][linha] * self.Stamanho_Total_ErroEXTMIS[Estacao][0][coluna]
              
                    self.Gtamanho_Produto_ErroDSF_W[Estacao][0][linha][coluna]      = self.Gtamanho_Total_ErroDSF_W [Estacao][0][linha]  * self.Gtamanho_Total_ErroDSF_W[Estacao][0][coluna]
                                      
            self.ErroSistematicoTotal_GYRO_XYZ[Estacao] = self.Stamanho_Produto_ErroAXYZ_XYB [Estacao] + self.Stamanho_Produto_ErroAXYZ_ZB [Estacao] + self.Stamanho_Produto_ErroAXYZ_SF [Estacao]+ self.Stamanho_Produto_ErroAXYZ_MS [Estacao]  + self.Stamanho_Produto_ErroGXYZ_XYB1[Estacao] + self.Stamanho_Produto_ErroGXYZ_XYB2 [Estacao]+ self.Stamanho_Produto_ErroGXYZ_XYG2 [Estacao] + self.Stamanho_Produto_ErroGXYZ_XYG3 [Estacao] + self.Stamanho_Produto_ErroGXYZ_ZG1[Estacao] + self.Stamanho_Produto_ErroGXYZ_XYG1 [Estacao] + self.Stamanho_Produto_ErroGXYZ_XYG4 [Estacao] + self.Stamanho_Produto_ErroGXYZ_ZB [Estacao] + self.Stamanho_Produto_ErroGXYZ_ZG2 [Estacao] + self.Stamanho_Produto_ErroGXYZ_SF [Estacao] + self.Stamanho_Produto_ErroGXYZ_MIS [Estacao]  +self.Stamanho_Produto_ErroGXYZ_GD [Estacao] + self.Stamanho_Produto_ErroGXYZ_RW [Estacao] + self.Stamanho_Produto_ErroGZ_GD  [Estacao] + self.Stamanho_Produto_ErroGZ_RW  [Estacao] + self.Stamanho_Produto_ErroXYM1_GYRO   [Estacao] + self.Stamanho_Produto_ErroXYM2_GYRO   [Estacao] + self.Stamanho_Produto_ErroXYM3_GYRO   [Estacao] + self.Stamanho_Produto_ErroXYM4_GYRO   [Estacao] + self.Stamanho_Produto_ErroVSAG [Estacao] + self.Stamanho_Produto_ErroDRF_S [Estacao]  +self.Stamanho_Produto_ErroEXTTIE[Estacao]  + self.Gtamanho_Produto_ErroDSF_W[Estacao] #+ self.Stamanho_Produto_ErroEXTREF [Estacao] + self.Stamanho_Produto_ErroEXTMIS[Estacao]
                    
            df = pd.DataFrame([[self.StamanhoErroAXYZ_XYB   , self.StamanhoErroAXY_B, self.StamanhoErroGXYZ_XYB1, self.StamanhoErroGXYZ_XYB2, self.StamanhoErroGXYZ_XYG2  , self.StamanhoErroGXYZ_XYG3, self.StamanhoErroGXYZ_ZG1, self.StamanhoErroGXY_B1, self.StamanhoErroGXY_B2, self.StamanhoErroGXY_G2, self.StamanhoErroGXY_G3, self.StamanhoErroGXYZ_XYG1, self.StamanhoErroGXYZ_XYG4  , self.StamanhoErroGXYZ_ZB, self.StamanhoErroGXYZ_ZG2, self.StamanhoErroGXYZ_SF, self.StamanhoErroGXYZ_MIS, self.StamanhoErroGXY_G1,self.StamanhoErroGXY_G4 , self.StamanhoErroGXY_SF, self.StamanhoErroGXY_MIS, self.StamanhoErroEXTREF, self.StamanhoErroEXTTIE, self.StamanhoErroEXTMIS , self.StamanhoErroGXYZ_GD, self.StamanhoErroGXYZ_RW, self.StamanhoErroGXY_GD, self.StamanhoErroGXY_RW, self.StamanhoErroGZ_GD, self.StamanhoErroGZ_RW, self.StamanhoErroXYM1_GYRO, self.StamanhoErroXYM2_GYRO, self.StamanhoErroXYM3_GYRO, self.StamanhoErroXYM4_GYRO, self.StamanhoErroVSAG, self.StamanhoErroDRF_S, self.Stamanho_Total_ErroAXYZ_XYB, self.Stamanho_Total_ErroAXY_B, self.Stamanho_Total_ErroAXYZ_ZB, self.Stamanho_Total_ErroAXYZ_SF, self.Stamanho_Total_ErroAXYZ_MS, self.Stamanho_Total_ErroAXY_SF, self.Stamanho_Total_ErroAXY_MS, self.Stamanho_Total_ErroAXY_GB , self.Stamanho_Total_ErroGXYZ_XYB1 , self.Stamanho_Total_ErroGXYZ_XYB2, self.Stamanho_Total_ErroGXYZ_XYG2, self.Stamanho_Total_ErroGXYZ_XYG3, self.Stamanho_Total_ErroGXYZ_ZG1, self.Stamanho_Total_ErroGXY_B1, self.Stamanho_Total_ErroGXY_B2, self.Stamanho_Total_ErroGXY_G2, self.Stamanho_Total_ErroGXY_G3, self.Stamanho_Total_ErroGXYZ_XYG1, self.Stamanho_Total_ErroGXYZ_XYG4, self.Stamanho_Total_ErroGXYZ_ZB, self.Stamanho_Total_ErroGXYZ_ZG2,                self.Stamanho_Total_ErroGXYZ_SF, self.Stamanho_Total_ErroGXYZ_MIS, self.Stamanho_Total_ErroGXY_G1, self.Stamanho_Total_ErroGXY_G4, self.Stamanho_Total_ErroGXY_SF, self.Stamanho_Total_ErroGXY_MIS, self.Stamanho_Total_ErroGXYZ_GD, self.Stamanho_Total_ErroGXYZ_RW, self.Stamanho_Total_ErroGXY_GD, self.Stamanho_Total_ErroGXY_RW , self.Stamanho_Total_ErroGZ_GD , self.Stamanho_Total_ErroGZ_RW , self.Stamanho_Total_ErroXYM1_GYRO, self.Stamanho_Total_ErroXYM2_GYRO, self.Stamanho_Total_ErroXYM3_GYRO, self.Stamanho_Total_ErroXYM4_GYRO, self.Stamanho_Total_ErroVSAG, self.Stamanho_Total_ErroDRF_S, self.Stamanho_Total_ErroEXTREF, self.Stamanho_Total_ErroEXTTIE ,                self.Stamanho_Total_ErroEXTMIS , self.Gtamanho_Total_ErroDSF_W, self.Stamanho_Produto_ErroAXYZ_XYB, self.Stamanho_Produto_ErroAXY_B, self.Stamanho_Produto_ErroAXYZ_ZB , self.Stamanho_Produto_ErroAXYZ_SF , self.Stamanho_Produto_ErroAXYZ_MS, self.Stamanho_Produto_ErroAXY_SF , self.Stamanho_Produto_ErroAXY_MS, self.Stamanho_Produto_ErroAXY_GB, self.Stamanho_Produto_ErroGXYZ_XYB1, self.Stamanho_Produto_ErroGXYZ_XYB2 , self.Stamanho_Produto_ErroGXYZ_XYG2 , self.Stamanho_Produto_ErroGXYZ_XYG3 , self.Stamanho_Produto_ErroGXYZ_ZG1,  self.Stamanho_Produto_ErroGXY_B1 , self.Stamanho_Produto_ErroGXY_B2 , self.Stamanho_Produto_ErroGXY_G2 , self.Stamanho_Produto_ErroGXY_G3 , self.Stamanho_Produto_ErroGXYZ_XYG1 , self.Stamanho_Produto_ErroGXYZ_XYG4 , self.Stamanho_Produto_ErroGXYZ_ZB   ,self.Stamanho_Produto_ErroGXYZ_ZG2, self.Stamanho_Produto_ErroGXYZ_SF, self.Stamanho_Produto_ErroGXYZ_MIS  , self.Stamanho_Produto_ErroGXY_G1,  self.Stamanho_Produto_ErroGXY_G4 , self.Stamanho_Produto_ErroGXY_SF , self.Stamanho_Produto_ErroGXY_MIS, self.Stamanho_Produto_ErroGXYZ_GD, self.Stamanho_Produto_ErroGXYZ_RW, self.Stamanho_Produto_ErroGXY_GD , self.Stamanho_Produto_ErroGXY_RW, self.Stamanho_Produto_ErroGZ_GD  , self.Stamanho_Produto_ErroGZ_RW  , self.Stamanho_Produto_ErroXYM1_GYRO  , self.Stamanho_Produto_ErroXYM2_GYRO  , self.Stamanho_Produto_ErroXYM3_GYRO, self.Stamanho_Produto_ErroXYM4_GYRO, self.Stamanho_Produto_ErroVSAG , self.Stamanho_Produto_ErroDRF_S , self.Stamanho_Produto_ErroEXTREF , self.Stamanho_Produto_ErroEXTTIE, self.Stamanho_Produto_ErroEXTMIS ]], columns=['self.StamanhoErroAXYZ_XYB   ', 'self.StamanhoErroAXY_B ', 'self.StamanhoErroGXYZ_XYB1  ',                'self.StamanhoErroGXYZ_XYB2  ', 'self.StamanhoErroGXYZ_XYG2', 'self.StamanhoErroGXYZ_XYG3  ', 'self.StamanhoErroGXYZ_ZG1   ','self.StamanhoErroGXY_B1     ', 'self.StamanhoErroGXY_B2     ', 'self.StamanhoErroGXY_G2   ', 'self.StamanhoErroGXY_G3     ', 'self.StamanhoErroGXYZ_XYG1  ', 'self.StamanhoErroGXYZ_XYG4' , 'self.StamanhoErroGXYZ_ZB    ', 'self.StamanhoErroGXYZ_ZG2 ', 'self.StamanhoErroGXYZ_SF    ', 'self.StamanhoErroGXYZ_MIS   ', 'self.StamanhoErroGXY_G1    ', 'self.StamanhoErroGXY_G4     ', 'self.StamanhoErroGXY_SF   ', 'self.StamanhoErroGXY_MIS    ', 'self.StamanhoErroEXTREF     ', 'self.StamanhoErroEXTTIE    ',                'self.StamanhoErroEXTMIS     ', 'self.StamanhoErroGXYZ_GD  ', 'self.StamanhoErroGXYZ_RW    ', 'self.StamanhoErroGXY_GD     ', 'self.StamanhoErroGXY_RW    ',                'self.StamanhoErroGZ_GD      ', 'self.StamanhoErroGZ_RW    ', 'self.StamanhoErroXYM1       ','self.StamanhoErroXYM2        ', 'self.StamanhoErroXYM3      ', 'self.StamanhoErroXYM4       ', 'self.StamanhoErroVSAG     ', 'self.StamanhoErroDRF_S      ', 'self.Stamanho_Total_ErroAXYZ_XYB','self.Stamanho_Total_ErroAXY_B', 'self.Stamanho_Total_ErroAXYZ_ZB'  ,'self.Stamanho_Total_ErroAXYZ_SF','self.Stamanho_Total_ErroAXYZ_MS'  , 'self.Stamanho_Total_ErroAXY_SF ', 'self.Stamanho_Total_ErroAXY_MS','self.Stamanho_Total_ErroAXY_GB','self.Stamanho_Total_ErroGXYZ_XYB1','self.Stamanho_Total_ErroGXYZ_XYB2','self.Stamanho_Total_ErroGXYZ_XYG2','self.Stamanho_Total_ErroGXYZ_XYG3','self.Stamanho_Total_ErroGXYZ_ZG1', 'self.Stamanho_Total_ErroGXY_B1','self.Stamanho_Total_ErroGXY_B2','self.Stamanho_Total_ErroGXY_G2',               'self.Stamanho_Total_ErroGXY_G3', 'self.Stamanho_Total_ErroGXYZ_XYG1', 'self.Stamanho_Total_ErroGXYZ_XYG4','self.Stamanho_Total_ErroGXYZ_ZB', 'self.Stamanho_Total_ErroGXYZ_ZG2',               'self.Stamanho_Total_ErroGXYZ_SF', 'self.Stamanho_Total_ErroGXYZ_MIS', 'self.Stamanho_Total_ErroGXY_G1',  'self.Stamanho_Total_ErroGXY_G4',                'self.Stamanho_Total_ErroGXY_SF', 'self.Stamanho_Total_ErroGXY_MIS', 'self.Stamanho_Total_ErroGXYZ_GD','self.Stamanho_Total_ErroGXYZ_RW','self.Stamanho_Total_ErroGXY_GD',               'self.Stamanho_Total_ErroGXY_RW' , 'self.Stamanho_Total_ErroGZ_GD ','self.Stamanho_Total_ErroGZ_RW ','self.Stamanho_Total_ErroXYM1',                'self.Stamanho_Total_ErroXYM2', 'self.Stamanho_Total_ErroXYM3', 'self.Stamanho_Total_ErroXYM4','self.Stamanho_Total_ErroVSAG',                'self.Stamanho_Total_ErroDRF_S','self.Stamanho_Total_ErroEXTREF', 'self.Stamanho_Total_ErroEXTTIE' , 'self.Stamanho_Total_ErroEXTMIS' , 'self.Gtamanho_Total_ErroDSF_W', 'self.Stamanho_Produto_ErroAXYZ_XYB','self.Stamanho_Produto_ErroAXY_B  ', 'self.Stamanho_Produto_ErroAXYZ_ZB' ,'self.Stamanho_Produto_ErroAXYZ_SF' , 'self.Stamanho_Produto_ErroAXYZ_MS','self.Stamanho_Produto_ErroAXY_SF ', 'self.Stamanho_Produto_ErroAXY_MS', 'self.Stamanho_Produto_ErroAXY_GB', 'self.Stamanho_Produto_ErroGXYZ_XYB1','self.Stamanho_Produto_ErroGXYZ_XYB2' ,'self.Stamanho_Produto_ErroGXYZ_XYG2' , 'self.Stamanho_Produto_ErroGXYZ_XYG3' ,'self.Stamanho_Produto_ErroGXYZ_ZG1 ' , 'self.Stamanho_Produto_ErroGXY_B1 ',  'self.Stamanho_Produto_ErroGXY_B2 ','self.Stamanho_Produto_ErroGXY_G2 ',               'self.Stamanho_Produto_ErroGXY_G3 ','self.Stamanho_Produto_ErroGXYZ_XYG1' , 'self.Stamanho_Produto_ErroGXYZ_XYG4' ,                  'self.Stamanho_Produto_ErroGXYZ_ZB  ' ,                  'self.Stamanho_Produto_ErroGXYZ_ZG2 ' ,'self.Stamanho_Produto_ErroGXYZ_SF', 'self.Stamanho_Produto_ErroGXYZ_MIS ' , 'self.Stamanho_Produto_ErroGXY_G1', 'self.Stamanho_Produto_ErroGXY_G4' , 'self.Stamanho_Produto_ErroGXY_SF' , 'self.Stamanho_Produto_ErroGXY_MIS','self.Stamanho_Produto_ErroGXYZ_GD', 'self.Stamanho_Produto_ErroGXYZ_RW', 'self.Stamanho_Produto_ErroGXY_GD ', 'self.Stamanho_Produto_ErroGXY_RW ', 'self.Stamanho_Produto_ErroGZ_GD  ','self.Stamanho_Produto_ErroGZ_RW  ','self.Stamanho_Produto_ErroXYM1  ', 'self.Stamanho_Produto_ErroXYM2 ' ,'self.Stamanho_Produto_ErroXYM3',
                'self.Stamanho_Produto_ErroXYM4'  , 'self.Stamanho_Produto_ErroVSAG' , 'self.Stamanho_Produto_ErroDRF_S' ,                'self.Stamanho_Produto_ErroEXTREF' ,                'self.Stamanho_Produto_ErroEXTTIE' , 'self.Stamanho_Produto_ErroEXTMIS'])
        
        writer = pd.ExcelWriter('Erro_Sistematico_GYRO.xlsx')
        
        df.to_excel(writer,'Erro GYRO',float_format='%.5f')
        
        writer.save()
        
    def ErroRandomicoGYRO_XYZ(self):
        
        for Estacao in range(0,len(self.dadosOriginaisGWD)):
            for coluna in range(0,1):
                for linha in range(0,3):
                    
                    self.RtamanhoErroAXYZ_XYB[Estacao][coluna][linha]  = self.Mag_AXYZ_XYB * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.AXYZ_XYB[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.AXYZ_XYB[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.AXYZ_XYB[Estacao][coluna + 2]))                     
                    
                    self.RtamanhoErroGXYZ_XYB1[Estacao][coluna][linha]  = self.Mag_GXYZ_XYB1 * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXYZ_XYB1[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXYZ_XYB1[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXYZ_XYB1[Estacao][coluna + 2]))                     
                    
                    self.RtamanhoErroGXYZ_XYB2[Estacao][coluna][linha]  = self.Mag_GXYZ_XYB2 * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXYZ_XYB2[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXYZ_XYB2[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXYZ_XYB2[Estacao][coluna + 2]))                     
                    
                    self.RtamanhoErroGXYZ_XYG2[Estacao][coluna][linha]  = self.Mag_GXYZ_XYG2 * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXYZ_XYG2[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXYZ_XYG2[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXYZ_XYG2[Estacao][coluna + 2]))                     
                    
                    self.RtamanhoErroGXYZ_XYG3[Estacao][coluna][linha]  = self.Mag_GXYZ_XYG3 * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXYZ_XYG3[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXYZ_XYG3[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXYZ_XYG3[Estacao][coluna + 2]))                     
                    
                    self.RtamanhoErroGXYZ_ZG1[Estacao][coluna][linha]  = self.Mag_GXYZ_ZG1 * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXYZ_ZG1[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXYZ_ZG1[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXYZ_ZG1[Estacao][coluna + 2]))                     
  
                    self.RtamanhoErroGXYZ_XYRN[Estacao][coluna][linha]  = self.Mag_GXYZ_XYRN * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXYZ_XYRN[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXYZ_XYRN[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXYZ_XYRN[Estacao][coluna + 2]))                     
                    
                    self.RtamanhoErroGXYZ_ZRN [Estacao][coluna][linha]  = self.Mag_GXYZ_ZRN * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXYZ_ZRN[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXYZ_ZRN[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXYZ_ZRN[Estacao][coluna + 2]))                     

                    self.RtamanhoErroDRF_R[Estacao][coluna][linha]  = self.Mag_DRF_R * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.DRF_R[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.DRF_R[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.DRF_R[Estacao][coluna + 2]))                     
    
        for Estacao in range(0,len(self.dadosOriginaisGWD)):
            for linha in range(0,3):
                for coluna in range(0,3):
                        
                    self.Rtamanho_Total_ErroAXYZ_XYB[Estacao][0][linha][coluna]  = self.RtamanhoErroAXYZ_XYB[Estacao][0][linha] * self.RtamanhoErroAXYZ_XYB[Estacao][0][coluna]
  
                    self.Rtamanho_Total_ErroGXYZ_XYB1[Estacao][0][linha][coluna] = self.RtamanhoErroGXYZ_XYB1[Estacao][0][linha] *  self.RtamanhoErroGXYZ_XYB1[Estacao][0][coluna]
                        
                    self.Rtamanho_Total_ErroGXYZ_XYB2[Estacao][0][linha][coluna] = self.RtamanhoErroGXYZ_XYB2[Estacao][0][linha]  * self.RtamanhoErroGXYZ_XYB2[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroGXYZ_XYG2[Estacao][0][linha][coluna] = self.RtamanhoErroGXYZ_XYG2[Estacao][0][linha]  * self.RtamanhoErroGXYZ_XYG2[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroGXYZ_XYG3[Estacao][0][linha][coluna] = self.RtamanhoErroGXYZ_XYG3[Estacao][0][linha]   * self.RtamanhoErroGXYZ_XYG3[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroGXYZ_ZG1[Estacao][0][linha][coluna]  = self.RtamanhoErroGXYZ_ZG1[Estacao][0][linha]  * self.RtamanhoErroGXYZ_ZG1[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroGXYZ_XYRN[Estacao][0][linha][coluna] =  self.RtamanhoErroGXYZ_XYRN[Estacao][0][linha] *  self.RtamanhoErroGXYZ_XYRN[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroGXYZ_ZRN [Estacao][0][linha][coluna] =  self.RtamanhoErroGXYZ_ZRN [Estacao][0][linha]  * self.RtamanhoErroGXYZ_ZRN [Estacao][0][coluna]

                    self.Rtamanho_Total_ErroDRF_R[Estacao][0][linha][coluna]     = self.RtamanhoErroDRF_R[Estacao][0][linha]  * self.RtamanhoErroDRF_R[Estacao][0][coluna]
        

        for Estacao in range(1,len(self.dadosOriginaisGWD)):
                        
            self.Rtamanho_Total_ErroAXYZ_XYB[Estacao]    = self.Rtamanho_Total_ErroAXYZ_XYB[Estacao]  + self.Rtamanho_Total_ErroAXYZ_XYB [Estacao - 1]
                        
            self.Rtamanho_Total_ErroGXYZ_XYB1[Estacao]   = self.Rtamanho_Total_ErroGXYZ_XYB1[Estacao] + self.Rtamanho_Total_ErroGXYZ_XYB1 [Estacao - 1]
            
            self.Rtamanho_Total_ErroGXYZ_XYB2[Estacao]   = self.Rtamanho_Total_ErroGXYZ_XYB2[Estacao] + self.Rtamanho_Total_ErroGXYZ_XYB2 [Estacao - 1]
            
            self.Rtamanho_Total_ErroGXYZ_XYG2[Estacao]   = self.Rtamanho_Total_ErroGXYZ_XYG2[Estacao] + self.Rtamanho_Total_ErroGXYZ_XYG2 [Estacao - 1]
            
            self.Rtamanho_Total_ErroGXYZ_XYG3[Estacao]   = self.Rtamanho_Total_ErroGXYZ_XYG3[Estacao] + self.Rtamanho_Total_ErroGXYZ_XYG3 [Estacao - 1]
            
            self.Rtamanho_Total_ErroGXYZ_ZG1[Estacao]    = self.Rtamanho_Total_ErroGXYZ_ZG1[Estacao]  + self.Rtamanho_Total_ErroGXYZ_ZG1 [Estacao - 1]
            
            self.Rtamanho_Total_ErroGXYZ_XYRN[Estacao]   = self.Rtamanho_Total_ErroGXYZ_XYRN[Estacao] + self.Rtamanho_Total_ErroGXYZ_XYRN [Estacao - 1]
            
            self.Rtamanho_Total_ErroGXYZ_ZRN [Estacao]   = self.Rtamanho_Total_ErroGXYZ_ZRN [Estacao] + self.Rtamanho_Total_ErroGXYZ_ZRN [Estacao - 1]

            self.Rtamanho_Total_ErroDRF_R[Estacao]       = self.Rtamanho_Total_ErroDRF_R[Estacao]     + self.Rtamanho_Total_ErroDRF_R [Estacao - 1]
            
            self.ErroRandomicoTotal_GYRO_XYZ[Estacao] =  self.Rtamanho_Total_ErroAXYZ_XYB[Estacao] + self.Rtamanho_Total_ErroGXYZ_XYB1[Estacao]  + self.Rtamanho_Total_ErroGXYZ_XYB2[Estacao] + self.Rtamanho_Total_ErroGXYZ_XYG2[Estacao] + self.Rtamanho_Total_ErroGXYZ_XYG3[Estacao] + self.Rtamanho_Total_ErroGXYZ_ZG1[Estacao] + self.Rtamanho_Total_ErroGXYZ_XYRN[Estacao] + self.Rtamanho_Total_ErroGXYZ_ZRN [Estacao] + self.Rtamanho_Total_ErroDRF_R[Estacao] 
        
        df = pd.DataFrame([[   self.StamanhoErroAXYZ_XYB   ,        self.StamanhoErroAXY_B      ,        self.RtamanhoErroAXYZ_XYB   ,         self.RtamanhoErroAXY_B      ,        self.StamanhoErroAXYZ_ZB    ,        self.StamanhoErroAXYZ_SF    ,        self.StamanhoErroAXYZ_MS    ,        self.StamanhoErroAXY_SF     ,        self.StamanhoErroAXY_MS     ,        self.StamanhoErroAXY_GB     ,        self.StamanhoErroGXYZ_XYB1  ,        self.StamanhoErroGXYZ_XYB2  ,        self.StamanhoErroGXYZ_XYG2  ,        self.StamanhoErroGXYZ_XYG3  ,        self.StamanhoErroGXYZ_ZG1   ,        self.StamanhoErroGXY_B1     ,        self.StamanhoErroGXY_B2     ,        self.StamanhoErroGXY_G2     ,        self.StamanhoErroGXY_G3     ,        self.RtamanhoErroGXYZ_XYB1  ,        self.RtamanhoErroGXYZ_XYB2  ,        self.RtamanhoErroGXYZ_XYG2 ,        self.RtamanhoErroGXYZ_XYG3  ,        self.RtamanhoErroGXYZ_ZG1   ,        self.RtamanhoErroGXY_B1     ,        self.RtamanhoErroGXY_B2     ,        self.RtamanhoErroGXY_G2     ,        self.RtamanhoErroGXY_G3     ,        self.RtamanhoErroGXYZ_XYRN  ,        self.RtamanhoErroGXYZ_ZRN   ,        self.RtamanhoErroGXY_RN     ,          self.RtamanhoErroDRF_R      ,        self.Rtamanho_Total_ErroAXYZ_XYB  , self.Rtamanho_Total_ErroAXY_B  ,               self.Rtamanho_Total_ErroGXYZ_XYB1   ,                self.Rtamanho_Total_ErroGXYZ_XYB2   , self.Rtamanho_Total_ErroGXYZ_XYG2 ,                self.Rtamanho_Total_ErroGXYZ_XYG3   ,                self.Rtamanho_Total_ErroGXYZ_ZG1   ,        self.Rtamanho_Total_ErroGXY_B1  ,               self.Rtamanho_Total_ErroGXY_B2 ,                self.Rtamanho_Total_ErroGXY_G2  ,                self.Rtamanho_Total_ErroGXY_G3  ,               self.Rtamanho_Total_ErroGXYZ_XYRN  ,                self.Rtamanho_Total_ErroGXYZ_ZRN   ,           self.Rtamanho_Total_ErroGXY_RN  ,        self.Rtamanho_Total_ErroDRF_R  ]], columns=[ 'self.StamanhoErroAXYZ_XYB'   ,         'self.StamanhoErroAXY_B'      ,
        'self.RtamanhoErroAXYZ_XYB   ',                 'self.RtamanhoErroAXY_B      ',        'self.StamanhoErroAXYZ_ZB    ',        'self.StamanhoErroAXYZ_SF    ',        'self.SamanhoErroAXYZ_MS    ',        'self.StamanhoErroAXY_SF     ',       'self.StamanhoErroAXY_MS     ',        'self.StamanhoErroAXY_GB     ',
        'self.StamanhoErroGXYZ_XYB1  ',        'self.StamanhoErroGXYZ_XYB2  ',        'self.StamanhoErroGXYZ_XYG2  ',        'self.StamanhoErroGXYZ_XYG3  ',
        'self.StamanhoErroGXYZ_ZG1   ',        'self.StamanhoErroGXY_B1     ',        'self.StamanhoErroGXY_B2     ',        'self.StamanhoErroGXY_G2     ',
        'self.StamanhoErroGXY_G3     ',        'self.RtamanhoErroGXYZ_XYB1  ',        'self.RtamanhoErroGXYZ_XYB2  ',        'self.RtamanhoErroGXYZ_XYG2  ',        'self.RtamanhoErroGXYZ_XYG3  ',        'self.RtamanhoErroGXYZ_ZG1   ',        'self.RtamanhoErroGXY_B1     ',        'self.RtamanhoErroGXY_B2     ',        'self.RtamanhoErroGXY_G2     ',        'self.RtamanhoErroGXY_G3     ',        'self.RtamanhoErroGXYZ_XYRN  ',        'self.RtamanhoErroGXYZ_ZRN   ',
        'self.RtamanhoErroGXY_RN     ',          'self.RtamanhoErroDRF_R      ',        'self.Rtamanho_Total_ErroAXYZ_XYB'  ,
        'self.Rtamanho_Total_ErroAXY_B  ',                'self.Rtamanho_Total_ErroGXYZ_XYB1'   ,                'self.Rtamanho_Total_ErroGXYZ_XYB2'   ,                'self.Rtamanho_Total_ErroGXYZ_XYG2' ,                'self.Rtamanho_Total_ErroGXYZ_XYG3'   ,                'self.Rtamanho_Total_ErroGXYZ_ZG1 '  ,        'self.Rtamanho_Total_ErroGXY_B1'  ,                'self.Rtamanho_Total_ErroGXY_B2' ,                'self.Rtamanho_Total_ErroGXY_G2 ' ,                'self.Rtamanho_Total_ErroGXY_G3  ',                'self.Rtamanho_Total_ErroGXYZ_XYRN'  ,                'self.Rtamanho_Total_ErroGXYZ_ZRN'   ,           'self.Rtamanho_Total_ErroGXY_RN'  ,        'self.Rtamanho_Total_ErroDRF_R'])
        
        writer = pd.ExcelWriter('Erro_Randomico_GYRO.xlsx')
        
        df.to_excel(writer,'Erro GYRO',float_format='%.5f')
        
        writer.save()
         
    def ErroSistematicoGYRO_XY(self):
        
        for Estacao in range(0,len(self.dadosOriginaisGWD)):
            for coluna in range(0,1):
                for linha in range(0,3):
                    
                    #Erro acelerometro
                    self.StamanhoErroAXYZ_XYB[Estacao][coluna][linha]  = self.Mag_AXYZ_XYB * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.AXYZ_XYB[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.AXYZ_XYB[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.AXYZ_XYB[Estacao][coluna + 2]))
                     
                    #Erro acelerometro
                    self.StamanhoErroAXYZ_ZB[Estacao][coluna][linha]  = self.Mag_AXYZ_ZB  * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.AXYZ_ZB[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.AXYZ_ZB[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.AXYZ_ZB[Estacao][coluna + 2]))
                     
                    #Erro acelerometro
                    self.StamanhoErroAXYZ_SF     [Estacao][coluna][linha]  = self.Mag_AXYZ_SF  * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.AXYZ_SF [Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.AXYZ_SF [Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.AXYZ_SF [Estacao][coluna + 2]))
                    
                    #Erro acelerometro
                    self.StamanhoErroAXYZ_MS     [Estacao][coluna][linha]  = self.Mag_AXYZ_MS * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.AXYZ_MS[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.AXYZ_MS[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.AXYZ_MS[Estacao][coluna + 2]))                    
                    
                    #Erro acelerometro
                    self.StamanhoErroAXY_B  [Estacao][coluna][linha]  = self.Mag_AXY_B * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.AXY_B[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.AXY_B[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.AXY_B[Estacao][coluna + 2]))                    

                    #Erro acelerometro
                    self.StamanhoErroAXY_SF [Estacao][coluna][linha]  = self.Mag_AXY_SF  * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.AXY_SF [Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.AXY_SF [Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.AXY_SF [Estacao][coluna + 2]))                    
                    
                    #Erro acelerometro
                    self.StamanhoErroAXY_MS[Estacao][coluna][linha]  = self.Mag_AXY_MS * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.AXY_MS[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.AXY_MS[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.AXY_MS[Estacao][coluna + 2]))                    
                    
                    #Erro acelerometro
                    self.StamanhoErroAXY_GB[Estacao][coluna][linha]  = self.Mag_AXY_GB  * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.AXY_GB [Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.AXY_GB [Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.AXY_GB [Estacao][coluna + 2]))                    
                   
                    #Erro Gyro XY
                    self.StamanhoErroGXY_B1 [Estacao][coluna][linha]  = self.Mag_GXY_B1  * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXY_B1 [Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXY_B1 [Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXY_B1 [Estacao][coluna + 2]))                    
                    
                    #Erro Gyro XY
                    self.StamanhoErroGXY_B2 [Estacao][coluna][linha]  = self.Mag_GXY_B2 * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXY_B2[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXY_B2[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXY_B2[Estacao][coluna + 2]))                    
                    
                    #Erro Gyro XY
                    self.StamanhoErroGXY_G2 [Estacao][coluna][linha]  = self.Mag_GXY_G2 * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXY_G2[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXY_G2[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXY_G2[Estacao][coluna + 2]))                    
                    
                    #Erro Gyro XY
                    self.StamanhoErroGXY_G3 [Estacao][coluna][linha]  = self.Mag_GXY_G3  * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXY_G3  [Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXY_G3  [Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXY_G3  [Estacao][coluna + 2]))                    
                    
                    #Erro Gyro XY
                    self.StamanhoErroGXY_G1 [Estacao][coluna][linha]  = self.Mag_GXY_G1 * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXY_G1[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXY_G1[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXY_G1[Estacao][coluna + 2]))                    
                    
                    #Erro Gyro XY
                    self.StamanhoErroGXY_G4 [Estacao][coluna][linha]  = self.Mag_GXY_G4 * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXY_G4[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXY_G4[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXY_G4[Estacao][coluna + 2]))                    
                    
                    #Erro Gyro XY
                    self.StamanhoErroGXY_SF [Estacao][coluna][linha]  = self.Mag_GXY_SF * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXY_SF[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXY_SF[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXY_SF[Estacao][coluna + 2]))                    
                  
                    #Erro Gyro XY
                    self.StamanhoErroGXY_MIS     [Estacao][coluna][linha]  = self.Mag_GXY_MIS * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXY_MIS[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXY_MIS[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXY_MIS[Estacao][coluna + 2]))                    
                    
                    #Erro Gyro XY
                    self.StamanhoErroGXY_GD [Estacao][coluna][linha]  = self.Mag_GXY_GD * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXY_GD[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXY_GD[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXY_GD[Estacao][coluna + 2]))                    
                 
                    #Erro Gyro XY
                    self.StamanhoErroGXY_RW [Estacao][coluna][linha]  = self.Mag_GXY_RW * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXY_RW[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXY_RW[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXY_RW[Estacao][coluna + 2]))                    
                  
                    #Erro desalinhamento
                    self.StamanhoErroXYM1_GYRO   [Estacao][coluna][linha]  = self.Mag_XYM1_GYRO * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.XYM1_GYRO[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.XYM1_GYRO[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.XYM1_GYRO[Estacao][coluna + 2]))                    
                 
                    #Erro desalinhamento
                    self.StamanhoErroXYM2_GYRO   [Estacao][coluna][linha]  = self.Mag_XYM2_GYRO * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.XYM2_GYRO[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.XYM2_GYRO[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.XYM2_GYRO[Estacao][coluna + 2]))                    
                 
                    #Erro desalinhamento
                    self.StamanhoErroXYM3_GYRO   [Estacao][coluna][linha]  = self.Mag_XYM3_GYRO * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.XYM3_GYRO[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.XYM3_GYRO[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.XYM3_GYRO[Estacao][coluna + 2]))                    
                
                    #Erro desalinhamento
                    self.StamanhoErroXYM4_GYRO   [Estacao][coluna][linha]  = self.Mag_XYM4_GYRO * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.XYM4_GYRO[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.XYM4_GYRO[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.XYM4_GYRO[Estacao][coluna + 2]))                    
                 
                    #Erro vertical SAG
                    self.StamanhoErroVSAG   [Estacao][coluna][linha]  = self.Mag_VSAG * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.VSAG[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.VSAG[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.VSAG[Estacao][coluna + 2]))                    
                  
                    #Erro profundidade
                    self.StamanhoErroDRF_S [Estacao][coluna][linha]  = self.Mag_DRF_S * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.DRF_S[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.DRF_S[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.DRF_S[Estacao][coluna + 2]))
                    
                    #Erro Externo
                    self.StamanhoErroEXTREF [Estacao][coluna][linha]  = self.Mag_EXTREF * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.EXTREF[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.EXTREF[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.EXTREF[Estacao][coluna + 2]))                    
                  
                    #Erro Externo
                    self.StamanhoErroEXTTIE[Estacao][coluna][linha]  = self.Mag_EXTTIE * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.EXTTIE[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.EXTTIE[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.EXTTIE[Estacao][coluna + 2]))                    
                  
                    #Erro Externo
                    self.StamanhoErroEXTMIS[Estacao][coluna][linha]  = self.Mag_EXTMIS * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.EXTMIS[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.EXTMIS[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.EXTMIS[Estacao][coluna + 2]))                    
      
                    self.GtamanhoErroDSF_W[Estacao][coluna][linha]  = self.Mag_DSF_W * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.DSF_W[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.DSF_W[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.DSF_W[Estacao][coluna + 2]))
                    
        for Estacao in range(1,len(self.dadosOriginaisGWD)):
           #Erro acelerometro
            self.Stamanho_Total_ErroAXYZ_XYB [Estacao]  =         self.Stamanho_Total_ErroAXYZ_XYB [Estacao - 1] +         self.StamanhoErroAXYZ_XYB [Estacao]
            #Erro acelerometro
            self.Stamanho_Total_ErroAXYZ_ZB [Estacao]    =         self.Stamanho_Total_ErroAXYZ_ZB [Estacao - 1]   +         self.StamanhoErroAXYZ_ZB [Estacao]
            
            #Erro acelerometro
            self.Stamanho_Total_ErroAXYZ_SF [Estacao]   =         self.Stamanho_Total_ErroAXYZ_SF [Estacao - 1]  +         self.StamanhoErroAXYZ_SF [Estacao]   
            
            #Erro acelerometro
            self.Stamanho_Total_ErroAXYZ_MS [Estacao]   =         self.Stamanho_Total_ErroAXYZ_MS [Estacao - 1]  +         self.StamanhoErroAXYZ_MS [Estacao]
            #Erro acelerometro
            self.Stamanho_Total_ErroAXY_B [Estacao]     =         self.Stamanho_Total_ErroAXY_B [Estacao - 1]    +         self.StamanhoErroAXY_B [Estacao]
            
            #Erro Gyro XY
            self.Stamanho_Total_ErroGXY_B1 [Estacao]    =         self.Stamanho_Total_ErroGXY_B1 [Estacao - 1]    +         self.StamanhoErroGXY_B1 [Estacao]
            
            #Erro Gyro XY
            self.Stamanho_Total_ErroGXY_B2 [Estacao]    =         self.Stamanho_Total_ErroGXY_B2 [Estacao - 1]    +         self.StamanhoErroGXY_B2 [Estacao]
            
            #Erro Gyro XY
            self.Stamanho_Total_ErroGXY_G2 [Estacao]    =         self.Stamanho_Total_ErroGXY_G2 [Estacao - 1]    +         self.StamanhoErroGXY_G2 [Estacao]
            
            #Erro Gyro XY
            self.Stamanho_Total_ErroGXY_G3 [Estacao]    =         self.Stamanho_Total_ErroGXY_G3 [Estacao - 1]    +         self.StamanhoErroGXY_G3 [Estacao]
            
            #Erro Gyro XY
            self.Stamanho_Total_ErroGXY_G1 [Estacao]    =         self.Stamanho_Total_ErroGXY_G1 [Estacao - 1]    +         self.StamanhoErroGXY_G1 [Estacao]
            
            #Erro Gyro XY
            self.Stamanho_Total_ErroGXY_G4 [Estacao]    =         self.Stamanho_Total_ErroGXY_G4 [Estacao - 1]    +         self.StamanhoErroGXY_G4 [Estacao]
            
            #Erro Gyro XY
            self.Stamanho_Total_ErroGXY_SF [Estacao]    =         self.Stamanho_Total_ErroGXY_SF [Estacao - 1]    +         self.StamanhoErroGXY_SF [Estacao]
          
            #Erro Gyro XY
            self.Stamanho_Total_ErroGXY_MIS [Estacao]   =         self.Stamanho_Total_ErroGXY_MIS [Estacao - 1]   +         self.StamanhoErroGXY_MIS     [Estacao]

            #Erro Gyro XY
            self.Stamanho_Total_ErroGXY_GD [Estacao]    =         self.Stamanho_Total_ErroGXY_GD [Estacao - 1]    +         self.StamanhoErroGXY_GD [Estacao]
         
            #Erro Gyro XY
            self.Stamanho_Total_ErroGXY_RW [Estacao]    =         self.Stamanho_Total_ErroGXY_RW [Estacao - 1]    +         self.StamanhoErroGXY_RW [Estacao]
          
            #Erro desalinhamento
            self.Stamanho_Total_ErroXYM1_GYRO   [Estacao]    =         self.Stamanho_Total_ErroXYM1_GYRO   [Estacao - 1]    +         self.StamanhoErroXYM1_GYRO   [Estacao]
         
            #Erro desalinhamento
            self.Stamanho_Total_ErroXYM2_GYRO   [Estacao]    =         self.Stamanho_Total_ErroXYM2_GYRO   [Estacao - 1]    +         self.StamanhoErroXYM2_GYRO   [Estacao]
         
            #Erro desalinhamento
            self.Stamanho_Total_ErroXYM3_GYRO   [Estacao]    =         self.Stamanho_Total_ErroXYM3_GYRO   [Estacao - 1]    +         self.StamanhoErroXYM3_GYRO   [Estacao]
        
            #Erro desalinhamento
            self.Stamanho_Total_ErroXYM4_GYRO   [Estacao]    =         self.Stamanho_Total_ErroXYM4_GYRO   [Estacao - 1]    +         self.StamanhoErroXYM4_GYRO   [Estacao]
         
            #Erro vertical SAG
            self.Stamanho_Total_ErroVSAG [Estacao]      =         self.Stamanho_Total_ErroVSAG [Estacao - 1]      +         self.StamanhoErroVSAG [Estacao]
          
            #Erro profundidade
            self.Stamanho_Total_ErroDRF_S [Estacao]     =         self.Stamanho_Total_ErroDRF_S [Estacao - 1]     +         self.StamanhoErroDRF_S [Estacao]
            
            #Erro Externo
            self.Stamanho_Total_ErroEXTREF [Estacao]    =         self.Stamanho_Total_ErroEXTREF [Estacao - 1]    +         self.StamanhoErroEXTREF [Estacao]
          
            #Erro Externo
            self.Stamanho_Total_ErroEXTTIE [Estacao]     =         self.Stamanho_Total_ErroEXTTIE[Estacao - 1]     +         self.StamanhoErroEXTTIE [Estacao]
          
            #Erro Externo
            self.Stamanho_Total_ErroEXTMIS [Estacao]     =         self.Stamanho_Total_ErroEXTMIS [Estacao - 1]     +         self.StamanhoErroEXTMIS [Estacao]
      
            self.Gtamanho_Total_ErroDSF_W [Estacao]      =         self.Gtamanho_Total_ErroDSF_W [Estacao - 1]      +         self.GtamanhoErroDSF_W [Estacao]

        for Estacao in range(0,len(self.dadosOriginaisGWD)):
            for linha in range(0,3):
                for coluna in range(0,3):
        
                    #Erro acelerometro
                    self.Stamanho_Produto_ErroAXYZ_XYB [Estacao][0][linha][coluna]  = self.Stamanho_Total_ErroAXYZ_XYB [Estacao][0][linha] * self.Stamanho_Total_ErroAXYZ_XYB [Estacao][0][coluna]
                    
                    #Erro acelerometro
                    self.Stamanho_Produto_ErroAXYZ_ZB [Estacao]    = self.Stamanho_Total_ErroAXYZ_ZB [Estacao][0][linha]  * self.Stamanho_Total_ErroAXYZ_ZB[Estacao][0][coluna]   
                    
                    #Erro acelerometro
                    self.Stamanho_Produto_ErroAXYZ_SF [Estacao][0][linha][coluna]   = self.Stamanho_Total_ErroAXYZ_SF [Estacao][0][linha] * self.Stamanho_Total_ErroAXYZ_SF [Estacao][0][coluna]   
                    
                    #Erro acelerometro
                    self.Stamanho_Produto_ErroAXYZ_MS [Estacao][0][linha][coluna]   = self.Stamanho_Total_ErroAXYZ_MS [Estacao][0][linha] * self.Stamanho_Total_ErroAXYZ_MS [Estacao][0][coluna]
                    
                    #Erro acelerometro
                    self.Stamanho_Produto_ErroAXY_B [Estacao][0][linha][coluna]     = self.Stamanho_Total_ErroAXY_B [Estacao][0][linha] * self.Stamanho_Total_ErroAXY_B [Estacao][0][coluna]
                    
                    #Erro acelerometro
                    self.Stamanho_Produto_ErroAXY_SF [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroAXY_SF [Estacao][0][linha] * self.Stamanho_Total_ErroAXY_SF [Estacao][0][coluna]
                    
                    #Erro acelerometro
                    self.Stamanho_Produto_ErroAXY_MS [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroAXY_MS [Estacao][0][linha] * self.Stamanho_Total_ErroAXY_MS [Estacao][0][coluna]
                    
                    #Erro acelerometro
                    self.Stamanho_Produto_ErroAXY_GB [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroAXY_GB [Estacao][0][linha] * self.Stamanho_Total_ErroAXY_GB [Estacao][0][coluna]
                   
                    #Erro Gyro XY
                    self.Stamanho_Produto_ErroGXY_B1 [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroGXY_B1 [Estacao][0][linha] * self.Stamanho_Total_ErroGXY_B1 [Estacao][0][coluna]
                    
                    #Erro Gyro XY
                    self.Stamanho_Produto_ErroGXY_B2 [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroGXY_B2 [Estacao][0][linha] * self.Stamanho_Total_ErroGXY_B2 [Estacao][0][coluna]
                    
                    #Erro Gyro XY
                    self.Stamanho_Produto_ErroGXY_G2 [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroGXY_G2 [Estacao][0][linha] * self.Stamanho_Total_ErroGXY_G2 [Estacao][0][coluna]
                    
                    #Erro Gyro XY
                    self.Stamanho_Produto_ErroGXY_G3 [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroGXY_G3 [Estacao][0][linha] * self.Stamanho_Total_ErroGXY_G3 [Estacao][0][coluna] 
                      
                    #Erro Gyro XY
                    self.Stamanho_Produto_ErroGXY_G1 [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroGXY_G1 [Estacao][0][linha] * self.Stamanho_Total_ErroGXY_G1 [Estacao][0][coluna]
                    
                    #Erro Gyro XY
                    self.Stamanho_Produto_ErroGXY_G4 [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroGXY_G4 [Estacao][0][linha] * self.Stamanho_Total_ErroGXY_G4 [Estacao][0][coluna]
                    
                    #Erro Gyro XY
                    self.Stamanho_Produto_ErroGXY_SF [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroGXY_G4 [Estacao][0][linha] * self.Stamanho_Total_ErroGXY_G4 [Estacao][0][coluna]
                  
                    #Erro Gyro XY
                    self.Stamanho_Produto_ErroGXY_MIS [Estacao][0][linha][coluna]   = self.Stamanho_Total_ErroGXY_MIS [Estacao][0][linha] * self.Stamanho_Total_ErroGXY_MIS [Estacao][0][coluna]
                    
                    #Erro Gyro XY
                    self.Stamanho_Produto_ErroGXY_GD [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroGXY_GD [Estacao][0][linha] * self.Stamanho_Total_ErroGXY_GD [Estacao][0][coluna]
                 
                    #Erro Gyro XY
                    self.Stamanho_Produto_ErroGXY_RW [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroGXY_RW [Estacao][0][linha] * self.Stamanho_Total_ErroGXY_RW [Estacao][0][coluna]
                  
                    #Erro desalinhamento
                    self.Stamanho_Produto_ErroXYM1_GYRO   [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroXYM1_GYRO [Estacao][0][linha] * self.Stamanho_Total_ErroXYM1_GYRO   [Estacao][0][coluna]
                 
                    #Erro desalinhamento
                    self.Stamanho_Produto_ErroXYM2_GYRO   [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroXYM2_GYRO [Estacao][0][linha] * self.Stamanho_Total_ErroXYM2_GYRO   [Estacao][0][coluna]
                 
                    #Erro desalinhamento
                    self.Stamanho_Produto_ErroXYM3_GYRO   [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroXYM3_GYRO [Estacao][0][linha] * self.Stamanho_Total_ErroXYM3_GYRO   [Estacao][0][coluna]
                
                    #Erro desalinhamento
                    self.Stamanho_Produto_ErroXYM4_GYRO   [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroXYM4_GYRO [Estacao][0][linha] * self.Stamanho_Total_ErroXYM4_GYRO   [Estacao][0][coluna]
                 
                    #Erro vertical SAG
                    self.Stamanho_Produto_ErroVSAG [Estacao][0][linha][coluna]      = self.Stamanho_Total_ErroVSAG [Estacao][0][linha]  * self.Stamanho_Total_ErroVSAG [Estacao][0][coluna]
                  
                    #Erro profundidade
                    self.Stamanho_Produto_ErroDRF_S [Estacao][0][linha][coluna]     = self.Stamanho_Total_ErroDRF_S [Estacao][0][linha]  * self.Stamanho_Total_ErroDRF_S [Estacao][0][coluna]
                    
                    #Erro Externo
                    self.Stamanho_Produto_ErroEXTREF [Estacao][0][linha][coluna]    = self.Stamanho_Total_ErroEXTREF [Estacao][0][linha] * self.Stamanho_Total_ErroDRF_S [Estacao][0][coluna]
                  
                    #Erro Externo
                    self.Stamanho_Produto_ErroEXTTIE[Estacao][0][linha][coluna]     = self.Stamanho_Total_ErroEXTTIE [Estacao][0][linha] * self.Stamanho_Total_ErroEXTTIE[Estacao][0][coluna]
                  
                    #Erro Externo
                    self.Stamanho_Produto_ErroEXTMIS[Estacao][0][linha][coluna]     = self.Stamanho_Total_ErroEXTMIS [Estacao][0][linha] * self.Stamanho_Total_ErroEXTMIS[Estacao][0][coluna]
              
                    self.Gtamanho_Produto_ErroDSF_W[Estacao][0][linha][coluna]      = self.Gtamanho_Total_ErroDSF_W [Estacao][0][linha]  * self.Gtamanho_Total_ErroDSF_W[Estacao][0][coluna]
                                      
            self.ErroSistematicoTotal_GYRO_XY[Estacao] = self.Stamanho_Produto_ErroAXYZ_XYB [Estacao] + self.Stamanho_Produto_ErroAXYZ_ZB [Estacao] + self.Stamanho_Produto_ErroAXYZ_SF[Estacao] + self.Stamanho_Produto_ErroAXYZ_MS[Estacao] + self.Stamanho_Produto_ErroGXY_B1 [Estacao] + self.Stamanho_Produto_ErroGXY_B2 [Estacao]  + self.Stamanho_Produto_ErroGXY_G1 [Estacao] + self.Stamanho_Produto_ErroGXY_G4 [Estacao] + self.Stamanho_Produto_ErroXYM1_GYRO   [Estacao] + self.Stamanho_Produto_ErroXYM2_GYRO   [Estacao] + self.Stamanho_Produto_ErroXYM3_GYRO [Estacao] + self.Stamanho_Produto_ErroXYM4_GYRO   [Estacao] + self.Stamanho_Produto_ErroVSAG [Estacao] + self.Stamanho_Produto_ErroDRF_S [Estacao] # + self.Stamanho_Produto_ErroAXY_B [Estacao] + self.Stamanho_Produto_ErroAXY_SF [Estacao] + self.Stamanho_Produto_ErroAXY_MS [Estacao]+  self.Stamanho_Produto_ErroAXY_GB [Estacao] + self.Stamanho_Produto_ErroGXY_RW [Estacao]   + self.Stamanho_Produto_ErroGXY_MIS [Estacao] + self.Stamanho_Produto_ErroGXY_SF [Estacao] + self.Stamanho_Produto_ErroGXY_G3 [Estacao]  + self.Stamanho_Produto_ErroGXY_G2 [Estacao] + self.Stamanho_Produto_ErroEXTREF [Estacao] + self.Stamanho_Produto_ErroEXTTIE[Estacao] + self.Stamanho_Produto_ErroEXTMIS[Estacao] + self.Gtamanho_Produto_ErroDSF_W[Estacao]  + self.Stamanho_Produto_ErroGXY_GD [Estacao] 
            
        
        df = pd.DataFrame([[self.StamanhoErroAXYZ_XYB, self.StamanhoErroAXY_B, self.StamanhoErroGXYZ_XYB1, self.StamanhoErroGXYZ_XYB2, self.StamanhoErroGXYZ_XYG2  , self.StamanhoErroGXYZ_XYG3  , self.StamanhoErroGXYZ_ZG1, self.StamanhoErroGXY_B1, self.StamanhoErroGXY_B2,  self.StamanhoErroGXY_G2     , self.StamanhoErroGXY_G3, self.StamanhoErroGXYZ_XYG1  , self.StamanhoErroGXYZ_XYG4  , self.StamanhoErroGXYZ_ZB, self.StamanhoErroGXYZ_ZG2, self.StamanhoErroGXYZ_SF    , self.StamanhoErroGXYZ_MIS   , self.StamanhoErroGXY_G1     , self.StamanhoErroGXY_G4, self.StamanhoErroGXY_SF,  self.StamanhoErroGXY_MIS,  self.StamanhoErroEXTREF     , self.StamanhoErroEXTTIE     , self.StamanhoErroEXTMIS, self.StamanhoErroGXYZ_GD    , self.StamanhoErroGXYZ_RW,  self.StamanhoErroGXY_GD, self.StamanhoErroGXY_RW     , self.StamanhoErroGZ_GD, self.StamanhoErroGZ_RW, self.StamanhoErroXYM1_GYRO, self.StamanhoErroXYM2_GYRO , self.StamanhoErroXYM3_GYRO, self.StamanhoErroXYM4_GYRO, self.StamanhoErroVSAG       , self.StamanhoErroDRF_S, self.Stamanho_Total_ErroAXYZ_XYB  , self.Stamanho_Total_ErroAXY_B  ,  self.Stamanho_Total_ErroAXYZ_ZB  , self.Stamanho_Total_ErroAXYZ_SF   , self.Stamanho_Total_ErroAXYZ_MS  , self.Stamanho_Total_ErroAXY_SF  ,self.Stamanho_Total_ErroAXY_MS  ,  self.Stamanho_Total_ErroAXY_GB , self.Stamanho_Total_ErroGXYZ_XYB1 ,                self.Stamanho_Total_ErroGXYZ_XYB2, self.Stamanho_Total_ErroGXYZ_XYG2,  self.Stamanho_Total_ErroGXYZ_XYG3, self.Stamanho_Total_ErroGXYZ_ZG1, self.Stamanho_Total_ErroGXY_B1, self.Stamanho_Total_ErroGXY_B2, self.Stamanho_Total_ErroGXY_G2, self.Stamanho_Total_ErroGXY_G3, self.Stamanho_Total_ErroGXYZ_XYG1, self.Stamanho_Total_ErroGXYZ_XYG4, self.Stamanho_Total_ErroGXYZ_ZB,self.Stamanho_Total_ErroGXYZ_ZG2, self.Stamanho_Total_ErroGXYZ_SF, self.Stamanho_Total_ErroGXYZ_MIS, self.Stamanho_Total_ErroGXY_G1,  self.Stamanho_Total_ErroGXY_G4, self.Stamanho_Total_ErroGXY_SF,self.Stamanho_Total_ErroGXY_MIS, self.Stamanho_Total_ErroGXYZ_GD, self.Stamanho_Total_ErroGXYZ_RW,                self.Stamanho_Total_ErroGXY_GD, self.Stamanho_Total_ErroGXY_RW , self.Stamanho_Total_ErroGZ_GD , self.Stamanho_Total_ErroGZ_RW , self.Stamanho_Total_ErroXYM1_GYRO, self.Stamanho_Total_ErroXYM2_GYRO, self.Stamanho_Total_ErroXYM3_GYRO, self.Stamanho_Total_ErroXYM4_GYRO, self.Stamanho_Total_ErroVSAG, self.Stamanho_Total_ErroDRF_S, self.Stamanho_Total_ErroEXTREF, self.Stamanho_Total_ErroEXTTIE , self.Stamanho_Total_ErroEXTMIS , self.Gtamanho_Total_ErroDSF_W, self.Stamanho_Produto_ErroAXYZ_XYB, self.Stamanho_Produto_ErroAXY_B  , self.Stamanho_Produto_ErroAXYZ_ZB , self.Stamanho_Produto_ErroAXYZ_SF , self.Stamanho_Produto_ErroAXYZ_MS, self.Stamanho_Produto_ErroAXY_SF , self.Stamanho_Produto_ErroAXY_MS, self.Stamanho_Produto_ErroAXY_GB, self.Stamanho_Produto_ErroGXYZ_XYB1, self.Stamanho_Produto_ErroGXYZ_XYB2 , self.Stamanho_Produto_ErroGXYZ_XYG2 , self.Stamanho_Produto_ErroGXYZ_XYG3 , self.Stamanho_Produto_ErroGXYZ_ZG1  , self.Stamanho_Produto_ErroGXY_B1 , self.Stamanho_Produto_ErroGXY_B2 , self.Stamanho_Produto_ErroGXY_G2 , self.Stamanho_Produto_ErroGXY_G3 , self.Stamanho_Produto_ErroGXYZ_XYG1 , self.Stamanho_Produto_ErroGXYZ_XYG4 ,  self.Stamanho_Produto_ErroGXYZ_ZB   , self.Stamanho_Produto_ErroGXYZ_ZG2  , self.Stamanho_Produto_ErroGXYZ_SF, self.Stamanho_Produto_ErroGXYZ_MIS  , self.Stamanho_Produto_ErroGXY_G1, self.Stamanho_Produto_ErroGXY_G4 , self.Stamanho_Produto_ErroGXY_SF , self.Stamanho_Produto_ErroGXY_MIS, self.Stamanho_Produto_ErroGXYZ_GD, self.Stamanho_Produto_ErroGXYZ_RW, self.Stamanho_Produto_ErroGXY_GD , self.Stamanho_Produto_ErroGXY_RW , self.Stamanho_Produto_ErroGZ_GD  , self.Stamanho_Produto_ErroGZ_RW  ,self.Stamanho_Produto_ErroXYM1_GYRO  , self.Stamanho_Produto_ErroXYM2_GYRO  , self.Stamanho_Produto_ErroXYM3_GYRO,  self.Stamanho_Produto_ErroXYM4_GYRO  ,  self.Stamanho_Produto_ErroVSAG , self.Stamanho_Produto_ErroDRF_S ,               self.Stamanho_Produto_ErroEXTREF , self.Stamanho_Produto_ErroEXTTIE , self.Stamanho_Produto_ErroEXTMIS ]], columns=['self.StamanhoErroAXYZ_XYB   ', 'self.StamanhoErroAXY_B      ', 'self.StamanhoErroGXYZ_XYB1  ', 'self.StamanhoErroGXYZ_XYB2  ', 'self.StamanhoErroGXYZ_XYG2 ', 'self.StamanhoErroGXYZ_XYG3 ', 'self.StamanhoErroGXYZ_ZG1   ', 'self.StamanhoErroGXY_B1    ', 'self.StamanhoErroGXY_B2     ', 'self.StamanhoErroGXY_G2    ','self.StamanhoErroGXY_G3     ', 'self.StamanhoErroGXYZ_XYG1  ', 'self.StamanhoErroGXYZ_XYG4 ',                'self.StamanhoErroGXYZ_ZB    ', 'self.StamanhoErroGXYZ_ZG2  ','self.StamanhoErroGXYZ_SF    ', 'self.StamanhoErroGXYZ_MIS   ', 'self.StamanhoErroGXY_G1    ', 'self.StamanhoErroGXY_G4     ','self.StamanhoErroGXY_SF     ', 'self.StamanhoErroGXY_MIS   ', 'self.StamanhoErroEXTREF     ', 'self.StamanhoErroEXTTIE    ', 'self.StamanhoErroEXTMIS     ','self.StamanhoErroGXYZ_GD    ', 'self.StamanhoErroGXYZ_RW   ', 'self.StamanhoErroGXY_GD     ', 'self.StamanhoErroGXY_RW    ', 'self.StamanhoErroGZ_GD      ',  'self.StamanhoErroGZ_RW    ', 'self.StamanhoErroXYM1      ', 'self.StamanhoErroXYM2       ', 'self.StamanhoErroXYM3      ', 'self.StamanhoErroXYM4       ', 'self.StamanhoErroVSAG      ', 'self.StamanhoErroDRF_S     ', 'self.Stamanho_Total_ErroAXYZ_XYB  ', 'self.Stamanho_Total_ErroAXY_B  ',                'self.Stamanho_Total_ErroAXYZ_ZB', 'self.Stamanho_Total_ErroAXYZ_SF', 'self.Stamanho_Total_ErroAXYZ_MS'  , 'self.Stamanho_Total_ErroAXY_SF ' , 'self.Stamanho_Total_ErroAXY_MS', 'self.Stamanho_Total_ErroAXY_GB ','self.Stamanho_Total_ErroGXYZ_XYB1' , 'self.Stamanho_Total_ErroGXYZ_XYB2', 'self.Stamanho_Total_ErroGXYZ_XYG2','self.Stamanho_Total_ErroGXYZ_XYG3', 'self.Stamanho_Total_ErroGXYZ_ZG1', 'self.Stamanho_Total_ErroGXY_B1','self.Stamanho_Total_ErroGXY_B2', 'self.Stamanho_Total_ErroGXY_G2 ','self.Stamanho_Total_ErroGXY_G3','self.Stamanho_Total_ErroGXYZ_XYG1','self.Stamanho_Total_ErroGXYZ_XYG4', 'self.Stamanho_Total_ErroGXYZ_ZB','self.Stamanho_Total_ErroGXYZ_ZG2','self.Stamanho_Total_ErroGXYZ_SF','self.Stamanho_Total_ErroGXYZ_MIS','self.Stamanho_Total_ErroGXY_G1','self.Stamanho_Total_ErroGXY_G4', 'self.Stamanho_Total_ErroGXY_SF', 'self.Stamanho_Total_ErroGXY_MIS', 'self.Stamanho_Total_ErroGXYZ_GD','self.Stamanho_Total_ErroGXYZ_RW','self.Stamanho_Total_ErroGXY_GD', 'self.Stamanho_Total_ErroGXY_RW' , 'self.Stamanho_Total_ErroGZ_GD ', 'self.Stamanho_Total_ErroGZ_RW ', 'self.Stamanho_Total_ErroXYM1'     ,'self.Stamanho_Total_rroXYM2', 'self.Stamanho_Total_ErroXYM3', 'self.Stamanho_Total_ErroXYM4', 'self.Stamanho_Total_ErroVSAG',  'self.Stamanho_Total_ErroDRF_S', 'self.Stamanho_Total_ErroEXTREF','self.Stamanho_Total_ErroEXTTIE' , 'self.Stamanho_Total_ErroEXTMIS','self.Gtamanho_Total_ErroDSF_W', 'self.Stamanho_Produto_ErroAXYZ_XYB', 'self.Stamanho_Produto_ErroAXY_B  ', 'self.Stamanho_Produto_ErroAXYZ_ZB','self.Stamanho_Produto_ErroAXYZ_SF' , 'self.Stamanho_Produto_ErroAXYZ_MS',  'self.Stamanho_Produto_ErroAXY_SF ', 'self.Stamanho_Produto_ErroAXY_MS', 'self.Stamanho_Produto_ErroAXY_GB', 'self.Stamanho_Produto_ErroGXYZ_XYB1','self.Stamanho_Produto_ErroGXYZ_XYB2' , 'self.Stamanho_Produto_ErroGXYZ_XYG2' , 'self.Stamanho_Produto_ErroGXYZ_XYG3' , 'self.Stamanho_Produto_ErroGXYZ_ZG1 ', 'self.Stamanho_Produto_ErroGXY_B1 ', 'self.Stamanho_Produto_ErroGXY_B2 ', 'self.Stamanho_Produto_ErroGXY_G2 ', 'self.Stamanho_Produto_ErroGXY_G3 ', 'self.Stamanho_Produto_ErroGXYZ_XYG1' , 'self.Stamanho_Produto_ErroGXYZ_XYG4' ,  'self.Stamanho_Produto_ErroGXYZ_ZB  ' , 'self.Stamanho_Produto_ErroGXYZ_ZG2 ' , 'self.Stamanho_Produto_ErroGXYZ_SF',                'self.Stamanho_Produto_ErroGXYZ_MIS ' , 'self.Stamanho_Produto_ErroGXY_G1', 'self.Stamanho_Produto_ErroXY_G4' ,'self.Stamanho_Produto_ErroGXY_SF', 'self.Stamanho_Produto_ErroGXY_MIS', 'self.Stamanho_Produto_ErroGXYZ_GD', 'self.Stamanho_Produto_ErroGXYZ_RW', 'self.Stamanho_Produto_ErroGXY_GD', 'self.Stamanho_Produto_ErroGXY_RW ', 'self.Stamanho_Produto_ErroGZ_GD  ', 'self.Stamanho_Produto_ErroGZ_RW  ', 'self.Stamanho_Produto_ErroXYM1', 'self.Stamanho_Produto_ErroXYM2', 'self.Stamanho_Produto_ErroXYM3', 'self.Stamanho_Produto_ErroXYM4'  , 'self.Stamanho_Produto_ErroVSAG', 'self.Stamanho_Produto_ErroDRF_S' , 'self.Stamanho_Produto_ErroEXTREF' , 'self.Stamanho_Produto_ErroEXTTIE' , 'self.Stamanho_Produto_ErroEXTMIS'])
        
        writer = pd.ExcelWriter('Erro_Sistematico_GYRO.xlsx')
        
        df.to_excel(writer,'Erro GYRO',float_format='%.5f')
        
        writer.save()
        
    def ErroRandomicoGYRO_XY(self):
        
        for Estacao in range(0,len(self.dadosOriginaisGWD)):
            for coluna in range(0,1):
                for linha in range(0,3):
                    
                    self.RtamanhoErroAXY_B[Estacao][coluna][linha]  = self.Mag_AXY_B * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.AXY_B[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.AXY_B[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.AXY_B[Estacao][coluna + 2]))                     
                          
                    self.RtamanhoErroGXY_B1[Estacao][coluna][linha]  = self.Mag_GXY_B1 * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXY_B1[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXY_B1[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXY_B1[Estacao][coluna + 2]))                     
                    
                    self.RtamanhoErroGXY_B2[Estacao][coluna][linha]  = self.Mag_GXY_B2 * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXY_B2[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXY_B2[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXY_B2[Estacao][coluna + 2]))                     
                    
                    self.RtamanhoErroGXY_G2[Estacao][coluna][linha]  = self.Mag_GXY_G2 * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXY_G2[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXY_G2[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXY_G2[Estacao][coluna + 2]))                     
                    
                    self.RtamanhoErroGXY_G3[Estacao][coluna][linha]  = self.Mag_GXY_G3 * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXY_G3[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXY_G3[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXY_G3[Estacao][coluna + 2]))         
                    
                    self.RtamanhoErroGXY_RN[Estacao][coluna][linha]  = self.Mag_GXY_RN * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.GXY_RN[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.GXY_RN[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.GXY_RN[Estacao][coluna + 2]))                     
                    
                    self.RtamanhoErroDRF_R[Estacao][coluna][linha]  = self.Mag_DRF_R * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.DRF_R[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.DRF_R[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.DRF_R[Estacao][coluna + 2]))                     
 
        for Estacao in range(0,len(self.dadosOriginaisGWD)):
            for linha in range(0,3):
                for coluna in range(0,3):
           
                    self.Rtamanho_Total_ErroAXY_B[Estacao][0][linha][coluna]     = self.RtamanhoErroAXY_B[Estacao][0][linha] *  self.RtamanhoErroAXY_B[Estacao][0][coluna]
                        
                    self.Rtamanho_Total_ErroGXY_B1[Estacao][0][linha][coluna]    = self.RtamanhoErroGXY_B1[Estacao][0][linha]  * self.RtamanhoErroGXY_B1[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroGXY_B2[Estacao][0][linha][coluna]    = self.RtamanhoErroGXY_B2[Estacao][0][linha]  * self.RtamanhoErroGXY_B2[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroGXY_G2[Estacao][0][linha][coluna]    =  self.RtamanhoErroGXY_G2[Estacao][0][linha]  * self.RtamanhoErroGXY_G2[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroGXY_G3[Estacao][0][linha][coluna]    =  self.RtamanhoErroGXY_G3[Estacao][0][linha]  * self.RtamanhoErroGXY_G3[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroGXY_RN[Estacao][0][linha][coluna]    =  self.RtamanhoErroGXY_RN[Estacao][0][linha]  * self.RtamanhoErroGXY_RN[Estacao][0][coluna]
                    
                    self.Rtamanho_Total_ErroDRF_R[Estacao][0][linha][coluna]     = self.RtamanhoErroDRF_R[Estacao][0][linha]  * self.RtamanhoErroDRF_R[Estacao][0][coluna]
        

        for Estacao in range(1,len(self.dadosOriginaisGWD)):
                
            self.Rtamanho_Total_ErroAXY_B[Estacao]       = self.Rtamanho_Total_ErroAXY_B[Estacao]     + self.Rtamanho_Total_ErroAXY_B [Estacao - 1]
            
            self.Rtamanho_Total_ErroGXY_B1[Estacao]      = self.Rtamanho_Total_ErroGXY_B1[Estacao]    + self.Rtamanho_Total_ErroGXY_B1 [Estacao - 1]
            
            self.Rtamanho_Total_ErroGXY_B2[Estacao]      = self.Rtamanho_Total_ErroGXY_B2[Estacao]    + self.Rtamanho_Total_ErroGXY_B2 [Estacao - 1]
            
            self.Rtamanho_Total_ErroGXY_G2[Estacao]      = self.Rtamanho_Total_ErroGXY_G2[Estacao]    + self.Rtamanho_Total_ErroGXY_G2 [Estacao - 1]
            
            self.Rtamanho_Total_ErroGXY_G3[Estacao]      = self.Rtamanho_Total_ErroGXY_G3[Estacao]    + self.Rtamanho_Total_ErroGXY_G3 [Estacao - 1]
            
            self.Rtamanho_Total_ErroGXY_RN[Estacao]      = self.Rtamanho_Total_ErroGXY_RN[Estacao]    + self.Rtamanho_Total_ErroGXY_RN [Estacao - 1]
            
            self.Rtamanho_Total_ErroDRF_R[Estacao]       = self.Rtamanho_Total_ErroDRF_R[Estacao]     + self.Rtamanho_Total_ErroDRF_R [Estacao - 1]
            
            self.ErroRandomicoTotal_GYRO_XY[Estacao] =  self.Rtamanho_Total_ErroGXY_B1[Estacao] + self.Rtamanho_Total_ErroGXY_B2[Estacao]   + self.Rtamanho_Total_ErroGXY_RN[Estacao] + self.Rtamanho_Total_ErroDRF_R[Estacao] # self.Rtamanho_Total_ErroAXY_B[Estacao] + self.Rtamanho_Total_ErroGXY_G3[Estacao] + self.Rtamanho_Total_ErroGXY_G2[Estacao]
        
        df = pd.DataFrame([[   self.StamanhoErroAXYZ_XYB   ,        self.StamanhoErroAXY_B      ,        self.RtamanhoErroAXYZ_XYB   ,         self.RtamanhoErroAXY_B      ,        self.StamanhoErroAXYZ_ZB    ,        self.StamanhoErroAXYZ_SF    ,        self.StamanhoErroAXYZ_MS    ,        self.StamanhoErroAXY_SF     ,        self.StamanhoErroAXY_MS     ,        self.StamanhoErroAXY_GB     ,        self.StamanhoErroGXYZ_XYB1  ,        self.StamanhoErroGXYZ_XYB2  ,        self.StamanhoErroGXYZ_XYG2  ,        self.StamanhoErroGXYZ_XYG3  ,        self.StamanhoErroGXYZ_ZG1   ,        self.StamanhoErroGXY_B1     ,        self.StamanhoErroGXY_B2     ,        self.StamanhoErroGXY_G2     ,        self.StamanhoErroGXY_G3     ,        self.RtamanhoErroGXYZ_XYB1  ,        self.RtamanhoErroGXYZ_XYB2  ,        self.RtamanhoErroGXYZ_XYG2 ,        self.RtamanhoErroGXYZ_XYG3  ,        self.RtamanhoErroGXYZ_ZG1   ,        self.RtamanhoErroGXY_B1     ,        self.RtamanhoErroGXY_B2     ,        self.RtamanhoErroGXY_G2     ,        self.RtamanhoErroGXY_G3     ,        self.RtamanhoErroGXYZ_XYRN  ,        self.RtamanhoErroGXYZ_ZRN   ,        self.RtamanhoErroGXY_RN     ,          self.RtamanhoErroDRF_R      ,        self.Rtamanho_Total_ErroAXYZ_XYB  , self.Rtamanho_Total_ErroAXY_B  ,               self.Rtamanho_Total_ErroGXYZ_XYB1   ,                self.Rtamanho_Total_ErroGXYZ_XYB2   , self.Rtamanho_Total_ErroGXYZ_XYG2 ,                self.Rtamanho_Total_ErroGXYZ_XYG3   ,                self.Rtamanho_Total_ErroGXYZ_ZG1   ,        self.Rtamanho_Total_ErroGXY_B1  ,               self.Rtamanho_Total_ErroGXY_B2 ,                self.Rtamanho_Total_ErroGXY_G2  ,                self.Rtamanho_Total_ErroGXY_G3  ,               self.Rtamanho_Total_ErroGXYZ_XYRN  ,                self.Rtamanho_Total_ErroGXYZ_ZRN   ,           self.Rtamanho_Total_ErroGXY_RN  ,        self.Rtamanho_Total_ErroDRF_R  ]], columns=[ 'self.StamanhoErroAXYZ_XYB'   ,         'self.StamanhoErroAXY_B'      ,
        'self.RtamanhoErroAXYZ_XYB   ',                 'self.RtamanhoErroAXY_B      ',        'self.StamanhoErroAXYZ_ZB    ',        'self.StamanhoErroAXYZ_SF    ',        'self.SamanhoErroAXYZ_MS    ',        'self.StamanhoErroAXY_SF     ',       'self.StamanhoErroAXY_MS     ',        'self.StamanhoErroAXY_GB     ',
        'self.StamanhoErroGXYZ_XYB1  ',        'self.StamanhoErroGXYZ_XYB2  ',        'self.StamanhoErroGXYZ_XYG2  ',        'self.StamanhoErroGXYZ_XYG3  ',
        'self.StamanhoErroGXYZ_ZG1   ',        'self.StamanhoErroGXY_B1     ',        'self.StamanhoErroGXY_B2     ',        'self.StamanhoErroGXY_G2     ',
        'self.StamanhoErroGXY_G3     ',        'self.RtamanhoErroGXYZ_XYB1  ',        'self.RtamanhoErroGXYZ_XYB2  ',        'self.RtamanhoErroGXYZ_XYG2  ',        'self.RtamanhoErroGXYZ_XYG3  ',        'self.RtamanhoErroGXYZ_ZG1   ',        'self.RtamanhoErroGXY_B1     ',        'self.RtamanhoErroGXY_B2     ',        'self.RtamanhoErroGXY_G2     ',        'self.RtamanhoErroGXY_G3     ',        'self.RtamanhoErroGXYZ_XYRN  ',        'self.RtamanhoErroGXYZ_ZRN   ',
        'self.RtamanhoErroGXY_RN     ',          'self.RtamanhoErroDRF_R      ',        'self.Rtamanho_Total_ErroAXYZ_XYB'  ,
        'self.Rtamanho_Total_ErroAXY_B  ',                'self.Rtamanho_Total_ErroGXYZ_XYB1'   ,                'self.Rtamanho_Total_ErroGXYZ_XYB2'   ,                'self.Rtamanho_Total_ErroGXYZ_XYG2' ,                'self.Rtamanho_Total_ErroGXYZ_XYG3'   ,                'self.Rtamanho_Total_ErroGXYZ_ZG1 '  ,        'self.Rtamanho_Total_ErroGXY_B1'  ,                'self.Rtamanho_Total_ErroGXY_B2' ,                'self.Rtamanho_Total_ErroGXY_G2 ' ,                'self.Rtamanho_Total_ErroGXY_G3  ',                'self.Rtamanho_Total_ErroGXYZ_XYRN'  ,                'self.Rtamanho_Total_ErroGXYZ_ZRN'   ,           'self.Rtamanho_Total_ErroGXY_RN'  ,        'self.Rtamanho_Total_ErroDRF_R'])
        
        writer = pd.ExcelWriter('Erro_Randomico_GYRO.xlsx')
        
        df.to_excel(writer,'Erro GYRO',float_format='%.5f')
        
        writer.save()
        
    def ErroWellGYRO(self):
        
        for Estacao in range(0,len(self.dadosOriginaisGWD)):
            for coluna in range(0,1):
                for linha in range(0,3):
                    
                    #Vetores erro de propagação sistematico e global 
                    self.GtamanhoErroDSF_W[Estacao][coluna][linha]  = self.Mag_DSF_W * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.DSF_W[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.DSF_W[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.DSF_W[Estacao][coluna + 2]))                     
                    
                    #Vetores erro de propagação global 
                    self.GtamanhoErroDST_G_GYRO[Estacao][coluna][linha]  = self.Mag_DST_G_GYRO * ((self.efeitoErroSurveyGWD[Estacao][coluna][linha]) * (self.DST_G_GYRO[Estacao][coluna]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 1][linha]) * (self.DST_G_GYRO[Estacao][coluna + 1]) + (self.efeitoErroSurveyGWD[Estacao][coluna + 2][linha]) * (self.DST_G_GYRO[Estacao][coluna + 2]))                       
                    
        for Estacao in range(1,len(self.dadosOriginaisGWD)):
            
            #Vetores erro de propagação sistematico e global 
            self.Gtamanho_Total_ErroDSF_W[Estacao] = self.Gtamanho_Total_ErroDSF_W[Estacao - 1] + self.GtamanhoErroDSF_W[Estacao]
                    
            #Vetores erro de propagação global 
            self.Gtamanho_Total_ErroDST_G_GYRO[Estacao]  = self.Gtamanho_Total_ErroDST_G_GYRO[Estacao - 1] + self.GtamanhoErroDST_G_GYRO[Estacao]
                    
        for Estacao in range(0,len(self.dadosOriginaisGWD)):
            for linha in range(0,3):
                for coluna in range(0,3):
                    
                    #Vetores erro de propagação sistematico e global 
                    self.Gtamanho_Produto_ErroDSF_W [Estacao][0][linha][coluna] = self.Gtamanho_Total_ErroDSF_W [Estacao][0][linha] * self.Gtamanho_Total_ErroDSF_W [Estacao][0][coluna]
                    #Vetores erro de propagação global 
                    self.Gtamanho_Produto_ErroDST_G_GYRO [Estacao][0][linha][coluna]  = self.Gtamanho_Total_ErroDST_G_GYRO [Estacao][0][linha] * self.Gtamanho_Total_ErroDST_G_GYRO [Estacao][0][coluna]
                    
            self.ErroWellTotal_GYRO[Estacao] = self.Gtamanho_Produto_ErroDST_G_GYRO[Estacao] # + self.Gtamanho_Produto_ErroDSF_W[Estacao] 
        
        df = pd.DataFrame([[self.Gtamanho_Produto_ErroDST_G_GYRO]], columns=[ 'self.Gtamanho_Produto_ErroDST_G_GYRO'])
        
        writer = pd.ExcelWriter('Erro_Global_GYRO.xlsx')
        
        df.to_excel(writer,'Erro GYRO',float_format='%.5f')
        
        writer.save()
        
    def ErroSurveyGYRO(self):
    
        if self.tipoGyro == 0:
            
            for Estacao in range(0,len(self.dadosOriginaisGWD)):
                
                self.ErroTotalGYRO[Estacao] = self.ErroRandomicoTotal_GYRO_XY[Estacao] + self.ErroSistematicoTotal_GYRO_XY[Estacao] + self.ErroWellTotal_GYRO[Estacao]
                
                print("\nMatriz Covariancia Gyro - Estacao: ", Estacao + 1)
                print(self.ErroTotalGYRO[Estacao])
                
        if self.tipoGyro == 1:
            
            for Estacao in range(0,len(self.dadosOriginaisGWD)):
                
                self.ErroTotalGYRO[Estacao] = self.ErroRandomicoTotal_GYRO_XYZ[Estacao] + self.ErroSistematicoTotal_GYRO_XYZ[Estacao] + self.ErroWellTotal_GYRO[Estacao]
            
                print("\nMatriz Covariancia Gyro - Estacao: ", Estacao + 1)
                print(self.ErroTotalGYRO[Estacao])       
            
class TransformarBLA(TamanhoErroSurveyMWD,TamanhoErroSurveyGyro):
    
    def __init__(self):
        
        super().__init__()
        
        self.T_MWD = np.zeros((len(self.dadosOriginaisMWD),3,3),dtype=np.float64)
        
        self.T_transposta_MWD = np.zeros((len(self.dadosOriginaisMWD),3,3),dtype=np.float64)
        
        self.Matriz_covariancia_BLH_MWD = np.zeros((len(self.dadosOriginaisMWD),1,3,3),dtype=np.float64)
        
        self.T_GYRO = np.zeros((len(self.dadosOriginaisGWD),3,3),dtype=np.float64)
        
        self.T_transposta_GYRO = np.zeros((len(self.dadosOriginaisGWD),3,3),dtype=np.float64)
        
        self.Matriz_covariancia_BLH_GYRO = np.zeros((len(self.dadosOriginaisGWD),1,3,3),dtype=np.float64)
          
        self.Transformar_MWD()
        
        self.Transformar_GYRO()

    def Transformar_MWD(self):
        
        for Estacao in range(0,len(self.dadosOriginaisMWD)):
            
            self.T_MWD[Estacao] = np.array([[np.cos(self.I_MWD[Estacao]) * np.cos(self.Azm_MWD[Estacao]), np.sin(self.Azm_MWD[Estacao]), np.sin(self.I_MWD[Estacao]) * np.cos(self.Azm_MWD[Estacao])], [np.cos(self.I_MWD[Estacao]) * np.sin(self.Azm_MWD[Estacao]), np.cos(self.Azm_MWD[Estacao]), np.sin(self.I_MWD[Estacao]) * np.sin(self.Azm_MWD[Estacao])],[- 1 * np.sin(self.I_MWD[Estacao]),0,np.cos(self.I_MWD[Estacao])]],dtype=object)
            
            self.T_transposta_MWD[Estacao] = self.T_MWD[Estacao].transpose()       
            
            self.Matriz_covariancia_BLH_MWD[Estacao] = np.matmul(self.T_MWD[Estacao],self.ErroTotalMWD[Estacao][0],self.T_transposta_MWD[Estacao])
                
    def Transformar_GYRO(self):
        
        for Estacao in range(0,len(self.dadosOriginaisGWD)):
            
            self.T_GYRO[Estacao] = np.array([[np.cos(self.I_GYRO[Estacao]) * np.cos(self.Azm_GYRO[Estacao]), np.sin(self.Azm_GYRO[Estacao]), np.sin(self.I_GYRO[Estacao]) * np.cos(self.Azm_GYRO[Estacao])], [np.cos(self.I_GYRO[Estacao]) * np.sin(self.Azm_GYRO[Estacao]), np.cos(self.Azm_GYRO[Estacao]), np.sin(self.I_GYRO[Estacao]) * np.sin(self.Azm_GYRO[Estacao])],[- 1 * np.sin(self.I_GYRO[Estacao]),0,np.cos(self.I_GYRO[Estacao])]],dtype=object)
            
            self.T_transposta_GYRO[Estacao] = self.T_GYRO[Estacao].transpose()       
            
            self.Matriz_covariancia_BLH_GYRO[Estacao] = np.matmul(self.T_GYRO[Estacao],self.ErroTotalGYRO[Estacao][0],self.T_transposta_GYRO[Estacao])


class MinimaCurvatura(TransformarBLA): 
    
    def __init__(self):
        
        super().__init__()
        
        self.variaveis_MWD()
        self.AnaliseParametros_MWD()
        self.CalculoNEV_MWD()
    
        self.variaveis_GYRO()
        self.AnaliseParametros_GYRO()
        self.CalculoNEV_GYRO()
        
    def variaveis_MWD(self):
        
        self.DeltaMd_MWD                         = np.zeros(len(self.dadosOriginaisMWD),dtype=np.float64)
        
        self.contadorMD_MWD                      = np.zeros(len(self.dadosOriginaisMWD),dtype=np.float64)
        
        self.numeroEstacoesInterpoladas_MWD      = int(round(self.Md_MWD[len(self.dadosOriginaisMWD)-1][0] - self.Md_MWD[0][0]))
        
        self.novoMd_MWD                          = np.zeros(self.numeroEstacoesInterpoladas_MWD,dtype=np.float64)
        
        self.Alfa_MWD                            = np.zeros(len(self.dadosOriginaisMWD)-1,dtype=np.float64)
        
        self.AlfaInterpolado_MWD                 = np.zeros(self.numeroEstacoesInterpoladas_MWD,dtype=np.float64)
        
        self.tN_MWD                              = np.zeros(self.numeroEstacoesInterpoladas_MWD,dtype=np.float64)
        
        self.tE_MWD                              = np.zeros(self.numeroEstacoesInterpoladas_MWD,dtype=np.float64)
                        
        self.tV_MWD                              = np.zeros(self.numeroEstacoesInterpoladas_MWD,dtype=np.float64)
                
        self.fatorGeometrico_MWD                 = float
        
        self.RazaoArco_MWD                       = float
        
        self.North_MWD                           = np.zeros(self.numeroEstacoesInterpoladas_MWD,dtype=np.float64)
    
        self.East_MWD                            = np.zeros(self.numeroEstacoesInterpoladas_MWD,dtype=np.float64)
        
        self.Vertical_MWD                        = np.zeros(self.numeroEstacoesInterpoladas_MWD,dtype=np.float64)
        
        self.TNorth_MWD                          = np.zeros(len(self.dadosOriginaisMWD),dtype=np.float64)
        
        self.TEast_MWD                           = np.zeros(len(self.dadosOriginaisMWD),dtype=np.float64)
        
        self.TVertical_MWD                       = np.zeros(len(self.dadosOriginaisMWD),dtype=np.float64)

    def variaveis_GYRO(self):
        
        self.DeltaMd_GYRO                         = np.zeros(len(self.dadosOriginaisGWD),dtype=np.float64)
        
        self.contadorMD_GYRO                      = np.zeros(len(self.dadosOriginaisGWD),dtype=np.float64)
        
        self.numeroEstacoesInterpoladas_GYRO      = int(round(self.Md_GYRO[len(self.dadosOriginaisGWD)-1][0] - self.Md_GYRO[0][0]))
        
        self.novoMd_GYRO                          = np.zeros(self.numeroEstacoesInterpoladas_GYRO,dtype=np.float64)
        
        self.Alfa_GYRO                            = np.zeros(len(self.dadosOriginaisGWD)-1,dtype=np.float64)
        
        self.AlfaInterpolado_GYRO                 = np.zeros(self.numeroEstacoesInterpoladas_GYRO,dtype=np.float64)
        
        self.tN_GYRO                              = np.zeros(self.numeroEstacoesInterpoladas_GYRO,dtype=np.float64)
        
        self.tE_GYRO                              = np.zeros(self.numeroEstacoesInterpoladas_GYRO,dtype=np.float64)
                        
        self.tV_GYRO                              = np.zeros(self.numeroEstacoesInterpoladas_GYRO,dtype=np.float64)
                
        self.fatorGeometrico_GYRO                 = float
        
        self.RazaoArco_GYRO                       = float
        
        self.North_GYRO                           = np.zeros(self.numeroEstacoesInterpoladas_GYRO,dtype=np.float64)
    
        self.East_GYRO                            = np.zeros(self.numeroEstacoesInterpoladas_GYRO,dtype=np.float64)
        
        self.Vertical_GYRO                        = np.zeros(self.numeroEstacoesInterpoladas_GYRO,dtype=np.float64)
        
        self.TNorth_GYRO                          = np.zeros(len(self.dadosOriginaisGWD),dtype=np.float64)
        
        self.TEast_GYRO                           = np.zeros(len(self.dadosOriginaisGWD),dtype=np.float64)
        
        self.TVertical_GYRO                       = np.zeros(len(self.dadosOriginaisGWD),dtype=np.float64)
        
    def AnaliseParametros_MWD(self):
        
        for Estacao in range(0,len(self.dadosOriginaisMWD)-1):
            
            self.DeltaMd_MWD[Estacao] = self.Md_MWD[Estacao + 1][0]- self.Md_MWD[Estacao][0]
            
            self.contadorMD_MWD[Estacao] =   self.DeltaMd_MWD[Estacao] + self.contadorMD_MWD[Estacao - 1]
            
        for Estacao in range(0,len(self.dadosOriginaisMWD)):
            
            self.I_MWD[Estacao] = mt.radians(self.I_MWD[Estacao][0])
            self.Azm_MWD[Estacao] = mt.radians(self.Azm_MWD[Estacao][0])
            
        self.novoMd_MWD[0] = self.Md_MWD[0][0]
        
        for interpolado in range(0,self.numeroEstacoesInterpoladas_MWD - 1):
            
            self.novoMd_MWD[interpolado + 1] = self.novoMd_MWD[interpolado] + 1
            
        for i in range(1,len(self.dadosOriginaisMWD)):
                    
            self.novoMd_MWD[int(round(self.contadorMD_MWD[i - 1]))-1] = self.Md_MWD[i][0]

    def AnaliseParametros_GYRO(self):
        
        for Estacao in range(0,len(self.dadosOriginaisGWD)-1):
            
            self.DeltaMd_GYRO[Estacao] = self.Md_GYRO[Estacao + 1][0]- self.Md_GYRO[Estacao][0]
            
            self.contadorMD_GYRO[Estacao] =   self.DeltaMd_GYRO[Estacao] + self.contadorMD_GYRO[Estacao - 1]
            
        for Estacao in range(0,len(self.dadosOriginaisGWD)):
            
            self.I_GYRO[Estacao] = mt.radians(self.I_GYRO[Estacao][0])
            self.Azm_GYRO[Estacao] = mt.radians(self.Azm_GYRO[Estacao][0])
            
        self.novoMd_GYRO[0] = self.Md_GYRO[0][0]
        
        for interpolado in range(0,self.numeroEstacoesInterpoladas_GYRO - 1):
            
            self.novoMd_GYRO[interpolado + 1] = self.novoMd_GYRO[interpolado] + 1
            
        for i in range(1,len(self.dadosOriginaisGWD)):
                    
            self.novoMd_GYRO[int(round(self.contadorMD_GYRO[i - 1]))-1] = self.Md_GYRO[i][0]

    def CalculoNEV_GYRO(self):
        
        self.RazaoArco_GYRO = 1.0
        
        for contadorY in range(1,len(self.dadosOriginaisGWD)):
            
            self.Alfa_GYRO[contadorY-1] = 2 * np.arcsin(mt.pow(mt.pow(np.sin((self.I_GYRO[contadorY] - self.I_GYRO[contadorY - 1])/2),2) + np.sin(self.I_GYRO[contadorY - 1]) * np.sin(self.I_GYRO[contadorY]) * mt.pow(np.sin((self.Azm_GYRO[contadorY] - self.Azm_GYRO[contadorY - 1])/2),2),0.5))
        
        for contadorX in range(0,self.numeroEstacoesInterpoladas_GYRO):
            
            for contadorY in range(0,len(self.dadosOriginaisGWD)-1):

                if self.novoMd_GYRO[contadorX] == self.Md_GYRO[contadorY][0]:
                                        
                    self.Alfa_GYRO[contadorY] = 2 * np.arcsin(mt.pow(mt.pow(np.sin((self.I_GYRO[contadorY  + 1][0] - self.I_GYRO[contadorY][0])/2),2) + np.sin(self.I_GYRO[contadorY][0]) * np.sin(self.I_GYRO[contadorY + 1][0]) * mt.pow(np.sin((self.Azm_GYRO[contadorY + 1][0] - self.Azm_GYRO[contadorY][0])/2),2),0.5))
                    
                    if self.Alfa_GYRO[contadorY] > 0.02:
                       
                        self.fatorGeometrico_GYRO = np.tan(self.Alfa_GYRO[contadorY]/2)/(self.Alfa_GYRO[contadorY]/2)
                        
                    else: 
                       
                        self.fatorGeometrico_GYRO = 1 + ((mt.pow(self.Alfa_GYRO[contadorY],2)/12) * ( 1 + (mt.pow(self.Alfa_GYRO[contadorY],2)/10) * ( 1 + (mt.pow(self.Alfa_GYRO[contadorY],2)/168) * ( 1 + 31 * (mt.pow(self.Alfa_GYRO[contadorY],2)/18)))))
                        
                    self.North_GYRO[int(round(self.contadorMD_GYRO[contadorY]))-1] = self.North_GYRO[int(round(self.contadorMD_GYRO[contadorY-1]))-1] + (self.DeltaMd_GYRO[contadorY] * self.fatorGeometrico_GYRO/2) * ((np.sin(self.I_GYRO[contadorY]) * np.cos(self.Azm_GYRO[contadorY])) + (np.sin(self.I_GYRO[contadorY + 1]) * np.cos(self.Azm_GYRO[contadorY + 1])))
        
                    self.East_GYRO[int(round(self.contadorMD_GYRO[contadorY]))-1] = self.East_GYRO[int(round(self.contadorMD_GYRO[contadorY-1]))-1] + (self.DeltaMd_GYRO[contadorY] * self.fatorGeometrico_GYRO/2) * ((np.sin(self.I_GYRO[contadorY]) * np.sin(self.Azm_GYRO[contadorY])) + (np.sin(self.I_GYRO[contadorY + 1]) * np.sin(self.Azm_GYRO[contadorY + 1])))
                        
                    self.Vertical_GYRO[int(round(self.contadorMD_GYRO[contadorY]))-1] = self.Vertical_GYRO[int(round(self.contadorMD_GYRO[contadorY-1]))-1] + (self.DeltaMd_GYRO[contadorY] * self.fatorGeometrico_GYRO/2) * ((np.cos(self.I_GYRO[contadorY])) + (np.cos(self.I_GYRO[contadorY + 1])))
                    
                    self.TNorth_GYRO[contadorY]                              = self.North_GYRO[int(round(self.contadorMD_GYRO[contadorY]))-1]
        
                    self.TEast_GYRO[contadorY]                               = self.East_GYRO[int(round(self.contadorMD_GYRO[contadorY]))-1]
        
                    self.TVertical_GYRO[contadorY]                           = self.Vertical_GYRO[int(round(self.contadorMD_GYRO[contadorY]))-1]
        
        self.TNorth_GYRO = np.delete(self.TNorth_GYRO, len(self.dadosOriginaisGWD)-1)
        self.TEast_GYRO = np.delete(self.TEast_GYRO, len(self.dadosOriginaisGWD)-1)
        self.TVertical_GYRO = np.delete(self.TVertical_GYRO, len(self.dadosOriginaisGWD)-1)
        self.TNorth_GYRO = np.insert(self.TNorth_GYRO, 0, 0)
        self.TEast_GYRO = np.insert(self.TEast_GYRO, 0, 0)
        self.TVertical_GYRO = np.insert(self.TVertical_GYRO, 0, 0)
        
        for contadorX in range(0,self.numeroEstacoesInterpoladas_GYRO):
            
            for contadorY in range(0,len(self.dadosOriginaisGWD)-1):
                
                if self.novoMd_GYRO[contadorX] > self.Md_GYRO[contadorY]:
                    
                    if self.novoMd_GYRO[contadorX] < self.Md_GYRO[contadorY + 1]:

                        self.AlfaInterpolado_GYRO[contadorX] = ((self.novoMd_GYRO[contadorX] - self.Md_GYRO[contadorY])/self.DeltaMd_GYRO[contadorY]) * self.Alfa_GYRO[contadorY]
                        
                        if self.Alfa_GYRO[contadorY] > 0.02:
                            
                            fator1 = np.sin(self.Alfa_GYRO[contadorY] - self.AlfaInterpolado_GYRO[contadorX])/np.sin(self.Alfa_GYRO[contadorY])
                            
                            fator2 = np.sin(self.AlfaInterpolado_GYRO[contadorX])/np.sin(self.Alfa_GYRO[contadorY])
                            
                        elif self.Alfa_GYRO[contadorY] < 0.02 and self.Alfa_GYRO[contadorY] != 0.00:
                        
                            constantefator1 = (1 - (self.novoMd_GYRO[contadorX] - self.Md_GYRO[contadorY]))/ (self.DeltaMd_GYRO[contadorY])
                            
                            fator1 = constantefator1 + mt.pow(self.Alfa_GYRO[contadorY],2) * (constantefator1 * ((1 - mt.pow(constantefator1,2))/6) + mt.pow(self.Alfa_GYRO[contadorY],2) * ( constantefator1 * ((7/360) + mt.pow(constantefator1,2) * ( (-1/36) + (mt.pow(constantefator1,2)/120))) + mt.pow(self.Alfa_GYRO[contadorY],2) * (constantefator1 * ( (31/15.120) + mt.pow(constantefator1,2) * ((-7/2.160) + (mt.pow(constantefator1,2) *(1/720 - mt.pow(constantefator1,2)/5.040))) + constantefator1 * mt.pow(self.Alfa_GYRO[contadorY],2) * ( (127/604.800) + mt.pow(constantefator1,2) * ( ( -31/90.720) + mt.pow(constantefator1,2) * ( (7/43.200) + mt.pow(constantefator1,2) * ( ( -1/30.240) + ( mt.pow(constantefator1,2)/362.880)))))))))
                            
                            self.RazaoArco_GYRO =  (self.novoMd_GYRO[contadorX] - self.Md_GYRO[contadorY])/ (self.DeltaMd_GYRO[contadorY])
                            
                            fator2 = self.RazaoArco_GYRO + mt.pow(self.Alfa_GYRO[contadorY],2) * (self.RazaoArco_GYRO * ((1 - mt.pow(self.RazaoArco_GYRO,2))/6) + mt.pow(self.Alfa_GYRO[contadorY],2) * ( self.RazaoArco_GYRO * ((7/360) + mt.pow(self.RazaoArco_GYRO,2) * ( (-1/36) + (mt.pow(self.RazaoArco_GYRO,2)/120))) + mt.pow(self.Alfa_GYRO[contadorY],2) * (self.RazaoArco_GYRO * ( (31/15.120) + mt.pow(self.RazaoArco_GYRO,2) * ((-7/2.160) + (mt.pow(self.RazaoArco_GYRO,2) *(1/720 - mt.pow(self.RazaoArco_GYRO,2)/5.040))) + self.RazaoArco_GYRO * mt.pow(self.Alfa_GYRO[contadorY],2) * ( (127/604.800) + mt.pow(self.RazaoArco_GYRO,2) * ( ( -31/90.720) + mt.pow(self.RazaoArco_GYRO,2) * ( (7/43.200) + mt.pow(self.RazaoArco_GYRO,2) * ( ( -1/30.240) + ( mt.pow(self.RazaoArco_GYRO,2)/362.880))     )))))))
                        
                        elif self.Alfa_GYRO[contadorY] == 0.00:
                        
                            self.RazaoArco_GYRO =  (self.novoMd_GYRO[contadorX] - self.Md_GYRO[contadorY]) / (self.DeltaMd_GYRO[contadorY])
                            
                            fator1 = self.RazaoArco_GYRO + mt.pow(self.Alfa_GYRO[contadorY],2) * (self.RazaoArco_GYRO * ((1 - mt.pow(self.RazaoArco_GYRO,2))/6) + mt.pow(self.Alfa_GYRO[contadorY],2) * ( self.RazaoArco_GYRO * ((7/360) + mt.pow(self.RazaoArco_GYRO,2) * ( (-1/36) + (mt.pow(self.RazaoArco_GYRO,2)/120))) + mt.pow(self.Alfa_GYRO[contadorY],2) * (self.RazaoArco_GYRO * ( (31/15.120) + mt.pow(self.RazaoArco_GYRO,2) * ((-7/2.160) + (mt.pow(self.RazaoArco_GYRO,2) *(1/720 - mt.pow(self.RazaoArco_GYRO,2)/5.040))) + self.RazaoArco_GYRO * mt.pow(self.Alfa_GYRO[contadorY],2) * ( (127/604.800) + mt.pow(self.RazaoArco_GYRO,2) * ( ( -31/90.720) + mt.pow(self.RazaoArco_GYRO,2) * ( (7/43.200) + mt.pow(self.RazaoArco_GYRO,2) * ( ( -1/30.240) + ( mt.pow(self.RazaoArco_GYRO,2)/362.880)))))))))
                             
                            fator2 = self.RazaoArco_GYRO + mt.pow(self.Alfa_GYRO[contadorY],2) * (self.RazaoArco_GYRO * ((1 - mt.pow(self.RazaoArco_GYRO,2))/6) + mt.pow(self.Alfa_GYRO[contadorY],2) * ( self.RazaoArco_GYRO * ((7/360) + mt.pow(self.RazaoArco_GYRO,2) * ( (-1/36) + (mt.pow(self.RazaoArco_GYRO,2)/120))) + mt.pow(self.Alfa_GYRO[contadorY],2) * (self.RazaoArco_GYRO * ( (31/15.120) + mt.pow(self.RazaoArco_GYRO,2) * ((-7/2.160) + (mt.pow(self.RazaoArco_GYRO,2) *(1/720 - mt.pow(self.RazaoArco_GYRO,2)/5.040))) + self.RazaoArco_GYRO * mt.pow(self.Alfa_GYRO[contadorY],2) * ( (127/604.800) + mt.pow(self.RazaoArco_GYRO,2) * ( ( -31/90.720) + mt.pow(self.RazaoArco_GYRO,2) * ( (7/43.200) + mt.pow(self.RazaoArco_GYRO,2) * ( ( -1/30.240) + ( mt.pow(self.RazaoArco_GYRO,2)/362.880))     )))       ))    ))
                       
                        self.tN_GYRO[contadorX] = fator1 * (np.sin(self.I_GYRO[contadorY]) * np.cos(self.Azm_GYRO[contadorY])) + fator2 * (np.sin(self.I_GYRO[contadorY + 1]) * np.cos(self.Azm_GYRO[contadorY + 1]))
                        
                        self.tE_GYRO[contadorX] = fator1 * (np.sin(self.I_GYRO[contadorY]) * np.sin(self.Azm_GYRO[contadorY])) + fator2 * (np.sin(self.I_GYRO[contadorY + 1]) * np.sin(self.Azm_GYRO[contadorY + 1]))
                        
                        self.tV_GYRO[contadorX] = fator1 * (np.cos(self.I_GYRO[contadorY])) + fator2 * (np.sin(self.I_GYRO[contadorY + 1]))
                        
                        if self.AlfaInterpolado_GYRO[contadorX] >= 0.02:

                            self.fatorGeometrico_GYRO = np.tan(self.AlfaInterpolado_GYRO[contadorX]/2)/(self.AlfaInterpolado_GYRO[contadorX]/2)
                        
                        else: 

                            self.fatorGeometrico_GYRO = 1 + ((mt.pow(self.AlfaInterpolado_GYRO[contadorX],2)/12) * ( 1 + (mt.pow(self.AlfaInterpolado_GYRO[contadorX],2)/10) * ( 1 + (mt.pow(self.AlfaInterpolado_GYRO[contadorX],2)/168) * ( 1 + 31 * (mt.pow(self.AlfaInterpolado_GYRO[contadorX],2)/18)))))
                                                
                        self.North_GYRO[contadorX] = self.North_GYRO[int(round(self.contadorMD_GYRO[contadorY]))-1] + ((self.novoMd_GYRO[contadorX] - self.Md_GYRO[contadorY]) * self.fatorGeometrico_GYRO/2) * ((np.sin(self.I_GYRO[contadorY]) * np.cos(self.Azm_GYRO[contadorY])) + self.tN_GYRO[contadorX])
        
                        self.East_GYRO[contadorX] = self.East_GYRO[int(round(self.contadorMD_GYRO[contadorY]))-1] + ((self.novoMd_GYRO[contadorX] - self.Md_GYRO[contadorY]) * self.fatorGeometrico_GYRO/2) * ((np.sin(self.I_GYRO[contadorY]) * np.sin(self.Azm_GYRO[contadorY])) + self.tE_GYRO[contadorX])
                        
                        self.Vertical_GYRO[contadorX] = self.Vertical_GYRO[int(round(self.contadorMD_GYRO[contadorY]))-1] + ((self.novoMd_GYRO[contadorX] - self.Md_GYRO[contadorY]) * self.fatorGeometrico_GYRO/2) * ((np.cos(self.I_GYRO[contadorY])) + self.tV_GYRO[contadorX])
                        
        #print(self.Alfa_GYRO)
        self.North_GYRO = np.delete(self.North_GYRO, self.numeroEstacoesInterpoladas_GYRO-1)
        self.East_GYRO = np.delete(self.East_GYRO, self.numeroEstacoesInterpoladas_GYRO-1)
        self.Vertical_GYRO = np.delete(self.Vertical_GYRO, self.numeroEstacoesInterpoladas_GYRO-1)
        
    def CalculoNEV_MWD(self):
        
        self.RazaoArco_MWD = 1.0
        
        for contadorY in range(1,len(self.dadosOriginaisMWD)):
            
            self.Alfa_MWD[contadorY-1] = 2 * np.arcsin(mt.pow(mt.pow(np.sin((self.I_MWD[contadorY] - self.I_MWD[contadorY - 1])/2),2) + np.sin(self.I_MWD[contadorY - 1]) * np.sin(self.I_MWD[contadorY]) * mt.pow(np.sin((self.Azm_MWD[contadorY] - self.Azm_MWD[contadorY - 1])/2),2),0.5))
        
        for contadorX in range(0,self.numeroEstacoesInterpoladas_MWD):
            
            for contadorY in range(0,len(self.dadosOriginaisMWD)-1):

                if self.novoMd_MWD[contadorX] == self.Md_MWD[contadorY][0]:

                    self.Alfa_MWD[contadorY] = 2 * np.arcsin(mt.pow(mt.pow(np.sin((self.I_MWD[contadorY  + 1][0] - self.I_MWD[contadorY][0])/2),2) + np.sin(self.I_MWD[contadorY][0]) * np.sin(self.I_MWD[contadorY + 1][0]) * mt.pow(np.sin((self.Azm_MWD[contadorY + 1][0] - self.Azm_MWD[contadorY][0])/2),2),0.5))
                    
                    if self.Alfa_MWD[contadorY] > 0.02:
                       
                        self.fatorGeometrico_MWD = np.tan(self.Alfa_MWD[contadorY]/2)/(self.Alfa_MWD[contadorY]/2)
                        
                    else: 
                       
                        self.fatorGeometrico_MWD = 1 + ((mt.pow(self.Alfa_MWD[contadorY],2)/12) * ( 1 + (mt.pow(self.Alfa_MWD[contadorY],2)/10) * ( 1 + (mt.pow(self.Alfa_MWD[contadorY],2)/168) * ( 1 + 31 * (mt.pow(self.Alfa_MWD[contadorY],2)/18)))))
                        
                    self.North_MWD[int(round(self.contadorMD_MWD[contadorY]))-1] = self.North_MWD[int(round(self.contadorMD_MWD[contadorY-1]))-1] + (self.DeltaMd_MWD[contadorY] * self.fatorGeometrico_MWD/2) * ((np.sin(self.I_MWD[contadorY]) * np.cos(self.Azm_MWD[contadorY])) + (np.sin(self.I_MWD[contadorY + 1]) * np.cos(self.Azm_MWD[contadorY + 1])))
        
                    self.East_MWD[int(round(self.contadorMD_MWD[contadorY]))-1] = self.East_MWD[int(round(self.contadorMD_MWD[contadorY-1]))-1] + (self.DeltaMd_MWD[contadorY] * self.fatorGeometrico_MWD/2) * ((np.sin(self.I_MWD[contadorY]) * np.sin(self.Azm_MWD[contadorY])) + (np.sin(self.I_MWD[contadorY + 1]) * np.sin(self.Azm_MWD[contadorY + 1])))
                        
                    self.Vertical_MWD[int(round(self.contadorMD_MWD[contadorY]))-1] = self.Vertical_MWD[int(round(self.contadorMD_MWD[contadorY-1]))-1] + (self.DeltaMd_MWD[contadorY] * self.fatorGeometrico_MWD/2) * ((np.cos(self.I_MWD[contadorY])) + (np.cos(self.I_MWD[contadorY + 1])))
                    
                    self.TNorth_MWD[contadorY]                              = self.North_MWD[int(round(self.contadorMD_MWD[contadorY]))-1]
        
                    self.TEast_MWD[contadorY]                               = self.East_MWD[int(round(self.contadorMD_MWD[contadorY]))-1]
        
                    self.TVertical_MWD[contadorY]                           = self.Vertical_MWD[int(round(self.contadorMD_MWD[contadorY]))-1]
        
        self.TNorth_MWD = np.delete(self.TNorth_MWD, len(self.dadosOriginaisMWD)-1)
        self.TEast_MWD = np.delete(self.TEast_MWD, len(self.dadosOriginaisMWD)-1)
        self.TVertical_MWD = np.delete(self.TVertical_MWD, len(self.dadosOriginaisMWD)-1)
        self.TNorth_MWD = np.insert(self.TNorth_MWD, 0, 0)
        self.TEast_MWD = np.insert(self.TEast_MWD, 0, 0)
        self.TVertical_MWD = np.insert(self.TVertical_MWD, 0, 0)

        for contadorX in range(0,self.numeroEstacoesInterpoladas_MWD):
            
            for contadorY in range(0,len(self.dadosOriginaisMWD)-1):
                
                if self.novoMd_MWD[contadorX] > self.Md_MWD[contadorY]:
                    
                    if self.novoMd_MWD[contadorX] < self.Md_MWD[contadorY + 1]:

                        self.AlfaInterpolado_MWD[contadorX] = ((self.novoMd_MWD[contadorX] - self.Md_MWD[contadorY])/self.DeltaMd_MWD[contadorY]) * self.Alfa_MWD[contadorY]
                        
                        if self.Alfa_MWD[contadorY] > 0.02:
                            
                            fator1 = np.sin(self.Alfa_MWD[contadorY] - self.AlfaInterpolado_MWD[contadorX])/np.sin(self.Alfa_MWD[contadorY])
                            
                            fator2 = np.sin(self.AlfaInterpolado_MWD[contadorX])/np.sin(self.Alfa_MWD[contadorY])
                            
                        elif self.Alfa_MWD[contadorY] < 0.02 and self.Alfa_MWD[contadorY] != 0.00:
                        
                            constantefator1 = (1 - (self.novoMd_MWD[contadorX] - self.Md_MWD[contadorY]))/ (self.DeltaMd_MWD[contadorY])
                            
                            fator1 = constantefator1 + mt.pow(self.Alfa_MWD[contadorY],2) * (constantefator1 * ((1 - mt.pow(constantefator1,2))/6) + mt.pow(self.Alfa_MWD[contadorY],2) * ( constantefator1 * ((7/360) + mt.pow(constantefator1,2) * ( (-1/36) + (mt.pow(constantefator1,2)/120))) + mt.pow(self.Alfa_MWD[contadorY],2) * (constantefator1 * ( (31/15.120) + mt.pow(constantefator1,2) * ((-7/2.160) + (mt.pow(constantefator1,2) *(1/720 - mt.pow(constantefator1,2)/5.040))) + constantefator1 * mt.pow(self.Alfa_MWD[contadorY],2) * ( (127/604.800) + mt.pow(constantefator1,2) * ( ( -31/90.720) + mt.pow(constantefator1,2) * ( (7/43.200) + mt.pow(constantefator1,2) * ( ( -1/30.240) + ( mt.pow(constantefator1,2)/362.880)))))))))
                            
                            self.RazaoArco_MWD =  (self.novoMd_MWD[contadorX] - self.Md_MWD[contadorY])/ (self.DeltaMd_MWD[contadorY])
                            
                            fator2 = self.RazaoArco_MWD + mt.pow(self.Alfa_MWD[contadorY],2) * (self.RazaoArco_MWD * ((1 - mt.pow(self.RazaoArco_MWD,2))/6) + mt.pow(self.Alfa_MWD[contadorY],2) * ( self.RazaoArco_MWD * ((7/360) + mt.pow(self.RazaoArco_MWD,2) * ( (-1/36) + (mt.pow(self.RazaoArco_MWD,2)/120))) + mt.pow(self.Alfa_MWD[contadorY],2) * (self.RazaoArco_MWD * ( (31/15.120) + mt.pow(self.RazaoArco_MWD,2) * ((-7/2.160) + (mt.pow(self.RazaoArco_MWD,2) *(1/720 - mt.pow(self.RazaoArco_MWD,2)/5.040))) + self.RazaoArco_MWD * mt.pow(self.Alfa_MWD[contadorY],2) * ( (127/604.800) + mt.pow(self.RazaoArco_MWD,2) * ( ( -31/90.720) + mt.pow(self.RazaoArco_MWD,2) * ( (7/43.200) + mt.pow(self.RazaoArco_MWD,2) * ( ( -1/30.240) + ( mt.pow(self.RazaoArco_MWD,2)/362.880))     )))))))
                        
                        elif self.Alfa_MWD[contadorY] == 0.00:
                        
                            self.RazaoArco_MWD =  (self.novoMd_MWD[contadorX] - self.Md_MWD[contadorY]) / (self.DeltaMd_MWD[contadorY])
                            
                            fator1 = self.RazaoArco_MWD + mt.pow(self.Alfa_MWD[contadorY],2) * (self.RazaoArco_MWD * ((1 - mt.pow(self.RazaoArco_MWD,2))/6) + mt.pow(self.Alfa_MWD[contadorY],2) * ( self.RazaoArco_MWD * ((7/360) + mt.pow(self.RazaoArco_MWD,2) * ( (-1/36) + (mt.pow(self.RazaoArco_MWD,2)/120))) + mt.pow(self.Alfa_MWD[contadorY],2) * (self.RazaoArco_MWD * ( (31/15.120) + mt.pow(self.RazaoArco_MWD,2) * ((-7/2.160) + (mt.pow(self.RazaoArco_MWD,2) *(1/720 - mt.pow(self.RazaoArco_MWD,2)/5.040))) + self.RazaoArco_MWD * mt.pow(self.Alfa_MWD[contadorY],2) * ( (127/604.800) + mt.pow(self.RazaoArco_MWD,2) * ( ( -31/90.720) + mt.pow(self.RazaoArco_MWD,2) * ( (7/43.200) + mt.pow(self.RazaoArco_MWD,2) * ( ( -1/30.240) + ( mt.pow(self.RazaoArco_MWD,2)/362.880)))))))))
                             
                            fator2 = self.RazaoArco_MWD + mt.pow(self.Alfa_MWD[contadorY],2) * (self.RazaoArco_MWD * ((1 - mt.pow(self.RazaoArco_MWD,2))/6) + mt.pow(self.Alfa_MWD[contadorY],2) * ( self.RazaoArco_MWD * ((7/360) + mt.pow(self.RazaoArco_MWD,2) * ( (-1/36) + (mt.pow(self.RazaoArco_MWD,2)/120))) + mt.pow(self.Alfa_MWD[contadorY],2) * (self.RazaoArco_MWD * ( (31/15.120) + mt.pow(self.RazaoArco_MWD,2) * ((-7/2.160) + (mt.pow(self.RazaoArco_MWD,2) *(1/720 - mt.pow(self.RazaoArco_MWD,2)/5.040))) + self.RazaoArco_MWD * mt.pow(self.Alfa_MWD[contadorY],2) * ( (127/604.800) + mt.pow(self.RazaoArco_MWD,2) * ( ( -31/90.720) + mt.pow(self.RazaoArco_MWD,2) * ( (7/43.200) + mt.pow(self.RazaoArco_MWD,2) * ( ( -1/30.240) + ( mt.pow(self.RazaoArco_MWD,2)/362.880))     )))       ))    ))
                       
                        self.tN_MWD[contadorX] = fator1 * (np.sin(self.I_MWD[contadorY]) * np.cos(self.Azm_MWD[contadorY])) + fator2 * (np.sin(self.I_MWD[contadorY + 1]) * np.cos(self.Azm_MWD[contadorY + 1]))
                        
                        self.tE_MWD[contadorX] = fator1 * (np.sin(self.I_MWD[contadorY]) * np.sin(self.Azm_MWD[contadorY])) + fator2 * (np.sin(self.I_MWD[contadorY + 1]) * np.sin(self.Azm_MWD[contadorY + 1]))
                        
                        self.tV_MWD[contadorX] = fator1 * (np.cos(self.I_MWD[contadorY])) + fator2 * (np.sin(self.I_MWD[contadorY + 1]))
                        
                        if self.AlfaInterpolado_MWD[contadorX] >= 0.02:

                            self.fatorGeometrico_MWD = np.tan(self.AlfaInterpolado_MWD[contadorX]/2)/(self.AlfaInterpolado_MWD[contadorX]/2)
                        
                        else: 

                            self.fatorGeometrico_MWD = 1 + ((mt.pow(self.AlfaInterpolado_MWD[contadorX],2)/12) * ( 1 + (mt.pow(self.AlfaInterpolado_MWD[contadorX],2)/10) * ( 1 + (mt.pow(self.AlfaInterpolado_MWD[contadorX],2)/168) * ( 1 + 31 * (mt.pow(self.AlfaInterpolado_MWD[contadorX],2)/18)))))
                                                
                        self.North_MWD[contadorX] = self.North_MWD[int(round(self.contadorMD_MWD[contadorY]))-1] + ((self.novoMd_MWD[contadorX] - self.Md_MWD[contadorY]) * self.fatorGeometrico_MWD/2) * ((np.sin(self.I_MWD[contadorY]) * np.cos(self.Azm_MWD[contadorY])) + self.tN_MWD[contadorX])
        
                        self.East_MWD[contadorX] = self.East_MWD[int(round(self.contadorMD_MWD[contadorY]))-1] + ((self.novoMd_MWD[contadorX] - self.Md_MWD[contadorY]) * self.fatorGeometrico_MWD/2) * ((np.sin(self.I_MWD[contadorY]) * np.sin(self.Azm_MWD[contadorY])) + self.tE_MWD[contadorX])
                        
                        self.Vertical_MWD[contadorX] = self.Vertical_MWD[int(round(self.contadorMD_MWD[contadorY]))-1] + ((self.novoMd_MWD[contadorX] - self.Md_MWD[contadorY]) * self.fatorGeometrico_MWD/2) * ((np.cos(self.I_MWD[contadorY])) + self.tV_MWD[contadorX])
                        
        #print(self.Alfa_MWD)
        self.North_MWD = np.delete(self.North_MWD, self.numeroEstacoesInterpoladas_MWD-1)
        self.East_MWD = np.delete(self.East_MWD, self.numeroEstacoesInterpoladas_MWD-1)
        self.Vertical_MWD = np.delete(self.Vertical_MWD, self.numeroEstacoesInterpoladas_MWD-1)

class ElipseErro(MinimaCurvatura):
    
    def __init__(self):
        
        super().__init__()
        
        self.autovalor_MWD = np.zeros((len(self.dadosOriginaisMWD),3))
        self.autovetor_MWD = np.zeros((len(self.dadosOriginaisMWD),1,3,3))
        self.anguloElipse_MWD = np.zeros((len(self.dadosOriginaisMWD),3))
        self.larguraElipse_MWD = np.zeros(len(self.dadosOriginaisMWD))
        self.alturaElipse_MWD = np.zeros(len(self.dadosOriginaisMWD))
        self.comprimentoElipse_MWD = np.zeros(len(self.dadosOriginaisMWD))
        self.ordemAutoValor_MWD = np.zeros((len(self.dadosOriginaisMWD),3))

        self.autovalor_GYRO = np.zeros((len(self.dadosOriginaisGWD),3))
        self.autovetor_GYRO = np.zeros((len(self.dadosOriginaisGWD),1,3,3))
        self.anguloElipse_GYRO = np.zeros((len(self.dadosOriginaisGWD),3))
        self.larguraElipse_GYRO = np.zeros(len(self.dadosOriginaisGWD))
        self.alturaElipse_GYRO = np.zeros(len(self.dadosOriginaisGWD))
        self.comprimentoElipse_GYRO = np.zeros(len(self.dadosOriginaisGWD))
        self.ordemAutoValor_GYRO = np.zeros((len(self.dadosOriginaisGWD),3))
        
        self.AutovalorAutovetor()
        self.Ellipse()
        
    def AutovalorAutovetor(self):
        
        for Estacao in range(0,len(self.dadosOriginaisMWD)):

            self.autovalor_MWD[Estacao], self.autovetor_MWD[Estacao] = np.linalg.eig(self.ErroTotalMWD[Estacao])
            
            self.ordemAutoValor_MWD[Estacao] = np.argsort(self.autovalor_MWD[Estacao], axis =0)
        
        for Estacao in range(0,len(self.dadosOriginaisGWD)):
            
            self.autovalor_GYRO[Estacao], self.autovetor_GYRO[Estacao] = np.linalg.eig(self.ErroTotalGYRO[Estacao])
            
            self.ordemAutoValor_GYRO[Estacao] = np.argsort(self.autovalor_GYRO[Estacao], axis =0)
        
        
    def Ellipse(self):
        """
        Source: http://stackoverflow.com/a/12321306/1391441
        """
        nstd = 1.0
        
        for Estacao in range(0,len(self.dadosOriginaisMWD)):
            
            self.anguloElipse_MWD[Estacao] = np.degrees(np.arctan2(self.autovetor_MWD[Estacao][0][1],self.autovalor_MWD[Estacao]))
            
            #Width and height are "full" widths, not radius
            self.larguraElipse_MWD[Estacao], self.alturaElipse_MWD[Estacao], self.comprimentoElipse_MWD[Estacao] = nstd * np.sqrt(self.autovalor_MWD[Estacao])
        
        for Estacao in range(0,len(self.dadosOriginaisGWD)):
            
            self.anguloElipse_GYRO[Estacao] = np.degrees(np.arctan2(self.autovetor_GYRO[Estacao][0][1],self.autovalor_GYRO[Estacao]))
            
            #Width and height are "full" widths, not radius
            self.larguraElipse_GYRO[Estacao], self.alturaElipse_GYRO[Estacao], self.comprimentoElipse_GYRO[Estacao] = nstd * np.sqrt(self.autovalor_GYRO[Estacao])
                  
class Graficos(ElipseErro):       
        
    def __init__(self):
        
        super().__init__()
        
        #self.MWD_minimaCurvatura()
        #self.MWD_vertical()
        #self.GYRO_minimaCurvatura()
        self.Comparativo_minimaCurvatura()
        #self.GYRO_vertical()
        self.Comparativo_vertical()
        
    def MWD_minimaCurvatura(self):
        
        figura = plt.figure()
        grafico_MWD = figura.add_subplot(111, projection='3d')

        grafico_MWD.plot(self.TNorth_MWD, self.TEast_MWD, self.TVertical_MWD, 'b-')
        
        for Estacao in range(0,len(self.dadosOriginaisMWD),6):
            
            centro = [self.TNorth_MWD[Estacao],self.TEast_MWD[Estacao]]
                      
            ellipse_MWD = Ellipse(xy= centro , width=self.larguraElipse_MWD[Estacao], height=self.alturaElipse_MWD[Estacao], angle= self.anguloElipse_MWD[Estacao][1], edgecolor='deepskyblue', fc='None', lw=1, zorder=4) 
            
            grafico_MWD.add_patch(ellipse_MWD)
            
            art3d.pathpatch_2d_to_3d(ellipse_MWD, z=self.TVertical_MWD[Estacao], zdir="z")
           
        grafico_MWD.set_xlabel('N', linespacing = 100, size = 10, weight = 'bold')
        grafico_MWD.set_ylabel('E', linespacing = 100, size = 10, weight = 'bold')
        grafico_MWD.set_zlabel('TVD', linespacing = 100, size = 10, weight = 'bold')

        grafico_MWD.invert_zaxis()
        
        grafico_MWD.set_title("Trajetória do Poço e elipses de incerteza\n (Ferramentas Magnéticas) - lateral", fontdict={'family': 'sans-serif', 'horizontalalignment': 'center',  'color' : 'black', 'weight': 'bold', 'size': 12})
        
        plt.show()
    
    def MWD_vertical(self):
        
        figura = plt.figure()
        grafico_MWD_vertical = figura.add_subplot(111, projection='3d')

        grafico_MWD_vertical.plot(self.TNorth_MWD, self.TEast_MWD, self.TVertical_MWD, 'b-')
        
        for Estacao in range(0,len(self.dadosOriginaisMWD)):
            
            centro = [self.TEast_MWD[Estacao],self.TVertical_MWD[Estacao]]
                     
            ellipse_MWD = Ellipse(xy= centro , width=self.alturaElipse_MWD[Estacao], height=self.comprimentoElipse_MWD[Estacao], angle= self.anguloElipse_MWD[Estacao][2], edgecolor='deepskyblue', fc='None', lw=1, zorder=4) # linestyle = '--',
            
            grafico_MWD_vertical.add_patch(ellipse_MWD)
            
            art3d.pathpatch_2d_to_3d(ellipse_MWD, z=self.TNorth_MWD[Estacao], zdir="x")
           
        grafico_MWD_vertical.set_xlabel('N', linespacing = 100, size = 10, weight = 'bold')
        grafico_MWD_vertical.set_ylabel('E', linespacing = 100, size = 10, weight = 'bold')
        grafico_MWD_vertical.set_zlabel('TVD', linespacing = 100, size = 10, weight = 'bold')

        grafico_MWD_vertical.invert_zaxis()
        
        grafico_MWD_vertical.set_title("Trajetória do Poço e elipses de incerteza\n (Ferramentas Magnéticas) - vertical", fontdict={'family': 'sans-serif', 'horizontalalignment': 'center',  'color' : 'black', 'weight': 'bold', 'size': 12})
        
        plt.show()
    
    def GYRO_minimaCurvatura(self):
        
        figura = plt.figure()
        grafico_GYRO = figura.add_subplot(111, projection='3d')

        grafico_GYRO.plot(self.TNorth_GYRO, self.TEast_GYRO, self.TVertical_GYRO, 'r-', label="Trajetória do Poço")
        
        for Estacao in range(0,len(self.dadosOriginaisGWD),6):
            
            centro = [self.TNorth_GYRO[Estacao],self.TEast_GYRO[Estacao]]
        
            ellipse_GYRO = Ellipse(xy= centro , width=self.larguraElipse_GYRO[Estacao], height=self.alturaElipse_GYRO[Estacao], angle= self.anguloElipse_GYRO[Estacao][1], edgecolor= 'gold', fc='None', lw=1, zorder=4, label = "Elipse")
            
            grafico_GYRO.add_patch(ellipse_GYRO)
            
            art3d.pathpatch_2d_to_3d(ellipse_GYRO, z=self.TVertical_GYRO[Estacao], zdir="z")
           
        grafico_GYRO.set_xlabel('N', linespacing = 100, size = 10, weight = 'bold')
        grafico_GYRO.set_ylabel('E', linespacing = 200, size = 10, weight = 'bold')
        grafico_GYRO.set_zlabel('TVD', linespacing = 500, size = 10, weight = 'bold')

        grafico_GYRO.invert_zaxis()

        grafico_GYRO.set_title("Trajetória do Poço e elipses de incerteza\n (Ferramentas Giroscópicas) - lateral", fontdict={'family': 'sans-serif', 'horizontalalignment': 'center',  'color' : 'black', 'weight': 'bold', 'size': 12})

        plt.show()
        
    def GYRO_vertical(self):
        
        figura = plt.figure()
        grafico_GYRO_vertical = figura.add_subplot(111, projection='3d')

        grafico_GYRO_vertical.plot(self.TNorth_GYRO, self.TEast_GYRO, self.TVertical_GYRO, 'r-', label="Trajetória do Poço")
        
        for Estacao in range(0,len(self.dadosOriginaisGWD)):
            
            centro = [self.TEast_GYRO[Estacao],self.TVertical_GYRO[Estacao]]
                        
            ellipse_GYRO = Ellipse(xy= centro , width=self.alturaElipse_GYRO[Estacao], height=self.comprimentoElipse_GYRO[Estacao], angle= self.anguloElipse_GYRO[Estacao][2], edgecolor= 'gold', fc='None', lw=1, zorder=4, label = "Elipse")
            
            grafico_GYRO_vertical.add_patch(ellipse_GYRO)
            
            art3d.pathpatch_2d_to_3d(ellipse_GYRO, z=self.TNorth_GYRO[Estacao], zdir="x")
           
        grafico_GYRO_vertical.set_xlabel('N', linespacing = 100, size = 10, weight = 'bold')
        grafico_GYRO_vertical.set_ylabel('E', linespacing = 200, size = 10, weight = 'bold')
        grafico_GYRO_vertical.set_zlabel('TVD', linespacing = 500, size = 10, weight = 'bold')

        grafico_GYRO_vertical.invert_zaxis()

        grafico_GYRO_vertical.set_title("Trajetória do Poço e elipses de incerteza\n (Ferramentas Giroscópicas) - vertical", fontdict={'family': 'sans-serif', 'horizontalalignment': 'center',  'color' : 'black', 'weight': 'bold', 'size': 12})

        plt.show()
    
    def Comparativo_minimaCurvatura(self):
        
        figura = plt.figure()
        grafico_comparativo = figura.add_subplot(111, projection='3d')

        grafico_comparativo.plot(self.TNorth_MWD, self.TEast_MWD, self.TVertical_MWD, 'b-', label="Trajetória do Poço - Ferramenta Magnética")
        grafico_comparativo.plot(self.TNorth_GYRO, self.TEast_GYRO, self.TVertical_GYRO, 'r-', label="Trajetória do Poço - Ferramenta Giroscópica")
        
        for Estacao in range(0,len(self.dadosOriginaisMWD),8):
            
            centro_MWD = [self.TNorth_MWD[Estacao],self.TEast_MWD[Estacao]]
            ellipse_MWD = Ellipse(xy= centro_MWD , width=self.larguraElipse_MWD[Estacao], height=self.alturaElipse_MWD[Estacao], angle= self.anguloElipse_MWD[Estacao][1], edgecolor= 'deepskyblue', fc='None', lw=1, zorder=4)
            grafico_comparativo.add_patch(ellipse_MWD)
            art3d.pathpatch_2d_to_3d(ellipse_MWD, z=self.TVertical_MWD[Estacao], zdir="z")
            
        for Estacao in range(0,len(self.dadosOriginaisGWD),8):
            
            centro_GYRO = [self.TNorth_GYRO[Estacao],self.TEast_GYRO[Estacao]]
            ellipse_GYRO = Ellipse(xy= centro_GYRO , width=self.larguraElipse_GYRO[Estacao], height=self.alturaElipse_GYRO[Estacao], angle= self.anguloElipse_GYRO[Estacao][1], edgecolor= 'gold', fc='None', lw=1, zorder=4)
            grafico_comparativo.add_patch(ellipse_GYRO)
            art3d.pathpatch_2d_to_3d(ellipse_GYRO, z=self.TVertical_GYRO[Estacao], zdir="z")
        
        grafico_comparativo.set_xlabel('N', linespacing = 100, size = 10, weight = 'bold')
        grafico_comparativo.set_ylabel('E', linespacing = 100, size = 10, weight = 'bold')
        grafico_comparativo.set_zlabel('TVD', linespacing = 100, size = 10, weight = 'bold')

        grafico_comparativo.invert_zaxis()
        
        grafico_comparativo.set_title("COMPARAÇÃO TRAJETÓRIA DO POÇO E ELIPSES DE INCERTEZA\n (FERRAMENTAS MAGNÉTICAS E GIROSCÓPICAS)", fontdict={'family': 'sans-serif', 'horizontalalignment': 'center',  'color' : 'black', 'weight': 'bold', 'size': 12})
        
        grafico_comparativo.legend(loc="best",  ncol=1, shadow=True, title="Legenda", fancybox=True)

        plt.show()
        
    def Comparativo_vertical(self):
        
        figura = plt.figure()
        grafico_vertical = figura.add_subplot(111, projection='3d')

        grafico_vertical.plot(self.TNorth_MWD, self.TEast_MWD, self.TVertical_MWD, 'b-', label="Trajetória do Poço - Ferramenta Magnética")
        grafico_vertical.plot(self.TNorth_GYRO, self.TEast_GYRO, self.TVertical_GYRO, 'r-', label="Trajetória do Poço - Ferramenta Giroscópica")
        
        for Estacao in range(0,len(self.dadosOriginaisMWD)):
            
            centro_MWD = [self.TEast_MWD[Estacao],self.TVertical_MWD[Estacao]]
            ellipse_MWD = Ellipse(xy= centro_MWD , width=self.larguraElipse_MWD[Estacao], height=self.alturaElipse_MWD[Estacao], angle= self.anguloElipse_MWD[Estacao][2], edgecolor= 'deepskyblue', fc='None', lw=1, zorder=4)
            grafico_vertical.add_patch(ellipse_MWD)
            art3d.pathpatch_2d_to_3d(ellipse_MWD, z=self.TNorth_MWD[Estacao], zdir="x")
            
        for Estacao in range(0,len(self.dadosOriginaisGWD)):
            
            centro_GYRO = [self.TEast_GYRO[Estacao],self.TVertical_GYRO[Estacao]]
            ellipse_GYRO = Ellipse(xy= centro_GYRO , width=self.larguraElipse_GYRO[Estacao], height=self.alturaElipse_GYRO[Estacao], angle= self.anguloElipse_GYRO[Estacao][2], edgecolor= 'gold', fc='None', lw=1, zorder=4)
            grafico_vertical.add_patch(ellipse_GYRO)
            art3d.pathpatch_2d_to_3d(ellipse_GYRO, z=self.TNorth_GYRO[Estacao], zdir="x")
        
        grafico_vertical.set_xlabel('N', linespacing = 100, size = 10, weight = 'bold')
        grafico_vertical.set_ylabel('E', linespacing = 200, size = 10, weight = 'bold')
        grafico_vertical.set_zlabel('TVD', linespacing = 500, size = 10, weight = 'bold')

        grafico_vertical.invert_zaxis()
        
        grafico_vertical.set_title("COMPARAÇÃO DAS ELIPSES DE INCERTEZA EIXO VERTICAL\n (FERRAMENTAS MAGNÉTICAS E GIROSCÓPICAS)", fontdict={'family': 'sans-serif', 'horizontalalignment': 'center',  'color' : 'black', 'weight': 'bold', 'size': 12})
        
        grafico_vertical.legend(loc="best",  ncol=1, shadow=True, title="Legenda", fancybox=True)

        plt.show()

Graficos()