class DataAnalyzer:

    def __init__(self, data: dict):
        self.data = data

    @property
    def general_info(self):
        general_data = {}
        general_data["Last update"] = self.data["batteryInfo"]["time"]
        general_data["State of Charge"] = self.data["batteryInfo"]["soc"]
        general_data["Battery temperature, °C"] = self.data["batteryInfo"]["tBat"]
        return general_data

    @property
    def energy_generation_info(self):
        energy_generation_data = {}
        if not self.data["runtime"]["isOffGrid"]:
            energy_generation_data["Solar generation"] = self.data["runtime"]["ppv"]
            energy_generation_data["Grid energy"] = self.data["runtime"]["gridPowerr"] + self.data["runtime"]["gridPowers"] + self.data["runtime"]["gridPowert"]
            if energy_generation_data["Grid energy"] > 0:
                energy_generation_data["Direction"] = "Export"
            else:
                energy_generation_data["Direction"] = "Import"
                energy_generation_data["Grid energy"] = abs(energy_generation_data["Grid energy"])
        else:
            energy_generation_data["Solar generation"] = self.data["runtime"]["ppv"]
        return energy_generation_data

    @property
    def energy_consumption_info(self):
        energy_consumption_data = {}
        if not self.data["runtime"]["isOffGrid"]:
            energy_consumption_data["Consumption"] = self.data["runtime"]["pLoadr"] + self.data["runtime"]["pLoads"] + self.data["runtime"]["pLoadt"]
            energy_consumption_data["Battery charging"] = self.data["runtime"]["batPower"]
        else:
            energy_consumption_data["Consumption"] = self.data["runtime"]["pepsr"] + self.data["runtime"]["pepss"] + self.data["runtime"]["pepst"]
            energy_consumption_data["Battery charging"] = self.data["runtime"]["batPower"]
        return energy_consumption_data

    @property
    def today_info(self):
        today_data = {}
        today_data["Yield"] = self.data["energy"]["todayYielding"]/10
        today_data["Export"] = self.data["energy"]["todayExport"]/10
        today_data["Import"] = self.data["energy"]["todayImport"]/10
        today_data["Consumed"] = self.data["energy"]["todayUsage"]/10
        return today_data

    @property
    def total_info(self):
        total_data = {}
        total_data["Yield"] = round(self.data["energy"]["totalYielding"]/10000, 2)
        total_data["Export"] = round(self.data["energy"]["totalExport"]/10000, 2)
        total_data["Import"] = round(self.data["energy"]["totalImport"]/10000, 2)
        total_data["Consumed"] = round(self.data["energy"]["totalUsage"]/10000, 2)
        return total_data
