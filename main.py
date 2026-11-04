"""
Главный файл системы управления задачами с интегрированным модулем учёта времени.
Содержит: базовые классы из лекции (разделы 2.2 и 2.3) + интеграцию с time_tracker.
"""
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

from time_tracker import TimeTracker


#Базовые классы

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class Status(Enum):
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    REVIEW = "Review"
    DONE = "Done"


class User:
    def __init__(self, user_id: int, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email

    def __str__(self):
        return f"User({self.name}, {self.email})"


class Task:
    def __init__(self, task_id: int, title: str, description: str,
                 priority: Priority, due_date: datetime):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.status = Status.TODO
        self.assignee: Optional[User] = None
        self.created_at = datetime.now()

    def assign_to(self, user: User):
        """Назначение задачи пользователю"""
        self.assignee = user
        self.status = Status.IN_PROGRESS

    def update_status(self, new_status: Status):
        """Обновление статуса задачи"""
        self.status = new_status

    def is_overdue(self) -> bool:
        """Проверка просрочки задачи"""
        return datetime.now() > self.due_date

    def __str__(self):
        return f"Task '{self.title}' ({self.status.value})"


#Менеджер задачи + интеграция

class TaskManager:
    """Класс для управления задачами с интегрированным модулем времени"""
    def __init__(self):
        self.tasks: Dict[int, Task] = {}
        self.users: Dict[int, User] = {}
        self.next_task_id = 1
        self.next_user_id = 1
        self.time_tracker = TimeTracker()  # интеграция с модулем времени

    def create_user(self, name: str, email: str) -> User:
        """Создание нового пользователя"""
        user = User(self.next_user_id, name, email)
        self.users[self.next_user_id] = user
        self.next_user_id += 1
        return user

    def create_task(self, title: str, description: str,
                   priority: Priority, due_date: datetime) -> Task:
        """Создание новой задачи"""
        task = Task(self.next_task_id, title, description, priority, due_date)
        self.tasks[self.next_task_id] = task
        self.next_task_id += 1
        return task

    def assign_task(self, task_id: int, user_id: int) -> bool:
        """Назначение задачи пользователю"""
        task = self.tasks.get(task_id)
        user = self.users.get(user_id)
        if task and user:
            task.assign_to(user)
            return True
        return False

    def get_overdue_tasks(self) -> List[Task]:
        """Получение списка просроченных задач"""
        return [task for task in self.tasks.values() if task.is_overdue()]

    def get_user_tasks(self, user_id: int) -> List[Task]:
        """Получение задач конкретного пользователя"""
        return [task for task in self.tasks.values()
                if task.assignee and task.assignee.user_id == user_id]

    def generate_report(self) -> Dict:
        """Генерация отчёта по задачам"""
        total_tasks = len(self.tasks)
        overdue_tasks = len(self.get_overdue_tasks())
        status_count = {}
        for task in self.tasks.values():
            status_count[task.status] = status_count.get(task.status, 0) + 1
        return {
            "total_tasks": total_tasks,
            "overdue_tasks": overdue_tasks,
            "status_distribution": {status.value: count for status, count in status_count.items()},
            "report_generated_at": datetime.now().isoformat()
        }

    #Новые методы: интеграция с модулем времени
    def set_estimated_time(self, task_id: int, hours: float):
        self.time_tracker.set_estimated_time(task_id, hours)

    def start_timer(self, task_id: int):
        if task_id not in self.tasks:
            raise ValueError("Задача не найдена")
        self.time_tracker.start_timer(task_id)

    def stop_timer(self, task_id: int):
        return self.time_tracker.stop_timer(task_id)

    def generate_time_report(self):
        return self.time_tracker.generate_report(self)

    def export_time_reports(self):
        self.time_tracker.export_to_json("time_report.json", self)
        self.time_tracker.export_to_csv("time_report.csv", self)

    def export_time_reports(self):
        self.time_tracker.export_to_json("time_report.json", self)
        self.time_tracker.export_to_csv("time_report.csv", self)


# Демонтстрация работы
def demo_implementation():
    manager = TaskManager()

    # 1. Создание пользователей и задач
    developer = manager.create_user("Алексей Кодлов", "alexey@company.com")
    tester = manager.create_user("Елена Тестова", "elena@company.com")

    task1 = manager.create_task(
        "Разработать REST API",
        "Создать API для управления задачами",
        Priority.HIGH,
        datetime.now() + timedelta(days=14)
    )
    task2 = manager.create_task(
        "Написать unit-тесты",
        "Покрыть код модульными тестами",
        Priority.MEDIUM,
        datetime.now() + timedelta(days=7)
    )

    manager.assign_task(task1.task_id, developer.user_id)
    manager.assign_task(task2.task_id, tester.user_id)

    # 2. Отчёт по задачам
    print("Отчёт по задачам:")
    report = manager.generate_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))

    # 3. Плановое время
    manager.set_estimated_time(task1.task_id, hours=2.0)
    manager.set_estimated_time(task2.task_id, hours=1.0)

    # 4. Работа с таймерами
    print("\nЗапуск таймеров...")
    manager.start_timer(task1.task_id)
    time.sleep(1.5)
    manager.stop_timer(task1.task_id)

    manager.start_timer(task2.task_id)
    time.sleep(1.0)
    manager.stop_timer(task2.task_id)

    # Повторный запуск для task1 (множественные сессии)
    manager.start_timer(task1.task_id)
    time.sleep(0.5)
    manager.stop_timer(task1.task_id)

    # 5. Отчёт по времени
    print("\nОтчёт по времени:")
    time_report = manager.generate_time_report()
    print(json.dumps(time_report, indent=2, ensure_ascii=False))

    # 6. Экспорт в файлы
    manager.export_time_reports()
    print("\nОтчёты экспортированы в time_report.json и time_report.csv")


if __name__ == "__main__":
    demo_implementation()
