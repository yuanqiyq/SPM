<template>
  <div v-if="isVisible" class="popup-overlay" @click="closePopup">
    <div class="popup-container" @click.stop>
      <div class="popup-header">
        <h3>{{ isSubtask ? 'Assign Subtask' : 'Assign Task' }}</h3>
        <button class="close-btn" @click="closePopup">&times;</button>
      </div>
      
      <div class="popup-content">
        <div class="task-info">
          <p><strong>{{ isSubtask ? 'Subtask' : 'Task' }}:</strong> {{ taskTitle }}</p>
          <p><strong>Current Owner:</strong> {{ currentOwner || 'Unassigned' }}</p>
          <p><strong>Your Role:</strong> {{ userRole.charAt(0).toUpperCase() + userRole.slice(1) }}</p>
        </div>

        <!-- Permission Info -->
        <div class="permission-info">
          <div class="info-icon">
            <i class="bi bi-info-circle"></i>
          </div>
          <div class="info-text">
            <p v-if="userRole === 'director'">
              <strong>As a Director</strong>, you can assign this task to managers in your department.
            </p>
            <p v-else-if="userRole === 'manager'">
              <strong>As a Manager</strong>, you can assign this task to staff members in your team.
            </p>
            <p v-else>
              <strong>Note:</strong> Only task owners with manager or director roles can reassign tasks.
            </p>
          </div>
        </div>

        <!-- Loading indicator -->
        <div v-if="isLoading" class="loading-message">
          <p>Loading team members...</p>
        </div>

        <!-- No eligible members message -->
        <div v-else-if="eligibleMembers.length === 0" class="no-members-message">
          <p>
            <strong>No team members available to assign to.</strong>
          </p>
          <p v-if="userRole === 'manager'">
            There are no staff members in your team to assign this task to.
          </p>
          <p v-else-if="userRole === 'director'">
            There are no managers in your department to assign this task to.
          </p>
        </div>

        <form v-else @submit.prevent="handleAssignment">
          <div class="form-group">
            <label for="assignee">Assign to:</label>
            <select 
              id="assignee" 
              v-model="selectedAssignee" 
              required
              :disabled="isLoading"
            >
              <option value="">Select team member</option>
              <option 
                v-for="member in eligibleMembers" 
                :key="member.userid" 
                :value="member.userid"
              >
                {{ member.name }} ({{ member.role }})
              </option>
            </select>
          </div>

          <!-- Status selection for director assigning to manager -->
          <div v-if="showStatusSelection" class="form-group">
            <label for="status">Set status to:</label>
            <select 
              id="status" 
              v-model="selectedStatus" 
              required
              :disabled="isLoading"
            >
              <option value="Unassigned">Unassigned</option>
              <option value="Ongoing">Ongoing</option>
            </select>
          </div>
          <div v-else class="form-group">
            <label for="status">Set status to:</label>
            <select 
                id="status" 
                v-model="selectedStatus" 
                required
                disabled 
            >
                <option value="Ongoing" selected>Ongoing</option>
            </select>
          </div>


          <div class="form-actions">
            <button type="button" @click="closePopup" :disabled="isLoading">
              Cancel
            </button>
            <button type="submit" :disabled="!selectedAssignee || isLoading">
              {{ isLoading ? 'Assigning...' : 'Assign Task' }}
            </button>
          </div>
        </form>

        <!-- Messages -->
        <div v-if="successMessage" class="message success">
          {{ successMessage }}
        </div>
        <div v-if="errorMessage" class="message error">
          {{ errorMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { enhancedNotificationService } from '../services/notifications'

export default {
  name: 'TaskAssignmentPopup',
  props: {
    isVisible: {
      type: Boolean,
      default: false
    },
    taskId: {
      type: [String, Number],
      required: true
    },
    taskTitle: {
      type: String,
      required: true
    },
    currentOwner: {
      type: String,
      default: ''
    },
    userRole: {
      type: String,
      required: true // 'director', 'manager', 'staff'
    },
    isSubtask: {
      type: Boolean,
      default: false
    },
    parentTaskId: {
      type: [String, Number],
      default: null
    },
    teamMembers: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      selectedAssignee: '',
      selectedStatus: 'Ongoing',
      isLoading: false,
      successMessage: '',
      errorMessage: '',
      currentUserDetails: null,
      eligibleUsers: []
    }
  },
  computed: {
    eligibleMembers() {
      // Use dynamically fetched eligible users instead of static teamMembers
      return this.eligibleUsers
    },
    showStatusSelection() {
      if (this.userRole !== 'director') return false
      const selectedMember = this.eligibleUsers.find(m => m.userid === this.selectedAssignee)
      return selectedMember && selectedMember.role === 'manager'
    }
  },
  methods: {
    async fetchCurrentUserDetails() {
      try {
        const currentUserId = localStorage.getItem('spm_userid')
        if (!currentUserId) {
          throw new Error('No user ID found in session')
        }

        const response = await fetch(`http://localhost:5003/users/${currentUserId}`)
        if (!response.ok) {
          throw new Error(`Failed to fetch user details: ${response.status}`)
        }

        const result = await response.json()
        this.currentUserDetails = result.data
        console.log('Current user details:', this.currentUserDetails)
      } catch (error) {
        console.error('Error fetching current user details:', error)
        this.errorMessage = 'Failed to load user details'
      }
    },

    async fetchEligibleUsers() {
      try {
        if (!this.currentUserDetails) {
          await this.fetchCurrentUserDetails()
        }

        if (!this.currentUserDetails) {
          throw new Error('Could not load current user details')
        }

        let eligibleUsers = []

        if (this.userRole === 'director') {
          // Director can assign to managers in the same department
          if (this.currentUserDetails.dept_id) {
            const response = await fetch(`http://localhost:5003/users/department/${this.currentUserDetails.dept_id}`)
            if (response.ok) {
              const result = await response.json()
              eligibleUsers = result.data.filter(user => 
                user.role === 'manager' && user.userid !== this.currentUserDetails.userid
              )
            }
          }
        } else if (this.userRole === 'manager') {
          // Manager can assign to staff in the same team
          if (this.currentUserDetails.team_id) {
            const response = await fetch(`http://localhost:5003/users/team/${this.currentUserDetails.team_id}`)
            if (response.ok) {
              const result = await response.json()
              eligibleUsers = result.data.filter(user => 
                user.role === 'staff' && user.userid !== this.currentUserDetails.userid
              )
            }
          }
        }

        this.eligibleUsers = eligibleUsers
        console.log('Eligible users for assignment:', this.eligibleUsers)
      } catch (error) {
        console.error('Error fetching eligible users:', error)
        this.errorMessage = 'Failed to load eligible users for assignment'
      }
    },

    async handleAssignment() {
      this.clearMessages()
      
      if (!this.validateAssignment()) {
        return
      }

      this.isLoading = true

      try {
        const assigneeData = this.eligibleUsers.find(m => m.userid === this.selectedAssignee)
        const updateData = this.prepareUpdateData(assigneeData)
        
        await this.updateTask(updateData)
        
        // Trigger assignment notification
        await this.triggerAssignmentNotification(assigneeData)
        
        this.successMessage = `${assigneeData.name} has been assigned as the new owner of the ${this.isSubtask ? 'subtask' : 'task'}`
        
        // Auto-close after 2 seconds
        setTimeout(() => {
          this.closePopup()
          this.$emit('assignment-success', {
            taskId: this.taskId,
            assignee: assigneeData,
            status: updateData.status
          })
        }, 2000)
        
      } catch (error) {
        this.errorMessage = error.message || 'Failed to assign task. Please try again.'
      } finally {
        this.isLoading = false
      }
    },

    validateAssignment() {
      const assigneeData = this.eligibleUsers.find(m => m.userid === this.selectedAssignee)
      
      if (!assigneeData) {
        this.errorMessage = 'Please select a valid team member'
        return false
      }

      // Validate role-based assignment rules
      if (this.userRole === 'director' && assigneeData.role !== 'manager') {
        this.errorMessage = 'Directors can only assign tasks to managers'
        return false
      }
      
      if (this.userRole === 'manager' && assigneeData.role !== 'staff') {
        this.errorMessage = 'Managers can only assign tasks to staff members'
        return false
      }

      return true
    },

    prepareUpdateData(assigneeData) {
      const updateData = {}

      // Set the assignee as the new owner
      updateData.owner_id = assigneeData.userid
      
      // For staff assignments, need to handle collaborators
      if (assigneeData.role === 'staff') {
        // We need to get current collaborators and add the new assignee
        // This will be handled by getting current task data first
        updateData.needsCollaboratorUpdate = true
        updateData.newCollaboratorId = assigneeData.userid
      }

      // Determine status based on assignment rules
      if (this.userRole === 'manager' && assigneeData.role === 'staff') {
        updateData.status = 'Ongoing'
      } else if (this.userRole === 'director' && assigneeData.role === 'manager') {
        updateData.status = this.selectedStatus
      }

      return updateData
    },

    async updateTask(updateData) {
      let finalUpdateData = { task_id: this.taskId }
      
      // Handle collaborators for staff assignments
      if (updateData.needsCollaboratorUpdate) {
        // First get current task data to get existing collaborators
        const currentTaskResponse = await fetch(`http://localhost:5002/tasks/${this.taskId}`)
        if (!currentTaskResponse.ok) {
          throw new Error('Failed to fetch current task data')
        }
        
        const currentTaskData = await currentTaskResponse.json()
        const currentTask = currentTaskData.task || currentTaskData
        
        // Get existing collaborators and add the new one
        const existingCollaborators = currentTask.collaborators || []
        const newCollaborators = [...existingCollaborators]
        
        // Add the new assignee as collaborator if not already present
        if (!newCollaborators.includes(updateData.newCollaboratorId)) {
          newCollaborators.push(updateData.newCollaboratorId)
        }
        
        finalUpdateData.collaborators = newCollaborators
        
        // If it's a subtask, also update parent task collaborators
        if (this.isSubtask && this.parentTaskId) {
          try {
            const parentTaskResponse = await fetch(`http://localhost:5002/tasks/${this.parentTaskId}`)
            if (parentTaskResponse.ok) {
              const parentTaskData = await parentTaskResponse.json()
              const parentTask = parentTaskData.task || parentTaskData
              const parentCollaborators = parentTask.collaborators || []
              
              if (!parentCollaborators.includes(updateData.newCollaboratorId)) {
                const updatedParentCollaborators = [...parentCollaborators, updateData.newCollaboratorId]
                
                // Update parent task collaborators
                await fetch(`http://localhost:5002/tasks/update`, {
                  method: 'PUT',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    task_id: this.parentTaskId,
                    collaborators: updatedParentCollaborators
                  })
                })
              }
            }
          } catch (error) {
            console.error('Failed to update parent task collaborators:', error)
            // Don't fail the main assignment
          }
        }
      }
      
      // Add other update fields
      Object.keys(updateData).forEach(key => {
        if (key !== 'needsCollaboratorUpdate' && key !== 'newCollaboratorId') {
          finalUpdateData[key] = updateData[key]
        }
      })

      // Update the task
      const response = await fetch(`http://localhost:5002/tasks/update`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(finalUpdateData)
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return response.json()
    },

    closePopup() {
      this.clearMessages()
      this.selectedAssignee = ''
      this.selectedStatus = 'Ongoing'
      this.$emit('close')
    },

    clearMessages() {
      this.successMessage = ''
      this.errorMessage = ''
    },

    async triggerAssignmentNotification(assigneeData) {
      try {
        // Get current user info
        const currentUserId = localStorage.getItem('spm_userid');
        let currentUserName = localStorage.getItem('spm_username') || 'System';
        
        // Try to get the actual user name from the user service
        if (currentUserId) {
          try {
            const userResponse = await fetch(`http://localhost:5003/users/${currentUserId}`);
            if (userResponse.ok) {
              const userData = await userResponse.json();
              currentUserName = userData.data?.name || currentUserName;
            }
          } catch (error) {
            console.warn('Failed to fetch user name, using stored name:', error);
          }
        }
        
        // Get current task owner for ownership transfer notification
        const currentTaskResponse = await fetch(`http://localhost:5002/tasks/${this.taskId}`)
        if (!currentTaskResponse.ok) {
          throw new Error('Failed to fetch current task data')
        }
        
        const currentTaskData = await currentTaskResponse.json()
        const currentTask = currentTaskData.task || currentTaskData
        const currentOwnerId = currentTask.owner_id
        
        // Trigger ownership transfer notification (since we're assigning as owner, not collaborator)
        await enhancedNotificationService.triggerTaskOwnershipTransferNotification(
          this.taskId,
          assigneeData.userid,
          currentUserName
        );
        
        console.log('Task ownership transfer notification sent successfully');
      } catch (error) {
        console.error('Failed to send task assignment notification:', error);
        // Don't throw error to avoid breaking the main assignment flow
      }
    }
  },

  watch: {
    isVisible(newVal) {
      if (newVal) {
        this.clearMessages()
        this.isLoading = true
        // Fetch eligible users when popup opens
        this.fetchEligibleUsers().finally(() => {
          this.isLoading = false
        })
      }
    },
    selectedAssignee() {
      this.clearMessages()
    }
  }
}
</script>

