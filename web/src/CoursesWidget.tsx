// /**
//  * CoursesWidget.tsx - FINAL FIX
//  * 
//  * Fixes:
//  * 1. Added key prop to CourseCard
//  * 2. Handle both API formats (id/name from structuredContent, courseId/courseName from full data)
//  * 3. Better error handling for missing fields
//  */

// import React, { useState, useEffect, useMemo } from 'react';
// import { createRoot } from 'react-dom/client';

// // =============================================================================
// // Type Definitions
// // =============================================================================

// interface Course {
//   // Support both formats
//   courseId?: string;
//   id?: string;
//   courseName?: string;
//   name?: string;
//   subTitle?: string;
//   description?: string;
//   publishStatus?: string;
//   status?: string;
//   enrolledCount?: number;
//   enrolled?: number;
//   rating?: number;
//   createdTime?: string;
// }

// interface CoursesMetadata {
//   courses: Course[];
//   courseCategories?: any[];
//   totalCourseCount?: number;
//   total?: number;
//   stats?: {
//     total: number;
//     published: number;
//     draft: number;
//   };
// }

// interface WidgetState {
//   viewMode: 'grid' | 'list';
//   sortBy: 'created' | 'name' | 'enrolled';
//   filterBy: 'all' | 'draft' | 'published';
//   searchQuery: string;
// }

// declare global {
//   interface Window {
//     openai?: {
//       toolOutput?: any;
//       toolResponseMetadata?: any;
//       toolInput?: any;
//       widgetState?: WidgetState;
//       setWidgetState?: (state: WidgetState) => void;
//       sendFollowUpMessage?: (params: { prompt: string }) => Promise<void>;
//       callTool?: (name: string, args: any) => Promise<any>;
//       theme?: 'light' | 'dark';
//       locale?: string;
//     };
//   }
// }

// // =============================================================================
// // Helper Functions
// // =============================================================================

// function log(category: string, message: string, data?: any) {
//   const timestamp = new Date().toISOString();
//   console.log(`[${timestamp}] [${category}] ${message}`);
//   if (data !== undefined) {
//     console.log('Data:', data);
//   }
// }

// // Normalize course data to handle both API formats
// function normalizeCourse(course: Course): Course {
//   return {
//     courseId: course.courseId || course.id || '',
//     courseName: course.courseName || course.name || 'Untitled Course',
//     subTitle: course.subTitle || '',
//     description: course.description || '',
//     publishStatus: course.publishStatus || course.status || 'NONE',
//     enrolledCount: course.enrolledCount || course.enrolled || 0,
//     rating: course.rating || 0.0,
//     createdTime: course.createdTime || ''
//   };
// }

// // =============================================================================
// // Main Component
// // =============================================================================

// function CoursesWidget() {
//   log('INIT', 'Widget component mounting');
  
//   const [debugMode, setDebugMode] = useState(false);
  
//   // Read from window.openai
//   const toolOutput = window.openai?.toolOutput;
//   const metadata = window.openai?.toolResponseMetadata;
//   const savedState = window.openai?.widgetState;
  
//   log('DATA', 'Current data state', {
//     hasToolOutput: !!toolOutput,
//     hasMetadata: !!metadata,
//     toolOutputKeys: toolOutput ? Object.keys(toolOutput) : [],
//     metadataKeys: metadata ? Object.keys(metadata) : []
//   });
  
//   // Local state
//   const [widgetState, setLocalWidgetState] = useState<WidgetState>(
//     savedState || {
//       viewMode: 'grid',
//       sortBy: 'created',
//       filterBy: 'all',
//       searchQuery: ''
//     }
//   );
  
//   // Update widget state helper
//   const updateWidgetState = (updates: Partial<WidgetState>) => {
//     const newState = { ...widgetState, ...updates };
//     setLocalWidgetState(newState);
//     window.openai?.setWidgetState?.(newState);
//   };
  
//   // Extract and normalize courses data
//   let rawCourses: Course[] = [];
//   let totalCount = 0;
//   let stats = { total: 0, published: 0, draft: 0 };
  
//   // Try multiple data sources
//   if (metadata?.courses) {
//     rawCourses = metadata.courses;
//     log('PARSE', `Found ${rawCourses.length} courses in metadata.courses`);
//   } else if (toolOutput?.courses) {
//     rawCourses = toolOutput.courses;
//     log('PARSE', `Found ${rawCourses.length} courses in toolOutput.courses`);
//   } else if (Array.isArray(toolOutput)) {
//     rawCourses = toolOutput;
//     log('PARSE', `toolOutput is array with ${rawCourses.length} items`);
//   } else if (Array.isArray(metadata)) {
//     rawCourses = metadata;
//     log('PARSE', `metadata is array with ${rawCourses.length} items`);
//   }
  
//   // Normalize all courses
//   const courses = rawCourses.map(normalizeCourse);
  
//   totalCount = metadata?.totalCourseCount || metadata?.total || toolOutput?.total || courses.length;
  
