// import React, { useEffect, useState } from "react";
// import { createRoot } from "react-dom/client";
// import "./styles.css";

// function CourseDetailsWidget() {
//   const [course, setCourse] = useState<any>(null);
  
//   useEffect(() => {
//     const output = window.openai?.toolOutput;
//     const meta = window.openai?.toolResponseMetadata ?? {};
//     console.log("Course details widget toolOutput:", output, "meta:", meta);
    
//     const full = meta?.course ?? output?._meta?.course ?? output?.course;
//     setCourse(full || null);
//   }, []);

//   if (!course) {
//     return <div className="loading">Loading course details…</div>;
//   }
  
//   return (
//     <div className="widget-container">
//       <h2>{course.courseName || course.name}</h2>

//       <span className={`badge ${course.publishStatus === "PUBLISHED" ? "published" : "draft"}`}>
//         {course.publishStatus || course.status || "Status Unknown"}
//       </span>

//       {course.subTitle && <p className="mt-1">{course.subTitle}</p>}
//       {course.description && <p className="mt-2">{course.description}</p>}

//       <div className="mt-2">
//         👥 Enrolled: {course.enrolledCount ?? course.enrolled ?? 0}
//       </div>

//       {course.createdTime && (
//         <div className="mt-1">
//           📅 Created: {new Date(course.createdTime).toLocaleDateString()}
//         </div>
//       )}
//       {course.lastUpdatedTime && (
//         <div className="mt-1">
//           🔄 Updated: {new Date(course.lastUpdatedTime).toLocaleDateString()}
//         </div>
//       )}
      
//       <div className="mt-2 flex flex-row gap-2">
//         <button
//           className="button"
//           onClick={async () => {
//             await window.openai?.callTool("tc_update_course", {
//               courseId: course.courseId || course.id,
//               orgId: course.orgId,
//               updates: {},
//             });
//           }}
//         >
//           Edit Course
//         </button>

//         <button
//           className="button"
//           onClick={async () => {
//             await window.openai?.callTool("tc_get_course_lessons", {
//               courseId: course.courseId || course.id,
//               orgId: course.orgId,
//             });
//           }}
//         >
//           View Lessons
//         </button>

//         <button
//           className="button"
//           onClick={async () => {
//             await window.openai?.callTool("tc_get_course_chapters", {
//               courseId: course.courseId || course.id,
//               orgId: course.orgId,
//             });
//           }}
//         >
//           View Chapters
//         </button>
//       </div>
//     </div>
//   );
// }

// const root = document.getElementById("root");
// if (root) createRoot(root).render(<CourseDetailsWidget />);

// export default CourseDetailsWidget;


import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";

const SET_GLOBALS_EVENT_TYPE = "openai:set_globals";

function useOpenAiGlobal(key) {
  const [val, setVal] = useState(window.openai?.[key]);

  useEffect(() => {
    const handler = (e) => {
      const globals = e.detail?.globals || {};
      if (globals[key] !== undefined) setVal(globals[key]);
    };
    window.addEventListener(SET_GLOBALS_EVENT_TYPE, handler);
    return () => window.removeEventListener(SET_GLOBALS_EVENT_TYPE, handler);
  }, [key]);

  return val;
}

function CourseDetailsWidget() {
  const metadata = useOpenAiGlobal("toolResponseMetadata");
  const course = metadata?.course;

  if (!metadata) return <div>Loading…</div>;
  if (!course) return <div>No details</div>;

  return (
    <div>
      <h3>{course.name}</h3>
      <p>ID: {course.courseId || course.id}</p>
      <p>{course.description}</p>
    </div>
  );
}

const root = createRoot(document.getElementById("root"));
root.render(<CourseDetailsWidget />);
