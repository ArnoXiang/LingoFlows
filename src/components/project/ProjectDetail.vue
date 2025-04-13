<template>
  <div class="project-detail-container">
    <a-drawer
      v-model:visible="visible"
      :width="drawerWidth"
      :title="drawerTitle"
      unmountOnClose
      @close="closeDrawer"
    >
      <!-- 自定义拖拽条 -->
      <div 
        class="drawer-resize-handle" 
        v-if="visible"
        @mousedown="startResize"
        title="拖拽调整宽度 / Drag to resize"
      >
        <div class="resize-indicator"></div>
      </div>
      <div v-if="project">
        <a-tabs v-model:activeKey="activeTabKey">
          <a-tab-pane key="info" title="项目信息 / Project Info">
            <a-descriptions :column="1" bordered>
              <a-descriptions-item label="项目名称 / Project Name">
                <a-input v-model="project.projectName" v-if="isEditing && userRole === 'LM'" />
                <span v-else>{{ project.projectName }}</span>
              </a-descriptions-item>
              <a-descriptions-item label="项目状态 / Project Status">
                <a-select v-model="project.projectStatus" v-if="isEditing && userRole === 'LM'">
                  <a-option value="pending">待处理 / Pending</a-option>
                  <a-option value="in_progress">进行中 / In Progress</a-option>
                  <a-option value="completed">已完成 / Completed</a-option>
                  <a-option value="cancelled">已取消 / Cancelled</a-option>
                </a-select>
                <a-tag v-else :color="getStatusColor(project.projectStatus)">
                  {{ getStatusText(project.projectStatus) }}
                </a-tag>
              </a-descriptions-item>
              <a-descriptions-item label="请求名称 / Request Name">
                <a-input v-model="project.requestName" v-if="isEditing && userRole === 'LM'" />
                <span v-else>{{ project.requestName }}</span>
              </a-descriptions-item>
              <a-descriptions-item label="项目经理 / Project Manager">
                <a-input v-model="project.projectManager" v-if="isEditing && userRole === 'LM'" />
                <span v-else>{{ project.projectManager }}</span>
              </a-descriptions-item>
              <a-descriptions-item label="创建时间 / Create Time">
                {{ formatDate(project.createTime) }}
              </a-descriptions-item>
              <a-descriptions-item label="源语言 / Source Language">
                <a-select v-model="project.sourceLanguage" v-if="isEditing && userRole === 'LM'">
                  <a-option v-for="lang in languages" :key="lang.code" :value="lang.code">{{ lang.name }}</a-option>
                </a-select>
                <span v-else>{{ getLanguageName(project.sourceLanguage) }}</span>
              </a-descriptions-item>
              <a-descriptions-item label="目标语言 / Target Languages">
                <a-select v-model="project.targetLanguages" multiple v-if="isEditing && userRole === 'LM'">
                  <a-option v-for="lang in languages" :key="lang.code" :value="lang.code">{{ lang.name }}</a-option>
                </a-select>
                <div v-else>
                  <a-tag v-for="lang in project.targetLanguages" :key="lang" style="margin: 2px;">
                    {{ getLanguageName(lang) }}
                  </a-tag>
                </div>
              </a-descriptions-item>
              <a-descriptions-item label="字数 / Word Count">
                <a-input-number v-model="project.wordCount" v-if="isEditing && userRole === 'LM'" />
                <span v-else>{{ project.wordCount }}</span>
              </a-descriptions-item>
              <a-descriptions-item label="预期交付日期 / Expected Delivery Date">
                <a-date-picker v-model="project.expectedDeliveryDate" v-if="isEditing && userRole === 'LM'" />
                <span v-else>{{ formatDate(project.expectedDeliveryDate) }}</span>
              </a-descriptions-item>
              <a-descriptions-item label="附加要求 / Additional Requirements">
                <a-checkbox-group 
                  v-model="project.additionalRequirements" 
                  v-if="isEditing && userRole === 'LM'"
                >
                  <a-checkbox value="lqa">语言质量保证 (LQA) / Linguistic Quality Assurance</a-checkbox>
                  <a-checkbox value="imageTranslation">图像文本翻译 / Image Text Translation</a-checkbox>
                </a-checkbox-group>
                <div v-else>
                  <a-tag v-for="req in project.additionalRequirements" :key="req" style="margin: 2px;">
                    {{ getRequirementText(req) }}
                  </a-tag>
                </div>
              </a-descriptions-item>
            </a-descriptions>
            
            <!-- 任务状态和详细信息 -->
            <div v-if="userRole === 'LM' && isEditing" style="margin-top: 24px;">
              <h3>任务详情 / Task Details</h3>
              <a-form :model="project.tasks">
                <a-collapse>
                  <a-collapse-item header="翻译任务 / Translation Task" key="1">
                    <div v-if="targetLanguagesList.length > 0">
                      <p><b>按语言分配：/ Assign by Language:</b></p>
                      <a-tabs type="card">
                        <a-tab-pane v-for="lang in targetLanguagesList" :key="lang" :title="getLanguageName(lang)">
                          <a-form-item label="负责人 / Assignee">
                            <a-input 
                              v-model="getLanguageAssignment('translation', lang).assignee" 
                              placeholder="翻译人员 / Translator" 
                            />
                          </a-form-item>
                          <a-form-item label="截止日期 / Deadline">
                            <a-date-picker 
                              v-model="getLanguageAssignment('translation', lang).deadline" 
                            />
                          </a-form-item>
                          <a-form-item label="备注 / Notes">
                            <a-textarea 
                              v-model="getLanguageAssignment('translation', lang).notes" 
                              placeholder="任务备注 / Task notes" 
                            />
                          </a-form-item>
                        </a-tab-pane>
                      </a-tabs>
                    </div>
                    <a-form-item label="状态 / Status">
                      <a-select v-model="project.tasks.translation.status">
                        <a-option value="not_started">未开始 / Not Started</a-option>
                        <a-option value="in_progress">进行中 / In Progress</a-option>
                        <a-option value="completed">已完成 / Completed</a-option>
                      </a-select>
                    </a-form-item>
                    <a-form-item label="负责人 / Assignee" v-if="!targetLanguagesList.length">
                      <a-input v-model="project.tasks.translation.assignee" placeholder="翻译人员 / Translator" />
                    </a-form-item>
                    <a-form-item label="截止日期 / Deadline" v-if="!targetLanguagesList.length">
                      <a-date-picker v-model="project.tasks.translation.deadline" />
                    </a-form-item>
                    <a-form-item label="备注 / Notes" v-if="!targetLanguagesList.length">
                      <a-textarea v-model="project.tasks.translation.notes" placeholder="任务备注 / Task notes" />
                    </a-form-item>
                  </a-collapse-item>
                  
                  <a-collapse-item header="LQA任务 / LQA Task" key="2">
                    <div v-if="targetLanguagesList.length > 0">
                      <p><b>按语言分配：/ Assign by Language:</b></p>
                      <a-tabs type="card">
                        <a-tab-pane v-for="lang in targetLanguagesList" :key="lang" :title="getLanguageName(lang)">
                          <a-form-item label="负责人 / Assignee">
                            <a-input 
                              v-model="getLanguageAssignment('lqa', lang).assignee" 
                              placeholder="LQA人员 / LQA Specialist" 
                            />
                          </a-form-item>
                          <a-form-item label="截止日期 / Deadline">
                            <a-date-picker 
                              v-model="getLanguageAssignment('lqa', lang).deadline" 
                            />
                          </a-form-item>
                          <a-form-item label="备注 / Notes">
                            <a-textarea 
                              v-model="getLanguageAssignment('lqa', lang).notes" 
                              placeholder="任务备注 / Task notes" 
                            />
                          </a-form-item>
                        </a-tab-pane>
                      </a-tabs>
                    </div>
                    <a-form-item label="状态 / Status">
                      <a-select v-model="project.tasks.lqa.status">
                        <a-option value="not_started">未开始 / Not Started</a-option>
                        <a-option value="in_progress">进行中 / In Progress</a-option>
                        <a-option value="completed">已完成 / Completed</a-option>
                      </a-select>
                    </a-form-item>
                    <a-form-item label="负责人 / Assignee" v-if="!targetLanguagesList.length">
                      <a-input v-model="project.tasks.lqa.assignee" placeholder="LQA人员 / LQA Specialist" />
                    </a-form-item>
                    <a-form-item label="截止日期 / Deadline" v-if="!targetLanguagesList.length">
                      <a-date-picker v-model="project.tasks.lqa.deadline" />
                    </a-form-item>
                    <a-form-item label="备注 / Notes" v-if="!targetLanguagesList.length">
                      <a-textarea v-model="project.tasks.lqa.notes" placeholder="任务备注 / Task notes" />
                    </a-form-item>
                  </a-collapse-item>
                  
                  <!-- 新增翻译更新任务 -->
                  <a-collapse-item header="翻译更新 / Translation Update" key="3">
                    <div v-if="targetLanguagesList.length > 0">
                      <p><b>按语言分配：/ Assign by Language:</b></p>
                      <a-tabs type="card">
                        <a-tab-pane v-for="lang in targetLanguagesList" :key="lang" :title="getLanguageName(lang)">
                          <a-form-item label="负责人 / Assignee">
                            <a-input 
                              v-model="getLanguageAssignment('translationUpdate', lang).assignee" 
                              placeholder="更新人员 / Update Specialist" 
                            />
                          </a-form-item>
                          <a-form-item label="截止日期 / Deadline">
                            <a-date-picker 
                              v-model="getLanguageAssignment('translationUpdate', lang).deadline" 
                            />
                          </a-form-item>
                          <a-form-item label="备注 / Notes">
                            <a-textarea 
                              v-model="getLanguageAssignment('translationUpdate', lang).notes" 
                              placeholder="任务备注 / Task notes" 
                            />
                          </a-form-item>
                        </a-tab-pane>
                      </a-tabs>
                    </div>
                    <a-form-item label="状态 / Status">
                      <a-select v-model="project.tasks.translationUpdate.status">
                        <a-option value="not_started">未开始 / Not Started</a-option>
                        <a-option value="in_progress">进行中 / In Progress</a-option>
                        <a-option value="completed">已完成 / Completed</a-option>
                      </a-select>
                    </a-form-item>
                    <a-form-item label="负责人 / Assignee" v-if="!targetLanguagesList.length">
                      <a-input v-model="project.tasks.translationUpdate.assignee" placeholder="更新人员 / Update Specialist" />
                    </a-form-item>
                    <a-form-item label="截止日期 / Deadline" v-if="!targetLanguagesList.length">
                      <a-date-picker v-model="project.tasks.translationUpdate.deadline" />
                    </a-form-item>
                    <a-form-item label="备注 / Notes" v-if="!targetLanguagesList.length">
                      <a-textarea v-model="project.tasks.translationUpdate.notes" placeholder="任务备注 / Task notes" />
                    </a-form-item>
                  </a-collapse-item>
                  
                  <!-- 新增LQA报告定稿任务 -->
                  <a-collapse-item header="LQA报告定稿 / LQA Report Finalization" key="4">
                    <div v-if="targetLanguagesList.length > 0">
                      <p><b>按语言分配：/ Assign by Language:</b></p>
                      <a-tabs type="card">
                        <a-tab-pane v-for="lang in targetLanguagesList" :key="lang" :title="getLanguageName(lang)">
                          <a-form-item label="负责人 / Assignee">
                            <a-input 
                              v-model="getLanguageAssignment('lqaReportFinalization', lang).assignee" 
                              placeholder="报告定稿人员 / Report Specialist" 
                            />
                          </a-form-item>
                          <a-form-item label="截止日期 / Deadline">
                            <a-date-picker 
                              v-model="getLanguageAssignment('lqaReportFinalization', lang).deadline" 
                            />
                          </a-form-item>
                          <a-form-item label="备注 / Notes">
                            <a-textarea 
                              v-model="getLanguageAssignment('lqaReportFinalization', lang).notes" 
                              placeholder="任务备注 / Task notes" 
                            />
                          </a-form-item>
                        </a-tab-pane>
                      </a-tabs>
                    </div>
                    <a-form-item label="状态 / Status">
                      <a-select v-model="project.tasks.lqaReportFinalization.status">
                        <a-option value="not_started">未开始 / Not Started</a-option>
                        <a-option value="in_progress">进行中 / In Progress</a-option>
                        <a-option value="completed">已完成 / Completed</a-option>
                      </a-select>
                    </a-form-item>
                    <a-form-item label="负责人 / Assignee" v-if="!targetLanguagesList.length">
                      <a-input v-model="project.tasks.lqaReportFinalization.assignee" placeholder="报告定稿人员 / Report Specialist" />
                    </a-form-item>
                    <a-form-item label="截止日期 / Deadline" v-if="!targetLanguagesList.length">
                      <a-date-picker v-model="project.tasks.lqaReportFinalization.deadline" />
                    </a-form-item>
                    <a-form-item label="备注 / Notes" v-if="!targetLanguagesList.length">
                      <a-textarea v-model="project.tasks.lqaReportFinalization.notes" placeholder="任务备注 / Task notes" />
                    </a-form-item>
                  </a-collapse-item>
                </a-collapse>
              </a-form>
            </div>
            
            <!-- 查看模式下的任务详情显示 -->
            <div v-else-if="project" style="margin-top: 24px;" class="task-details-container">
              <h3>任务详情 / Task Details</h3>
              <a-collapse>
                <!-- 翻译任务详情 -->
                <a-collapse-item header="翻译任务 / Translation Task" key="1">
                  <a-descriptions :column="1" bordered size="small">
                    <a-descriptions-item label="状态 / Status">
                      <a-tag :color="getTaskStatus(project.taskTranslation)">
                        {{ getTaskText(project.taskTranslation) }}
                      </a-tag>
                    </a-descriptions-item>
                    
                    <!-- 如果有目标语言，则显示按语言的分配 -->
                    <template v-if="targetLanguagesList.length > 0">
                      <a-descriptions-item label="按语言分配 / Assignments by Language">
                        <a-table 
                          :data="getTaskAssignmentTableData('translation')" 
                          :pagination="false"
                          :bordered="true"
                          size="small"
                          style="margin-top: 10px; width: 100%;"
                        >
                          <template #columns>
                            <a-table-column title="语言 / Language" data-index="language" :width="120">
                              <template #cell="{ record }">
                                <div style="word-break: normal; white-space: normal;">{{ record.language }}</div>
                              </template>
                            </a-table-column>
                            <a-table-column title="负责人 / Assignee" data-index="assignee" :width="150">
                              <template #cell="{ record }">
                                <div style="word-break: normal; white-space: normal;">{{ record.assignee }}</div>
                              </template>
                            </a-table-column>
                            <a-table-column title="截止日期 / Deadline" data-index="deadline" :width="150">
                              <template #cell="{ record }">
                                <div style="word-break: normal; white-space: normal;">{{ record.deadline }}</div>
                              </template>
                            </a-table-column>
                            <a-table-column title="备注 / Notes" data-index="notes">
                              <template #cell="{ record }">
                                <div style="word-break: normal; white-space: normal;">{{ record.notes }}</div>
                              </template>
                            </a-table-column>
                          </template>
                        </a-table>
                      </a-descriptions-item>
                    </template>
                    
                    <!-- 如果没有目标语言，则显示常规分配 -->
                    <template v-else>
                      <a-descriptions-item label="负责人 / Assignee">
                        {{ project.tasks.translation.assignee || '未分配 / Not Assigned' }}
                      </a-descriptions-item>
                      <a-descriptions-item label="截止日期 / Deadline">
                        {{ project.tasks.translation.deadline ? formatDate(project.tasks.translation.deadline) : '未设置 / Not Set' }}
                      </a-descriptions-item>
                      <a-descriptions-item label="备注 / Notes">
                        {{ project.tasks.translation.notes || '无 / None' }}
                      </a-descriptions-item>
                    </template>
                  </a-descriptions>
                </a-collapse-item>
                
                <!-- LQA任务详情 -->
                <a-collapse-item header="LQA任务 / LQA Task" key="2">
                  <a-descriptions :column="1" bordered size="small">
                    <a-descriptions-item label="状态 / Status">
                      <a-tag :color="getTaskStatus(project.taskLQA)">
                        {{ getTaskText(project.taskLQA) }}
                      </a-tag>
                    </a-descriptions-item>
                    
                    <!-- 如果有目标语言，则显示按语言的分配 -->
                    <template v-if="targetLanguagesList.length > 0">
                      <a-descriptions-item label="按语言分配 / Assignments by Language">
                        <a-table 
                          :data="getTaskAssignmentTableData('lqa')" 
                          :pagination="false"
                          :bordered="true"
                          size="small"
                          style="margin-top: 10px; width: 100%;"
                        >
                          <template #columns>
                            <a-table-column title="语言 / Language" data-index="language" :width="120">
                              <template #cell="{ record }">
                                <div style="word-break: normal; white-space: normal;">{{ record.language }}</div>
                              </template>
                            </a-table-column>
                            <a-table-column title="负责人 / Assignee" data-index="assignee" :width="150">
                              <template #cell="{ record }">
                                <div style="word-break: normal; white-space: normal;">{{ record.assignee }}</div>
                              </template>
                            </a-table-column>
                            <a-table-column title="截止日期 / Deadline" data-index="deadline" :width="150">
                              <template #cell="{ record }">
                                <div style="word-break: normal; white-space: normal;">{{ record.deadline }}</div>
                              </template>
                            </a-table-column>
                            <a-table-column title="备注 / Notes" data-index="notes">
                              <template #cell="{ record }">
                                <div style="word-break: normal; white-space: normal;">{{ record.notes }}</div>
                              </template>
                            </a-table-column>
                          </template>
                        </a-table>
                      </a-descriptions-item>
                    </template>
                    
                    <!-- 如果没有目标语言，则显示常规分配 -->
                    <template v-else>
                      <a-descriptions-item label="负责人 / Assignee">
                        {{ project.tasks.lqa.assignee || '未分配 / Not Assigned' }}
                      </a-descriptions-item>
                      <a-descriptions-item label="截止日期 / Deadline">
                        {{ project.tasks.lqa.deadline ? formatDate(project.tasks.lqa.deadline) : '未设置 / Not Set' }}
                      </a-descriptions-item>
                      <a-descriptions-item label="备注 / Notes">
                        {{ project.tasks.lqa.notes || '无 / None' }}
                      </a-descriptions-item>
                    </template>
                  </a-descriptions>
                </a-collapse-item>
                
                <!-- 翻译更新任务详情 -->
                <a-collapse-item header="翻译更新 / Translation Update" key="3">
                  <a-descriptions :column="1" bordered size="small">
                    <a-descriptions-item label="状态 / Status">
                      <a-tag :color="getTaskStatus(project.taskTranslationUpdate)">
                        {{ getTaskText(project.taskTranslationUpdate) }}
                      </a-tag>
                    </a-descriptions-item>
                    
                    <!-- 如果有目标语言，则显示按语言的分配 -->
                    <template v-if="targetLanguagesList.length > 0">
                      <a-descriptions-item label="按语言分配 / Assignments by Language">
                        <a-table 
                          :data="getTaskAssignmentTableData('translationUpdate')" 
                          :pagination="false"
                          :bordered="true"
                          size="small"
                          style="margin-top: 10px; width: 100%;"
                        >
                          <template #columns>
                            <a-table-column title="语言 / Language" data-index="language" :width="120">
                              <template #cell="{ record }">
                                <div style="word-break: normal; white-space: normal;">{{ record.language }}</div>
                              </template>
                            </a-table-column>
                            <a-table-column title="负责人 / Assignee" data-index="assignee" :width="150">
                              <template #cell="{ record }">
                                <div style="word-break: normal; white-space: normal;">{{ record.assignee }}</div>
                              </template>
                            </a-table-column>
                            <a-table-column title="截止日期 / Deadline" data-index="deadline" :width="150">
                              <template #cell="{ record }">
                                <div style="word-break: normal; white-space: normal;">{{ record.deadline }}</div>
                              </template>
                            </a-table-column>
                            <a-table-column title="备注 / Notes" data-index="notes">
                              <template #cell="{ record }">
                                <div style="word-break: normal; white-space: normal;">{{ record.notes }}</div>
                              </template>
                            </a-table-column>
                          </template>
                        </a-table>
                      </a-descriptions-item>
                    </template>
                    
                    <!-- 如果没有目标语言，则显示常规分配 -->
                    <template v-else>
                      <a-descriptions-item label="负责人 / Assignee">
                        {{ project.tasks.translationUpdate.assignee || '未分配 / Not Assigned' }}
                      </a-descriptions-item>
                      <a-descriptions-item label="截止日期 / Deadline">
                        {{ project.tasks.translationUpdate.deadline ? formatDate(project.tasks.translationUpdate.deadline) : '未设置 / Not Set' }}
                      </a-descriptions-item>
                      <a-descriptions-item label="备注 / Notes">
                        {{ project.tasks.translationUpdate.notes || '无 / None' }}
                      </a-descriptions-item>
                    </template>
                  </a-descriptions>
                </a-collapse-item>
                
                <!-- LQA报告定稿任务详情 -->
                <a-collapse-item header="LQA报告定稿 / LQA Report Finalization" key="4">
                  <a-descriptions :column="1" bordered size="small">
                    <a-descriptions-item label="状态 / Status">
                      <a-tag :color="getTaskStatus(project.taskLQAReportFinalization)">
                        {{ getTaskText(project.taskLQAReportFinalization) }}
                      </a-tag>
                    </a-descriptions-item>
                    
                    <!-- 如果有目标语言，则显示按语言的分配 -->
                    <template v-if="targetLanguagesList.length > 0">
                      <a-descriptions-item label="按语言分配 / Assignments by Language">
                        <a-table 
                          :data="getTaskAssignmentTableData('lqaReportFinalization')" 
                          :pagination="false"
                          :bordered="true"
                          size="small"
                          style="margin-top: 10px; width: 100%;"
                        >
                          <template #columns>
                            <a-table-column title="语言 / Language" data-index="language" :width="120">
                              <template #cell="{ record }">
                                <div style="word-break: normal; white-space: normal;">{{ record.language }}</div>
                              </template>
                            </a-table-column>
                            <a-table-column title="负责人 / Assignee" data-index="assignee" :width="150">
                              <template #cell="{ record }">
                                <div style="word-break: normal; white-space: normal;">{{ record.assignee }}</div>
                              </template>
                            </a-table-column>
                            <a-table-column title="截止日期 / Deadline" data-index="deadline" :width="150">
                              <template #cell="{ record }">
                                <div style="word-break: normal; white-space: normal;">{{ record.deadline }}</div>
                              </template>
                            </a-table-column>
                            <a-table-column title="备注 / Notes" data-index="notes">
                              <template #cell="{ record }">
                                <div style="word-break: normal; white-space: normal;">{{ record.notes }}</div>
                              </template>
                            </a-table-column>
                          </template>
                        </a-table>
                      </a-descriptions-item>
                    </template>
                    
                    <!-- 如果没有目标语言，则显示常规分配 -->
                    <template v-else>
                      <a-descriptions-item label="负责人 / Assignee">
                        {{ project.tasks.lqaReportFinalization.assignee || '未分配 / Not Assigned' }}
                      </a-descriptions-item>
                      <a-descriptions-item label="截止日期 / Deadline">
                        {{ project.tasks.lqaReportFinalization.deadline ? formatDate(project.tasks.lqaReportFinalization.deadline) : '未设置 / Not Set' }}
                      </a-descriptions-item>
                      <a-descriptions-item label="备注 / Notes">
                        {{ project.tasks.lqaReportFinalization.notes || '无 / None' }}
                      </a-descriptions-item>
                    </template>
                  </a-descriptions>
                </a-collapse-item>
              </a-collapse>
            </div>
            
            <div class="task-status" style="margin-top: 24px;" v-if="userRole === 'BO'">
              <h3>任务状态 / Task Status</h3>
              <a-descriptions :column="1" bordered>
                <a-descriptions-item label="翻译任务 / Translation Task">
                  <a-tag :color="getTaskStatus(project.taskTranslation)">
                    {{ getTaskText(project.taskTranslation) }}
                  </a-tag>
                </a-descriptions-item>
                <a-descriptions-item label="LQA任务 / LQA Task">
                  <a-tag :color="getTaskStatus(project.taskLQA)">
                    {{ getTaskText(project.taskLQA) }}
                  </a-tag>
                </a-descriptions-item>
                <a-descriptions-item label="翻译更新 / Translation Update">
                  <a-tag :color="getTaskStatus(project.taskTranslationUpdate)">
                    {{ getTaskText(project.taskTranslationUpdate) }}
                  </a-tag>
                </a-descriptions-item>
                <a-descriptions-item label="LQA报告定稿 / LQA Report Finalization">
                  <a-tag :color="getTaskStatus(project.taskLQAReportFinalization)">
                    {{ getTaskText(project.taskLQAReportFinalization) }}
                  </a-tag>
                </a-descriptions-item>
              </a-descriptions>
            </div>
          </a-tab-pane>
          
          <!-- 新增文件管理标签页 -->
          <a-tab-pane key="files" title="项目文件 / Project Files">
            <div class="project-files-container">
              <!-- 内嵌FileManager组件，明确设置visible为true -->
              <FileManager
                ref="fileManagerRef"
                :projectId="project.id"
                :userRole="userRole"
                :userId="userId"
                :visible="true"
                @refresh-files="handleFilesRefreshed"
              />
              
              <!-- 如果需要额外的上传按钮，可以放在这里 -->
              <div class="upload-button-container" style="margin-top: 16px; text-align: right;">
                <a-button type="primary" @click="openFileUploadModal">
                  上传文件 / Upload Files
                </a-button>
              </div>
            </div>
          </a-tab-pane>
        </a-tabs>
        
        <div class="drawer-footer" style="margin-top: 24px; text-align: right;">
          <a-space>
            <a-button @click="closeDrawer">
              关闭 / Close
            </a-button>
            <a-button type="primary" @click="saveProject" v-if="userRole === 'LM' && isEditing">
              保存 / Save
            </a-button>
          </a-space>
        </div>
      </div>
    </a-drawer>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits, computed, watch, nextTick } from 'vue';
