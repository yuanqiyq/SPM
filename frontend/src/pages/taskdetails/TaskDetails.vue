<template>
  <div class="app-layout ms-2">
    <!-- Side Navigation -->
    <SideNavbar />
    
    <!-- Main Content Area -->
    <div class="app-container">
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner">
        </div>
        <p>Loading task details...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <div class="error-icon">
          <i class="bi bi-exclamation-triangle"></i>
        </div>
        <h3>Error Loading Task</h3>
        <p>{{ error }}</p>
        <button @click="goBack" class="btn btn-secondary">
          <i class="bi bi-arrow-left"></i>
          Go Back
        </button>
      </div>

      <!-- Task Details Content -->
      <div v-else-if="task" class="task-details-content">
        <!-- Breadcrumb Navigation -->
        <div class="breadcrumb-section">
          <nav class="breadcrumb-nav">
            <button @click="goBack" class="breadcrumb-item">
              <i class="bi bi-house"></i>
              Tasks
            </button>
            <i class="bi bi-chevron-right breadcrumb-separator"></i>
            <span v-if="project" class="breadcrumb-item">
              <div class="project-dot" :style="{ backgroundColor: project.color || '#6366f1' }"></div>
              {{ project.proj_name  }}
              <i class="bi bi-chevron-right breadcrumb-separator"></i>
            </span>
            <span v-if="parentTask" class="breadcrumb-item" @click="navigateToTask(parentTask.id)">
              {{ parentTask.task_name }}
              <i class="bi bi-chevron-right breadcrumb-separator"></i>
            </span>
            <span class="breadcrumb-current">{{ task.task_name }}</span>
          </nav>
        </div>

        <!-- Header Section -->
        <div class="header-section">
          <div class="header-content">
            <div class="task-header">
              <div class="task-icon-title">
                <div class="task-icon" :class="getTaskTypeClass()">
                  <i :class="getTaskTypeIcon()"></i>
                </div>
                <h1 class="page-title">{{ task.task_name }}</h1>
              </div>
              
              <div class="header-actions">
                <div class="task-status-badge" :class="getStatusClass(task.status)">
                  <i :class="getStatusIcon(task.status)"></i>
                  <span>{{ getStatusLabel(task.status) }}</span>
                </div>
                
                <div class="action-buttons">
                  <button 
                    v-if="canEditTask" 
                    @click="openEditPopup" 
                    class="btn btn-ghost"
                  >
                    <i class="bi bi-pencil"></i>
                    Edit
                  </button>
                  <button 
                    v-if="canAssignTask" 
                    @click="openAssignPopup" 
                    class="btn btn-primary"
                  >
                    <i class="bi bi-person-plus"></i>
                    Assign
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Main Content -->
        <div class="main-content">
          <!-- Task Description -->
          <div class="content-block">
            <h3 class="block-title">
              <i class="bi bi-card-text"></i>
              Description
            </h3>
            <div class="block-content">
              <div class="description-content">
                <p v-if="task.description" class="description-text">{{ task.description }}</p>
                <p v-else class="description-placeholder">No description provided</p>
              </div>
            </div>
          </div>

          <!-- Properties Section -->
          <div class="content-block">
            <h3 class="block-title">
              <i class="bi bi-list-ul"></i>
              Properties
            </h3>
            <div class="block-content">
              <div class="properties-grid">
                <div class="property-item">
                  <label class="property-label">
                    <i class="bi bi-flag"></i>
                    Status
                  </label>
                  <div class="property-value">
                    <div class="task-status-inline" :class="getStatusClass(task.status)">
                      <i :class="getStatusIcon(task.status)"></i>
                      <span>{{ getStatusLabel(task.status) }}</span>
                    </div>
                  </div>
                </div>

                <div class="property-item">
                  <label class="property-label">
                    <i class="bi bi-calendar3"></i>
                    Due Date
                  </label>
                  <div class="property-value">
                    <span class="date-value">{{ formatDate(task.due_date) }}</span>
                    <span v-if="task.due_date" class="date-relative">{{ getRelativeDate(task.due_date) }}</span>
                  </div>
                </div>

                <div class="property-item">
                  <label class="property-label">
                    <i class="bi bi-flag-fill"></i>
                    Priority
                  </label>
                  <div class="property-value">
                    <div class="task-priority-badge" :class="getPriorityClass(task.priority)">
                      <i class="bi bi-flag-fill"></i>
                      <span>Priority {{ task.priority }}</span>
                    </div>
                  </div>
                </div>

                <div class="property-item">
                  <label class="property-label">
                    <i class="bi bi-person"></i>
                    Owner
                  </label>
                  <div class="property-value">
                    <div v-if="task.owner" class="user-chip">
                      <div class="user-avatar">
                        <i class="bi bi-person-circle"></i>
                      </div>
                      <span>{{ task.owner }}</span>
                    </div>
                    <span v-else class="unassigned-text">Unassigned</span>
                  </div>
                </div>

                <div v-if="project" class="property-item">
                  <label class="property-label">
                    <i class="bi bi-folder"></i>
                    Project
                  </label>
                  <div class="property-value">
                    <div class="project-chip">
                      <div class="project-dot" :style="{ backgroundColor: project.color || '#6366f1' }"></div>
                      <span>{{ project.proj_name }}</span>
                    </div>
                  </div>
                </div>

                <div class="property-item">
                  <label class="property-label">
                    <i class="bi bi-clock"></i>
                    Created
                  </label>
                  <div class="property-value">
                    <span class="date-value">{{ formatDate(task.created_at) }}</span>
                  </div>
                </div>

                <div v-if="task.collaborators && task.collaborators.length > 0" class="property-item">
                  <label class="property-label">
                    <i class="bi bi-people"></i>
                    Collaborators
                  </label>
                  <div class="property-value">
                    <div class="collaborators-list">
                      <div v-for="collaboratorId in task.collaborators" :key="collaboratorId" class="user-chip">
                        <div class="user-avatar">
                          <i class="bi bi-person-circle"></i>
                        </div>
                        <span>{{ getUserName(collaboratorId) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Attachments Section -->
          <div v-if="hasAttachments" class="content-block">
            <h3 class="block-title">
              <i class="bi bi-paperclip"></i>
              Attachments
            </h3>
            <div class="block-content">
              <div class="attachments-grid">
                <!-- PDF Attachments -->
                <div 
                  v-for="attachment in parsedAttachments" 
                  :key="`pdf-${attachment.name}`"
                  class="attachment-card"
                  @click="openAttachment(attachment)"
                >
                  <div class="attachment-icon pdf">
                    <i class="bi bi-file-earmark-pdf"></i>
                  </div>
                  <div class="attachment-info">
                    <h4 class="attachment-name">{{ attachment.name }}</h4>
                    <p class="attachment-meta">
                      <span v-if="attachment.size">{{ formatFileSize(attachment.size) }}</span>
                      <span v-if="attachment.uploaded_at">• {{ formatDate(attachment.uploaded_at) }}</span>
                      <span class="attachment-type">• PDF</span>
                    </p>
                  </div>
                  <div class="attachment-actions">
                    <button class="btn-icon" @click.stop="downloadAttachment(attachment)">
                      <i class="bi bi-download"></i>
                    </button>
                  </div>
                </div>

                <!-- Image Attachments -->
                <div 
                  v-for="attachment in task.image_attachments || []" 
                  :key="`img-${attachment.id || attachment.name}`"
                  class="attachment-card"
                  @click="openAttachment(attachment)"
                >
                  <div class="attachment-icon image">
                    <i class="bi bi-file-earmark-image"></i>
                  </div>
                  <div class="attachment-info">
                    <h4 class="attachment-name">{{ attachment.name || attachment.filename }}</h4>
                    <p class="attachment-meta">
                      <span v-if="attachment.size">{{ formatFileSize(attachment.size) }}</span>
                      <span v-if="attachment.uploaded_at">• {{ formatDate(attachment.uploaded_at) }}</span>
                      <span class="attachment-type">• Image</span>
                    </p>
                  </div>
                  <div class="attachment-actions">
                    <button class="btn-icon" @click.stop="downloadAttachment(attachment)">
                      <i class="bi bi-download"></i>
                    </button>
                  </div>
                </div>

                <!-- Document Attachments -->
                <div 
                  v-for="attachment in task.document_attachments || []" 
                  :key="`doc-${attachment.id || attachment.name}`"
                  class="attachment-card"
                  @click="openAttachment(attachment)"
                >
                  <div class="attachment-icon document">
                    <i class="bi bi-file-earmark-text"></i>
                  </div>
                  <div class="attachment-info">
                    <h4 class="attachment-name">{{ attachment.name || attachment.filename }}</h4>
                    <p class="attachment-meta">
                      <span v-if="attachment.size">{{ formatFileSize(attachment.size) }}</span>
                      <span v-if="attachment.uploaded_at">• {{ formatDate(attachment.uploaded_at) }}</span>
                      <span class="attachment-type">• Document</span>
                    </p>
                  </div>
                  <div class="attachment-actions">
                    <button class="btn-icon" @click.stop="downloadAttachment(attachment)">
                      <i class="bi bi-download"></i>
                    </button>
                  </div>
                </div>

                <!-- Other Attachments -->
                <div 
                  v-for="attachment in task.other_attachments || []" 
                  :key="`other-${attachment.id || attachment.name}`"
                  class="attachment-card"
                  @click="openAttachment(attachment)"
                >
                  <div class="attachment-icon other">
                    <i class="bi bi-file-earmark"></i>
                  </div>
                  <div class="attachment-info">
                    <h4 class="attachment-name">{{ attachment.name || attachment.filename }}</h4>
                    <p class="attachment-meta">
                      <span v-if="attachment.size">{{ formatFileSize(attachment.size) }}</span>
                      <span v-if="attachment.uploaded_at">• {{ formatDate(attachment.uploaded_at) }}</span>
                      <span v-if="attachment.type" class="attachment-type">• {{ attachment.type.toUpperCase() }}</span>
                    </p>
                  </div>
                  <div class="attachment-actions">
                    <button class="btn-icon" @click.stop="downloadAttachment(attachment)">
                      <i class="bi bi-download"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Subtasks Section -->
          <div v-if="task.subtasks && task.subtasks.length > 0" class="content-block">
            <h3 class="block-title">
              <i class="bi bi-diagram-3"></i>
              Subtasks
              <div class="subtasks-progress">
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: `${getSubtaskProgress(task)}%` }"
                  ></div>
                </div>
                <span class="progress-text">{{ getCompletedSubtasks(task) }}/{{ task.subtasks.length }}</span>
              </div>
            </h3>
            <div class="block-content">
              <div class="subtasks-list">
                <div 
                  v-for="subtask in task.subtasks" 
                  :key="subtask.id"
                  class="subtask-item"
                  :class="{ completed: subtask.status === 'Completed' }"
                  @click="navigateToTask(subtask.id)"
                >
                  <div class="subtask-content">
                    <h4 class="subtask-title" :class="{ completed: subtask.status === 'Completed' }">
                      {{ subtask.task_name }}
                    </h4>
                    <div class="subtask-meta">
                      <div class="task-status-mini" :class="getStatusClass(subtask.status)">
                        {{ getStatusLabel(subtask.status) }}
                      </div>
                      <span v-if="subtask.due_date" class="subtask-date">
                        {{ formatDate(subtask.due_date) }}
                      </span>
                      <span v-if="subtask.owner" class="subtask-owner">
                        {{ subtask.owner }}
                      </span>
                    </div>
                  </div>
                  <div class="subtask-arrow">
                    <i class="bi bi-arrow-right"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Comment Section -->
            <div>
              <CommentSection 
                :taskId="selectedTaskId"
                :taskOwnerId="taskOwnerId"
                @comments-updated="handleCommentsUpdate"
              />
          </div>

          <!-- Parent Task Reference -->
          <div v-if="parentTask" class="content-block">
            <h3 class="block-title">
              <i class="bi bi-arrow-up"></i>
              Parent Task
            </h3>
            <div class="block-content">
              <div class="parent-task-link" @click="navigateToTask(parentTask.id)">
                <div class="task-icon parent">
                  <i class="bi bi-list-task"></i>
                </div>
                <div class="parent-task-info">
                  <h4 class="parent-task-title">{{ parentTask.task_name }}</h4>
                  <p class="parent-task-meta">Parent Task</p>
                </div>
                <div class="parent-task-arrow">
                  <i class="bi bi-arrow-right"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Popup -->
    <EditPopup
      :isVisible="showEditPopup"
      :taskId="task?.id"
      :taskTitle="task?.task_name || ''"
      :currentOwner="task?.owner || ''"
      :userRole="currentUser.role"
      :isSubtask="!!task?.parent_task"
      :parentTaskId="task?.parent_task"
      :parentTaskTitle="parentTask?.task_name || ''"
      :teamMembers="teamMembers"
      @close="closeEditPopup"
      @update-success="updateSuccess"
    />

    <!-- Assign Popup -->
    <AssignPopup 
      :isVisible="showAssignPopup"
      :taskId="task?.id"
      :taskTitle="task?.task_name || ''"
      :currentOwner="task?.owner || ''"
      :userRole="currentUser.role"
      :isSubtask="!!task?.parent_task"
      :parentTaskId="task?.parent_task"
      :teamMembers="teamMembers"
      @close="closeAssignPopup"
      @assignment-success="handleAssignmentSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AssignPopup from '@/components/AssignPopup.vue'
import EditPopup from '@/components/EditPopup.vue'
import SideNavbar from '../../components/SideNavbar.vue'
import '../taskview/taskview.css'
import './taskdetails.css'
import CommentSection from '@/components/CommentSection.vue'

const route = useRoute()
const router = useRouter()

const task = ref(null)
const project = ref(null)
const parentTask = ref(null)
const loading = ref(true)
const error = ref(null)
const showEditPopup = ref(false)
const showAssignPopup = ref(false)
const users = ref({}) // Store user information lookup { userid: { name, email, ... } }
const selectedTaskId = computed(() => task.value?.id)
const taskOwnerId = computed(() => task.value?.owner_id)
const taskComments = ref([])

// Team members data for assign popup - replace with real data fetching as needed
const teamMembers = ref([
  { id: 1, name: 'John Manager', role: 'manager' },
  { id: 2, name: 'Jane Manager', role: 'manager' },
  { id: 3, name: 'Alice Staff', role: 'staff' },
  { id: 4, name: 'Bob Staff', role: 'staff' },
  { id: 5, name: 'Carol Staff', role: 'staff' }
])

// Get user info from localStorage
const getCurrentUser = () => {
  try {
    const userRole = localStorage.getItem('spm_role') || localStorage.getItem('userRole') || ''
    const userId = localStorage.getItem('spm_userid') || localStorage.getItem('userId') || ''
    return { role: userRole, userId: userId }
  } catch (err) {
    return { role: '', userId: '' }
  }
}

const currentUser = getCurrentUser()

// Computed properties for permissions
const canEditTask = computed(() => {
  if (!task.value || !currentUser.userId) return false
  
  const currentUserId = String(currentUser.userId).trim()
  const taskOwnerId = String(task.value.owner_id).trim()
  const isTaskOwner = currentUserId === taskOwnerId && currentUserId !== ''
  // const hasRolePermission = currentUser.role === 'manager' || currentUser.role === 'director'
  
  return isTaskOwner //|| hasRolePermission
})

// User can only assign if they are BOTH the task owner AND a manager/director
const canAssignTask = computed(() => {
  if (!task.value || !currentUser.userId) return false
  
  // Check if user is the task owner
  const currentUserId = String(currentUser.userId).trim()
  const taskOwnerId = String(task.value.owner_id).trim()
  const isTaskOwner = currentUserId === taskOwnerId && currentUserId !== ''
  
  // Check if user has manager or director role
  const hasRolePermission = currentUser.role === 'manager' || currentUser.role === 'director'
  
  // Both conditions must be true
  return isTaskOwner && hasRolePermission
})

// Computed property to check if task has any attachments
const hasAttachments = computed(() => {
  if (!task.value) return false
  
  return (parsedAttachments.value && parsedAttachments.value.length > 0) ||
         (task.value.image_attachments && task.value.image_attachments.length > 0) ||
         (task.value.document_attachments && task.value.document_attachments.length > 0) ||
         (task.value.other_attachments && task.value.other_attachments.length > 0)
})

// Computed property to parse attachments from JSON string
const parsedAttachments = computed(() => {
  if (!task.value?.attachments) return []
  
  try {
    if (Array.isArray(task.value.attachments)) {
      return task.value.attachments
    }
    return JSON.parse(task.value.attachments)
  } catch (error) {
    console.error('Error parsing attachments:', error)
    return []
  }
})

// Watch for route parameter changes to reload task details
watch(() => route.params.id, async (newId, oldId) => {
  if (newId && newId !== oldId) {
    await fetchTaskDetails()
  }
}, { immediate: false })

// Function to fetch user details by userid
const fetchUserDetails = async (userid) => {
  if (!userid) return null
  if (users.value[userid]) {
    return users.value[userid] // Return cached user
  }
  
  try {
    console.log(`Fetching user details for userid: ${userid}`)
    const response = await fetch(`http://localhost:5003/users/${userid}`)
    if (response.ok) {
      const data = await response.json()
      console.log(`User data received for ${userid}:`, data)
      const user = data.data
      if (user) {
        users.value[userid] = user
        console.log(`Cached user ${userid}:`, user)
        return user
      }
    } else {
      console.error(`Failed to fetch user ${userid}: ${response.status}`)
    }
  } catch (error) {
    console.error(`Error fetching user ${userid}:`, error)
  }
  return null
}

// Function to get user names for display
const getUserName = (userid) => {
  if (!userid) return 'Unknown User'
  const user = users.value[userid]
  return user?.name || `Invalid user`
}

// Function to fetch all users mentioned in task
const fetchTaskUsers = async () => {
  const userIds = new Set()
  
  // Collect all unique user IDs from task
  if (task.value.owner_id) userIds.add(task.value.owner_id)
  if (task.value.collaborators) {
    task.value.collaborators.forEach(id => userIds.add(id))
  }
  
  // Fetch user details for all unique IDs
  const fetchPromises = Array.from(userIds).map(userid => fetchUserDetails(userid))
  const results = await Promise.all(fetchPromises)
  console.log(`Fetched ${results.filter(r => r !== null).length} users out of ${userIds.size}`)
}

onMounted(async () => {
  await fetchTaskDetails()
})

const fetchTaskDetails = async () => {
  try {
    loading.value = true
    error.value = null
    
    const taskId = route.params.id
    
    // Reset current task data
    task.value = null
    project.value = null
    parentTask.value = null
    
    // Fetch task details
    const taskResponse = await fetch(`http://localhost:5002/tasks/${taskId}`)
    if (!taskResponse.ok) {
      throw new Error(`Failed to fetch task: ${taskResponse.status}`)
    }
    
    const taskData = await taskResponse.json()
    task.value = taskData.task || taskData

    // Fetch project details if project_id exists
    if (task.value.project_id) {
      try {
        const projectResponse = await fetch(`http://localhost:5001/projects/${task.value.project_id}`)
        if (projectResponse.ok) {
          const projectData = await projectResponse.json()
          project.value = projectData.data || projectData
        } else {
          project.value = null
        }
      } catch (err) {
        console.error('Error fetching project:', err)
        project.value = null
      }
    } else {
      project.value = null
    }

    // Fetch owner details using owner_id
    if (task.value.owner_id) {
      try {
        const ownerResponse = await fetch(`http://localhost:5003/users/${task.value.owner_id}`)
        if (ownerResponse.ok) {
          const responseData = await ownerResponse.json()
          const ownerData = responseData.data
          
          if (ownerData && (ownerData.name || ownerData.username || ownerData.email)) {
            task.value.owner = ownerData.name || ownerData.username || ownerData.email
          } else {
            task.value.owner = null
          }
        } else {
          task.value.owner = null
        }
      } catch (err) {
        task.value.owner = null
      }
    } else {
      task.value.owner = null
    }

    // Fetch subtask details if subtasks array contains IDs
    if (task.value.subtasks && task.value.subtasks.length > 0) {
      try {
        const subtaskPromises = task.value.subtasks.map(async (subtaskId) => {
          if (typeof subtaskId === 'object') {
            return subtaskId
          }
          
          const subtaskResponse = await fetch(`http://localhost:5002/tasks/${subtaskId}`)
          if (subtaskResponse.ok) {
            const subtaskData = await subtaskResponse.json()
            return subtaskData.task || subtaskData
          }
          return null
        })
        
        const subtaskResults = await Promise.all(subtaskPromises)
        task.value.subtasks = subtaskResults.filter(subtask => subtask !== null)
      } catch (err) {
        // Silently handle subtask fetch errors
      }
    }
    
    // Fetch parent task details if parent_task exists
    if (task.value.parent_task) {
      try {
        const parentResponse = await fetch(`http://localhost:5002/tasks/${task.value.parent_task}`)
        if (parentResponse.ok) {
          const parentData = await parentResponse.json()
          parentTask.value = parentData.task || parentData
        }
      } catch (err) {
        // Silently handle parent task fetch errors
      }
    }
    
    // Fetch user details for all users mentioned in task
    await fetchTaskUsers()
    
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/tasks')
}

const navigateToTask = async (taskId) => {
  if (taskId) {
    await router.push({ name: 'task-detail', params: { id: taskId.toString() } })
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'No date'
  
  // Parse the UTC date and convert to Singapore timezone
  const date = new Date(dateString)
  
  // Convert to Singapore timezone (UTC+8)
  return date.toLocaleDateString('en-SG', { 
    timeZone: 'Asia/Singapore',
    year: 'numeric',
    month: 'short', 
    day: 'numeric'
  })
}

const getRelativeDate = (dateString) => {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  
  const nowSG = new Date(new Date().toLocaleString("en-US", {timeZone: "Asia/Singapore"}))
  const dateSG = new Date(date.toLocaleString("en-US", {timeZone: "Asia/Singapore"}))
  
  const diffTime = dateSG.setHours(0,0,0,0) - nowSG.setHours(0,0,0,0)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) {
    return `${Math.abs(diffDays)} days overdue`
  } else if (diffDays === 0) {
    return 'Due today'
  } else if (diffDays === 1) {
    return 'Due tomorrow'
  } else {
    return `Due in ${diffDays} days`
  }
}

const formatFileSize = (bytes) => {
  if (!bytes) return ''
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  if (bytes === 0) return '0 Bytes'
  const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

const getStatusClass = (status) => {
  const statusClassMap = {
    'Ongoing': 'ongoing',
    'Under Review': 'under-review',
    'Completed': 'completed',
    'Unassigned': 'unassigned'
  }
  return statusClassMap[status] || 'unassigned'
}

const getStatusIcon = (status) => {
  const icons = {
    'Ongoing': 'bi-play-circle',
    'Under Review': 'bi-eye',
    'Completed': 'bi-check-circle-fill',
    'Unassigned': 'bi-person-dash'
  }
  return icons[status] || 'bi-circle'
}

const getStatusLabel = (status) => {
  const labels = {
    'Ongoing': 'Ongoing',
    'Under Review': 'Under Review',
    'Completed': 'Completed',
    'Unassigned': 'Unassigned'
  }
  return labels[status]
}

const getPriorityClass = (priority) => {
  const level = parseInt(priority)
  if (level >= 8) return 'priority-high'
  if (level >= 5) return 'priority-medium'
  return 'priority-low'
}

const getTaskTypeClass = () => {
  return task.value?.parent_task ? 'subtask' : 'task'
}

const getTaskTypeIcon = () => {
  return task.value?.parent_task ? 'bi-diagram-2' : 'bi-list-task'
}

const getSubtaskProgress = (task) => {
  if (!task.subtasks || task.subtasks.length === 0) return 0
  const completed = task.subtasks.filter(subtask => subtask.status === 'Completed').length
  return Math.round((completed / task.subtasks.length) * 100)
}

const getCompletedSubtasks = (task) => {
  if (!task.subtasks) return 0
  return task.subtasks.filter(subtask => subtask.status === 'Completed').length
}

const openAttachment = (attachment) => {
  if (attachment.url) {
    window.open(attachment.url, '_blank')
  }
}

const downloadAttachment = (attachment) => {
  console.log('Attempting to download attachment:', attachment)
  
  if (attachment.url) {
    console.log('Downloading from URL:', attachment.url)
    const link = document.createElement('a')
    link.href = attachment.url
    link.download = attachment.name || attachment.filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } else if (attachment.download_url) {
    console.log('Downloading from download_url:', attachment.download_url)
    const link = document.createElement('a')
    link.href = attachment.download_url
    link.download = attachment.name || attachment.filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } else {
    console.error('No URL available for attachment:', attachment)
    alert(`Cannot download "${attachment.name}": No URL available. This usually means the file wasn't uploaded properly.`)
  }
}

// Assign popup methods
const openAssignPopup = () => {
  showAssignPopup.value = true
}

const closeAssignPopup = () => {
  showAssignPopup.value = false
}

const handleAssignmentSuccess = async (assignmentData) => {
  await fetchTaskDetails()
  closeAssignPopup()
}

// Edit popup methods
const openEditPopup = () => {
  showEditPopup.value = true
}

const closeEditPopup = () => {
  showEditPopup.value = false
}

const updateSuccess = async (updateData) => {
  console.log('TaskDetails received update data:', updateData);
  
  // Close popup
  closeEditPopup();
  
  // Small delay then refresh
  await new Promise(resolve => setTimeout(resolve, 300))
  await fetchTaskDetails()
  
  console.log('Task refreshed')
}

// Add this handler function
const handleCommentsUpdate = (comments) => {
  console.log('Comments updated:', comments)
  taskComments.value = comments
}

</script>