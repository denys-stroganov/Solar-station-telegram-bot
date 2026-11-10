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
            
            grid_r = self.data["runtime"]["gridPowerr"]
            grid_s = self.data["runtime"]["gridPowers"]
            grid_t = self.data["runtime"]["gridPowert"]
            
            energy_generation_data["Grid R"] = grid_r
            energy_generation_data["Grid S"] = grid_s
            energy_generation_data["Grid T"] = grid_t
            
            grid_sum = grid_r + grid_s + grid_t
            energy_generation_data["Grid energy"] = grid_sum
            if grid_sum > 0:
                energy_generation_data["Direction"] = "Export"
            else:
                energy_generation_data["Direction"] = "Import"
                energy_generation_data["Grid energy"] = abs(grid_sum)
        else:
            energy_generation_data["Solar generation"] = self.data["runtime"]["ppv"]
        return energy_generation_data

    @property
    def energy_consumption_info(self):
        energy_consumption_data = {}
        if not self.data["runtime"]["isOffGrid"]:
            r = self.data["runtime"]["pLoadr"]
            s = self.data["runtime"]["pLoads"]
            t = self.data["runtime"]["pLoadt"]
        else:
            r = self.data["runtime"]["pepsr"]
            s = self.data["runtime"]["pepss"]
            t = self.data["runtime"]["pepst"]
            
        energy_consumption_data["Consumption R"] = r
        energy_consumption_data["Consumption S"] = s
        energy_consumption_data["Consumption T"] = t
        energy_consumption_data["Consumption"] = r + s + t
        energy_consumption_data["Battery charging"] = self.data["runtime"]["batPower"]
        return energy_consumption_data

    @property
    def voltage_info(self):
        voltage_data = {}
        runtime = self.data.get("runtime", {})
        if not runtime.get("isOffGrid", True):
            voltage_data["Voltage R"] = round((runtime.get("vacr") or 0) / 10, 1)
            voltage_data["Voltage S"] = round((runtime.get("vacs") or 0) / 10, 1)
            voltage_data["Voltage T"] = round((runtime.get("vact") or 0) / 10, 1)
            voltage_data["Frequency R"] = round((runtime.get("facr") or 0) / 100, 2)
            voltage_data["Frequency S"] = round((runtime.get("facs") or 0) / 100, 2)
            voltage_data["Frequency T"] = round((runtime.get("fact") or 0) / 100, 2)
        return voltage_data

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