import { Message } from '@arco-design/web-vue';
import axios from 'axios';
import { languages } from '../../utils/languages';
import { 
  getStatusColor, 
  getStatusText, 
  getTaskStatus, 
  getTaskText,
  getRequirementText,
  getLanguageName,
  formatDate 
} from './utils/projectUtils';
import FileManager from './FileManager.vue'; // 导入FileManager组件

const props = defineProps({
  userRole: {
    type: String,
    default: ''
  },
  userId: {
    type: Number,
    default: null
  }
});

const emit = defineEmits(['close', 'update', 'files-refreshed']);

// 状态
const visible = ref(false);
const drawerTitle = ref('项目详情 / Project Details');
const project = ref(null);
const isEditing = ref(false);
const activeTabKey = ref('info'); // 当前激活的标签页
const fileManagerRef = ref(null); // 文件管理器引用
const drawerWidth = ref(800); // 添加drawerWidth状态

// 用于拖拽调整抽屉宽度
const isResizing = ref(false);
const minDrawerWidth = 600; // 最小宽度
const maxDrawerWidth = 1200; // 最大宽度

// 目标语言列表计算属性
const targetLanguagesList = computed(() => {
  if (!project.value || !project.value.targetLanguages) {
    return [];
  }

  try {
    // 如果目标语言是数组，直接返回有效的语言代码
    if (Array.isArray(project.value.targetLanguages)) {
      return project.value.targetLanguages.filter(Boolean);
    }

    // 如果目标语言是字符串，按逗号分割并过滤掉空值
    return project.value.targetLanguages
      .split(',')
      .map(lang => lang.trim())
      .filter(Boolean);
  } catch (error) {
    console.error('处理目标语言列表时出错:', error);
    return [];
  }
});