//   // Calculate stats
//   stats = {
//     total: totalCount,
//     published: courses.filter(c => c.publishStatus === 'PUBLISHED').length,
//     draft: courses.filter(c => c.publishStatus !== 'PUBLISHED').length
//   };
  
//   log('FINAL', 'Final parsed data', {
//     courseCount: courses.length,
//     totalCount,
//     stats,
//     sampleCourse: courses[0]
//   });
  
//   // Filter and sort courses
//   const filteredCourses = useMemo(() => {
//     log('FILTER', 'Filtering courses', {
//       totalCourses: courses.length,
//       filterBy: widgetState.filterBy,
//       searchQuery: widgetState.searchQuery
//     });
    
//     let filtered = courses;
    
//     // Apply filter by status
//     if (widgetState.filterBy === 'draft') {
//       filtered = filtered.filter(c => 
//         c.publishStatus === 'DRAFT' || c.publishStatus === 'NONE'
//       );
//     } else if (widgetState.filterBy === 'published') {
//       filtered = filtered.filter(c => c.publishStatus === 'PUBLISHED');
//     }
    
//     // Apply search
//     if (widgetState.searchQuery) {
//       const query = widgetState.searchQuery.toLowerCase();
//       filtered = filtered.filter(c =>
//         c.courseName?.toLowerCase().includes(query) ||
//         c.subTitle?.toLowerCase().includes(query)
//       );
//     }
    
//     // Apply sort
//     const sorted = [...filtered].sort((a, b) => {
//       switch (widgetState.sortBy) {
//         case 'name':
//           return (a.courseName || '').localeCompare(b.courseName || '');
//         case 'enrolled':
//           return (b.enrolledCount || 0) - (a.enrolledCount || 0);
//         case 'created':
//         default:
//           return (Number(b.createdTime) || 0) - (Number(a.createdTime) || 0);
//       }
//     });
    
//     log('FILTER', `Filtered to ${sorted.length} courses`);
//     return sorted;
//   }, [courses, widgetState]);
  
//   // Handle course click
//   const handleCourseClick = async (course: Course) => {
//     log('ACTION', 'Course clicked', { courseId: course.courseId, name: course.courseName });
    
//     await window.openai?.sendFollowUpMessage?.({
//       prompt: `Show me details for the course "${course.courseName}" (ID: ${course.courseId})`
//     });
//   };
  
//   // Handle create course
//   const handleCreateCourse = async () => {
//     await window.openai?.sendFollowUpMessage?.({
//       prompt: "I want to create a new course"
//     });
//   };
  
//   // Loading state
//   if (!toolOutput && !metadata) {
//     return (
//       <div style={styles.loading}>
//         <div style={styles.spinner}></div>
//         <p style={styles.loadingText}>Loading courses...</p>
//       </div>
//     );
//   }
  
//   // No data state
//   if (courses.length === 0) {
//     return (
//       <div style={styles.container}>
//         <div style={styles.empty}>
//           <h2 style={styles.emptyTitle}>No Courses Found</h2>
//           <p style={styles.emptyText}>Get started by creating your first course</p>
//           <button onClick={handleCreateCourse} style={styles.createButton}>
//             <span style={styles.createIcon}>⊕</span>
//             Create First Course
//           </button>
//         </div>
//       </div>
//     );
//   }
  
//   // Main render
//   return (
//     <div style={styles.container}>
//       {/* Debug toggle */}
//       {debugMode && (
//         <button 
//           onClick={() => setDebugMode(false)}
//           style={styles.debugToggleSmall}
//           title="Hide debug"
//         >
//           🐛
//         </button>
//       )}
      
//       {/* Header */}
//       <div style={styles.header}>
//         <div style={styles.headerLeft}>
//           <h1 style={styles.title}>Courses ({filteredCourses.length})</h1>
//           <div style={styles.stats}>
//             <span style={styles.statBadge}>
//               📊 {stats.published} Published
//             </span>
//             <span style={{ ...styles.statBadge, ...styles.statBadgeDraft }}>
//               📝 {stats.draft} Draft
//             </span>
//           </div>
//         </div>
//         <button style={styles.createButton} onClick={handleCreateCourse}>
//           <span style={styles.createIcon}>⊕</span>
//           Create
//         </button>
//       </div>
      
//       {/* Controls */}
//       <div style={styles.controls}>
//         <div style={styles.controlsLeft}>
//           {/* Search */}
//           <div style={styles.searchBox}>
//             <span style={styles.searchIcon}>🔍</span>
//             <input
//               type="text"
//               placeholder="Search courses..."
//               style={styles.searchInput}
//               value={widgetState.searchQuery}
//               onChange={(e) => updateWidgetState({ searchQuery: e.target.value })}
//             />
//             {widgetState.searchQuery && (
//               <button
//                 style={styles.clearSearchButton}
//                 onClick={() => updateWidgetState({ searchQuery: '' })}
//               >
//                 ✕
//               </button>
//             )}
//           </div>
          
