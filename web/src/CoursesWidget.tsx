/**
 * CoursesWidget.tsx - UPDATED
 * 
 * Properly integrates with ChatGPT widget runtime using window.openai
 * Uses @openai/apps-sdk-ui components for consistent styling
 */

import React, { useState, useEffect, useMemo } from 'react';
import { createRoot } from 'react-dom/client';

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
  courseCategories?: Array<{ categoryName: string }>;
}

interface CoursesMetadata {
  courses: Course[];
  courseCategories: any[];
  totalCourseCount: number;
  stats: {
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

// Extend window type for TypeScript
declare global {
  interface Window {
    openai?: {
      toolOutput?: any;
      toolResponseMetadata?: CoursesMetadata;
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
  // Read from window.openai
  const toolOutput = window.openai?.toolOutput;
  const metadata = window.openai?.toolResponseMetadata;
  const savedState = window.openai?.widgetState;
  
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
    const newState = { ...widgetState, ...updates };
    setLocalWidgetState(newState);
    window.openai?.setWidgetState?.(newState);
  };
  
  // Extract courses data
  const courses = metadata?.courses || [];
  const stats = metadata?.stats || { total: 0, published: 0, draft: 0 };
  
  // Filter and sort courses
  const filteredCourses = useMemo(() => {
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
    
    return sorted;
  }, [courses, widgetState]);
  
  // Handle course click
  const handleCourseClick = async (course: Course) => {
    await window.openai?.sendFollowUpMessage?.({
      prompt: `Show me details for the course "${course.courseName}" (ID: ${course.courseId})`
    });
  };
  
  // Handle create course
  const handleCreateCourse = async () => {
    await window.openai?.sendFollowUpMessage?.({
      prompt: "I want to create a new course"
    });
  };
  
  // Handle refresh
  const handleRefresh = async () => {
    await window.openai?.callTool?.('tc_list_courses_with_widget', {
      orgId: metadata?.orgId
    });
  };
  
  // Loading state
  if (!metadata || !courses.length) {
    return (
      <div style={styles.loading}>
        <div style={styles.spinner}></div>
        <p style={styles.loadingText}>Loading courses...</p>
      </div>
    );
  }
  
  return (
    <div style={styles.container}>
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
                style={styles.clearButton}
                onClick={() => updateWidgetState({ searchQuery: '' })}
              >
                ✕
              </button>
            )}
          </div>
          
          {/* Filter */}
          <div style={styles.dropdown}>
            <label style={styles.label}>Filter by:</label>
            <select
              style={styles.select}
              value={widgetState.filterBy}
              onChange={(e) => updateWidgetState({ filterBy: e.target.value as any })}
            >
              <option value="all">All courses</option>
              <option value="draft">Draft only</option>
              <option value="published">Published only</option>
            </select>
          </div>
          
          {/* Sort */}
          <div style={styles.dropdown}>
            <label style={styles.label}>Sort by:</label>
            <select
              style={styles.select}
              value={widgetState.sortBy}
              onChange={(e) => updateWidgetState({ sortBy: e.target.value as any })}
            >
              <option value="created">Created time</option>
              <option value="name">Name</option>
              <option value="enrolled">Enrollment</option>
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
            title="Grid view"
          >
            ⊞
          </button>
          <button
            style={{
              ...styles.viewButton,
              ...(widgetState.viewMode === 'list' ? styles.viewButtonActive : {})
            }}
            onClick={() => updateWidgetState({ viewMode: 'list' })}
            title="List view"
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
      
      {/* Empty state */}
      {filteredCourses.length === 0 && (
        <div style={styles.empty}>
          <p style={styles.emptyText}>No courses found</p>
          {widgetState.searchQuery && (
            <button
              style={styles.clearFiltersButton}
              onClick={() => updateWidgetState({ searchQuery: '', filterBy: 'all' })}
            >
              Clear filters
            </button>
          )}
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
  
  // Generate gradient based on course name
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
            <span style={styles.listStat}>
              📊 {course.rating || 0.0}
            </span>
            <span style={styles.listStat}>
              👥 {course.enrolledCount || 0} enrolled
            </span>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div style={styles.card} onClick={onClick}>
      {/* Thumbnail */}
      <div style={{ ...styles.thumbnail, background: gradient }}>
        <span style={styles.thumbnailIcon}>📚</span>
        {isDraft && (
          <span style={styles.draftBadge}>Draft</span>
        )}
      </div>
      
      {/* Content */}
      <div style={styles.cardContent}>
        <h3 style={styles.courseName}>{course.courseName}</h3>
        
        {course.subTitle && (
          <p style={styles.subtitle}>{course.subTitle}</p>
        )}
        
        <div style={styles.cardFooter}>
          <div style={styles.statsRow}>
            <span style={styles.stat}>
              <span style={styles.statIcon}>📊</span>
              <span>{course.rating || 0.0}</span>
            </span>
            <span style={styles.stat}>
              <span style={styles.statIcon}>👥</span>
              <span>{course.enrolledCount || 0} enrolled</span>
            </span>
          </div>
          <button
            style={styles.menuButton}
            onClick={(e) => {
              e.stopPropagation();
              // Show context menu (future enhancement)
            }}
          >
            ⋮
          </button>
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
    padding: '24px',
    backgroundColor: '#f8f9fa',
    minHeight: '100vh',
  },
  loading: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '400px',
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
    fontSize: '14px',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '24px',
    gap: '16px',
  },
  headerLeft: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  title: {
    fontSize: '28px',
    fontWeight: '600',
    margin: 0,
    color: '#1a1a1a',
  },
  stats: {
    display: 'flex',
    gap: '12px',
  },
  statBadge: {
    fontSize: '13px',
    padding: '4px 12px',
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
    padding: '12px 24px',
    fontSize: '15px',
    fontWeight: '600',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    transition: 'all 0.2s',
    boxShadow: '0 2px 8px rgba(255, 107, 53, 0.2)',
  },
  createIcon: {
    fontSize: '18px',
  },
  controls: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px',
    gap: '16px',
    flexWrap: 'wrap',
  },
  controlsLeft: {
    display: 'flex',
    gap: '12px',
    flex: 1,
    flexWrap: 'wrap',
    alignItems: 'center',
  },
  searchBox: {
    display: 'flex',
    alignItems: 'center',
    backgroundColor: 'white',
    border: '1px solid #e0e0e0',
    borderRadius: '8px',
    padding: '10px 14px',
    minWidth: '240px',
    gap: '8px',
  },
  searchIcon: {
    fontSize: '16px',
    color: '#999',
  },
  searchInput: {
    border: 'none',
    outline: 'none',
    flex: 1,
    fontSize: '14px',
    fontFamily: 'inherit',
  },
  clearButton: {
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    padding: '4px',
    color: '#999',
    fontSize: '14px',
  },
  dropdown: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  label: {
    fontSize: '14px',
    color: '#666',
    fontWeight: '500',
    whiteSpace: 'nowrap',
  },
  select: {
    border: '1px solid #e0e0e0',
    borderRadius: '8px',
    padding: '10px 14px',
    fontSize: '14px',
    backgroundColor: 'white',
    cursor: 'pointer',
    fontFamily: 'inherit',
  },
  viewToggle: {
    display: 'flex',
    gap: '4px',
    backgroundColor: 'white',
    padding: '4px',
    borderRadius: '8px',
    border: '1px solid #e0e0e0',
  },
  viewButton: {
    backgroundColor: 'transparent',
    border: 'none',
    borderRadius: '6px',
    padding: '8px 12px',
    fontSize: '18px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    color: '#666',
  },
  viewButtonActive: {
    backgroundColor: '#f0f0f0',
    color: '#ff6b35',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '20px',
  },
  list: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '12px',
    overflow: 'hidden',
    cursor: 'pointer',
    transition: 'all 0.2s',
    boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
    border: '1px solid #f0f0f0',
  },
  thumbnail: {
    height: '160px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  thumbnailIcon: {
    fontSize: '56px',
    opacity: 0.3,
  },
  draftBadge: {
    position: 'absolute',
    top: '12px',
    right: '12px',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    padding: '6px 14px',
    borderRadius: '14px',
    fontSize: '12px',
    fontWeight: '600',
    color: '#666',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
  },
  cardContent: {
    padding: '16px',
  },
  courseName: {
    fontSize: '16px',
    fontWeight: '600',
    margin: '0 0 8px 0',
    color: '#1a1a1a',
    lineHeight: '1.4',
    minHeight: '44px',
    display: '-webkit-box',
    WebkitLineClamp: 2,
    WebkitBoxOrient: 'vertical',
    overflow: 'hidden',
  },
  subtitle: {
    fontSize: '13px',
    color: '#666',
    marginBottom: '12px',
    display: '-webkit-box',
    WebkitLineClamp: 2,
    WebkitBoxOrient: 'vertical',
    overflow: 'hidden',
  },
  cardFooter: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  statsRow: {
    display: 'flex',
    gap: '12px',
  },
  stat: {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    fontSize: '13px',
    color: '#666',
  },
  statIcon: {
    fontSize: '15px',
  },
  menuButton: {
    backgroundColor: 'transparent',
    border: 'none',
    fontSize: '20px',
    cursor: 'pointer',
    padding: '4px 8px',
    color: '#999',
    borderRadius: '4px',
    transition: 'all 0.2s',
  },
  listCard: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '16px',
    display: 'flex',
    gap: '16px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
    border: '1px solid #f0f0f0',
  },
  listThumbnail: {
    width: '80px',
    height: '80px',
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
    fontSize: '16px',
    fontWeight: '600',
    margin: '0 0 4px 0',
    color: '#1a1a1a',
  },
  listSubtitle: {
    fontSize: '13px',
    color: '#666',
    margin: 0,
  },
  listFooter: {
    display: 'flex',
    gap: '12px',
    alignItems: 'center',
  },
  listDraftBadge: {
    fontSize: '12px',
    padding: '4px 10px',
    borderRadius: '12px',
    backgroundColor: '#f5f5f5',
    color: '#666',
    fontWeight: '600',
  },
  listStat: {
    fontSize: '13px',
    color: '#666',
  },
  empty: {
    textAlign: 'center',
    padding: '80px 20px',
    color: '#999',
  },
  emptyText: {
    fontSize: '16px',
    marginBottom: '16px',
  },
  clearFiltersButton: {
    backgroundColor: '#f0f0f0',
    border: 'none',
    borderRadius: '8px',
    padding: '10px 20px',
    fontSize: '14px',
    cursor: 'pointer',
    fontWeight: '500',
    color: '#666',
  },
};

// Add CSS animation
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  [style*="cursor: pointer"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.12) !important;
  }
  
  button:hover {
    opacity: 0.9;
  }
`;
document.head.appendChild(styleSheet);

// =============================================================================
// Mount the Component
// =============================================================================

const root = document.getElementById('root');
if (root) {
  createRoot(root).render(<CoursesWidget />);
}

export default CoursesWidget;