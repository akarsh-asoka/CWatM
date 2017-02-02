# -------------------------------------------------------------------------
# Name:        Water Balance module
# Purpose:		1.) check if water balance per time step is ok ( = 0)
#               2.) produce an annual overview - income, outcome storage 
# Author:      PB
#
# Created:     22/08/2016
# Copyright:   (c) PB 2016
# -------------------------------------------------------------------------

from management_modules.data_handling import *


class waterbalance(object):

    """
    # ************************************************************
    # ***** WATER BALANCE ****************************************
    # ************************************************************

	# 1.) check if water balnace per time step is ok ( = 0)
    # 2.) produce an annual overview - income, outcome storage 
    """

    def __init__(self, waterbalance_variable):
        self.var = waterbalance_variable

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------

    def initial(self):
        """ initial part of the water balance module
        """
        if option['calcWaterBalance']:
            i = 1

        """ store the initial storage volume of snow, soil etc.
        """
        if option['sumWaterBalance']:
            # variables of storage
            self.var.sum_balanceStore = ['SnowCover','sum_interceptStor','sum_topWaterLayer','sum_storUpp000005','sum_storUpp005030','sum_storLow030150']

            # variable of fluxes
            self.var.sum_balanceFlux = ['Precipitation','SnowMelt','Rain','sum_interceptEvap','actualET']

            #for variable in self.var.sum_balanceStore:
                # vars(self.var)["sumup_" + variable] =  vars(self.var)[variable]
            for variable in self.var.sum_balanceFlux:
                vars(self.var)["sumup_" + variable] =  globals.inZero.copy()
            i =1


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------


    """
    def getMinMaxMean(mapFile):
        mn = pcr.cellvalue(pcr.mapminimum(mapFile), 1)[0]
        mx = pcr.cellvalue(pcr.mapmaximum(mapFile), 1)[0]
        nrValues = pcr.cellvalue(pcr.maptotal(pcr.scalar(pcr.defined(mapFile))), 1)[
                0]  # / getNumNonMissingValues(mapFile)
        return mn, mx, (getMapTotal(mapFile) / nrValues)
    """

    def waterBalanceCheck(self, fluxesIn, fluxesOut, preStorages, endStorages, processName, printTrue=False):
        """ dynamic part of the water balance module
        Returns the water balance for a list of input, output, and storage map files
        """

        if printTrue:
            minB =0
            maxB = 0
            maxBB = 0
            income =  0
            out = 0
            store = 0

            for fluxIn in fluxesIn:   income += fluxIn
            for fluxOut in fluxesOut: out += fluxOut
            for preStorage in preStorages: store += preStorage
            for endStorage in endStorages: store -= endStorage
            balance =  income + store - out
            #balance = endStorages
            #if balance is not empty
            if balance.size:
                minB = np.amin(balance)
                maxB = np.amax(balance)
                maxBB = np.maximum(np.abs(minB),np.abs(maxB))
            #meanB = np.average(balance, axis=0)
            #meanB = 0.0

            #print "     %s %10.8f " % (processName, maxBB),
            print "     %s %10.8f %10.8f" % (processName, minB,maxB),
            if (minB < -0.00001) or (maxB > 0.00001):
                i=11111



    def waterBalanceCheckSum(self, fluxesIn, fluxesOut, preStorages, endStorages, processName, printTrue=False):
        """ dynamic part of the water balance module
        Returns the water balance for a list of input, output, and storage map files
        """
        if printTrue:
            minB =0
            maxB = 0
            maxBB = 0

            income =  0
            out = 0
            store =  0

            for fluxIn in fluxesIn:
                income = income + np.bincount(self.var.catchment,weights=fluxIn)
            for fluxOut in fluxesOut: out = out + np.bincount(self.var.catchment,weights=fluxOut)
            for preStorage in preStorages:
                store = store + np.bincount(self.var.catchment,weights=preStorage)
            for endStorage in endStorages: store = store - np.bincount(self.var.catchment,weights=endStorage)
            balance =  income + store - out
            #balance = endStorages
            if balance.size:
                minB = np.amin(balance)
                maxB = np.amax(balance)
                maxBB = np.maximum(np.abs(minB),np.abs(maxB))
                #meanB = np.average(balance, axis=0)
                #meanB = 0.0
            no = self.var.catchmentNo


            #print "     %s %10.8f " % (processName, maxBB),
            #print "     %s %10.8f %10.8f" % (processName, minB,maxB),
            print "     %s %10.8f" % (processName, balance[no]),





# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------

    def checkWaterSoilGround(self):
        """ Check water balance of snow, vegetation, soil, groundwater
        """
        if option['calcWaterBalance']:
            self.var.waterbalance_module.waterBalanceCheck(
                [self.var.Precipitation,self.var.sum_capRiseFromGW,self.var.sum_irrGrossDemand],    # In
                [self.var.sum_directRunoff,self.var.sum_interflow, self.var.sum_percToGW,    # Out
                 self.var.sum_PrefFlow,self.var.sum_actTransTotal,
                 self.var.sum_actBareSoilEvap,self.var.sum_openWaterEvap, self.var.sum_interceptEvap],
                [self.var.prevSnowCover, self.var.pretotalSoil],                                       # prev storage
                [self.var.SnowCover, self.var.totalSoil],
                "AllSoilWB", False)  #true

            self.var.waterbalance_module.waterBalanceCheck(
                [self.var.Precipitation,self.var.sum_irrGrossDemand, self.var.surfaceWaterInf],    # In
                [self.var.sum_directRunoff,self.var.sum_interflow,                            # Out
                 self.var.totalET,  self.var.nonFossilGroundwaterAbs,self.var.baseflow],
                [self.var.prevSnowCover, self.var.pretotalSoil,self.var.prestorGroundwater],       # prev storage
                [self.var.SnowCover, self.var.totalSoil,self.var.storGroundwater],
                "Soil+G", True)

            self.var.waterbalance_module.waterBalanceCheck(
                [self.var.runoff, self.var.nonIrrReturnFlow],  # In
                [self.var.sum_actSurfaceWaterAbstract, self.var.localQW, self.var.riverbedExchange * self.var.InvCellArea],           # Out
                [self.var.prechannelStorage * self.var.InvCellArea],  # prev storage
                [self.var.channelStorageBefore * self.var.InvCellArea],
                "Routing", False)




            self.var.waterbalance_module.waterBalanceCheck(
                [self.var.sum_irrGrossDemand,self.var.nonIrrGrossDemand],                                           # In
                [self.var.unmetDemand,self.var.nonFossilGroundwaterAbs, self.var.sum_actSurfaceWaterAbstract],     # Out
                [globals.inZero],
                [globals.inZero],
                "Waterdemand", False)

            self.var.waterbalance_module.waterBalanceCheck(
                [self.var.Precipitation, self.var.surfaceWaterInf,self.var.sum_irrGrossDemand,self.var.nonIrrReturnFlow],    # In
                [self.var.totalET,   self.var.localQW, self.var.riverbedExchange * self.var.InvCellArea, self.var.nonFossilGroundwaterAbs, self.var.sum_actSurfaceWaterAbstract],
                [self.var.prevSnowCover, self.var.pretotalSoil,self.var.prestorGroundwater,self.var.prechannelStorage * self.var.InvCellArea],       # prev storage
                [self.var.SnowCover, self.var.totalSoil,self.var.storGroundwater,self.var.channelStorageBefore * self.var.InvCellArea],
                "S+G+Rout1",True)
            #print self.var.channelStorageBefore[10],
            # print "%10.8f %10.8f %10.8f " % (income[10], out[10], store[10]),

            self.var.waterbalance_module.waterBalanceCheck(
                [self.var.Precipitation * self.var.cellArea, self.var.surfaceWaterInf * self.var.cellArea,self.var.sum_irrGrossDemand * self.var.cellArea,self.var.nonIrrReturnFlow * self.var.cellArea],    # In
                [self.var.totalET  * self.var.cellArea,   self.var.localQW * self.var.cellArea, self.var.riverbedExchange, self.var.nonFossilGroundwaterAbs * self.var.cellArea, self.var.sum_actSurfaceWaterAbstract * self.var.cellArea],
                [self.var.prevSnowCover * self.var.cellArea, self.var.pretotalSoil * self.var.cellArea,self.var.prestorGroundwater * self.var.cellArea,self.var.prechannelStorage],       # prev storage
                [self.var.SnowCover * self.var.cellArea, self.var.totalSoil * self.var.cellArea,self.var.storGroundwater * self.var.cellArea,self.var.channelStorageBefore],
                "S+G+Rout2", True)   # True


        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


        if option['sumWaterBalance']:
            self.var.waterbalance_module.waterBalanceCheckSum(
                [self.var.sum_irrGrossDemand,self.var.nonIrrGrossDemand],                                           # In
                [self.var.unmetDemand,self.var.nonFossilGroundwaterAbs, self.var.sum_actSurfaceWaterAbstract],     # Out
                [globals.inZero],
                [globals.inZero],
                "WaterdemandSum", False)


            self.var.waterbalance_module.waterBalanceCheckSum(
                [self.var.Precipitation, self.var.surfaceWaterInf,self.var.sum_irrGrossDemand,self.var.nonIrrReturnFlow],    # In
                [self.var.totalET,   self.var.localQW, self.var.riverbedExchange * self.var.InvCellArea, self.var.nonFossilGroundwaterAbs, self.var.sum_actSurfaceWaterAbstract],
                [self.var.prevSnowCover, self.var.pretotalSoil,self.var.prestorGroundwater,self.var.prechannelStorage * self.var.InvCellArea],       # prev storage
                [self.var.SnowCover, self.var.totalSoil,self.var.storGroundwater,self.var.channelStorageBefore * self.var.InvCellArea],
                "S+G+Rout1Sum", False)


            # discharge at outlets of catchments
            DisOut = self.var.discharge * self.var.DtSec
            DisOut = np.where(self.var.outlets > 0, DisOut, 0.)

            self.var.waterbalance_module.waterBalanceCheckSum(
                [self.var.Precipitation * self.var.cellArea, self.var.surfaceWaterInf * self.var.cellArea, self.var.sum_irrGrossDemand * self.var.cellArea,self.var.nonIrrReturnFlow * self.var.cellArea],    # In
                [self.var.totalET  * self.var.cellArea,   self.var.localQW  * self.var.cellArea, self.var.riverbedExchange, self.var.nonFossilGroundwaterAbs * self.var.cellArea, self.var.sum_actSurfaceWaterAbstract * self.var.cellArea, DisOut],
                [self.var.prevSnowCover * self.var.cellArea, self.var.pretotalSoil * self.var.cellArea,self.var.prestorGroundwater * self.var.cellArea,self.var.prechannelStorage],       # prev storage
                [self.var.SnowCover * self.var.cellArea, self.var.totalSoil * self.var.cellArea,self.var.storGroundwater * self.var.cellArea,self.var.channelStorage],
                "S+G+Rout2Sum", False)

        if option['budyko']:


            # in mm
            self.var.area = npareatotal(self.var.cellArea, self.var.catchment)
            self.var.sumETRef = 1000 * npareatotal(self.var.ETRef * self.var.cellArea, self.var.catchment)/self.var.area
            self.var.sumP = 1000 * npareatotal(self.var.Precipitation * self.var.cellArea, self.var.catchment) / self.var.area
            self.var.sumETA = 1000 * npareatotal((self.var.totalET + self.var.localQW) * self.var.cellArea , self.var.catchment)/self.var.area
            #self.var.sumRunoff = 1000 *  npareatotal((self.var.channelStorageBefore - self.var.prechannelStorage), self.var.catchment)/self.var.area
            #self.var.sumDelta1 = 1000 * npareatotal((self.var.SnowCover + self.var.totalSoil + self.var.storGroundwater) * self.var.cellArea , self.var.catchment)/self.var.area
            #self.var.sumDelta2 = 1000 * npareatotal((self.var.prevSnowCover + self.var.pretotalSoil + self.var.prestorGroundwater) * self.var.cellArea , self.var.catchment)/self.var.area
            #self.var.sumAll = self.var.sumDelta1- self.var.sumDelta2





            #report(decompress(self.var.sumRunoff), "C:\work\output3/sumRun.map")

            ii= 1



    def dynamic(self):
        """ dynamic part of the water balance module
        """
        if option['sumWaterBalance']:
            i = 1

        # sum up storage variables
        #for variable in self.var.sum_balanceStore:
         #   vars(self.var)["sumup_" + variable] =  vars(self.var)[variable].copy()


        # sum up fluxes variables
            for variable in self.var.sum_balanceFlux:
                vars(self.var)["sumup_" + variable] = vars(self.var)["sumup_" + variable] + vars(self.var)[variable]