//           {/* Filter */}
//           <div style={styles.dropdown}>
//             <label style={styles.label}>Filter:</label>
//             <select
//               style={styles.select}
//               value={widgetState.filterBy}
//               onChange={(e) => updateWidgetState({ filterBy: e.target.value as any })}
//             >
//               <option value="all">All</option>
//               <option value="draft">Draft</option>
//               <option value="published">Published</option>
//             </select>
//           </div>
          
//           {/* Sort */}
//           <div style={styles.dropdown}>
//             <label style={styles.label}>Sort:</label>
//             <select
//               style={styles.select}
//               value={widgetState.sortBy}
//               onChange={(e) => updateWidgetState({ sortBy: e.target.value as any })}
//             >
//               <option value="created">Created</option>
//               <option value="name">Name</option>
//               <option value="enrolled">Enrolled</option>
//             </select>
//           </div>
//         </div>
        
//         {/* View toggle */}
//         <div style={styles.viewToggle}>
//           <button
//             style={{
//               ...styles.viewButton,
//               ...(widgetState.viewMode === 'grid' ? styles.viewButtonActive : {})
//             }}
//             onClick={() => updateWidgetState({ viewMode: 'grid' })}
//           >
//             ⊞
//           </button>
//           <button
//             style={{
//               ...styles.viewButton,
//               ...(widgetState.viewMode === 'list' ? styles.viewButtonActive : {})
//             }}
//             onClick={() => updateWidgetState({ viewMode: 'list' })}
//           >
//             ☰
//           </button>
//         </div>
//       </div>
      
//       {/* Course Grid/List */}
//       <div style={widgetState.viewMode === 'grid' ? styles.grid : styles.list}>
//         {filteredCourses.map((course) => (
//           <CourseCard
//             key={course.courseId}  
//             course={course}
//             viewMode={widgetState.viewMode}
//             onClick={() => handleCourseClick(course)}
//           />
//         ))}
//       </div>
      
//       {/* Empty filtered state */}
//       {filteredCourses.length === 0 && courses.length > 0 && (
//         <div style={styles.emptyFiltered}>
//           <p>No courses match your filters</p>
//           <button
//             onClick={() => updateWidgetState({ searchQuery: '', filterBy: 'all' })}
//             style={styles.clearButton}
//           >
//             Clear Filters
//           </button>
//         </div>
//       )}
//     </div>
//   );
// }

// // =============================================================================
// // Course Card Component
// // =============================================================================

// interface CourseCardProps {
//   course: Course;
//   viewMode: 'grid' | 'list';
//   onClick: () => void;
// }

// function CourseCard({ course, viewMode, onClick }: CourseCardProps) {
//   const isDraft = course.publishStatus === 'DRAFT' || course.publishStatus === 'NONE';
  
//   const gradients = [
//     'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
//     'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
//     'linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%)',
//     'linear-gradient(135deg, #fdcbf1 0%, #e6dee9 100%)',
//     'linear-gradient(135deg, #f6d365 0%, #fda085 100%)',
//   ];
  
//   // ✅ FIXED: Safe access to courseName
//   const gradientIndex = (course.courseName?.length || 0) % gradients.length;
//   const gradient = gradients[gradientIndex];
  
//   if (viewMode === 'list') {
//     return (
//       <div style={styles.listCard} onClick={onClick}>
//         <div style={{ ...styles.listThumbnail, background: gradient }}>
//           <span style={styles.thumbnailIcon}>📚</span>
//         </div>
//         <div style={styles.listContent}>
//           <div>
//             <h3 style={styles.listCourseName}>{course.courseName}</h3>
//             {course.subTitle && (
//               <p style={styles.listSubtitle}>{course.subTitle}</p>
//             )}
//           </div>
//           <div style={styles.listFooter}>
//             {isDraft && <span style={styles.listDraftBadge}>Draft</span>}
//             <span style={styles.listStat}>📊 {course.rating || 0.0}</span>
//             <span style={styles.listStat}>👥 {course.enrolledCount || 0}</span>
//           </div>
//         </div>
//       </div>
//     );
//   }
  
//   return (
//     <div style={styles.card} onClick={onClick}>
//       <div style={{ ...styles.thumbnail, background: gradient }}>
//         <span style={styles.thumbnailIcon}>📚</span>
//         {isDraft && <span style={styles.draftBadge}>Draft</span>}
//       </div>
//       <div style={styles.cardContent}>
//         <h3 style={styles.courseName}>{course.courseName}</h3>
//         {course.subTitle && <p style={styles.subtitle}>{course.subTitle}</p>}
//         <div style={styles.cardFooter}>
//           <div style={styles.statsRow}>
//             <span style={styles.stat}>
//               <span>📊</span> {course.rating || 0.0}
//             </span>
//             <span style={styles.stat}>
//               <span>👥</span> {course.enrolledCount || 0}
//             </span>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }

// // =============================================================================
// // Styles (same as before)
// // =============================================================================

