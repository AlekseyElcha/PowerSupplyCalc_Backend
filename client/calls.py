
from PyQt6.QtCore import QThread, pyqtSignal
import re
import math

class CalculationWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, task='fetch', cpu_name=None, gpu_name=None, ram_name=None, ram_modules=1, storage_names=None, cooling_name=None, drive_name=None, motherboard_name=None, power_margin=20, api_base="http://localhost:8000"):
        super().__init__()
        self.task = task
        self.cpu_name = cpu_name
        self.gpu_name = gpu_name
        self.ram_name = ram_name
        self.ram_modules = ram_modules
        self.storage_names = storage_names or []
        self.cooling_name = cooling_name
        self.drive_name = drive_name
        self.motherboard_name = motherboard_name
        self.power_margin = power_margin
        self.api_base = api_base
        self._should_stop = False

    def stop(self):
        """Метод для корректной остановки потока"""
        self._should_stop = True

    @staticmethod
    def _parse_watt(s: str) -> int:
        if not s:
            return 0
        m = re.search(r"(\d+)", str(s))
        return int(m.group(1)) if m else 0

    def run(self):
        import requests
        try:
            if self._should_stop:
                return
            
            if self.task == 'fetch':
                cpus_resp = requests.get(f"{self.api_base}/cpus/", timeout=5)
                gpus_resp = requests.get(f"{self.api_base}/gpus/", timeout=5)
                rams_resp = requests.get(f"{self.api_base}/ram/", timeout=5)
                storages_resp = requests.get(f"{self.api_base}/storages/", timeout=5)
                cooling_resp = requests.get(f"{self.api_base}/cooling/", timeout=5)
                drives_resp = requests.get(f"{self.api_base}/drives/", timeout=5)
                motherboards_resp = requests.get(f"{self.api_base}/motherboards/", timeout=5)
                psus_resp = requests.get(f"{self.api_base}/psus/", timeout=5)

                cpus = cpus_resp.json().get("data", [])
                gpus = gpus_resp.json().get("data", [])
                rams = rams_resp.json().get("data", [])
                storages = storages_resp.json().get("data", [])
                cooling = cooling_resp.json().get("data", [])
                drives = drives_resp.json().get("data", [])
                motherboards = motherboards_resp.json().get("data", [])
                psus = psus_resp.json().get("data", [])

                if not self._should_stop:
                    self.finished.emit({
                        "cpus": cpus, "gpus": gpus, "rams": rams, "storages": storages, 
                        "cooling": cooling, "drives": drives, "motherboards": motherboards, "psus": psus
                    })
                return

            if self._should_stop:
                return
                
            if self.task == 'calc':
                cpus_resp = requests.get(f"{self.api_base}/cpus/", timeout=5)
                gpus_resp = requests.get(f"{self.api_base}/gpus/", timeout=5)
                rams_resp = requests.get(f"{self.api_base}/ram/", timeout=5)
                storages_resp = requests.get(f"{self.api_base}/storages/", timeout=5)
                cooling_resp = requests.get(f"{self.api_base}/cooling/", timeout=5)
                drives_resp = requests.get(f"{self.api_base}/drives/", timeout=5)
                motherboards_resp = requests.get(f"{self.api_base}/motherboards/", timeout=5)
                psus_resp = requests.get(f"{self.api_base}/psus/", timeout=5)

                cpus = cpus_resp.json().get("data", [])
                gpus = gpus_resp.json().get("data", [])
                rams = rams_resp.json().get("data", [])
                storages = storages_resp.json().get("data", [])
                cooling = cooling_resp.json().get("data", [])
                drives = drives_resp.json().get("data", [])
                motherboards = motherboards_resp.json().get("data", [])
                psus = psus_resp.json().get("data", [])

                def find_entry(entries, name):
                    if not name:
                        return None
                    for e in entries:
                        if e.get("name", "") == name:
                            return e
                    for e in entries:
                        if name.lower() in e.get("name", "").lower():
                            return e
                    return None

                cpu_entry = find_entry(cpus, self.cpu_name)
                gpu_entry = find_entry(gpus, self.gpu_name)
                ram_entry = find_entry(rams, self.ram_name)
                cooling_entry = find_entry(cooling, self.cooling_name)
                drive_entry = find_entry(drives, self.drive_name)
                motherboard_entry = find_entry(motherboards, self.motherboard_name)

                cpu_w = self._parse_watt(cpu_entry.get("consumption", "")) if cpu_entry else 0
                gpu_w = self._parse_watt(gpu_entry.get("consumption", "")) if gpu_entry else 0
                ram_w_single = self._parse_watt(ram_entry.get("consumption", "")) if ram_entry else 0
                ram_w = ram_w_single * self.ram_modules  # Умножаем на количество модулей
                cooling_w = int(cooling_entry.get("consumption", 0)) if cooling_entry else 0
                drive_w = int(drive_entry.get("consumption", 0)) if drive_entry else 0
                motherboard_w = int(motherboard_entry.get("consumption", 0)) if motherboard_entry else 0
                
                # Обрабатываем несколько дисков
                storage_w = 0
                storage_details = []
                for storage_name in self.storage_names:
                    if storage_name.strip():
                        storage_entry = find_entry(storages, storage_name)
                        if storage_entry:
                            storage_power = self._parse_watt(storage_entry.get("consumption", ""))
                            storage_w += storage_power
                            storage_details.append({
                                "name": storage_name,
                                "consumption": storage_power
                            })

                overhead = 200
                raw_total = cpu_w + gpu_w + ram_w + storage_w + cooling_w + drive_w + motherboard_w + overhead
                margin_multiplier = 1.0 + (self.power_margin / 100.0)  # Преобразуем проценты в множитель
                required = math.ceil(raw_total * margin_multiplier)

                psu_filtered = []
                for p in psus:
                    try:
                        watt = int(str(p.get("wattage", "")).strip())
                    except Exception:
                        watt = self._parse_watt(p.get("wattage", ""))
                    if watt >= required:
                        psu_filtered.append({"name": p.get("name", ""), "wattage": watt})

                psu_filtered.sort(key=lambda x: x["wattage"])
                top5 = psu_filtered[:5]

                if not self._should_stop:
                    self.finished.emit({
                        "required": required,
                        "cpu_w": cpu_w,
                        "gpu_w": gpu_w,
                        "ram_w": ram_w,
                        "ram_modules": self.ram_modules,
                        "ram_w_single": ram_w_single,
                        "storage_w": storage_w,
                        "storage_details": storage_details,
                        "cooling_w": cooling_w,
                        "drive_w": drive_w,
                        "motherboard_w": motherboard_w,
                        "overhead": overhead,
                        "power_margin": self.power_margin,
                        "raw_total": raw_total,
                        "psus": top5
                    })
                return

            if not self._should_stop:
                self.finished.emit({"error": f"Unknown task: {self.task}"})
        except Exception as e:
            if not self._should_stop:
                self.finished.emit({"error": str(e)})