// 按语言分配任务的数据结构
const languageAssignments = ref({
  translation: {},
  lqa: {},
  translationUpdate: {},
  lqaReportFinalization: {}
});

// 初始化语言分配数据
const initLanguageAssignments = (languages, existingAssignments = {}) => {
  const taskTypes = ['translation', 'lqa', 'translationUpdate', 'lqaReportFinalization'];
  
  // 先确保languageAssignments各字段都初始化为对象
  taskTypes.forEach(taskType => {
    if (!languageAssignments.value[taskType]) {
      languageAssignments.value[taskType] = {};
    }
  });
  
  // 仅在有语言时才进行初始化
  if (!languages || languages.length === 0) {
    return;
  }
  
  // 为每种任务类型初始化
  taskTypes.forEach(taskType => {
    // 为每种语言初始化
    languages.forEach(lang => {
      // 如果语言代码为空，跳过
      if (!lang) return;
      
      // 如果不存在该语言的对象，创建它
      if (!languageAssignments.value[taskType][lang]) {
        languageAssignments.value[taskType][lang] = {
          assignee: '',
          deadline: null,
          notes: ''
        };
      }
      
      // 如果存在现有分配，使用它更新数据
      const existing = existingAssignments[taskType] && existingAssignments[taskType][lang];
      if (existing) {
        languageAssignments.value[taskType][lang].assignee = existing.assignee || '';
        languageAssignments.value[taskType][lang].deadline = existing.deadline || null;
        languageAssignments.value[taskType][lang].notes = existing.notes || '';
      }
    });
  });
  
  console.log("初始化后的语言分配数据:", JSON.stringify(languageAssignments.value));
};