// const styles: { [key: string]: React.CSSProperties } = {
//   container: {
//     fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
//     padding: '20px',
//     backgroundColor: '#f8f9fa',
//     minHeight: '100vh',
//   },
//   loading: {
//     display: 'flex',
//     flexDirection: 'column',
//     alignItems: 'center',
//     justifyContent: 'center',
//     minHeight: '400px',
//     gap: '16px',
//   },
//   spinner: {
//     border: '4px solid #f3f3f3',
//     borderTop: '4px solid #ff6b35',
//     borderRadius: '50%',
//     width: '48px',
//     height: '48px',
//     animation: 'spin 1s linear infinite',
//   },
//   loadingText: {
//     color: '#666',
//     fontSize: '16px',
//   },
//   debugToggleSmall: {
//     position: 'fixed',
//     top: '10px',
//     right: '10px',
//     width: '40px',
//     height: '40px',
//     backgroundColor: '#333',
//     color: 'white',
//     border: 'none',
//     borderRadius: '50%',
//     cursor: 'pointer',
//     fontSize: '20px',
//     zIndex: 1000,
//   },
//   header: {
//     display: 'flex',
//     justifyContent: 'space-between',
//     alignItems: 'flex-start',
//     marginBottom: '20px',
//   },
//   headerLeft: {
//     display: 'flex',
//     flexDirection: 'column',
//     gap: '8px',
//   },
//   title: {
//     fontSize: '24px',
//     fontWeight: '600',
//     margin: 0,
//     color: '#1a1a1a',
//   },
//   stats: {
//     display: 'flex',
//     gap: '10px',
//   },
//   statBadge: {
//     fontSize: '12px',
//     padding: '4px 10px',
//     borderRadius: '12px',
//     backgroundColor: '#e8f5e9',
//     color: '#2e7d32',
//     fontWeight: '500',
//   },
//   statBadgeDraft: {
//     backgroundColor: '#fff3e0',
//     color: '#e65100',
//   },
//   createButton: {
//     backgroundColor: '#ff6b35',
//     color: 'white',
//     border: 'none',
//     borderRadius: '8px',
//     padding: '10px 20px',
//     fontSize: '14px',
//     fontWeight: '600',
//     cursor: 'pointer',
//     display: 'flex',
//     alignItems: 'center',
//     gap: '6px',
//     transition: 'all 0.2s',
//   },
//   createIcon: {
//     fontSize: '16px',
//   },
//   controls: {
//     display: 'flex',
//     justifyContent: 'space-between',
//     alignItems: 'center',
//     marginBottom: '20px',
//     gap: '12px',
//     flexWrap: 'wrap',
//   },
//   controlsLeft: {
//     display: 'flex',
//     gap: '12px',
//     flex: 1,
//     flexWrap: 'wrap',
//   },
//   searchBox: {
//     display: 'flex',
//     alignItems: 'center',
//     backgroundColor: 'white',
//     border: '1px solid #ddd',
//     borderRadius: '6px',
//     padding: '8px 12px',
//     minWidth: '200px',
//   },
//   searchIcon: {
//     marginRight: '8px',
//   },
//   searchInput: {
//     border: 'none',
//     outline: 'none',
//     flex: 1,
//     fontSize: '14px',
//   },
//   clearSearchButton: {
//     background: 'none',
//     border: 'none',
//     cursor: 'pointer',
//     padding: '4px',
//     color: '#999',
//   },
//   dropdown: {
//     display: 'flex',
//     alignItems: 'center',
//     gap: '6px',
//   },
//   label: {
//     fontSize: '13px',
//     color: '#666',
//     fontWeight: '500',
//   },
//   select: {
//     border: '1px solid #ddd',
//     borderRadius: '6px',
//     padding: '8px 12px',
//     fontSize: '14px',
//     backgroundColor: 'white',
//     cursor: 'pointer',
//   },
//   viewToggle: {
//     display: 'flex',
//     gap: '4px',
//     backgroundColor: 'white',
//     padding: '4px',
//     borderRadius: '6px',
//     border: '1px solid #ddd',
//   },
//   viewButton: {
//     backgroundColor: 'transparent',
//     border: 'none',
//     borderRadius: '4px',
//     padding: '6px 10px',
//     fontSize: '16px',
//     cursor: 'pointer',
//     color: '#666',
//   },
//   viewButtonActive: {
//     backgroundColor: '#f0f0f0',
//     color: '#ff6b35',
//   },
//   grid: {
//     display: 'grid',
//     gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
//     gap: '16px',
//   },
//   list: {
//     display: 'flex',
//     flexDirection: 'column',
//     gap: '12px',
//   },
//   card: {
//     backgroundColor: 'white',
//     borderRadius: '10px',
//     overflow: 'hidden',
//     cursor: 'pointer',
//     transition: 'transform 0.2s',
//     boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
//   },
//   thumbnail: {
//     height: '140px',
//     display: 'flex',
//     alignItems: 'center',
//     justifyContent: 'center',
//     position: 'relative',
//   },
//   thumbnailIcon: {
//     fontSize: '48px',
//     opacity: 0.3,
//   },
//   draftBadge: {
//     position: 'absolute',
//     top: '10px',
//     right: '10px',
//     backgroundColor: 'rgba(255,255,255,0.95)',
//     padding: '4px 10px',
//     borderRadius: '12px',
//     fontSize: '11px',
//     fontWeight: '600',
//     color: '#666',
//   },
//   cardContent: {
//     padding: '14px',
//   },
//   courseName: {
//     fontSize: '15px',
//     fontWeight: '600',
//     margin: '0 0 6px 0',
//     color: '#1a1a1a',
//     lineHeight: '1.3',
//     minHeight: '40px',
//   },
//   subtitle: {
//     fontSize: '12px',
//     color: '#666',
//     marginBottom: '10px',
//   },
//   cardFooter: {
//     display: 'flex',
//     justifyContent: 'space-between',
//     alignItems: 'center',
//   },
//   statsRow: {
//     display: 'flex',
//     gap: '10px',
//   },
//   stat: {
//     display: 'flex',
//     alignItems: 'center',
//     gap: '4px',
//     fontSize: '12px',
//     color: '#666',
//   },
//   listCard: {
//     backgroundColor: 'white',
//     borderRadius: '10px',
//     padding: '14px',
//     display: 'flex',
//     gap: '14px',
//     cursor: 'pointer',
//     boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
//   },
//   listThumbnail: {
//     width: '70px',
//     height: '70px',
//     borderRadius: '8px',
//     display: 'flex',
//     alignItems: 'center',
//     justifyContent: 'center',
//     flexShrink: 0,
//   },
//   listContent: {
//     flex: 1,
//     display: 'flex',
//     flexDirection: 'column',
//     justifyContent: 'space-between',
//   },
//   listCourseName: {
//     fontSize: '15px',
//     fontWeight: '600',
//     margin: '0 0 4px 0',
//     color: '#1a1a1a',
//   },
//   listSubtitle: {
//     fontSize: '12px',
//     color: '#666',
//     margin: 0,
//   },
//   listFooter: {
//     display: 'flex',
//     gap: '10px',
//     alignItems: 'center',
//   },
//   listDraftBadge: {
//     fontSize: '11px',
//     padding: '3px 8px',
//     borderRadius: '10px',
//     backgroundColor: '#f5f5f5',
//     color: '#666',
//     fontWeight: '600',
//   },
//   listStat: {
//     fontSize: '12px',
//     color: '#666',
//   },
//   empty: {
//     textAlign: 'center',
//     padding: '80px 20px',
//   },
//   emptyTitle: {
//     fontSize: '20px',
//     fontWeight: '600',
//     color: '#333',
//     marginBottom: '8px',
//   },
//   emptyText: {
//     fontSize: '14px',
//     color: '#666',
//     marginBottom: '20px',
//   },
//   emptyFiltered: {
//     textAlign: 'center',
//     padding: '40px 20px',
//     color: '#999',
//   },
//   clearButton: {
//     marginTop: '12px',
//     padding: '8px 16px',
//     backgroundColor: '#f0f0f0',
//     border: 'none',
//     borderRadius: '6px',
//     cursor: 'pointer',
//     fontSize: '13px',
//   },
// };

