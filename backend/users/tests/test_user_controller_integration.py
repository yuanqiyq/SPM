import unittest
import json
import sys
import os
import uuid

# Add parent directory to path to find modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.user_service import UserService
from models.user import User
from repo.supa_user_repo import SupabaseUserRepo

# Import the controller and service
from controllers.user_controller import user_bp, service


class TestUserControllerIntegration(unittest.TestCase):
    """Integration tests for user controller endpoints."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Set up environment variables for Supabase connection
        # You'll need to set these in your environment or .env file
        if not os.getenv("SUPABASE_URL"):
            os.environ["SUPABASE_URL"] = "your_supabase_url_here"
        if not os.getenv("SUPABASE_SERVICE_KEY"):
            os.environ["SUPABASE_SERVICE_KEY"] = "your_supabase_service_key_here"
        
        # Test Supabase connection
        try:
            self.repo = SupabaseUserRepo()
            print(f"[SUCCESS] Supabase connection successful")
        except Exception as e:
            print(f"[ERROR] Supabase connection failed: {e}")
            raise
        
        # Replace the service's repository with our real repository
        service.repo = self.repo

        # Create a test Flask app
        from flask import Flask
        self.app = Flask(__name__)
        self.app.register_blueprint(user_bp)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Clean up any existing test data
        self.cleanup_test_data()

    def tearDown(self):
        """Clean up after each test method."""
        self.cleanup_test_data()

    def cleanup_test_data(self):
        """Clean up test data from the database."""
        try:
            # Delete test users for common test userids
            test_userids = [9999, 9998, 9997, 9996, 9995]  # Common test userids
            deleted_count = 0
            
            for userid in test_userids:
                # Get user for this userid
                user_data = self.repo.get_user_by_userid(userid)
                if user_data:
                    print(f"Found user with userid {userid}")
                    
                    # Delete user (assuming there's a delete method or we can use update to mark as deleted)
                    # For now, we'll just log that we found test data
                    print(f"Test user with userid {userid} found - manual cleanup may be needed")
                    deleted_count += 1
            
            if deleted_count > 0:
                print(f"Cleanup completed: {deleted_count} test users found")
            else:
                print("No test users found to clean up")
                
        except Exception as e:
            print(f"Warning: Could not clean up test data: {e}")
            import traceback
            traceback.print_exc()

    # # ==================== create_user Tests ====================
    
    # def test_create_user_success(self):
    #     """Test successful user creation with all required fields."""
    #     # Clean up any existing test data first
    #     self.cleanup_test_data()
        
    #     # Make request with required fields
    #     user_id = "2d1ad2e0-27aa-45c1-8e10-4c1b218c8f5d"
    #     response = self.client.post('/users', json={
    #         "id": user_id,
    #         "userid": 9999,
    #         "role": "manager",
    #         "name": "Test User",
    #         "email": "test.user@example.com"
    #     })
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 201)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["status"], 201)
    #     self.assertIn("User 9999 created successfully", data["message"])
    #     self.assertIn("data", data)
    #     self.assertEqual(data["data"]["userid"], 9999)
    #     self.assertEqual(data["data"]["name"], "Test User")
    #     self.assertEqual(data["data"]["email"], "test.user@example.com")

    # def test_create_user_with_optional_fields(self):
    #     """Test user creation with optional fields."""
    #     # Clean up any existing test data first
    #     self.cleanup_test_data()
        
    #     # Make request with all fields
    #     user_id = "2d1ad2e0-27aa-45c1-8e10-4c1b218c8f5d"
    #     response = self.client.post('/users', json={
    #         "id": user_id,
    #         "userid": 9998,
    #         "role": "staff",
    #         "name": "Complete User",
    #         "email": "complete.user@example.com",
    #         "team_id": 1,
    #         "dept_id": 2,
    #         "notification_preferences": {"in_app": True, "email": False}
    #     })
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 201)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["status"], 201)
    #     self.assertEqual(data["data"]["userid"], 9998)
    #     self.assertEqual(data["data"]["team_id"], 1)
    #     self.assertEqual(data["data"]["dept_id"], 2)
    #     self.assertEqual(data["data"]["notification_preferences"]["in_app"], True)
    #     self.assertEqual(data["data"]["notification_preferences"]["email"], False)

    # def test_create_user_missing_id(self):
    #     """Test user creation fails when id is missing."""
    #     response = self.client.post('/users', json={
    #         "userid": 9999,
    #         "role": "manager",
    #         "name": "Test User",
    #         "email": "test.user@example.com"
    #         # id is missing
    #     })
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 400)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["status"], 400)
    #     self.assertIn("Missing required fields", data["message"])

    # def test_create_user_missing_userid(self):
    #     """Test user creation fails when userid is missing."""
    #     user_id = "2d1ad2e0-27aa-45c1-8e10-4c1b218c8f5d"
    #     response = self.client.post('/users', json={
    #         "id": user_id,
    #         "role": "manager",
    #         "name": "Test User",
    #         "email": "test.user@example.com"
    #         # userid is missing
    #     })
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 400)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["status"], 400)
    #     self.assertIn("Missing required fields", data["message"])

    # def test_create_user_missing_role(self):
    #     """Test user creation fails when role is missing."""
    #     user_id = "2d1ad2e0-27aa-45c1-8e10-4c1b218c8f5d"
    #     response = self.client.post('/users', json={
    #         "id": user_id,
    #         "userid": 9999,
    #         "name": "Test User",
    #         "email": "test.user@example.com"
    #         # role is missing
    #     })
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 400)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["status"], 400)
    #     self.assertIn("Missing required fields", data["message"])

    # def test_create_user_missing_name(self):
    #     """Test user creation fails when name is missing."""
    #     user_id = "2d1ad2e0-27aa-45c1-8e10-4c1b218c8f5d"
    #     response = self.client.post('/users', json={
    #         "id": user_id,
    #         "userid": 9999,
    #         "role": "manager",
    #         "email": "test.user@example.com"
    #         # name is missing
    #     })
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 400)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["status"], 400)
    #     self.assertIn("Missing required fields", data["message"])

    # def test_create_user_missing_email(self):
    #     """Test user creation fails when email is missing."""
    #     user_id = "2d1ad2e0-27aa-45c1-8e10-4c1b218c8f5d"
    #     response = self.client.post('/users', json={
    #         "id": user_id,
    #         "userid": 9999,
    #         "role": "manager",
    #         "name": "Test User"
    #         # email is missing
    #     })
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 400)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["status"], 400)
    #     self.assertIn("Missing required fields", data["message"])

    # def test_create_user_with_unicode_content(self):
    #     """Test user creation with unicode characters."""
    #     # Clean up any existing test data first
    #     self.cleanup_test_data()
        
    #     user_id = "2d1ad2e0-27aa-45c1-8e10-4c1b218c8f5d"
    #     unicode_name = "张三李四"
    #     unicode_email = "张三@example.com"
        
    #     response = self.client.post('/users', json={
    #         "id": user_id,
    #         "userid": 9997,
    #         "role": "staff",
    #         "name": unicode_name,
    #         "email": unicode_email
    #     })
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 201)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["status"], 201)
    #     self.assertEqual(data["data"]["name"], unicode_name)
    #     self.assertEqual(data["data"]["email"], unicode_email)

    # ==================== get_user_by_userid Tests ====================
    
    def test_get_user_success(self):
        """Test successfully retrieving a user by userid."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # # First, create a user
        # user_id = "2d1ad2e0-27aa-45c1-8e10-4c1b218c8f5d"
        # create_response = self.client.post('/users', json={
        #     "id": user_id,
        #     "userid": 9996,
        #     "role": "manager",
        #     "name": "Test User",
        #     "email": "test.user@example.com"
        # })
        # self.assertEqual(create_response.status_code, 201)
        
        # Make request
        response = self.client.get('/users/297')
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertIn("data", data)
        self.assertEqual(data["data"]["userid"], 297)

    def test_get_user_not_found(self):
        """Test get user when user doesn't exist."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request with non-existent user
        response = self.client.get('/users/99999')
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 404)
        self.assertIn("User with userid 99999 not found", data["message"])

    def test_get_user_invalid_userid(self):
        """Test get user with invalid userid format."""
        # Make request with invalid userid
        response = self.client.get('/users/invalid')
        
        # Assertions - should return 404 due to Flask routing
        self.assertEqual(response.status_code, 404)


    # ==================== update_user_by_userid Tests ====================
    
    def test_update_user_success(self):
        """Test successful user update."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # # First, create a user
        # user_id = "2d1ad2e0-27aa-45c1-8e10-4c1b218c8f5d"
        # create_response = self.client.post('/users', json={
        #     "id": user_id,
        #     "userid": 9994,
        #     "role": "staff",
        #     "name": "Original Name",
        #     "email": "original@example.com"
        # })
        # self.assertEqual(create_response.status_code, 201)
        
        # Update the user
        response = self.client.put('/users/297', json={
            "role": "manager"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertIn("User 297 updated successfully", data["message"])
        self.assertEqual(data["data"]["role"], "manager")


    def test_update_user_no_fields(self):
        """Test user update fails when no fields provided."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Try to update without any fields
        response = self.client.put('/users/297', json={})
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 400)
        self.assertIn("No valid fields to update provided", data["message"])

    def test_update_user_not_found(self):
        """Test update user fails when user doesn't exist."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request with non-existent user
        response = self.client.put('/users/99999', json={
            "name": "Updated Name"
        })
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 404)
        self.assertIn("User with userid 99999 not found", data["message"])

    def test_update_user_with_team_dept(self):
        """Test user update with team_id and dept_id."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Update with team and department
        response = self.client.put('/users/297', json={
            "team_id": 12,
            "dept_id": 6
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["data"]["team_id"], 12)
        self.assertEqual(data["data"]["dept_id"], 6)

    # # ==================== get_users_by_dept_id Tests ====================
    
    # def test_get_users_by_dept_success(self):
    #     """Test successfully retrieving users by department ID."""
    #     # Clean up any existing test data first
    #     self.cleanup_test_data()
        
    #     # Make request
    #     response = self.client.get('/users/department/1')
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["status"], 200)
    #     self.assertIn("data", data)

    # def test_get_users_by_dept_not_found(self):
    #     """Test get users by department when no users found."""
    #     # Clean up any existing test data first
    #     self.cleanup_test_data()
        
    #     # Make request for department with no users
    #     response = self.client.get('/users/department/999')
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["status"], 200)
    #     self.assertIn("No users found for department ID 999", data["message"])
    #     self.assertEqual(data["data"], [])

    # def test_get_users_by_dept_invalid_id(self):
    #     """Test get users by department with invalid ID format."""
    #     # Make request with invalid department ID
    #     response = self.client.get('/users/department/invalid')
        
    #     # Assertions - should return 404 due to Flask routing
    #     self.assertEqual(response.status_code, 404)

    # # ==================== get_users_by_team_id Tests ====================
    
    # def test_get_users_by_team_success(self):
    #     """Test successfully retrieving users by team ID."""
    #     # Clean up any existing test data first
    #     self.cleanup_test_data()
        
    #     # First, create users in the same team
    #     user_id1 = "2d1ad2e0-27aa-45c1-8e10-4c1b218c8f5d"
    #     user_id2 = "670dad0b-09e7-4624-a61a-8007b549d2fc"
        
    #     create_response1 = self.client.post('/users', json={
    #         "id": user_id1,
    #         "userid": 9988,
    #         "role": "staff",
    #         "name": "Team User 1",
    #         "email": "teamuser1@example.com",
    #         "team_id": 20
    #     })
    #     self.assertEqual(create_response1.status_code, 201)
        
    #     create_response2 = self.client.post('/users', json={
    #         "id": user_id2,
    #         "userid": 9987,
    #         "role": "lead",
    #         "name": "Team User 2",
    #         "email": "teamuser2@example.com",
    #         "team_id": 20
    #     })
    #     self.assertEqual(create_response2.status_code, 201)
        
    #     # Make request
    #     response = self.client.get('/users/team/20')
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["status"], 200)
    #     self.assertIn("Retrieved 2 user(s) for team ID 20", data["message"])
    #     self.assertIn("data", data)
    #     self.assertEqual(len(data["data"]), 2)

    # def test_get_users_by_team_not_found(self):
    #     """Test get users by team when no users found."""
    #     # Clean up any existing test data first
    #     self.cleanup_test_data()
        
    #     # Make request for team with no users
    #     response = self.client.get('/users/team/999')
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["status"], 200)
    #     self.assertIn("No users found for team ID 999", data["message"])
    #     self.assertEqual(data["data"], [])

    # def test_get_users_by_team_invalid_id(self):
    #     """Test get users by team with invalid ID format."""
    #     # Make request with invalid team ID
    #     response = self.client.get('/users/team/invalid')
        
    #     # Assertions - should return 404 due to Flask routing
    #     self.assertEqual(response.status_code, 404)

    # ==================== search_users_by_email Tests ====================
    
    # def test_search_users_by_email_success(self):
    #     """Test successfully searching users by email."""
    #     # Clean up any existing test data first
    #     self.cleanup_test_data()
        
    #     # # First, create users with similar emails
    #     # user_id1 = "2d1ad2e0-27aa-45c1-8e10-4c1b218c8f5d"
    #     # user_id2 = "670dad0b-09e7-4624-a61a-8007b549d2fc"
        
    #     # create_response1 = self.client.post('/users', json={
    #     #     "id": user_id1,
    #     #     "userid": 9986,
    #     #     "role": "staff",
    #     #     "name": "John Doe",
    #     #     "email": "john.doe@company.com"
    #     # })
    #     # self.assertEqual(create_response1.status_code, 201)
        
    #     # create_response2 = self.client.post('/users', json={
    #     #     "id": user_id2,
    #     #     "userid": 9985,
    #     #     "role": "manager",
    #     #     "name": "Jane Doe",
    #     #     "email": "jane.doe@company.com"
    #     # })
    #     # self.assertEqual(create_response2.status_code, 201)
        
    #     # Make request
    #     response = self.client.get('/users/search?email=yong.yq321@gmail.com')
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["status"], 200)
    #     self.assertIn("Found 1 user(s)", data["message"])
    #     self.assertIn("data", data)
    #     self.assertEqual(len(data["data"]), 1)

    # def test_search_users_by_email_no_results(self):
    #     """Test search users by email when no matches found."""
    #     # Clean up any existing test data first
    #     self.cleanup_test_data()
        
    #     # Make request with non-matching email
    #     response = self.client.get('/users/search?email=nonexistent')
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["status"], 200)
    #     self.assertIn("No users found", data["message"])
    #     self.assertEqual(data["data"], [])

    # def test_search_users_by_email_no_query(self):
    #     """Test search users by email when no query provided."""
    #     # Make request without email query
    #     response = self.client.get('/users/search')
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 400)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["status"], 400)
    #     self.assertIn("No search query provided", data["message"])

    # def test_search_users_by_email_empty_query(self):
    #     """Test search users by email with empty query."""
    #     # Make request with empty email query
    #     response = self.client.get('/users/search?email=')
        
    #     # Assertions
    #     self.assertEqual(response.status_code, 400)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["status"], 400)
    #     self.assertIn("No search query provided", data["message"])


    # ==================== update_notification_preferences Tests ====================
    
    def test_update_notification_preferences_success(self):
        """Test successful notification preferences update."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # # First, create a user
        # user_id = "2d1ad2e0-27aa-45c1-8e10-4c1b218c8f5d"
        # create_response = self.client.post('/users', json={
        #     "id": user_id,
        #     "userid": 9983,
        #     "role": "staff",
        #     "name": "Test User",
        #     "email": "test@example.com"
        # })
        # self.assertEqual(create_response.status_code, 201)
        
        # Update notification preferences
        response = self.client.put('/users/297/notification-preferences', json={
            "in_app": False,
            "email": True
        })
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 200)
        self.assertIn("User 297 updated successfully", data["message"])
        self.assertEqual(data["data"]["notification_preferences"]["in_app"], False)
        self.assertEqual(data["data"]["notification_preferences"]["email"], True)

    def test_update_notification_preferences_invalid_keys(self):
        """Test notification preferences update with invalid keys."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # # First, create a user
        # user_id = "2d1ad2e0-27aa-45c1-8e10-4c1b218c8f5d"
        # create_response = self.client.post('/users', json={
        #     "id": user_id,
        #     "userid": 9982,
        #     "role": "staff",
        #     "name": "Test User",
        #     "email": "test@example.com"
        # })
        # self.assertEqual(create_response.status_code, 201)
        
        # Try to update with invalid keys
        response = self.client.put('/users/297/notification-preferences', json={
            "invalid_key": True,
            "another_invalid": False
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 400)
        self.assertIn("Invalid preference keys", data["message"])

    def test_update_notification_preferences_invalid_values(self):
        """Test notification preferences update with invalid values."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # # First, create a user
        # user_id = "2d1ad2e0-27aa-45c1-8e10-4c1b218c8f5d"
        # create_response = self.client.post('/users', json={
        #     "id": user_id,
        #     "userid": 9981,
        #     "role": "staff",
        #     "name": "Test User",
        #     "email": "test@example.com"
        # })
        # self.assertEqual(create_response.status_code, 201)
        
        # Try to update with invalid values
        response = self.client.put('/users/297/notification-preferences', json={
            "in_app": "not_a_boolean",
            "email": True
        })
        
        # Assertions
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 400)
        self.assertIn("must be a boolean value", data["message"])

    def test_update_notification_preferences_user_not_found(self):
        """Test notification preferences update when user doesn't exist."""
        # Clean up any existing test data first
        self.cleanup_test_data()
        
        # Make request with non-existent user
        response = self.client.put('/users/99999/notification-preferences', json={
            "in_app": False,
            "email": True
        })
        
        # Assertions
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["status"], 404)
        self.assertIn("User with userid 99999 not found", data["message"])


    # # ==================== Multiple Users Tests ====================
    
    # def test_multiple_users_same_department(self):
    #     """Test creating and retrieving multiple users in the same department."""
    #     # Clean up any existing test data first
    #     self.cleanup_test_data()
        
    #     # Create multiple users in the same department
    #     users_data = [
    #         {"userid": 9980, "name": "User 1", "email": "user1@dept.com"},
    #         {"userid": 9979, "name": "User 2", "email": "user2@dept.com"},
    #         {"userid": 9978, "name": "User 3", "email": "user3@dept.com"}
    #     ]
        
    #     for i, user_data in enumerate(users_data):
    #         user_id = "2d1ad2e0-27aa-45c1-8e10-4c1b218c8f5d"
    #         response = self.client.post('/users', json={
    #             "id": user_id,
    #             "role": "staff",
    #             "dept_id": 30,
    #             **user_data
    #         })
    #         self.assertEqual(response.status_code, 201)
        
    #     # Retrieve all users for the department
    #     response = self.client.get('/users/department/30')
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["status"], 200)
    #     self.assertEqual(len(data["data"]), 3)
        
    #     # Verify all users are present
    #     retrieved_userids = [user["userid"] for user in data["data"]]
    #     for user_data in users_data:
    #         self.assertIn(user_data["userid"], retrieved_userids)

    # def test_users_different_teams(self):
    #     """Test users in different teams are isolated."""
    #     # Clean up any existing test data first
    #     self.cleanup_test_data()
        
    #     # Create users in different teams
    #     user_id1 = "2d1ad2e0-27aa-45c1-8e10-4c1b218c8f5d"
    #     user_id2 = "670dad0b-09e7-4624-a61a-8007b549d2fc"
        
    #     self.client.post('/users', json={
    #         "id": user_id1,
    #         "userid": 9977,
    #         "role": "staff",
    #         "name": "Team 1 User",
    #         "email": "team1@example.com",
    #         "team_id": 40
    #     })
        
    #     self.client.post('/users', json={
    #         "id": user_id2,
    #         "userid": 9976,
    #         "role": "staff",
    #         "name": "Team 2 User",
    #         "email": "team2@example.com",
    #         "team_id": 50
    #     })
        
    #     # Get users for team 1
    #     response1 = self.client.get('/users/team/40')
    #     self.assertEqual(response1.status_code, 200)
    #     data1 = json.loads(response1.data)
    #     self.assertEqual(len(data1["data"]), 1)
    #     self.assertEqual(data1["data"][0]["name"], "Team 1 User")
        
    #     # Get users for team 2
    #     response2 = self.client.get('/users/team/50')
    #     self.assertEqual(response2.status_code, 200)
    #     data2 = json.loads(response2.data)
    #     self.assertEqual(len(data2["data"]), 1)
    #     self.assertEqual(data2["data"][0]["name"], "Team 2 User")

    # def test_user_with_special_characters(self):
    #     """Test user with special characters in name and email."""
    #     # Clean up any existing test data first
    #     self.cleanup_test_data()
        
    #     special_name = "José María O'Connor-Smith"
    #     special_email = "josé.maría@example.com"
    #     user_id = "2d1ad2e0-27aa-45c1-8e10-4c1b218c8f5d"
        
    #     # Create user with special characters
    #     create_response = self.client.post('/users', json={
    #         "id": user_id,
    #         "userid": 9975,
    #         "role": "staff",
    #         "name": special_name,
    #         "email": special_email
    #     })
    #     self.assertEqual(create_response.status_code, 201)
        
    #     # Retrieve the user
    #     response = self.client.get('/users/9975')
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["data"]["name"], special_name)
    #     self.assertEqual(data["data"]["email"], special_email)

    # def test_user_with_long_content(self):
    #     """Test user with very long name and email."""
    #     # Clean up any existing test data first
    #     self.cleanup_test_data()
        
    #     long_name = "This is a very long name that might cause issues in some systems. " * 10
    #     long_email = "very.long.email.address.that.might.cause.issues@very.long.domain.name.com"
    #     user_id = "2d1ad2e0-27aa-45c1-8e10-4c1b218c8f5d"
        
    #     # Create user with long content
    #     create_response = self.client.post('/users', json={
    #         "id": user_id,
    #         "userid": 9974,
    #         "role": "staff",
    #         "name": long_name,
    #         "email": long_email
    #     })
    #     self.assertEqual(create_response.status_code, 201)
        
    #     # Retrieve the user
    #     response = self.client.get('/users/9974')
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.data)
    #     self.assertEqual(data["data"]["name"], long_name)
    #     self.assertEqual(data["data"]["email"], long_email)
    #     self.assertGreater(len(data["data"]["name"]), 500)
    #     self.assertGreater(len(data["data"]["email"]), 100)


if __name__ == "__main__":
    unittest.main()
