class TelegramFormatter:
    def __init__(self, analyser):
        self.a = analyser

    def general_info(self):
        info = self.a.general_info
        electricity = "🟢 Available" if not self.a.data["runtime"]["isOffGrid"] else "🔴 NOT available"
        return (
            "<b>⚡ GENERAL INFO</b>\n"
            f"Electricity: {electricity}\n"
            f"Last update: <code>{info['Last update']}</code>\n"
            f"SOC: <code>{info['State of Charge']}</code>\n"
            f"Battery temp: <code>{info['Battery temperature, °C']}°C</code>"
        )

    def runtime_info(self):
        generation = self.a.energy_generation_info
        consumption = self.a.energy_consumption_info

        text = "<b>🔌 ELECTRICITY</b>\n"
        text += f"Solar: <code>{generation['Solar generation']} Wt</code>\n"

        if "Grid energy" in generation:
            text += f"Grid: <code>{generation['Grid energy']} Wt</code> ({generation['Direction']})\n"
            
            r, s, t = generation["Grid R"], generation["Grid S"], generation["Grid T"]
            r_dir = "Export" if r > 0 else "Import" if r < 0 else "—"
            s_dir = "Export" if s > 0 else "Import" if s < 0 else "—"
            t_dir = "Export" if t > 0 else "Import" if t < 0 else "—"
            
            text += f"  ├ R: <code>{abs(r)} Wt</code> ({r_dir})\n"
            text += f"  ├ S: <code>{abs(s)} Wt</code> ({s_dir})\n"
            text += f"  └ T: <code>{abs(t)} Wt</code> ({t_dir})\n"

        text += f"Consumption: <code>{consumption['Consumption']} Wt</code>\n"
        
        c_r, c_s, c_t = consumption["Consumption R"], consumption["Consumption S"], consumption["Consumption T"]
        text += f"  ├ R: <code>{abs(c_r)} Wt</code>\n"
        text += f"  ├ S: <code>{abs(c_s)} Wt</code>\n"
        text += f"  └ T: <code>{abs(c_t)} Wt</code>\n"

        text += f"Battery: <code>{consumption['Battery charging']} Wt</code>"

        return text

    def today_info(self):
        today = self.a.today_info
        return (
            "<b>📅 TODAY</b>\n"
            f"Yield: <code>{today['Yield']} kWt</code>\n"
            f"Export: <code>{today['Export']} kWt</code>\n"
            f"Import: <code>{today['Import']} kWt</code>\n"
            f"Consumed: <code>{today['Consumed']} kWt</code>"
        )

    def total_info(self):
        total = self.a.total_info
        return (
            "<b>📊 TOTAL</b>\n"
            f"Yield: <code>{total['Yield']} MWt</code>\n"
            f"Export: <code>{total['Export']} MWt</code>\n"
            f"Import: <code>{total['Import']} MWt</code>\n"
            f"Consumed: <code>{total['Consumed']} MWt</code>"
        )