// // Add CSS animation
// const styleSheet = document.createElement('style');
// styleSheet.textContent = `
//   @keyframes spin {
//     0% { transform: rotate(0deg); }
//     100% { transform: rotate(360deg); }
//   }
// `;
// document.head.appendChild(styleSheet);

// // =============================================================================
// // Mount
// // =============================================================================

// const root = document.getElementById('root');
// if (root) {
//   log('MOUNT', 'Mounting React component to #root');
//   createRoot(root).render(<CoursesWidget />);
// } else {
//   log('ERROR', 'Root element #root not found!');
// }

// export default CoursesWidget;


/*
 * CoursesWidget.tsx
 * Stable, production-ready ChatGPT Widget UI for TrainerCentral MCP
 *
 * Fixes & guarantees:
 * - Normalizes all course shapes (structuredContent + full API)
 * - Never crashes on missing fields
 * - Proper React keys
 * - No infinite loading / remount loop
 * - Safe rendering under ChatGPT widget runtime
 */
/*
 * CoursesWidget.tsx
 * Stable, production-ready ChatGPT Widget UI for TrainerCentral MCP
 *
 * Includes lightweight diagnostic logging:
 * - init
 * - data parsing
 * - normalization
 * - render safety
 *
 * Logs are intentionally minimal and safe for production MCP widgets.
 */


// V1


import React, { useState, useMemo } from "react";
import { createRoot } from "react-dom/client";
import { useSyncExternalStore } from "react";

// ----------------------------------------------
// Hook to subscribe to `window.openai` globals
// as described in the official Apps SDK docs
// ----------------------------------------------

const SET_GLOBALS_EVENT_TYPE = "openai:set_globals";

