# -------------------------------------------------------------------------
# Name:        Sealed_water module
# Purpose:     runoff calculation for open water and sealed areas

# Author:      PB
#
# Created:     12/12/2016
# Copyright:   (c) PB 2016
# -------------------------------------------------------------------------

from cwatm.management_modules.data_handling import *


class sealed_water(object):
    """
    Sealed and open water runoff

    calculated runoff from impermeable surface (sealed) and into water bodies


    **Global variables**

    =====================================  ======================================================================  =====
    Variable [self.var]                    Description                                                             Unit 
    =====================================  ======================================================================  =====
    modflow                                Flag: True if modflow_coupling = True in settings file                  --   
    availWaterInfiltration                 quantity of water reaching the soil after interception, more snowmelt   m    
    EWRef                                  potential evaporation rate from water surface                           m    
    actualET                               simulated evapotranspiration from soil, flooded area and vegetation     m    
    directRunoff                           Simulated surface runoff                                                m    
    openWaterEvap                          Simulated evaporation from open areas                                   m    
    actTransTotal                          Total actual transpiration from the three soil layers                   m    
    actBareSoilEvap                        Simulated evaporation from the first soil layer                         m    
    capillar                               Flow from groundwater to the third CWATM soil layer. Used with MODFLOW  m    
    =====================================  ======================================================================  =====

    **Functions**
    """

    def __init__(self, model):
        self.var = model.var
        self.model = model

    def dynamic(self,coverType, No):
        """
        Dynamic part of the sealed_water module

        runoff calculation for open water and sealed areas
        """

        if No > 3:  # 4 = sealed areas, 5 = water
            if coverType == "water":
                # bigger than 1.0 because of wind evaporation
                mult = 1.0
            else:
                mult = 0.2  # evaporation from open areas on sealed area estimated as 0.2 EWRef

            if self.var.modflow:  # ModFlow Capillary rise under sealed areas and water bodies is sent to runoff
                self.var.openWaterEvap[No] = np.minimum(mult * self.var.EWRef,
                                                        self.var.availWaterInfiltration[No] + self.var.capillar)
                self.var.directRunoff[No] = self.var.availWaterInfiltration[No] \
                                            - self.var.openWaterEvap[No] + self.var.capillar
            else:
                self.var.openWaterEvap[No] =  np.minimum(mult * self.var.EWRef, self.var.availWaterInfiltration[No])
                self.var.directRunoff[No] = self.var.availWaterInfiltration[No] - self.var.openWaterEvap[No]

            # open water evaporation is directly subtracted from the rivers, lakes, and reservoirs
            self.var.actualET[No] = self.var.actualET[No] +  self.var.openWaterEvap[No]

        if checkOption('calcWaterBalance') and (No>3):
            self.model.waterbalance_module.waterBalanceCheck(
                [self.var.availWaterInfiltration[No] ],  # In
                [self.var.directRunoff[No], self.var.actTransTotal[No], self.var.actBareSoilEvap[No], self.var.openWaterEvap[No]],  # Out
                [globals.inZero],  # prev storage
                [globals.inZero],
                "NoSoil", False)