<style scoped>
/* Popup Overlay */
.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 1rem;
  box-sizing: border-box;
}

.popup-container {
  background: white;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  animation: slideIn 0.3s ease-out both;
}

/* Header */
.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.popup-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a1a1a;
  letter-spacing: -0.01em;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  color: #374151;
  background: #f3f4f6;
}

/* Content */
.popup-content {
  padding: 1.5rem;
}

.task-info {
  background: #f9fafb;
  border: 1px solid #f3f4f6;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.task-info p {
  margin: 0.25rem 0;
  font-size: 0.85rem;
  color: #374151;
  line-height: 1.4;
}

/* No Members Message */
.no-members-message {
  background: #fef3c7;
  border: 1px solid #fcd34d;
  border-radius: 8px;
  padding: 1.25rem;
  margin-top: 1rem;
  text-align: center;
}

.no-members-message p {
  margin: 0.5rem 0;
  font-size: 0.875rem;
  color: #92400e;
  line-height: 1.5;
}

.no-members-message p:first-child {
  margin-top: 0;
}

.no-members-message p:last-child {
  margin-bottom: 0;
}

.no-members-message strong {
  color: #78350f;
  font-weight: 600;
}

/* Loading Message */
.loading-message {
  background: #e0f2fe;
  border: 1px solid #bae6fd;
  border-radius: 8px;
  padding: 1.25rem;
  margin-top: 1rem;
  text-align: center;
}