function useOpenAiGlobal(key) {
  return useSyncExternalStore(
    (onChange) => {
      const handler = (event) => {
        const value = event.detail.globals?.[key];
        if (value !== undefined) {
          onChange();
        }
      };
      window.addEventListener(SET_GLOBALS_EVENT_TYPE, handler, {
        passive: true,
      });
      return () => {
        window.removeEventListener(SET_GLOBALS_EVENT_TYPE, handler);
      };
    },
    () => window.openai?.[key],
    () => window.openai?.[key]
  );
}

// ----------------------------------------------
// Types
// ----------------------------------------------

type ViewMode = "grid" | "list";
type SortBy = "created" | "name" | "enrolled";
type FilterBy = "all" | "draft" | "published";

interface RawCourse {
  id?: string;
  courseId?: string;
  name?: string;
  courseName?: string;
  subTitle?: string;
  description?: string;
  status?: string;
  publishStatus?: string;
  enrolled?: number;
  enrolledCount?: number;
  rating?: number;
  createdTime?: string | number;
}

interface Course {
  courseId: string;
  courseName: string;
  subTitle: string;
  publishStatus: "PUBLISHED" | "DRAFT" | "NONE";
  enrolledCount: number;
  rating: number;
  createdTime: number;
}

interface WidgetState {
  viewMode: ViewMode;
  sortBy: SortBy;
  filterBy: FilterBy;
  searchQuery: string;
}

// ----------------------------------------------
// Helpers
// ----------------------------------------------

function log(level, message, data) {
  const prefix = `[CoursesWidget:${level.toUpperCase()}]`;
  if (data !== undefined) {
    console[level === "error" ? "error" : "log"](prefix, message, data);
  } else {
    console[level === "error" ? "error" : "log"](prefix, message);
  }
}

function normalizeCourse(raw: RawCourse): Course {
  return {
    courseId: raw.courseId || raw.id || crypto.randomUUID(),
    courseName: raw.courseName || raw.name || "Untitled Course",
    subTitle: raw.subTitle || "",
    publishStatus:
      (raw.publishStatus || raw.status || "NONE") === "PUBLISHED"
        ? "PUBLISHED"
        : "DRAFT",
    enrolledCount: raw.enrolledCount ?? raw.enrolled ?? 0,
    rating: raw.rating ?? 0,
    createdTime: Number(raw.createdTime) || 0,
  };
}

// ----------------------------------------------
// Main Widget
// ----------------------------------------------

// function CoursesWidget() {
//   log("info", "Widget mounting");

//   // --- Subscribe to MCP data via hooks ---
//   const toolOutput = useOpenAiGlobal("toolOutput");
//   const metadata = useOpenAiGlobal("toolResponseMetadata");

//   log("info", "Received toolOutput snapshot", toolOutput);

//   // --- Widget UI state (persistent) ---
//   const [state, setState] = useState<WidgetState>(
//     window.openai?.widgetState ?? {
//       viewMode: "grid",
//       sortBy: "created",
//       filterBy: "all",
//       searchQuery: "",
//     }
//   );

//   const updateState = (patch: Partial<WidgetState>) => {
//     const next = { ...state, ...patch };
//     setState(next);
//     window.openai?.setWidgetState?.(next);
//   };

//   // --- Data extraction: read courses from top-level `toolOutput.courses` ---
//   let rawCourses: RawCourse[] = [];

//   if (Array.isArray(toolOutput?.courses)) {
//     rawCourses = toolOutput.courses;
//   }

//   log("info", `Raw courses received: ${rawCourses.length}`);

//   const courses = useMemo(() => {
//     const normalized = rawCourses.map((c, idx) => {
//       try {
//         return normalizeCourse(c);
//       } catch (e) {
//         log("warn", `Failed to normalize course at index ${idx}`, c);
//         return normalizeCourse({});
//       }
//     });
//     log("info", `Normalized courses: ${normalized.length}`);
//     return normalized;
//   }, [rawCourses]);

//   // --- Filtering / sorting logic ---
//   const filteredCourses = useMemo(() => {
//     let list = [...courses];

//     if (state.filterBy === "published")
//       list = list.filter((c) => c.publishStatus === "PUBLISHED");
//     if (state.filterBy === "draft")
//       list = list.filter((c) => c.publishStatus !== "PUBLISHED");

//     if (state.searchQuery) {
//       const q = state.searchQuery.toLowerCase();
//       list = list.filter((c) =>
//         c.courseName.toLowerCase().includes(q)
//       );
//     }

//     list.sort((a, b) => {
//       if (state.sortBy === "name")
//         return a.courseName.localeCompare(b.courseName);
//       if (state.sortBy === "enrolled")
//         return b.enrolledCount - a.enrolledCount;
//       return b.createdTime - a.createdTime;
//     });

//     return list;
//   }, [courses, state]);

//   log("info", "Render phase start");

//   // --- Loading / empty states ---
//   if (toolOutput === undefined && metadata === undefined) {
//     return <div style={styles.loading}>Loading courses…</div>;
//   }

