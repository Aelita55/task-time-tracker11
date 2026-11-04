"""
Модуль учёта времени (Time Tracking Module)
Базовые требования: старт/стоп, учёт времени, отчёты.
Доп. функции: множественные сессии, плановое время, экспорт в CSV/JSON.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import csv


class TimeLog:
    """Запись одной сессии работы над задачей"""

    def __init__(self, start_time: datetime,
                 end_time: Optional[datetime] = None):
        self.start_time = start_time
        self.end_time = end_time

    def stop(self):  
        """Остановка сессии"""
        if self.end_time is None:
            self.end_time = datetime.now()

    @property
    def duration(self) -> timedelta:
        """Длительность сессии"""
        end = self.end_time if self.end_time else datetime.now()
        return end - self.start_time


class TimeTracker:
    """Класс для управления таймерами и учётом времени"""

    def __init__(self):
        self.logs: Dict[int, List[TimeLog]] = {}
        self.active_timers: Dict[int, TimeLog] = {}
        self.estimated_times: Dict[int, timedelta] = {}

    def set_estimated_time(self, task_id: int, hours: float):
        """Установка планового времени (в часах)"""
        self.estimated_times[task_id] = timedelta(hours=hours)

    def start_timer(self, task_id: int):
        """Запуск таймера для задачи"""
        if task_id in self.active_timers:
            raise ValueError(f"Таймер для задачи {task_id} уже запущен.")
        log = TimeLog(datetime.now())
        self.logs.setdefault(task_id, []).append(log)
        self.active_timers[task_id] = log

    def stop_timer(self, task_id: int) -> timedelta:
        """Остановка таймера и возврат длительности"""
        if task_id not in self.active_timers:
            raise ValueError(f"Нет активного таймера для {task_id}.")
        self.active_timers[task_id].stop()
        duration = self.active_timers[task_id].duration
        del self.active_timers[task_id]
        return duration

    def get_total_time(self, task_id: int) -> timedelta:
        """Общее затраченное время (сумма всех сессий)"""
        logs = self.logs.get(task_id, [])
        return sum((log.duration for log in logs), timedelta())

    def generate_report(self, task_manager=None) -> Dict[str, Any]:
        """Генерация отчёта по времени"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "tasks": []
        }
        for task_id, logs in self.logs.items():
            total_time = self.get_total_time(task_id)
            task_info = {
                "task_id": task_id,
                "total_seconds": total_time.total_seconds(),
                "total_time_str": str(total_time),
                "sessions": len(logs)
            }
            if task_manager and task_id in task_manager.tasks:
                task_info["title"] = task_manager.tasks[task_id].title
            if task_id in self.estimated_times:
                estimated = self.estimated_times[task_id]
                task_info["estimated_seconds"] = estimated.total_seconds()
                task_info["deviation_seconds"] = (
                        total_time.total_seconds() - estimated.total_seconds()
                )
            report["tasks"].append(task_info)
        return report

    def export_to_json(self, filename: str, task_manager=None):
        """Экспорт отчёта в JSON"""
        report = self.generate_report(task_manager)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=4)

    def export_to_csv(self, filename: str, task_manager=None):
        """Экспорт отчёта в CSV"""
        report = self.generate_report(task_manager)
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["task_id", "title", "total_seconds",
                            "total_time_str", "sessions"]
            )
            writer.writeheader()
            for task in report["tasks"]:
                writer.writerow({k: task.get(k, "")
                                 for k in writer.fieldnames})
