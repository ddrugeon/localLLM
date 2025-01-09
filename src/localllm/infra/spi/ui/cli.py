from tqdm import tqdm

from localllm.domain.ports.feedback import TaskProgress


class CLITaskProgress(TaskProgress):
    def __init__(self, task_id: str, silent: bool = True):
        self.progress_bar = tqdm(total=100, desc=f"Task {task_id}", unit="%", position=0, leave=False)
        self.silent = silent

    async def update_progress(self, task_id: str, percentage: float, message: str = "") -> None:
        """
        Update the progress of a task.

        :param task_id: An identifier for the task to track.
        :param percentage: The percentage of the task before completion.
        :param message: A message to display to the user.
        :return: None
        """
        if self.silent:
            return

        self.progress_bar.n = int(percentage)
        if message:
            self.progress_bar.set_description(message)
        self.progress_bar.refresh()

    async def complete(self) -> None:
        """Cleaning up resources if needed."""
        self.progress_bar.close()