//   if (filteredCourses.length === 0) {
//     return (
//       <div style={styles.empty}>
//         <h3>No courses found</h3>
//         <button
//           onClick={() =>
//             window.openai?.sendFollowUpMessage?.({
//               prompt: "Create a new course",
//             })
//           }
//         >
//           Create Course
//         </button>
//       </div>
//     );
//   }

//   // --- Final render ---
//   return (
//     <div style={styles.container}>
//       <header style={styles.header}>
//         <h2>Courses ({filteredCourses.length})</h2>
//         <button
//           onClick={() =>
//             window.openai?.sendFollowUpMessage?.({
//               prompt: "Create a new course",
//             })
//           }
//         >
//           + Create
//         </button>
//       </header>

//       <div style={styles.controls}>
//         <input
//           placeholder="Search"
//           value={state.searchQuery}
//           onChange={(e) =>
//             updateState({ searchQuery: e.target.value })
//           }
//         />

//         <select
//           value={state.filterBy}
//           onChange={(e) =>
//             updateState({ filterBy: e.target.value as FilterBy })
//           }
//         >
//           <option value="all">All</option>
//           <option value="published">Published</option>
//           <option value="draft">Draft</option>
//         </select>

//         <select
//           value={state.sortBy}
//           onChange={(e) =>
//             updateState({ sortBy: e.target.value as SortBy })
//           }
//         >
//           <option value="created">Created</option>
//           <option value="name">Name</option>
//           <option value="enrolled">Enrolled</option>
//         </select>

//         <button
//           onClick={() =>
//             updateState({
//               viewMode:
//                 state.viewMode === "grid" ? "list" : "grid",
//             })
//           }
//         >
//           {state.viewMode === "grid" ? "☰" : "⊞"}
//         </button>
//       </div>

//       <div
//         style={
//           state.viewMode === "grid" ? styles.grid : styles.list
//         }
//       >
//         {filteredCourses.map((course) => (
//           <CourseCard
//             key={course.courseId}
//             course={course}
//             viewMode={state.viewMode}
//             onClick={() =>
//               window.openai?.sendFollowUpMessage?.({
//                 prompt: `Show details for course ${course.courseName}`,
//               })
//             }
//           />
//         ))}
//       </div>
//     </div>
//   );
// }

// // ----------------------------------------------
// // CourseCard component
// // ----------------------------------------------

// function CourseCard({
//   course,
//   viewMode,
//   onClick,
// }: {
//   course: Course;
//   viewMode: ViewMode;
//   onClick: () => void;
// }) {
//   const gradient =
//     gradients[course.courseName.length % gradients.length];

//   return (
//     <div
//       style={{
//         ...styles.card,
//         background: viewMode === "grid" ? "white" : undefined,
//       }}
//       onClick={onClick}
//     >
//       <div
//         style={{ ...styles.thumb, background: gradient }}
//       >
//         📘
//       </div>
//       <div style={styles.cardBody}>
//         <strong>{course.courseName}</strong>
//         {course.subTitle && (
//           <div style={styles.subtitle}>{course.subTitle}</div>
//         )}
//         <div style={styles.meta}>
//           👥 {course.enrolledCount} · ⭐ {course.rating}
//         </div>
//       </div>
//     </div>
//   );
// }

// // ----------------------------------------------
// // Styles
// // ----------------------------------------------

// const gradients = [
//   "linear-gradient(135deg,#ffecd2,#fcb69f)",
//   "linear-gradient(135deg,#a8edea,#fed6e3)",
//   "linear-gradient(135deg,#fbc2eb,#a6c1ee)",
// ];

// const styles: Record<string, React.CSSProperties> = {
//   container: { padding: 16, fontFamily: "system-ui" },
//   header: {
//     display: "flex",
//     justifyContent: "space-between",
//     marginBottom: 12,
//   },
//   controls: { display: "flex", gap: 8, marginBottom: 12 },
//   grid: {
//     display: "grid",
//     gridTemplateColumns: "repeat(auto-fill,minmax(220px,1fr))",
//     gap: 12,
//   },
//   list: { display: "flex", flexDirection: "column", gap: 8 },
//   card: {
//     borderRadius: 8,
//     boxShadow: "0 2px 6px rgba(0,0,0,.08)",
//     cursor: "pointer",
//     overflow: "hidden",
//   },
//   thumb: {
//     height: 100,
//     display: "flex",
//     alignItems: "center",
//     justifyContent: "center",
//     fontSize: 32,
//   },
//   cardBody: { padding: 12 },
//   subtitle: { fontSize: 12, color: "#666" },
//   meta: { fontSize: 12, marginTop: 6, color: "#555" },
//   loading: { padding: 40, textAlign: "center" },
//   empty: { padding: 40, textAlign: "center" },
// };

// // ----------------------------------------------
// // Mount
// // ----------------------------------------------

// const root = document.getElementById("root");
// if (root) createRoot(root).render(<CoursesWidget />);

// export default CoursesWidget;


// V2

