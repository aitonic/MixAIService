# agent/agent.py
import asyncio


class Agent:
    def __init__(self, name: str):
        self.name = name
        self.tasks = []

    async def add_task(self, task: str):
        self.tasks.append(task)
        print(f"Agent {self.name}: Added task - {task}")

    async def run_tasks(self):
        print(f"Agent {self.name}: Running tasks...")
        for task in self.tasks:
            await self.execute_task(task)
        print(f"Agent {self.name}: All tasks completed.")

    async def execute_task(self, task: str):
        print(f"Agent {self.name}: Executing task - {task}")
        await asyncio.sleep(1)  # Simulate task execution

    def get_tasks(self) -> list[str]:
        return self.tasks
