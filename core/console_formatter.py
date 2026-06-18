class ConsoleFormatter:

    def __init__(self, analyser):
        self.a = analyser

    def general_info(self):
        lines = ["=====GENERAL INFO====="]

        electricity = "Available" if not self.a.data["runtime"]["isOffGrid"] else "Not Available"
        lines.append(f"Electricity: {electricity}")

        for key, value in self.a.general_info.items():
            lines.append(f"{key}: {value}")

        return "\n".join(lines)

    def electricity_info(self):
        generation = self.a.energy_generation_info
        consumption = self.a.energy_consumption_info

        lines = ["======ELECTRICITY======"]
        lines.append(f"Solar generation: {generation['Solar generation']} Wt")

        if "Grid energy" in generation:
            lines.append(f"Grid energy: {generation['Grid energy']} Wt {generation['Direction']}")
            r, s, t = generation["Grid R"], generation["Grid S"], generation["Grid T"]
            r_dir = "Export" if r > 0 else "Import" if r < 0 else "—"
            s_dir = "Export" if s > 0 else "Import" if s < 0 else "—"
            t_dir = "Export" if t > 0 else "Import" if t < 0 else "—"
            lines.append(f"  ├ R: {abs(r)} Wt ({r_dir})")
            lines.append(f"  ├ S: {abs(s)} Wt ({s_dir})")
            lines.append(f"  └ T: {abs(t)} Wt ({t_dir})")
        lines.append(f"Consumption: {consumption['Consumption']} Wt")
        c_r, c_s, c_t = consumption["Consumption R"], consumption["Consumption S"], consumption["Consumption T"]
        lines.append(f"  ├ R: {abs(c_r)} Wt")
        lines.append(f"  ├ S: {abs(c_s)} Wt")
        lines.append(f"  └ T: {abs(c_t)} Wt")
        lines.append(f"Battery charging: {consumption['Battery charging']} Wt")

        return "\n".join(lines)

    def today_info(self):
        lines = ["========TODAY========="]
        for key, value in self.a.today_info.items():
            lines.append(f"{key}: {value} kWt")

        return "\n".join(lines)

    def total_info(self):
        lines = ["========TOTAL========="]
        for key, value in self.a.total_info.items():
            lines.append(f"{key}: {value} kWt")

        return "\n".join(lines)
