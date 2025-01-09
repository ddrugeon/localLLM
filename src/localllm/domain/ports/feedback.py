from typing import Protocol


class TaskProgress(Protocol):
    """
    A protocol for tracking the progress of a task.

    This protocol is used to track the progress of a task. It is used to update the progress of a task and
    to give feedback when task is completed.
    """

    async def update_progress(self, task_id: str, percentage: float, message: str = "") -> None:
        """
        Update the progress of a task.

        :param task_id: An identifier for the task to track.
        :param percentage: The percentage of the task before completion.
        :param message: A message to display to the user.
        :return: None
        """
        pass

    async def complete(self) -> None:
        """Cleaning up resources if needed."""
        pass
