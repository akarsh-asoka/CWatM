# -------------------------------------------------------------------------
# Name:        INITCONDITION
# Purpose:	   Read/write initial condtions for warm start
#
# Author:      PB
#
# Created:     19/08/2016
# Copyright:   (c) PB 2016
# -------------------------------------------------------------------------

from management_modules.data_handling import *

class initcondition(object):

    """
     # ************************************************************
     # ***** READ/WRITE INITIAL CONDITIONS         ****************
     # ************************************************************
    """

    def __init__(self, initcondition_variable):
        self.var = initcondition_variable


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------

    def initial(self):
        """ initial part of the initcondition module
		    read intial conditions
        """

        # list all initiatial variables

        # Snow & Frost
        number = int(loadmap('NumberSnowLayers'))
        for i in xrange(number):
            initCondVar.append("SnowCover"+str(i+1))
            initCondVarValue.append("SnowCoverS["+str(i)+"]")
        initCondVar.append("FrostIndex")
        initCondVarValue.append("FrostIndex")

        # soil / landcover
        i = 0
        self.var.coverTypes = map(str.strip, binding["coverTypes"].split(","))

        #self.var.soilStor[1]

        for coverType in self.var.coverTypes:
            if coverType in ['forest', 'grassland', 'irrPaddy', 'irrNonPaddy']:
                for cond in ["interceptStor", "topWaterLayer","soilStor[0]","soilStor[1]","soilStor[2]","interflow"]:
                    initCondVar.append(coverType+"_"+ cond)
                    initCondVarValue.append(cond+"["+str(i)+"]")
            if coverType in ['sealed']:
                for cond in ["interceptStor"]:
                    initCondVar.append(coverType+"_"+ cond)
                    initCondVarValue.append(cond+"["+str(i)+"]")
            i += 1
        # groundwater
        initCondVar.append("storGroundwater")
        initCondVarValue.append("storGroundwater")

        # routing
        Var1 = ["channelStorage","readAvlChannelStorage","timestepsToAvgDischarge","avgChannelDischarge","m2tChannelDischarge","avgBaseflow","riverbedExchange"]
        Var2 = ["channelStorage","readAvlChannelStorage","timestepsToAvgDischarge1","avgDischarge","m2tDischarge","avgBaseflow","riverbedExchange"]
        initCondVar.extend(Var1)
        initCondVarValue.extend(Var2)

        # lakes & reservoirs
        Var1 = ["waterBodyStorage","avgInflowLakeReserv","avgOutflowDischarge"]
        Var2 = ["waterBodyStorage","avgInflow","avgOutflow"]
        initCondVar.extend(Var1)
        initCondVarValue.extend(Var2)


        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


        self.var.saveInit = binding['save_initial'].lower() == "true"
        if self.var.saveInit:
            self.var.saveInitFile = binding['initSave']
            initdates = binding['StepInit'].split()
            dateVar['intInit'] =[]
            for d in initdates:
                dateVar['intInit'].append(datetoInt(d, dateVar['dateBegin']))
            #dateVar['intInit'] = datetoInt(binding['StepInit'],dateVar['dateBegin'])

        self.var.loadInit = binding['load_initial'].lower() == "true"
        if self.var.loadInit:
            self.var.initLoadFile = binding['initLoad']



        j = 1

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------

    def load_initial(self,name,default = 0.0):

        init = binding[name+'Ini']
        if init.lower() == "none":
            if self.var.loadInit:
                return readnetcdfInitial(self.var.initLoadFile, name)
            else:
                #def1 = globals.inZero.copy()
                return default
        else:
            return loadmap(name+'Ini')

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------

    def dynamic(self):
        """ dynamic part of the initcondition module
            write initital conditions into 1 netcdf file
        """

        # ************************************************************
        # ***** WRITE INITIAL CONDITION  *****************************
        # ************************************************************



        if self.var.saveInit:

            if  dateVar['curr'] in dateVar['intInit']:

                self.var.timestepsToAvgDischarge1 = self.var.timestepsToAvgDischarge + globals.inZero

                self.var.avgOutflow = globals.inZero.copy()
                np.put(self.var.avgOutflow, self.var.waterBodyIndexC, self.var.avgOutflowC)
                self.var.avgInflow = globals.inZero.copy()
                np.put(self.var.avgInflow, self.var.waterBodyIndexC, self.var.avgInflowC)

                saveFile = self.var.saveInitFile + "_" + dateVar['currDate'].strftime("%Y%m%d") +".nc"
                initVar=[]
                i = 0
                for var in initCondVar:
                    variabel = "self.var."+initCondVarValue[i]
                    initVar.append(eval(variabel))
                    i += 1
                writeIniNetcdf(saveFile, initCondVar,initVar)
                i =1