// import React, { useEffect } from "react";
// import { createRoot } from "react-dom/client";
// import { useOpenAiGlobal } from "./openAiGlobalHook";
// import CourseList from "./CourseList";
// import CourseDetails from "./CourseDetails";

// export default function CoursesWidget() {
//   const toolOutput = useOpenAiGlobal("toolOutput");
//   const metadata = useOpenAiGlobal("toolResponseMetadata");
//   const [widgetState, setWidgetState] = React.useState(
//     window.openai?.widgetState ?? {}
//   );

//   // Navigation stack
//   const navStack = widgetState.navStack ?? ["CourseList"];

//   const push = (screen, params) => {
//     const next = { ...widgetState, navStack: [...navStack, screen], params };
//     setWidgetState(next);
//     window.openai?.setWidgetState(next);
//   };

//   const pop = () => {
//     if (navStack.length > 1) {
//       const newStack = navStack.slice(0, -1);
//       setWidgetState({ ...widgetState, navStack: newStack });
//       window.openai?.setWidgetState({ ...widgetState, navStack: newStack });
//     }
//   };

//   useEffect(() => {
//     // Ensure toolOutput arrives
//   }, [toolOutput]);

//   if (!toolOutput) {
//     return <div>Loading...</div>;
//   }

//   const current = navStack[navStack.length - 1];

//   return (
//     <>
//       {current === "CourseList" && (
//         <CourseList
//           courses={toolOutput.courses}
//           onSelect={(c) => push("CourseDetails", { course: c })}
//         />
//       )}
//       {current === "CourseDetails" && (
//         <CourseDetails
//           course={widgetState.params.course}
//           goBack={pop}
//           push={push}
//         />
//       )}
//     </>
//   );
// }

// const root = document.getElementById("root");
// if (root) createRoot(root).render(<CoursesWidget />);


// V3

// import React, { useEffect, useState } from "react";
// import { createRoot } from "react-dom/client";

// declare global {
//   interface Window {
//     openai?: {
//       toolOutput?: any;
//       toolResponseMetadata?: any;
//     };
//   }
// }

// export default function CoursesWidget() {
//   const [courses, setCourses] = useState<any[]>([]);

//   useEffect(() => {
//     // Read the global from ChatGPT
//     const output = window.openai?.toolOutput;
//     console.log("Widget received toolOutput:", output);

//     if (output?.courses && Array.isArray(output.courses)) {
//       setCourses(output.courses);
//     } else {
//       // Also check nested structuredContent if needed
//       const sc = output?.structuredContent;
//       if (sc?.courses && Array.isArray(sc.courses)) {
//         setCourses(sc.courses);
//       }
//     }
//   }, []);

//   return (
//     <div style={{ padding: "16px", fontFamily: "system-ui" }}>
//       <h2>Courses ({courses.length})</h2>

//       {courses.length === 0 && (
//         <p>No courses detected — check console for toolOutput</p>
//       )}

//       {courses.map((course: any) => (
//         <div
//           key={course.id}
//           style={{
//             marginBottom: "8px",
//             padding: "12px",
//             background: "white",
//             borderRadius: "8px",
//             boxShadow: "0 1px 4px rgba(0,0,0,.1)",
//           }}
//         >
//           <strong>{course.name}</strong>
//         </div>
//       ))}
//     </div>
//   );
// }

// const root = document.getElementById("root");
// if (root) createRoot(root).render(<CoursesWidget />);

import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

function CoursesWidget() {
  const [courses, setCourses] = useState<any[]>([]);
  
  useEffect(() => {
    const output = window.openai?.toolOutput;
    console.log("Courses widget toolOutput:", output);
    
    // Full data is in _meta.courses
    const all = output?._meta?.courses ?? [];
    setCourses(Array.isArray(all) ? all : []);
  }, []);
  
  if (!courses) {
    return <div className="loading">Loading courses…</div>;
  }

  return (
    <div className="widget-container">
      <h2>Courses ({courses.length})</h2>
      {courses.length === 0 && (
        <p>No courses found.</p>
      )}
      
      {courses.map((course: any) => (
        <div key={course.courseId || course.id} className="card">
          <h3>{course.courseName || course.name}</h3>
          <div className="flex justify-between align-center">
            <span className={`badge ${course.publishStatus === "PUBLISHED" ? "published" : "draft"}`}>
              {course.publishStatus || course.status || "Unknown"}
            </span>
            <span>👥 {course.enrolledCount ?? course.enrolled ?? 0}</span>
          </div>
          
          <button
            className="button"
            onClick={async () => {
              // Calls tc_get_course and loads CourseDetailsWidget
              await window.openai?.callTool("tc_get_course", {
                courseId: course.courseId || course.id,
                orgId: course.orgId || course.orgId, 
              });
            }}
          >
            View Details
          </button>
        </div>
      ))}
    </div>
  );
}

const root = document.getElementById("root");
console.log("WIDGET METADATA:", window.openai?.toolResponseMetadata);
if (root) createRoot(root).render(<CoursesWidget />);

export default CoursesWidget;