// 格式化语言分配数据用于提交
const formatLanguageAssignmentsForSubmit = () => {
  const result = [];
  const taskTypes = ['translation', 'lqa', 'translationUpdate', 'lqaReportFinalization'];
  
  if (!project.value || !project.value.id) return result;
  
  taskTypes.forEach(taskType => {
    if (languageAssignments.value[taskType]) {
      Object.keys(languageAssignments.value[taskType]).forEach(lang => {
        const assignment = languageAssignments.value[taskType][lang];
        if (assignment.assignee) {
          let deadline = assignment.deadline;
          if (deadline instanceof Date) {
            deadline = deadline.toISOString().split('T')[0];
          }
          
          result.push({
            project_id: project.value.id,
            task_type: taskType,
            language: lang,
            assignee: assignment.assignee,
            deadline: deadline,
            notes: assignment.notes || ''
          });
        }
      });
    }
  });
  
  return result;
};

// 为表格获取任务分配数据
const getTaskAssignmentTableData = (taskType) => {
  if (!targetLanguagesList.value.length) {
    return [];
  }
  
  // 确保有语言分配数据
  if (!languageAssignments.value || !languageAssignments.value[taskType]) {
    return targetLanguagesList.value.map(lang => ({
      language: getLanguageName(lang),
      assignee: '未分配 / Not Assigned',
      deadline: '未设置 / Not Set',
      notes: '无 / None'
    }));
  }
  
  return targetLanguagesList.value.map(lang => {
    let assignment = { assignee: '', deadline: null, notes: '' };
    
    // 尝试获取语言分配
    if (languageAssignments.value[taskType][lang]) {
      assignment = languageAssignments.value[taskType][lang];
    }
    
    return {
      language: getLanguageName(lang),
      assignee: assignment.assignee || '未分配 / Not Assigned',
      deadline: assignment.deadline ? formatDate(assignment.deadline) : '未设置 / Not Set',
      notes: assignment.notes || '无 / None'
    };
  });
};

