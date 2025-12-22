import React, { useEffect, useState } from "react";
import { Box, Button, Spinner } from "./ui";

export default function LessonsTab({ courseId }) {
  const [lessons, setLessons] = useState(null);

  useEffect(() => {
    window.openai
      ?.callTool("tc_get_course_lessons", { courseId })
      .then((res) => setLessons(res.lessons));
  }, [courseId]);

  if (!lessons) return <Spinner />;

  return (
    <Box>
      {lessons.map((lesson) => (
        <Box key={lesson.sessionId}>
          {lesson.name}
        </Box>
      ))}
    </Box>
  );
}
