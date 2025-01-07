import asyncio


class Agent:
    def __init__(self, name: str) -> None:
        self.name = name
        self.tasks: list[str] = []

    async def add_task(self, task: str) -> None:
        """添加任务到任务列表。

        Args:
            task (str): 要添加的任务。

        """
        self.tasks.append(task)
        print(f"Agent {self.name}: Added task - {task}")

    async def run_tasks(self) -> None:
        """执行所有任务。"""
        print(f"Agent {self.name}: Running tasks...")
        for task in self.tasks:
            await self.execute_task(task)
        print(f"Agent {self.name}: All tasks completed.")

    async def execute_task(self, task: str) -> None:
        """执行单个任务。

        Args:
            task (str): 要执行的任务。

        """
        print(f"Agent {self.name}: Executing task - {task}")
        await asyncio.sleep(1)  # Simulate task execution

    def get_tasks(self) -> list[str]:
        """获取任务列表。

        Returns:
            List[str]: 当前的任务列表。

        """
        return self.tasks