// 从API响应加载语言分配数据
const loadLanguageAssignmentsFromResponse = (assignments) => {
  // 初始化数据结构
  const result = {
    translation: {},
    lqa: {},
    translationUpdate: {},
    lqaReportFinalization: {}
  };
  
  // 处理每个分配
  assignments.forEach(assignment => {
    const { task_type, language, assignee, deadline, notes } = assignment;
    
    if (!result[task_type]) {
      result[task_type] = {};
    }
    
    result[task_type][language] = {
      assignee: assignee || '',
      deadline: deadline ? new Date(deadline) : null,
      notes: notes || ''
    };
  });
  
  return result;
};

// 获取特定任务类型和语言的分配对象
const getLanguageAssignment = (taskType, language) => {
  // 确保taskType有效
  if (!languageAssignments.value[taskType]) {
    languageAssignments.value[taskType] = {};
  }
  
  // 确保语言对象有效
  if (!languageAssignments.value[taskType][language]) {
    languageAssignments.value[taskType][language] = {
      assignee: '',
      deadline: null,
      notes: ''
    };
  }
  
  return languageAssignments.value[taskType][language];
};

// 加载项目任务分配
const loadProjectTaskAssignments = async (projectId) => {
  if (!projectId) return Promise.resolve([]);
  
  try {
    // 获取token
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('未找到认证令牌，无法获取任务分配数据');
      return Promise.resolve([]);
    }
    
    // 发送请求获取任务分配数据
    const response = await axios.get(`http://localhost:5000/api/project-task-assignments/${projectId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.data && Array.isArray(response.data)) {
      // 处理响应数据
      const assignmentsData = loadLanguageAssignmentsFromResponse(response.data);
      
      // 更新语言分配数据
      languageAssignments.value = assignmentsData;
      
      console.log('已加载项目任务分配数据:', assignmentsData);
      return Promise.resolve(response.data);
    }
    
    return Promise.resolve([]);
  } catch (error) {
    console.error('获取项目任务分配数据失败:', error);
    // 即使获取失败，也要初始化空的任务分配
    initLanguageAssignments(targetLanguagesList.value);
    return Promise.reject(error);
  }
};

// 监听标签页变化
watch(() => activeTabKey.value, async (newVal) => {
  if (newVal === 'files' && project.value && project.value.id) {
    console.log('切换到文件标签页，执行自动加载文件');
    
    // 加载文件和修复映射关系
    if (fileManagerRef.value) {
      try {
        // 加载项目文件前先进行自动修复
        console.log('开始修复文件映射并加载文件...');
        
        // 先显示加载状态
        fileManagerRef.value.loadingFiles = true;
        
        // 修复映射关系（静默模式）
        try {
          await fileManagerRef.value.fixFileMappings(true);
        } catch (error) {
          console.error('自动修复文件映射失败:', error);
          // 继续加载文件，不中断流程
        }
        
        // 加载项目文件
        await fileManagerRef.value.loadProjectFiles(project.value.id);
        
        // 通知父组件文件已刷新
        emit('files-refreshed');
      } catch (error) {
        console.error('自动加载文件失败:', error);
        Message.error('加载项目文件失败，请稍后重试');
      }
    }
  }
});

// 方法
const openDrawer = (currentProject, mode = 'view') => {
  // 处理任务详细信息
  let translationDeadline = null;
  if (currentProject.translationDeadline) {
    try {
      translationDeadline = new Date(currentProject.translationDeadline);
    } catch (error) {
      console.error('处理翻译截止日期时出错:', error);
    }
  }
  
  let lqaDeadline = null;
  if (currentProject.lqaDeadline) {
    try {
      lqaDeadline = new Date(currentProject.lqaDeadline);
    } catch (error) {
      console.error('处理LQA截止日期时出错:', error);
    }
  }
  
  let translationUpdateDeadline = null;
  if (currentProject.translationUpdateDeadline) {
    try {
      translationUpdateDeadline = new Date(currentProject.translationUpdateDeadline);
    } catch (error) {
      console.error('处理翻译更新截止日期时出错:', error);
    }
  }
  
  let lqaReportFinalizationDeadline = null;
  if (currentProject.lqaReportFinalizationDeadline) {
    try {
      lqaReportFinalizationDeadline = new Date(currentProject.lqaReportFinalizationDeadline);
    } catch (error) {
      console.error('处理LQA报告定稿截止日期时出错:', error);
    }
  }
  
  // 处理预期交付日期
  let expectedDeliveryDate = currentProject.expectedDeliveryDate;
  if (expectedDeliveryDate) {
    try {
      // 尝试将日期字符串转换为日期对象
      const dateObj = new Date(expectedDeliveryDate);
      if (!isNaN(dateObj.getTime())) {
        expectedDeliveryDate = dateObj;
      }
    } catch (error) {
      console.error('处理日期字段时出错:', error);
    }
  }
  
  // 初始化任务字段
  const initTaskField = (status, assignee, deadline, notes) => {
    return {
      status: status || 'not_started',
      assignee: assignee || '',
      deadline: deadline || null,
      notes: notes || ''
    };
  };
  
  // 克隆项目数据，避免直接修改原始数据
  project.value = {
    ...currentProject,
    expectedDeliveryDate,
    tasks: {
      translation: initTaskField(
        currentProject.taskTranslation,
        currentProject.translationAssignee,
        translationDeadline,
        currentProject.translationNotes
      ),
      lqa: initTaskField(
        currentProject.taskLQA,
        currentProject.lqaAssignee,
        lqaDeadline,
        currentProject.lqaNotes
      ),
      translationUpdate: initTaskField(
        currentProject.taskTranslationUpdate,
        currentProject.translationUpdateAssignee,
        translationUpdateDeadline,
        currentProject.translationUpdateNotes
      ),
      lqaReportFinalization: initTaskField(
        currentProject.taskLQAReportFinalization,
        currentProject.lqaReportFinalizationAssignee,
        lqaReportFinalizationDeadline,
        currentProject.lqaReportFinalizationNotes
      )
    }
  };
  
  isEditing.value = mode === 'edit';
  drawerTitle.value = isEditing.value 
    ? `编辑项目 / Edit Project: ${currentProject.projectName}`
    : `项目详情 / Project Details: ${currentProject.projectName}`;
  
  visible.value = true;
  
  // 在抽屉打开后延迟设置拖拽把手位置
  nextTick(() => {
    // 计算抽屉左侧边缘位置并设置把手
    const drawerLeftEdge = window.innerWidth - drawerWidth.value;
    const resizeHandle = document.querySelector('.drawer-resize-handle');
    if (resizeHandle) {
      resizeHandle.style.left = `${drawerLeftEdge}px`;
      
      // 设置指示器位置
      const indicator = resizeHandle.querySelector('.resize-indicator');
      if (indicator) {
        indicator.style.left = `${drawerLeftEdge + 3}px`;
      }
    }
  });
  
  // 根据不同场景选择初始标签页
  if (isEditing.value) {
    activeTabKey.value = 'info'; // 编辑模式下默认显示信息标签页
  } else {
    // 查看模式默认显示项目信息
    activeTabKey.value = 'info';
  }
  
  // 初始化语言分配
  const languages = Array.isArray(project.value.targetLanguages) 
    ? project.value.targetLanguages 
    : (project.value.targetLanguages || '').split(',').map(lang => lang.trim()).filter(Boolean);
  
  console.log("目标语言列表:", languages);
  
  // 先初始化空的分配数据
  initLanguageAssignments(languages);
  
  // 不管是编辑模式还是查看模式，都加载项目的任务分配数据
  if (project.value && project.value.id) {
    loadProjectTaskAssignments(project.value.id).then(() => {
      // 确保在任务分配数据加载完成后更新UI
      if (!isEditing.value) {
        console.log('查看模式：任务分配数据已加载');
        // 强制更新组件以显示新的数据
        nextTick(() => {
          // 如果需要，可以在这里添加额外的UI更新逻辑
        });
      }
    }).catch(error => {
      console.error('加载任务分配数据失败:', error);
    });
  }
  
  // 如果文件管理器引用存在，加载项目文件
  if (project.value && project.value.id && fileManagerRef.value) {
    // 在nextTick中执行，确保DOM已经更新
    nextTick(() => {
      fileManagerRef.value.loadProjectFiles(project.value.id);
    });
  }
};

const closeDrawer = () => {
  visible.value = false;
  emit('close');
};

// 打开文件上传模态框
const openFileUploadModal = () => {
  if (!project.value || !project.value.id) {
    Message.error('项目ID不存在，无法上传文件 / Project ID does not exist, cannot upload files');
    return;
  }
  
  if (fileManagerRef.value) {
    fileManagerRef.value.openUploadModal(project.value.id);
  }
};

// 处理文件刷新事件
const handleFilesRefreshed = () => {
  console.log('项目文件已刷新');
  emit('files-refreshed');
};

// 切换到文件标签页
const switchToFilesTab = () => {
  if (!project.value || !project.value.id) {
    console.warn('无法切换到文件标签页：项目不存在或没有ID');
    return;
  }
  
  console.log('切换到文件标签页');
  activeTabKey.value = 'files';
};

const saveProject = async () => {
  if (!project.value) return;
  
  // 检查用户角色
  if (props.userRole !== 'LM') {
    Message.error('只有本地化经理可以更新项目 / Only Localization Managers can update projects');
    return;
  }
  
  try {
    // 格式化日期为字符串
    let formattedExpectedDeliveryDate = project.value.expectedDeliveryDate;
    if (formattedExpectedDeliveryDate instanceof Date) {
      formattedExpectedDeliveryDate = formattedExpectedDeliveryDate.toISOString().split('T')[0]; // 格式化为 YYYY-MM-DD
    }
    
    // 格式化任务截止日期
    let formattedTranslationDeadline = project.value.tasks.translation.deadline;
    if (formattedTranslationDeadline instanceof Date) {
      formattedTranslationDeadline = formattedTranslationDeadline.toISOString().split('T')[0];
    }
    
    let formattedLQADeadline = project.value.tasks.lqa.deadline;
    if (formattedLQADeadline instanceof Date) {
      formattedLQADeadline = formattedLQADeadline.toISOString().split('T')[0];
    }
    
    let formattedTranslationUpdateDeadline = project.value.tasks.translationUpdate.deadline;
    if (formattedTranslationUpdateDeadline instanceof Date) {
      formattedTranslationUpdateDeadline = formattedTranslationUpdateDeadline.toISOString().split('T')[0];
    }
    
    let formattedLQAReportFinalizationDeadline = project.value.tasks.lqaReportFinalization.deadline;
    if (formattedLQAReportFinalizationDeadline instanceof Date) {
      formattedLQAReportFinalizationDeadline = formattedLQAReportFinalizationDeadline.toISOString().split('T')[0];
    }
    
    // 准备更新的项目数据
    const updatedProject = {
      id: project.value.id,
      projectName: project.value.projectName,
      projectStatus: project.value.projectStatus,
      requestName: project.value.requestName,
      projectManager: project.value.projectManager,
      
      // 保留创建时间字段，防止被覆盖
      createTime: project.value.createTime,
      
      // 任务状态
      taskTranslation: project.value.tasks.translation.status,
      taskLQA: project.value.tasks.lqa.status,
      taskTranslationUpdate: project.value.tasks.translationUpdate.status,
      taskLQAReportFinalization: project.value.tasks.lqaReportFinalization.status,
      
      // 任务详细信息
      translationAssignee: project.value.tasks.translation.assignee || '',
      translationDeadline: formattedTranslationDeadline || null,
      translationNotes: project.value.tasks.translation.notes || '',
      
      lqaAssignee: project.value.tasks.lqa.assignee || '',
      lqaDeadline: formattedLQADeadline || null,
      lqaNotes: project.value.tasks.lqa.notes || '',
      
      translationUpdateAssignee: project.value.tasks.translationUpdate.assignee || '',
      translationUpdateDeadline: formattedTranslationUpdateDeadline || null,
      translationUpdateNotes: project.value.tasks.translationUpdate.notes || '',
      
      lqaReportFinalizationAssignee: project.value.tasks.lqaReportFinalization.assignee || '',
      lqaReportFinalizationDeadline: formattedLQAReportFinalizationDeadline || null,
      lqaReportFinalizationNotes: project.value.tasks.lqaReportFinalization.notes || '',
      
      // 其他信息
      sourceLanguage: project.value.sourceLanguage,
      targetLanguages: Array.isArray(project.value.targetLanguages) 
        ? project.value.targetLanguages.join(',') 
        : project.value.targetLanguages,
      wordCount: project.value.wordCount,
      expectedDeliveryDate: formattedExpectedDeliveryDate,
      additionalRequirements: Array.isArray(project.value.additionalRequirements) 
        ? project.value.additionalRequirements.join(',') 
        : project.value.additionalRequirements,
    };
    
    // 添加按语言任务分配数据
    updatedProject.taskAssignments = formatLanguageAssignmentsForSubmit();
    
    console.log('准备更新项目数据:', updatedProject);
    
    // 发送更新请求
    const response = await axios.put(`http://localhost:5000/api/projects/${updatedProject.id}`, updatedProject);
    
    if (response.status === 200) {
      Message.success('项目更新成功 / Project updated successfully');
      visible.value = false;
      emit('update', updatedProject); // 通知父组件更新成功
    } else {
      throw new Error('更新失败 / Update failed');
    }
  } catch (error) {
    console.error('Error updating project:', error);
    
    let errorMessage = '更新失败 / Update failed';
    
    if (error.response) {
      // 服务器返回了错误响应
      console.error('错误响应:', error.response.data);
      console.error('状态码:', error.response.status);
      errorMessage = `更新失败: ${error.response.data?.error || error.response.statusText}`;
    } else if (error.request) {
      // 请求已发送但没有收到响应
      console.error('请求已发送但没有收到响应:', error.request);
      errorMessage = '无法连接到服务器，请检查网络连接 / Cannot connect to server, please check your network';
    } else {
      // 设置请求时发生错误
      errorMessage = `更新失败: ${error.message}`;
    }
    
    Message.error(errorMessage);
  }
};