.loading-message p {
  margin: 0;
  font-size: 0.875rem;
  color: #075985;
  line-height: 1.5;
}

.task-info p:first-child {
  margin-top: 0;
}

.task-info p:last-child {
  margin-bottom: 0;
}

.task-info strong {
  color: #1a1a1a;
  font-weight: 500;
}

/* Permission Info */
.permission-info {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.permission-info .info-icon {
  color: #3b82f6;
  font-size: 1.125rem;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.permission-info .info-text {
  flex: 1;
}

.permission-info .info-text p {
  margin: 0;
  font-size: 0.875rem;
  color: #1e40af;
  line-height: 1.5;
}

.permission-info .info-text strong {
  font-weight: 600;
  color: #1e3a8a;
}

/* Form */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.875rem;
  background-color: white;
  color: #374151;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.form-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group select:disabled {
  background-color: #f9fafb;
  color: #6b7280;
  cursor: not-allowed;
}

/* Form Actions */
.form-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.form-actions button {
  padding: 0.75rem 1.25rem;
  border-radius: 6px;
  border: 1px solid;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
  min-width: 80px;
}

.form-actions button[type="button"] {
  background-color: white;
  border-color: #e5e7eb;
  color: #6b7280;
}

.form-actions button[type="button"]:hover:not(:disabled) {
  background-color: #f9fafb;
  border-color: #d1d5db;
  color: #374151;
}

.form-actions button[type="submit"] {
  background-color: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.form-actions button[type="submit"]:hover:not(:disabled) {
  background-color: #2563eb;
  border-color: #2563eb;
}

.form-actions button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Messages */
.message {
  padding: 0.75rem;
  border-radius: 6px;
  margin-top: 1rem;
  font-size: 0.875rem;
  line-height: 1.4;
  border: 1px solid;
}

.message.success {
  background-color: #d1fae5;
  border-color: #a7f3d0;
  color: #065f46;
}

.message.error {
  background-color: #fef2f2;
  border-color: #fecaca;
  color: #991b1b;
}

/* Animation */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .popup-overlay {
    padding: 1rem;
    align-items: flex-start;
    padding-top: 2rem;
  }

  .popup-container {
    max-width: 100%;
    max-height: calc(100vh - 4rem);
  }

  .popup-header {
    padding: 1.25rem;
  }

  .popup-header h3 {
    font-size: 1.125rem;
  }

  .popup-content {
    padding: 1.25rem;
  }

  .task-info {
    padding: 0.875rem;
  }

  .task-info p {
    font-size: 0.8rem;
  }

  .no-members-message {
    padding: 1rem;
  }

  .no-members-message p {
    font-size: 0.8rem;
  }

  .loading-message {
    padding: 1rem;
  }

  .loading-message p {
    font-size: 0.8rem;
  }

  .form-group {
    margin-bottom: 1.25rem;
  }

  .form-actions {
    flex-direction: column-reverse;
    gap: 0.5rem;
  }

  .form-actions button {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 640px) {
  .popup-overlay {
    padding: 0.75rem;
    align-items: flex-start;
    padding-top: 1.5rem;
  }

  .popup-container {
    max-height: calc(100vh - 3rem);
  }

  .popup-header {
    padding: 1rem;
  }

  .popup-header h3 {
    font-size: 1rem;
    line-height: 1.3;
  }

  .close-btn {
    width: 28px;
    height: 28px;
    font-size: 1.25rem;
  }

  .popup-content {
    padding: 1rem;
  }

  .task-info {
    padding: 0.75rem;
  }

  .task-info p {
    font-size: 0.75rem;
    margin: 0.125rem 0;
  }

  .no-members-message {
    padding: 0.875rem;
  }

  .no-members-message p {
    font-size: 0.75rem;
  }

  .loading-message {
    padding: 0.875rem;
  }

  .loading-message p {
    font-size: 0.75rem;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-group label {
    font-size: 0.8rem;
  }

  .form-group select {
    padding: 0.625rem;
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .popup-overlay {
    padding: 0.5rem;
    padding-top: 1rem;
  }

  .popup-container {
    max-height: calc(100vh - 2rem);
  }

  .popup-header {
    padding: 0.875rem;
  }

  .popup-content {
    padding: 0.875rem;
  }

  .task-info {
    padding: 0.625rem;
  }

  .no-members-message {
    padding: 0.75rem;
  }

  .no-members-message p {
    font-size: 0.7rem;
  }

  .loading-message {
    padding: 0.75rem;
  }

  .loading-message p {
    font-size: 0.7rem;
  }

  .form-actions button {
    padding: 0.625rem 1rem;
    font-size: 0.8rem;
  }
}

/* Ensure proper text wrapping on very small screens */
@media (max-width: 400px) {
  .popup-header h3 {
    font-size: 0.9rem;
    line-height: 1.2;
    word-break: break-word;
  }

  .task-info p {
    font-size: 0.7rem;
    line-height: 1.3;
  }

  .no-members-message p {
    font-size: 0.65rem;
    line-height: 1.3;
  }

  .loading-message p {
    font-size: 0.65rem;
    line-height: 1.3;
  }

  .form-group label {
    font-size: 0.75rem;
  }

  .form-group select {
    font-size: 0.75rem;
  }

  .message {
    font-size: 0.8rem;
  }
}
</style>