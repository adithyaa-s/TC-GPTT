/**
 * CoursesWidget.tsx - WITH COMPREHENSIVE LOGGING
 * 
 * This version logs everything to help debug why the widget isn't loading
 */

import React, { useState, useEffect, useMemo } from 'react';
import { createRoot } from 'react-dom/client';

// =============================================================================
// LOGGING HELPER
// =============================================================================

function log(category: string, message: string, data?: any) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [${category}] ${message}`;
  
  console.log(logMessage);
  if (data !== undefined) {
    console.log('Data:', data);
  }
  
  // Also show in UI for debugging
  const debugDiv = document.getElementById('debug-log');
  if (debugDiv) {
    const entry = document.createElement('div');
    entry.style.fontSize = '11px';
    entry.style.padding = '4px';
    entry.style.borderBottom = '1px solid #eee';
    entry.style.fontFamily = 'monospace';
    entry.textContent = logMessage;
    debugDiv.appendChild(entry);
    debugDiv.scrollTop = debugDiv.scrollHeight;
  }
}

// =============================================================================
// Type Definitions
// =============================================================================

interface Course {
  courseId: string;
  courseName: string;
  subTitle?: string;
  description?: string;
  publishStatus: string;
  enrolledCount?: number;
  rating?: number;
  createdTime?: string;
}

interface CoursesMetadata {
  courses: Course[];
  courseCategories?: any[];
  totalCourseCount: number;
  stats?: {
    total: number;
    published: number;
    draft: number;
  };
}

interface WidgetState {
  viewMode: 'grid' | 'list';
  sortBy: 'created' | 'name' | 'enrolled';
  filterBy: 'all' | 'draft' | 'published';
  searchQuery: string;
}

declare global {
  interface Window {
    openai?: {
      toolOutput?: any;
      toolResponseMetadata?: any;
      toolInput?: any;
      widgetState?: WidgetState;
      setWidgetState?: (state: WidgetState) => void;
      sendFollowUpMessage?: (params: { prompt: string }) => Promise<void>;
      callTool?: (name: string, args: any) => Promise<any>;
      theme?: 'light' | 'dark';
      locale?: string;
    };
  }
}

// =============================================================================
// Main Component
// =============================================================================

function CoursesWidget() {
  log('INIT', 'Widget component mounting');
  
  const [debugMode, setDebugMode] = useState(true);
  const [renderKey, setRenderKey] = useState(0);
  
  // Log window.openai availability
  useEffect(() => {
    log('CHECK', 'Checking window.openai...', {
      exists: !!window.openai,
      keys: window.openai ? Object.keys(window.openai) : []
    });
    
    if (window.openai) {
      log('OPENAI', 'window.openai contents:', {
        toolOutput: window.openai.toolOutput,
        toolResponseMetadata: window.openai.toolResponseMetadata,
        toolInput: window.openai.toolInput,
        widgetState: window.openai.widgetState,
        hasSetWidgetState: !!window.openai.setWidgetState,
        hasSendFollowUp: !!window.openai.sendFollowUpMessage,
        hasCallTool: !!window.openai.callTool
      });
    } else {
      log('ERROR', 'window.openai is NOT available!');
    }
    
    // Listen for window.openai changes
    const interval = setInterval(() => {
      if (window.openai && !metadata) {
        log('POLL', 'window.openai became available, re-rendering');
        setRenderKey(prev => prev + 1);
      }
    }, 500);
    
    return () => clearInterval(interval);
  }, []);
  
  // Read from window.openai
  const toolOutput = window.openai?.toolOutput;
  const metadata = window.openai?.toolResponseMetadata;
  const savedState = window.openai?.widgetState;
  
  log('DATA', 'Current data state', {
    hasToolOutput: !!toolOutput,
    hasMetadata: !!metadata,
    hasSavedState: !!savedState,
    toolOutputKeys: toolOutput ? Object.keys(toolOutput) : [],
    metadataKeys: metadata ? Object.keys(metadata) : []
  });
  
  // Local state
  const [widgetState, setLocalWidgetState] = useState<WidgetState>(
    savedState || {
      viewMode: 'grid',
      sortBy: 'created',
      filterBy: 'all',
      searchQuery: ''
    }
  );
  
  // Update widget state helper
  const updateWidgetState = (updates: Partial<WidgetState>) => {
    log('STATE', 'Updating widget state', updates);
    const newState = { ...widgetState, ...updates };
    setLocalWidgetState(newState);
    
    if (window.openai?.setWidgetState) {
      window.openai.setWidgetState(newState);
      log('STATE', 'Called window.openai.setWidgetState');
    } else {
      log('WARN', 'window.openai.setWidgetState not available');
    }
  };
  
  // Extract courses data - try multiple paths
  let courses: Course[] = [];
  let totalCount = 0;
  let stats = { total: 0, published: 0, draft: 0 };
  
  if (metadata) {
    log('PARSE', 'Parsing metadata', metadata);
    
    // Try multiple possible data structures
    if (metadata.courses) {
      courses = metadata.courses;
      log('PARSE', `Found ${courses.length} courses in metadata.courses`);
    } else if (Array.isArray(metadata)) {
      courses = metadata;
      log('PARSE', `metadata is array with ${courses.length} items`);
    }
    
    totalCount = metadata.totalCourseCount || metadata.total || courses.length;
    stats = metadata.stats || {
      total: totalCount,
      published: courses.filter(c => c.publishStatus === 'PUBLISHED').length,
      draft: courses.filter(c => c.publishStatus !== 'PUBLISHED').length
    };
  } else if (toolOutput) {
    log('PARSE', 'Trying to parse from toolOutput', toolOutput);
    
    if (toolOutput.courses) {
      courses = toolOutput.courses;
      log('PARSE', `Found ${courses.length} courses in toolOutput.courses`);
    }
  }
  
  log('FINAL', 'Final parsed data', {
    courseCount: courses.length,
    totalCount,
    stats
  });
  
  // Filter and sort courses
  const filteredCourses = useMemo(() => {
    log('FILTER', 'Filtering courses', {
      totalCourses: courses.length,
      filterBy: widgetState.filterBy,
      searchQuery: widgetState.searchQuery,
      sortBy: widgetState.sortBy
    });
    
    let filtered = courses;
    
    // Apply filter by status
    if (widgetState.filterBy === 'draft') {
      filtered = filtered.filter(c => 
        c.publishStatus === 'DRAFT' || c.publishStatus === 'NONE'
      );
    } else if (widgetState.filterBy === 'published') {
      filtered = filtered.filter(c => c.publishStatus === 'PUBLISHED');
    }
    
    // Apply search
    if (widgetState.searchQuery) {
      const query = widgetState.searchQuery.toLowerCase();
      filtered = filtered.filter(c =>
        c.courseName.toLowerCase().includes(query) ||
        c.subTitle?.toLowerCase().includes(query)
      );
    }
    
    // Apply sort
    const sorted = [...filtered].sort((a, b) => {
      switch (widgetState.sortBy) {
        case 'name':
          return a.courseName.localeCompare(b.courseName);
        case 'enrolled':
          return (b.enrolledCount || 0) - (a.enrolledCount || 0);
        case 'created':
        default:
          return (Number(b.createdTime) || 0) - (Number(a.createdTime) || 0);
      }
    });
    
    log('FILTER', `Filtered to ${sorted.length} courses`);
    return sorted;
  }, [courses, widgetState]);
  
  // Handle course click
  const handleCourseClick = async (course: Course) => {
    log('ACTION', 'Course clicked', { courseId: course.courseId, name: course.courseName });
    
    if (window.openai?.sendFollowUpMessage) {
      try {
        await window.openai.sendFollowUpMessage({
          prompt: `Show me details for the course "${course.courseName}" (ID: ${course.courseId})`
        });
        log('ACTION', 'Follow-up message sent successfully');
      } catch (err) {
        log('ERROR', 'Failed to send follow-up', err);
      }
    } else {
      log('WARN', 'window.openai.sendFollowUpMessage not available');
    }
  };
  
  // Handle create course
  const handleCreateCourse = async () => {
    log('ACTION', 'Create course clicked');
    
    if (window.openai?.sendFollowUpMessage) {
      try {
        await window.openai.sendFollowUpMessage({
          prompt: "I want to create a new course"
        });
        log('ACTION', 'Create course message sent');
      } catch (err) {
        log('ERROR', 'Failed to send create message', err);
      }
    }
  };
  
  // RENDER DECISION
  const shouldShowLoading = !metadata && !toolOutput;
  const hasNoData = courses.length === 0;
  
  log('RENDER', 'Render decision', {
    shouldShowLoading,
    hasNoData,
    hasCourses: courses.length > 0
  });
  
  // Loading state
  if (shouldShowLoading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>
          <div style={styles.spinner}></div>
          <p style={styles.loadingText}>Loading courses...</p>
          <button 
            onClick={() => setDebugMode(!debugMode)}
            style={styles.debugToggle}
          >
            {debugMode ? 'Hide' : 'Show'} Debug
          </button>
        </div>
        
        {debugMode && (
          <div style={styles.debugPanel}>
            <h3 style={styles.debugTitle}>Debug Info</h3>
            <div id="debug-log" style={styles.debugLog}></div>
            <button onClick={() => {
              document.getElementById('debug-log')!.innerHTML = '';
              log('DEBUG', 'Log cleared');
            }} style={styles.clearButton}>
              Clear Log
            </button>
          </div>
        )}
      </div>
    );
  }
  
  // No data state
  if (hasNoData) {
    return (
      <div style={styles.container}>
        <div style={styles.empty}>
          <h2>No Courses Found</h2>
          <p>window.openai status: {window.openai ? 'Available' : 'Not available'}</p>
          <p>metadata: {metadata ? 'Present' : 'Missing'}</p>
          <p>toolOutput: {toolOutput ? 'Present' : 'Missing'}</p>
          <button onClick={handleCreateCourse} style={styles.createButton}>
            Create First Course
          </button>
        </div>
        
        {debugMode && (
          <div style={styles.debugPanel}>
            <h3 style={styles.debugTitle}>Debug Info</h3>
            <div id="debug-log" style={styles.debugLog}></div>
          </div>
        )}
      </div>
    );
  }
  
  // Main render
  return (
    <div style={styles.container}>
      {/* Debug toggle */}
      <button 
        onClick={() => setDebugMode(!debugMode)}
        style={styles.debugToggleSmall}
        title="Toggle debug panel"
      >
        🐛
      </button>
      
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <h1 style={styles.title}>Courses ({filteredCourses.length})</h1>
          <div style={styles.stats}>
            <span style={styles.statBadge}>
              📊 {stats.published} Published
            </span>
            <span style={{ ...styles.statBadge, ...styles.statBadgeDraft }}>
              📝 {stats.draft} Draft
            </span>
          </div>
        </div>
        <button style={styles.createButton} onClick={handleCreateCourse}>
          <span style={styles.createIcon}>⊕</span>
          Create
        </button>
      </div>
      
      {/* Controls */}
      <div style={styles.controls}>
        <div style={styles.controlsLeft}>
          {/* Search */}
          <div style={styles.searchBox}>
            <span style={styles.searchIcon}>🔍</span>
            <input
              type="text"
              placeholder="Search courses..."
              style={styles.searchInput}
              value={widgetState.searchQuery}
              onChange={(e) => updateWidgetState({ searchQuery: e.target.value })}
            />
            {widgetState.searchQuery && (
              <button
                style={styles.clearSearchButton}
                onClick={() => updateWidgetState({ searchQuery: '' })}
              >
                ✕
              </button>
            )}
          </div>
          
          {/* Filter */}
          <div style={styles.dropdown}>
            <label style={styles.label}>Filter:</label>
            <select
              style={styles.select}
              value={widgetState.filterBy}
              onChange={(e) => updateWidgetState({ filterBy: e.target.value as any })}
            >
              <option value="all">All</option>
              <option value="draft">Draft</option>
              <option value="published">Published</option>
            </select>
          </div>
          
          {/* Sort */}
          <div style={styles.dropdown}>
            <label style={styles.label}>Sort:</label>
            <select
              style={styles.select}
              value={widgetState.sortBy}
              onChange={(e) => updateWidgetState({ sortBy: e.target.value as any })}
            >
              <option value="created">Created</option>
              <option value="name">Name</option>
              <option value="enrolled">Enrolled</option>
            </select>
          </div>
        </div>
        
        {/* View toggle */}
        <div style={styles.viewToggle}>
          <button
            style={{
              ...styles.viewButton,
              ...(widgetState.viewMode === 'grid' ? styles.viewButtonActive : {})
            }}
            onClick={() => updateWidgetState({ viewMode: 'grid' })}
          >
            ⊞
          </button>
          <button
            style={{
              ...styles.viewButton,
              ...(widgetState.viewMode === 'list' ? styles.viewButtonActive : {})
            }}
            onClick={() => updateWidgetState({ viewMode: 'list' })}
          >
            ☰
          </button>
        </div>
      </div>
      
      {/* Course Grid/List */}
      <div style={widgetState.viewMode === 'grid' ? styles.grid : styles.list}>
        {filteredCourses.map((course) => (
          <CourseCard
            key={course.courseId}
            course={course}
            viewMode={widgetState.viewMode}
            onClick={() => handleCourseClick(course)}
          />
        ))}
      </div>
      
      {/* Empty filtered state */}
      {filteredCourses.length === 0 && courses.length > 0 && (
        <div style={styles.emptyFiltered}>
          <p>No courses match your filters</p>
          <button
            onClick={() => updateWidgetState({ searchQuery: '', filterBy: 'all' })}
            style={styles.clearButton}
          >
            Clear Filters
          </button>
        </div>
      )}
      
      {/* Debug panel */}
      {debugMode && (
        <div style={styles.debugPanel}>
          <h3 style={styles.debugTitle}>Debug Info</h3>
          <div id="debug-log" style={styles.debugLog}></div>
          <button onClick={() => {
            document.getElementById('debug-log')!.innerHTML = '';
          }} style={styles.clearButton}>
            Clear Log
          </button>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Course Card Component
// =============================================================================

interface CourseCardProps {
  course: Course;
  viewMode: 'grid' | 'list';
  onClick: () => void;
}

function CourseCard({ course, viewMode, onClick }: CourseCardProps) {
  const isDraft = course.publishStatus === 'DRAFT' || course.publishStatus === 'NONE';
  
  const gradients = [
    'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
    'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
    'linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%)',
    'linear-gradient(135deg, #fdcbf1 0%, #e6dee9 100%)',
    'linear-gradient(135deg, #f6d365 0%, #fda085 100%)',
  ];
  
  const gradientIndex = course.courseName.length % gradients.length;
  const gradient = gradients[gradientIndex];
  
  if (viewMode === 'list') {
    return (
      <div style={styles.listCard} onClick={onClick}>
        <div style={{ ...styles.listThumbnail, background: gradient }}>
          <span style={styles.thumbnailIcon}>📚</span>
        </div>
        <div style={styles.listContent}>
          <div>
            <h3 style={styles.listCourseName}>{course.courseName}</h3>
            {course.subTitle && (
              <p style={styles.listSubtitle}>{course.subTitle}</p>
            )}
          </div>
          <div style={styles.listFooter}>
            {isDraft && <span style={styles.listDraftBadge}>Draft</span>}
            <span style={styles.listStat}>📊 {course.rating || 0.0}</span>
            <span style={styles.listStat}>👥 {course.enrolledCount || 0}</span>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div style={styles.card} onClick={onClick}>
      <div style={{ ...styles.thumbnail, background: gradient }}>
        <span style={styles.thumbnailIcon}>📚</span>
        {isDraft && <span style={styles.draftBadge}>Draft</span>}
      </div>
      <div style={styles.cardContent}>
        <h3 style={styles.courseName}>{course.courseName}</h3>
        {course.subTitle && <p style={styles.subtitle}>{course.subTitle}</p>}
        <div style={styles.cardFooter}>
          <div style={styles.statsRow}>
            <span style={styles.stat}>
              <span>📊</span> {course.rating || 0.0}
            </span>
            <span style={styles.stat}>
              <span>👥</span> {course.enrolledCount || 0}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Styles
// =============================================================================

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    padding: '20px',
    backgroundColor: '#f8f9fa',
    minHeight: '100vh',
    position: 'relative',
  },
  loading: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '400px',
    gap: '16px',
  },
  spinner: {
    border: '4px solid #f3f3f3',
    borderTop: '4px solid #ff6b35',
    borderRadius: '50%',
    width: '48px',
    height: '48px',
    animation: 'spin 1s linear infinite',
  },
  loadingText: {
    color: '#666',
    fontSize: '16px',
  },
  debugToggle: {
    marginTop: '20px',
    padding: '10px 20px',
    backgroundColor: '#333',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
  },
  debugToggleSmall: {
    position: 'fixed',
    top: '10px',
    right: '10px',
    width: '40px',
    height: '40px',
    backgroundColor: '#333',
    color: 'white',
    border: 'none',
    borderRadius: '50%',
    cursor: 'pointer',
    fontSize: '20px',
    zIndex: 1000,
  },
  debugPanel: {
    marginTop: '20px',
    padding: '16px',
    backgroundColor: '#1a1a1a',
    borderRadius: '8px',
    color: 'white',
  },
  debugTitle: {
    margin: '0 0 12px 0',
    fontSize: '14px',
    color: '#ff6b35',
  },
  debugLog: {
    maxHeight: '300px',
    overflowY: 'auto',
    backgroundColor: '#000',
    padding: '12px',
    borderRadius: '4px',
    fontSize: '11px',
    fontFamily: 'monospace',
    marginBottom: '12px',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '20px',
  },
  headerLeft: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  title: {
    fontSize: '24px',
    fontWeight: '600',
    margin: 0,
    color: '#1a1a1a',
  },
  stats: {
    display: 'flex',
    gap: '10px',
  },
  statBadge: {
    fontSize: '12px',
    padding: '4px 10px',
    borderRadius: '12px',
    backgroundColor: '#e8f5e9',
    color: '#2e7d32',
    fontWeight: '500',
  },
  statBadgeDraft: {
    backgroundColor: '#fff3e0',
    color: '#e65100',
  },
  createButton: {
    backgroundColor: '#ff6b35',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    padding: '10px 20px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  createIcon: {
    fontSize: '16px',
  },
  controls: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
    gap: '12px',
    flexWrap: 'wrap',
  },
  controlsLeft: {
    display: 'flex',
    gap: '12px',
    flex: 1,
    flexWrap: 'wrap',
  },
  searchBox: {
    display: 'flex',
    alignItems: 'center',
    backgroundColor: 'white',
    border: '1px solid #ddd',
    borderRadius: '6px',
    padding: '8px 12px',
    minWidth: '200px',
  },
  searchIcon: {
    marginRight: '8px',
  },
  searchInput: {
    border: 'none',
    outline: 'none',
    flex: 1,
    fontSize: '14px',
  },
  clearSearchButton: {
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    padding: '4px',
    color: '#999',
  },
  dropdown: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  label: {
    fontSize: '13px',
    color: '#666',
    fontWeight: '500',
  },
  select: {
    border: '1px solid #ddd',
    borderRadius: '6px',
    padding: '8px 12px',
    fontSize: '14px',
    backgroundColor: 'white',
    cursor: 'pointer',
  },
  viewToggle: {
    display: 'flex',
    gap: '4px',
    backgroundColor: 'white',
    padding: '4px',
    borderRadius: '6px',
    border: '1px solid #ddd',
  },
  viewButton: {
    backgroundColor: 'transparent',
    border: 'none',
    borderRadius: '4px',
    padding: '6px 10px',
    fontSize: '16px',
    cursor: 'pointer',
    color: '#666',
  },
  viewButtonActive: {
    backgroundColor: '#f0f0f0',
    color: '#ff6b35',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
    gap: '16px',
  },
  list: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '10px',
    overflow: 'hidden',
    cursor: 'pointer',
    transition: 'transform 0.2s',
    boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
  },
  thumbnail: {
    height: '140px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  thumbnailIcon: {
    fontSize: '48px',
    opacity: 0.3,
  },
  draftBadge: {
    position: 'absolute',
    top: '10px',
    right: '10px',
    backgroundColor: 'rgba(255,255,255,0.95)',
    padding: '4px 10px',
    borderRadius: '12px',
    fontSize: '11px',
    fontWeight: '600',
    color: '#666',
  },
  cardContent: {
    padding: '14px',
  },
  courseName: {
    fontSize: '15px',
    fontWeight: '600',
    margin: '0 0 6px 0',
    color: '#1a1a1a',
    lineHeight: '1.3',
    minHeight: '40px',
  },
  subtitle: {
    fontSize: '12px',
    color: '#666',
    marginBottom: '10px',
  },
  cardFooter: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statsRow: {
    display: 'flex',
    gap: '10px',
  },
  stat: {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    fontSize: '12px',
    color: '#666',
  },
  listCard: {
    backgroundColor: 'white',
    borderRadius: '10px',
    padding: '14px',
    display: 'flex',
    gap: '14px',
    cursor: 'pointer',
    boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
  },
  listThumbnail: {
    width: '70px',
    height: '70px',
    borderRadius: '8px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  },
  listContent: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
  },
  listCourseName: {
    fontSize: '15px',
    fontWeight: '600',
    margin: '0 0 4px 0',
    color: '#1a1a1a',
  },
  listSubtitle: {
    fontSize: '12px',
    color: '#666',
    margin: 0,
  },
  listFooter: {
    display: 'flex',
    gap: '10px',
    alignItems: 'center',
  },
  listDraftBadge: {
    fontSize: '11px',
    padding: '3px 8px',
    borderRadius: '10px',
    backgroundColor: '#f5f5f5',
    color: '#666',
    fontWeight: '600',
  },
  listStat: {
    fontSize: '12px',
    color: '#666',
  },
  empty: {
    textAlign: 'center',
    padding: '60px 20px',
    color: '#666',
  },
  emptyFiltered: {
    textAlign: 'center',
    padding: '40px 20px',
    color: '#999',
  },
  clearButton: {
    marginTop: '12px',
    padding: '8px 16px',
    backgroundColor: '#f0f0f0',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '13px',
  },
};

// Add CSS animation
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;
document.head.appendChild(styleSheet);

// =============================================================================
// Mount
// =============================================================================

const root = document.getElementById('root');
if (root) {
  log('MOUNT', 'Mounting React component to #root');
  createRoot(root).render(<CoursesWidget />);
} else {
  log('ERROR', 'Root element #root not found!');
}

export default CoursesWidget;