// 开始拖拽
const startResize = (e) => {
  // 阻止默认事件
  e.preventDefault();
  
  isResizing.value = true;
  
  // 计算抽屉左侧边缘的位置(从右侧打开，所以是窗口宽度减去抽屉宽度)
  const drawerLeftEdge = window.innerWidth - drawerWidth.value;
  
  // 动态设置拖拽把手和指示器的位置
  const resizeHandle = e.currentTarget;
  resizeHandle.style.left = `${drawerLeftEdge}px`;
  
  // 获取指示器元素并设置其位置
  const indicator = resizeHandle.querySelector('.resize-indicator');
  if (indicator) {
    indicator.style.left = `${drawerLeftEdge + 3}px`;
  }
  
  // 添加鼠标移动和松开事件监听
  document.addEventListener('mousemove', handleResize);
  document.addEventListener('mouseup', stopResize);
  
  // 添加一个遮罩避免文本选择等问题
  const resizeMask = document.createElement('div');
  resizeMask.id = 'resize-mask';
  resizeMask.style.position = 'fixed';
  resizeMask.style.top = '0';
  resizeMask.style.left = '0';
  resizeMask.style.right = '0';
  resizeMask.style.bottom = '0';
  resizeMask.style.zIndex = '10000';
  resizeMask.style.cursor = 'col-resize';
  document.body.appendChild(resizeMask);
  
  // 更改鼠标样式
  document.body.style.cursor = 'col-resize';
};

