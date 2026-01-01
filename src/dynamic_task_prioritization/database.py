"""MongoDB database operations for task priority data."""

import os
from datetime import datetime
from typing import Dict, List, Optional
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, PyMongoError


class MongoDBHandler:
    """Handle MongoDB operations for task priority storage."""

    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize MongoDB connection.

        Args:
            connection_string: MongoDB connection URI. If None, reads from MONGODB_URI env variable.

        Raises:
            ValueError: If connection string is not provided
            ConnectionFailure: If connection to MongoDB fails
        """
        self.connection_string = connection_string or os.getenv("MONGODB_URI")

        if not self.connection_string:
            raise ValueError(
                "MongoDB connection string not provided. "
                "Set MONGODB_URI environment variable or pass connection_string parameter."
            )

        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            print("[OK] Successfully connected to MongoDB")

            # Set database and collection
            self.db = self.client['research_task_db']
            self.tasks_collection = self.db['tasks']

            # Create indexes for better query performance
            self._create_indexes()

        except ConnectionFailure as e:
            raise ConnectionFailure(f"Failed to connect to MongoDB: {e}")
        except Exception as e:
            raise Exception(f"Error initializing MongoDB: {e}")

    def _create_indexes(self):
        """Create indexes for efficient querying."""
        try:
            # Index on priority for quick filtering
            self.tasks_collection.create_index([("priority", ASCENDING)])

            # Index on deadline for time-based queries
            self.tasks_collection.create_index([("metrics.deadline", ASCENDING)])

            # Index on created_at for chronological queries
            self.tasks_collection.create_index([("created_at", ASCENDING)])

            # Index on final_weighted_score for sorting
            self.tasks_collection.create_index([("mcdm_calculation.final_weighted_score", ASCENDING)])

        except PyMongoError as e:
            print(f"Warning: Failed to create indexes: {e}")

    def save_task(self, task_data: Dict) -> str:
        """
        Save a single task to MongoDB.

        Args:
            task_data: Dictionary containing task information with structure:
                {
                    "task_name": str,
                    "task_description": str,
                    "sub_tasks": List[str],
                    "context": str,
                    "metrics": {
                        "deadline": str,
                        "days_left": int,
                        "credits": int,
                        "percentage": int,
                        "difficulty_rating": int
                    },
                    "mcdm_calculation": {
                        "urgency_score": int,
                        "impact_score": int,
                        "difficulty_score": int,
                        "final_weighted_score": float
                    },
                    "priority": str
                }

        Returns:
            str: The inserted document's ID

        Raises:
            PyMongoError: If database operation fails
        """
        try:
            # Add timestamp
            task_data['created_at'] = datetime.utcnow()
            task_data['updated_at'] = datetime.utcnow()

            # Insert into MongoDB
            result = self.tasks_collection.insert_one(task_data)

            print(f"[OK] Task saved to MongoDB with ID: {result.inserted_id}")
            return str(result.inserted_id)

        except PyMongoError as e:
            raise PyMongoError(f"Failed to save task to MongoDB: {e}")

    def save_multiple_tasks(self, tasks_data: List[Dict]) -> List[str]:
        """
        Save multiple tasks to MongoDB.

        Args:
            tasks_data: List of task dictionaries

        Returns:
            List[str]: List of inserted document IDs

        Raises:
            PyMongoError: If database operation fails
        """
        try:
            # Add timestamps to all tasks
            current_time = datetime.utcnow()
            for task in tasks_data:
                task['created_at'] = current_time
                task['updated_at'] = current_time

            # Insert into MongoDB
            result = self.tasks_collection.insert_many(tasks_data)

            inserted_ids = [str(id) for id in result.inserted_ids]
            print(f"[OK] {len(inserted_ids)} tasks saved to MongoDB")
            return inserted_ids

        except PyMongoError as e:
            raise PyMongoError(f"Failed to save tasks to MongoDB: {e}")

    def get_all_tasks(self, limit: int = 100) -> List[Dict]:
        """
        Retrieve all tasks from MongoDB.

        Args:
            limit: Maximum number of tasks to retrieve (default: 100)

        Returns:
            List[Dict]: List of task documents
        """
        try:
            tasks = list(self.tasks_collection.find().sort("created_at", -1).limit(limit))

            # Convert ObjectId to string for JSON serialization
            for task in tasks:
                task['_id'] = str(task['_id'])

            return tasks

        except PyMongoError as e:
            print(f"Error retrieving tasks: {e}")
            return []

    def get_tasks_by_priority(self, priority: str) -> List[Dict]:
        """
        Retrieve tasks filtered by priority level.

        Args:
            priority: Priority level ("High", "Medium", "Low")

        Returns:
            List[Dict]: List of matching task documents
        """
        try:
            tasks = list(
                self.tasks_collection.find({"priority": priority})
                .sort("mcdm_calculation.final_weighted_score", -1)
            )

            # Convert ObjectId to string
            for task in tasks:
                task['_id'] = str(task['_id'])

            return tasks

        except PyMongoError as e:
            print(f"Error retrieving tasks by priority: {e}")
            return []

    def get_upcoming_tasks(self, days_threshold: int = 7) -> List[Dict]:
        """
        Retrieve tasks with deadlines within the specified number of days.

        Args:
            days_threshold: Number of days to look ahead (default: 7)

        Returns:
            List[Dict]: List of upcoming task documents
        """
        try:
            tasks = list(
                self.tasks_collection.find({"metrics.days_left": {"$lte": days_threshold}})
                .sort("metrics.days_left", ASCENDING)
            )

            # Convert ObjectId to string
            for task in tasks:
                task['_id'] = str(task['_id'])

            return tasks

        except PyMongoError as e:
            print(f"Error retrieving upcoming tasks: {e}")
            return []

    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task by its ID.

        Args:
            task_id: The task's MongoDB ObjectId as string

        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            from bson.objectid import ObjectId
            result = self.tasks_collection.delete_one({"_id": ObjectId(task_id)})

            if result.deleted_count > 0:
                print(f"[OK] Task {task_id} deleted successfully")
                return True
            else:
                print(f"Warning: No task found with ID {task_id}")
                return False

        except Exception as e:
            print(f"Error deleting task: {e}")
            return False

    def get_task_statistics(self) -> Dict:
        """
        Get statistics about stored tasks.

        Returns:
            Dict: Statistics including total count, priority breakdown, etc.
        """
        try:
            total = self.tasks_collection.count_documents({})
            high_priority = self.tasks_collection.count_documents({"priority": "High"})
            medium_priority = self.tasks_collection.count_documents({"priority": "Medium"})
            low_priority = self.tasks_collection.count_documents({"priority": "Low"})

            return {
                "total_tasks": total,
                "high_priority": high_priority,
                "medium_priority": medium_priority,
                "low_priority": low_priority
            }

        except PyMongoError as e:
            print(f"Error getting statistics: {e}")
            return {}

    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            print("[OK] MongoDB connection closed")