// 处理拖拽过程
const handleResize = (e) => {
  if (!isResizing.value) return;
  
  // 计算新宽度 - 抽屉从右侧打开，所以鼠标越靠左，抽屉越宽
  const newWidth = window.innerWidth - e.clientX;
  
  // 限制在最小和最大宽度范围内
  if (newWidth >= minDrawerWidth && newWidth <= maxDrawerWidth) {
    drawerWidth.value = newWidth;
    
    // 更新拖拽把手和指示器的位置
    const drawerLeftEdge = e.clientX;
    const resizeHandle = document.querySelector('.drawer-resize-handle');
    if (resizeHandle) {
      resizeHandle.style.left = `${drawerLeftEdge}px`;
      
      // 更新指示器位置
      const indicator = resizeHandle.querySelector('.resize-indicator');
      if (indicator) {
        indicator.style.left = `${drawerLeftEdge + 3}px`;
      }
    }
  }
};

// 停止拖拽
const stopResize = () => {
  isResizing.value = false;
  
  // 移除事件监听
  document.removeEventListener('mousemove', handleResize);
  document.removeEventListener('mouseup', stopResize);
  
  // 移除遮罩
  const resizeMask = document.getElementById('resize-mask');
  if (resizeMask) {
    document.body.removeChild(resizeMask);
  }
  
  // 恢复鼠标样式
  document.body.style.cursor = 'default';
};

// 监听抽屉可见性和宽度变化，更新拖拽把手位置
watch([visible, drawerWidth], ([newVisible, newWidth]) => {
  if (newVisible) {
    // 延迟执行以确保抽屉已渲染
    nextTick(() => {
      // 计算抽屉左侧边缘的位置
      const drawerLeftEdge = window.innerWidth - newWidth;
      
      // 获取拖拽把手元素
      const resizeHandle = document.querySelector('.drawer-resize-handle');
      if (resizeHandle) {
        resizeHandle.style.left = `${drawerLeftEdge}px`;
        
        // 获取指示器元素并设置其位置
        const indicator = resizeHandle.querySelector('.resize-indicator');
        if (indicator) {
          indicator.style.left = `${drawerLeftEdge + 3}px`;
        }
      }

      // 动态插入样式以确保状态标签文字为黑色
      ensureStatusTagsTextColor();
    });
  }
});

// 确保状态标签文字颜色为黑色的函数
const ensureStatusTagsTextColor = () => {
  // 查找所有抽屉内的标签
  const drawerContent = document.querySelector('.arco-drawer-content');
  if (!drawerContent) return;

  // 查找所有标签
  const tags = drawerContent.querySelectorAll('.arco-tag');
  
  // 直接修改每个标签的样式
  tags.forEach(tag => {
    tag.style.color = '#000000';
    
    // 修改所有子元素
    Array.from(tag.querySelectorAll('*')).forEach(el => {
      el.style.color = '#000000';
    });
  });

  console.log(`已将${tags.length}个标签设置为黑色文字`);
};

// 暴露方法给父组件
defineExpose({
  openDrawer,
  // 添加便捷方法
  viewProject: (project) => openDrawer(project, 'view'),
  editProject: (project) => openDrawer(project, 'edit'),
  switchToFilesTab
});
</script>

<style scoped>
.project-detail-container {
  width: 100%;
}

.project-files-container {
  margin-top: 16px;
}

.upload-button-container {
  margin-top: 16px;
  text-align: right;
}

.task-details-container {
  margin-top: 16px;
}

.task-details-container h3 {
  margin-bottom: 16px;
  font-size: 18px;
  color: var(--color-text-1);
}

.task-details-container h4 {
  margin: 10px 0;
  font-size: 16px;
  color: var(--color-text-2);
}

.task-details-container .arco-collapse-item {
  margin-bottom: 16px;
}

.task-details-container .arco-table-th {
  background-color: var(--color-fill-2);
  font-weight: 600;
}

.task-details-container .arco-table-container {
  width: 100%;
  overflow-x: auto;
}

.task-details-container .arco-table-td {
  word-break: normal;
  white-space: normal;
  max-width: 200px;
}

.task-details-container .arco-descriptions-item-content {
  width: 100%;
}

/* 抽屉可调整大小样式 */
:deep(.arco-drawer-resize-trigger) {
  width: 5px;
  background-color: var(--color-fill-3);
  transition: background-color 0.2s;
}

:deep(.arco-drawer-resize-trigger:hover) {
  background-color: var(--color-primary-light-4);
  cursor: col-resize;
}

:deep(.arco-drawer-body) {
  overflow-x: hidden;
  padding: 16px;
}

/* 自定义拖拽把手 */
.drawer-resize-handle {
  position: fixed; /* 改为fixed定位，使其不随内容滚动 */
  top: 0;
  /* 把手的位置会在JavaScript中动态计算和设置 */
  width: 15px; /* 增加点击区域宽度，便于操作 */
  height: 100vh; /* 设置为视口高度，确保覆盖整个屏幕高度 */
  background-color: transparent;
  cursor: col-resize;
  z-index: 2001;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drawer-resize-handle:hover,
.drawer-resize-handle:active {
  background-color: rgba(64, 158, 255, 0.3); /* 保持原有的悬停效果 */
}

/* 拖拽指示器 */
.resize-indicator {
  width: 6px; /* 增加宽度，使其更加明显 */
  height: 100vh; /* 设置为视口高度，确保指示器始终覆盖整个屏幕高度 */
  background-color: rgba(64, 158, 255, 0.5);
  border-radius: 3px;
  position: fixed; /* 改为fixed定位，使其不随内容滚动 */
  left: 3px;
  top: 0;
  bottom: 0;
  visibility: visible; /* 保持始终可见 */
  opacity: 0.3;
  transition: opacity 0.2s;
}

.drawer-resize-handle:hover .resize-indicator {
  opacity: 1; /* 悬停时完全不透明 */
  background-color: rgba(64, 158, 255, 0.8); /* 悬停时加深颜色 */
}

/* 调整抽屉层级确保边缘可拖拽 */
:deep(.arco-drawer) {
  overflow: visible !important;
}

/* 抽屉中状态标签文本 - 更精确的选择器 */
:deep(.arco-drawer-content) .arco-tag {
  color: #000000 !important;
}

/* 确保标签内部的所有文本元素都是黑色 */
:deep(.arco-drawer-content) .arco-tag * {
  color: #000000 !important;
}

/* 直接针对标签内部的span元素 */
:deep(.arco-drawer-content) .arco-tag span {
  color: #000000 !important;
}

/* 针对特定类型的标签 - 进行中状态 */
:deep(.arco-drawer-content) .arco-tag-blue {
  color: #000000 !important;
}

:deep(.arco-drawer-content) .arco-tag-green {
  color: #000000 !important;
}

:deep(.arco-drawer-content) .arco-tag-orange {
  color: #000000 !important;
}

:deep(.arco-drawer-content) .arco-tag-red {
  color: #000000 !important;
}

:deep(.arco-drawer-content) .arco-tag-gray {
  color: #000000 !important;
}

/* 任务状态标签文本 */
.task-details-container .arco-tag,
.task-details-container .arco-tag * {
  color: #000000 !important;
}

/* 覆盖任何可能的内联样式 */
:deep(.arco-drawer-content) [style*="color"] {
  color: #000000 !important;
}

/* 移除之前不兼容的选择器 */
</style> 